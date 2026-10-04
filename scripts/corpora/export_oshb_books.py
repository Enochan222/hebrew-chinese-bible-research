#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from export_oshb_words import DEFAULT_INPUT, iter_words

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_CANON = ROOT / "contracts/v1.1/hebrew-bible-canon-system.json"


def file_sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for block in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def load_books(path: Path) -> list[dict]:
    data = json.loads(path.read_text(encoding="utf-8"))
    books = sorted((b for b in data["books"] if b.get("included")), key=lambda b: b["bookOrder"])
    if not books:
        raise SystemExit("configured canon contains no included books")
    return books


def main() -> int:
    parser = argparse.ArgumentParser(description="Export pinned OSHB words into one provider-scoped NDJSON file per configured biblical book.")
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--canon", type=Path, default=DEFAULT_CANON)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--report", type=Path)
    args = parser.parse_args()

    books = load_books(args.canon)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    summary = []

    for book in books:
        code = book["osisCode"]
        source = args.input / f"{code}.xml"
        if not source.is_file():
            raise SystemExit(f"configured OSHB book source missing: {source}")
        output = args.output_dir / f"{code}.ndjson"
        count = 0
        references: set[str] = set()
        with output.open("w", encoding="utf-8") as out:
            for record in iter_words(source, None):
                label = str(record["referenceLabel"])
                if not label.startswith(code + "."):
                    raise SystemExit(f"OSHB book export escaped configured book {code}: {label}")
                out.write(json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n")
                count += 1
                references.add(label)
        if count == 0:
            output.unlink(missing_ok=True)
            raise SystemExit(f"configured OSHB book {code} exported zero words")
        summary.append({
            "book": code,
            "bookOrder": book["bookOrder"],
            "wordRecords": count,
            "referenceLabels": len(references),
            "sha256": file_sha256(output),
        })
        print(f"OSHB {code}: words={count} references={len(references)}")

    report = {
        "schemaVersion": "1.0",
        "sourceKey": "OSHB_MORPHHB",
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
