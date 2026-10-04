#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
SCRIPT = ROOT / "scripts/corpora/load_wb1_postgres.py"


def write_json(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def write_ndjson(path: Path, rows: list[dict]) -> None:
    path.write_text("".join(json.dumps(r, ensure_ascii=False, sort_keys=True) + "\n" for r in rows), encoding="utf-8")


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh, delimiter="\t"))


class WB1IdentityTests(unittest.TestCase):
    def test_common_stable_uuid_preserves_wb0_identity(self):
        code = (
            "from scripts.corpora.corpus_identity import stable_uuid;"
            "print(stable_uuid('reference-span','1Sam',16,7));"
            "print(stable_uuid('annotation-layer','OSHB_MORPHHB','MORPHOLOGY'));"
            "print(stable_uuid('annotation-layer','BHSA_2021','WB0_WORD_PHRASE_CLAUSE'))"
        )
        result = subprocess.run([sys.executable, "-c", code], cwd=ROOT, capture_output=True, text=True, check=False)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(
            result.stdout.splitlines(),
            [
                "4089aeaa-ddae-5adb-9510-1ca22845c4c2",
                "de8e8f74-c7fe-50ca-9c0d-4716a01d7657",
                "d59aeef3-2f5c-5d07-b0da-26a6dec58219",
            ],
        )


