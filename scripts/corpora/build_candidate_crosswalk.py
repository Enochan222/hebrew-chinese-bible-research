#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
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

def oshb_signature(row: dict) -> str:
    return hebrew_letters_only(row.get("surfaceSourceExact"))

def bhsa_signature(row: dict) -> str:
    return hebrew_letters_only(row.get("consonantalSourceExact") or row.get("surfaceSourceExact"))

def align_contiguous_spans(o_rows: list[dict], b_rows: list[dict]) -> tuple[list[tuple[list[dict], list[dict], str]] | None, str | None]:
    if not o_rows or not b_rows:
        return None, "MISSING_PROVIDER_ROWS"

    osigs = [oshb_signature(r) for r in o_rows]
    bsigs = [bhsa_signature(r) for r in b_rows]
    if any(not s for s in osigs) or any(not s for s in bsigs):
        return None, "EMPTY_CONSONANTAL_SIGNATURE"

    if "".join(osigs) != "".join(bsigs):
        return None, "VERSE_CONSONANTAL_STREAM_MISMATCH"

    groups: list[tuple[list[dict], list[dict], str]] = []
    i = j = 0
    while i < len(o_rows) or j < len(b_rows):
        oi, bj = i, j
        os = bs = ""

        while True:
            if os and os == bs:
                break

            if not os:
                if i >= len(o_rows):
                    return None, "SOURCE_EXHAUSTED_DURING_ALIGNMENT"
                os += osigs[i]
                i += 1
                continue

            if not bs:
                if j >= len(b_rows):
                    return None, "TARGET_EXHAUSTED_DURING_ALIGNMENT"
                bs += bsigs[j]
                j += 1
                continue

            if len(os) < len(bs) and bs.startswith(os):
                if i >= len(o_rows):
                    return None, "SOURCE_EXHAUSTED_DURING_ALIGNMENT"
                os += osigs[i]
                i += 1
                continue

            if len(bs) < len(os) and os.startswith(bs):
                if j >= len(b_rows):
                    return None, "TARGET_EXHAUSTED_DURING_ALIGNMENT"
                bs += bsigs[j]
                j += 1
                continue

            return None, "NON_PREFIX_TOKENIZATION_DIVERGENCE"

        groups.append((o_rows[oi:i], b_rows[bj:j], os))

    if i != len(o_rows) or j != len(b_rows):
        return None, "UNCONSUMED_PROVIDER_ROWS"
    return groups, None

def stream_diagnostics(o_rows: list[dict], b_rows: list[dict]) -> dict:
    os = "".join(oshb_signature(r) for r in o_rows)
    bs = "".join(bhsa_signature(r) for r in b_rows)
    limit = min(len(os), len(bs))
    first_difference = next((i for i in range(limit) if os[i] != bs[i]), None)
    if first_difference is None and len(os) != len(bs):
        first_difference = limit
    return {
        "oshbConsonantalLength": len(os),
        "bhsaConsonantalLength": len(bs),
        "oshbStreamSha256": hashlib.sha256(os.encode("utf-8")).hexdigest(),
        "bhsaStreamSha256": hashlib.sha256(bs.encode("utf-8")).hexdigest(),
        "firstDifferenceIndex": first_difference,
    }

def unresolved_record(ref: tuple[str, int, int], o_rows: list[dict], b_rows: list[dict], reason: str) -> dict:
    return {
        "recordType": "UNRESOLVED_REFERENCE",
        "reference": {"book": ref[0], "chapter": ref[1], "verse": ref[2]},
        "oshbWordCount": len(o_rows),
        "bhsaWordCount": len(b_rows),
        "reason": reason,
        "signatureAlgorithm": "HEBREW_LETTERS_ONLY_NFD_V1",
        "reviewStatus": "NEEDS_REVIEW",
        "canonical": False,
        **stream_diagnostics(o_rows, b_rows),
    }

def mapping_record(ref: tuple[str, int, int], o_group: list[dict], b_group: list[dict], signature: str) -> dict:
    return {
        "recordType": "CANDIDATE_SPAN_MAPPING",
        "sourceKey": "OSHB_MORPHHB",
        "sourceProviderScopedWordIds": [r.get("providerScopedWordId") for r in o_group],
        "sourceWordOrders": [r["wordOrderInVerse"] for r in o_group],
        "targetKey": "BHSA_2021",
        "targetProviderScopedNodeIds": [r.get("providerScopedNodeId") for r in b_group],
        "targetWordOrders": [r["wordOrderInVerse"] for r in b_group],
        "sourceCount": len(o_group),
        "targetCount": len(b_group),
        "reference": {"book": ref[0], "chapter": ref[1], "verse": ref[2]},
        "signatureAlgorithm": "HEBREW_LETTERS_ONLY_NFD_V1",
        "consonantalSignature": signature,
        "mappingMethod": "CONTIGUOUS_CONSONANTAL_SPAN_ALIGNMENT_V1",
        "reviewStatus": "CANDIDATE_AUTOMATED",
        "canonical": False,
    }

def main() -> int:
    parser = argparse.ArgumentParser(
        description="Build conservative many-to-many candidate OSHB-to-BHSA span mappings for Database Spike review."
    )
    parser.add_argument("--oshb", type=Path, required=True)
    parser.add_argument("--bhsa", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    groups_o: dict[tuple[str, int, int], list[dict]] = defaultdict(list)
    groups_b: dict[tuple[str, int, int], list[dict]] = defaultdict(list)
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
            groups, reason = align_contiguous_spans(o_rows, b_rows)

            if groups is None:
                record = unresolved_record(ref, o_rows, b_rows, reason or "UNKNOWN_ALIGNMENT_FAILURE")
                out.write(json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n")
                print(
                    f"unresolved {ref[0]}.{ref[1]}.{ref[2]}: {record['reason']}; "
                    f"oshb_words={len(o_rows)} bhsa_words={len(b_rows)} "
                    f"oshb_letters={record['oshbConsonantalLength']} bhsa_letters={record['bhsaConsonantalLength']} "
                    f"first_difference={record['firstDifferenceIndex']} "
                    f"oshb_sha256={record['oshbStreamSha256']} bhsa_sha256={record['bhsaStreamSha256']}"
                )
                unresolved_count += 1
                continue

            for o_group, b_group, signature in groups:
                out.write(json.dumps(mapping_record(ref, o_group, b_group, signature), ensure_ascii=False, sort_keys=True) + "\n")
                mapping_count += 1

    print(f"candidate span mappings={mapping_count}; unresolved references={unresolved_count}; output={args.output}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
