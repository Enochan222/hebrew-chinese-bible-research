\set ON_ERROR_STOP on

BEGIN;

-- Candidate release combines the existing synthetic Hebrew corpus with one
-- synthetic Chinese DigitalExpression. No real copyrighted translation data.
INSERT INTO authoring.research_builds(
  research_build_id,build_version,status,started_at,completed_at,compiler_version,git_commit_sha
) VALUES (
  '46000000-0000-4000-8000-000000000003','wb4-db1-synthetic','COMPLETED',
  now(),now(),'wb4-db1-test','fixture'
);

INSERT INTO serving.research_objects(
  research_object_id,object_type,source_content_hash,published_at
) VALUES (
  '22000000-0000-4000-8000-000000000002',
  'DIGITAL_EXPRESSION',
  '9999999999999999999999999999999999999999999999999999999999999999',
  now()
);

INSERT INTO serving.research_releases(
  research_release_id,release_label,source_build_id,published_at,
  manifest_schema_version,manifest_hash,manifest_hash_algorithm,
  manifest_canonical_serialization,git_commit_sha,compiler_version
) VALUES (
  '47000000-0000-4000-8000-000000000003',
  'wb4-db1-synthetic-release',
  '46000000-0000-4000-8000-000000000003',
  now(),'1.1',
  '9191919191919191919191919191919191919191919191919191919191919191',
  'SHA256','RFC8785_JSON_CANONICALIZATION_SCHEME','fixture','wb4-db1-test'
);

INSERT INTO serving.research_release_components(
  research_release_id,component_kind,component_research_object_id,
  component_version,content_hash,component_order
) VALUES
(
  '47000000-0000-4000-8000-000000000003',
  'CORPUS',
  '30000000-0000-4000-8000-000000000001',
  '1','corpus-fixture',0
),
(
  '47000000-0000-4000-8000-000000000003',
  'TRANSLATION_WITNESS',
  '22000000-0000-4000-8000-000000000002',
  'fixture-v1',
  '9999999999999999999999999999999999999999999999999999999999999999',
  1
);

-- Exact rights snapshots for display and persisted storage.
INSERT INTO serving.rights_decision_snapshots(
  rights_decision_snapshot_id,subject_type,subject_identifier,operation,purpose_scope,
  audience_scope,commercial_context,applicable_rule_ids,winning_rule_ids,decision,
  decision_basis,conditions_json,obligations_json,resolver_version,evaluated_at,decision_hash
) VALUES
(
  '45200000-0000-4000-8000-000000000010',
  'DIGITAL_EXPRESSION','22000000-0000-4000-8000-000000000002',
  'DISPLAY_FULLTEXT','PUBLIC_DISPLAY','PUBLIC','MIXED',
  ARRAY['45100000-0000-4000-8000-000000000010'::uuid],
  ARRAY['45100000-0000-4000-8000-000000000010'::uuid],
  'ALLOW','RULE',NULL,'[]'::jsonb,'wb4-db1-test',now(),
  'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa1'
),
(
  '45200000-0000-4000-8000-000000000011',
  'PROVIDER_DISTRIBUTION','41414141-4141-4414-8414-414141414141',
  'STORE_EXTRACTED_TEXT','PUBLICATION','INTERNAL_SERVICE','MIXED',
  ARRAY['45100000-0000-4000-8000-000000000011'::uuid],
  ARRAY['45100000-0000-4000-8000-000000000011'::uuid],
  'ALLOW','RULE',NULL,'[]'::jsonb,'wb4-db1-test',now(),
  'bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb1'
),
(
  '45200000-0000-4000-8000-000000000012',
  'DIGITAL_EXPRESSION','22000000-0000-4000-8000-000000000001',
  'DISPLAY_FULLTEXT','PUBLIC_DISPLAY','PUBLIC','MIXED',
  ARRAY['45100000-0000-4000-8000-000000000012'::uuid],
  ARRAY['45100000-0000-4000-8000-000000000012'::uuid],
  'ALLOW','RULE',NULL,'[]'::jsonb,'wb4-db1-test',now(),
  'ccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc1'
),
(
  '45200000-0000-4000-8000-000000000013',
  'PROVIDER_DISTRIBUTION','41414141-4141-4414-8414-414141414141',
  'STORE_EXTRACTED_TEXT','PUBLICATION','PUBLIC','MIXED',
  ARRAY['45100000-0000-4000-8000-000000000013'::uuid],
  ARRAY['45100000-0000-4000-8000-000000000013'::uuid],
  'ALLOW','RULE',NULL,'[]'::jsonb,'wb4-db1-test',now(),
  'ddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddd1'
);