class WB1LoadsetTests(unittest.TestCase):
    def fixture(self, root: Path) -> dict[str, Path]:
        inventory = {
            "schemaVersion": "1.0",
            "inventoryType": "REFERENCE_SYSTEM_BOOTSTRAP_SNAPSHOT",
            "referenceSystemCode": "OSHB_OSIS",
            "authorityStatus": "BOOTSTRAP_SOURCE_DERIVED_NOT_FINAL_CANON_ADJUDICATION",
            "derivation": "PINNED_OSHB_SOURCE_XML_INDEPENDENT_OF_EXPORTER_OUTPUT",
            "sourceKey": "OSHB_MORPHHB",
            "sourceCommitSha": "oshb-pin",
            "sourceManifestSha256": "a" * 64,
            "providerBookDivisionCount": 1,
            "referenceCount": 2,
            "wordCount": 3,
            "referenceSetSha256": "b" * 64,
            "references": ["Gen.1.1", "Gen.1.2"],
            "bookDivisions": [{"providerBookCode": "Gen", "chapterCount": 1, "referenceCount": 2, "wordCount": 3, "sourceFile": "Gen.xml", "sourceFileSha256": "c" * 64}],
        }
        coverage = {
            "schemaVersion": "1.0",
            "milestone": "WB-CORPUS-001",
            "buildId": "fixture",
            "status": "COMPLETE_WITH_EXPLICIT_EXCEPTIONS",
            "gatePass": True,
            "sourcePins": {},
            "referenceSystem": {
                "code": "OSHB_OSIS",
                "authorityStatus": inventory["authorityStatus"],
                "derivation": inventory["derivation"],
                "expectedReferenceSpans": 2,
                "providerBookDivisionCount": 1,
                "referenceSetSha256": inventory["referenceSetSha256"],
                "note": "fixture",
            },
            "coverage": {
                "oshb": {"wordRecords": 3, "referenceSpans": 2},
                "bhsa": {"wordNodes": 4, "referenceSpans": 2},
                "crosswalk": {
                    "recordTypes": {"CANDIDATE_SPAN_MAPPING": 1, "ANNOTATION_ONLY_TARGET_NODE": 1, "UNRESOLVED_REFERENCE": 1},
                    "candidateMappings": 1,
                    "annotationOnlyNodes": 1,
                    "unresolvedReferenceSpans": 1,
                    "unresolvedReasons": {"VERSE_CONSONANTAL_STREAM_MISMATCH": 1},
                    "mappedSourceNodes": 2,
                    "mappedTargetNodes": 2,
                    "observedReferenceSpans": 2,
                },
                "silentReferenceLoss": 0,
            },
            "exceptions": {
                "oshbMissingExpectedReferences": [],
                "oshbProviderOnlyReferences": [],
                "bhsaMissingExpectedReferences": [],
                "bhsaProviderOnlyReferences": [],
                "crosswalkMissingProviderReferences": [],
                "crosswalkProviderOnlyReferences": [],
                "silentReferenceLossReferences": [],
                "unresolvedCrosswalkReferences": ["Gen.1.2"],
            },
            "exceptionCounts": {
                "oshbMissingExpectedReferences": 0,
                "oshbProviderOnlyReferences": 0,
                "bhsaMissingExpectedReferences": 0,
                "bhsaProviderOnlyReferences": 0,
                "crosswalkMissingProviderReferences": 0,
                "crosswalkProviderOnlyReferences": 0,
                "silentReferenceLossReferences": 0,
                "unresolvedCrosswalkReferences": 1,
            },
            "perBook": [],
            "artifacts": {},
        }
        oshb = [
            {"schemaVersion":"1.0","sourceKey":"OSHB_MORPHHB","providerScopedWordId":"o1","referenceSystemCode":"OSHB_OSIS","referenceLabel":"Gen.1.1","wordOrderInVerse":1,"surfaceSourceExact":"אב","lemmaRaw":"אב","morphRaw":"N"},
            {"schemaVersion":"1.0","sourceKey":"OSHB_MORPHHB","providerScopedWordId":"o2","referenceSystemCode":"OSHB_OSIS","referenceLabel":"Gen.1.1","wordOrderInVerse":2,"surfaceSourceExact":"גד","lemmaRaw":"גד","morphRaw":"N"},
            {"schemaVersion":"1.0","sourceKey":"OSHB_MORPHHB","providerScopedWordId":"o3","referenceSystemCode":"OSHB_OSIS","referenceLabel":"Gen.1.2","wordOrderInVerse":1,"surfaceSourceExact":"הו","lemmaRaw":"הו","morphRaw":"N"},
        ]
        bhsa = [
            {"schemaVersion":"1.0","sourceKey":"BHSA_2021","providerScopedNodeId":101,"referenceSystemCode":"BHSA_2021_SECTION","referenceLabel":"Genesis.1.1","wordOrderInVerse":1,"surfaceSourceExact":"אב","consonantalSourceExact":"אב","lexemeRaw":"אב","partOfSpeechRaw":"subs","phraseNodeId":201,"phraseFunctionRaw":"Subj","phraseTypeRaw":"NP","clauseNodeId":301,"clauseTypeRaw":"x","languageIsoRaw":"hbo"},
            {"schemaVersion":"1.0","sourceKey":"BHSA_2021","providerScopedNodeId":102,"referenceSystemCode":"BHSA_2021_SECTION","referenceLabel":"Genesis.1.1","wordOrderInVerse":2,"surfaceSourceExact":None,"consonantalSourceExact":None,"lexemeRaw":None,"partOfSpeechRaw":"art","phraseDependentPartOfSpeechRaw":"art","phraseNodeId":201,"phraseFunctionRaw":"Subj","phraseTypeRaw":"NP","clauseNodeId":301,"clauseTypeRaw":"x","languageIsoRaw":"hbo"},
            {"schemaVersion":"1.0","sourceKey":"BHSA_2021","providerScopedNodeId":103,"referenceSystemCode":"BHSA_2021_SECTION","referenceLabel":"Genesis.1.1","wordOrderInVerse":3,"surfaceSourceExact":"גד","consonantalSourceExact":"גד","lexemeRaw":"גד","partOfSpeechRaw":"subs","phraseNodeId":201,"phraseFunctionRaw":"Subj","phraseTypeRaw":"NP","clauseNodeId":301,"clauseTypeRaw":"x","languageIsoRaw":"hbo"},
            {"schemaVersion":"1.0","sourceKey":"BHSA_2021","providerScopedNodeId":104,"referenceSystemCode":"BHSA_2021_SECTION","referenceLabel":"Genesis.1.2","wordOrderInVerse":1,"surfaceSourceExact":"הו","consonantalSourceExact":"הו","lexemeRaw":"הו","partOfSpeechRaw":"subs","phraseNodeId":202,"phraseFunctionRaw":"Pred","phraseTypeRaw":"VP","clauseNodeId":301,"clauseTypeRaw":"x","languageIsoRaw":"hbo"},
        ]
        crosswalk = [
            {"schemaVersion":"1.0","recordType":"CANDIDATE_SPAN_MAPPING","reference":{"book":"Gen","chapter":1,"verse":1},"sourceProviderScopedWordIds":["o1","o2"],"targetProviderScopedNodeIds":[101,103],"sourceCount":2,"targetCount":2,"mappingMethod":"VERSE_CONSONANTAL_GREEDY_SPAN_V1","reviewStatus":"CANDIDATE_AUTOMATED","canonical":False,"signatureAlgorithm":"HEBREW_LETTERS_ONLY_NFD_V1","consonantalSignature":"אבגד"},
            {"schemaVersion":"1.0","recordType":"ANNOTATION_ONLY_TARGET_NODE","reference":{"book":"Gen","chapter":1,"verse":1},"targetProviderScopedNodeId":102,"reason":"BHSA_HEBREW_ARTICLE_EMPTY_ORTHOGRAPHIC_NODE"},
            {"schemaVersion":"1.0","recordType":"UNRESOLVED_REFERENCE","reference":{"book":"Gen","chapter":1,"verse":2},"reason":"VERSE_CONSONANTAL_STREAM_MISMATCH"},
        ]
        paths = {name: root / name for name in ["inventory.json","coverage.json","oshb.ndjson","bhsa.ndjson","crosswalk.ndjson"]}
        write_json(paths["inventory.json"], inventory)
        write_json(paths["coverage.json"], coverage)
        write_ndjson(paths["oshb.ndjson"], oshb)
        write_ndjson(paths["bhsa.ndjson"], bhsa)
        write_ndjson(paths["crosswalk.ndjson"], crosswalk)
        return paths

    def run_loader(self, root: Path, coverage_override: dict | None = None) -> subprocess.CompletedProcess[str]:
        paths = self.fixture(root)
        if coverage_override is not None:
            coverage = json.loads(paths["coverage.json"].read_text(encoding="utf-8"))
            coverage.update(coverage_override)
            write_json(paths["coverage.json"], coverage)
        return subprocess.run(
            [
                sys.executable, str(SCRIPT),
                "--inventory", str(paths["inventory.json"]),
                "--oshb", str(paths["oshb.ndjson"]),
                "--bhsa", str(paths["bhsa.ndjson"]),
                "--crosswalk", str(paths["crosswalk.ndjson"]),
                "--coverage-manifest", str(paths["coverage.json"]),
                "--loadset-dir", str(root / "loadset"),
                "--report", str(root / "report.json"),
                "--dry-run",
            ],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
        )

    def test_multiverse_loadset_uses_copy_preserves_unresolved_provider_nodes_and_range_spans(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            result = self.run_loader(root)
            self.assertEqual(result.returncode, 0, result.stderr + result.stdout)

            report = json.loads((root / "report.json").read_text(encoding="utf-8"))
            self.assertEqual(report["milestone"], "WB-1")
            self.assertEqual(report["counts"]["referenceVerseSpans"], 2)
            self.assertEqual(report["counts"]["referenceRangeSpans"], 1)
            self.assertEqual(report["counts"]["oshbWordNodes"], 3)
            self.assertEqual(report["counts"]["bhsaWordNodes"], 4)
            self.assertEqual(report["counts"]["bhsaAnnotationOnlyWordNodes"], 1)
            self.assertEqual(report["counts"]["bhsaPhraseNodes"], 2)
            self.assertEqual(report["counts"]["bhsaClauseNodes"], 1)
            self.assertEqual(report["counts"]["candidateMappingGroups"], 1)
            self.assertEqual(report["counts"]["unresolvedReferences"], 1)
            self.assertEqual(report["canonicalCandidateMappings"], 0)
            self.assertFalse(report["servingProjectionWritten"])

            load_sql = (root / "loadset" / "load.sql").read_text(encoding="utf-8")
            self.assertIn("\\copy authoring.text_segments", load_sql)
            self.assertNotIn("INSERT INTO authoring.text_segments", load_sql)

            nodes = read_tsv(root / "loadset" / "analysis_nodes.tsv")
            self.assertEqual({r["external_node_id"] for r in nodes if r["node_type"] == "WORD"}, {"o1","o2","o3","101","102","103","104"})
            annotation = next(r for r in nodes if r["external_node_id"] == "102")
            self.assertTrue(json.loads(annotation["metadata"])["annotationOnly"])

            spans = read_tsv(root / "loadset" / "reference_spans.tsv")
            self.assertEqual(len(spans), 3)

            segments = read_tsv(root / "loadset" / "text_segments.tsv")
            orders_by_stream: dict[str, set[int]] = {}
            for row in segments:
                orders_by_stream.setdefault(row["text_stream_id"], set())
                order = int(row["segment_order"])
                self.assertNotIn(order, orders_by_stream[row["text_stream_id"]])
                orders_by_stream[row["text_stream_id"]].add(order)

            groups = read_tsv(root / "loadset" / "cross_annotation_mapping_groups.tsv")
            self.assertEqual(len(groups), 1)
            self.assertEqual(groups[0]["canonical"], "false")

    def test_refuses_failed_source_foundation_gate(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = self.run_loader(Path(tmp), {"gatePass": False, "status": "FAILED"})
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("WB-1 refuses WB-CORPUS-001 gatePass=false", result.stderr + result.stdout)


if __name__ == "__main__":
    unittest.main()
