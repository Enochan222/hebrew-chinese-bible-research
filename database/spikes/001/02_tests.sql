\set ON_ERROR_STOP on

CREATE SCHEMA IF NOT EXISTS spike_test;

CREATE OR REPLACE FUNCTION spike_test.assert_true(ok boolean, message text)
RETURNS void
LANGUAGE plpgsql
AS $assert$
BEGIN
  IF NOT COALESCE(ok,false) THEN
    RAISE EXCEPTION 'ASSERTION FAILED: %', message;
  END IF;
END
$assert$;

GRANT USAGE ON SCHEMA spike_test TO authenticated, anon;
GRANT EXECUTE ON FUNCTION spike_test.assert_true(boolean,text) TO authenticated, anon;

-- Reference identity and alternate addressing.
SELECT spike_test.assert_true(
  (SELECT count(*) FROM authoring.reference_label_members
   WHERE reference_label_id='14000000-0000-4000-8000-000000000003') = 2,
  'alternate label must deterministically map to two ordered atoms'
);

-- Shared-PK subtype identity must match research_objects.object_type.
INSERT INTO authoring.research_objects(research_object_id,object_type)
VALUES ('30000000-0000-4000-8000-000000000099','RULE_VERSION');

DO $wrong_object_type$
DECLARE failed boolean := false;
BEGIN
  BEGIN
    INSERT INTO authoring.corpus_releases(
      corpus_release_id,digital_expression_id,release_name,release_version,importer_version
    ) VALUES (
      '30000000-0000-4000-8000-000000000099',
      '22000000-0000-4000-8000-000000000001',
      'invalid wrong object type','1','spike'
    );
  EXCEPTION WHEN raise_exception THEN failed := true;
  END;
  IF NOT failed THEN RAISE EXCEPTION 'wrong research_object subtype must fail'; END IF;
END
$wrong_object_type$;

DELETE FROM authoring.research_objects
WHERE research_object_id='30000000-0000-4000-8000-000000000099';

DO $$
DECLARE failed boolean := false;
BEGIN
  BEGIN
    INSERT INTO authoring.reference_spans(reference_span_id,book_id,start_atom_id,start_sequence,end_atom_id,end_sequence,span_kind)
    VALUES ('13000000-0000-4000-8000-000000000099','10000000-0000-4000-8000-000000000002',
      '12000000-0000-4000-8000-000000000003',3001,'12000000-0000-4000-8000-000000000002',3000,'INVALID');
  EXCEPTION WHEN check_violation THEN failed := true;
  END;
  IF NOT failed THEN RAISE EXCEPTION 'expected reversed reference span to fail'; END IF;
END $$;

-- Same-layer edge enforcement.
DO $$
DECLARE failed boolean := false;
BEGIN
  BEGIN
    INSERT INTO authoring.analysis_edges(analysis_edge_id,annotation_layer_id,from_node_id,to_node_id,relation_type,relation_ontology)
    VALUES ('33100000-0000-4000-8000-000000000099','32000000-0000-4000-8000-000000000001',
      '33000000-0000-4000-8000-000000000001','33000000-0000-4000-8000-000000000005','INVALID','SPIKE');
  EXCEPTION WHEN foreign_key_violation THEN failed := true;
  END;
  IF NOT failed THEN RAISE EXCEPTION 'cross-layer AnalysisEdge must fail'; END IF;
END $$;

-- Node/segment compatibility.
DO $$
DECLARE failed boolean := false;
BEGIN
  BEGIN
    INSERT INTO authoring.analysis_node_segments(analysis_node_id,text_segment_id,member_order)
    VALUES ('33000000-0000-4000-8000-000000000002','24000000-0000-4000-8000-000000000010',9);
  EXCEPTION WHEN raise_exception THEN failed := true;
  END;
  IF NOT failed THEN RAISE EXCEPTION 'cross-expression node/segment membership must fail'; END IF;
END $$;

