\set ON_ERROR_STOP on

BEGIN;

CREATE SCHEMA rl1_test;

CREATE OR REPLACE FUNCTION rl1_test.assert_true(condition boolean, message text)
RETURNS void
LANGUAGE plpgsql
AS $rl1_assert$
BEGIN
  IF condition IS DISTINCT FROM true THEN
    RAISE EXCEPTION 'RL-1 assertion failed: %', message;
  END IF;
END
$rl1_assert$;

GRANT USAGE ON SCHEMA rl1_test TO anon, authenticated;
GRANT EXECUTE ON FUNCTION rl1_test.assert_true(boolean,text) TO anon, authenticated;

-- Both controlled releases were first published by the existing spike path.
SELECT rl1_test.assert_true(
  serving.release_was_published('47000000-0000-4000-8000-000000000001'),
  'release 1 must retain permanent ever-published state'
);
SELECT rl1_test.assert_true(
  serving.release_lifecycle_state('47000000-0000-4000-8000-000000000002') = 'PUBLISHED',
  'release 2 must begin RL-1 in PUBLISHED state'
);
SELECT rl1_test.assert_true(
  (SELECT event_sequence FROM serving.research_release_events
   WHERE research_release_id='47000000-0000-4000-8000-000000000002'
     AND event_type='PUBLISHED') = 1,
  'initial publication must be event_sequence=1'
);

-- Equal effective timestamps are explicitly legal; event_sequence is the total
-- order. SUPERSEDED remains pinned/publicly servable historical scholarship.
SELECT publication_control.transition_release_lifecycle(
  '47000000-0000-4000-8000-000000000002',
  'SUPERSEDED',
  (SELECT effective_at FROM serving.research_release_events
   WHERE research_release_id='47000000-0000-4000-8000-000000000002'
     AND event_sequence=1),
  'RL-1 equal-time supersession test',
  NULL
);

SELECT rl1_test.assert_true(
  serving.release_lifecycle_state('47000000-0000-4000-8000-000000000002') = 'SUPERSEDED',
  'SUPERSEDED must become the latest lifecycle state'
);
SELECT rl1_test.assert_true(
  serving.release_is_publicly_servable('47000000-0000-4000-8000-000000000002'),
  'SUPERSEDED historical pinned release must remain publicly servable'
);
SELECT rl1_test.assert_true(
  (SELECT max(event_sequence) FROM serving.research_release_events
   WHERE research_release_id='47000000-0000-4000-8000-000000000002') = 2,
  'equal-time SUPERSEDED event must receive sequence 2'
);

-- Effective time may not move backwards.
DO $rl1_backward_time$
DECLARE failed boolean := false;
BEGIN
  BEGIN
    PERFORM publication_control.transition_release_lifecycle(
      '47000000-0000-4000-8000-000000000002',
      'REVOKED',
      (SELECT effective_at - interval '1 second'
       FROM serving.research_release_events
       WHERE research_release_id='47000000-0000-4000-8000-000000000002'
         AND event_sequence=2),
      'must fail because chronology moves backwards',
      NULL
    );
  EXCEPTION WHEN raise_exception THEN
    failed := true;
  END;
  IF NOT failed THEN
    RAISE EXCEPTION 'backwards lifecycle effective_at must fail closed';
  END IF;
END
$rl1_backward_time$;

-- Sequence gaps are never inferred from UUID or timestamp ordering.
DO $rl1_sequence_gap$
DECLARE failed boolean := false;
BEGIN
  BEGIN
    INSERT INTO serving.research_release_events(
      research_release_event_id,research_release_id,event_type,effective_at,
      reason,event_sequence,changed_by
    ) VALUES (
      '47990000-0000-4000-8000-000000000004',
      '47000000-0000-4000-8000-000000000002',
      'REVOKED',
      (SELECT effective_at FROM serving.research_release_events
       WHERE research_release_id='47000000-0000-4000-8000-000000000002'
         AND event_sequence=2),
      'must fail because sequence 3 was skipped',
      4,
      NULL
    );
  EXCEPTION WHEN raise_exception THEN
    failed := true;
  END;
  IF NOT failed THEN
    RAISE EXCEPTION 'non-contiguous lifecycle event_sequence must fail';
  END IF;
