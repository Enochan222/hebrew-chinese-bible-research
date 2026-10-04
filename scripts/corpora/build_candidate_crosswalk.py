#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import unicodedata
from collections import defaultdict
from pathlib import Path

from reference_aliases import parse_reference_label
def load_ndjson(path: Path) -> list[dict]:
    with path.open(encoding="utf-8") as fh:
        return [json.loads(line) for line in fh if line.strip()]

def hebrew_letters_only(value: str | None) -> str:
    if not value:
        return ""
    decomposed = unicodedata.normalize("NFD", value)
    return "".join(
        ch for ch in decomposed
        if "\u0590" <= ch <= "\u05ff" and unicodedata.category(ch).startswith("L")
    )

def main() -> int:
    parser = argparse.ArgumentParser(description="Build conservative candidate OSHB-to-BHSA word mappings for Database Spike review.")
    parser.add_argument("--oshb", type=Path, required=True)
    parser.add_argument("--bhsa", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    groups_o = defaultdict(list)
    groups_b = defaultdict(list)
    for row in load_ndjson(args.oshb):
        groups_o[parse_reference_label(row["referenceLabel"])].append(row)
    for row in load_ndjson(args.bhsa):
        groups_b[parse_reference_label(row["referenceLabel"])].append(row)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    mapping_count = 0
    unresolved_count = 0
    with args.output.open("w", encoding="utf-8") as out:
        for ref in sorted(set(groups_o) | set(groups_b)):
            o_rows = sorted(groups_o.get(ref, []), key=lambda r: r["wordOrderInVerse"])
            b_rows = sorted(groups_b.get(ref, []), key=lambda r: r["wordOrderInVerse"])
            if len(o_rows) != len(b_rows) or not o_rows:
                out.write(json.dumps({
                    "recordType": "UNRESOLVED_REFERENCE",
                    "reference": {"book": ref[0], "chapter": ref[1], "verse": ref[2]},
                    "oshbWordCount": len(o_rows), "bhsaWordCount": len(b_rows),
                    "reason": "WORD_COUNT_MISMATCH_OR_MISSING", "reviewStatus": "NEEDS_REVIEW"
                }, ensure_ascii=False, sort_keys=True) + "\n")
                unresolved_count += 1
                continue
            pairs = []
            valid = True
            for o, b in zip(o_rows, b_rows):
                osig = hebrew_letters_only(o.get("surfaceSourceExact"))
                bsig = hebrew_letters_only(b.get("consonantalSourceExact") or b.get("surfaceSourceExact"))
                if not osig or osig != bsig:
                    valid = False
                    break
                pairs.append((o, b, osig))
            if not valid:
                out.write(json.dumps({
                    "recordType": "UNRESOLVED_REFERENCE",
                    "reference": {"book": ref[0], "chapter": ref[1], "verse": ref[2]},
                    "oshbWordCount": len(o_rows), "bhsaWordCount": len(b_rows),
                    "reason": "ORDERED_CONSONANTAL_SIGNATURE_MISMATCH",
                    "signatureAlgorithm": "HEBREW_LETTERS_ONLY_V1", "reviewStatus": "NEEDS_REVIEW"
                }, ensure_ascii=False, sort_keys=True) + "\n")
                unresolved_count += 1
                continue
            for o, b, sig in pairs:
                out.write(json.dumps({
                    "recordType": "CANDIDATE_WORD_MAPPING",
                    "sourceKey": "OSHB_MORPHHB",
                    "sourceProviderScopedWordId": o.get("providerScopedWordId"),
                    "targetKey": "BHSA_2021",
                    "targetProviderScopedNodeId": b.get("providerScopedNodeId"),
                    "reference": {"book": ref[0], "chapter": ref[1], "verse": ref[2]},
                    "wordOrderInVerse": o["wordOrderInVerse"],
                    "signatureAlgorithm": "HEBREW_LETTERS_ONLY_V1",
                    "consonantalSignature": sig,
                    "mappingMethod": "SAME_REFERENCE_ORDER_AND_CONSONANTAL_SIGNATURE",
                    "reviewStatus": "CANDIDATE_AUTOMATED",
                    "canonical": False
                }, ensure_ascii=False, sort_keys=True) + "\n")
                mapping_count += 1
    print(f"candidate mappings={mapping_count}; unresolved references={unresolved_count}; output={args.output}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
