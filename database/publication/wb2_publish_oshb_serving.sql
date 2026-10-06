\set ON_ERROR_STOP on
BEGIN;

-- Resolve the accepted WB-1 OSHB identities rather than hard-coding provider UUIDs.
SELECT cr.corpus_release_id::text AS oshb_corpus_id,
       cr.release_version AS oshb_release_version,
       cr.source_checksum AS oshb_checksum
FROM authoring.corpus_releases cr
JOIN authoring.digital_expressions de
  ON de.digital_expression_id = cr.digital_expression_id
WHERE de.metadata->>'sourceKey' = 'OSHB_MORPHHB'
\gset

SELECT al.annotation_layer_id::text AS oshb_layer_id
FROM authoring.annotation_layers al
WHERE al.metadata->>'sourceKey' = 'OSHB_MORPHHB'
  AND al.layer_kind = 'MORPHOLOGY'
\gset

SELECT ts.text_stream_id::text AS oshb_stream_id
FROM authoring.text_streams ts
JOIN authoring.digital_expressions de
  ON de.digital_expression_id = ts.digital_expression_id
WHERE de.metadata->>'sourceKey' = 'OSHB_MORPHHB'
  AND ts.stream_type = 'BASE'
\gset

SELECT reference_system_id::text AS oshb_reference_system_id
FROM authoring.reference_systems
WHERE code = 'OSHB_OSIS'
\gset

-- Explicit public-display rights for the pinned OSHB/WLC source.
INSERT INTO authoring.rights_policies(
  rights_policy_id,policy_key,policy_version,rights_basis,verified_at
) VALUES (
  '71000000-0000-4000-8000-000000000001',
  'WB2_OSHB_PUBLIC_DISPLAY','1',
  'WLC text public domain per upstream; OSHB lemma/morphology CC-BY-4.0 with attribution',
  now()
);

INSERT INTO authoring.rights_rules(
  rights_rule_id,rights_policy_id,operation,decision,purpose_scope,audience_scope,
  commercial_context,attribution_requirement
) VALUES (
  '71000000-0000-4000-8000-000000000002',
  '71000000-0000-4000-8000-000000000001',
  'DISPLAY_FULLTEXT','CONDITIONAL','PUBLIC_DISPLAY','PUBLIC','MIXED',
  'Open Scriptures Hebrew Bible / Westminster Leningrad Codex; preserve upstream attribution and license notice.'
);

-- Materialize only the OSHB corpus research object into Serving.
INSERT INTO serving.research_objects(
  research_object_id,object_type,source_content_hash,published_at
)
SELECT cr.corpus_release_id,'CORPUS_RELEASE',cr.source_checksum,now()
FROM authoring.corpus_releases cr
WHERE cr.corpus_release_id = current_setting('wb2.oshb_corpus_id')::uuid;

-- Project the exact verse spans needed by the OSHB word layer.
INSERT INTO serving.reference_spans(
  reference_span_id,book_code,start_sequence,end_sequence,reference_sort_key,span_kind
)
SELECT DISTINCT
  rs.reference_span_id,
  b.osis_code,
  rs.start_sequence,
  rs.end_sequence,
  cb.book_order::bigint * 1000000000 + rs.start_sequence::bigint,
  rs.span_kind
FROM authoring.analysis_nodes n
JOIN authoring.reference_spans rs USING (reference_span_id)
JOIN authoring.biblical_books b ON b.book_id = rs.book_id
JOIN authoring.canon_systems cs ON cs.code = 'TANAKH_OSIS_39'
JOIN authoring.canon_books cb
  ON cb.canon_system_id = cs.canon_system_id
 AND cb.book_id = rs.book_id
 AND cb.included
WHERE n.annotation_layer_id = :'oshb_layer_id'::uuid;

INSERT INTO serving.reference_systems(reference_system_id,code,name)
SELECT reference_system_id,code,name
FROM authoring.reference_systems
WHERE reference_system_id = :'oshb_reference_system_id'::uuid;