END
$rl1_sequence_gap$;

-- REACTIVATED is valid only after REVOKED.
DO $rl1_invalid_reactivation$
DECLARE failed boolean := false;
BEGIN
  BEGIN
    PERFORM publication_control.transition_release_lifecycle(
      '47000000-0000-4000-8000-000000000002',
      'REACTIVATED',
      (SELECT effective_at FROM serving.research_release_events
       WHERE research_release_id='47000000-0000-4000-8000-000000000002'
         AND event_sequence=2),
      'must fail from SUPERSEDED',
      NULL
    );
  EXCEPTION WHEN raise_exception THEN
    failed := true;
  END;
  IF NOT failed THEN
    RAISE EXCEPTION 'SUPERSEDED -> REACTIVATED must fail';
  END IF;
END
$rl1_invalid_reactivation$;

-- Valid revoke at the same effective timestamp is sequence 3.
SELECT publication_control.transition_release_lifecycle(
  '47000000-0000-4000-8000-000000000002',
  'REVOKED',
  (SELECT effective_at FROM serving.research_release_events
   WHERE research_release_id='47000000-0000-4000-8000-000000000002'
     AND event_sequence=2),
  'RL-1 revoke test',
  NULL
);

SELECT rl1_test.assert_true(
  serving.release_lifecycle_state('47000000-0000-4000-8000-000000000002') = 'REVOKED',
  'release 2 must enter REVOKED state'
);
SELECT rl1_test.assert_true(
  serving.release_was_published('47000000-0000-4000-8000-000000000002'),
  'REVOKED release must remain permanently ever-published'
);
SELECT rl1_test.assert_true(
  NOT serving.release_is_publicly_servable('47000000-0000-4000-8000-000000000002'),
  'REVOKED release must not be publicly servable'
);

SET ROLE anon;
SELECT rl1_test.assert_true(
  (SELECT count(*) FROM serving.research_releases
   WHERE research_release_id='47000000-0000-4000-8000-000000000002') = 0,
  'anon must not see revoked ResearchRelease'
);
SELECT rl1_test.assert_true(
  (SELECT count(*) FROM serving.research_release_components
   WHERE research_release_id='47000000-0000-4000-8000-000000000002') = 0,
  'anon must not see revoked release components'
);
SELECT rl1_test.assert_true(
  serving.read_passage_core(
    '47000000-0000-4000-8000-000000000002','MT_TEST','1 Sam 16:7'
  ) IS NULL,
  'pinned passage serving must fail closed for revoked release'
);
RESET ROLE;

SET ROLE authenticated;
SELECT rl1_test.assert_true(
  (SELECT count(*) FROM serving.research_releases
   WHERE research_release_id='47000000-0000-4000-8000-000000000002') = 0,
  'authenticated must not see revoked ResearchRelease'
);
SELECT rl1_test.assert_true(
  serving.read_passage_core(
    '47000000-0000-4000-8000-000000000002','MT_TEST','1 Sam 16:7'
  ) IS NULL,
  'authenticated pinned passage serving must fail closed for revoked release'
);
RESET ROLE;

-- Revocation never restores mutability.
DO $rl1_revoked_immutable$
DECLARE failed boolean := false;
BEGIN
  BEGIN
    INSERT INTO serving.published_evidence_packets(
      published_evidence_packet_id,research_release_id,packet_type
    ) VALUES (
      '50100000-0000-4000-8000-000000000099',
      '47000000-0000-4000-8000-000000000002',
      'MUST_FAIL_AFTER_REVOKE'
    );
  EXCEPTION WHEN raise_exception THEN
    failed := true;
  END;
  IF NOT failed THEN
    RAISE EXCEPTION 'revoked release became mutable';
  END IF;
END
$rl1_revoked_immutable$;

