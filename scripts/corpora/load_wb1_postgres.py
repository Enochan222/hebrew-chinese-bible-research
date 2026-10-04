#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import tempfile
import unicodedata
import uuid
from collections import Counter, defaultdict
from pathlib import Path
from typing import Iterable, Iterator

from build_candidate_crosswalk import is_bhsa_annotation_only_node
from reference_aliases import parse_reference_label

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_CANON = ROOT / "contracts/v1.1/hebrew-bible-canon-system.json"
DEFAULT_REGISTRY = ROOT / "contracts/v1.1/corpus-source-registry.json"
DEFAULT_CACHE_ROOT = ROOT / ".local/corpora"
CORPUS_NAMESPACE = uuid.UUID("7e09c574-2ef0-5a2f-8d89-754ee9d0fe93")
EXPECTED_SOURCE_KEYS = {"OSHB_MORPHHB", "BHSA_2021", "ETCBC_BRIDGING_2021"}
IMPORTER_VERSION = "wb1-whole-corpus-v1"


def stable_uuid(*parts: object) -> str:
    return str(uuid.uuid5(CORPUS_NAMESPACE, "|".join(str(p) for p in parts)))


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for block in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def canonical_hash(value: object) -> str:
    raw = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def load_ndjson(path: Path) -> list[dict]:
    with path.open(encoding="utf-8") as fh:
        return [json.loads(line) for line in fh if line.strip()]


def hebrew_letters_only(value: str | None) -> str:
    if not value:
        return ""
    return "".join(
        ch for ch in unicodedata.normalize("NFD", value)
        if "\u0590" <= ch <= "\u05ff" and unicodedata.category(ch).startswith("L")
    )


def copy_escape(value: object) -> str:
    if value is None:
        return r"\N"
    if isinstance(value, bool):
        return "t" if value else "f"
    if isinstance(value, (dict, list)):
        value = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    text = str(value)
    if "\x00" in text:
        raise ValueError("PostgreSQL COPY text cannot contain NUL")
    return (
        text.replace("\\", "\\\\")
        .replace("\t", "\\t")
        .replace("\n", "\\n")
        .replace("\r", "\\r")
    )


def write_copy(out, table: str, columns: list[str], rows: Iterable[Iterable[object]]) -> int:
    out.write(f"COPY {table} ({','.join(columns)}) FROM STDIN;\n")
    count = 0
    for row in rows:
        out.write("\t".join(copy_escape(value) for value in row) + "\n")
        count += 1
    out.write("\\.\n")
    return count


def psql_file(path: Path) -> None:
    subprocess.run(["psql", "-X", "-v", "ON_ERROR_STOP=1", "-f", str(path)], check=True)


