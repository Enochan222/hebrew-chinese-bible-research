from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "build_whole_bible_manifest.py"


def write_ndjson(path: Path, rows: list[dict]) -> None:
    path.write_text(
        "".join(json.dumps(row, ensure_ascii=False) + "\n" for row in rows),
        encoding="utf-8",
    )


class WholeBibleManifestTests(unittest.TestCase):
    def setup_files(self, root: Path):
        inventory = root / "inventory.json"
        oshb = root / "oshb.ndjson"
        bhsa = root / "bhsa.ndjson"
        crosswalk = root / "crosswalk.ndjson"
        registry = root / "registry.json"
        output = root / "manifest.json"

        inventory.write_text(
            json.dumps({
                "referenceSystemCode": "OSHB_OSIS",
                "authorityStatus": "BOOTSTRAP_SOURCE_DERIVED_NOT_FINAL_CANON_ADJUDICATION",
                "derivation": "PINNED_OSHB_SOURCE_XML_INDEPENDENT_OF_EXPORTER_OUTPUT",
                "referenceSetSha256": "a" * 64,
                "providerBookDivisionCount": 2,
                "references": ["Gen.1.1", "Exod.1.1"],
            }),
            encoding="utf-8",
        )
        write_ndjson(oshb, [
            {"sourceKey": "OSHB_MORPHHB", "providerScopedWordId": "o1", "referenceLabel": "Gen.1.1"},
            {"sourceKey": "OSHB_MORPHHB", "providerScopedWordId": "o2", "referenceLabel": "Exod.1.1"},
        ])
        write_ndjson(bhsa, [
            {"sourceKey": "BHSA_2021", "providerScopedNodeId": 1, "referenceLabel": "Genesis.1.1"},
        ])
        registry.write_text(
            json.dumps({"sources": [
                {"sourceKey": "OSHB_MORPHHB", "pin": {"commitSha": "1" * 40, "datasetVersion": None}},
                {"sourceKey": "BHSA_2021", "pin": {"commitSha": "2" * 40, "datasetVersion": "2021"}},
                {"sourceKey": "ETCBC_BRIDGING_2021", "pin": {"commitSha": "3" * 40, "datasetVersion": "2021"}},
            ]}),
            encoding="utf-8",
        )
        return inventory, oshb, bhsa, crosswalk, registry, output

    def run_build(self, paths):
        inventory, oshb, bhsa, crosswalk, registry, output = paths
        return subprocess.run(
            [
                sys.executable,
                str(SCRIPT),
                "--reference-inventory", str(inventory),
                "--oshb", str(oshb),
                "--bhsa", str(bhsa),
                "--crosswalk", str(crosswalk),
                "--registry", str(registry),
                "--output", str(output),
            ],
            capture_output=True,
            text=True,
            check=False,
        )

    def test_provider_gap_is_explicit_not_silent_and_book_count_is_dynamic(self):
        with tempfile.TemporaryDirectory() as tmp:
            paths = self.setup_files(Path(tmp))
            write_ndjson(paths[3], [
                {
                    "recordType": "CANDIDATE_SPAN_MAPPING",
                    "reference": {"book": "Gen", "chapter": 1, "verse": 1},
                    "sourceCount": 1,
                    "targetCount": 1,
                },
                {
                    "recordType": "UNRESOLVED_REFERENCE",
                    "reference": {"book": "Exod", "chapter": 1, "verse": 1},
                    "reason": "MISSING_PROVIDER_ROWS",
                },
            ])
            result = self.run_build(paths)
            self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
            manifest = json.loads(paths[5].read_text(encoding="utf-8"))
            self.assertTrue(manifest["gatePass"])
            self.assertEqual(manifest["status"], "COMPLETE_WITH_EXPLICIT_EXCEPTIONS")
            self.assertEqual(manifest["referenceSystem"]["expectedReferenceSpans"], 2)
            self.assertEqual(manifest["referenceSystem"]["providerBookDivisionCount"], 2)
            self.assertEqual(manifest["exceptions"]["bhsaMissingExpectedReferences"], ["Exod.1.1"])
            self.assertEqual(manifest["coverage"]["silentReferenceLoss"], 0)
            self.assertEqual({row["bookCode"] for row in manifest["perBook"]}, {"Gen", "Exod"})

    def test_missing_crosswalk_reference_fails_gate(self):
        with tempfile.TemporaryDirectory() as tmp:
            paths = self.setup_files(Path(tmp))
            write_ndjson(paths[3], [
                {
                    "recordType": "UNRESOLVED_REFERENCE",
                    "reference": {"book": "Exod", "chapter": 1, "verse": 1},
                    "reason": "MISSING_PROVIDER_ROWS",
                },
            ])
            result = self.run_build(paths)
            self.assertEqual(result.returncode, 2)
            manifest = json.loads(paths[5].read_text(encoding="utf-8"))
            self.assertFalse(manifest["gatePass"])
            self.assertEqual(manifest["status"], "INVALID_SILENT_REFERENCE_LOSS")
            self.assertEqual(manifest["coverage"]["silentReferenceLoss"], 1)
            self.assertEqual(manifest["exceptions"]["silentReferenceLossReferences"], ["Gen.1.1"])


if __name__ == "__main__":
    unittest.main()