-- Every release-pinned Serving payload surface stays immutable after first
-- publication, not only corpus_nodes/features/edges.
DO $rl1_reference_label_immutable$
DECLARE failed boolean := false;
BEGIN
  BEGIN
    UPDATE serving.reference_labels
    SET label=label
    WHERE (corpus_release_id,reference_label_id)=(
      SELECT corpus_release_id,reference_label_id
      FROM serving.reference_labels
      LIMIT 1
    );
  EXCEPTION WHEN raise_exception THEN failed := true;
  END;
  IF NOT failed THEN RAISE EXCEPTION 'published reference label became mutable'; END IF;
END
$rl1_reference_label_immutable$;

DO $rl1_text_segment_immutable$
DECLARE failed boolean := false;
BEGIN
  BEGIN
    UPDATE serving.corpus_text_segments
    SET surface_original=surface_original
    WHERE (corpus_release_id,text_segment_id)=(
      SELECT corpus_release_id,text_segment_id
      FROM serving.corpus_text_segments
      LIMIT 1
    );
  EXCEPTION WHEN raise_exception THEN failed := true;
  END;
  IF NOT failed THEN RAISE EXCEPTION 'published corpus text segment became mutable'; END IF;
END
$rl1_text_segment_immutable$;

DO $rl1_node_segment_immutable$
DECLARE failed boolean := false;
BEGIN
  BEGIN
    UPDATE serving.corpus_node_segments
    SET member_order=member_order
    WHERE (corpus_release_id,analysis_node_id,text_segment_id,membership_role)=(
      SELECT corpus_release_id,analysis_node_id,text_segment_id,membership_role
      FROM serving.corpus_node_segments
      LIMIT 1
    );
  EXCEPTION WHEN raise_exception THEN failed := true;
  END;
  IF NOT failed THEN RAISE EXCEPTION 'published corpus node/segment membership became mutable'; END IF;
END
$rl1_node_segment_immutable$;

-- Serving identity rows used by published payloads are append-only from
-- materialization. RightsDecisionSnapshot hardening remains a separate rights
-- work package because the pre-RL-1 spike intentionally creates/removes
-- candidate snapshots while exercising fail-closed publication.
DO $rl1_global_serving_identity_immutable$
DECLARE
  failed_object boolean := false;
  failed_span boolean := false;
  failed_system boolean := false;
BEGIN
  BEGIN
    UPDATE serving.research_objects SET object_type=object_type
    WHERE research_object_id=(SELECT research_object_id FROM serving.research_objects LIMIT 1);
  EXCEPTION WHEN raise_exception THEN failed_object := true;
  END;

  BEGIN
    UPDATE serving.reference_spans SET span_kind=span_kind
    WHERE reference_span_id=(SELECT reference_span_id FROM serving.reference_spans LIMIT 1);
  EXCEPTION WHEN raise_exception THEN failed_span := true;
  END;

  BEGIN
    UPDATE serving.reference_systems SET name=name
    WHERE reference_system_id=(SELECT reference_system_id FROM serving.reference_systems LIMIT 1);
  EXCEPTION WHEN raise_exception THEN failed_system := true;
  END;

  IF NOT (failed_object AND failed_span AND failed_system) THEN
    RAISE EXCEPTION
      'Serving identity immutability gap object=% span=% system=%',
      failed_object,failed_span,failed_system;
  END IF;
END
$rl1_global_serving_identity_immutable$;

-- Mutation guards must inspect both OLD and NEW ownership. Otherwise a
-- privileged writer could move an ever-published row to an unpublished
-- release/component and mutate it in the same UPDATE.
INSERT INTO serving.research_releases(
  research_release_id,release_label,source_build_id,published_at,
  manifest_schema_version,manifest_hash,manifest_hash_algorithm,
  manifest_canonical_serialization,git_commit_sha,compiler_version
) VALUES (
  '47000000-0000-4000-8000-000000000003',
  'rl1-unpublished-reparent-target',
  '46000000-0000-4000-8000-000000000002',
  now(),'1.1',
  '3434343434343434343434343434343434343434343434343434343434343434',
  'SHA256','RFC8785_JSON_CANONICALIZATION_SCHEME',
  'rl1-reparent-test','rl1-test'
);