-- WB-1: multi-atom AnalysisNode spans may contain verse-local TextSegments.
DO $node_segment_span_containment$
DECLARE invalid_failed boolean := false;
BEGIN
  INSERT INTO authoring.reference_atoms(reference_atom_id,book_id,sequence,atom_kind)
  VALUES ('12000000-0000-4000-8000-000000000098','10000000-0000-4000-8000-000000000001',16008,'VERSE');

  INSERT INTO authoring.reference_spans(
    reference_span_id,book_id,start_atom_id,start_sequence,end_atom_id,end_sequence,span_kind
  ) VALUES
  ('13000000-0000-4000-8000-000000000098','10000000-0000-4000-8000-000000000001',
   '12000000-0000-4000-8000-000000000098',16008,'12000000-0000-4000-8000-000000000098',16008,'VERSE'),
  ('13000000-0000-4000-8000-000000000097','10000000-0000-4000-8000-000000000001',
   '12000000-0000-4000-8000-000000000001',16007,'12000000-0000-4000-8000-000000000098',16008,'MULTI_ATOM_TEST');

  INSERT INTO authoring.text_segments(
    text_segment_id,text_stream_id,reference_span_id,segment_order,segment_storage_mode,surface_original,segment_kind
  ) VALUES (
    '24000000-0000-4000-8000-000000000098','23000000-0000-4000-8000-000000000001',
    '13000000-0000-4000-8000-000000000098',98,'PERSISTED_CONTENT','בדיקה','WORD'
  );

  INSERT INTO authoring.analysis_nodes(
    analysis_node_id,annotation_layer_id,node_type,reference_span_id,node_order
  ) VALUES (
    '33000000-0000-4000-8000-000000000098','32000000-0000-4000-8000-000000000001',
    'CLAUSE','13000000-0000-4000-8000-000000000097',98
  );

  INSERT INTO authoring.analysis_node_segments(analysis_node_id,text_segment_id,member_order)
  VALUES
    ('33000000-0000-4000-8000-000000000098','24000000-0000-4000-8000-000000000001',0),
    ('33000000-0000-4000-8000-000000000098','24000000-0000-4000-8000-000000000098',1);

  BEGIN
    INSERT INTO authoring.analysis_node_segments(analysis_node_id,text_segment_id,member_order)
    VALUES ('33000000-0000-4000-8000-000000000001','24000000-0000-4000-8000-000000000098',99);
  EXCEPTION WHEN raise_exception THEN
    IF SQLERRM <> 'analysis-node reference span must contain every member text-segment span' THEN
      RAISE;
    END IF;
    invalid_failed := true;
  END;

  IF NOT invalid_failed THEN
    RAISE EXCEPTION 'verse-local node must reject a later-verse segment in the same expression';
  END IF;

  DELETE FROM authoring.analysis_node_segments WHERE analysis_node_id='33000000-0000-4000-8000-000000000098';
  DELETE FROM authoring.analysis_nodes WHERE analysis_node_id='33000000-0000-4000-8000-000000000098';
  DELETE FROM authoring.text_segments WHERE text_segment_id='24000000-0000-4000-8000-000000000098';
  DELETE FROM authoring.reference_spans WHERE reference_span_id IN (
    '13000000-0000-4000-8000-000000000097','13000000-0000-4000-8000-000000000098'
  );
  DELETE FROM authoring.reference_atoms WHERE reference_atom_id='12000000-0000-4000-8000-000000000098';
END
$node_segment_span_containment$;

-- Alignment stream pinning (WRITTEN vs READ).
DO $$
DECLARE failed boolean := false;
BEGIN
  BEGIN
    INSERT INTO authoring.alignment_source_members(alignment_group_id,text_segment_id,member_order)
    VALUES ('25000000-0000-4000-8000-000000000001','24000000-0000-4000-8000-000000000004',9);
  EXCEPTION WHEN raise_exception THEN failed := true;
  END;
  IF NOT failed THEN RAISE EXCEPTION 'READ segment must not enter WRITTEN-pinned alignment group'; END IF;
END $$;

-- Research position must pin an IssueVersion belonging to the same stable issue.
DO $cross_issue_position$
DECLARE failed boolean := false;
BEGIN
  BEGIN
    INSERT INTO authoring.research_objects(research_object_id,object_type)
    VALUES ('44000000-0000-4000-8000-000000000099','RESEARCH_POSITION_VERSION');

    INSERT INTO authoring.research_position_versions(
      research_position_version_id,research_position_id,research_issue_id,research_issue_version_id,
      version_number,title,position_summary,position_status,review_status,content_hash
    ) VALUES (
      '44000000-0000-4000-8000-000000000099','44100000-0000-4000-8000-000000000001',
      '43100000-0000-4000-8000-000000000001','43000000-0000-4000-8000-000000000002',
      2,'Invalid','Invalid','ACTIVE','HUMAN_REVIEWED',
      '9999999999999999999999999999999999999999999999999999999999999999'
    );
  EXCEPTION WHEN foreign_key_violation THEN
    failed := true;
  END;
  IF NOT failed THEN
    RAISE EXCEPTION 'cross-issue ResearchPositionVersion must fail on exact issue/version compatibility';
  END IF;
END
$cross_issue_position$;

-- Translation source basis must use pinned stream.
DO $$
DECLARE failed boolean := false;
BEGIN
  BEGIN
    INSERT INTO authoring.translation_source_basis_segments(translation_source_basis_id,text_segment_id,member_order)
    VALUES ('40000000-0000-4000-8000-000000000001','24000000-0000-4000-8000-000000000004',9);
  EXCEPTION WHEN raise_exception THEN failed := true;
  END;
  IF NOT failed THEN RAISE EXCEPTION 'source-basis segment from READ stream must fail for WRITTEN basis'; END IF;
