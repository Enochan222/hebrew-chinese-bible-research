#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
import tempfile
from pathlib import Path

from load_wb1_postgres import psql_file, psql_query, shared_ids, source_index, stable_uuid

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_REGISTRY = ROOT / "contracts/v1.1/corpus-source-registry.json"
DEFAULT_CANON = ROOT / "contracts/v1.1/hebrew-bible-canon-system.json"
COMPILER_VERSION = "wb2-rights-safe-serving-v1"
ATTRIBUTION_TEXT = (
    "Open Scriptures Hebrew Bible (morphhb). WLC text is public domain per upstream; "
    "lemma and morphology data are CC BY 4.0 per the pinned source registry."
)
LICENSE_LABEL = "WLC public domain; OSHB lemma/morphology CC BY 4.0"


def sql_literal(value: object) -> str:
    if value is None:
        return "NULL"
    if isinstance(value, bool):
        return "TRUE" if value else "FALSE"
    return "'" + str(value).replace("'", "''") + "'"


def canonical_json(value: object) -> str:
    # This manifest contains only JSON strings, integers, arrays and objects.
    # For this value domain, sorted-key compact UTF-8 JSON is RFC 8785-equivalent.
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def canonical_hash(value: object) -> str:
    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def scalar(sql: str) -> str:
    return psql_query(sql).strip()


def count(sql: str) -> int:
    raw = scalar(sql)
    return int(raw or "0")


def rows(sql: str) -> list[list[str]]:
    return [line.split("\t") for line in psql_query(sql).splitlines() if line]


def symmetric_difference_count(left_sql: str, right_sql: str) -> int:
    sql = f"""
WITH left_rows AS (
{left_sql.rstrip().rstrip(";")}
),
right_rows AS (
{right_sql.rstrip().rstrip(";")}
),
left_minus_right AS (
  SELECT * FROM left_rows
  EXCEPT ALL
  SELECT * FROM right_rows
),
right_minus_left AS (
  SELECT * FROM right_rows
  EXCEPT ALL
  SELECT * FROM left_rows
)
SELECT
  (SELECT count(*) FROM left_minus_right)
  +
  (SELECT count(*) FROM right_minus_left);
"""
    return count(sql)