-- Provider availability/storage semantics fail closed independently of rights.
DO $invalid_live_persisted_binding$
DECLARE failed boolean := false;
BEGIN
  BEGIN
    INSERT INTO authoring.provider_witness_observations(
      provider_distribution_id,reference_span_id,text_stream_id,binding_mode,segment_storage_mode,
      provider_reference,provider_segment_key,provider_version,observed_hash,observed_at,
      snapshot_content_hash,delivery_status
    ) VALUES (
      '41414141-4141-4414-8414-414141414141',
      '13000000-0000-4000-8000-000000000002',
      '23000000-0000-4000-8000-000000000003',
      'LIVE_EXTERNAL','PERSISTED_CONTENT',
      '1Sam.16.8','invalid-live-persisted','fixture-v1',
      '8989898989898989898989898989898989898989898989898989898989898989',
      '2026-10-03T00:00:00Z',
      '9090909090909090909090909090909090909090909090909090909090909090',
      'READY'
    );
  EXCEPTION WHEN check_violation THEN failed := true;
  END;
  IF NOT failed THEN
    RAISE EXCEPTION 'LIVE_EXTERNAL observation masqueraded as persisted snapshot';
  END IF;
END
$invalid_live_persisted_binding$;

-- Missing rights snapshots must fail closed, not degrade to displayable text.
DO $missing_display_rights$
DECLARE failed boolean := false;
BEGIN
  BEGIN
    PERFORM publication_control.materialize_translation_witness_candidate(
      '47000000-0000-4000-8000-000000000003',
      '13000000-0000-4000-8000-000000000001',
      '41414141-4141-4414-8414-414141414141',
      '45200000-0000-4000-8000-000000009999',
      '45200000-0000-4000-8000-000000000011',
      'Synthetic Chinese Test Witness','zh-Hant','Synthetic fixture only',
      '40404040-4040-4040-8040-404040404040',0
    );
  EXCEPTION WHEN raise_exception THEN failed := true;
  END;
  IF NOT failed THEN RAISE EXCEPTION 'missing display RightsDecisionSnapshot was accepted'; END IF;
END
$missing_display_rights$;

DO $missing_storage_rights$
DECLARE failed boolean := false;
BEGIN
  BEGIN
    PERFORM publication_control.materialize_translation_witness_candidate(
      '47000000-0000-4000-8000-000000000003',
      '13000000-0000-4000-8000-000000000001',
      '41414141-4141-4414-8414-414141414141',
      '45200000-0000-4000-8000-000000000010',
      '45200000-0000-4000-8000-000000009999',
      'Synthetic Chinese Test Witness','zh-Hant','Synthetic fixture only',
      '40404040-4040-4040-8040-404040404040',0
    );
  EXCEPTION WHEN raise_exception THEN failed := true;
  END;
  IF NOT failed THEN RAISE EXCEPTION 'missing storage RightsDecisionSnapshot was accepted'; END IF;
END
$missing_storage_rights$;

-- Stale provider delivery remains independent from otherwise-valid rights and
-- must compile metadata only with zero translation text.
UPDATE authoring.provider_witness_observations
SET delivery_status='STALE'
WHERE provider_distribution_id='41414141-4141-4414-8414-414141414141'
  AND reference_span_id='13000000-0000-4000-8000-000000000001';

SELECT publication_control.materialize_translation_witness_candidate(
  '47000000-0000-4000-8000-000000000003',
  '13000000-0000-4000-8000-000000000001',
  '41414141-4141-4414-8414-414141414141',
  '45200000-0000-4000-8000-000000000010',
  '45200000-0000-4000-8000-000000000011',
  'Synthetic Chinese Test Witness','zh-Hant','Synthetic fixture only',
  '40404040-4040-4040-8040-404040404040',0
);

