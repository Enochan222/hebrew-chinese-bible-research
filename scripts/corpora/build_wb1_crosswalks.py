#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_CANON = ROOT / "contracts/v1.1/hebrew-bible-canon-system.json"
CROSSWALK = Path(__file__).resolve().parent / "build_candidate_crosswalk.py"


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for block in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def load_books(path: Path) -> list[dict]:
    data = json.loads(path.read_text(encoding="utf-8"))
    return sorted((b for b in data["books"] if b.get("included")), key=lambda b: b["bookOrder"])


def summarize(path: Path) -> dict:
    counts = {
        "candidateMappingGroups": 0,
        "annotationOnlyTargetNodes": 0,
        "unresolvedReferences": 0,
        "nonOneToOneCandidateGroups": 0,
    }
    unresolved_reasons: dict[str, int] = {}
    with path.open(encoding="utf-8") as fh:
        for line in fh:
            if not line.strip():
                continue
            row = json.loads(line)
            kind = row.get("recordType")
            if kind == "CANDIDATE_SPAN_MAPPING":
                counts["candidateMappingGroups"] += 1
                if row.get("sourceCount") != 1 or row.get("targetCount") != 1:
                    counts["nonOneToOneCandidateGroups"] += 1
            elif kind == "ANNOTATION_ONLY_TARGET_NODE":
                counts["annotationOnlyTargetNodes"] += 1
            elif kind == "UNRESOLVED_REFERENCE":
                counts["unresolvedReferences"] += 1
                reason = str(row.get("reason") or "UNKNOWN")
                unresolved_reasons[reason] = unresolved_reasons.get(reason, 0) + 1
            else:
                raise SystemExit(f"unknown crosswalk record type in {path}: {kind!r}")
    return {**counts, "unresolvedReasons": dict(sorted(unresolved_reasons.items()))}


def main() -> int:
    parser = argparse.ArgumentParser(description="Build bounded per-book OSHB/BHSA candidate crosswalks for WB-1.")
    parser.add_argument("--oshb-dir", type=Path, required=True)
    parser.add_argument("--bhsa-dir", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--canon", type=Path, default=DEFAULT_CANON)
    parser.add_argument("--report", type=Path)
    args = parser.parse_args()

    books = load_books(args.canon)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    summary = []

    for book in books:
        code = book["osisCode"]
        oshb = args.oshb_dir / f"{code}.ndjson"
        bhsa = args.bhsa_dir / f"{code}.ndjson"
        output = args.output_dir / f"{code}.ndjson"
        if not oshb.is_file() or not bhsa.is_file():
            raise SystemExit(f"WB-1 crosswalk input missing for {code}")
        subprocess.run(
            [
                sys.executable,
                str(CROSSWALK),
                "--oshb", str(oshb),
                "--bhsa", str(bhsa),
                "--output", str(output),
            ],
            check=True,
        )
        stats = summarize(output)
        summary.append({
            "book": code,
            "bookOrder": book["bookOrder"],
            "sha256": sha256_file(output),
            **stats,
        })
        print(f"crosswalk {code}: {json.dumps(stats, sort_keys=True)}")

    totals = {
        key: sum(int(row[key]) for row in summary)
        for key in (
            "candidateMappingGroups",
            "annotationOnlyTargetNodes",
            "unresolvedReferences",
            "nonOneToOneCandidateGroups",
        )
    }
    report = {
        "schemaVersion": "1.0",
        "bookCount": len(summary),
        "totals": totals,
        "books": summary,
    }
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(report, ensure_ascii=False, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
