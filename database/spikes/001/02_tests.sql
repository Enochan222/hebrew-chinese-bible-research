\set ON_ERROR_STOP on

CREATE SCHEMA IF NOT EXISTS spike_test;

CREATE OR REPLACE FUNCTION spike_test.assert_true(ok boolean, message text)
RETURNS void
LANGUAGE plpgsql
AS $$
BEGIN
  IF NOT COALESCE(ok,false) THEN
    RAISE EXCEPTION 'ASSERTION FAILED: %', message;
  END IF;
END
$$;

-- Reference identity and alternate addressing.
SELECT spike_test.assert_true(
  (SELECT count(*) FROM authoring.reference_label_members
   WHERE reference_label_id='14000000-0000-4000-8000-000000000003') = 2,
  'alternate label must deterministically map to two ordered atoms'
);

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
DO $$
DECLARE failed boolean := false;
BEGIN
  BEGIN
    INSERT INTO authoring.research_position_versions(
      research_position_version_id,research_position_id,research_issue_id,research_issue_version_id,
      version_number,title,position_summary,position_status,review_status,content_hash
    ) VALUES (
      '44000000-0000-4000-8000-000000000099','44100000-0000-4000-8000-000000000001',
      '43100000-0000-4000-8000-000000000001','43000000-0000-4000-8000-000000000002',
      2,'Invalid','Invalid','ACTIVE','HUMAN_REVIEWED',
      '9999999999999999999999999999999999999999999999999999999999999999'
    );
  EXCEPTION WHEN foreign_key_violation THEN failed := true;
  END;
  IF NOT failed THEN RAISE EXCEPTION 'cross-issue ResearchPositionVersion must fail'; END IF;
END $$;

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
DO $$
DECLARE failed boolean := false;
BEGIN
  BEGIN
    INSERT INTO authoring.translation_source_bases(
      translation_source_basis_id,reference_span_id,source_digital_expression_id,source_text_stream_id,
      basis_kind,review_status,content_hash
    ) VALUES (
      '40000000-0000-4000-8000-000000000099','13000000-0000-4000-8000-000000000001',
      '22000000-0000-4000-8000-000000000001','23000000-0000-4000-8000-000000000001',
      'EDITORIAL_EMENDATION','HUMAN_REVIEWED',
      'abababababababababababababababababababababababababababababababab'
    );
  EXCEPTION WHEN check_violation THEN failed := true;
  END;
  IF NOT failed THEN RAISE EXCEPTION 'editorial emendation without adopted reading text must fail'; END IF;
END $$;

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

-- Public excerpt cannot reuse wrong-operation / DENY snapshot.
DO $$
DECLARE failed boolean := false;
BEGIN
  BEGIN
    INSERT INTO serving.published_evidence_items(
      published_evidence_item_id,published_evidence_packet_id,research_object_id,evidence_content_hash,
      evidence_class,citation_locator,permitted_excerpt,rights_decision_snapshot_id,evidence_stability_class,sort_order
    ) VALUES (
      '50200000-0000-4000-8000-000000000099','50100000-0000-4000-8000-000000000001',
      '51000000-0000-4000-8000-000000000001',
      'ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff',
      'SCHOLARLY_SOURCE_TEXT','{"locatorType":"BIBLICAL_REFERENCE","referenceSpanId":"13000000-0000-4000-8000-000000000001"}',
      'must fail','45200000-0000-4000-8000-000000000002','IMMUTABLE_SNAPSHOT',9
    );
  EXCEPTION WHEN raise_exception THEN failed := true;
  END;
  IF NOT failed THEN RAISE EXCEPTION 'wrong-operation rights snapshot must not publish excerpt'; END IF;
END $$;

-- Immutable evidence requires a content hash.
DO $$
DECLARE failed boolean := false;
BEGIN
  BEGIN
    INSERT INTO serving.published_evidence_items(
      published_evidence_item_id,published_evidence_packet_id,research_object_id,
      evidence_class,citation_locator,evidence_stability_class,sort_order
    ) VALUES (
      '50200000-0000-4000-8000-000000000098','50100000-0000-4000-8000-000000000001',
      '51000000-0000-4000-8000-000000000001','SCHOLARLY_SOURCE_TEXT',
      '{"locatorType":"BIBLICAL_REFERENCE","referenceSpanId":"13000000-0000-4000-8000-000000000001"}',
      'IMMUTABLE_SNAPSHOT',8
    );
  EXCEPTION WHEN check_violation THEN failed := true;
  END;
  IF NOT failed THEN RAISE EXCEPTION 'immutable evidence without hash must fail'; END IF;
END $$;

-- Deterministic release-pinned CorpusQuery analogue.
SELECT spike_test.assert_true(
  (SELECT count(*) FROM serving.spike_corpus_query(
    '47000000-0000-4000-8000-000000000001',
    '34000000-0000-4000-8000-000000000001',NULL,50
  )) = 1,
  'release-pinned query must return exactly one distinct fixture span'
);
SELECT spike_test.assert_true(
  (SELECT min(reference_span_id)::text FROM serving.spike_corpus_query(
    '47000000-0000-4000-8000-000000000001',
    '34000000-0000-4000-8000-000000000001',NULL,50
  )) = '13000000-0000-4000-8000-000000000001',
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
  length(serving.translation_aggregate_hash('42200000-0000-4000-8000-000000000001')) = 64,
  'translation aggregate hash must be SHA-256 hex'
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

-- Public read path uses security-invoker view and exposes no Authoring tables.
SET ROLE anon;
SELECT spike_test.assert_true(
  (SELECT count(*) FROM serving.current_release WHERE channel_key='PRODUCTION') = 1,
  'anon public read must resolve current production release'
);
RESET ROLE;

DROP SCHEMA spike_test CASCADE;