INSERT INTO serving.research_objects(
  research_object_id,object_type,source_content_hash,published_at
) VALUES (
  '53000000-0000-4000-8000-000000000001',
  'CORPUS_RELEASE','rl1-unpublished-component',now()
);

INSERT INTO serving.published_evidence_packets(
  published_evidence_packet_id,research_release_id,packet_type
) VALUES (
  '50100000-0000-4000-8000-000000000003',
  '47000000-0000-4000-8000-000000000003',
  'RL1_UNPUBLISHED_PACKET'
);

INSERT INTO serving.published_evidence_items(
  published_evidence_item_id,published_evidence_packet_id,research_object_id,
  research_object_version,evidence_content_hash,evidence_class,citation_locator,
  permitted_excerpt,rights_decision_snapshot_id,evidence_stability_class,sort_order
) VALUES (
  '50200000-0000-4000-8000-000000000003',
  '50100000-0000-4000-8000-000000000003',
  '51000000-0000-4000-8000-000000000001',
  NULL,NULL,'SCHOLARLY_SOURCE_TEXT',NULL,NULL,NULL,'METADATA_ONLY',0
);

INSERT INTO serving.published_assertions(
  published_assertion_id,research_release_id,assertion_text,assertion_type,
  confidence_class,assertion_hash
) VALUES (
  '50300000-0000-4000-8000-000000000003',
  '47000000-0000-4000-8000-000000000003',
  'RL-1 unpublished assertion','TRANSLATION',NULL,
  '4545454545454545454545454545454545454545454545454545454545454545'
);

INSERT INTO serving.published_assertion_evidence(
  published_assertion_id,published_evidence_item_id,stance,
  entailment_review_status,weight_metadata
) VALUES (
  '50300000-0000-4000-8000-000000000003',
  '50200000-0000-4000-8000-000000000003',
  'SUPPORTS','UNREVIEWED',NULL
);

DO $rl1_direct_release_reparent$
DECLARE failed boolean := false;
BEGIN
  BEGIN
    UPDATE serving.published_passage_analyses
    SET research_release_id='47000000-0000-4000-8000-000000000003'
    WHERE published_analysis_id='50000000-0000-4000-8000-000000000001';
  EXCEPTION WHEN raise_exception THEN failed := true;
  END;
  IF NOT failed THEN
    RAISE EXCEPTION 'ever-published direct payload escaped immutability by reparenting';
  END IF;
END
$rl1_direct_release_reparent$;

DO $rl1_component_reparent$
DECLARE failed boolean := false;
BEGIN
  BEGIN
    UPDATE serving.reference_labels
    SET corpus_release_id='53000000-0000-4000-8000-000000000001'
    WHERE (corpus_release_id,reference_label_id)=(
      SELECT corpus_release_id,reference_label_id
      FROM serving.reference_labels
      WHERE corpus_release_id='30000000-0000-4000-8000-000000000001'
      LIMIT 1
    );
  EXCEPTION WHEN raise_exception THEN failed := true;
  END;
  IF NOT failed THEN
    RAISE EXCEPTION 'ever-published component projection escaped immutability by reparenting';
  END IF;
END
$rl1_component_reparent$;

DO $rl1_evidence_item_reparent$
DECLARE failed boolean := false;
BEGIN
  BEGIN
    UPDATE serving.published_evidence_items
    SET published_evidence_packet_id='50100000-0000-4000-8000-000000000003'
    WHERE published_evidence_item_id='50200000-0000-4000-8000-000000000001';
  EXCEPTION WHEN raise_exception THEN failed := true;
  END;
  IF NOT failed THEN
    RAISE EXCEPTION 'ever-published evidence item escaped immutability by reparenting';
  END IF;
END
$rl1_evidence_item_reparent$;