-- WB-CORPUS-001 OSHB labels are atomic selected-reference labels.
WITH selected_labels AS (
  SELECT
    rl.reference_label_id,
    rl.reference_system_id,
    rl.book_id,
    rl.label,
    rl.chapter_number,
    rl.verse_label,
    min(rlm.reference_atom_id::text)::uuid AS reference_atom_id,
    count(*) AS member_count
  FROM authoring.reference_labels rl
  JOIN authoring.reference_label_members rlm
    ON rlm.reference_label_id = rl.reference_label_id
  WHERE rl.reference_system_id = :'oshb_reference_system_id'::uuid
  GROUP BY
    rl.reference_label_id,rl.reference_system_id,rl.book_id,rl.label,
    rl.chapter_number,rl.verse_label
)
INSERT INTO serving.reference_labels(
  corpus_release_id,reference_label_id,reference_system_id,reference_span_id,
  book_code,label,chapter_number,verse_label,reference_sort_key
)
SELECT
  :'oshb_corpus_id'::uuid,
  sl.reference_label_id,
  sl.reference_system_id,
  rs.reference_span_id,
  b.osis_code,
  sl.label,
  sl.chapter_number,
  sl.verse_label,
  srs.reference_sort_key
FROM selected_labels sl
JOIN authoring.reference_spans rs
  ON rs.start_atom_id = sl.reference_atom_id
 AND rs.end_atom_id = sl.reference_atom_id
JOIN serving.reference_spans srs USING (reference_span_id)
JOIN authoring.biblical_books b ON b.book_id = sl.book_id
WHERE sl.member_count = 1;

INSERT INTO serving.corpus_text_segments(
  corpus_release_id,text_segment_id,reference_span_id,segment_order,
  surface_original,segment_kind,content_hash
)
SELECT
  :'oshb_corpus_id'::uuid,
  s.text_segment_id,
  s.reference_span_id,
  s.segment_order,
  s.surface_original,
  s.segment_kind,
  s.content_hash
FROM authoring.text_segments s
WHERE s.text_stream_id = :'oshb_stream_id'::uuid
  AND s.segment_storage_mode = 'PERSISTED_CONTENT'
  AND s.surface_original IS NOT NULL;

INSERT INTO serving.corpus_nodes(
  corpus_release_id,analysis_node_id,annotation_layer_id,node_type,reference_span_id
)
SELECT
  :'oshb_corpus_id'::uuid,
  n.analysis_node_id,
  n.annotation_layer_id,
  n.node_type,
  n.reference_span_id
FROM authoring.analysis_nodes n
WHERE n.annotation_layer_id = :'oshb_layer_id'::uuid;

INSERT INTO serving.corpus_node_features(
  corpus_release_id,analysis_node_id,feature_key,feature_value
)
SELECT
  :'oshb_corpus_id'::uuid,
  f.analysis_node_id,
  f.feature_key,
  f.feature_value
FROM authoring.analysis_node_features f
JOIN authoring.analysis_nodes n USING (analysis_node_id)
WHERE n.annotation_layer_id = :'oshb_layer_id'::uuid;

INSERT INTO serving.corpus_node_segments(
  corpus_release_id,analysis_node_id,text_segment_id,member_order,membership_role
)
SELECT
  :'oshb_corpus_id'::uuid,
  ns.analysis_node_id,
  ns.text_segment_id,
  ns.member_order,
  ns.membership_role
FROM authoring.analysis_node_segments ns
JOIN authoring.analysis_nodes n USING (analysis_node_id)
JOIN serving.corpus_text_segments sts
  ON sts.corpus_release_id = current_setting('wb2.oshb_corpus_id')::uuid
 AND sts.text_segment_id = ns.text_segment_id
WHERE n.annotation_layer_id = :'oshb_layer_id'::uuid;

