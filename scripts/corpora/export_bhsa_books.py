#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from export_bhsa_features import DEFAULT_BHSA, DEFAULT_BRIDGE, REQUESTED_FEATURES
from reference_aliases import normalize_section_tuple

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_CANON = ROOT / "contracts/v1.1/hebrew-bible-canon-system.json"


def file_sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for block in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def load_books(path: Path) -> tuple[list[dict], dict[str, dict]]:
    data = json.loads(path.read_text(encoding="utf-8"))
    books = sorted((b for b in data["books"] if b.get("included")), key=lambda b: b["bookOrder"])
    by_code = {b["osisCode"]: b for b in books}
    if len(by_code) != len(books):
        raise SystemExit("configured canon contains duplicate OSIS codes")
    return books, by_code


def main() -> int:
    parser = argparse.ArgumentParser(description="Export pinned BHSA word/phrase/clause features into one NDJSON file per configured biblical book.")
    parser.add_argument("--bhsa-dir", type=Path, default=DEFAULT_BHSA)
    parser.add_argument("--bridging-dir", type=Path, default=DEFAULT_BRIDGE)
    parser.add_argument("--canon", type=Path, default=DEFAULT_CANON)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--report", type=Path)
    args = parser.parse_args()

    try:
        from tf.fabric import Fabric
    except ImportError as exc:
        raise SystemExit("text-fabric is required; install requirements-corpus.txt") from exc
    if not args.bhsa_dir.is_dir():
        raise SystemExit(f"BHSA cache missing at {args.bhsa_dir}; run fetch_sources.py first")

    books, by_code = load_books(args.canon)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    locations = [str(args.bhsa_dir)]
    if args.bridging_dir.is_dir():
        locations.append(str(args.bridging_dir))

    tf = Fabric(locations=locations, modules=[""])
    explored = tf.explore(silent=True)
    available = set(explored.get("nodes", []))
    requested = " ".join(name for name in REQUESTED_FEATURES if name in available)
    api = tf.load(requested, silent="deep")
    if not api:
        raise SystemExit("Text-Fabric could not load the configured BHSA feature subset")
    F, L, T = api.F, api.L, api.T

    def feature(name: str, node: int):
        obj = getattr(F, name, None)
        return obj.v(node) if obj is not None else None

    handles: dict[str, object] = {}
    counts = {b["osisCode"]: 0 for b in books}
    references: dict[str, set[str]] = {b["osisCode"]: set() for b in books}
    native_books: dict[str, set[str]] = {b["osisCode"]: set() for b in books}
    last_section = None
    word_order = 0

    try:
        for word in F.otype.s("word"):
            section = tuple(T.sectionFromNode(word))
            canonical_section = normalize_section_tuple(section)
            canonical_book = canonical_section[0]
            if canonical_book not in by_code:
                raise SystemExit(f"BHSA emitted book outside configured canon: native={section[0]!r} canonical={canonical_book!r}")
            if section != last_section:
                last_section = section
                word_order = 0
            word_order += 1

            phrase_nodes = L.u(word, otype="phrase")
            clause_nodes = L.u(word, otype="clause")
            phrase = phrase_nodes[0] if phrase_nodes else None
            clause = clause_nodes[0] if clause_nodes else None
            label = f"{section[0]}.{section[1]}.{section[2]}"
            record = {
                "schemaVersion": "1.0",
                "sourceKey": "BHSA_2021",
                "providerScopedNodeId": word,
                "referenceSystemCode": "BHSA_2021_SECTION",
                "referenceLabel": label,
                "wordOrderInVerse": word_order,
                "surfaceSourceExact": feature("g_word_utf8", word),
                "consonantalSourceExact": feature("g_cons_utf8", word),
                "lexemeRaw": feature("lex_utf8", word),
                "partOfSpeechRaw": feature("sp", word),
                "phraseDependentPartOfSpeechRaw": feature("pdp", word),
                "genderRaw": feature("gn", word),
                "numberRaw": feature("nu", word),
                "stateRaw": feature("st", word),
                "verbalStemRaw": feature("vs", word),
                "verbalTenseRaw": feature("vt", word),
                "languageRaw": feature("language", word),
                "languageIsoRaw": feature("languageISO", word),
                "qereRaw": feature("qere_utf8", word),
                "phraseNodeId": phrase,
                "phraseFunctionRaw": feature("function", phrase) if phrase else None,
                "phraseTypeRaw": feature("typ", phrase) if phrase else None,
                "phraseRelationRaw": feature("rela", phrase) if phrase else None,
                "clauseNodeId": clause,
                "clauseTypeRaw": feature("typ", clause) if clause else None,
                "clauseRelationRaw": feature("rela", clause) if clause else None,
                "bridgeOshbMorphologyPrimaryRaw": feature("osm", word),
                "bridgeOshbMorphologySecondaryRaw": feature("osm_sf", word),
                "bridgeSemantics": "ETCBC bridging morphology attached to a BHSA word node; not a universal OSHB provider-word-ID mapping.",
            }
            if canonical_book not in handles:
                handles[canonical_book] = (args.output_dir / f"{canonical_book}.ndjson").open("w", encoding="utf-8")
            handles[canonical_book].write(json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n")
            counts[canonical_book] += 1
            references[canonical_book].add(label)
            native_books[canonical_book].add(str(section[0]))
    finally:
        for handle in handles.values():
            handle.close()

    missing = [code for code,count in counts.items() if count == 0]
    if missing:
        raise SystemExit(f"configured BHSA books exported zero words: {missing}")

    summary = []
    for book in books:
        code = book["osisCode"]
        output = args.output_dir / f"{code}.ndjson"
        summary.append({
            "book": code,
            "bookOrder": book["bookOrder"],
            "nativeBookLabels": sorted(native_books[code]),
            "wordRecords": counts[code],
            "referenceLabels": len(references[code]),
            "sha256": file_sha256(output),
        })
        print(f"BHSA {code}: words={counts[code]} references={len(references[code])} native={sorted(native_books[code])}")

    report = {
        "schemaVersion": "1.0",
        "sourceKey": "BHSA_2021",
        "bookCount": len(summary),
        "wordRecords": sum(x["wordRecords"] for x in summary),
        "referenceLabels": sum(x["referenceLabels"] for x in summary),
        "books": summary,
    }
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(report, ensure_ascii=False, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
