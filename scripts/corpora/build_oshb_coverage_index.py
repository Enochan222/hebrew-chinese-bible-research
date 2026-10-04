#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import re
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_INPUT = ROOT / ".local/corpora/oshb-morphhb/wlc"
DEFAULT_OUTPUT = ROOT / ".local/exports/oshb-whole-bible-coverage.json"
REGISTRY = ROOT / "contracts/v1.1/corpus-source-registry.json"

OSIS_BOOK_ORDER = [
    "Gen","Exod","Lev","Num","Deut","Josh","Judg","Ruth","1Sam","2Sam",
    "1Kgs","2Kgs","1Chr","2Chr","Ezra","Neh","Esth","Job","Ps","Prov",
    "Eccl","Song","Isa","Jer","Lam","Ezek","Dan","Hos","Joel","Amos",
    "Obad","Jonah","Mic","Nah","Hab","Zeph","Hag","Zech","Mal",
]

OSIS_BOOK_NAMES = {
    "Gen":"Genesis","Exod":"Exodus","Lev":"Leviticus","Num":"Numbers","Deut":"Deuteronomy",
    "Josh":"Joshua","Judg":"Judges","Ruth":"Ruth","1Sam":"1 Samuel","2Sam":"2 Samuel",
    "1Kgs":"1 Kings","2Kgs":"2 Kings","1Chr":"1 Chronicles","2Chr":"2 Chronicles",
    "Ezra":"Ezra","Neh":"Nehemiah","Esth":"Esther","Job":"Job","Ps":"Psalms","Prov":"Proverbs",
    "Eccl":"Ecclesiastes","Song":"Song of Songs","Isa":"Isaiah","Jer":"Jeremiah",
    "Lam":"Lamentations","Ezek":"Ezekiel","Dan":"Daniel","Hos":"Hosea","Joel":"Joel",
    "Amos":"Amos","Obad":"Obadiah","Jonah":"Jonah","Mic":"Micah","Nah":"Nahum",
    "Hab":"Habakkuk","Zeph":"Zephaniah","Hag":"Haggai","Zech":"Zechariah","Mal":"Malachi",
}
REFERENCE_RE = re.compile(r"^(?P<book>[^.]+)\.(?P<chapter>\d+)\.(?P<verse>\d+)$")


def local_name(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def source_pin() -> str:
    registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
    for source in registry["sources"]:
        if source["sourceKey"] == "OSHB_MORPHHB":
            return source["pin"]["commitSha"]
    raise RuntimeError("OSHB_MORPHHB missing from corpus source registry")


def discover_book_files(input_dir: Path) -> list[tuple[str, Path]]:
    actual = {p.stem: p for p in input_dir.glob("*.xml") if p.is_file()}
    expected = set(OSIS_BOOK_ORDER)
    missing = sorted(expected - set(actual))
    unexpected = sorted(set(actual) - expected)
    if missing or unexpected:
        raise RuntimeError(f"OSHB book-file set mismatch: missing={missing}; unexpected={unexpected}")
    return [(book, actual[book]) for book in OSIS_BOOK_ORDER]


def iter_verse_counts(xml_path: Path, expected_book: str):
    current_reference: str | None = None
    word_count = 0
    for event, elem in ET.iterparse(xml_path, events=("start", "end")):
        name = local_name(elem.tag)
        if event == "start" and name == "verse":
            if current_reference is not None:
                raise RuntimeError(f"nested verse in {xml_path}")
            current_reference = elem.attrib.get("osisID")
            word_count = 0
        elif event == "end" and name == "w" and current_reference is not None:
            word_count += 1
            elem.clear()
        elif event == "end" and name == "verse":
            if current_reference is None:
                raise RuntimeError(f"verse end without start in {xml_path}")
            match = REFERENCE_RE.fullmatch(current_reference)
            if not match:
                raise RuntimeError(f"unsupported OSHB reference {current_reference!r}")
            if match.group("book") != expected_book:
                raise RuntimeError(
                    f"reference {current_reference} does not match provider book file {expected_book}"
                )
            if word_count <= 0:
                raise RuntimeError(f"OSHB verse {current_reference} has no word records")
            yield current_reference, int(match.group("chapter")), int(match.group("verse")), word_count
            current_reference = None
            elem.clear()


def build_index(input_dir: Path) -> dict:
    seen: set[str] = set()
    ref_hash = hashlib.sha256()
    books = []
    total_chapters = 0
    total_verses = 0
    total_words = 0

    for order, (book, path) in enumerate(discover_book_files(input_dir), start=1):
        chapters: dict[int, dict[str, int | str]] = {}
        previous = (0, 0)
        book_verses = 0
        book_words = 0
        for reference, chapter, verse, words in iter_verse_counts(path, book):
            if reference in seen:
                raise RuntimeError(f"duplicate OSHB reference: {reference}")
            seen.add(reference)
            if (chapter, verse) <= previous:
                raise RuntimeError(f"non-monotonic OSHB reference order in {book}: {reference}")
            previous = (chapter, verse)
            stats = chapters.setdefault(
                chapter,
                {
                    "chapterNumber": chapter,
                    "verseCount": 0,
                    "wordCount": 0,
                    "firstReference": reference,
                    "lastReference": reference,
                },
            )
            stats["verseCount"] = int(stats["verseCount"]) + 1
            stats["wordCount"] = int(stats["wordCount"]) + words
            stats["lastReference"] = reference
            book_verses += 1
            book_words += words
            ref_hash.update(f"{reference}\t{words}\n".encode("utf-8"))

        if not chapters:
            raise RuntimeError(f"OSHB book {book} contains no chapters")
        chapter_rows = [chapters[n] for n in sorted(chapters)]
        books.append(
            {
                "osisCode": book,
                "englishName": OSIS_BOOK_NAMES[book],
                "providerBookOrder": order,
                "chapterCount": len(chapter_rows),
                "verseCount": book_verses,
                "wordCount": book_words,
                "chapters": chapter_rows,
            }
        )
        total_chapters += len(chapter_rows)
        total_verses += book_verses
        total_words += book_words

    return {
        "schemaVersion": "1.0",
        "sourceKey": "OSHB_MORPHHB",
        "sourceCommitSha": source_pin(),
        "referenceSystemCode": "OSHB_OSIS",
        "coverageKind": "WHOLE_PINNED_PROVIDER_CORPUS",
        "referenceWordCountSha256": ref_hash.hexdigest(),
        "totals": {
            "books": len(books),
            "chapters": total_chapters,
            "verses": total_verses,
            "words": total_words,
        },
        "books": books,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Build and validate whole-Bible OSHB coverage metadata.")
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    if not args.input.is_dir():
        raise SystemExit(f"OSHB input missing at {args.input}; run fetch_sources.py first")
    index = build_index(args.input)
    if index["totals"]["books"] != len(OSIS_BOOK_ORDER):
        raise SystemExit("whole-Bible OSHB coverage did not include every expected provider book")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(index, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(index["totals"], sort_keys=True))
    print(f"coverage index: {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