DO $stale_metadata_only$
BEGIN
  IF (SELECT display_status FROM serving.translation_witnesses
      WHERE research_release_id='47000000-0000-4000-8000-000000000003'
        AND reference_span_id='13000000-0000-4000-8000-000000000001')
     <> 'METADATA_ONLY' THEN
    RAISE EXCEPTION 'STALE delivery did not compile metadata-only';
  END IF;
  IF EXISTS (
    SELECT 1 FROM serving.translation_witness_segments
    WHERE research_release_id='47000000-0000-4000-8000-000000000003'
  ) THEN
    RAISE EXCEPTION 'STALE delivery exposed translation text segments';
  END IF;
END
$stale_metadata_only$;

DELETE FROM serving.translation_witnesses
WHERE research_release_id='47000000-0000-4000-8000-000000000003'
  AND reference_span_id='13000000-0000-4000-8000-000000000001';

UPDATE authoring.provider_witness_observations
SET delivery_status='READY'
WHERE provider_distribution_id='41414141-4141-4414-8414-414141414141'
  AND reference_span_id='13000000-0000-4000-8000-000000000001';

-- Wrong-expression display snapshot must fail closed.
DO $wrong_display_subject$
DECLARE failed boolean := false;
BEGIN
  BEGIN
    PERFORM publication_control.materialize_translation_witness_candidate(
      '47000000-0000-4000-8000-000000000003',
      '13000000-0000-4000-8000-000000000001',
      '41414141-4141-4414-8414-414141414141',
      '45200000-0000-4000-8000-000000000012',
      '45200000-0000-4000-8000-000000000011',
      'Synthetic Chinese Test Witness','zh-Hant','Synthetic fixture only',
      '40404040-4040-4040-8040-404040404040',0
    );
  EXCEPTION WHEN raise_exception THEN failed := true;
  END;
  IF NOT failed THEN RAISE EXCEPTION 'wrong DigitalExpression display rights were accepted'; END IF;
END
$wrong_display_subject$;

-- Wrong storage audience must also fail closed for persisted snapshots.
DO $wrong_storage_scope$
DECLARE failed boolean := false;
BEGIN
  BEGIN
    PERFORM publication_control.materialize_translation_witness_candidate(
      '47000000-0000-4000-8000-000000000003',
      '13000000-0000-4000-8000-000000000001',
      '41414141-4141-4414-8414-414141414141',
      '45200000-0000-4000-8000-000000000010',
      '45200000-0000-4000-8000-000000000013',
      'Synthetic Chinese Test Witness','zh-Hant','Synthetic fixture only',
      '40404040-4040-4040-8040-404040404040',0
    );
  EXCEPTION WHEN raise_exception THEN failed := true;
  END;
  IF NOT failed THEN RAISE EXCEPTION 'wrong storage audience was accepted'; END IF;
END
$wrong_storage_scope$;

SET ROLE publication_worker;
SELECT publication_control.materialize_translation_witness_candidate(
  '47000000-0000-4000-8000-000000000003',
  '13000000-0000-4000-8000-000000000001',
  '41414141-4141-4414-8414-414141414141',
  '45200000-0000-4000-8000-000000000010',
  '45200000-0000-4000-8000-000000000011',
  'Synthetic Chinese Test Witness','zh-Hant','Synthetic fixture only',
  '40404040-4040-4040-8040-404040404040',0
);
RESET ROLE;