INSERT INTO serving.rights_decision_snapshots(
  rights_decision_snapshot_id,subject_type,subject_identifier,operation,purpose_scope,
  audience_scope,commercial_context,applicable_rule_ids,winning_rule_ids,
  decision,decision_basis,conditions_json,obligations_json,resolver_version,evaluated_at,decision_hash
) VALUES (
  '71000000-0000-4000-8000-000000000003',
  'CORPUS_RELEASE',:'oshb_corpus_id'::uuid,'DISPLAY_FULLTEXT','PUBLIC_DISPLAY',
  'PUBLIC','MIXED',
  ARRAY['71000000-0000-4000-8000-000000000002'::uuid],
  ARRAY['71000000-0000-4000-8000-000000000002'::uuid],
  'CONDITIONAL','RULE',NULL,
  '[{"obligationType":"ATTRIBUTION","value":"Open Scriptures Hebrew Bible / Westminster Leningrad Codex; preserve upstream attribution and license notice."}]'::jsonb,
  'wb2-rights-1',now(),
  encode(sha256(convert_to(
    'OSHB_MORPHHB|DISPLAY_FULLTEXT|PUBLIC_DISPLAY|PUBLIC|MIXED|ATTRIBUTION|' || :'oshb_checksum',
    'UTF8'
  )),'hex')
);

INSERT INTO authoring.research_builds(
  research_build_id,build_version,status,started_at,completed_at,compiler_version,git_commit_sha
) VALUES (
  '71000000-0000-4000-8000-000000000004',
  'wb2-oshb-serving-1','COMPLETED',now(),now(),'wb2-serving-compiler-1',:'GIT_SHA'
);

INSERT INTO serving.research_releases(
  research_release_id,release_label,source_build_id,published_at,manifest_schema_version,
  manifest_hash,manifest_hash_algorithm,manifest_canonical_serialization,git_commit_sha,compiler_version
)
SELECT
  '71000000-0000-4000-8000-000000000005'::uuid,
  'wb2-oshb-serving-1',
  '71000000-0000-4000-8000-000000000004'::uuid,
  now(),'1.1',
  encode(sha256(convert_to(concat_ws('|',
    :'oshb_corpus_id',
    :'oshb_checksum',
    (SELECT count(*)::text FROM serving.reference_labels WHERE corpus_release_id=current_setting('wb2.oshb_corpus_id')::uuid),
    (SELECT count(*)::text FROM serving.corpus_nodes WHERE corpus_release_id=current_setting('wb2.oshb_corpus_id')::uuid),
    (SELECT count(*)::text FROM serving.corpus_text_segments WHERE corpus_release_id=current_setting('wb2.oshb_corpus_id')::uuid)
  ),'UTF8')),'hex'),
  'SHA256','RFC8785_JSON_CANONICALIZATION_SCHEME',:'GIT_SHA','wb2-serving-compiler-1';

INSERT INTO serving.research_release_components(
  research_release_id,component_kind,component_research_object_id,component_version,content_hash,component_order
) VALUES (
  '71000000-0000-4000-8000-000000000005',
  'CORPUS',:'oshb_corpus_id'::uuid,:'oshb_release_version',:'oshb_checksum',0
);

INSERT INTO serving.release_channels(release_channel_id,channel_key,description)
VALUES ('71000000-0000-4000-8000-000000000006','PRODUCTION','WB-2 production pointer');

SELECT publication_control.publish_release_to_channel(
  'PRODUCTION','71000000-0000-4000-8000-000000000005',NULL,false
);

-- Fail closed on any whole-corpus drift.
SELECT set_config('wb2.oshb_corpus_id', :'oshb_corpus_id', true);
DO $wb2_acceptance$
DECLARE
  ref_count bigint;
  node_count bigint;
  segment_count bigint;
  membership_count bigint;
  bhsa_rows bigint;
  gen_payload jsonb;
  canary_payload jsonb;
  cross_book_next text;