END $$;

-- TranslationDecision language mismatch must fail.
DO $$
DECLARE failed boolean := false;
BEGIN
  BEGIN
    INSERT INTO authoring.translation_decisions(
      translation_decision_id,reference_span_id,translation_source_basis_id,translation_policy_version_id,
      target_language_tag,decision_kind,selected_rendering,decision_schema_version,decision_payload,review_status
    ) VALUES (
      '42200000-0000-4000-8000-000000000099','13000000-0000-4000-8000-000000000001',
      '40000000-0000-4000-8000-000000000001','42000000-0000-4000-8000-000000000001',
      'en','INVALID','invalid','1.1','{}','HUMAN_REVIEWED'
    );
  EXCEPTION WHEN raise_exception THEN failed := true;
  END;
  IF NOT failed THEN RAISE EXCEPTION 'TranslationDecision language mismatch must fail'; END IF;
END $$;

-- Editorial/composite basis requires actual adopted reading text.
DO $missing_adopted_reading$
DECLARE failed boolean := false;
BEGIN
  BEGIN
    INSERT INTO authoring.research_objects(research_object_id,object_type)
    VALUES ('40000000-0000-4000-8000-000000000099','TRANSLATION_SOURCE_BASIS');

    INSERT INTO authoring.translation_source_bases(
      translation_source_basis_id,reference_span_id,source_digital_expression_id,source_text_stream_id,
      basis_kind,review_status,content_hash
    ) VALUES (
      '40000000-0000-4000-8000-000000000099','13000000-0000-4000-8000-000000000001',
      '22000000-0000-4000-8000-000000000001','23000000-0000-4000-8000-000000000001',
      'EDITORIAL_EMENDATION','HUMAN_REVIEWED',
      'abababababababababababababababababababababababababababababababab'
    );
  EXCEPTION WHEN check_violation THEN
    failed := true;
  END;
  IF NOT failed THEN
    RAISE EXCEPTION 'editorial emendation without adopted reading text must fail on basis-kind CHECK';
  END IF;
END
$missing_adopted_reading$;

-- Rights: no applicable rule defaults DENY; same-specificity DENY beats ALLOW.
SELECT spike_test.assert_true(
  authoring.evaluate_rights(
    '45000000-0000-4000-8000-000000000001','MODEL_CONTEXT',
    'PUBLICATION','PUBLIC','COMMERCIAL'
  ) = 'DENY',
  'no applicable rights rule must default DENY'
);
SELECT spike_test.assert_true(
  authoring.evaluate_rights(
    '45000000-0000-4000-8000-000000000001','DISPLAY_EXCERPT',
    'PUBLICATION','PUBLIC','COMMERCIAL'
  ) = 'DENY',
  'same-specificity DENY must beat ALLOW'
);

-- Snapshot winner must be among applicable rules.
DO $$
DECLARE failed boolean := false;
BEGIN
  BEGIN
    INSERT INTO serving.rights_decision_snapshots(
      rights_decision_snapshot_id,subject_type,subject_identifier,operation,purpose_scope,audience_scope,
      commercial_context,applicable_rule_ids,winning_rule_ids,decision,decision_basis,obligations_json,
      resolver_version,evaluated_at,decision_hash
    ) VALUES (
      '45200000-0000-4000-8000-000000000099','RESEARCH_OBJECT','51000000-0000-4000-8000-000000000001',
      'DISPLAY_EXCERPT','PUBLICATION','PUBLIC','COMMERCIAL',
      ARRAY['45100000-0000-4000-8000-000000000001'::uuid],
      ARRAY['45100000-0000-4000-8000-000000000002'::uuid],
      'DENY','RULE','[]','spike',now(),
      'eeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee'
    );
  EXCEPTION WHEN check_violation THEN failed := true;
  END;
  IF NOT failed THEN RAISE EXCEPTION 'winning rights rule outside applicable set must fail'; END IF;
END $$;

-- Candidate evidence packet belongs to unpublished release 2 so negative evidence
-- tests hit rights/citation/hash validation before any release-immutability guard.
INSERT INTO serving.published_evidence_packets(
  published_evidence_packet_id,research_release_id,packet_type
) VALUES (
  '50100000-0000-4000-8000-000000000002',
  '47000000-0000-4000-8000-000000000002',
  'PASSAGE_ANALYSIS_CANDIDATE'
);

