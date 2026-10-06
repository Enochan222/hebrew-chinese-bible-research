#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_SCHEMA = ROOT / "contracts/v1.1/json-schema/wb2-serving-build-report.schema.json"
DEFAULT_RELEASE_SCHEMA = ROOT / "contracts/v1.1/json-schema/release-manifest.schema.json"
DEFAULT_REGISTRY = ROOT / "contracts/v1.1/corpus-source-registry.json"
DEFAULT_CANON = ROOT / "contracts/v1.1/hebrew-bible-canon-system.json"


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def run_sql(sql: str, check: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["psql", "-X", "-v", "ON_ERROR_STOP=1", "-At", "-F", "\t", "-c", sql],
        check=check,
        capture_output=True,
        text=True,
    )


def role_scalar(role: str, sql: str) -> str:
    result = run_sql(f"SET ROLE {role}; {sql}; RESET ROLE;")
    lines = [
        line.strip()
        for line in result.stdout.splitlines()
        if line.strip() and line.strip() not in {"SET", "RESET"}
    ]
    return lines[-1] if lines else ""


def scalar(sql: str) -> str:
    result = run_sql(sql)
    lines = [line.strip() for line in result.stdout.splitlines() if line.strip()]
    return lines[-1] if lines else ""


def validate_json(schema_path: Path, value: dict, *, release_schema_path: Path | None = None) -> list[str]:
    schema = load(schema_path)
    if release_schema_path is not None:
        # Resolve the one local release-manifest reference explicitly so CI does
        # not depend on implicit filesystem URI resolution.
        schema = json.loads(json.dumps(schema))
        schema["properties"]["manifest"] = load(release_schema_path)
    validator = Draft202012Validator(schema)
    return [error.message for error in validator.iter_errors(value)]


