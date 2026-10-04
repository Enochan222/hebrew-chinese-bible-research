from __future__ import annotations

import sys
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


if __name__ == "__main__":
    unittest.main()