-- Public excerpt cannot reuse wrong-operation / DENY snapshot.
DO $$
DECLARE failed boolean := false;
BEGIN
  BEGIN
    INSERT INTO serving.published_evidence_items(
      published_evidence_item_id,published_evidence_packet_id,research_object_id,evidence_content_hash,
      evidence_class,citation_locator,permitted_excerpt,rights_decision_snapshot_id,evidence_stability_class,sort_order
    ) VALUES (
      '50200000-0000-4000-8000-000000000099','50100000-0000-4000-8000-000000000002',
      '51000000-0000-4000-8000-000000000001',
      'ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff',
      'SCHOLARLY_SOURCE_TEXT','{"locatorType":"BIBLICAL_REFERENCE","referenceSpanId":"13000000-0000-4000-8000-000000000001"}',
      'must fail','45200000-0000-4000-8000-000000000002','IMMUTABLE_SNAPSHOT',9
    );
  EXCEPTION WHEN raise_exception THEN failed := true;
  END;
  IF NOT failed THEN RAISE EXCEPTION 'wrong-operation rights snapshot must not publish excerpt'; END IF;
END $$;

-- Public excerpt cannot borrow an ALLOW snapshot from a different subject.
INSERT INTO serving.rights_decision_snapshots(
  rights_decision_snapshot_id,subject_type,subject_identifier,operation,purpose_scope,audience_scope,
  commercial_context,applicable_rule_ids,winning_rule_ids,decision,decision_basis,obligations_json,
  resolver_version,evaluated_at,decision_hash
) VALUES (
  '45200000-0000-4000-8000-000000000098','RESEARCH_OBJECT','42000000-0000-4000-8000-000000000001',
  'DISPLAY_EXCERPT','PUBLICATION','PUBLIC','COMMERCIAL',
  ARRAY['45100000-0000-4000-8000-000000000001'::uuid],
  ARRAY['45100000-0000-4000-8000-000000000001'::uuid],
  'ALLOW','RULE','[]','spike',now(),
  'abababababababababababababababababababababababababababababababab'
);

DO $wrong_subject$
DECLARE failed boolean := false;
BEGIN
  BEGIN
    INSERT INTO serving.published_evidence_items(
      published_evidence_item_id,published_evidence_packet_id,research_object_id,evidence_content_hash,
      evidence_class,citation_locator,permitted_excerpt,rights_decision_snapshot_id,evidence_stability_class,sort_order
    ) VALUES (
      '50200000-0000-4000-8000-000000000097','50100000-0000-4000-8000-000000000002',
      '51000000-0000-4000-8000-000000000001',
      'edededededededededededededededededededededededededededededededed',
      'SCHOLARLY_SOURCE_TEXT','{"locatorType":"BIBLICAL_REFERENCE","referenceSpanId":"13000000-0000-4000-8000-000000000001"}',
      'must fail','45200000-0000-4000-8000-000000000098','IMMUTABLE_SNAPSHOT',7
    );
  EXCEPTION WHEN raise_exception THEN failed := true;
  END;
  IF NOT failed THEN RAISE EXCEPTION 'rights snapshot for another subject must not publish excerpt'; END IF;
END $wrong_subject$;

-- Typed CitationLocator must enforce locator-specific identity.
DO $bad_locator$
DECLARE failed boolean := false;
BEGIN
  BEGIN
    INSERT INTO serving.published_evidence_items(
      published_evidence_item_id,published_evidence_packet_id,research_object_id,evidence_content_hash,
      evidence_class,citation_locator,evidence_stability_class,sort_order
    ) VALUES (
      '50200000-0000-4000-8000-000000000096',
      '50100000-0000-4000-8000-000000000002',
      '51000000-0000-4000-8000-000000000001',
      'cdcdcdcdcdcdcdcdcdcdcdcdcdcdcdcdcdcdcdcdcdcdcdcdcdcdcdcdcdcdcdcd',
      'SCHOLARLY_SOURCE_TEXT',
      '{"locatorType":"BIBLICAL_REFERENCE"}',
      'IMMUTABLE_SNAPSHOT',6
    );
  EXCEPTION WHEN check_violation THEN failed := true;
  END;
  IF NOT failed THEN RAISE EXCEPTION 'BIBLICAL_REFERENCE without referenceSpanId must fail'; END IF;
END
$bad_locator$;

-- Immutable evidence requires a content hash.
DO $immutable_evidence$
DECLARE failed boolean := false;
BEGIN
  BEGIN
    INSERT INTO serving.published_evidence_items(
      published_evidence_item_id,published_evidence_packet_id,research_object_id,
      evidence_class,citation_locator,evidence_stability_class,sort_order
    ) VALUES (
      '50200000-0000-4000-8000-000000000098','50100000-0000-4000-8000-000000000002',
      '51000000-0000-4000-8000-000000000001','SCHOLARLY_SOURCE_TEXT',
      '{"locatorType":"BIBLICAL_REFERENCE","referenceSpanId":"13000000-0000-4000-8000-000000000001"}',
      'IMMUTABLE_SNAPSHOT',8
    );
  EXCEPTION WHEN check_violation THEN failed := true;
  END;
  IF NOT failed THEN RAISE EXCEPTION 'immutable evidence without hash must fail'; END IF;
