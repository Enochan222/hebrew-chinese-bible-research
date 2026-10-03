#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_BHSA = ROOT / ".local/corpora/bhsa-2021/tf/2021"
DEFAULT_BRIDGE = ROOT / ".local/corpora/etcbc-bridging-2021/tf/2021"
REQUESTED_FEATURES = [
    "book", "chapter", "verse", "g_word_utf8", "g_cons_utf8", "lex_utf8",
    "sp", "pdp", "gn", "nu", "st", "vs", "vt", "function", "typ", "rela",
    "mother", "language", "languageISO", "qere_utf8", "osm", "osm_sf",
]

def parse_reference(value: str) -> tuple[str, int, int]:
    parts = value.rsplit(".", 2)
    if len(parts) != 3:
        raise ValueError("reference must look like 1_Samuel.16.7")
    return parts[0], int(parts[1]), int(parts[2])

def main() -> int:
    parser = argparse.ArgumentParser(description="Export provider-scoped BHSA word/phrase/clause features as NDJSON.")
    parser.add_argument("--bhsa-dir", type=Path, default=DEFAULT_BHSA)
    parser.add_argument("--bridging-dir", type=Path, default=DEFAULT_BRIDGE)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--reference", help="BHSA section label such as 1_Samuel.16.7")
    parser.add_argument("--limit", type=int, default=0)
    args = parser.parse_args()
    try:
        from tf.fabric import Fabric
    except ImportError as exc:
        raise SystemExit("text-fabric is required; install requirements-corpus.txt") from exc
    if not args.bhsa_dir.is_dir():
        raise SystemExit(f"BHSA cache missing at {args.bhsa_dir}; run fetch_sources.py first")
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
    target = parse_reference(args.reference) if args.reference else None
    args.output.parent.mkdir(parents=True, exist_ok=True)

    def feature(name: str, node: int):
        obj = getattr(F, name, None)
        return obj.v(node) if obj is not None else None

    count = 0
    with args.output.open("w", encoding="utf-8") as out:
        for word in F.otype.s("word"):
            section = T.sectionFromNode(word)
            if target and tuple(section) != target:
                continue
            phrase_nodes = L.u(word, otype="phrase")
            clause_nodes = L.u(word, otype="clause")
            phrase = phrase_nodes[0] if phrase_nodes else None
            clause = clause_nodes[0] if clause_nodes else None
            record = {
                "schemaVersion": "1.0",
                "sourceKey": "BHSA_2021",
                "providerScopedNodeId": word,
                "referenceSystemCode": "BHSA_2021_SECTION",
                "referenceLabel": f"{section[0]}.{section[1]}.{section[2]}",
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
            out.write(json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n")
            count += 1
            if args.limit and count >= args.limit:
                break
    print(f"exported {count} BHSA words to {args.output}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