DO $rl1_assertion_evidence_reparent$
DECLARE failed boolean := false;
BEGIN
  BEGIN
    UPDATE serving.published_assertion_evidence
    SET published_assertion_id='50300000-0000-4000-8000-000000000003',
        published_evidence_item_id='50200000-0000-4000-8000-000000000003'
    WHERE published_assertion_id='50300000-0000-4000-8000-000000000001'
      AND published_evidence_item_id='50200000-0000-4000-8000-000000000001';
  EXCEPTION WHEN raise_exception THEN failed := true;
  END;
  IF NOT failed THEN
    RAISE EXCEPTION 'ever-published assertion/evidence link escaped immutability by reparenting';
  END IF;
END
$rl1_assertion_evidence_reparent$;

SELECT rl1_test.assert_true(
  (SELECT research_release_id
   FROM serving.published_passage_analyses
   WHERE published_analysis_id='50000000-0000-4000-8000-000000000001')
    = '47000000-0000-4000-8000-000000000001',
  'failed reparenting attempt must preserve direct payload ownership'
);
SELECT rl1_test.assert_true(
  (SELECT corpus_release_id
   FROM serving.reference_labels
   WHERE reference_label_id=(
     SELECT reference_label_id
     FROM serving.reference_labels
     WHERE corpus_release_id='30000000-0000-4000-8000-000000000001'
     LIMIT 1
   ))
    = '30000000-0000-4000-8000-000000000001',
  'failed reparenting attempt must preserve component ownership'
);

-- Neither direct pointer mutation nor publish-to-channel may expose a revoked release.
DO $rl1_revoked_pointer$
DECLARE failed boolean := false;
BEGIN
  BEGIN
    UPDATE serving.release_channel_pointers
    SET research_release_id='47000000-0000-4000-8000-000000000002'
    WHERE release_channel_id='47200000-0000-4000-8000-000000000001';
  EXCEPTION WHEN raise_exception THEN
    failed := true;
  END;
  IF NOT failed THEN
    RAISE EXCEPTION 'channel pointer accepted revoked release';
  END IF;
END
$rl1_revoked_pointer$;

DO $rl1_publish_revoked$
DECLARE failed boolean := false;
BEGIN
  BEGIN
    PERFORM publication_control.publish_release_to_channel(
      'PRODUCTION','47000000-0000-4000-8000-000000000002',NULL,false
    );
  EXCEPTION WHEN raise_exception THEN
    failed := true;
  END;
  IF NOT failed THEN
    RAISE EXCEPTION 'publish_release_to_channel implicitly reactivated revoked release';
  END IF;
END
$rl1_publish_revoked$;

-- Valid reactivation restores servability but does not silently restore a channel.
SELECT publication_control.transition_release_lifecycle(
  '47000000-0000-4000-8000-000000000002',
  'REACTIVATED',
  (SELECT effective_at FROM serving.research_release_events
   WHERE research_release_id='47000000-0000-4000-8000-000000000002'
     AND event_sequence=3),
  'RL-1 explicit reactivation test',
  NULL
);

SELECT rl1_test.assert_true(
  serving.release_lifecycle_state('47000000-0000-4000-8000-000000000002') = 'REACTIVATED',
  'release 2 must enter REACTIVATED state'
);
SELECT rl1_test.assert_true(
  serving.release_is_publicly_servable('47000000-0000-4000-8000-000000000002'),
  'REACTIVATED release must become publicly servable'
);
SELECT rl1_test.assert_true(
  (SELECT count(*) FROM serving.research_release_events
   WHERE research_release_id='47000000-0000-4000-8000-000000000002'
     AND event_type='PUBLISHED') = 1,
  'reactivation must not append a second PUBLISHED event'
);

SELECT publication_control.publish_release_to_channel(
  'PRODUCTION','47000000-0000-4000-8000-000000000002',NULL,false
);
SELECT rl1_test.assert_true(
  (SELECT research_release_id FROM serving.release_channel_pointers
   WHERE release_channel_id='47200000-0000-4000-8000-000000000001')
   = '47000000-0000-4000-8000-000000000002',
  'explicitly reactivated release may receive the channel pointer'
);