END
$immutable_evidence$;

-- Deterministic release-pinned CorpusQuery analogue.
SELECT spike_test.assert_true(
  (SELECT count(*) FROM serving.spike_corpus_query(
    '47000000-0000-4000-8000-000000000001',
    '34000000-0000-4000-8000-000000000001',NULL,50
  )) = 1,
  'release-pinned query must return exactly one distinct fixture span'
);
SELECT spike_test.assert_true(
  (SELECT reference_span_id::text FROM serving.spike_corpus_query(
    '47000000-0000-4000-8000-000000000001',
    '34000000-0000-4000-8000-000000000001',NULL,50
  ) ORDER BY reference_span_id LIMIT 1) = '13000000-0000-4000-8000-000000000001',
  'query membership must resolve to 1 Samuel 16:7 fixture span'
);
SELECT spike_test.assert_true(
  (SELECT count(*) FROM serving.spike_corpus_query(
    '47000000-0000-4000-8000-000000000001',
    '34000000-0000-4000-8000-000000000001',
    '13000000-0000-4000-8000-000000000001',50
  )) = 0,
  'cursor must not mutate scholarly query meaning and must page past the only result'
);

-- Translation aggregate hash seals source-basis identity.
SELECT spike_test.assert_true(
  length(publication_control.translation_aggregate_hash('42200000-0000-4000-8000-000000000001')) = 64,
  'translation aggregate hash must be SHA-256 hex'
);

-- Serving must be physically separable: no Serving FK/function may depend on Authoring.
SELECT spike_test.assert_true(
  NOT EXISTS (
    SELECT 1
    FROM pg_constraint c
    JOIN pg_namespace n ON n.oid=c.connamespace
    JOIN pg_class parent ON parent.oid=c.confrelid
    JOIN pg_namespace pn ON pn.oid=parent.relnamespace
    WHERE n.nspname='serving' AND c.contype='f' AND pn.nspname='authoring'
  ),
  'serving schema must not contain foreign keys to authoring schema'
);
SELECT spike_test.assert_true(
  NOT EXISTS (
    SELECT 1
    FROM pg_proc p
    JOIN pg_namespace n ON n.oid=p.pronamespace
    WHERE n.nspname='serving'
      AND p.prokind='f'
      AND CASE WHEN p.prokind='f' THEN pg_get_functiondef(p.oid) ELSE '' END ILIKE '%authoring.%'
  ),
  'serving functions must not query authoring schema'
);

-- RLS: User A sees only User A private workspace data.
SET ROLE authenticated;
SELECT set_config('request.jwt.claim.sub','aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa',false);
SELECT spike_test.assert_true(
  (SELECT count(*) FROM workspace.research_projects) = 1,
  'RLS must hide User B project from User A'
);
SELECT spike_test.assert_true(
  (SELECT count(*) FROM workspace.saved_queries) = 1,
  'RLS must hide User B saved query from User A'
);
SELECT spike_test.assert_true(
  (SELECT count(*) FROM workspace.user_translation_drafts) = 1,
  'RLS must hide User B translation draft from User A'
);

DO $cross_tenant_project$
DECLARE failed boolean := false;
BEGIN
  BEGIN
    INSERT INTO workspace.saved_queries(saved_query_id,owner_user_id,project_id,query_json)
    VALUES (
      '60100000-0000-4000-8000-000000000099',
      'aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa',
      '60000000-0000-4000-8000-000000000002',
      '{"q":"must-fail"}'
    );
  EXCEPTION WHEN foreign_key_violation THEN failed := true;
  END;
  IF NOT failed THEN RAISE EXCEPTION 'User A must not attach a child row to User B project'; END IF;
END
$cross_tenant_project$;
RESET ROLE;

-- Inactive candidate materialization must not be publicly visible before publication.
-- Release 2 already has release/component rows, and the candidate evidence packet
-- was created above, so these assertions detect direct-table leaks that a
-- pointer-only test would miss.
SET ROLE anon;
SELECT spike_test.assert_true(
  (SELECT count(*) FROM serving.research_releases
   WHERE research_release_id='47000000-0000-4000-8000-000000000002') = 0,
  'anon must not read an unpublished ResearchRelease directly'
);
SELECT spike_test.assert_true(
  (SELECT count(*) FROM serving.research_release_components
   WHERE research_release_id='47000000-0000-4000-8000-000000000002') = 0,
  'anon must not read components of an unpublished ResearchRelease directly'
);
SELECT spike_test.assert_true(
  (SELECT count(*) FROM serving.published_evidence_packets
   WHERE published_evidence_packet_id='50100000-0000-4000-8000-000000000002') = 0,
  'anon must not read materialized evidence for an unpublished ResearchRelease'
);
SELECT spike_test.assert_true(
  (SELECT count(*) FROM serving.spike_corpus_query(
    '47000000-0000-4000-8000-000000000002',
    '34000000-0000-4000-8000-000000000001',NULL,50
  )) = 0,
  'anon corpus query must not use an unpublished ResearchRelease'
);
RESET ROLE;