DO $candidate_shape$
DECLARE w serving.translation_witnesses%ROWTYPE;
BEGIN
  SELECT * INTO w
  FROM serving.translation_witnesses
  WHERE research_release_id='47000000-0000-4000-8000-000000000003';

  IF w.display_status <> 'DISPLAYABLE'
     OR w.coverage_status <> 'COVERED'
     OR w.delivery_status <> 'READY'
     OR w.digital_expression_id <> '22000000-0000-4000-8000-000000000002'
     OR w.provider_distribution_id <> '41414141-4141-4414-8414-414141414141'
     OR w.display_rights_decision_snapshot_id <> '45200000-0000-4000-8000-000000000010'
     OR w.storage_rights_decision_snapshot_id <> '45200000-0000-4000-8000-000000000011' THEN
    RAISE EXCEPTION 'compiled translation witness metadata drift';
  END IF;

  IF (SELECT count(*) FROM serving.translation_witness_segments
      WHERE research_release_id='47000000-0000-4000-8000-000000000003') <> 2 THEN
    RAISE EXCEPTION 'displayable synthetic witness must compile exactly two persisted segments';
  END IF;

  IF EXISTS (
    SELECT 1
    FROM serving.translation_witness_segments s
    JOIN authoring.text_segments a USING (text_segment_id)
    WHERE s.research_release_id='47000000-0000-4000-8000-000000000003'
      AND (s.content_hash <> a.content_hash OR s.text_content <> a.surface_original)
  ) THEN
    RAISE EXCEPTION 'compiled translation segment text/hash differs from Authoring snapshot';
  END IF;
END
$candidate_shape$;

-- Existing OSHB-only release remains contract-compatible with zero witnesses.
SET ROLE anon;
DO $oshb_only_empty$
DECLARE payload jsonb;
BEGIN
  payload := serving.read_translation_witnesses(
    '47000000-0000-4000-8000-000000000001','MT_TEST','1 Sam 16:7'
  );
  IF payload IS NULL OR payload->'witnesses' <> '[]'::jsonb THEN
    RAISE EXCEPTION 'existing OSHB-only release must return an empty witness list';
  END IF;
END
$oshb_only_empty$;
RESET ROLE;

-- Inactive candidate is invisible through public RLS/RPC.
SET ROLE anon;
DO $inactive_hidden$
BEGIN
  IF EXISTS (
    SELECT 1 FROM serving.translation_witnesses
    WHERE research_release_id='47000000-0000-4000-8000-000000000003'
  ) THEN
    RAISE EXCEPTION 'inactive translation witness leaked through RLS';
  END IF;
  IF EXISTS (
    SELECT 1 FROM serving.translation_witness_segments
    WHERE research_release_id='47000000-0000-4000-8000-000000000003'
  ) THEN
    RAISE EXCEPTION 'inactive translation witness segments leaked through RLS';
  END IF;
  IF serving.read_translation_witnesses(
    '47000000-0000-4000-8000-000000000003','MT_TEST','1 Sam 16:7'
  ) IS NOT NULL THEN
    RAISE EXCEPTION 'inactive translation witness RPC leaked';
  END IF;
END
$inactive_hidden$;
RESET ROLE;

SELECT publication_control.publish_release_to_channel(
  'PRODUCTION','47000000-0000-4000-8000-000000000003',NULL,false
);

SET ROLE anon;
DO $published_payload$
DECLARE payload jsonb;
DECLARE witness jsonb;
BEGIN
  payload := serving.read_translation_witnesses(
    '47000000-0000-4000-8000-000000000003','MT_TEST','1 Sam 16:7'
  );
  IF payload IS NULL THEN RAISE EXCEPTION 'published witness list is null'; END IF;
  IF payload->>'schemaVersion' <> '1.1'
     OR payload->>'researchReleaseId' <> '47000000-0000-4000-8000-000000000003'
     OR payload->>'referenceSpanId' <> '13000000-0000-4000-8000-000000000001'
     OR payload#>>'{resolvedReference,referenceSystemCode}' <> 'MT_TEST'
     OR payload#>>'{resolvedReference,referenceLabel}' <> '1 Sam 16:7'
     OR jsonb_array_length(payload->'witnesses') <> 1 THEN
    RAISE EXCEPTION 'translation witness list top-level contract drift: %', payload;
  END IF;

  witness := payload->'witnesses'->0;
  IF witness->>'digitalExpressionId' <> '22000000-0000-4000-8000-000000000002'
     OR witness->>'displayStatus' <> 'DISPLAYABLE'
     OR witness#>>'{binding,bindingMode}' <> 'SNAPSHOT_PINNED'
     OR witness#>>'{binding,providerDistributionId}' <> '41414141-4141-4414-8414-414141414141'
     OR witness->>'rightsDecisionSnapshotId' <> '45200000-0000-4000-8000-000000000010'
     OR jsonb_array_length(witness->'segments') <> 2
     OR witness#>>'{segments,0,segmentOrder}' <> '0'
     OR witness#>>'{segments,1,segmentOrder}' <> '1' THEN
    RAISE EXCEPTION 'translation witness payload contract drift: %', witness;
  END IF;

  IF serving.read_current_translation_witnesses(
    'PRODUCTION','MT_TEST','1 Sam 16:7'
  ) IS NULL THEN
    RAISE EXCEPTION 'current-release translation witness RPC failed';
  END IF;
