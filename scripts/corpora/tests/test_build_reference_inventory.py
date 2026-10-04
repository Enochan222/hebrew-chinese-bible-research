from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

CORPUS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(CORPUS))
from build_reference_inventory import build_inventory  # noqa: E402


class ReferenceInventoryTests(unittest.TestCase):
    def test_inventory_is_source_derived_and_book_count_is_dynamic(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            wlc = root / "wlc"
            wlc.mkdir()
            (wlc / "Gen.xml").write_text(
                '<osis><verse osisID="Gen.1.1"><w id="g1">א</w></verse></osis>',
                encoding="utf-8",
            )
            (wlc / "Exod.xml").write_text(
                '<osis><verse osisID="Exod.1.1"><w id="e1">ב</w><w id="e2">ג</w></verse></osis>',
                encoding="utf-8",
            )
            (wlc / "VerseMap.xml").write_text("<verseMap/>", encoding="utf-8")
            registry = root / "registry.json"
            registry.write_text(
                json.dumps({
                    "sources": [{
                        "sourceKey": "OSHB_MORPHHB",
                        "pin": {"commitSha": "1" * 40, "datasetVersion": None},
                    }]
                }),
                encoding="utf-8",
            )
            source_manifest = root / "source-manifest.json"
            source_manifest.write_text(
                json.dumps({"sourceKey": "OSHB_MORPHHB", "commitSha": "1" * 40}),
                encoding="utf-8",
            )

            inventory = build_inventory(wlc, source_manifest, registry)
            self.assertEqual(inventory["providerBookDivisionCount"], 2)
            self.assertEqual(inventory["referenceCount"], 2)
            self.assertEqual(inventory["wordCount"], 3)
            self.assertEqual(inventory["references"], ["Exod.1.1", "Gen.1.1"])
            self.assertEqual(
                inventory["authorityStatus"],
                "BOOTSTRAP_SOURCE_DERIVED_NOT_FINAL_CANON_ADJUDICATION",
            )


if __name__ == "__main__":
    unittest.main()
