#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import unicodedata
import uuid
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_REGISTRY = ROOT / "contracts/v1.1/corpus-source-registry.json"
DEFAULT_CACHE_ROOT = ROOT / ".local/corpora"
WB0_NAMESPACE = uuid.UUID("7e09c574-2ef0-5a2f-8d89-754ee9d0fe93")
EXPECTED_SOURCE_KEYS = {"OSHB_MORPHHB", "BHSA_2021", "ETCBC_BRIDGING_2021"}


def load_ndjson(path: Path) -> list[dict]:
    with path.open(encoding="utf-8") as fh:
        return [json.loads(line) for line in fh if line.strip()]


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for block in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def stable_uuid(*parts: object) -> str:
    return str(uuid.uuid5(WB0_NAMESPACE, "|".join(str(p) for p in parts)))


def hebrew_letters_only(value: str | None) -> str:
    if not value:
        return ""
    return "".join(
        ch
        for ch in unicodedata.normalize("NFD", value)
        if "\u0590" <= ch <= "\u05ff" and unicodedata.category(ch).startswith("L")
    )


def sql_literal(value) -> str:
    if value is None:
        return "NULL"
    if isinstance(value, bool):
        return "TRUE" if value else "FALSE"
    if isinstance(value, (int, float)):
        return str(value)
    if isinstance(value, (dict, list)):
        raw = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        return "'" + raw.replace("'", "''") + "'::jsonb"
    raw = str(value)
    return "'" + raw.replace("'", "''") + "'"


def emit_insert(out: list[str], table: str, columns: list[str], rows: list[list[object]]) -> None:
    if not rows:
        return
    values = ",\n".join(
        "(" + ",".join(sql_literal(value) for value in row) + ")" for row in rows
    )
    out.append(f"INSERT INTO {table}({','.join(columns)}) VALUES\n{values};")


def source_index(registry: dict) -> dict[str, dict]:
    sources = {s["sourceKey"]: s for s in registry["sources"]}
    missing = EXPECTED_SOURCE_KEYS - set(sources)
    if missing:
        raise SystemExit(f"corpus registry missing WB-0 sources: {sorted(missing)}")
    return sources


def load_source_manifests(registry: dict, cache_root: Path) -> dict[str, dict]:
    manifests: dict[str, dict] = {}
    for source in registry["sources"]:
        if source["sourceKey"] not in EXPECTED_SOURCE_KEYS:
            continue
        path = cache_root / source["acquisition"]["localSubdir"] / "source-manifest.json"
        if not path.is_file():
            raise SystemExit(f"source manifest missing for {source['sourceKey']}: {path}")
        manifest = json.loads(path.read_text(encoding="utf-8"))
        if manifest.get("sourceKey") != source["sourceKey"]:
            raise SystemExit(f"{source['sourceKey']}: source manifest key mismatch")
        if manifest.get("commitSha") != source["pin"]["commitSha"]:
            raise SystemExit(f"{source['sourceKey']}: source manifest pin mismatch")
        if manifest.get("datasetVersion") != source["pin"].get("datasetVersion"):
            raise SystemExit(f"{source['sourceKey']}: source manifest dataset version mismatch")
        manifests[source["sourceKey"]] = {
            **manifest,
            "manifestSha256": sha256_file(path),
        }
    return manifests


def canonical_reference(crosswalk: list[dict]) -> tuple[str, int, int]:
    refs = {
        (
            row["reference"]["book"],
            int(row["reference"]["chapter"]),
            int(row["reference"]["verse"]),
        )
        for row in crosswalk
        if isinstance(row.get("reference"), dict)
    }
    if len(refs) != 1:
        raise SystemExit(f"WB-0 expects exactly one canonical reference, observed {sorted(refs)}")
    return next(iter(refs))