END
$published_payload$;

DO $public_authoring_isolation$
DECLARE failed boolean := false;
BEGIN
  BEGIN
    PERFORM count(*) FROM authoring.provider_distributions;
  EXCEPTION WHEN insufficient_privilege THEN failed := true;
  END;
  IF NOT failed THEN
    RAISE EXCEPTION 'anon unexpectedly read Authoring provider distribution table';
  END IF;
END
$public_authoring_isolation$;
RESET ROLE;

-- Published rows remain permanently immutable.
DO $published_immutable$
DECLARE failed_witness boolean := false;
DECLARE failed_segment boolean := false;
BEGIN
  BEGIN
    UPDATE serving.translation_witnesses
    SET display_name=display_name
    WHERE research_release_id='47000000-0000-4000-8000-000000000003';
  EXCEPTION WHEN raise_exception THEN failed_witness := true;
  END;
  BEGIN
    UPDATE serving.translation_witness_segments
    SET text_content=text_content
    WHERE research_release_id='47000000-0000-4000-8000-000000000003';
  EXCEPTION WHEN raise_exception THEN failed_segment := true;
  END;
  IF NOT failed_witness OR NOT failed_segment THEN
    RAISE EXCEPTION 'published translation Serving rows remained mutable';
  END IF;
END
$published_immutable$;

-- Revoked release becomes unreadable but never mutable.
SET ROLE publication_worker;
SELECT publication_control.transition_release_lifecycle(
  '47000000-0000-4000-8000-000000000003','REVOKED',now(),'WB-4 DB-1 revoke test',NULL
);
RESET ROLE;

SET ROLE anon;
DO $revoked_hidden$
BEGIN
  IF EXISTS (
    SELECT 1 FROM serving.translation_witnesses
    WHERE research_release_id='47000000-0000-4000-8000-000000000003'
  ) OR EXISTS (
    SELECT 1 FROM serving.translation_witness_segments
    WHERE research_release_id='47000000-0000-4000-8000-000000000003'
  ) THEN
    RAISE EXCEPTION 'revoked translation rows remained visible through public RLS';
  END IF;
  IF serving.read_translation_witnesses(
    '47000000-0000-4000-8000-000000000003','MT_TEST','1 Sam 16:7'
  ) IS NOT NULL THEN
    RAISE EXCEPTION 'revoked translation witness remained publicly readable';
  END IF;
END
$revoked_hidden$;
RESET ROLE;

DO $revoked_immutable$
DECLARE failed boolean := false;
BEGIN
  BEGIN
    DELETE FROM serving.translation_witness_segments
    WHERE research_release_id='47000000-0000-4000-8000-000000000003';
  EXCEPTION WHEN raise_exception THEN failed := true;
  END;
  IF NOT failed THEN RAISE EXCEPTION 'revoked translation witness segments became mutable'; END IF;
END
$revoked_immutable$;

-- Serving runtime functions/tables must not depend on Authoring.
DO $serving_no_authoring_dependency$
BEGIN
  IF EXISTS (
    SELECT 1
    FROM pg_depend d
    JOIN pg_proc p ON p.oid=d.objid
    JOIN pg_namespace pn ON pn.oid=p.pronamespace
    JOIN pg_class c ON c.oid=d.refobjid
    JOIN pg_namespace cn ON cn.oid=c.relnamespace
    WHERE pn.nspname='serving'
      AND p.proname IN ('read_translation_witnesses','read_current_translation_witnesses')
      AND cn.nspname='authoring'
  ) THEN
    RAISE EXCEPTION 'Serving translation RPC has an Authoring table dependency';
  END IF;
END
$serving_no_authoring_dependency$;

ROLLBACK;