-- Public/authenticated role cannot read Authoring.
SET ROLE authenticated;
DO $$
DECLARE failed boolean := false;
BEGIN
  BEGIN
    PERFORM count(*) FROM authoring.research_objects;
  EXCEPTION WHEN insufficient_privilege THEN failed := true;
  END;
  IF NOT failed THEN RAISE EXCEPTION 'authenticated role must not read authoring schema'; END IF;
END $$;
RESET ROLE;

-- Authenticated role cannot execute publication-only SECURITY DEFINER function.
SET ROLE authenticated;
DO $$
DECLARE failed boolean := false;
BEGIN
  BEGIN
    PERFORM publication_control.publish_release_to_channel(
      'PRODUCTION','47000000-0000-4000-8000-000000000002',NULL,false
    );
  EXCEPTION WHEN insufficient_privilege THEN failed := true;
  END;
  IF NOT failed THEN RAISE EXCEPTION 'authenticated role must not execute publication function'; END IF;
END $$;
RESET ROLE;

-- Publication failure before pointer move preserves old production release.
DO $$
DECLARE failed boolean := false;
BEGIN
  BEGIN
    PERFORM publication_control.publish_release_to_channel(
      'PRODUCTION','47000000-0000-4000-8000-000000000002',NULL,true
    );
  EXCEPTION WHEN raise_exception THEN failed := true;
  END;
  IF NOT failed THEN RAISE EXCEPTION 'failure injection did not fire'; END IF;
END $$;

SELECT spike_test.assert_true(
  (SELECT research_release_id FROM serving.release_channel_pointers
   WHERE release_channel_id='47200000-0000-4000-8000-000000000001')
   = '47000000-0000-4000-8000-000000000001',
  'failed publication must not move production pointer'
);

SELECT spike_test.assert_true(
  (SELECT count(*) FROM serving.research_release_events
   WHERE research_release_id='47000000-0000-4000-8000-000000000002'
     AND event_type='PUBLISHED') = 0,
  'failed publication must roll back the candidate PUBLISHED event'
);

-- Successful publication moves one mutable pointer; rollback is another pointer move.
SELECT publication_control.publish_release_to_channel(
  'PRODUCTION','47000000-0000-4000-8000-000000000002',NULL,false
);
SELECT spike_test.assert_true(
  (SELECT research_release_id FROM serving.release_channel_pointers
   WHERE release_channel_id='47200000-0000-4000-8000-000000000001')
   = '47000000-0000-4000-8000-000000000002',
  'successful publication must move production pointer to complete candidate release'
);
SELECT spike_test.assert_true(
  (SELECT count(*) FROM serving.research_release_events
   WHERE research_release_id='47000000-0000-4000-8000-000000000002'
     AND event_type='PUBLISHED') = 1,
  'successful publication must append exactly one PUBLISHED event'
);

-- The same materialized candidate becomes visible only after the publication
-- transaction commits its PUBLISHED event and channel-pointer move.
SET ROLE anon;
SELECT spike_test.assert_true(
  (SELECT count(*) FROM serving.research_releases
   WHERE research_release_id='47000000-0000-4000-8000-000000000002') = 1,
  'published ResearchRelease must become visible to anon'
);
SELECT spike_test.assert_true(
  (SELECT count(*) FROM serving.research_release_components
   WHERE research_release_id='47000000-0000-4000-8000-000000000002') = 3,
  'published ResearchRelease components must become visible to anon'
);
SELECT spike_test.assert_true(
  (SELECT count(*) FROM serving.published_evidence_packets
   WHERE published_evidence_packet_id='50100000-0000-4000-8000-000000000002') = 1,
  'published evidence packet must become visible to anon'
);
RESET ROLE;

INSERT INTO serving.research_objects(research_object_id,object_type,source_content_hash,published_at)
VALUES (
  '52000000-0000-4000-8000-000000000001','PUBLISHED_ANALYSIS_SET',
  'post-publish-negative-fixture',now()
);

DO $late_component$
DECLARE failed boolean := false;
BEGIN
  BEGIN
    INSERT INTO serving.research_release_components(
      research_release_id,component_kind,component_research_object_id,
      component_version,content_hash,component_order
    ) VALUES (
      '47000000-0000-4000-8000-000000000002','PUBLISHED_ANALYSIS',
      '52000000-0000-4000-8000-000000000001','1',
      '1212121212121212121212121212121212121212121212121212121212121212',99
    );
  EXCEPTION WHEN raise_exception THEN failed := true;
  END;
  IF NOT failed THEN RAISE EXCEPTION 'cannot add a release component after PUBLISHED'; END IF;