BEGIN
  SELECT count(*) INTO ref_count
  FROM serving.reference_labels
  WHERE corpus_release_id=current_setting('wb2.oshb_corpus_id')::uuid;

  SELECT count(*) INTO node_count
  FROM serving.corpus_nodes
  WHERE corpus_release_id=current_setting('wb2.oshb_corpus_id')::uuid;

  SELECT count(*) INTO segment_count
  FROM serving.corpus_text_segments
  WHERE corpus_release_id=current_setting('wb2.oshb_corpus_id')::uuid;

  SELECT count(*) INTO membership_count
  FROM serving.corpus_node_segments
  WHERE corpus_release_id=current_setting('wb2.oshb_corpus_id')::uuid;

  SELECT count(*) INTO bhsa_rows
  FROM serving.corpus_node_features
  WHERE corpus_release_id=current_setting('wb2.oshb_corpus_id')::uuid
    AND feature_key='SOURCE_KEY'
    AND feature_value <> 'OSHB_MORPHHB';

  IF ref_count <> 23213 THEN
    RAISE EXCEPTION 'WB-2 reference-label parity drift: %', ref_count;
  END IF;
  IF node_count <> 306785 THEN
    RAISE EXCEPTION 'WB-2 OSHB node parity drift: %', node_count;
  END IF;
  IF segment_count <> 306785 OR membership_count <> 306785 THEN
    RAISE EXCEPTION 'WB-2 OSHB text/member parity drift: segments=% memberships=%', segment_count, membership_count;
  END IF;
  IF bhsa_rows <> 0 THEN
    RAISE EXCEPTION 'WB-2 leaked non-OSHB source rows into Serving: %', bhsa_rows;
  END IF;

  gen_payload := serving.read_passage_core(
    '71000000-0000-4000-8000-000000000005','OSHB_OSIS','Gen.1.1'
  );
  canary_payload := serving.read_passage_core(
    '71000000-0000-4000-8000-000000000005','OSHB_OSIS','1Sam.16.7'
  );
  IF gen_payload IS NULL OR jsonb_array_length(gen_payload->'tokens') = 0 THEN
    RAISE EXCEPTION 'WB-3 arbitrary non-fixture passage Gen.1.1 is not readable';
  END IF;
  IF canary_payload IS NULL OR jsonb_array_length(canary_payload->'tokens') = 0 THEN
    RAISE EXCEPTION 'WB-3 1Sam.16.7 acceptance canary is not readable';
  END IF;
  IF position('Open Scriptures Hebrew Bible' in (gen_payload->>'attribution')) = 0 THEN
    RAISE EXCEPTION 'WB-3 attribution missing from passage payload';
  END IF;

  SELECT next_label.label INTO cross_book_next
  FROM serving.reference_labels current_label
  JOIN serving.reference_labels next_label
    ON next_label.corpus_release_id=current_label.corpus_release_id
   AND next_label.reference_system_id=current_label.reference_system_id
   AND next_label.reference_sort_key = (
     SELECT min(x.reference_sort_key)
     FROM serving.reference_labels x
     WHERE x.corpus_release_id=current_label.corpus_release_id
       AND x.reference_system_id=current_label.reference_system_id
       AND x.reference_sort_key > current_label.reference_sort_key
   )
  WHERE current_label.corpus_release_id=current_setting('wb2.oshb_corpus_id')::uuid
    AND current_label.book_code='Gen'
    AND next_label.book_code <> current_label.book_code
  ORDER BY current_label.reference_sort_key DESC
  LIMIT 1;

  IF cross_book_next IS NULL OR cross_book_next NOT LIKE 'Exod.%' THEN
    RAISE EXCEPTION 'WB-3 cross-book navigation Gen -> Exod failed: %', cross_book_next;
  END IF;
END
$wb2_acceptance$;

COMMIT;
