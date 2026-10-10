import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location("candidate_engine", ROOT/"scripts/corpora/oshb_pattern_candidates.py")
engine = importlib.util.module_from_spec(spec)
spec.loader.exec_module(engine)

PATTERN = {
    "schemaVersion": "0.1", "sourceKey": "OSHB_MORPHHB", "scope": "SAME_VERSE",
    "actionLemmaRaw": ["7200"], "bodyLemmaRaw": ["5869 a"],
    "targetPrefixLemmaRaw": "l", "direction": "ACTION_BEFORE_TARGET",
    "minInterveningWords": 0, "maxInterveningWords": 2,
}

def word(ref, order, lemma, morph="HNcfsa"):
    return {
        "sourceKey": "OSHB_MORPHHB", "referenceSystemCode": "OSHB_OSIS",
        "referenceLabel": ref, "wordOrderInVerse": order,
        "surfaceSourceExact": "SYNTHETIC", "lemmaRaw": lemma,
        "morphRaw": morph, "providerScopedWordId": f"{ref}-{order}"
    }

class SearchTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.path = Path(self.tmp.name) / "sample.ndjson"

    def source(self, rows):
        self.path.write_text("".join(json.dumps(x) + "\n" for x in rows), encoding="utf-8")
        return self.path

    def test_adjacent_prefixed_noun(self):
        r = engine.search(self.source([word("Gen.1.1",1,"c/7200","HC/Vqw3ms"),
            word("Gen.1.1",2,"l/5869 a","HR/Ncfsa")]), PATTERN)
        self.assertEqual(r["totalCandidateMatchesExactWithinInput"], 1)
        self.assertEqual(r["matches"][0]["interveningWords"], 0)
        self.assertEqual(r["matches"][0]["classification"], "MORPHOLOGICAL_PROXIMITY_CANDIDATE")

    def test_gap_and_direction(self):
        rows=[word("Gen.1.1",1,"7200","HVqp3ms"),word("Gen.1.1",2,"999"),
              word("Gen.1.1",3,"999"),word("Gen.1.1",4,"l/5869 a")]
        self.assertEqual(engine.search(self.source(rows),PATTERN)["totalCandidateMatchesExactWithinInput"],1)
        self.assertEqual(engine.search(self.path,dict(PATTERN,maxInterveningWords=1))["totalCandidateMatchesExactWithinInput"],0)
        self.assertEqual(engine.search(self.path,dict(PATTERN,direction="TARGET_BEFORE_ACTION"))["totalCandidateMatchesExactWithinInput"],0)

    def test_do_not_join_cross_verse(self):
        rows=[word("Gen.1.1",1,"7200","HVqp3ms"),word("Gen.1.2",1,"l/5869 a")]
        self.assertEqual(engine.search(self.source(rows),PATTERN)["totalCandidateMatchesExactWithinInput"],0)

    def test_prefix_must_be_component(self):
        rows=[word("Gen.1.1",1,"7200","HVqp3ms"),word("Gen.1.1",2,"5869 a"),
              word("Gen.1.1",3,"5869 a/l")]
        self.assertEqual(engine.search(self.source(rows),PATTERN)["totalCandidateMatchesExactWithinInput"],0)

    def test_verb_morphology_required(self):
        rows=[word("Gen.1.1",1,"7200","HNcmsa"),word("Gen.1.1",2,"l/5869 a")]
        self.assertEqual(engine.search(self.source(rows),PATTERN)["totalCandidateMatchesExactWithinInput"],0)

    def test_invalid_order_fails_closed(self):
        rows=[word("Gen.1.1",1,"7200","HVqp3ms"),word("Gen.1.1",1,"l/5869 a")]
        with self.assertRaisesRegex(ValueError,"word order"):
            engine.search(self.source(rows),PATTERN)

    def test_noncontiguous_reference_fails_closed(self):
        rows=[word("Gen.1.1",1,"7200","HVqp3ms"),word("Gen.1.2",1,"l/5869 a"),
              word("Gen.1.1",1,"7200","HVqp3ms")]
        with self.assertRaisesRegex(ValueError,"noncontiguous"):
            engine.search(self.source(rows),PATTERN)

    def test_reject_unsupported_clause_claim(self):
        self.source([word("Gen.1.1",1,"7200","HVqp3ms")])
        with self.assertRaisesRegex(ValueError,"same-clause"):
            engine.search(self.path,dict(PATTERN,scope="SAME_CLAUSE"))

    def test_reject_bad_distance(self):
        self.source([word("Gen.1.1",1,"7200","HVqp3ms")])
        with self.assertRaisesRegex(ValueError,"word-distance"):
            engine.search(self.path,dict(PATTERN,maxInterveningWords=101))

    def test_source_hash_and_scope_disclosure(self):
        self.source([word("Gen.1.1",1,"7200","HVqp3ms")])
        r=engine.search(self.path,PATTERN)
        self.assertEqual(len(r["sourceSha256"]),64)
        self.assertEqual(r["sourceCompleteness"],"UNVERIFIED_INPUT_SCOPE")

if __name__=="__main__":
    unittest.main()