END
$late_component$;

DO $late_analysis_update$
DECLARE failed boolean := false;
BEGIN
  BEGIN
    UPDATE serving.published_passage_analyses
    SET rendered_payload='{"mutated":true}'
    WHERE published_analysis_id='50000000-0000-4000-8000-000000000001';
  EXCEPTION WHEN raise_exception THEN failed := true;
  END;
  IF NOT failed THEN RAISE EXCEPTION 'published passage analysis must be immutable'; END IF;
END
$late_analysis_update$;

DO $late_projection$
DECLARE failed boolean := false;
BEGIN
  BEGIN
    INSERT INTO serving.corpus_node_features(
      corpus_release_id,analysis_node_id,feature_key,feature_value
    ) VALUES (
      '30000000-0000-4000-8000-000000000001',
      '33000000-0000-4000-8000-000000000001',
      'POST_PUBLISH_MUTATION','must-fail'
    );
  EXCEPTION WHEN raise_exception THEN failed := true;
  END;
  IF NOT failed THEN RAISE EXCEPTION 'published corpus projection must be immutable'; END IF;
END
$late_projection$;
SELECT publication_control.publish_release_to_channel(
  'PRODUCTION','47000000-0000-4000-8000-000000000001',NULL,false
);
SELECT spike_test.assert_true(
  (SELECT research_release_id FROM serving.release_channel_pointers
   WHERE release_channel_id='47200000-0000-4000-8000-000000000001')
   = '47000000-0000-4000-8000-000000000001',
  'rollback must restore old release by pointer move'
);

-- Release rows are immutable.
DO $$
DECLARE failed boolean := false;
BEGIN
  BEGIN
    UPDATE serving.research_releases
    SET release_label='mutated'
    WHERE research_release_id='47000000-0000-4000-8000-000000000001';
  EXCEPTION WHEN raise_exception THEN failed := true;
  END;
  IF NOT failed THEN RAISE EXCEPTION 'ResearchRelease mutation must fail'; END IF;
END $$;

-- Public read path uses only Serving projections and no Authoring privileges.
SET ROLE anon;
SELECT spike_test.assert_true(
  (SELECT count(*) FROM serving.current_release WHERE channel_key='PRODUCTION') = 1,
  'anon public read must resolve current production release'
);
SELECT spike_test.assert_true(
  (SELECT count(*) FROM serving.spike_corpus_query(
    '47000000-0000-4000-8000-000000000001',
    '34000000-0000-4000-8000-000000000001',NULL,50
  )) = 1,
  'anon corpus query must work entirely from Serving projections'
);
RESET ROLE;

-- Stronger plane-isolation proof: make Authoring unavailable by name, then rerun public reads.
ALTER SCHEMA authoring RENAME TO authoring_offline;

SET ROLE anon;
SELECT spike_test.assert_true(
  (SELECT count(*) FROM serving.current_release WHERE channel_key='PRODUCTION') = 1,
  'current release must remain readable while Authoring is offline'
);
SELECT spike_test.assert_true(
  (SELECT count(*) FROM serving.spike_corpus_query(
    '47000000-0000-4000-8000-000000000001',
    '34000000-0000-4000-8000-000000000001',NULL,50
  )) = 1,
  'public corpus query must remain functional while Authoring is offline'
);
RESET ROLE;

ALTER SCHEMA authoring_offline RENAME TO authoring;


-- WB-2/WB-3: publication must fail closed when a CORPUS component lacks public full-text rights.
DELETE FROM serving.rights_decision_snapshots
WHERE rights_decision_snapshot_id='45200000-0000-4000-8000-000000000003';

SET ROLE publication_worker;
DO $wb2_missing_corpus_rights$
DECLARE failed boolean := false;
BEGIN
  BEGIN
    PERFORM publication_control.publish_release_to_channel(
      'PRODUCTION','47000000-0000-4000-8000-000000000002',NULL,false
    );
  EXCEPTION WHEN raise_exception THEN failed := true;
  END;
  IF NOT failed THEN
    RAISE EXCEPTION 'release publication without corpus DISPLAY_FULLTEXT rights must fail';
  END IF;
END
$wb2_missing_corpus_rights$;
RESET ROLE;

INSERT INTO serving.rights_decision_snapshots(
  rights_decision_snapshot_id,subject_type,subject_identifier,operation,purpose_scope,audience_scope,
  commercial_context,applicable_rule_ids,winning_rule_ids,decision,decision_basis,obligations_json,
  resolver_version,evaluated_at,decision_hash
) VALUES (
  '45200000-0000-4000-8000-000000000003','CORPUS_RELEASE','30000000-0000-4000-8000-000000000001',
  'DISPLAY_FULLTEXT','PUBLIC_DISPLAY','PUBLIC','MIXED',
  ARRAY['45100000-0000-4000-8000-000000000004'::uuid],
  ARRAY['45100000-0000-4000-8000-000000000004'::uuid],
  'CONDITIONAL','RULE',
  '[{"obligationType":"ATTRIBUTION","value":"Fixture Hebrew attribution"}]'::jsonb,
  'spike-rights-1',now(),'5656565656565656565656565656565656565656565656565656565656565656'
);

