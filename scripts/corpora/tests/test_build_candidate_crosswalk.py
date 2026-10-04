from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


CORPUS_SCRIPTS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(CORPUS_SCRIPTS))

from build_candidate_crosswalk import is_bhsa_annotation_only_node  # noqa: E402


def empty_bhsa_node(**overrides):
    row = {
        "surfaceSourceExact": None,
        "consonantalSourceExact": None,
        "lexemeRaw": "H",
        "partOfSpeechRaw": "art",
        "phraseDependentPartOfSpeechRaw": "art",
        "languageIsoRaw": "hbo",
        "phraseNodeId": 10,
        "clauseNodeId": 20,
        "qereRaw": None,
        "bridgeOshbMorphologyPrimaryRaw": None,
        "bridgeOshbMorphologySecondaryRaw": None,
    }
    row.update(overrides)
    return row


SCRIPT = CORPUS_SCRIPTS / "build_candidate_crosswalk.py"


class AnnotationOnlyClassificationTests(unittest.TestCase):
    def test_known_article_node_is_annotation_only(self):
        self.assertTrue(is_bhsa_annotation_only_node(empty_bhsa_node()))

    def test_unknown_empty_lexical_node_remains_unclassified(self):
        self.assertFalse(
            is_bhsa_annotation_only_node(
                empty_bhsa_node(
                    partOfSpeechRaw="verb",
                    phraseDependentPartOfSpeechRaw="verb",
                )
            )
        )

    def test_non_hebrew_or_bridged_empty_node_remains_unclassified(self):
        self.assertFalse(is_bhsa_annotation_only_node(empty_bhsa_node(languageIsoRaw="arc")))
        self.assertFalse(
            is_bhsa_annotation_only_node(
                empty_bhsa_node(bridgeOshbMorphologyPrimaryRaw="HTd")
            )
        )

    def test_known_annotation_only_node_is_preserved_even_when_reference_is_unresolved(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            oshb = root / "oshb.ndjson"
            bhsa = root / "bhsa.ndjson"
            output = root / "crosswalk.ndjson"
            oshb.write_text(
                json.dumps({
                    "sourceKey": "OSHB_MORPHHB",
                    "providerScopedWordId": "o1",
                    "referenceLabel": "Gen.1.1",
                    "wordOrderInVerse": 1,
                    "surfaceSourceExact": "אב",
                }) + "\n",
                encoding="utf-8",
            )
            known = empty_bhsa_node(
                providerScopedNodeId=1,
                referenceLabel="Genesis.1.1",
                wordOrderInVerse=1,
            )
            unknown = empty_bhsa_node(
                providerScopedNodeId=2,
                referenceLabel="Genesis.1.1",
                wordOrderInVerse=2,
                partOfSpeechRaw="verb",
                phraseDependentPartOfSpeechRaw="verb",
            )
            bhsa.write_text(
                json.dumps(known) + "\n" + json.dumps(unknown) + "\n",
                encoding="utf-8",
            )
            result = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--oshb", str(oshb),
                    "--bhsa", str(bhsa),
                    "--output", str(output),
                    "--quiet-unresolved",
                ],
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
            rows = [json.loads(line) for line in output.read_text(encoding="utf-8").splitlines()]
            self.assertEqual(rows[0]["recordType"], "ANNOTATION_ONLY_TARGET_NODE")
            self.assertEqual(rows[0]["targetProviderScopedNodeId"], 1)
            self.assertEqual(rows[1]["recordType"], "UNRESOLVED_REFERENCE")
            self.assertEqual(rows[1]["reason"], "UNCLASSIFIED_EMPTY_TARGET_SIGNATURE")


if __name__ == "__main__":
    unittest.main()
