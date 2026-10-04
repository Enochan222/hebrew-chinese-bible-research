#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import sys
import uuid
import xml.etree.ElementTree as ET
from contextlib import ExitStack
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from scripts.corpora.build_oshb_coverage_index import (  # noqa: E402
    OSIS_BOOK_NAMES,
    OSIS_BOOK_ORDER,
    REFERENCE_RE,
    discover_book_files,
    local_name,
    source_pin,
)

DEFAULT_INPUT = ROOT / ".local/corpora/oshb-morphhb/wlc"
DEFAULT_SOURCE_MANIFEST = ROOT / ".local/corpora/oshb-morphhb/source-manifest.json"
DEFAULT_OUTPUT = ROOT / ".local/db-import/oshb"
IMPORTER_VERSION = "oshb-whole-bible-base-1"
NS = uuid.UUID("c7778a15-0c47-4abc-a998-cbb5534cdb52")


def stable_id(kind: str, *parts: object) -> str:
    return str(uuid.uuid5(NS, ":".join([kind, *(str(p) for p in parts)])))


def file_sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def compact_json(value: object) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


class Tsv:
    def __init__(self, fh):
        self.writer = csv.writer(fh, delimiter="\t", quotechar='"', lineterminator="\n")

    def row(self, *values: object | None) -> None:
        self.writer.writerow(["\\N" if value is None else value for value in values])


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Build deterministic PostgreSQL COPY loadset for the complete pinned OSHB baseline corpus."
    )
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--source-manifest", type=Path, default=DEFAULT_SOURCE_MANIFEST)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()

    if not args.input.is_dir():
        raise SystemExit(f"OSHB input missing at {args.input}; run fetch_sources.py first")
    if not args.source_manifest.is_file():
        raise SystemExit(f"OSHB source manifest missing at {args.source_manifest}")

    commit = source_pin()
    source_manifest = json.loads(args.source_manifest.read_text(encoding="utf-8"))
    if source_manifest.get("sourceKey") != "OSHB_MORPHHB" or source_manifest.get("commitSha") != commit:
        raise SystemExit("OSHB source manifest does not match the active pinned source")
    source_manifest_sha = file_sha256(args.source_manifest)

    args.output_dir.mkdir(parents=True, exist_ok=True)

    reference_system_id = stable_id("reference-system", "OSHB_OSIS")
    work_id = stable_id("textual-work", "OSHB_WLC")
    edition_id = stable_id("textual-edition", "OSHB_WLC", commit)
    expression_id = stable_id("digital-expression", "OSHB_WLC", commit)
    text_stream_id = stable_id("text-stream", "OSHB_WLC", commit, "BASE")
    corpus_release_id = stable_id("corpus-release", "OSHB_MORPHHB", commit)
    framework_id = stable_id("annotation-framework", "OSHB_MORPHHB")
    morphology_layer_id = stable_id("annotation-layer", "OSHB_MORPHHB", commit, "MORPHOLOGY")

    files = {
        "biblical_books": "biblical_books.tsv",
        "reference_systems": "reference_systems.tsv",
        "reference_atoms": "reference_atoms.tsv",
        "reference_spans": "reference_spans.tsv",
        "reference_labels": "reference_labels.tsv",
        "reference_label_members": "reference_label_members.tsv",
        "textual_works": "textual_works.tsv",
        "textual_editions": "textual_editions.tsv",
        "digital_expressions": "digital_expressions.tsv",
        "text_streams": "text_streams.tsv",
        "research_objects": "research_objects.tsv",
        "annotation_frameworks": "annotation_frameworks.tsv",
        "corpus_releases": "corpus_releases.tsv",
        "annotation_layers": "annotation_layers.tsv",
        "text_segments": "text_segments.tsv",
        "analysis_nodes": "analysis_nodes.tsv",
        "analysis_node_features": "analysis_node_features.tsv",
        "analysis_node_segments": "analysis_node_segments.tsv",
    }

    counts = {key: 0 for key in files}
    seen_provider_word_ids: set[str] = set()
    seen_references: set[str] = set()
    global_segment_order = 0

    with ExitStack() as stack:
        writers = {}
        for key, filename in files.items():
            fh = stack.enter_context((args.output_dir / filename).open("w", encoding="utf-8", newline=""))
            writers[key] = Tsv(fh)

        for book in OSIS_BOOK_ORDER:
            book_id = stable_id("book", book)
            writers["biblical_books"].row(book_id, book, OSIS_BOOK_NAMES[book])
            counts["biblical_books"] += 1

        writers["reference_systems"].row(reference_system_id, "OSHB_OSIS", "Open Scriptures OSIS reference labels")
        counts["reference_systems"] += 1
        writers["textual_works"].row(
            work_id, "HEBREW_BIBLE", "Westminster Leningrad Codex", "hbo", "Hebr",
            "Provider-scoped OSHB/WLC baseline work identity for the initial whole-Bible import."
        )
        counts["textual_works"] += 1
        writers["textual_editions"].row(
            edition_id, work_id, "OSHB pinned WLC source", None, "PROVIDER_PINNED",
            compact_json({"sourceKey":"OSHB_MORPHHB","sourceCommitSha":commit})
        )
        counts["textual_editions"] += 1
        writers["digital_expressions"].row(
            expression_id, edition_id, work_id, "OSHB morphhb digital expression", commit,
            source_manifest_sha,
            compact_json({"sourceKey":"OSHB_MORPHHB","sourceManifestSha256":source_manifest_sha})
        )
        counts["digital_expressions"] += 1
        writers["text_streams"].row(text_stream_id, expression_id, "BASE", commit)
        counts["text_streams"] += 1
        writers["research_objects"].row(corpus_release_id, "CORPUS_RELEASE")
        writers["research_objects"].row(morphology_layer_id, "ANNOTATION_LAYER")
        counts["research_objects"] += 2
        writers["annotation_frameworks"].row(
            framework_id, "OSHB_MORPHHB", "Open Scriptures Hebrew Bible morphology",
            "Provider-scoped word/lemma/morphology framework; not universal phrase/clause identity.", commit
        )
        counts["annotation_frameworks"] += 1
        writers["corpus_releases"].row(
            corpus_release_id, expression_id, "OSHB whole-Bible baseline", commit,
            IMPORTER_VERSION, source_manifest_sha
        )
        counts["corpus_releases"] += 1
        writers["annotation_layers"].row(
            morphology_layer_id, corpus_release_id, framework_id, "MORPHOLOGY", commit,
            source_manifest_sha,
            compact_json({"sourceKey":"OSHB_MORPHHB","providerScoped":True,"wholeBibleBaseline":True})
        )
        counts["annotation_layers"] += 1

        for book_order, (book, path) in enumerate(discover_book_files(args.input), start=1):
            book_id = stable_id("book", book)
            verse_sequence = 0
            current_reference: str | None = None
            current_span_id: str | None = None
            word_order = 0

            for event, elem in ET.iterparse(path, events=("start", "end")):
                name = local_name(elem.tag)
                if event == "start" and name == "verse":
                    current_reference = elem.attrib.get("osisID")
                    if not current_reference:
                        raise RuntimeError(f"verse without osisID in {path}")
                    if current_reference in seen_references:
                        raise RuntimeError(f"duplicate OSHB reference: {current_reference}")
                    match = REFERENCE_RE.fullmatch(current_reference)
                    if not match or match.group("book") != book:
                        raise RuntimeError(f"invalid/mismatched OSHB reference {current_reference!r} in {book}")
                    seen_references.add(current_reference)
                    verse_sequence += 1
                    word_order = 0
                    chapter = int(match.group("chapter"))
                    verse = int(match.group("verse"))

                    atom_id = stable_id("reference-atom", "OSHB_OSIS", current_reference)
                    current_span_id = stable_id("reference-span", "OSHB_OSIS", current_reference)
                    label_id = stable_id("reference-label", "OSHB_OSIS", current_reference)
                    sort_key = book_order * 1_000_000 + chapter * 1_000 + verse

                    writers["reference_atoms"].row(
                        atom_id, book_id, verse_sequence, "VERSE",
                        compact_json({"referenceSystemCode":"OSHB_OSIS","referenceLabel":current_reference})
                    )
                    counts["reference_atoms"] += 1
                    writers["reference_spans"].row(
                        current_span_id, book_id, atom_id, verse_sequence, atom_id, verse_sequence, "VERSE",
                        compact_json({"referenceSystemCode":"OSHB_OSIS","referenceLabel":current_reference})
                    )
                    counts["reference_spans"] += 1
                    writers["reference_labels"].row(
                        label_id, reference_system_id, book_id, current_reference,
                        chapter, str(verse), sort_key
                    )
                    counts["reference_labels"] += 1
                    writers["reference_label_members"].row(label_id, book_id, atom_id, verse_sequence, 0)
                    counts["reference_label_members"] += 1

                elif event == "end" and name == "w" and current_reference and current_span_id:
                    provider_word_id = elem.attrib.get("id")
                    if not provider_word_id:
                        raise RuntimeError(f"OSHB word without provider id at {current_reference}")
                    if provider_word_id in seen_provider_word_ids:
                        raise RuntimeError(f"duplicate OSHB provider word id: {provider_word_id}")
                    seen_provider_word_ids.add(provider_word_id)
                    word_order += 1
                    global_segment_order += 1
                    surface = "".join(elem.itertext())
                    if not surface:
                        raise RuntimeError(f"empty OSHB word {provider_word_id} at {current_reference}")
                    lemma = elem.attrib.get("lemma")
                    morph = elem.attrib.get("morph")
                    segment_id = stable_id("text-segment", "OSHB_MORPHHB", commit, provider_word_id)
                    node_id = stable_id("analysis-node", "OSHB_MORPHHB", commit, provider_word_id)
                    content_hash = hashlib.sha256(surface.encode("utf-8")).hexdigest()
                    metadata = compact_json({
                        "sourceKey":"OSHB_MORPHHB",
                        "providerScopedWordId":provider_word_id,
                        "referenceLabel":current_reference,
                        "wordOrderInVerse":word_order,
                        "unicodePolicy":"PRESERVE_SOURCE_CODEPOINT_ORDER_DO_NOT_NFC",
                    })
                    writers["text_segments"].row(
                        segment_id, text_stream_id, current_span_id, global_segment_order,
                        "PERSISTED_CONTENT", surface, "WORD", content_hash, metadata
                    )
                    counts["text_segments"] += 1
                    writers["analysis_nodes"].row(
                        node_id, morphology_layer_id, "WORD", current_span_id,
                        global_segment_order, provider_word_id, metadata
                    )
                    counts["analysis_nodes"] += 1
                    for key, value in (
                        ("provider_word_id", provider_word_id),
                        ("reference_label", current_reference),
                        ("word_order_in_verse", str(word_order)),
                        ("lemma_raw", lemma),
                        ("morph_raw", morph),
                    ):
                        if value is not None and value != "":
                            writers["analysis_node_features"].row(node_id, key, value)
                            counts["analysis_node_features"] += 1
                    writers["analysis_node_segments"].row(node_id, segment_id, 0, "ORTHOGRAPHIC_HOST")
                    counts["analysis_node_segments"] += 1
                    elem.clear()

                elif event == "end" and name == "verse":
                    if current_reference is None:
                        raise RuntimeError(f"verse end without active reference in {path}")
                    if word_order == 0:
                        raise RuntimeError(f"OSHB verse {current_reference} imported zero words")
                    current_reference = None
                    current_span_id = None
                    elem.clear()

    if counts["biblical_books"] != len(OSIS_BOOK_ORDER):
        raise RuntimeError("whole-Bible importer did not emit complete expected OSHB book set")
    if counts["reference_labels"] != len(seen_references):
        raise RuntimeError("reference label count does not match unique references")
    if counts["text_segments"] != len(seen_provider_word_ids):
        raise RuntimeError("text segment count does not match unique provider word IDs")
    if counts["text_segments"] != counts["analysis_nodes"] or counts["analysis_nodes"] != counts["analysis_node_segments"]:
        raise RuntimeError("word segment/node/membership counts diverged")

    manifest = {
        "schemaVersion": "1.0",
        "importerVersion": IMPORTER_VERSION,
        "sourceKey": "OSHB_MORPHHB",
        "sourceCommitSha": commit,
        "sourceManifestSha256": source_manifest_sha,
        "referenceSystemCode": "OSHB_OSIS",
        "ids": {
            "referenceSystemId": reference_system_id,
            "textualWorkId": work_id,
            "textualEditionId": edition_id,
            "digitalExpressionId": expression_id,
            "textStreamId": text_stream_id,
            "corpusReleaseId": corpus_release_id,
            "annotationFrameworkId": framework_id,
            "morphologyLayerId": morphology_layer_id,
        },
        "rowCounts": counts,
    }
    (args.output_dir / "import-manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )

    copy_specs = [
        ("biblical_books", "authoring.biblical_books", "book_id,osis_code,english_name"),
        ("reference_systems", "authoring.reference_systems", "reference_system_id,code,name"),
        ("reference_atoms", "authoring.reference_atoms", "reference_atom_id,book_id,sequence,atom_kind,metadata"),
        ("reference_spans", "authoring.reference_spans", "reference_span_id,book_id,start_atom_id,start_sequence,end_atom_id,end_sequence,span_kind,metadata"),
        ("reference_labels", "authoring.reference_labels", "reference_label_id,reference_system_id,book_id,label,chapter_number,verse_label,sort_key"),
        ("reference_label_members", "authoring.reference_label_members", "reference_label_id,book_id,reference_atom_id,atom_sequence,member_order"),
        ("textual_works", "authoring.textual_works", "textual_work_id,work_kind,canonical_name,language_code,script_code,description"),
        ("textual_editions", "authoring.textual_editions", "textual_edition_id,textual_work_id,edition_label,publication_year,edition_status,metadata"),
        ("digital_expressions", "authoring.digital_expressions", "digital_expression_id,textual_edition_id,textual_work_id,expression_label,expression_version,source_checksum,metadata"),
        ("text_streams", "authoring.text_streams", "text_stream_id,digital_expression_id,stream_type,stream_version"),
        ("research_objects", "authoring.research_objects", "research_object_id,object_type"),
        ("annotation_frameworks", "authoring.annotation_frameworks", "annotation_framework_id,framework_key,name,description,ontology_version"),
        ("corpus_releases", "authoring.corpus_releases", "corpus_release_id,digital_expression_id,release_name,release_version,importer_version,source_checksum"),
        ("annotation_layers", "authoring.annotation_layers", "annotation_layer_id,corpus_release_id,annotation_framework_id,layer_kind,layer_version,content_hash,metadata"),
        ("text_segments", "authoring.text_segments", "text_segment_id,text_stream_id,reference_span_id,segment_order,segment_storage_mode,surface_original,segment_kind,content_hash,metadata"),
        ("analysis_nodes", "authoring.analysis_nodes", "analysis_node_id,annotation_layer_id,node_type,reference_span_id,node_order,external_node_id,metadata"),
        ("analysis_node_features", "authoring.analysis_node_features", "analysis_node_id,feature_key,feature_value"),
        ("analysis_node_segments", "authoring.analysis_node_segments", "analysis_node_id,text_segment_id,member_order,membership_role"),
    ]
    load_sql = "\\set ON_ERROR_STOP on\nBEGIN;\n"
    for key, table, columns in copy_specs:
        path = (args.output_dir / files[key]).as_posix()
        load_sql += (
            f"\\copy {table} ({columns}) FROM '{path}' "
            "WITH (FORMAT csv, DELIMITER E'\\t', NULL E'\\\\N');\n"
        )
    load_sql += """COMMIT;
ANALYZE authoring.biblical_books;
ANALYZE authoring.reference_atoms;
ANALYZE authoring.reference_spans;
ANALYZE authoring.reference_labels;
ANALYZE authoring.reference_label_members;
ANALYZE authoring.text_segments;
ANALYZE authoring.analysis_nodes;
ANALYZE authoring.analysis_node_features;
ANALYZE authoring.analysis_node_segments;
"""
    (args.output_dir / "load.sql").write_text(load_sql, encoding="utf-8")

    print(json.dumps({"rowCounts": counts, "outputDir": str(args.output_dir)}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