def stream_hash_sections(sections: list[tuple[str, str]]) -> str:
    """Hash projection row multisets while retaining semantic order keys in rows.

    Query planners may emit the same relational projection in different physical
    row orders. Every WB-2 projection row already carries its semantic ordering
    key (for example segment_order or reference_sort_key), so the stable release
    hash sorts per-row SHA-256 digests rather than depending on iterator order.
    Duplicate rows remain significant because duplicate digests are retained.
    """
    digest = hashlib.sha256()
    for section_name, sql in sections:
        row_digests: list[bytes] = []
        proc = subprocess.Popen(
            ["psql", "-X", "-v", "ON_ERROR_STOP=1", "-At", "-F", "\t", "-c", sql],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        assert proc.stdout is not None
        assert proc.stderr is not None
        for line in proc.stdout:
            row_digests.append(hashlib.sha256(line.rstrip("\n").encode("utf-8")).digest())
        stderr = proc.stderr.read()
        returncode = proc.wait()
        if returncode != 0:
            raise RuntimeError(
                f"psql projection-hash query failed for {section_name}: {stderr}"
            )
        digest.update(b"WB2-SECTION-MULTISET\0")
        digest.update(section_name.encode("utf-8"))
        digest.update(b"\0")
        digest.update(str(len(row_digests)).encode("ascii"))
        digest.update(b"\0")
        for row_digest in sorted(row_digests):
            digest.update(row_digest)
        digest.update(b"\0WB2-END-SECTION\0")
    return digest.hexdigest()

def main() -> int:
    parser = argparse.ArgumentParser(
        description="Materialize an inactive rights-safe WB-2 OSHB Serving projection from accepted WB-1 Authoring data."
    )
    parser.add_argument("--source-foundation-manifest", type=Path, required=True)
    parser.add_argument("--wb1-report", type=Path, required=True)
    parser.add_argument("--registry", type=Path, default=DEFAULT_REGISTRY)
    parser.add_argument("--canon", type=Path, default=DEFAULT_CANON)
    parser.add_argument("--git-commit-sha", default=os.environ.get("GITHUB_SHA"))
    parser.add_argument("--report", type=Path, required=True)
    parser.add_argument("--sql-output", type=Path)
    args = parser.parse_args()

    if not args.git_commit_sha or not re.fullmatch(r"[0-9a-fA-F]{40}", args.git_commit_sha):
        raise SystemExit("--git-commit-sha must be an exact 40-hex commit SHA")

    foundation = load(args.source_foundation_manifest)
    wb1 = load(args.wb1_report)
    registry = load(args.registry)
    canon = load(args.canon)
    sources = source_index(registry)
    ids = shared_ids(sources)

    if foundation.get("gatePass") is not True:
        raise SystemExit("WB-2 requires accepted WB-CORPUS-001 gatePass=true")
    if wb1.get("milestone") != "WB-1" or wb1.get("gate", {}).get("coreFreezeWb002EvidenceReady") is not True:
        raise SystemExit("WB-2 requires accepted WB-1 relational evidence")
    if wb1.get("sourceFoundation", {}).get("buildId") != foundation.get("buildId"):
        raise SystemExit("WB-2 WB-1/source-foundation build identity mismatch")

    source_rights = {s["sourceKey"]: s["licensing"] for s in registry["sources"]}
    if source_rights["OSHB_MORPHHB"]["publicServingDefault"] != "ALLOW_WITH_ATTRIBUTION":
        raise SystemExit("OSHB source registry is not publishable under the WB-2 attribution policy")
    if source_rights["BHSA_2021"]["publicServingDefault"] == "ALLOW_WITH_ATTRIBUTION":
        raise SystemExit("BHSA unexpectedly became auto-publishable; explicit rights review is required")
    if source_rights["ETCBC_BRIDGING_2021"]["publicServingDefault"] != "DENY_UNTIL_RIGHTS_REVIEW":
        raise SystemExit("bridging rights boundary drift")

    selected_canon = canon["canonSystem"]["code"]
    included_books = [b for b in canon["books"] if b.get("included")]
    if len(included_books) != wb1["totals"]["configuredBooks"]:
        raise SystemExit("WB-2 canon/WB-1 configured-book count mismatch")

    oshb_corpus = ids["oshbCorpus"]
    oshb_layer = ids["oshbLayer"]
    oshb_stream = ids["oshbStream"]
    bhsa_layer = ids["bhsaLayer"]

    oshb_source_checksum = scalar(
        f"SELECT COALESCE(source_checksum,'') FROM authoring.corpus_releases "
        f"WHERE corpus_release_id='{oshb_corpus}'::uuid;"
    )
    oshb_layer_hash = scalar(
        f"SELECT COALESCE(content_hash,'') FROM authoring.annotation_layers "
        f"WHERE annotation_layer_id='{oshb_layer}'::uuid;"
    )
    if not re.fullmatch(r"[0-9a-fA-F]{64}", oshb_source_checksum):
        raise SystemExit("OSHB corpus source checksum is missing or not SHA-256")
    if not re.fullmatch(r"[0-9a-fA-F]{64}", oshb_layer_hash):
        raise SystemExit("OSHB annotation-layer content hash is missing or not SHA-256")

    authoring_reference_projection_sql = f"""
WITH label_ranges AS (
  SELECT
    rl.reference_system_id,rsys.code AS reference_system_code,rl.label AS reference_label,
    rl.book_id,b.osis_code AS book_code,rl.chapter_number,rl.verse_label,
    min(rlm.atom_sequence) AS start_sequence,
    max(rlm.atom_sequence) AS end_sequence
  FROM authoring.reference_labels rl
  JOIN authoring.reference_systems rsys USING (reference_system_id)
  JOIN authoring.reference_label_members rlm
    ON rlm.reference_label_id=rl.reference_label_id
   AND rlm.book_id=rl.book_id
  JOIN authoring.biblical_books b ON b.book_id=rl.book_id
  WHERE rsys.code='OSHB_OSIS'
  GROUP BY
    rl.reference_system_id,rsys.code,rl.label,rl.book_id,b.osis_code,
    rl.chapter_number,rl.verse_label
)
SELECT
  lr.reference_system_id::text,lr.reference_system_code,lr.reference_label,
  sp.reference_span_id::text,lr.book_code,
  COALESCE(lr.chapter_number::text,''),COALESCE(lr.verse_label,''),
  (cb.book_order::bigint * 1000000 + lr.start_sequence)::text
FROM label_ranges lr
JOIN authoring.reference_spans sp
  ON sp.book_id=lr.book_id
 AND sp.start_sequence=lr.start_sequence
 AND sp.end_sequence=lr.end_sequence
 AND sp.span_kind='VERSE'
JOIN authoring.canon_books cb ON cb.book_id=lr.book_id
JOIN authoring.canon_systems cs USING (canon_system_id)
WHERE cs.code={sql_literal(selected_canon)}
  AND cb.included
ORDER BY cb.book_order,lr.start_sequence,lr.reference_system_code,lr.reference_label;
"""
    authoring_text_projection_sql = f"""
SELECT
  s.text_segment_id::text,s.reference_span_id::text,s.segment_order::text,
  'OSHB_MORPHHB',s.surface_original,s.segment_kind,s.content_hash
FROM authoring.text_segments s
WHERE s.text_stream_id={sql_literal(oshb_stream)}::uuid
  AND s.segment_storage_mode='PERSISTED_CONTENT'
  AND s.surface_original IS NOT NULL
  AND s.content_hash IS NOT NULL
ORDER BY s.segment_order,s.text_segment_id;
"""
    authoring_nodes_projection_sql = f"""
SELECT
  n.analysis_node_id::text,n.annotation_layer_id::text,n.node_type,n.reference_span_id::text
FROM authoring.analysis_nodes n
WHERE n.annotation_layer_id={sql_literal(oshb_layer)}::uuid
ORDER BY n.analysis_node_id;
"""
    authoring_features_projection_sql = f"""
SELECT f.analysis_node_id::text,f.feature_key,f.feature_value
FROM authoring.analysis_node_features f
JOIN authoring.analysis_nodes n USING (analysis_node_id)
WHERE n.annotation_layer_id={sql_literal(oshb_layer)}::uuid
ORDER BY f.analysis_node_id,f.feature_key,f.feature_value;
"""
    authoring_membership_projection_sql = f"""
SELECT
  ns.analysis_node_id::text,ns.text_segment_id::text,ns.member_order::text,
  COALESCE(ns.membership_role,'')
FROM authoring.analysis_node_segments ns
JOIN authoring.analysis_nodes n USING (analysis_node_id)
WHERE n.annotation_layer_id={sql_literal(oshb_layer)}::uuid
ORDER BY ns.analysis_node_id,ns.member_order,ns.text_segment_id;
"""
    attribution_projection_sql = (
        "SELECT 'OSHB_MORPHHB'::text AS source_key,"
        + sql_literal(ATTRIBUTION_TEXT)
        + "::text AS attribution_text,"
        + sql_literal(LICENSE_LABEL)
        + "::text AS license_label;"
    )

    authoring_corpus_projection_hash = stream_hash_sections([
        ("reference-index", authoring_reference_projection_sql),
        ("text-segments", authoring_text_projection_sql),
        ("attribution", attribution_projection_sql),
    ])
    authoring_annotation_projection_hash = stream_hash_sections([
        ("analysis-nodes", authoring_nodes_projection_sql),
        ("analysis-node-features", authoring_features_projection_sql),
        ("analysis-node-segments", authoring_membership_projection_sql),
    ])

    build_id = stable_uuid("research-build", "WB-2", foundation["buildId"], args.git_commit_sha)
    release_id = stable_uuid("research-release", "WB-2", foundation["buildId"], args.git_commit_sha)
    rights_policy_id = stable_uuid("rights-policy", "OSHB_MORPHHB", "WB2_PUBLIC_COMMERCIAL_V1")
    storage_rule_id = stable_uuid("rights-rule", "OSHB_MORPHHB", "STORE_EXTRACTED_TEXT", "WB2")
    display_rule_id = stable_uuid("rights-rule", "OSHB_MORPHHB", "DISPLAY_FULLTEXT", "WB2")
    storage_snapshot_id = stable_uuid("rights-snapshot", str(release_id), "STORE_EXTRACTED_TEXT")
    display_snapshot_id = stable_uuid("rights-snapshot", str(release_id), "DISPLAY_FULLTEXT")
    production_channel_id = stable_uuid("release-channel", "PRODUCTION")
    release_label = f"wb2-oshb-{str(foundation['buildId'])[:16]}"

    component_version = sources["OSHB_MORPHHB"]["pin"]["commitSha"]
    components = [
        {
            "componentKind": "CORPUS",
            "researchObjectId": oshb_corpus,
            "componentVersion": component_version,
            "contentHash": authoring_corpus_projection_hash,
            "componentOrder": 0,
        },
        {
            "componentKind": "ANNOTATION_LAYER",
            "researchObjectId": oshb_layer,
            "componentVersion": component_version,
            "contentHash": authoring_annotation_projection_hash,
            "componentOrder": 1,
        },
    ]
    manifest = {
        "manifestSchemaVersion": "1.1",
        "researchReleaseId": release_id,
        "releaseLabel": release_label,
        "sourceBuildId": build_id,
        "compilerVersion": COMPILER_VERSION,
        "gitCommitSha": args.git_commit_sha.lower(),
        "canonicalSerialization": "RFC8785_JSON_CANONICALIZATION_SCHEME",
        "hashAlgorithm": "SHA256",
        "components": components,
    }
    manifest_hash = canonical_hash(manifest)

    storage_snapshot = {
        "schemaVersion": "1.1",
        "snapshotId": storage_snapshot_id,
        "subjectType": "CORPUS_RELEASE",
        "subjectIdentifier": oshb_corpus,
        "operation": "STORE_EXTRACTED_TEXT",
        "purposeScope": "PUBLICATION",
        "audienceScope": "INTERNAL_SERVICE",
        "commercialContext": "COMMERCIAL",
        "applicableRuleIds": [storage_rule_id],
        "winningRuleIds": [storage_rule_id],
        "decision": "ALLOW",
        "decisionBasis": "RULE",
        "conditions": None,
        "obligations": [],
        "resolverVersion": "wb2-registry-rights-v1",
    }
    display_snapshot = {
        "schemaVersion": "1.1",
        "snapshotId": display_snapshot_id,
        "subjectType": "CORPUS_RELEASE",
        "subjectIdentifier": oshb_corpus,
        "operation": "DISPLAY_FULLTEXT",
        "purposeScope": "PUBLIC_DISPLAY",
        "audienceScope": "PUBLIC",
        "commercialContext": "COMMERCIAL",
        "applicableRuleIds": [display_rule_id],
        "winningRuleIds": [display_rule_id],
        "decision": "CONDITIONAL",
        "decisionBasis": "RULE",
        "conditions": None,
        "obligations": [{"obligationType": "ATTRIBUTION", "value": ATTRIBUTION_TEXT}],
        "resolverVersion": "wb2-registry-rights-v1",
    }
    storage_hash = canonical_hash(storage_snapshot)
    display_hash = canonical_hash(display_snapshot)

    sql = f"""\set ON_ERROR_STOP on
BEGIN;

INSERT INTO authoring.research_builds(
  research_build_id,build_version,status,started_at,completed_at,compiler_version,git_commit_sha
) VALUES (
  {sql_literal(build_id)}::uuid,'WB-2','COMPLETED',now(),now(),
  {sql_literal(COMPILER_VERSION)},{sql_literal(args.git_commit_sha.lower())}
);

INSERT INTO authoring.rights_policies(
  rights_policy_id,policy_key,policy_version,rights_basis,verified_at
) VALUES (
  {sql_literal(rights_policy_id)}::uuid,'OSHB_MORPHHB_PUBLIC_SERVING','1',
  {sql_literal(source_rights["OSHB_MORPHHB"]["dataLicense"])},now()
);

INSERT INTO authoring.rights_rules(
  rights_rule_id,rights_policy_id,operation,decision,purpose_scope,audience_scope,
  commercial_context,attribution_requirement
) VALUES
(
  {sql_literal(storage_rule_id)}::uuid,{sql_literal(rights_policy_id)}::uuid,
  'STORE_EXTRACTED_TEXT','ALLOW','PUBLICATION','INTERNAL_SERVICE','COMMERCIAL',NULL
),
(
  {sql_literal(display_rule_id)}::uuid,{sql_literal(rights_policy_id)}::uuid,
  'DISPLAY_FULLTEXT','CONDITIONAL','PUBLIC_DISPLAY','PUBLIC','COMMERCIAL',
  {sql_literal(ATTRIBUTION_TEXT)}
);

DO $rights_eval$
BEGIN
  IF authoring.evaluate_rights(
       {sql_literal(rights_policy_id)}::uuid,'STORE_EXTRACTED_TEXT',
       'PUBLICATION','INTERNAL_SERVICE','COMMERCIAL'
     ) <> 'ALLOW' THEN
    RAISE EXCEPTION 'OSHB storage rights did not resolve ALLOW';
  END IF;
  IF authoring.evaluate_rights(
       {sql_literal(rights_policy_id)}::uuid,'DISPLAY_FULLTEXT',
       'PUBLIC_DISPLAY','PUBLIC','COMMERCIAL'
     ) <> 'CONDITIONAL' THEN
    RAISE EXCEPTION 'OSHB public-display rights did not resolve CONDITIONAL';
  END IF;
END
$rights_eval$;

INSERT INTO serving.research_objects(research_object_id,object_type,source_content_hash,published_at)
VALUES
({sql_literal(oshb_corpus)}::uuid,'CORPUS_RELEASE',{sql_literal(authoring_corpus_projection_hash)},now()),
({sql_literal(oshb_layer)}::uuid,'ANNOTATION_LAYER',{sql_literal(authoring_annotation_projection_hash)},now());

INSERT INTO serving.rights_decision_snapshots(
  rights_decision_snapshot_id,subject_type,subject_identifier,operation,purpose_scope,
  audience_scope,commercial_context,applicable_rule_ids,winning_rule_ids,decision,
  decision_basis,conditions_json,obligations_json,resolver_version,evaluated_at,decision_hash
) VALUES
(
  {sql_literal(storage_snapshot_id)}::uuid,'CORPUS_RELEASE',{sql_literal(oshb_corpus)}::uuid,
  'STORE_EXTRACTED_TEXT','PUBLICATION','INTERNAL_SERVICE','COMMERCIAL',
  ARRAY[{sql_literal(storage_rule_id)}::uuid],ARRAY[{sql_literal(storage_rule_id)}::uuid],
  'ALLOW','RULE',NULL,'[]'::jsonb,'wb2-registry-rights-v1',now(),{sql_literal(storage_hash)}
),
(
  {sql_literal(display_snapshot_id)}::uuid,'CORPUS_RELEASE',{sql_literal(oshb_corpus)}::uuid,
  'DISPLAY_FULLTEXT','PUBLIC_DISPLAY','PUBLIC','COMMERCIAL',
  ARRAY[{sql_literal(display_rule_id)}::uuid],ARRAY[{sql_literal(display_rule_id)}::uuid],
  'CONDITIONAL','RULE',NULL,
  {sql_literal(json.dumps(display_snapshot["obligations"], ensure_ascii=False, separators=(",", ":")))}::jsonb,
  'wb2-registry-rights-v1',now(),{sql_literal(display_hash)}
);

INSERT INTO serving.corpus_projection_rights(
  corpus_release_id,operation,rights_decision_snapshot_id
) VALUES
({sql_literal(oshb_corpus)}::uuid,'STORE_EXTRACTED_TEXT',{sql_literal(storage_snapshot_id)}::uuid),
({sql_literal(oshb_corpus)}::uuid,'DISPLAY_FULLTEXT',{sql_literal(display_snapshot_id)}::uuid);

INSERT INTO serving.corpus_attributions(
  corpus_release_id,source_key,attribution_text,license_label
) VALUES (
  {sql_literal(oshb_corpus)}::uuid,'OSHB_MORPHHB',
  {sql_literal(ATTRIBUTION_TEXT)},{sql_literal(LICENSE_LABEL)}
);

INSERT INTO serving.reference_spans(
  reference_span_id,book_code,start_sequence,end_sequence,reference_sort_key,span_kind
)
SELECT DISTINCT
  rs.reference_span_id,b.osis_code,rs.start_sequence,rs.end_sequence,
  cb.book_order::bigint * 1000000 + rs.start_sequence,
  rs.span_kind
FROM authoring.reference_spans rs
JOIN authoring.biblical_books b USING (book_id)
JOIN authoring.canon_books cb USING (book_id)
JOIN authoring.canon_systems cs USING (canon_system_id)
JOIN authoring.analysis_nodes n ON n.reference_span_id=rs.reference_span_id
WHERE n.annotation_layer_id={sql_literal(oshb_layer)}::uuid
  AND cs.code={sql_literal(selected_canon)}
  AND cb.included
ON CONFLICT (reference_span_id) DO NOTHING;

INSERT INTO serving.corpus_nodes(
  corpus_release_id,analysis_node_id,annotation_layer_id,node_type,reference_span_id
)
SELECT
  {sql_literal(oshb_corpus)}::uuid,n.analysis_node_id,n.annotation_layer_id,n.node_type,n.reference_span_id
FROM authoring.analysis_nodes n
WHERE n.annotation_layer_id={sql_literal(oshb_layer)}::uuid;

INSERT INTO serving.corpus_node_features(
  corpus_release_id,analysis_node_id,feature_key,feature_value
)
SELECT
  {sql_literal(oshb_corpus)}::uuid,f.analysis_node_id,f.feature_key,f.feature_value
FROM authoring.analysis_node_features f
JOIN authoring.analysis_nodes n USING (analysis_node_id)
WHERE n.annotation_layer_id={sql_literal(oshb_layer)}::uuid;

INSERT INTO serving.corpus_text_segments(
  corpus_release_id,text_segment_id,reference_span_id,segment_order,source_key,
  surface_original,segment_kind,content_hash,
  storage_rights_decision_snapshot_id,display_rights_decision_snapshot_id
)
SELECT
  {sql_literal(oshb_corpus)}::uuid,s.text_segment_id,s.reference_span_id,s.segment_order,
  'OSHB_MORPHHB',s.surface_original,s.segment_kind,s.content_hash,
  {sql_literal(storage_snapshot_id)}::uuid,{sql_literal(display_snapshot_id)}::uuid
FROM authoring.text_segments s
WHERE s.text_stream_id={sql_literal(oshb_stream)}::uuid
  AND s.segment_storage_mode='PERSISTED_CONTENT'
  AND s.surface_original IS NOT NULL
  AND s.content_hash IS NOT NULL;

INSERT INTO serving.corpus_node_segments(
  corpus_release_id,analysis_node_id,text_segment_id,member_order,membership_role
)
SELECT
  {sql_literal(oshb_corpus)}::uuid,ns.analysis_node_id,ns.text_segment_id,ns.member_order,ns.membership_role
FROM authoring.analysis_node_segments ns
JOIN authoring.analysis_nodes n USING (analysis_node_id)
WHERE n.annotation_layer_id={sql_literal(oshb_layer)}::uuid;

WITH label_ranges AS (
  SELECT
    rl.reference_system_id,rsys.code AS reference_system_code,rl.label AS reference_label,
    rl.book_id,b.osis_code AS book_code,rl.chapter_number,rl.verse_label,
    min(rlm.atom_sequence) AS start_sequence,
    max(rlm.atom_sequence) AS end_sequence
  FROM authoring.reference_labels rl
  JOIN authoring.reference_systems rsys USING (reference_system_id)
  JOIN authoring.reference_label_members rlm
    ON rlm.reference_label_id=rl.reference_label_id
   AND rlm.book_id=rl.book_id
  JOIN authoring.biblical_books b ON b.book_id=rl.book_id
  WHERE rsys.code='OSHB_OSIS'
  GROUP BY
    rl.reference_system_id,rsys.code,rl.label,rl.book_id,b.osis_code,
    rl.chapter_number,rl.verse_label
)
INSERT INTO serving.passage_reference_index(
  corpus_release_id,reference_system_id,reference_system_code,reference_label,
  reference_span_id,book_code,chapter_number,verse_label,reference_sort_key
)
SELECT
  {sql_literal(oshb_corpus)}::uuid,lr.reference_system_id,lr.reference_system_code,
  lr.reference_label,sp.reference_span_id,lr.book_code,lr.chapter_number,lr.verse_label,
  cb.book_order::bigint * 1000000 + lr.start_sequence
FROM label_ranges lr
JOIN authoring.reference_spans sp
  ON sp.book_id=lr.book_id
 AND sp.start_sequence=lr.start_sequence
 AND sp.end_sequence=lr.end_sequence
 AND sp.span_kind='VERSE'
JOIN authoring.canon_books cb ON cb.book_id=lr.book_id
JOIN authoring.canon_systems cs USING (canon_system_id)
WHERE cs.code={sql_literal(selected_canon)}
  AND cb.included;

INSERT INTO serving.research_releases(
  research_release_id,release_label,source_build_id,published_at,
  manifest_schema_version,manifest_hash,manifest_hash_algorithm,
  manifest_canonical_serialization,git_commit_sha,compiler_version
) VALUES (
  {sql_literal(release_id)}::uuid,{sql_literal(release_label)},{sql_literal(build_id)}::uuid,now(),
  '1.1',{sql_literal(manifest_hash)},'SHA256','RFC8785_JSON_CANONICALIZATION_SCHEME',
  {sql_literal(args.git_commit_sha.lower())},{sql_literal(COMPILER_VERSION)}
);

INSERT INTO serving.research_release_components(
  research_release_id,component_kind,component_research_object_id,
  component_version,content_hash,component_order
) VALUES
(
  {sql_literal(release_id)}::uuid,'CORPUS',{sql_literal(oshb_corpus)}::uuid,
  {sql_literal(component_version)},{sql_literal(authoring_corpus_projection_hash)},0
),
(
  {sql_literal(release_id)}::uuid,'ANNOTATION_LAYER',{sql_literal(oshb_layer)}::uuid,
  {sql_literal(component_version)},{sql_literal(authoring_annotation_projection_hash)},1
);

INSERT INTO serving.release_channels(release_channel_id,channel_key,description)
VALUES ({sql_literal(production_channel_id)}::uuid,'PRODUCTION','Production pointer')
ON CONFLICT (channel_key) DO NOTHING;

COMMIT;
"""

    if args.sql_output:
        sql_path = args.sql_output
        sql_path.parent.mkdir(parents=True, exist_ok=True)
        sql_path.write_text(sql, encoding="utf-8")
        keep_sql = True
    else:
        tmp = tempfile.NamedTemporaryFile("w", suffix=".sql", delete=False, encoding="utf-8")
        tmp.write(sql)
        tmp.close()
        sql_path = Path(tmp.name)
        keep_sql = False

    try:
        psql_file(sql_path)
    finally:
        if not keep_sql:
            sql_path.unlink(missing_ok=True)

    serving_reference_projection_sql = f"""
SELECT
  reference_system_id::text,reference_system_code,reference_label,
  reference_span_id::text,book_code,COALESCE(chapter_number::text,''),
  COALESCE(verse_label,''),reference_sort_key::text
FROM serving.passage_reference_index
WHERE corpus_release_id={sql_literal(oshb_corpus)}::uuid
ORDER BY reference_sort_key,reference_system_code,reference_label;
"""
    serving_text_projection_sql = f"""
SELECT
  text_segment_id::text,reference_span_id::text,segment_order::text,
  source_key,surface_original,segment_kind,content_hash
FROM serving.corpus_text_segments
WHERE corpus_release_id={sql_literal(oshb_corpus)}::uuid
ORDER BY segment_order,text_segment_id;
"""
    serving_attribution_projection_sql = f"""
SELECT source_key::text AS source_key,
       attribution_text::text AS attribution_text,
       license_label::text AS license_label
FROM serving.corpus_attributions
WHERE corpus_release_id={sql_literal(oshb_corpus)}::uuid
ORDER BY source_key;
"""
    serving_nodes_projection_sql = f"""
SELECT analysis_node_id::text,annotation_layer_id::text,node_type,reference_span_id::text
FROM serving.corpus_nodes
WHERE corpus_release_id={sql_literal(oshb_corpus)}::uuid
ORDER BY analysis_node_id;
"""
    serving_features_projection_sql = f"""
SELECT analysis_node_id::text,feature_key,feature_value
FROM serving.corpus_node_features
WHERE corpus_release_id={sql_literal(oshb_corpus)}::uuid
ORDER BY analysis_node_id,feature_key,feature_value;
"""
    serving_membership_projection_sql = f"""
SELECT
  analysis_node_id::text,text_segment_id::text,member_order::text,
  COALESCE(membership_role,'')
FROM serving.corpus_node_segments
WHERE corpus_release_id={sql_literal(oshb_corpus)}::uuid
ORDER BY analysis_node_id,member_order,text_segment_id;
"""

    authoring_reference_hash = stream_hash_sections([("reference-index", authoring_reference_projection_sql)])
    serving_reference_hash = stream_hash_sections([("reference-index", serving_reference_projection_sql)])
    authoring_text_hash = stream_hash_sections([("text-segments", authoring_text_projection_sql)])
    serving_text_hash = stream_hash_sections([("text-segments", serving_text_projection_sql)])
    authoring_attribution_hash = stream_hash_sections([("attribution", attribution_projection_sql)])
    serving_attribution_hash = stream_hash_sections([("attribution", serving_attribution_projection_sql)])

    reference_projection_diff_rows = symmetric_difference_count(
        authoring_reference_projection_sql, serving_reference_projection_sql
    )
    text_projection_diff_rows = symmetric_difference_count(
        authoring_text_projection_sql, serving_text_projection_sql
    )
    attribution_projection_diff_rows = symmetric_difference_count(
        attribution_projection_sql, serving_attribution_projection_sql
    )

    serving_corpus_projection_hash = stream_hash_sections([
        ("reference-index", serving_reference_projection_sql),
        ("text-segments", serving_text_projection_sql),
        ("attribution", serving_attribution_projection_sql),
    ])
    serving_annotation_projection_hash = stream_hash_sections([
        ("analysis-nodes", serving_nodes_projection_sql),
        ("analysis-node-features", serving_features_projection_sql),
        ("analysis-node-segments", serving_membership_projection_sql),
    ])

    authoring_oshb_nodes = count(
        f"SELECT count(*) FROM authoring.analysis_nodes WHERE annotation_layer_id='{oshb_layer}'::uuid;"
    )
    authoring_oshb_segments = count(
        f"SELECT count(*) FROM authoring.text_segments WHERE text_stream_id='{oshb_stream}'::uuid "
        "AND segment_storage_mode='PERSISTED_CONTENT' AND surface_original IS NOT NULL;"
    )
    serving_nodes = count(
        f"SELECT count(*) FROM serving.corpus_nodes WHERE corpus_release_id='{oshb_corpus}'::uuid;"
    )
    serving_segments = count(
        f"SELECT count(*) FROM serving.corpus_text_segments WHERE corpus_release_id='{oshb_corpus}'::uuid;"
    )
    serving_node_segments = count(
        f"SELECT count(*) FROM serving.corpus_node_segments WHERE corpus_release_id='{oshb_corpus}'::uuid;"
    )
    reference_index = count(
        f"SELECT count(*) FROM serving.passage_reference_index WHERE corpus_release_id='{oshb_corpus}'::uuid;"
    )
    reference_books = count(
        f"SELECT count(DISTINCT book_code) FROM serving.passage_reference_index "
        f"WHERE corpus_release_id='{oshb_corpus}'::uuid;"
    )
    bhsa_node_leaks = count(
        f"SELECT count(*) FROM serving.corpus_nodes WHERE annotation_layer_id='{bhsa_layer}'::uuid;"
    )
    bridge_feature_leaks = count(
        "SELECT count(*) FROM serving.corpus_node_features WHERE feature_key LIKE 'BRIDGE_%';"
    )
    non_oshb_segments = count(
        "SELECT count(*) FROM serving.corpus_text_segments WHERE source_key <> 'OSHB_MORPHHB';"
    )
    release_components = count(
        f"SELECT count(*) FROM serving.research_release_components "
        f"WHERE research_release_id='{release_id}'::uuid;"
    )
    published_events = count(
        f"SELECT count(*) FROM serving.research_release_events "
        f"WHERE research_release_id='{release_id}'::uuid AND event_type='PUBLISHED';"
    )
    rights_rows = {
        operation: decision
        for operation, decision in rows(
            f"SELECT operation,decision FROM serving.rights_decision_snapshots "
            f"WHERE subject_type='CORPUS_RELEASE' AND subject_identifier='{oshb_corpus}'::uuid "
            "ORDER BY operation;"
        )
    }

    expected_oshb = int(wb1["totals"]["oshbWordRecords"])
    expected_refs = int(wb1["totals"]["selectedReferenceAtoms"])
    expected_books = int(wb1["totals"]["configuredBooks"])

    checks = {
        "authoringOshbNodesMatchWb1": authoring_oshb_nodes == expected_oshb,
        "authoringOshbSegmentsMatchWb1": authoring_oshb_segments == expected_oshb,
        "servingNodesMatchAuthoring": serving_nodes == authoring_oshb_nodes,
        "servingSegmentsMatchAuthoring": serving_segments == authoring_oshb_segments,
        "nodeSegmentMembershipComplete": serving_node_segments == serving_nodes,
        "referenceIndexMatchesSelectedReferences": reference_index == expected_refs,
        "referenceIndexCoversConfiguredBooks": reference_books == expected_books,
        "bhsaServingLeakCountZero": bhsa_node_leaks == 0,
        "bridgingServingLeakCountZero": bridge_feature_leaks == 0,
        "nonOshbServingSegmentCountZero": non_oshb_segments == 0,
        "releaseHasExpectedComponents": release_components == 2,
        "candidateRemainsInactive": published_events == 0,
        "oshbStorageRightsAllow": rights_rows.get("STORE_EXTRACTED_TEXT") == "ALLOW",
        "oshbDisplayRightsConditionalAttribution": rights_rows.get("DISPLAY_FULLTEXT") == "CONDITIONAL",
        "referenceProjectionRowsMatchAuthoring": reference_projection_diff_rows == 0,
        "textProjectionRowsMatchAuthoring": text_projection_diff_rows == 0,
        "attributionProjectionRowsMatchAuthoring": attribution_projection_diff_rows == 0,
        "referenceProjectionHashMatchesAuthoring": serving_reference_hash == authoring_reference_hash,
        "textProjectionHashMatchesAuthoring": serving_text_hash == authoring_text_hash,
        "attributionProjectionHashMatchesAuthoring": serving_attribution_hash == authoring_attribution_hash,
        "corpusProjectionHashMatchesAuthoring": serving_corpus_projection_hash == authoring_corpus_projection_hash,
        "annotationProjectionHashMatchesAuthoring": serving_annotation_projection_hash == authoring_annotation_projection_hash,
    }

    report = {
        "schemaVersion": "1.0",
        "milestone": "WB-2",
        "compilerVersion": COMPILER_VERSION,
        "gitCommitSha": args.git_commit_sha.lower(),
        "sourceFoundationBuildId": foundation["buildId"],
        "wb1AggregatePartitionHash": wb1.get("aggregatePartitionHash"),
        "researchBuildId": build_id,
        "researchReleaseId": release_id,
        "releaseLabel": release_label,
        "manifest": manifest,
        "manifestHash": manifest_hash,
        "projectionHashes": {
            "algorithm": "SHA256",
            "serialization": "WB2_PSQL_TSV_ROW_MULTISET_V2",
            "authoringCorpus": authoring_corpus_projection_hash,
            "servingCorpus": serving_corpus_projection_hash,
            "authoringAnnotationLayer": authoring_annotation_projection_hash,
            "servingAnnotationLayer": serving_annotation_projection_hash,
            "sections": {
                "referenceIndex": {
                    "authoring": authoring_reference_hash,
                    "serving": serving_reference_hash,
                    "symmetricDifferenceRows": reference_projection_diff_rows,
                },
                "textSegments": {
                    "authoring": authoring_text_hash,
                    "serving": serving_text_hash,
                    "symmetricDifferenceRows": text_projection_diff_rows,
                },
                "attribution": {
                    "authoring": authoring_attribution_hash,
                    "serving": serving_attribution_hash,
                    "symmetricDifferenceRows": attribution_projection_diff_rows,
                },
            },
        },
        "sourceHashes": {
            "oshbCorpusSourceChecksum": oshb_source_checksum,
            "oshbAnnotationSourceHash": oshb_layer_hash,
        },
        "projectedSources": ["OSHB_MORPHHB"],
        "excludedSources": [
            {
                "sourceKey": "BHSA_2021",
                "reason": "PUBLIC_RIGHTS_REVIEW_REQUIRED",
                "publicServingDefault": source_rights["BHSA_2021"]["publicServingDefault"],
            },
            {
                "sourceKey": "ETCBC_BRIDGING_2021",
                "reason": "DENY_UNTIL_RIGHTS_REVIEW",
                "publicServingDefault": source_rights["ETCBC_BRIDGING_2021"]["publicServingDefault"],
            },
        ],
        "rights": {
            "policyId": rights_policy_id,
            "storageSnapshotId": storage_snapshot_id,
            "displaySnapshotId": display_snapshot_id,
            "storageDecision": rights_rows.get("STORE_EXTRACTED_TEXT"),
            "displayDecision": rights_rows.get("DISPLAY_FULLTEXT"),
            "displayObligation": {"obligationType": "ATTRIBUTION", "value": ATTRIBUTION_TEXT},
        },
        "counts": {
            "configuredBooks": expected_books,
            "authoringOshbNodes": authoring_oshb_nodes,
            "authoringOshbSegments": authoring_oshb_segments,
            "servingCorpusNodes": serving_nodes,
            "servingTextSegments": serving_segments,
            "servingNodeSegmentMemberships": serving_node_segments,
            "passageReferenceIndexRows": reference_index,
            "passageReferenceIndexBooks": reference_books,
            "bhsaNodeLeaks": bhsa_node_leaks,
            "bridgingFeatureLeaks": bridge_feature_leaks,
            "nonOshbServingSegments": non_oshb_segments,
            "releaseComponents": release_components,
            "publishedEventsBeforeActivation": published_events,
        },
        "checks": checks,
        "pass": all(checks.values()),
    }

    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(
        json.dumps(report, ensure_ascii=False, sort_keys=True, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(
        {
            "milestone": report["milestone"],
            "researchReleaseId": release_id,
            "counts": report["counts"],
            "rights": report["rights"],
            "pass": report["pass"],
        },
        ensure_ascii=False,
        sort_keys=True,
    ))
    return 0 if report["pass"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