def validate_inputs(oshb: list[dict], bhsa: list[dict], crosswalk: list[dict]) -> dict:
    if not oshb or not bhsa or not crosswalk:
        raise SystemExit("WB-0 inputs must all be non-empty")
    if {row.get("sourceKey") for row in oshb} != {"OSHB_MORPHHB"}:
        raise SystemExit("OSHB export contains unexpected sourceKey")
    if {row.get("sourceKey") for row in bhsa} != {"BHSA_2021"}:
        raise SystemExit("BHSA export contains unexpected sourceKey")

    unresolved = [r for r in crosswalk if r.get("recordType") == "UNRESOLVED_REFERENCE"]
    if unresolved:
        raise SystemExit(f"WB-0 refuses unresolved crosswalk references: {unresolved}")

    candidates = [r for r in crosswalk if r.get("recordType") == "CANDIDATE_SPAN_MAPPING"]
    annotation_only = [r for r in crosswalk if r.get("recordType") == "ANNOTATION_ONLY_TARGET_NODE"]
    unknown_types = sorted(
        {
            r.get("recordType")
            for r in crosswalk
            if r.get("recordType")
            not in {"CANDIDATE_SPAN_MAPPING", "ANNOTATION_ONLY_TARGET_NODE", "UNRESOLVED_REFERENCE"}
        }
    )
    if unknown_types:
        raise SystemExit(f"WB-0 crosswalk contains unknown record types: {unknown_types}")
    if not candidates:
        raise SystemExit("WB-0 requires at least one candidate span mapping")
    for row in candidates:
        if row.get("canonical") is not False or row.get("reviewStatus") != "CANDIDATE_AUTOMATED":
            raise SystemExit("WB-0 refuses promoted or unexpectedly reviewed automatic candidate mapping")

    annotation_ids = {str(r["targetProviderScopedNodeId"]) for r in annotation_only}
    bhsa_ids = {str(r["providerScopedNodeId"]) for r in bhsa}
    if not annotation_ids <= bhsa_ids:
        raise SystemExit("crosswalk annotation-only nodes are absent from BHSA export")

    # The pinned canary evidence is intentionally exact: any drift requires a reviewed source/import change.
    if len(oshb) != 25 or len(bhsa) != 34:
        raise SystemExit(f"pinned 1 Sam 16:7 count drift: OSHB={len(oshb)} BHSA={len(bhsa)}")
    if annotation_ids != {"150439", "150445"}:
        raise SystemExit(f"pinned annotation-only node drift: {sorted(annotation_ids)}")
    if len(candidates) != 25:
        raise SystemExit(f"pinned candidate-group count drift: {len(candidates)}")

    many_to_many = [
        r for r in candidates
        if len(r.get("sourceProviderScopedWordIds", [])) > 1
        or len(r.get("targetProviderScopedNodeIds", [])) > 1
    ]
    if not many_to_many:
        raise SystemExit("WB-0 canary must exercise a non-1:1 cross-framework mapping")

    return {
        "reference": canonical_reference(crosswalk),
        "candidates": candidates,
        "annotationOnly": annotation_only,
        "annotationIds": annotation_ids,
        "manyToManyCount": len(many_to_many),
    }