def psql_query(sql: str) -> str:
    result = subprocess.run(
        ["psql", "-X", "-v", "ON_ERROR_STOP=1", "-At", "-F", "\t", "-c", sql],
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout


def source_index(registry: dict) -> dict[str, dict]:
    sources = {s["sourceKey"]: s for s in registry["sources"]}
    missing = EXPECTED_SOURCE_KEYS - set(sources)
    if missing:
        raise SystemExit(f"corpus registry missing WB-1 sources: {sorted(missing)}")
    return sources


def load_source_manifests(registry: dict, cache_root: Path) -> dict[str, dict]:
    manifests: dict[str, dict] = {}
    for source in registry["sources"]:
        key = source["sourceKey"]
        if key not in EXPECTED_SOURCE_KEYS:
            continue
        path = cache_root / source["acquisition"]["localSubdir"] / "source-manifest.json"
        if not path.is_file():
            raise SystemExit(f"source manifest missing for {key}: {path}")
        manifest = json.loads(path.read_text(encoding="utf-8"))
        if manifest.get("sourceKey") != key:
            raise SystemExit(f"{key}: source manifest key mismatch")
        if manifest.get("commitSha") != source["pin"]["commitSha"]:
            raise SystemExit(f"{key}: source manifest pin mismatch")
        if manifest.get("datasetVersion") != source["pin"].get("datasetVersion"):
            raise SystemExit(f"{key}: source manifest dataset version mismatch")
        manifests[key] = {**manifest, "manifestSha256": sha256_file(path)}
    return manifests


def load_canon(path: Path) -> tuple[dict, list[dict]]:
    data = json.loads(path.read_text(encoding="utf-8"))
    books = sorted((b for b in data["books"] if b.get("included")), key=lambda b: b["bookOrder"])
    orders = [b["bookOrder"] for b in books]
    if orders != list(range(1, len(books) + 1)):
        raise SystemExit("configured canon order is not contiguous")
    return data["canonSystem"], books


def sequence(chapter: int, verse: int) -> int:
    if chapter < 0 or verse < 0 or verse >= 1000:
        raise ValueError(f"unsupported reference address {chapter}.{verse}")
    return chapter * 1000 + verse


def ref_from_row(row: dict, expected_book: str) -> tuple[str, int, int]:
    ref = parse_reference_label(str(row["referenceLabel"]))
    if ref[0] != expected_book:
        raise ValueError(f"record escaped configured book {expected_book}: {row['referenceLabel']!r} -> {ref}")
    return ref


def verse_atom_id(ref: tuple[str, int, int]) -> str:
    return stable_uuid("reference-atom", *ref)


def verse_span_id(ref: tuple[str, int, int]) -> str:
    return stable_uuid("reference-span", *ref)


def range_span_id(book: str, start_seq: int, end_seq: int, kind: str) -> str:
    return stable_uuid("reference-span-range", book, start_seq, end_seq, kind)


def shared_ids(sources: dict[str, dict]) -> dict[str, str]:
    return {
        "work": stable_uuid("textual-work", "WB0_MT_SOURCE_LINEAGE"),
        "oshbEdition": stable_uuid("textual-edition", "OSHB_MORPHHB"),
        "bhsaEdition": stable_uuid("textual-edition", "BHSA_2021"),
        "oshbExpression": stable_uuid("digital-expression", "OSHB_MORPHHB", sources["OSHB_MORPHHB"]["pin"]["commitSha"]),
        "bhsaExpression": stable_uuid("digital-expression", "BHSA_2021", sources["BHSA_2021"]["pin"]["commitSha"]),
        "oshbStream": stable_uuid("text-stream", "OSHB_MORPHHB", "BASE"),
        "bhsaStream": stable_uuid("text-stream", "BHSA_2021", "BASE"),
        "oshbCorpus": stable_uuid("corpus-release", "OSHB_MORPHHB", sources["OSHB_MORPHHB"]["pin"]["commitSha"]),
        "bhsaCorpus": stable_uuid("corpus-release", "BHSA_2021", sources["BHSA_2021"]["pin"]["commitSha"]),
        "oshbFramework": stable_uuid("annotation-framework", "OSHB_MORPHHB"),
        "bhsaFramework": stable_uuid("annotation-framework", "BHSA_2021"),
        "oshbLayer": stable_uuid("annotation-layer", "OSHB_MORPHHB", "MORPHOLOGY"),
        "bhsaLayer": stable_uuid("annotation-layer", "BHSA_2021", "WB0_WORD_PHRASE_CLAUSE"),
        "semanticSet": stable_uuid("semantic-set", "BODY_PART"),
        "semanticVersion": stable_uuid("semantic-set-version", "BODY_PART", 1),
    }


def write_shared_setup(
    path: Path,
    canon_system: dict,
    books: list[dict],
    sources: dict[str, dict],
    manifests: dict[str, dict],
    ids: dict[str, str],
) -> None:
    canon_id = stable_uuid("canon-system", canon_system["code"])
    oshb_manifest = manifests["OSHB_MORPHHB"]["manifestSha256"]
    bhsa_manifest = manifests["BHSA_2021"]["manifestSha256"]
    bridge_manifest = manifests["ETCBC_BRIDGING_2021"]["manifestSha256"]
    with path.open("w", encoding="utf-8") as out:
        out.write("\\set ON_ERROR_STOP on\nBEGIN;\n")
        write_copy(out, "authoring.biblical_books", ["book_id","osis_code","english_name"], (
            (stable_uuid("book", b["osisCode"]), b["osisCode"], b["englishName"]) for b in books
        ))
        write_copy(out, "authoring.canon_systems", ["canon_system_id","code","name","tradition","description"], [
            (canon_id, canon_system["code"], canon_system["name"], canon_system.get("tradition"), canon_system.get("description"))
        ])
        write_copy(out, "authoring.canon_books", ["canon_system_id","book_id","book_order","included"], (
            (canon_id, stable_uuid("book", b["osisCode"]), b["bookOrder"], True) for b in books
        ))
        write_copy(out, "authoring.reference_systems", ["reference_system_id","code","name"], [
            (stable_uuid("reference-system","OSHB_OSIS"), "OSHB_OSIS", "OSHB provider OSIS addressing"),
            (stable_uuid("reference-system","BHSA_2021_SECTION"), "BHSA_2021_SECTION", "BHSA 2021 provider section addressing"),
        ])
        write_copy(out, "authoring.textual_works", [
            "textual_work_id","work_kind","canonical_name","language_code","script_code","description"
        ], [(
            ids["work"], "HEBREW_BIBLE", "WB-1 Masoretic Hebrew source lineage", "hbo", "Hebr",
            "Whole-corpus provider-scoped source lineage; annotation frameworks remain distinct."
        )])
        write_copy(out, "authoring.textual_editions", [
            "textual_edition_id","textual_work_id","edition_label","edition_status","metadata"
        ], [
            (ids["oshbEdition"], ids["work"], "OSHB morphhb pinned source", "PINNED_SOURCE", {"sourceKey":"OSHB_MORPHHB"}),
            (ids["bhsaEdition"], ids["work"], "BHSA 2021 pinned source", "PINNED_SOURCE", {"sourceKey":"BHSA_2021"}),
        ])
        write_copy(out, "authoring.digital_expressions", [
            "digital_expression_id","textual_edition_id","textual_work_id","expression_label","expression_version","source_checksum","metadata"
        ], [
            (
                ids["oshbExpression"], ids["oshbEdition"], ids["work"], "OSHB morphhb WB-1 expression",
                sources["OSHB_MORPHHB"]["pin"]["commitSha"], oshb_manifest,
                {"sourceKey":"OSHB_MORPHHB","commitSha":sources["OSHB_MORPHHB"]["pin"]["commitSha"],"sourceManifestSha256":oshb_manifest}
            ),
            (
                ids["bhsaExpression"], ids["bhsaEdition"], ids["work"], "BHSA 2021 WB-1 expression",
                sources["BHSA_2021"]["pin"]["datasetVersion"], bhsa_manifest,
                {
                    "sourceKey":"BHSA_2021","commitSha":sources["BHSA_2021"]["pin"]["commitSha"],
                    "datasetVersion":sources["BHSA_2021"]["pin"]["datasetVersion"],
                    "sourceManifestSha256":bhsa_manifest,
                    "bridgingCommitSha":sources["ETCBC_BRIDGING_2021"]["pin"]["commitSha"],
                    "bridgingManifestSha256":bridge_manifest,
                }
            ),
        ])
        write_copy(out, "authoring.text_streams", [
            "text_stream_id","digital_expression_id","stream_type","stream_version"
        ], [
            (ids["oshbStream"], ids["oshbExpression"], "BASE", sources["OSHB_MORPHHB"]["pin"]["commitSha"]),
            (ids["bhsaStream"], ids["bhsaExpression"], "BASE", sources["BHSA_2021"]["pin"]["datasetVersion"]),
        ])
        write_copy(out, "authoring.research_objects", ["research_object_id","object_type"], [
            (ids["oshbCorpus"], "CORPUS_RELEASE"),
            (ids["bhsaCorpus"], "CORPUS_RELEASE"),
            (ids["oshbLayer"], "ANNOTATION_LAYER"),
            (ids["bhsaLayer"], "ANNOTATION_LAYER"),
            (ids["semanticVersion"], "SEMANTIC_SET_VERSION"),
        ])
        write_copy(out, "authoring.annotation_frameworks", [
            "annotation_framework_id","framework_key","name","description","ontology_version"
        ], [
            (ids["oshbFramework"], "OSHB_MORPHHB_REAL", "OSHB / morphhb", "Pinned provider-scoped OSHB morphology framework.", sources["OSHB_MORPHHB"]["pin"]["commitSha"]),
            (ids["bhsaFramework"], "BHSA_2021_REAL", "ETCBC BHSA 2021", "Pinned provider-scoped BHSA structural framework.", "2021"),
        ])
        write_copy(out, "authoring.corpus_releases", [
            "corpus_release_id","digital_expression_id","release_name","release_version","importer_version","source_checksum"
        ], [
            (ids["oshbCorpus"], ids["oshbExpression"], "OSHB morphhb WB-1 whole corpus", sources["OSHB_MORPHHB"]["pin"]["commitSha"], IMPORTER_VERSION, oshb_manifest),
            (ids["bhsaCorpus"], ids["bhsaExpression"], "BHSA 2021 WB-1 whole corpus", "2021", IMPORTER_VERSION, bhsa_manifest),
        ])
        write_copy(out, "authoring.annotation_layers", [
            "annotation_layer_id","corpus_release_id","annotation_framework_id","layer_kind","layer_version","content_hash","metadata"
        ], [
            (
                ids["oshbLayer"], ids["oshbCorpus"], ids["oshbFramework"], "MORPHOLOGY",
                sources["OSHB_MORPHHB"]["pin"]["commitSha"], oshb_manifest,
                {"sourceKey":"OSHB_MORPHHB","providerScoped":True,"wb1Role":"WORD_MORPHOLOGY"}
            ),
            (
                ids["bhsaLayer"], ids["bhsaCorpus"], ids["bhsaFramework"], "CLAUSE_STRUCTURE",
                "2021", bhsa_manifest,
                {
                    "sourceKey":"BHSA_2021","providerScoped":True,"wb1Role":"WORD_PHRASE_CLAUSE_GRAPH",
                    "note":"WB-1 preserves BHSA word/phrase/clause graph identity without claiming universal phrase/clause identity."
                }
            ),
        ])
        write_copy(out, "authoring.semantic_sets", [
            "semantic_set_id","name","description","set_scope","official_status","current_version_id"
        ], [(ids["semanticSet"], "BODY_PART", "Project-curated body-part lexeme canary", "OFFICIAL", "PUBLISHED", None)])
        write_copy(out, "authoring.semantic_set_versions", [
            "semantic_set_version_id","semantic_set_id","version_number","definition_json","review_status"
        ], [(ids["semanticVersion"], ids["semanticSet"], 1, {"kind":"LEXEME_SET","normalization":"HEBREW_LETTERS_ONLY_NFD_V1"}, "HUMAN_REVIEWED")])
        out.write(
            "UPDATE authoring.semantic_sets SET current_version_id='"
            + ids["semanticVersion"]
            + "' WHERE semantic_set_id='"
            + ids["semanticSet"]
            + "';\n"
        )
        write_copy(out, "authoring.semantic_set_members", [
            "semantic_set_version_id","member_object_type","member_key","inclusion_type","reason","review_status"
        ], [(ids["semanticVersion"], "LEXEME", "עין", "INCLUDE", "Project-curated WB-1 body-part canary membership.", "HUMAN_REVIEWED")])
        out.write("COMMIT;\n")


def word_features_bhsa(node_id: str, row: dict) -> Iterator[tuple[object,...]]:
    mapping = [
        ("LEXEME_RAW","lexemeRaw"),
        ("PART_OF_SPEECH_RAW","partOfSpeechRaw"),
        ("PHRASE_DEPENDENT_POS_RAW","phraseDependentPartOfSpeechRaw"),
        ("GENDER_RAW","genderRaw"),("NUMBER_RAW","numberRaw"),("STATE_RAW","stateRaw"),
        ("VERBAL_STEM_RAW","verbalStemRaw"),("VERBAL_TENSE_RAW","verbalTenseRaw"),
        ("LANGUAGE_RAW","languageRaw"),("LANGUAGE_ISO_RAW","languageIsoRaw"),
        ("QERE_RAW","qereRaw"),
        ("BRIDGE_OSM_PRIMARY_RAW","bridgeOshbMorphologyPrimaryRaw"),
        ("BRIDGE_OSM_SECONDARY_RAW","bridgeOshbMorphologySecondaryRaw"),
    ]
    yield (node_id, "SOURCE_KEY", "BHSA_2021")
    lexeme_key = hebrew_letters_only(row.get("lexemeRaw"))
    if lexeme_key:
        yield (node_id, "HEBREW_LEXEME_LETTERS_V1", lexeme_key)
    for feature_key, field in mapping:
        value = row.get(field)
        if value not in (None, ""):
            yield (node_id, feature_key, str(value))


def phrase_features(node_id: str, rows: list[dict]) -> Iterator[tuple[object,...]]:
    first = rows[0]
    for key, field in (
        ("PHRASE_FUNCTION_RAW","phraseFunctionRaw"),
        ("PHRASE_TYPE_RAW","phraseTypeRaw"),
        ("PHRASE_RELATION_RAW","phraseRelationRaw"),
    ):
        value = first.get(field)
        if value not in (None, ""):
            yield (node_id, key, str(value))


def clause_features(node_id: str, rows: list[dict]) -> Iterator[tuple[object,...]]:
    first = rows[0]
    for key, field in (("CLAUSE_TYPE_RAW","clauseTypeRaw"),("CLAUSE_RELATION_RAW","clauseRelationRaw")):
        value = first.get(field)
        if value not in (None, ""):
            yield (node_id, key, str(value))


def process_book(
    book: dict,
    oshb_path: Path,
    bhsa_path: Path,
    crosswalk_path: Path,
    ids: dict[str,str],
    sql_dir: Path,
) -> dict:
    code = book["osisCode"]
    book_order = int(book["bookOrder"])
    oshb = load_ndjson(oshb_path)
    bhsa = load_ndjson(bhsa_path)
    crosswalk = load_ndjson(crosswalk_path)
    if not oshb or not bhsa:
        raise ValueError(f"{code}: source exports must both be non-empty")
    if {r.get("sourceKey") for r in oshb} != {"OSHB_MORPHHB"}:
        raise ValueError(f"{code}: OSHB sourceKey drift")
    if {r.get("sourceKey") for r in bhsa} != {"BHSA_2021"}:
        raise ValueError(f"{code}: BHSA sourceKey drift")

    oshb_refs = [ref_from_row(r, code) for r in oshb]
    bhsa_refs = [ref_from_row(r, code) for r in bhsa]
    all_refs = sorted(set(oshb_refs) | set(bhsa_refs), key=lambda ref: sequence(ref[1],ref[2]))
    refs_by_seq = {sequence(ref[1],ref[2]): ref for ref in all_refs}
    if len(refs_by_seq) != len(all_refs):
        raise ValueError(f"{code}: canonical reference sequence collision")

    oshb_id_counts = Counter(str(r.get("providerScopedWordId")) for r in oshb)
    bhsa_id_counts = Counter(str(r.get("providerScopedNodeId")) for r in bhsa)
    duplicate_oshb = sorted(k for k,v in oshb_id_counts.items() if v > 1)
    duplicate_bhsa = sorted(k for k,v in bhsa_id_counts.items() if v > 1)

    annotation_only_ids = {
        str(r["providerScopedNodeId"]) for r in bhsa if is_bhsa_annotation_only_node(r)
    }
    unclassified_empty_ids = {
        str(r["providerScopedNodeId"]) for r in bhsa
        if not (r.get("surfaceSourceExact") or r.get("consonantalSourceExact"))
        and str(r["providerScopedNodeId"]) not in annotation_only_ids
    }
    oshb_missing_surface = {
        str(r["providerScopedWordId"]) for r in oshb if not r.get("surfaceSourceExact")
    }

    candidates = [r for r in crosswalk if r.get("recordType") == "CANDIDATE_SPAN_MAPPING"]
    crosswalk_annotation = [r for r in crosswalk if r.get("recordType") == "ANNOTATION_ONLY_TARGET_NODE"]
    unresolved = [r for r in crosswalk if r.get("recordType") == "UNRESOLVED_REFERENCE"]
    unknown_types = {
        r.get("recordType") for r in crosswalk
        if r.get("recordType") not in {"CANDIDATE_SPAN_MAPPING","ANNOTATION_ONLY_TARGET_NODE","UNRESOLVED_REFERENCE"}
    }
    if unknown_types:
        raise ValueError(f"{code}: unknown crosswalk record types {sorted(unknown_types)}")
    if any(r.get("canonical") is not False or r.get("reviewStatus") != "CANDIDATE_AUTOMATED" for r in candidates):
        raise ValueError(f"{code}: candidate crosswalk state is not fail-closed")

    book_id = stable_uuid("book", code)
    reference_spans: dict[tuple[int,int,str], str] = {}
    phrase_words: dict[str,list[dict]] = defaultdict(list)
    clause_words: dict[str,list[dict]] = defaultdict(list)
    phrase_clause_pairs: set[tuple[str,str]] = set()
    for row in bhsa:
        if row.get("phraseNodeId") is not None:
            phrase_words[str(row["phraseNodeId"])].append(row)
        if row.get("clauseNodeId") is not None:
            clause_words[str(row["clauseNodeId"])].append(row)
        if row.get("phraseNodeId") is not None and row.get("clauseNodeId") is not None:
            phrase_clause_pairs.add((str(row["phraseNodeId"]),str(row["clauseNodeId"])))

    def group_span(rows: list[dict], kind: str) -> str:
        seqs = [sequence(ref_from_row(row, code)[1], ref_from_row(row, code)[2]) for row in rows]
        start, end = min(seqs), max(seqs)
        if start == end:
            return verse_span_id(refs_by_seq[start])
        key = (start,end,kind)
        sid = reference_spans.get(key)
        if sid is None:
            sid = range_span_id(code,start,end,kind)
            reference_spans[key] = sid
        return sid

    phrase_spans = {pid:group_span(rows,"BHSA_PHRASE") for pid,rows in phrase_words.items()}
    clause_spans = {cid:group_span(rows,"BHSA_CLAUSE") for cid,rows in clause_words.items()}

    oshb_node_ids = {
        str(r["providerScopedWordId"]): stable_uuid("analysis-node","OSHB_MORPHHB",str(r["providerScopedWordId"]))
        for r in oshb
    }
    bhsa_word_node_ids = {
        str(r["providerScopedNodeId"]): stable_uuid("analysis-node","BHSA_2021","word",str(r["providerScopedNodeId"]))
        for r in bhsa
    }
    phrase_node_ids = {pid:stable_uuid("analysis-node","BHSA_2021","phrase",pid) for pid in phrase_words}
    clause_node_ids = {cid:stable_uuid("analysis-node","BHSA_2021","clause",cid) for cid in clause_words}

    oshb_segment_ids: dict[str,str] = {}
    bhsa_segment_ids: dict[str,str] = {}
    body_part_targets = 0
    bridge_values = 0

    sql_path = sql_dir / f"{book_order:02d}-{code}.sql"
    with sql_path.open("w", encoding="utf-8") as out:
        out.write("\\set ON_ERROR_STOP on\nBEGIN;\n")

        atom_rows = []
        verse_span_rows = []
        for ref in all_refs:
            seq = sequence(ref[1],ref[2])
            atom_id = verse_atom_id(ref)
            span_id = verse_span_id(ref)
            atom_rows.append((atom_id,book_id,seq,"PROVIDER_VERSE_ZERO" if ref[2] == 0 else "VERSE",{"wb1":True,"chapter":ref[1],"verse":ref[2]}))
            verse_span_rows.append((span_id,book_id,atom_id,seq,atom_id,seq,"VERSE",{"wb1":True}))
        write_copy(out,"authoring.reference_atoms",[
            "reference_atom_id","book_id","sequence","atom_kind","metadata"
        ],atom_rows)

        range_rows = []
        for (start,end,kind),sid in sorted(reference_spans.items()):
            range_rows.append((
                sid,book_id,verse_atom_id(refs_by_seq[start]),start,verse_atom_id(refs_by_seq[end]),end,kind,
                {"wb1":True,"sourceKey":"BHSA_2021"}
            ))
        write_copy(out,"authoring.reference_spans",[
            "reference_span_id","book_id","start_atom_id","start_sequence","end_atom_id","end_sequence","span_kind","metadata"
        ],verse_span_rows + range_rows)

        labels: dict[tuple[str,str],tuple] = {}
        for row in oshb + bhsa:
            system = str(row["referenceSystemCode"])
            label = str(row["referenceLabel"])
            ref = ref_from_row(row,code)
            seq = sequence(ref[1],ref[2])
            key=(system,label)
            labels[key]=(
                stable_uuid("reference-label",system,label),
                stable_uuid("reference-system",system),
                book_id,label,ref[1],str(ref[2]),book_order*1_000_000+seq,
            )
        write_copy(out,"authoring.reference_labels",[
            "reference_label_id","reference_system_id","book_id","label","chapter_number","verse_label","sort_key"
        ],labels.values())
        write_copy(out,"authoring.reference_label_members",[
            "reference_label_id","book_id","reference_atom_id","atom_sequence","member_order"
        ],(
            (
                row[0],book_id,
                verse_atom_id(ref_from_row({"referenceLabel":row[3]},code)),
                sequence(ref_from_row({"referenceLabel":row[3]},code)[1],ref_from_row({"referenceLabel":row[3]},code)[2]),
                0
            )
            for row in labels.values()
        ))

        def text_segments() -> Iterator[tuple[object,...]]:
            for i,row in enumerate(oshb, start=1):
                provider_id=str(row["providerScopedWordId"])
                surface=row.get("surfaceSourceExact")
                if not surface:
                    continue
                segment_id=stable_uuid("text-segment","OSHB_MORPHHB",provider_id)
                oshb_segment_ids[provider_id]=segment_id
                ref=ref_from_row(row,code)
                yield (
                    segment_id,ids["oshbStream"],verse_span_id(ref),book_order*1_000_000+i,
                    "PERSISTED_CONTENT",surface,"WORD",hashlib.sha256(surface.encode("utf-8")).hexdigest(),
                    {"sourceKey":"OSHB_MORPHHB","providerScopedWordId":provider_id,"referenceLabel":row["referenceLabel"]}
                )
            for i,row in enumerate(bhsa, start=1):
                provider_id=str(row["providerScopedNodeId"])
                surface=row.get("surfaceSourceExact") or row.get("consonantalSourceExact")
                if not surface:
                    continue
                segment_id=stable_uuid("text-segment","BHSA_2021",provider_id)
                bhsa_segment_ids[provider_id]=segment_id
                ref=ref_from_row(row,code)
                yield (
                    segment_id,ids["bhsaStream"],verse_span_id(ref),book_order*1_000_000+i,
                    "PERSISTED_CONTENT",surface,"WORD",hashlib.sha256(surface.encode("utf-8")).hexdigest(),
                    {"sourceKey":"BHSA_2021","providerScopedNodeId":provider_id,"referenceLabel":row["referenceLabel"]}
                )
        write_copy(out,"authoring.text_segments",[
            "text_segment_id","text_stream_id","reference_span_id","segment_order","segment_storage_mode",
            "surface_original","segment_kind","content_hash","metadata"
        ],text_segments())

        def analysis_nodes() -> Iterator[tuple[object,...]]:
            for i,row in enumerate(oshb, start=1):
                provider_id=str(row["providerScopedWordId"])
                ref=ref_from_row(row,code)
                yield (
                    oshb_node_ids[provider_id],ids["oshbLayer"],"WORD",verse_span_id(ref),
                    book_order*1_000_000+i,provider_id,
                    {"sourceKey":"OSHB_MORPHHB","providerScopedWordId":provider_id,"referenceSystemCode":row["referenceSystemCode"],"referenceLabel":row["referenceLabel"],"textStatus":"TEXT_BEARING" if provider_id in oshb_segment_ids else "MISSING_SOURCE_SURFACE"}
                )
            for i,row in enumerate(bhsa, start=1):
                provider_id=str(row["providerScopedNodeId"])
                ref=ref_from_row(row,code)
                status=(
                    "ANNOTATION_ONLY_REVIEWED" if provider_id in annotation_only_ids
                    else "UNCLASSIFIED_EMPTY_SOURCE_SURFACE" if provider_id in unclassified_empty_ids
                    else "TEXT_BEARING"
                )
                yield (
                    bhsa_word_node_ids[provider_id],ids["bhsaLayer"],"WORD",verse_span_id(ref),
                    book_order*1_000_000+i,provider_id,
                    {
                        "sourceKey":"BHSA_2021","providerScopedNodeId":provider_id,
                        "referenceSystemCode":row["referenceSystemCode"],"referenceLabel":row["referenceLabel"],
                        "textStatus":status,"annotationOnly":provider_id in annotation_only_ids,
                        "phraseNodeId":row.get("phraseNodeId"),"clauseNodeId":row.get("clauseNodeId")
                    }
                )
            for i,pid in enumerate(sorted(phrase_words,key=lambda x:int(x)),start=1):
                yield (
                    phrase_node_ids[pid],ids["bhsaLayer"],"PHRASE",phrase_spans[pid],
                    book_order*1_000_000+i,f"phrase:{pid}",
                    {"sourceKey":"BHSA_2021","providerScopedPhraseNodeId":pid}
                )
            for i,cid in enumerate(sorted(clause_words,key=lambda x:int(x)),start=1):
                yield (
                    clause_node_ids[cid],ids["bhsaLayer"],"CLAUSE",clause_spans[cid],
                    book_order*1_000_000+i,f"clause:{cid}",
                    {"sourceKey":"BHSA_2021","providerScopedClauseNodeId":cid}
                )
        write_copy(out,"authoring.analysis_nodes",[
            "analysis_node_id","annotation_layer_id","node_type","reference_span_id","node_order","external_node_id","metadata"
        ],analysis_nodes())

        def features() -> Iterator[tuple[object,...]]:
            nonlocal body_part_targets, bridge_values
            for row in oshb:
                provider_id=str(row["providerScopedWordId"])
                node_id=oshb_node_ids[provider_id]
                yield (node_id,"SOURCE_KEY","OSHB_MORPHHB")
                for key,field in (("LEMMA_RAW","lemmaRaw"),("MORPH_RAW","morphRaw")):
                    value=row.get(field)
                    if value not in (None,""):
                        yield (node_id,key,str(value))
            for row in bhsa:
                provider_id=str(row["providerScopedNodeId"])
                node_id=bhsa_word_node_ids[provider_id]
                lexeme_key=hebrew_letters_only(row.get("lexemeRaw"))
                if lexeme_key=="עין":
                    body_part_targets += 1
                for feat in word_features_bhsa(node_id,row):
                    if feat[1] in {"BRIDGE_OSM_PRIMARY_RAW","BRIDGE_OSM_SECONDARY_RAW"}:
                        bridge_values += 1
                    yield feat
            for pid,rows in phrase_words.items():
                yield from phrase_features(phrase_node_ids[pid],rows)
            for cid,rows in clause_words.items():
                yield from clause_features(clause_node_ids[cid],rows)
        write_copy(out,"authoring.analysis_node_features",[
            "analysis_node_id","feature_key","feature_value"
        ],features())

        def node_segments() -> Iterator[tuple[object,...]]:
            for provider_id,node_id in oshb_node_ids.items():
                segment_id=oshb_segment_ids.get(provider_id)
                if segment_id:
                    yield (node_id,segment_id,0,"ORTHOGRAPHIC_WORD")
            for provider_id,node_id in bhsa_word_node_ids.items():
                segment_id=bhsa_segment_ids.get(provider_id)
                if segment_id:
                    yield (node_id,segment_id,0,"ORTHOGRAPHIC_WORD")
        write_copy(out,"authoring.analysis_node_segments",[
            "analysis_node_id","text_segment_id","member_order","membership_role"
        ],node_segments())

        edge_seen: set[tuple[str,str,str]] = set()
        for row in bhsa:
            word_id=bhsa_word_node_ids[str(row["providerScopedNodeId"])]
            if row.get("phraseNodeId") is not None:
                edge_seen.add((word_id,phrase_node_ids[str(row["phraseNodeId"])],"MEMBER_OF_PHRASE"))
            if row.get("clauseNodeId") is not None:
                edge_seen.add((word_id,clause_node_ids[str(row["clauseNodeId"])],"MEMBER_OF_CLAUSE"))
        for pid,cid in phrase_clause_pairs:
            edge_seen.add((phrase_node_ids[pid],clause_node_ids[cid],"MEMBER_OF_CLAUSE"))
        write_copy(out,"authoring.analysis_edges",[
            "analysis_edge_id","annotation_layer_id","from_node_id","to_node_id","relation_type","relation_ontology","properties"
        ],(
            (
                stable_uuid("analysis-edge","BHSA_2021",from_node,to_node,relation),
                ids["bhsaLayer"],from_node,to_node,relation,"BHSA_2021_MEMBERSHIP_V1",{"sourceKey":"BHSA_2021"}
            )
            for from_node,to_node,relation in sorted(edge_seen)
        ))

        mapping_groups=[]
        from_members=[]
        to_members=[]
        crosswalk_hash=sha256_file(crosswalk_path)
        for candidate in candidates:
            ref_obj=candidate["reference"]
            ref=(str(ref_obj["book"]),int(ref_obj["chapter"]),int(ref_obj["verse"]))
            if ref[0] != code:
                raise ValueError(f"{code}: crosswalk candidate escaped book: {ref}")
            source_ids=[str(v) for v in candidate["sourceProviderScopedWordIds"]]
            target_ids=[str(v) for v in candidate["targetProviderScopedNodeIds"]]
            missing_source=[x for x in source_ids if x not in oshb_node_ids]
            missing_target=[x for x in target_ids if x not in bhsa_word_node_ids]
            if missing_source or missing_target:
                raise ValueError(f"{code}: candidate mapping references absent nodes source={missing_source} target={missing_target}")
            if set(target_ids) & annotation_only_ids:
                raise ValueError(f"{code}: reviewed annotation-only BHSA node entered orthographic crosswalk")
            group_id=stable_uuid(
                "cross-annotation-mapping-group",code,ref[1],ref[2],
                ",".join(source_ids),",".join(target_ids),candidate["mappingMethod"]
            )
            mapping_groups.append((
                group_id,ids["oshbLayer"],ids["bhsaLayer"],verse_span_id(ref),
                "ORTHOGRAPHIC_SPAN_CANDIDATE",candidate["mappingMethod"],candidate["reviewStatus"],
                False,None,
                {
                    "signatureAlgorithm":candidate["signatureAlgorithm"],
                    "consonantalSignature":candidate["consonantalSignature"],
                    "sourceCount":candidate["sourceCount"],"targetCount":candidate["targetCount"],
                    "crosswalkBookSha256":crosswalk_hash,
                }
            ))
            from_members.extend((group_id,ids["oshbLayer"],oshb_node_ids[x],i) for i,x in enumerate(source_ids))
            to_members.extend((group_id,ids["bhsaLayer"],bhsa_word_node_ids[x],i) for i,x in enumerate(target_ids))
        write_copy(out,"authoring.cross_annotation_mapping_groups",[
            "mapping_group_id","from_annotation_layer_id","to_annotation_layer_id","reference_span_id",
            "mapping_type","mapping_method","review_status","canonical","confidence","properties"
        ],mapping_groups)
        write_copy(out,"authoring.cross_annotation_mapping_from_members",[
            "mapping_group_id","from_annotation_layer_id","from_node_id","member_order"
        ],from_members)
        write_copy(out,"authoring.cross_annotation_mapping_to_members",[
            "mapping_group_id","to_annotation_layer_id","to_node_id","member_order"
        ],to_members)

        out.write("COMMIT;\n")

    psql_file(sql_path)
    sql_path.unlink(missing_ok=True)

    unresolved_summary = []
    for row in unresolved:
        unresolved_summary.append({
            "reference":row.get("reference"),
            "reason":row.get("reason"),
            "oshbWordCount":row.get("oshbWordCount"),
            "bhsaWordCount":row.get("bhsaWordCount"),
            "oshbStreamSha256":row.get("oshbStreamSha256"),
            "bhsaStreamSha256":row.get("bhsaStreamSha256"),
            "firstDifferenceIndex":row.get("firstDifferenceIndex"),
            "oshbEmptySignatureTokens":row.get("oshbEmptySignatureTokens"),
            "bhsaEmptySignatureTokens":row.get("bhsaEmptySignatureTokens"),
        })

    return {
        "book":code,
        "bookOrder":book_order,
        "sourceHashes":{
            "oshb":sha256_file(oshb_path),
            "bhsa":sha256_file(bhsa_path),
            "crosswalk":sha256_file(crosswalk_path),
        },
        "source":{
            "oshbWordRecords":len(oshb),
            "bhsaWordRecords":len(bhsa),
            "oshbReferenceLabels":len(set(r["referenceLabel"] for r in oshb)),
            "bhsaReferenceLabels":len(set(r["referenceLabel"] for r in bhsa)),
            "canonicalReferenceAtoms":len(all_refs),
            "oshbOnlyCanonicalReferences":[f"{r[0]}.{r[1]}.{r[2]}" for r in sorted(set(oshb_refs)-set(bhsa_refs))],
            "bhsaOnlyCanonicalReferences":[f"{r[0]}.{r[1]}.{r[2]}" for r in sorted(set(bhsa_refs)-set(oshb_refs))],
            "duplicateOshbProviderIds":duplicate_oshb,
            "duplicateBhsaProviderIds":duplicate_bhsa,
            "oshbMissingSurfaceProviderIds":sorted(oshb_missing_surface),
            "reviewedAnnotationOnlyBhsaProviderIds":sorted(annotation_only_ids,key=lambda x:int(x)),
            "unclassifiedEmptyBhsaProviderIds":sorted(unclassified_empty_ids,key=lambda x:int(x)),
        },
        "structure":{
            "bhsaPhraseNodes":len(phrase_words),
            "bhsaClauseNodes":len(clause_words),
            "crossVerseBhsaPhraseNodes":sum(1 for pid in phrase_words if phrase_spans[pid] not in {verse_span_id(ref_from_row(row,code)) for row in phrase_words[pid]}),
            "crossVerseBhsaClauseNodes":sum(1 for cid in clause_words if clause_spans[cid] not in {verse_span_id(ref_from_row(row,code)) for row in clause_words[cid]}),
            "bhsaMembershipEdges":len(edge_seen),
            "bridgeFeatureValues":bridge_values,
            "projectBodyPartTargetNodes":body_part_targets,
        },
        "crosswalk":{
            "candidateMappingGroups":len(candidates),
            "nonOneToOneCandidateGroups":sum(1 for r in candidates if r.get("sourceCount")!=1 or r.get("targetCount")!=1),
            "annotationOnlyRecordsEmitted":len(crosswalk_annotation),
            "unresolvedReferences":len(unresolved),
            "unresolved":unresolved_summary,
        },
        "expectedImport":{
            "oshbWordNodes":len(oshb),
            "bhsaWordNodes":len(bhsa),
            "oshbTextSegments":len(oshb_segment_ids),
            "bhsaTextSegments":len(bhsa_segment_ids),
            "bhsaPhraseNodes":len(phrase_words),
            "bhsaClauseNodes":len(clause_words),
            "mappingGroups":len(candidates),
        }
    }


def database_counts(ids: dict[str,str]) -> dict[str,dict[str,dict[str,int]]]:
    node_sql = f"""
SELECT b.osis_code, f.framework_key, n.node_type, count(*)
FROM authoring.analysis_nodes n
JOIN authoring.annotation_layers l USING (annotation_layer_id)
JOIN authoring.annotation_frameworks f USING (annotation_framework_id)
JOIN authoring.reference_spans rs USING (reference_span_id)
JOIN authoring.biblical_books b USING (book_id)
WHERE l.annotation_layer_id IN ('{ids["oshbLayer"]}'::uuid,'{ids["bhsaLayer"]}'::uuid)
GROUP BY b.osis_code,f.framework_key,n.node_type
ORDER BY b.osis_code,f.framework_key,n.node_type;
"""
    segment_sql = f"""
SELECT b.osis_code, ts.text_stream_id, count(*)
FROM authoring.text_segments s
JOIN authoring.text_streams ts USING (text_stream_id)
JOIN authoring.reference_spans rs USING (reference_span_id)
JOIN authoring.biblical_books b USING (book_id)
WHERE ts.text_stream_id IN ('{ids["oshbStream"]}'::uuid,'{ids["bhsaStream"]}'::uuid)
GROUP BY b.osis_code,ts.text_stream_id
ORDER BY b.osis_code,ts.text_stream_id;
"""
    mapping_sql = """
SELECT b.osis_code,count(*)
FROM authoring.cross_annotation_mapping_groups g
JOIN authoring.reference_spans rs USING (reference_span_id)
JOIN authoring.biblical_books b USING (book_id)
GROUP BY b.osis_code ORDER BY b.osis_code;
"""
    atom_sql = """
SELECT b.osis_code,count(*)
FROM authoring.reference_atoms a
JOIN authoring.biblical_books b USING (book_id)
GROUP BY b.osis_code ORDER BY b.osis_code;
"""

    nodes: dict[str,dict[str,dict[str,int]]] = defaultdict(lambda:defaultdict(dict))
    for line in psql_query(node_sql).splitlines():
        if not line: continue
        book,framework,node_type,count=line.split("\t")
        nodes[book][framework][node_type]=int(count)
    segments: dict[str,dict[str,int]] = defaultdict(dict)
    for line in psql_query(segment_sql).splitlines():
        if not line: continue
        book,stream,count=line.split("\t")
        source="OSHB_MORPHHB" if stream==ids["oshbStream"] else "BHSA_2021"
        segments[book][source]=int(count)
    mappings={}
    for line in psql_query(mapping_sql).splitlines():
        if not line: continue
        book,count=line.split("\t")
        mappings[book]=int(count)
    atoms={}
    for line in psql_query(atom_sql).splitlines():
        if not line: continue
        book,count=line.split("\t")
        atoms[book]=int(count)
    return {
        "nodes":{k:{fk:dict(nv) for fk,nv in fv.items()} for k,fv in nodes.items()},
        "segments":{k:dict(v) for k,v in segments.items()},
        "mappingGroups":mappings,
        "referenceAtoms":atoms,
    }


def verify_parity(books: list[dict], per_book: list[dict], db: dict, ids: dict[str,str]) -> list[dict]:
    failures=[]
    by_book={row["book"]:row for row in per_book}
    for book in books:
        code=book["osisCode"]
        expected=by_book.get(code)
        if expected is None:
            failures.append({"book":code,"kind":"BOOK_IMPORT_MISSING"})
            continue
        exp=expected["expectedImport"]
        node_counts=db["nodes"].get(code,{})
        oshb_nodes=node_counts.get("OSHB_MORPHHB_REAL",{}).get("WORD",0)
        bhsa_nodes=node_counts.get("BHSA_2021_REAL",{})
        checks={
            "oshbWordNodes":(exp["oshbWordNodes"],oshb_nodes),
            "bhsaWordNodes":(exp["bhsaWordNodes"],bhsa_nodes.get("WORD",0)),
            "bhsaPhraseNodes":(exp["bhsaPhraseNodes"],bhsa_nodes.get("PHRASE",0)),
            "bhsaClauseNodes":(exp["bhsaClauseNodes"],bhsa_nodes.get("CLAUSE",0)),
            "oshbTextSegments":(exp["oshbTextSegments"],db["segments"].get(code,{}).get("OSHB_MORPHHB",0)),
            "bhsaTextSegments":(exp["bhsaTextSegments"],db["segments"].get(code,{}).get("BHSA_2021",0)),
            "mappingGroups":(exp["mappingGroups"],db["mappingGroups"].get(code,0)),
            "referenceAtoms":(expected["source"]["canonicalReferenceAtoms"],db["referenceAtoms"].get(code,0)),
        }
        for kind,(wanted,actual) in checks.items():
            if wanted!=actual:
                failures.append({"book":code,"kind":kind,"expected":wanted,"actual":actual})
    return failures


def main() -> int:
    parser=argparse.ArgumentParser(description="Import the complete configured pinned OSHB/BHSA corpus into PostgreSQL Authoring and emit WB-1 coverage evidence.")
    parser.add_argument("--oshb-dir",type=Path,required=True)
    parser.add_argument("--bhsa-dir",type=Path,required=True)
    parser.add_argument("--crosswalk-dir",type=Path,required=True)
    parser.add_argument("--canon",type=Path,default=DEFAULT_CANON)
    parser.add_argument("--registry",type=Path,default=DEFAULT_REGISTRY)
    parser.add_argument("--cache-root",type=Path,default=DEFAULT_CACHE_ROOT)
    parser.add_argument("--report",type=Path,required=True)
    parser.add_argument("--sql-dir",type=Path)
    args=parser.parse_args()

    canon_system,books=load_canon(args.canon)
    registry=json.loads(args.registry.read_text(encoding="utf-8"))
    sources=source_index(registry)
    manifests=load_source_manifests(registry,args.cache_root)
    ids=shared_ids(sources)
    sql_dir=args.sql_dir or Path(tempfile.mkdtemp(prefix="wb1-sql-"))
    sql_dir.mkdir(parents=True,exist_ok=True)

    setup_path=sql_dir/"00-shared.sql"
    write_shared_setup(setup_path,canon_system,books,sources,manifests,ids)
    psql_file(setup_path)
    setup_path.unlink(missing_ok=True)

    per_book=[]
    importer_errors=[]
    global_oshb_ids=set()
    global_bhsa_ids=set()
    global_duplicate_oshb=[]
    global_duplicate_bhsa=[]

    for book in books:
        code=book["osisCode"]
        paths={
            "oshb":args.oshb_dir/f"{code}.ndjson",
            "bhsa":args.bhsa_dir/f"{code}.ndjson",
            "crosswalk":args.crosswalk_dir/f"{code}.ndjson",
        }
        missing=[str(path) for path in paths.values() if not path.is_file()]
        if missing:
            importer_errors.append({"book":code,"stage":"INPUT","error":"missing input","paths":missing})
            continue
        try:
            # Detect cross-book provider-ID duplication before DB insertion.
            oshb_rows=load_ndjson(paths["oshb"])
            bhsa_rows=load_ndjson(paths["bhsa"])
            for row in oshb_rows:
                pid=str(row.get("providerScopedWordId"))
                if pid in global_oshb_ids: global_duplicate_oshb.append(pid)
                global_oshb_ids.add(pid)
            for row in bhsa_rows:
                pid=str(row.get("providerScopedNodeId"))
                if pid in global_bhsa_ids: global_duplicate_bhsa.append(pid)
                global_bhsa_ids.add(pid)

            evidence=process_book(book,paths["oshb"],paths["bhsa"],paths["crosswalk"],ids,sql_dir)
            per_book.append(evidence)
            print(f"WB-1 imported {code}: OSHB={evidence['source']['oshbWordRecords']} BHSA={evidence['source']['bhsaWordRecords']} unresolved={evidence['crosswalk']['unresolvedReferences']}")
        except Exception as exc:
            importer_errors.append({"book":code,"stage":"RELATIONAL_IMPORT","error":f"{type(exc).__name__}: {exc}"})
            print(f"WB-1 import failed for {code}: {type(exc).__name__}: {exc}", flush=True)

    db=database_counts(ids)
    parity_failures=verify_parity(books,per_book,db,ids)

    imported_books={row["book"] for row in per_book}
    expected_books=[b["osisCode"] for b in books]
    missing_books=[code for code in expected_books if code not in imported_books]
    source_duplicate_books=[
        {
            "book":row["book"],
            "oshb":row["source"]["duplicateOshbProviderIds"],
            "bhsa":row["source"]["duplicateBhsaProviderIds"],
        }
        for row in per_book
        if row["source"]["duplicateOshbProviderIds"] or row["source"]["duplicateBhsaProviderIds"]
    ]
    source_missing_surface=sum(len(row["source"]["oshbMissingSurfaceProviderIds"]) for row in per_book)
    unclassified_empty=sum(len(row["source"]["unclassifiedEmptyBhsaProviderIds"]) for row in per_book)
    annotation_only=sum(len(row["source"]["reviewedAnnotationOnlyBhsaProviderIds"]) for row in per_book)
    unresolved=sum(row["crosswalk"]["unresolvedReferences"] for row in per_book)
    serving_rows=int(psql_query("SELECT count(*) FROM serving.corpus_nodes;").strip() or "0")
    canon_rows=int(psql_query("SELECT count(*) FROM authoring.canon_books WHERE included;").strip() or "0")

    source_integrity_pass=(
        not importer_errors
        and not missing_books
        and not source_duplicate_books
        and not global_duplicate_oshb
        and not global_duplicate_bhsa
        and source_missing_surface==0
        and not parity_failures
        and canon_rows==len(books)
    )
    rights_boundary_pass=(serving_rows==0)

    source_hash_index=[
        {
            "book":row["book"],
            "bookOrder":row["bookOrder"],
            **row["sourceHashes"],
        }
        for row in sorted(per_book,key=lambda r:r["bookOrder"])
    ]
    report={
        "schemaVersion":"1.0",
        "milestone":"WB-1",
        "canonSystem":{**canon_system,"configuredBookCount":len(books),"includedBooks":expected_books},
        "sourcePins":{
            key:{
                "commitSha":sources[key]["pin"]["commitSha"],
                "datasetVersion":sources[key]["pin"].get("datasetVersion"),
                "manifestSha256":manifests[key]["manifestSha256"],
            }
            for key in sorted(EXPECTED_SOURCE_KEYS)
        },
        "aggregateExportHash":canonical_hash(source_hash_index),
        "books":sorted(per_book,key=lambda r:r["bookOrder"]),
        "totals":{
            "configuredBooks":len(books),
            "importedBooks":len(per_book),
            "oshbWordRecords":sum(r["source"]["oshbWordRecords"] for r in per_book),
            "bhsaWordRecords":sum(r["source"]["bhsaWordRecords"] for r in per_book),
            "canonicalReferenceAtoms":sum(r["source"]["canonicalReferenceAtoms"] for r in per_book),
            "reviewedAnnotationOnlyBhsaNodes":annotation_only,
            "unclassifiedEmptyBhsaNodes":unclassified_empty,
            "bhsaPhraseNodes":sum(r["structure"]["bhsaPhraseNodes"] for r in per_book),
            "bhsaClauseNodes":sum(r["structure"]["bhsaClauseNodes"] for r in per_book),
            "crossVerseBhsaPhraseNodes":sum(r["structure"]["crossVerseBhsaPhraseNodes"] for r in per_book),
            "crossVerseBhsaClauseNodes":sum(r["structure"]["crossVerseBhsaClauseNodes"] for r in per_book),
            "bhsaMembershipEdges":sum(r["structure"]["bhsaMembershipEdges"] for r in per_book),
            "bridgeFeatureValues":sum(r["structure"]["bridgeFeatureValues"] for r in per_book),
            "projectBodyPartTargetNodes":sum(r["structure"]["projectBodyPartTargetNodes"] for r in per_book),
            "candidateMappingGroups":sum(r["crosswalk"]["candidateMappingGroups"] for r in per_book),
            "nonOneToOneCandidateGroups":sum(r["crosswalk"]["nonOneToOneCandidateGroups"] for r in per_book),
            "unresolvedCrossFrameworkReferences":unresolved,
            "oshbMissingSurfaceRecords":source_missing_surface,
            "servingCorpusRows":serving_rows,
        },
        "coverage":{
            "missingConfiguredBooks":missing_books,
            "perBookDuplicateProviderIds":source_duplicate_books,
            "crossBookDuplicateOshbProviderIds":sorted(set(global_duplicate_oshb)),
            "crossBookDuplicateBhsaProviderIds":sorted(set(global_duplicate_bhsa)),
            "parityFailures":parity_failures,
            "importerErrors":importer_errors,
            "retries":0,
            "unresolvedMappingsAreSourceIngestionFailures":False,
        },
        "databaseCounts":db,
        "gate":{
            "sourceIngestionIntegrity":source_integrity_pass,
            "rightsBoundaryServingRemainsEmpty":rights_boundary_pass,
            "coreFreezeWb002EvidenceReady":source_integrity_pass and rights_boundary_pass,
            "note":"Unresolved cross-framework mappings are explicit research exceptions and do not count as silent source-record drops."
        },
        "servingProjectionWritten":False,
    }

    args.report.parent.mkdir(parents=True,exist_ok=True)
    args.report.write_text(json.dumps(report,ensure_ascii=False,sort_keys=True,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(report,ensure_ascii=False,sort_keys=True))

    if not source_integrity_pass or not rights_boundary_pass:
        return 2
    return 0


if __name__=="__main__":
    raise SystemExit(main())
