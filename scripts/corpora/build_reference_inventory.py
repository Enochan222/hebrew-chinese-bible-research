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
DEFAULT_SOURCE_MANIFEST = ROOT / ".local/corpora/oshb-morphhb/source-manifest.json"
DEFAULT_OUTPUT = ROOT / ".local/whole-bible-corpus/reference-inventory.json"
REGISTRY = ROOT / "contracts/v1.1/corpus-source-registry.json"
REFERENCE_RE = re.compile(r"^(?P<book>[^.]+)\.(?P<chapter>\d+)\.(?P<verse>\d+)$")
AUXILIARY_XML_FILENAMES = {"VerseMap.xml"}


def local_name(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def source_pin(registry_path: Path) -> str:
    registry = json.loads(registry_path.read_text(encoding="utf-8"))
    for source in registry["sources"]:
        if source["sourceKey"] == "OSHB_MORPHHB":
            return source["pin"]["commitSha"]
    raise RuntimeError("OSHB_MORPHHB missing from corpus source registry")


def scan_file(path: Path):
    current_reference: str | None = None
    words = 0
    for event, elem in ET.iterparse(path, events=("start", "end")):
        name = local_name(elem.tag)
        if event == "start" and name == "verse":
            if current_reference is not None:
                raise RuntimeError(f"nested verse in {path}")
            current_reference = elem.attrib.get("osisID")
            words = 0
        elif event == "end" and name == "w" and current_reference is not None:
            words += 1
            elem.clear()
        elif event == "end" and name == "verse":
            if current_reference is None:
                raise RuntimeError(f"verse end without osisID in {path}")
            match = REFERENCE_RE.fullmatch(current_reference)
            if not match:
                raise RuntimeError(f"unsupported OSHB reference {current_reference!r} in {path}")
            if words <= 0:
                raise RuntimeError(f"OSHB reference {current_reference} has no word records")
            yield (
                current_reference,
                match.group("book"),
                int(match.group("chapter")),
                int(match.group("verse")),
                words,
            )
            current_reference = None
            elem.clear()


def build_inventory(input_dir: Path, source_manifest_path: Path, registry_path: Path) -> dict:
    pin = source_pin(registry_path)
    source_manifest = json.loads(source_manifest_path.read_text(encoding="utf-8"))
    if source_manifest.get("sourceKey") != "OSHB_MORPHHB" or source_manifest.get("commitSha") != pin:
        raise RuntimeError("OSHB source manifest does not match the active pinned source")

    xml_files = sorted(
        path
        for path in input_dir.glob("*.xml")
        if path.is_file() and path.name not in AUXILIARY_XML_FILENAMES
    )
    if not xml_files:
        raise RuntimeError(f"no OSHB book XML files found under {input_dir}")

    seen: set[str] = set()
    references: list[str] = []
    book_divisions: list[dict] = []
    total_words = 0

    for path in xml_files:
        file_rows = list(scan_file(path))
        if not file_rows:
            raise RuntimeError(f"OSHB source file {path.name} contains no verse records")
        file_books = {book for _, book, _, _, _ in file_rows}
        if len(file_books) != 1:
            raise RuntimeError(f"OSHB source file {path.name} spans multiple provider book codes: {sorted(file_books)}")
        provider_book = next(iter(file_books))
        if path.stem != provider_book:
            raise RuntimeError(f"OSHB provider file/reference mismatch: {path.name} vs {provider_book}")

        chapters: set[int] = set()
        book_words = 0
        previous = (0, 0)
        for reference, _book, chapter, verse, words in file_rows:
            if reference in seen:
                raise RuntimeError(f"duplicate OSHB reference {reference}")
            if (chapter, verse) <= previous:
                raise RuntimeError(f"non-monotonic OSHB reference order in {provider_book}: {reference}")
            previous = (chapter, verse)
            seen.add(reference)
            references.append(reference)
            chapters.add(chapter)
            book_words += words
            total_words += words

        book_divisions.append(
            {
                "providerBookCode": provider_book,
                "chapterCount": len(chapters),
                "referenceCount": len(file_rows),
                "wordCount": book_words,
                "sourceFile": path.name,
                "sourceFileSha256": sha256_file(path),
            }
        )

    reference_hash = hashlib.sha256()
    for reference in references:
        reference_hash.update((reference + "\n").encode("utf-8"))

    return {
        "schemaVersion": "1.0",
        "inventoryType": "REFERENCE_SYSTEM_BOOTSTRAP_SNAPSHOT",
        "referenceSystemCode": "OSHB_OSIS",
        "authorityStatus": "BOOTSTRAP_SOURCE_DERIVED_NOT_FINAL_CANON_ADJUDICATION",
        "derivation": "PINNED_OSHB_SOURCE_XML_INDEPENDENT_OF_EXPORTER_OUTPUT",
        "sourceKey": "OSHB_MORPHHB",
        "sourceCommitSha": pin,
        "sourceManifestSha256": sha256_file(source_manifest_path),
        "providerBookDivisionCount": len(book_divisions),
        "referenceCount": len(references),
        "wordCount": total_words,
        "referenceSetSha256": reference_hash.hexdigest(),
        "references": references,
        "bookDivisions": book_divisions,
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Build an independent OSHB_OSIS reference inventory from the exact pinned source XML."
    )
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--source-manifest", type=Path, default=DEFAULT_SOURCE_MANIFEST)
    parser.add_argument("--registry", type=Path, default=REGISTRY)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    if not args.input.is_dir():
        raise SystemExit(f"OSHB input missing at {args.input}; run fetch_sources.py first")
    if not args.source_manifest.is_file():
        raise SystemExit(f"OSHB source manifest missing at {args.source_manifest}")

    inventory = build_inventory(args.input, args.source_manifest, args.registry)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(inventory, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {
                "providerBookDivisions": inventory["providerBookDivisionCount"],
                "references": inventory["referenceCount"],
                "words": inventory["wordCount"],
                "referenceSetSha256": inventory["referenceSetSha256"],
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