def build_sql(
    oshb: list[dict],
    bhsa: list[dict],
    crosswalk_info: dict,
    registry: dict,
    manifests: dict[str, dict],
    input_hashes: dict[str, str],
) -> tuple[str, dict]:
    sources = source_index(registry)
    book, chapter, verse = crosswalk_info["reference"]
    if book != "1Sam" or chapter != 16 or verse != 7:
        raise SystemExit(f"WB-0 loader is intentionally pinned to 1Sam.16.7; observed {(book, chapter, verse)}")

    reference_span_id = stable_uuid("reference-span", book, chapter, verse)
    book_id = stable_uuid("book", book)
    atom_id = stable_uuid("reference-atom", book, chapter, verse)
    atom_sequence = chapter * 1000 + verse

    work_id = stable_uuid("textual-work", "WB0_MT_SOURCE_LINEAGE")
    oshb_edition_id = stable_uuid("textual-edition", "OSHB_MORPHHB")
    bhsa_edition_id = stable_uuid("textual-edition", "BHSA_2021")
    oshb_expression_id = stable_uuid("digital-expression", "OSHB_MORPHHB", sources["OSHB_MORPHHB"]["pin"]["commitSha"])
    bhsa_expression_id = stable_uuid("digital-expression", "BHSA_2021", sources["BHSA_2021"]["pin"]["commitSha"])
    oshb_stream_id = stable_uuid("text-stream", "OSHB_MORPHHB", "BASE")
    bhsa_stream_id = stable_uuid("text-stream", "BHSA_2021", "BASE")
    oshb_corpus_release_id = stable_uuid("corpus-release", "OSHB_MORPHHB", sources["OSHB_MORPHHB"]["pin"]["commitSha"])
    bhsa_corpus_release_id = stable_uuid("corpus-release", "BHSA_2021", sources["BHSA_2021"]["pin"]["commitSha"])
    oshb_framework_id = stable_uuid("annotation-framework", "OSHB_MORPHHB")
    bhsa_framework_id = stable_uuid("annotation-framework", "BHSA_2021")
    oshb_layer_id = stable_uuid("annotation-layer", "OSHB_MORPHHB", "MORPHOLOGY")
    bhsa_layer_id = stable_uuid("annotation-layer", "BHSA_2021", "WB0_WORD_PHRASE_CLAUSE")

    out = ["\\set ON_ERROR_STOP on", "BEGIN;"]

    emit_insert(out, "authoring.biblical_books", ["book_id", "osis_code", "english_name"], [
        [book_id, book, "1 Samuel"],
    ])
    emit_insert(out, "authoring.reference_atoms", ["reference_atom_id", "book_id", "sequence", "atom_kind", "metadata"], [
        [atom_id, book_id, atom_sequence, "VERSE", {"wb0": True, "chapter": chapter, "verse": verse}],
    ])
    emit_insert(out, "authoring.reference_spans", [
        "reference_span_id", "book_id", "start_atom_id", "start_sequence", "end_atom_id", "end_sequence", "span_kind", "metadata"
    ], [[reference_span_id, book_id, atom_id, atom_sequence, atom_id, atom_sequence, "VERSE", {"wb0": True}]])

    reference_system_rows = []
    reference_label_rows = []
    reference_member_rows = []
    seen_labels: set[tuple[str, str]] = set()
    for source_rows, label_name in ((oshb, "OSHB"), (bhsa, "BHSA")):
        for row in source_rows:
            code = str(row["referenceSystemCode"])
            label = str(row["referenceLabel"])
            key = (code, label)
            if key in seen_labels:
                continue
            seen_labels.add(key)
            system_id = stable_uuid("reference-system", code)
            label_id = stable_uuid("reference-label", code, label)
            reference_system_rows.append([system_id, code, f"{label_name} provider reference system"])
            reference_label_rows.append([label_id, system_id, book_id, label, chapter, str(verse), atom_sequence])
            reference_member_rows.append([label_id, book_id, atom_id, atom_sequence, 0])
    # Deduplicate systems while preserving first descriptive label.
    dedup_systems = {}
    for row in reference_system_rows:
        dedup_systems[row[0]] = row
    emit_insert(out, "authoring.reference_systems", ["reference_system_id", "code", "name"], list(dedup_systems.values()))
    emit_insert(out, "authoring.reference_labels", [
        "reference_label_id", "reference_system_id", "book_id", "label", "chapter_number", "verse_label", "sort_key"
    ], reference_label_rows)
    emit_insert(out, "authoring.reference_label_members", [
        "reference_label_id", "book_id", "reference_atom_id", "atom_sequence", "member_order"
    ], reference_member_rows)

    emit_insert(out, "authoring.textual_works", [
        "textual_work_id", "work_kind", "canonical_name", "language_code", "script_code", "description"
    ], [[work_id, "HEBREW_BIBLE", "WB-0 Masoretic Hebrew source lineage", "hbo", "Hebr", "Provider-scoped real-corpus canary; not a universal tokenization."]])
    emit_insert(out, "authoring.textual_editions", [
        "textual_edition_id", "textual_work_id", "edition_label", "edition_status", "metadata"
    ], [
        [oshb_edition_id, work_id, "OSHB morphhb pinned source", "PINNED_SOURCE", {"sourceKey": "OSHB_MORPHHB"}],
        [bhsa_edition_id, work_id, "BHSA 2021 pinned source", "PINNED_SOURCE", {"sourceKey": "BHSA_2021"}],
    ])
    emit_insert(out, "authoring.digital_expressions", [
        "digital_expression_id", "textual_edition_id", "textual_work_id", "expression_label", "expression_version", "source_checksum", "metadata"
    ], [
        [
            oshb_expression_id, oshb_edition_id, work_id, "OSHB morphhb WB-0 expression",
            sources["OSHB_MORPHHB"]["pin"]["commitSha"], input_hashes["oshb"],
            {
                "sourceKey": "OSHB_MORPHHB",
                "commitSha": sources["OSHB_MORPHHB"]["pin"]["commitSha"],
                "sourceManifestSha256": manifests["OSHB_MORPHHB"]["manifestSha256"],
                "reference": f"{book}.{chapter}.{verse}",
            },
        ],
        [
            bhsa_expression_id, bhsa_edition_id, work_id, "BHSA 2021 WB-0 expression",
            sources["BHSA_2021"]["pin"]["datasetVersion"], input_hashes["bhsa"],
            {
                "sourceKey": "BHSA_2021",
                "commitSha": sources["BHSA_2021"]["pin"]["commitSha"],
                "datasetVersion": sources["BHSA_2021"]["pin"]["datasetVersion"],
                "sourceManifestSha256": manifests["BHSA_2021"]["manifestSha256"],
                "bridgingCommitSha": sources["ETCBC_BRIDGING_2021"]["pin"]["commitSha"],
                "bridgingManifestSha256": manifests["ETCBC_BRIDGING_2021"]["manifestSha256"],
                "reference": f"{book}.{chapter}.{verse}",
            },
        ],
    ])
    emit_insert(out, "authoring.text_streams", [
        "text_stream_id", "digital_expression_id", "stream_type", "stream_version"
    ], [
        [oshb_stream_id, oshb_expression_id, "BASE", sources["OSHB_MORPHHB"]["pin"]["commitSha"]],
        [bhsa_stream_id, bhsa_expression_id, "BASE", sources["BHSA_2021"]["pin"]["datasetVersion"]],
    ])

    emit_insert(out, "authoring.research_objects", ["research_object_id", "object_type"], [
        [oshb_corpus_release_id, "CORPUS_RELEASE"],
        [bhsa_corpus_release_id, "CORPUS_RELEASE"],
        [oshb_layer_id, "ANNOTATION_LAYER"],
        [bhsa_layer_id, "ANNOTATION_LAYER"],
    ])
    emit_insert(out, "authoring.annotation_frameworks", [
        "annotation_framework_id", "framework_key", "name", "description", "ontology_version"
    ], [
        [oshb_framework_id, "OSHB_MORPHHB_REAL", "OSHB / morphhb", "Pinned provider-scoped OSHB morphology framework.", sources["OSHB_MORPHHB"]["pin"]["commitSha"]],
        [bhsa_framework_id, "BHSA_2021_REAL", "ETCBC BHSA 2021", "Pinned provider-scoped BHSA structural framework.", "2021"],
    ])
    emit_insert(out, "authoring.corpus_releases", [
        "corpus_release_id", "digital_expression_id", "release_name", "release_version", "importer_version", "source_checksum"
    ], [
        [oshb_corpus_release_id, oshb_expression_id, "OSHB morphhb WB-0 canary", sources["OSHB_MORPHHB"]["pin"]["commitSha"], "wb0-relational-canary-v1", input_hashes["oshb"]],
        [bhsa_corpus_release_id, bhsa_expression_id, "BHSA 2021 WB-0 canary", "2021", "wb0-relational-canary-v1", input_hashes["bhsa"]],
    ])
    emit_insert(out, "authoring.annotation_layers", [
        "annotation_layer_id", "corpus_release_id", "annotation_framework_id", "layer_kind", "layer_version", "content_hash", "metadata"
    ], [
        [
            oshb_layer_id, oshb_corpus_release_id, oshb_framework_id, "MORPHOLOGY",
            sources["OSHB_MORPHHB"]["pin"]["commitSha"], input_hashes["oshb"],
            {"sourceKey": "OSHB_MORPHHB", "providerScoped": True, "wb0Role": "WORD_MORPHOLOGY"},
        ],
        [
            bhsa_layer_id, bhsa_corpus_release_id, bhsa_framework_id, "CLAUSE_STRUCTURE",
            "2021", input_hashes["bhsa"],
            {
                "sourceKey": "BHSA_2021",
                "providerScoped": True,
                "wb0Role": "COMPOSITE_WORD_PHRASE_CLAUSE_CANARY",
                "note": "WB-0 keeps word/phrase/clause nodes in one structural layer so source graph membership is relationally testable; later whole-corpus layer decomposition remains open.",
            },
        ],
    ])

    text_segments: list[list[object]] = []
    analysis_nodes: list[list[object]] = []
    features: list[list[object]] = []
    node_segments: list[list[object]] = []

    oshb_node_ids: dict[str, str] = {}
    for row in sorted(oshb, key=lambda r: int(r["wordOrderInVerse"])):
        provider_id = str(row["providerScopedWordId"])
        node_id = stable_uuid("analysis-node", "OSHB_MORPHHB", provider_id)
        segment_id = stable_uuid("text-segment", "OSHB_MORPHHB", provider_id)
        oshb_node_ids[provider_id] = node_id
        surface = row.get("surfaceSourceExact")
        if not surface:
            raise SystemExit(f"OSHB word {provider_id} has empty source surface")
        text_segments.append([
            segment_id, oshb_stream_id, reference_span_id, int(row["wordOrderInVerse"]),
            "PERSISTED_CONTENT", surface, "WORD", hashlib.sha256(surface.encode("utf-8")).hexdigest(),
            {"sourceKey": "OSHB_MORPHHB", "providerScopedWordId": provider_id, "referenceLabel": row["referenceLabel"]},
        ])
        analysis_nodes.append([
            node_id, oshb_layer_id, "WORD", reference_span_id, int(row["wordOrderInVerse"]), provider_id,
            {"sourceKey": "OSHB_MORPHHB", "providerScopedWordId": provider_id, "referenceSystemCode": row["referenceSystemCode"], "referenceLabel": row["referenceLabel"]},
        ])
        node_segments.append([node_id, segment_id, 0, "ORTHOGRAPHIC_WORD"])
        for key, value in (
            ("SOURCE_KEY", "OSHB_MORPHHB"),
            ("LEMMA_RAW", row.get("lemmaRaw")),
            ("MORPH_RAW", row.get("morphRaw")),
        ):
            if value not in (None, ""):
                features.append([node_id, key, str(value)])

    annotation_ids = crosswalk_info["annotationIds"]
    bhsa_node_ids: dict[str, str] = {}
    bhsa_segment_ids: dict[str, str] = {}
    phrase_words: dict[str, list[dict]] = defaultdict(list)
    clause_words: dict[str, list[dict]] = defaultdict(list)
    phrase_clause_pairs: set[tuple[str, str]] = set()
    bridge_feature_count = 0
    body_part_node_ids: list[str] = []

    raw_feature_map = [
        ("LEXEME_RAW", "lexemeRaw"),
        ("PART_OF_SPEECH_RAW", "partOfSpeechRaw"),
        ("PHRASE_DEPENDENT_POS_RAW", "phraseDependentPartOfSpeechRaw"),
        ("GENDER_RAW", "genderRaw"),
        ("NUMBER_RAW", "numberRaw"),
        ("STATE_RAW", "stateRaw"),
        ("VERBAL_STEM_RAW", "verbalStemRaw"),
        ("VERBAL_TENSE_RAW", "verbalTenseRaw"),
        ("LANGUAGE_RAW", "languageRaw"),
        ("LANGUAGE_ISO_RAW", "languageIsoRaw"),
        ("QERE_RAW", "qereRaw"),
        ("PHRASE_FUNCTION_RAW", "phraseFunctionRaw"),
        ("PHRASE_TYPE_RAW", "phraseTypeRaw"),
        ("PHRASE_RELATION_RAW", "phraseRelationRaw"),
        ("CLAUSE_TYPE_RAW", "clauseTypeRaw"),
        ("CLAUSE_RELATION_RAW", "clauseRelationRaw"),
        ("BRIDGE_OSM_PRIMARY_RAW", "bridgeOshbMorphologyPrimaryRaw"),
        ("BRIDGE_OSM_SECONDARY_RAW", "bridgeOshbMorphologySecondaryRaw"),
    ]

    for row in sorted(bhsa, key=lambda r: int(r["wordOrderInVerse"])):
        provider_id = str(row["providerScopedNodeId"])
        node_id = stable_uuid("analysis-node", "BHSA_2021", "word", provider_id)
        bhsa_node_ids[provider_id] = node_id
        is_annotation_only = provider_id in annotation_ids
        analysis_nodes.append([
            node_id, bhsa_layer_id, "WORD", reference_span_id, int(row["wordOrderInVerse"]), provider_id,
            {
                "sourceKey": "BHSA_2021",
                "providerScopedNodeId": provider_id,
                "referenceSystemCode": row["referenceSystemCode"],
                "referenceLabel": row["referenceLabel"],
                "annotationOnly": is_annotation_only,
                "phraseNodeId": row.get("phraseNodeId"),
                "clauseNodeId": row.get("clauseNodeId"),
            },
        ])
        surface = row.get("surfaceSourceExact") or row.get("consonantalSourceExact")
        if is_annotation_only:
            if surface:
                raise SystemExit(f"annotation-only BHSA node unexpectedly has surface content: {provider_id}")
        else:
            if not surface:
                raise SystemExit(f"text-bearing BHSA node has no source surface: {provider_id}")
            segment_id = stable_uuid("text-segment", "BHSA_2021", provider_id)
            bhsa_segment_ids[provider_id] = segment_id
            text_segments.append([
                segment_id, bhsa_stream_id, reference_span_id, int(row["wordOrderInVerse"]),
                "PERSISTED_CONTENT", surface, "WORD", hashlib.sha256(surface.encode("utf-8")).hexdigest(),
                {"sourceKey": "BHSA_2021", "providerScopedNodeId": provider_id, "referenceLabel": row["referenceLabel"]},
            ])
            node_segments.append([node_id, segment_id, 0, "ORTHOGRAPHIC_WORD"])

        features.append([node_id, "SOURCE_KEY", "BHSA_2021"])
        lexeme_key = hebrew_letters_only(row.get("lexemeRaw"))
        if lexeme_key:
            features.append([node_id, "HEBREW_LEXEME_LETTERS_V1", lexeme_key])
            if lexeme_key == "עין":
                body_part_node_ids.append(node_id)
        for feature_key, source_key in raw_feature_map:
            value = row.get(source_key)
            if value not in (None, ""):
                features.append([node_id, feature_key, str(value)])
                if feature_key.startswith("BRIDGE_OSM_"):
                    bridge_feature_count += 1

        if row.get("phraseNodeId") is not None:
            phrase_words[str(row["phraseNodeId"])].append(row)
        if row.get("clauseNodeId") is not None:
            clause_words[str(row["clauseNodeId"])].append(row)
        if row.get("phraseNodeId") is not None and row.get("clauseNodeId") is not None:
            phrase_clause_pairs.add((str(row["phraseNodeId"]), str(row["clauseNodeId"])))

    if not body_part_node_ids:
        raise SystemExit("WB-0 expected BHSA lexeme עין in 1 Sam 16:7 but found none")

    phrase_node_ids: dict[str, str] = {}
    clause_node_ids: dict[str, str] = {}
    for order, provider_id in enumerate(sorted(phrase_words, key=lambda x: int(x)), start=1):
        node_id = stable_uuid("analysis-node", "BHSA_2021", "phrase", provider_id)
        phrase_node_ids[provider_id] = node_id
        analysis_nodes.append([
            node_id, bhsa_layer_id, "PHRASE", reference_span_id, order, f"phrase:{provider_id}",
            {"sourceKey": "BHSA_2021", "providerScopedPhraseNodeId": provider_id},
        ])
        segments = [
            bhsa_segment_ids[str(row["providerScopedNodeId"])]
            for row in sorted(phrase_words[provider_id], key=lambda r: int(r["wordOrderInVerse"]))
            if str(row["providerScopedNodeId"]) in bhsa_segment_ids
        ]
        for member_order, segment_id in enumerate(dict.fromkeys(segments)):
            node_segments.append([node_id, segment_id, member_order, "PHRASE_MEMBER"])

    for order, provider_id in enumerate(sorted(clause_words, key=lambda x: int(x)), start=1):
        node_id = stable_uuid("analysis-node", "BHSA_2021", "clause", provider_id)
        clause_node_ids[provider_id] = node_id
        analysis_nodes.append([
            node_id, bhsa_layer_id, "CLAUSE", reference_span_id, order, f"clause:{provider_id}",
            {"sourceKey": "BHSA_2021", "providerScopedClauseNodeId": provider_id},
        ])
        segments = [
            bhsa_segment_ids[str(row["providerScopedNodeId"])]
            for row in sorted(clause_words[provider_id], key=lambda r: int(r["wordOrderInVerse"]))
            if str(row["providerScopedNodeId"]) in bhsa_segment_ids
        ]
        for member_order, segment_id in enumerate(dict.fromkeys(segments)):
            node_segments.append([node_id, segment_id, member_order, "CLAUSE_MEMBER"])

    emit_insert(out, "authoring.text_segments", [
        "text_segment_id", "text_stream_id", "reference_span_id", "segment_order", "segment_storage_mode",
        "surface_original", "segment_kind", "content_hash", "metadata"
    ], text_segments)
    emit_insert(out, "authoring.analysis_nodes", [
        "analysis_node_id", "annotation_layer_id", "node_type", "reference_span_id", "node_order", "external_node_id", "metadata"
    ], analysis_nodes)
    emit_insert(out, "authoring.analysis_node_features", [
        "analysis_node_id", "feature_key", "feature_value"
    ], features)
    emit_insert(out, "authoring.analysis_node_segments", [
        "analysis_node_id", "text_segment_id", "member_order", "membership_role"
    ], node_segments)

    edge_rows: list[list[object]] = []
    edge_seen: set[tuple[str, str, str]] = set()
    for row in bhsa:
        word_id = bhsa_node_ids[str(row["providerScopedNodeId"])]
        if row.get("phraseNodeId") is not None:
            phrase_id = phrase_node_ids[str(row["phraseNodeId"])]
            edge_seen.add((word_id, phrase_id, "MEMBER_OF_PHRASE"))
        if row.get("clauseNodeId") is not None:
            clause_id = clause_node_ids[str(row["clauseNodeId"])]
            edge_seen.add((word_id, clause_id, "MEMBER_OF_CLAUSE"))
    for phrase_provider_id, clause_provider_id in phrase_clause_pairs:
        edge_seen.add((phrase_node_ids[phrase_provider_id], clause_node_ids[clause_provider_id], "MEMBER_OF_CLAUSE"))
    for from_node, to_node, relation in sorted(edge_seen):
        edge_rows.append([
            stable_uuid("analysis-edge", "BHSA_2021", from_node, to_node, relation),
            bhsa_layer_id, from_node, to_node, relation, "BHSA_2021_MEMBERSHIP_V1",
            {"sourceKey": "BHSA_2021"},
        ])
    emit_insert(out, "authoring.analysis_edges", [
        "analysis_edge_id", "annotation_layer_id", "from_node_id", "to_node_id", "relation_type", "relation_ontology", "properties"
    ], edge_rows)

    # Project semantic-set authority remains separate from BHSA lexical features.
    semantic_set_id = stable_uuid("semantic-set", "BODY_PART")
    semantic_version_id = stable_uuid("semantic-set-version", "BODY_PART", 1)
    emit_insert(out, "authoring.research_objects", ["research_object_id", "object_type"], [
        [semantic_version_id, "SEMANTIC_SET_VERSION"],
    ])
    emit_insert(out, "authoring.semantic_sets", [
        "semantic_set_id", "name", "description", "set_scope", "official_status", "current_version_id"
    ], [[semantic_set_id, "BODY_PART", "WB-0 project semantic-set canary", "OFFICIAL", "PUBLISHED", None]])
    emit_insert(out, "authoring.semantic_set_versions", [
        "semantic_set_version_id", "semantic_set_id", "version_number", "definition_json", "review_status"
    ], [[semantic_version_id, semantic_set_id, 1, {"kind": "LEXEME_SET", "normalization": "HEBREW_LETTERS_ONLY_NFD_V1"}, "HUMAN_REVIEWED"]])
    out.append(
        "UPDATE authoring.semantic_sets SET current_version_id="
        + sql_literal(semantic_version_id)
        + " WHERE semantic_set_id="
        + sql_literal(semantic_set_id)
        + ";"
    )
    emit_insert(out, "authoring.semantic_set_members", [
        "semantic_set_version_id", "member_object_type", "member_key", "inclusion_type", "reason", "review_status"
    ], [[semantic_version_id, "LEXEME", "עין", "INCLUDE", "Project-curated WB-0 body-part canary membership.", "HUMAN_REVIEWED"]])

    mapping_group_rows: list[list[object]] = []
    from_member_rows: list[list[object]] = []
    to_member_rows: list[list[object]] = []
    mapping_group_ids: list[str] = []
    for candidate in crosswalk_info["candidates"]:
        source_ids = [str(v) for v in candidate["sourceProviderScopedWordIds"]]
        target_ids = [str(v) for v in candidate["targetProviderScopedNodeIds"]]
        missing_source = [v for v in source_ids if v not in oshb_node_ids]
        missing_target = [v for v in target_ids if v not in bhsa_node_ids]
        if missing_source or missing_target:
            raise SystemExit(f"candidate mapping references absent provider nodes: source={missing_source} target={missing_target}")
        if set(target_ids) & annotation_ids:
            raise SystemExit("annotation-only BHSA node must not enter orthographic candidate mapping")

        group_id = stable_uuid(
            "cross-annotation-mapping-group",
            book, chapter, verse,
            ",".join(source_ids),
            ",".join(target_ids),
            candidate["mappingMethod"],
        )
        mapping_group_ids.append(group_id)
        mapping_group_rows.append([
            group_id, oshb_layer_id, bhsa_layer_id, reference_span_id,
            "ORTHOGRAPHIC_SPAN_CANDIDATE", candidate["mappingMethod"], candidate["reviewStatus"],
            False, None,
            {
                "signatureAlgorithm": candidate["signatureAlgorithm"],
                "consonantalSignature": candidate["consonantalSignature"],
                "sourceCount": candidate["sourceCount"],
                "targetCount": candidate["targetCount"],
                "crosswalkInputSha256": input_hashes["crosswalk"],
            },
        ])
        for member_order, provider_id in enumerate(source_ids):
            from_member_rows.append([group_id, oshb_layer_id, oshb_node_ids[provider_id], member_order])
        for member_order, provider_id in enumerate(target_ids):
            to_member_rows.append([group_id, bhsa_layer_id, bhsa_node_ids[provider_id], member_order])

    emit_insert(out, "authoring.cross_annotation_mapping_groups", [
        "mapping_group_id", "from_annotation_layer_id", "to_annotation_layer_id", "reference_span_id",
        "mapping_type", "mapping_method", "review_status", "canonical", "confidence", "properties"
    ], mapping_group_rows)
    emit_insert(out, "authoring.cross_annotation_mapping_from_members", [
        "mapping_group_id", "from_annotation_layer_id", "from_node_id", "member_order"
    ], from_member_rows)
    emit_insert(out, "authoring.cross_annotation_mapping_to_members", [
        "mapping_group_id", "to_annotation_layer_id", "to_node_id", "member_order"
    ], to_member_rows)

    out.append("COMMIT;")

    report = {
        "schemaVersion": "1.0",
        "milestone": "WB-0",
        "reference": f"{book}.{chapter}.{verse}",
        "referenceSpanId": reference_span_id,
        "sourcePins": {
            key: {
                "commitSha": sources[key]["pin"]["commitSha"],
                "datasetVersion": sources[key]["pin"].get("datasetVersion"),
                "manifestSha256": manifests[key]["manifestSha256"],
            }
            for key in sorted(EXPECTED_SOURCE_KEYS)
        },
        "inputSha256": input_hashes,
        "counts": {
            "oshbWordNodes": len(oshb),
            "bhsaWordNodes": len(bhsa),
            "bhsaTextBearingWordNodes": len(bhsa_segment_ids),
            "bhsaAnnotationOnlyWordNodes": len(annotation_ids),
            "bhsaPhraseNodes": len(phrase_node_ids),
            "bhsaClauseNodes": len(clause_node_ids),
            "bhsaMembershipEdges": len(edge_rows),
            "candidateMappingGroups": len(mapping_group_rows),
            "manyToManyCandidateGroups": crosswalk_info["manyToManyCount"],
            "bridgeFeatureValues": bridge_feature_count,
            "projectBodyPartTargetNodes": len(body_part_node_ids),
            "unresolvedReferences": 0,
        },
        "annotationOnlyProviderNodeIds": sorted(annotation_ids, key=int),
        "layerIds": {"oshb": oshb_layer_id, "bhsa": bhsa_layer_id},
        "corpusReleaseIds": {"oshb": oshb_corpus_release_id, "bhsa": bhsa_corpus_release_id},
        "semanticSetVersionId": semantic_version_id,
        "canonicalCandidateMappings": 0,
        "servingProjectionWritten": False,
    }
    return "\n\n".join(out) + "\n", report


