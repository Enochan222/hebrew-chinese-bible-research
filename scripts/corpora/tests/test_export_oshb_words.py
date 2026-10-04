from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "export_oshb_words.py"


class OshbExportTests(unittest.TestCase):
    def test_requested_reference_with_zero_words_fails_closed(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "wlc"
            source.mkdir()
            (source / "Gen.xml").write_text(
                '<osis><verse osisID="Gen.1.1"><w id="w1">ב</w></verse></osis>',
                encoding="utf-8",
            )
            output = root / "out.ndjson"
            result = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--input",
                    str(source),
                    "--reference",
                    "Gen.1.2",
                    "--output",
                    str(output),
                ],
                capture_output=True,
                text=True,
                check=False,
            )

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("resolved to no words", result.stderr + result.stdout)
            self.assertFalse(output.exists(), "failed export must not leave an empty artifact")

    def test_scope_must_be_explicit(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "wlc"
            source.mkdir()
            (source / "Gen.xml").write_text(
                '<osis><verse osisID="Gen.1.1"><w id="w1">ב</w></verse></osis>',
                encoding="utf-8",
            )
            output = root / "out.ndjson"
            result = subprocess.run(
                [sys.executable, str(SCRIPT), "--input", str(source), "--output", str(output)],
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertFalse(output.exists())

    def test_all_mode_exports_every_book_file_without_versemap(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "wlc"
            source.mkdir()
            (source / "Gen.xml").write_text(
                '<osis><verse osisID="Gen.1.1"><w id="w1">ב</w></verse></osis>',
                encoding="utf-8",
            )
            (source / "Exod.xml").write_text(
                '<osis><verse osisID="Exod.1.1"><w id="w2">ג</w></verse></osis>',
                encoding="utf-8",
            )
            (source / "VerseMap.xml").write_text("<verseMap/>", encoding="utf-8")
            output = root / "out.ndjson"
            result = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--input",
                    str(source),
                    "--all",
                    "--output",
                    str(output),
                ],
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
            rows = [json.loads(line) for line in output.read_text(encoding="utf-8").splitlines()]
            self.assertEqual({row["referenceLabel"] for row in rows}, {"Gen.1.1", "Exod.1.1"})
            self.assertEqual({row["providerScopedWordId"] for row in rows}, {"w1", "w2"})


if __name__ == "__main__":
    unittest.main()