-- A superseded release remains citation-stable/public, while rollback itself is
-- only a pointer move and does not append lifecycle events to either release.
SELECT publication_control.transition_release_lifecycle(
  '47000000-0000-4000-8000-000000000002',
  'SUPERSEDED',
  (SELECT effective_at FROM serving.research_release_events
   WHERE research_release_id='47000000-0000-4000-8000-000000000002'
     AND event_sequence=4),
  'RL-1 superseded historical release test',
  NULL
);
SELECT rl1_test.assert_true(
  serving.release_is_publicly_servable('47000000-0000-4000-8000-000000000002'),
  'SUPERSEDED release must remain pinned-publicly servable'
);

SELECT publication_control.publish_release_to_channel(
  'PRODUCTION','47000000-0000-4000-8000-000000000001',NULL,false
);
SELECT rl1_test.assert_true(
  (SELECT max(event_sequence) FROM serving.research_release_events
   WHERE research_release_id='47000000-0000-4000-8000-000000000002') = 5,
  'rollback pointer move must not mutate superseded release lifecycle'
);
SELECT rl1_test.assert_true(
  (SELECT count(*) FROM serving.research_release_events
   WHERE research_release_id='47000000-0000-4000-8000-000000000001') = 1,
  'rollback pointer move must not mutate destination release lifecycle'
);

-- Revoking the currently pointed release atomically removes the channel pointer.
SELECT publication_control.transition_release_lifecycle(
  '47000000-0000-4000-8000-000000000001',
  'REVOKED',
  now(),
  'RL-1 revoke active production release test',
  NULL
);
SELECT rl1_test.assert_true(
  (SELECT count(*) FROM serving.release_channel_pointers
   WHERE research_release_id='47000000-0000-4000-8000-000000000001') = 0,
  'revocation must remove channel pointers to revoked release'
);

SET ROLE anon;
SELECT rl1_test.assert_true(
  (SELECT count(*) FROM serving.current_release WHERE channel_key='PRODUCTION') = 0,
  'current_release must not expose a revoked production target'
);
SELECT rl1_test.assert_true(
  serving.read_passage_core(
    '47000000-0000-4000-8000-000000000001','MT_TEST','1 Sam 16:7'
  ) IS NULL,
  'revoked release pinned passage must not remain public'
);
RESET ROLE;

DO $rl1_release1_immutable$
DECLARE failed boolean := false;
BEGIN
  BEGIN
    UPDATE serving.published_passage_analyses
    SET rendered_payload='{"revokedMutation":true}'
    WHERE published_analysis_id='50000000-0000-4000-8000-000000000001';
  EXCEPTION WHEN raise_exception THEN
    failed := true;
  END;
  IF NOT failed THEN
    RAISE EXCEPTION 'revoked release analysis became mutable';
  END IF;
END
$rl1_release1_immutable$;

-- Reactivation restores servability only after the explicit event and a new
-- pointer move; it does not create another publication identity.
SELECT publication_control.transition_release_lifecycle(
  '47000000-0000-4000-8000-000000000001',
  'REACTIVATED',
  now(),
  'RL-1 restore production release for downstream spike checks',
  NULL
);
SELECT publication_control.publish_release_to_channel(
  'PRODUCTION','47000000-0000-4000-8000-000000000001',NULL,false
);

SELECT rl1_test.assert_true(
  (SELECT research_release_id FROM serving.current_release
   WHERE channel_key='PRODUCTION')
   = '47000000-0000-4000-8000-000000000001',
  'explicitly reactivated release must be restorable to production'
);
SELECT rl1_test.assert_true(
  (SELECT count(*) FROM serving.research_release_events
   WHERE research_release_id='47000000-0000-4000-8000-000000000001'
     AND event_type='PUBLISHED') = 1,
  'reactivated release must retain exactly one original PUBLISHED event'
);
SELECT rl1_test.assert_true(
  (SELECT array_agg(event_type ORDER BY event_sequence)
   FROM serving.research_release_events
   WHERE research_release_id='47000000-0000-4000-8000-000000000001')
  = ARRAY['PUBLISHED','REVOKED','REACTIVATED']::text[],
  'release 1 lifecycle ordering must be deterministic'
);

DROP SCHEMA rl1_test CASCADE;

COMMIT;
