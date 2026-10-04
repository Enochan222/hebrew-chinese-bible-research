#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_INPUT = ROOT / ".local/corpora/oshb-morphhb/wlc"
BOOK_RE = re.compile(r"^(?P<book>[^.]+)\.(?P<chapter>\d+)\.(?P<verse>\d+)$")


def local_name(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def parse_reference(value: str | None) -> tuple[str, int, int] | None:
    if not value:
        return None
    m = BOOK_RE.match(value)
    if not m:
        return None
    return m.group("book"), int(m.group("chapter")), int(m.group("verse"))


def iter_words(xml_path: Path, target_reference: str | None):
    current_reference: str | None = None
    word_order = 0
    for event, elem in ET.iterparse(xml_path, events=("start", "end")):
        name = local_name(elem.tag)
        if event == "start" and name == "verse":
            current_reference = elem.attrib.get("osisID")
            word_order = 0
        elif (
            event == "end"
            and name == "w"
            and current_reference
            and (target_reference is None or target_reference == current_reference)
        ):
            word_order += 1
            yield {
                "schemaVersion": "1.0",
                "sourceKey": "OSHB_MORPHHB",
                "providerScopedWordId": elem.attrib.get("id"),
                "referenceSystemCode": "OSHB_OSIS",
                "referenceLabel": current_reference,
                "wordOrderInVerse": word_order,
                "surfaceSourceExact": "".join(elem.itertext()),
                "lemmaRaw": elem.attrib.get("lemma"),
                "morphRaw": elem.attrib.get("morph"),
                "note": "Source Unicode is preserved exactly; no NFC normalization is applied.",
            }
            elem.clear()
        elif event == "end" and name == "verse":
            if target_reference and current_reference == target_reference:
                return
            current_reference = None
            elem.clear()


def main() -> int:
    parser = argparse.ArgumentParser(description="Export pinned OSHB OSIS words as provider-scoped NDJSON.")
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--output", type=Path, required=True)
    scope = parser.add_mutually_exclusive_group(required=True)
    scope.add_argument("--reference", help="exact OSIS reference such as 1Sam.16.7")
    scope.add_argument("--all", action="store_true", dest="export_all", help="export every available OSHB word")
    parser.add_argument("--limit", type=int, default=0)
    args = parser.parse_args()

    if args.reference:
        parsed = parse_reference(args.reference)
        if not parsed:
            raise SystemExit("--reference must look like 1Sam.16.7")
        files = [args.input / f"{parsed[0]}.xml"]
    else:
        files = sorted(p for p in args.input.glob("*.xml") if p.name != "VerseMap.xml")

    if not files or any(not p.is_file() for p in files):
        raise SystemExit(f"OSHB input missing under {args.input}; run fetch_sources.py first")

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.unlink(missing_ok=True)
    partial = args.output.with_name(args.output.name + ".partial")
    partial.unlink(missing_ok=True)

    count = 0
    try:
        with partial.open("w", encoding="utf-8") as out:
            for path in files:
                for record in iter_words(path, args.reference):
                    out.write(json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n")
                    count += 1
                    if args.limit and count >= args.limit:
                        break
                if args.limit and count >= args.limit:
                    break

        if count == 0:
            if args.reference:
                raise RuntimeError(f"OSHB reference {args.reference!r} resolved to no words")
            raise RuntimeError("OSHB whole-source export produced no word records")

        partial.replace(args.output)
    except Exception as exc:
        partial.unlink(missing_ok=True)
        args.output.unlink(missing_ok=True)
        raise SystemExit(str(exc)) from exc

    print(f"exported {count} OSHB words to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