def main() -> int:
    parser = argparse.ArgumentParser(description="Verify WB-2 materialization and public-release behavior.")
    parser.add_argument("--report", type=Path, required=True)
    parser.add_argument("--wb1-report", type=Path, required=True)
    parser.add_argument("--source-foundation-manifest", type=Path, required=True)
    parser.add_argument("--registry", type=Path, default=DEFAULT_REGISTRY)
    parser.add_argument("--canon", type=Path, default=DEFAULT_CANON)
    parser.add_argument("--schema", type=Path, default=DEFAULT_SCHEMA)
    parser.add_argument("--release-schema", type=Path, default=DEFAULT_RELEASE_SCHEMA)
    parser.add_argument("--phase", choices=("materialized", "published"), required=True)
    args = parser.parse_args()

    report = load(args.report)
    wb1 = load(args.wb1_report)
    foundation = load(args.source_foundation_manifest)
    registry = load(args.registry)
    canon = load(args.canon)
    errors: list[str] = []

    errors.extend(
        f"report schema: {e}"
        for e in validate_json(args.schema, report, release_schema_path=args.release_schema)
    )
    errors.extend(
        f"release manifest schema: {e}"
        for e in validate_json(args.release_schema, report.get("manifest", {}))
    )

    if report.get("sourceFoundationBuildId") != foundation.get("buildId"):
        errors.append("source foundation build identity mismatch")
    if wb1.get("sourceFoundation", {}).get("buildId") != foundation.get("buildId"):
        errors.append("WB-1/source foundation identity mismatch")
    if report.get("wb1AggregatePartitionHash") != wb1.get("aggregatePartitionHash"):
        errors.append("WB-2 is not pinned to the accepted WB-1 aggregate partition hash")

    expected_books = len([b for b in canon["books"] if b.get("included")])
    expected_words = wb1["totals"]["oshbWordRecords"]
    expected_refs = wb1["totals"]["selectedReferenceAtoms"]
    counts = report.get("counts", {})
    for key in ("authoringOshbNodes","authoringOshbSegments","servingCorpusNodes","servingTextSegments","servingNodeSegmentMemberships"):
        if counts.get(key) != expected_words:
            errors.append(f"{key} must equal accepted WB-1 OSHB word total {expected_words}")
    if counts.get("passageReferenceIndexRows") != expected_refs:
        errors.append("passage reference index must equal accepted selected ReferenceSystem size")
    if counts.get("configuredBooks") != expected_books or counts.get("passageReferenceIndexBooks") != expected_books:
        errors.append("WB-2 configured/serving book coverage mismatch")

    rights_by_source = {s["sourceKey"]: s["licensing"]["publicServingDefault"] for s in registry["sources"]}
    if rights_by_source.get("OSHB_MORPHHB") != "ALLOW_WITH_ATTRIBUTION":
        errors.append("OSHB registry rights default drift")
    excluded = {row["sourceKey"]: row for row in report.get("excludedSources", [])}
    if excluded.get("BHSA_2021", {}).get("publicServingDefault") != rights_by_source.get("BHSA_2021"):
        errors.append("BHSA exclusion does not match registry rights state")
    if excluded.get("ETCBC_BRIDGING_2021", {}).get("publicServingDefault") != rights_by_source.get("ETCBC_BRIDGING_2021"):
        errors.append("bridging exclusion does not match registry rights state")

    release_id = report["researchReleaseId"]
    if args.phase == "materialized":
        if scalar(
            f"SELECT count(*) FROM serving.research_release_events "
            f"WHERE research_release_id='{release_id}'::uuid AND event_type='PUBLISHED';"
        ) != "0":
            errors.append("materialized WB-2 release must remain inactive before publication")
        if role_scalar(
            "anon",
            f"SELECT count(*) FROM serving.research_release_components "
            f"WHERE research_release_id='{release_id}'::uuid;"
        ) != "0":
            errors.append("anon can observe inactive ResearchRelease components")
        if role_scalar(
            "anon",
            f"SELECT serving.get_passage_core('{release_id}'::uuid,'OSHB_OSIS','1Sam.16.7') IS NULL;"
        ) != "t":
            errors.append("inactive passage projection leaked before publication")

    else:
        if scalar(
            f"SELECT count(*) FROM serving.research_release_events "
            f"WHERE research_release_id='{release_id}'::uuid AND event_type='PUBLISHED';"
        ) != "1":
            errors.append("published WB-2 release must have exactly one PUBLISHED event")
        if role_scalar(
            "anon",
            "SELECT research_release_id::text FROM serving.current_release WHERE channel_key='PRODUCTION';"
        ) != release_id:
            errors.append("PRODUCTION pointer does not resolve to WB-2 release")
        if int(role_scalar("anon", "SELECT count(*) FROM serving.corpus_text_segments;") or "0") != expected_words:
            errors.append("anon Serving text-segment count differs from accepted WB-1 OSHB total")
        if int(role_scalar("anon", "SELECT count(*) FROM serving.corpus_nodes;") or "0") != expected_words:
            errors.append("anon Serving corpus-node count differs from accepted WB-1 OSHB total")
        if int(role_scalar("anon", "SELECT count(*) FROM serving.passage_reference_index;") or "0") != expected_refs:
            errors.append("anon passage index count differs from selected ReferenceSystem total")
        if int(role_scalar("anon", "SELECT count(DISTINCT book_code) FROM serving.passage_reference_index;") or "0") != expected_books:
            errors.append("anon passage index does not span all configured books")

        for label in ("Gen.1.1", "1Sam.16.7", "2Chr.36.23"):
            visible = role_scalar(
                "anon",
                f"SELECT serving.get_passage_core('{release_id}'::uuid,'OSHB_OSIS','{label}') IS NOT NULL;"
            )
            if visible != "t":
                errors.append(f"published passage read failed for {label}")
            has_segments = role_scalar(
                "anon",
                f"SELECT jsonb_array_length(serving.get_passage_core("
                f"'{release_id}'::uuid,'OSHB_OSIS','{label}')->'segments') > 0;"
            )
            if has_segments != "t":
                errors.append(f"published passage contains no OSHB segments for {label}")

        mutation = run_sql(
            "UPDATE serving.corpus_text_segments "
            "SET surface_original=surface_original "
            "WHERE (corpus_release_id,text_segment_id)=("
            "SELECT corpus_release_id,text_segment_id FROM serving.corpus_text_segments LIMIT 1"
            ");",
            check=False,
        )
        if mutation.returncode == 0:
            errors.append("published corpus text projection remained mutable")

        authoring_read = run_sql(
            "SET ROLE anon; SELECT count(*) FROM authoring.analysis_nodes; RESET ROLE;",
            check=False,
        )
        if authoring_read.returncode == 0:
            errors.append("anon unexpectedly retained Authoring read access")

        if scalar("SELECT count(*) FROM serving.corpus_nodes n JOIN authoring.annotation_layers l ON l.annotation_layer_id=n.annotation_layer_id JOIN authoring.annotation_frameworks f USING(annotation_framework_id) WHERE f.framework_key='BHSA_2021_REAL';") != "0":
            errors.append("BHSA-derived node leaked into Serving")
        if scalar("SELECT count(*) FROM serving.corpus_node_features WHERE feature_key LIKE 'BRIDGE_%';") != "0":
            errors.append("bridging-derived feature leaked into Serving")

    if errors:
        print(f"WB-2 {args.phase.upper()} VERIFICATION FAILED")
        for error in errors:
            print(f"- {error}")
        return 1

    print(
        f"WB-2 {args.phase} verified: release={release_id} "
        f"books={expected_books} refs={expected_refs} oshbWords={expected_words}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