def main() -> int:
    parser = argparse.ArgumentParser(description="Load the WB-0 real 1 Samuel 16:7 corpus canary into PostgreSQL.")
    parser.add_argument("--oshb", type=Path, required=True)
    parser.add_argument("--bhsa", type=Path, required=True)
    parser.add_argument("--crosswalk", type=Path, required=True)
    parser.add_argument("--registry", type=Path, default=DEFAULT_REGISTRY)
    parser.add_argument("--cache-root", type=Path, default=DEFAULT_CACHE_ROOT)
    parser.add_argument("--report", type=Path, required=True)
    parser.add_argument("--emit-sql", type=Path)
    args = parser.parse_args()

    for path in (args.oshb, args.bhsa, args.crosswalk, args.registry):
        if not path.is_file():
            raise SystemExit(f"required WB-0 input missing: {path}")

    registry = json.loads(args.registry.read_text(encoding="utf-8"))
    manifests = load_source_manifests(registry, args.cache_root)
    oshb = load_ndjson(args.oshb)
    bhsa = load_ndjson(args.bhsa)
    crosswalk = load_ndjson(args.crosswalk)
    info = validate_inputs(oshb, bhsa, crosswalk)
    input_hashes = {
        "oshb": sha256_file(args.oshb),
        "bhsa": sha256_file(args.bhsa),
        "crosswalk": sha256_file(args.crosswalk),
    }
    sql, report = build_sql(oshb, bhsa, info, registry, manifests, input_hashes)

    if args.emit_sql:
        args.emit_sql.parent.mkdir(parents=True, exist_ok=True)
        args.emit_sql.write_text(sql, encoding="utf-8")

    subprocess.run(
        ["psql", "-X", "-v", "ON_ERROR_STOP=1"],
        input=sql,
        text=True,
        check=True,
    )

    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(report, ensure_ascii=False, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