-- WB-3: public runtime reads the release-pinned Serving projection, not Authoring.
SET ROLE anon;
SELECT spike_test.assert_true(
  serving.read_passage_core(
    '47000000-0000-4000-8000-000000000001','MT_TEST','1 Sam 16:7'
  )->>'referenceSpanId' = '13000000-0000-4000-8000-000000000001',
  'Serving passage RPC must resolve the pinned ReferenceSpan'
);
SELECT spike_test.assert_true(
  serving.read_passage_core(
    '47000000-0000-4000-8000-000000000001','MT_TEST','1 Sam 16:7'
  )->>'hebrewText' = 'יראה עינים',
  'Serving passage RPC must reconstruct Hebrew surface from published text segments'
);
SELECT spike_test.assert_true(
  jsonb_array_length(
    serving.read_passage_core(
      '47000000-0000-4000-8000-000000000001','MT_TEST','1 Sam 16:7'
    )->'tokens'
  ) = 2,
  'Serving passage RPC must return published word tokens only'
);
RESET ROLE;

DROP SCHEMA spike_test CASCADE;


-- WB-2 RED: database rights obligation JSON must use the canonical contract key obligationType.
DO $wb2_obligation_type_contract$
DECLARE
  inserted boolean := false;
BEGIN
  BEGIN
    INSERT INTO serving.rights_decision_snapshots(
      rights_decision_snapshot_id,subject_type,subject_identifier,operation,purpose_scope,
      audience_scope,commercial_context,applicable_rule_ids,winning_rule_ids,
      decision,decision_basis,conditions_json,obligations_json,resolver_version,evaluated_at,decision_hash
    ) VALUES (
      '45200000-0000-4000-8000-0000000000a1','CORPUS_RELEASE',
      '30000000-0000-4000-8000-000000000001','DISPLAY_FULLTEXT','PUBLIC_DISPLAY',
      'PUBLIC','MIXED',ARRAY['45100000-0000-4000-8000-000000000001'::uuid],
      ARRAY['45100000-0000-4000-8000-000000000001'::uuid],
      'CONDITIONAL','RULE',NULL,
      '[{"obligationType":"ATTRIBUTION","value":"Open Scriptures Hebrew Bible attribution fixture"}]'::jsonb,
      'wb2-red-contract',now(),'abababababababababababababababababababababababababababababababab'
    );
    inserted := true;
  EXCEPTION WHEN check_violation THEN
    inserted := false;
  END;
  IF NOT inserted THEN
    RAISE EXCEPTION 'canonical RightsDecisionSnapshot obligationType payload must be accepted by PostgreSQL';
  END IF;
  DELETE FROM serving.rights_decision_snapshots
  WHERE rights_decision_snapshot_id='45200000-0000-4000-8000-0000000000a1';
END
$wb2_obligation_type_contract$;

-- WB-2 GREEN: reject the legacy obligation key so SQL and JSON Schema cannot diverge again.
DO $wb2_reject_legacy_obligation_key$
DECLARE
  inserted boolean := false;
BEGIN
  BEGIN
    INSERT INTO serving.rights_decision_snapshots(
      rights_decision_snapshot_id,subject_type,subject_identifier,operation,purpose_scope,
      audience_scope,commercial_context,applicable_rule_ids,winning_rule_ids,
      decision,decision_basis,conditions_json,obligations_json,resolver_version,evaluated_at,decision_hash
    ) VALUES (
      '45200000-0000-4000-8000-0000000000a2','CORPUS_RELEASE',
      '30000000-0000-4000-8000-000000000001','DISPLAY_FULLTEXT','PUBLIC_DISPLAY',
      'PUBLIC','MIXED',ARRAY['45100000-0000-4000-8000-000000000001'::uuid],
      ARRAY['45100000-0000-4000-8000-000000000001'::uuid],
      'CONDITIONAL','RULE',NULL,
      '[{"type":"ATTRIBUTION","value":"legacy key must fail"}]'::jsonb,
      'wb2-green-contract',now(),'acacacacacacacacacacacacacacacacacacacacacacacacacacacacacacacac'
    );
    inserted := true;
  EXCEPTION WHEN check_violation THEN
    inserted := false;
  END;
  IF inserted THEN
    RAISE EXCEPTION 'legacy rights obligation type key must be rejected';
  END IF;
END
$wb2_reject_legacy_obligation_key$;

