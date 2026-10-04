\set ON_ERROR_STOP on

CREATE SCHEMA IF NOT EXISTS wb0_test;

CREATE OR REPLACE FUNCTION wb0_test.assert_true(ok boolean, message text)
RETURNS void
LANGUAGE plpgsql
AS $assert$
BEGIN
  IF NOT COALESCE(ok,false) THEN
    RAISE EXCEPTION 'WB0 ASSERTION FAILED: %', message;
  END IF;
END
$assert$;

-- The two provider-native addresses must resolve to the same canonical atom.
SELECT wb0_test.assert_true(
  (
    SELECT count(DISTINCT rlm.reference_atom_id)
    FROM authoring.reference_labels rl
    JOIN authoring.reference_systems rs USING (reference_system_id)
    JOIN authoring.reference_label_members rlm USING (reference_label_id)
    WHERE rs.code IN ('OSHB_OSIS','BHSA_2021_SECTION')
  ) = 1,
  'OSHB and BHSA provider labels must resolve to one canonical 1 Sam 16:7 atom'
);

SELECT wb0_test.assert_true(
  (
    SELECT count(*)
    FROM authoring.analysis_nodes n
    JOIN authoring.annotation_layers l USING (annotation_layer_id)
    JOIN authoring.annotation_frameworks f USING (annotation_framework_id)
    WHERE f.framework_key='OSHB_MORPHHB_REAL' AND n.node_type='WORD'
  ) = 25,
  'pinned WB-0 OSHB word-node count must be 25'
);

SELECT wb0_test.assert_true(
  (
    SELECT count(*)
    FROM authoring.analysis_nodes n
    JOIN authoring.annotation_layers l USING (annotation_layer_id)
    JOIN authoring.annotation_frameworks f USING (annotation_framework_id)
    WHERE f.framework_key='BHSA_2021_REAL' AND n.node_type='WORD'
  ) = 34,
  'pinned WB-0 BHSA word-node count must be 34'
);

SELECT wb0_test.assert_true(
  (
    SELECT count(*)
    FROM authoring.analysis_nodes n
    JOIN authoring.annotation_layers l USING (annotation_layer_id)
    JOIN authoring.annotation_frameworks f USING (annotation_framework_id)
    WHERE f.framework_key='BHSA_2021_REAL' AND n.node_type='PHRASE'
  ) = 22,
  'pinned WB-0 BHSA phrase-node count must be 22'
);

SELECT wb0_test.assert_true(
  (
    SELECT count(*)
    FROM authoring.analysis_nodes n
    JOIN authoring.annotation_layers l USING (annotation_layer_id)
    JOIN authoring.annotation_frameworks f USING (annotation_framework_id)
    WHERE f.framework_key='BHSA_2021_REAL' AND n.node_type='CLAUSE'
  ) = 7,
  'pinned WB-0 BHSA clause-node count must be 7'
);

SELECT wb0_test.assert_true(
  (
    SELECT count(*)
    FROM authoring.analysis_edges e
    JOIN authoring.annotation_layers l USING (annotation_layer_id)
    JOIN authoring.annotation_frameworks f USING (annotation_framework_id)
    WHERE f.framework_key='BHSA_2021_REAL'
      AND e.relation_type IN ('MEMBER_OF_PHRASE','MEMBER_OF_CLAUSE')
  ) = 90,
  'pinned WB-0 BHSA graph membership-edge count must be 90'
);

SELECT wb0_test.assert_true(
  (
    SELECT count(*)
    FROM authoring.analysis_node_features
    WHERE feature_key IN ('BRIDGE_OSM_PRIMARY_RAW','BRIDGE_OSM_SECONDARY_RAW')
  ) = 35,
  'pinned WB-0 bridging feature-value count must be 35'
);

SELECT wb0_test.assert_true(
  (
    SELECT count(*)
    FROM authoring.analysis_nodes n
    JOIN authoring.annotation_layers l USING (annotation_layer_id)
    JOIN authoring.annotation_frameworks f USING (annotation_framework_id)
    WHERE f.framework_key='BHSA_2021_REAL'
      AND n.node_type='WORD'
      AND n.metadata @> '{"annotationOnly":true}'::jsonb
  ) = 2,
  'exactly two pinned BHSA word nodes must remain annotation-only'
);

SELECT wb0_test.assert_true(
  (
    SELECT array_agg(n.external_node_id ORDER BY n.external_node_id)
    FROM authoring.analysis_nodes n
    JOIN authoring.annotation_layers l USING (annotation_layer_id)
    JOIN authoring.annotation_frameworks f USING (annotation_framework_id)
    WHERE f.framework_key='BHSA_2021_REAL'
      AND n.node_type='WORD'
      AND n.metadata @> '{"annotationOnly":true}'::jsonb
  ) = ARRAY['150439','150445']::text[],
  'annotation-only provider IDs must remain the pinned 150439/150445 nodes'
);

SELECT wb0_test.assert_true(
  NOT EXISTS (
    SELECT 1
    FROM authoring.analysis_nodes n
    JOIN authoring.analysis_node_segments ns USING (analysis_node_id)
    JOIN authoring.annotation_layers l USING (annotation_layer_id)
    JOIN authoring.annotation_frameworks f USING (annotation_framework_id)
    WHERE f.framework_key='BHSA_2021_REAL'
      AND n.metadata @> '{"annotationOnly":true}'::jsonb
  ),
  'annotation-only BHSA nodes must have zero invented TextSegment memberships'
);

SELECT wb0_test.assert_true(
  (
    SELECT count(*)
    FROM authoring.analysis_nodes n
    JOIN authoring.annotation_layers l USING (annotation_layer_id)
    JOIN authoring.annotation_frameworks f USING (annotation_framework_id)
    WHERE f.framework_key='BHSA_2021_REAL'
      AND n.node_type='WORD'
      AND NOT (n.metadata @> '{"annotationOnly":true}'::jsonb)
      AND (
        SELECT count(*) FROM authoring.analysis_node_segments ns
        WHERE ns.analysis_node_id=n.analysis_node_id
      ) = 1
  ) = 32,
  'all 32 text-bearing BHSA word nodes must map to exactly one source TextSegment'
);

SELECT wb0_test.assert_true(
  NOT EXISTS (
    SELECT 1
    FROM authoring.analysis_nodes n
    JOIN authoring.annotation_layers l USING (annotation_layer_id)
    JOIN authoring.annotation_frameworks f USING (annotation_framework_id)
    WHERE f.framework_key='BHSA_2021_REAL'
      AND n.metadata @> '{"annotationOnly":true}'::jsonb
      AND (
        NOT EXISTS (
          SELECT 1 FROM authoring.analysis_edges e
          WHERE e.from_node_id=n.analysis_node_id AND e.relation_type='MEMBER_OF_PHRASE'
        )
        OR NOT EXISTS (
          SELECT 1 FROM authoring.analysis_edges e
          WHERE e.from_node_id=n.analysis_node_id AND e.relation_type='MEMBER_OF_CLAUSE'
        )
      )
  ),
  'annotation-only BHSA nodes must retain phrase and clause graph membership'
);

SELECT wb0_test.assert_true(
  (
    SELECT count(*) FROM authoring.cross_annotation_mapping_groups
    WHERE mapping_type='ORTHOGRAPHIC_SPAN_CANDIDATE'
  ) = 25,
  'pinned WB-0 crosswalk must load 25 grouped candidate mappings'
);

SELECT wb0_test.assert_true(
  NOT EXISTS (
    SELECT 1 FROM authoring.cross_annotation_mapping_groups
    WHERE canonical OR review_status <> 'CANDIDATE_AUTOMATED'
  ),
  'automatic WB-0 mapping groups must remain non-canonical candidates'
);

SELECT wb0_test.assert_true(
  EXISTS (
    SELECT 1
    FROM authoring.cross_annotation_mapping_groups g
    WHERE
      (SELECT count(*) FROM authoring.cross_annotation_mapping_from_members fm
       WHERE fm.mapping_group_id=g.mapping_group_id) > 1
      OR
      (SELECT count(*) FROM authoring.cross_annotation_mapping_to_members tm
       WHERE tm.mapping_group_id=g.mapping_group_id) > 1
  ),
  'real WB-0 evidence must exercise at least one non-1:1 mapping group'
);

SELECT wb0_test.assert_true(
  NOT EXISTS (
    SELECT 1
    FROM authoring.cross_annotation_mapping_to_members tm
    JOIN authoring.analysis_nodes n ON n.analysis_node_id=tm.to_node_id
    WHERE n.metadata @> '{"annotationOnly":true}'::jsonb
  ),
  'annotation-only BHSA nodes must be excluded from orthographic crosswalk membership'
);

SELECT wb0_test.assert_true(
  (SELECT count(*) FROM authoring.cross_annotation_mappings) = 0,
  'automatic n:m candidates must not be decomposed into false pairwise equivalence rows'
);

SELECT wb0_test.assert_true(
  EXISTS (
    SELECT 1
    FROM authoring.analysis_node_features f
    WHERE f.feature_key IN ('BRIDGE_OSM_PRIMARY_RAW','BRIDGE_OSM_SECONDARY_RAW')
  ),
  'pinned ETCBC bridging comparison values must be preserved where available'
);

SELECT wb0_test.assert_true(
  EXISTS (
    SELECT 1
    FROM authoring.semantic_set_members sm
    JOIN authoring.semantic_set_versions sv USING (semantic_set_version_id)
    JOIN authoring.semantic_sets s USING (semantic_set_id)
    WHERE s.name='BODY_PART' AND sm.member_key='עין' AND sm.review_status='HUMAN_REVIEWED'
  ),
  'project BODY_PART authority must remain distinct and present'
);

-- Real multi-layer query canary:
-- BHSA BODY_PART target -> explicit grouped mapping -> OSHB morphology source,
-- while the BHSA target is also a member of a BHSA clause.
SELECT wb0_test.assert_true(
  EXISTS (
    SELECT 1
    FROM authoring.cross_annotation_mapping_groups g
    JOIN authoring.cross_annotation_mapping_from_members fm
      ON fm.mapping_group_id=g.mapping_group_id
    JOIN authoring.analysis_node_features source_morph
      ON source_morph.analysis_node_id=fm.from_node_id
     AND source_morph.feature_key='MORPH_RAW'
    JOIN authoring.cross_annotation_mapping_to_members tm
      ON tm.mapping_group_id=g.mapping_group_id
    JOIN authoring.analysis_node_features target_lexeme
      ON target_lexeme.analysis_node_id=tm.to_node_id
     AND target_lexeme.feature_key='HEBREW_LEXEME_LETTERS_V1'
    JOIN authoring.semantic_set_members sm
      ON sm.member_key=target_lexeme.feature_value
     AND sm.member_object_type='LEXEME'
     AND sm.inclusion_type='INCLUDE'
    JOIN authoring.semantic_set_versions sv
      ON sv.semantic_set_version_id=sm.semantic_set_version_id
    JOIN authoring.semantic_sets s
      ON s.semantic_set_id=sv.semantic_set_id AND s.name='BODY_PART'
    JOIN authoring.analysis_edges e
      ON e.from_node_id=tm.to_node_id AND e.relation_type='MEMBER_OF_CLAUSE'
    WHERE g.review_status='CANDIDATE_AUTOMATED' AND NOT g.canonical
  ),
  'WB-0 must be able to join OSHB morphology to a BHSA BODY_PART/clause target only through explicit mapping evidence'
);

-- Composite FKs must reject a source-layer node pretending to be a target-layer member.
DO $wrong_mapping_layer$
DECLARE
  g_id uuid;
  target_layer uuid;
  source_node uuid;
  failed boolean := false;
BEGIN
  SELECT g.mapping_group_id, g.to_annotation_layer_id, fm.from_node_id
    INTO g_id, target_layer, source_node
  FROM authoring.cross_annotation_mapping_groups g
  JOIN authoring.cross_annotation_mapping_from_members fm USING (mapping_group_id)
  LIMIT 1;

  BEGIN
    INSERT INTO authoring.cross_annotation_mapping_to_members(
      mapping_group_id,to_annotation_layer_id,to_node_id,member_order
    ) VALUES (g_id,target_layer,source_node,999);
  EXCEPTION
    WHEN foreign_key_violation THEN
      failed := true;
    WHEN raise_exception THEN
      IF SQLERRM <> 'cross-annotation mapping member must share the mapping-group reference span' THEN
        RAISE;
      END IF;
      failed := true;
  END;

  IF NOT failed THEN
    RAISE EXCEPTION 'cross-annotation target member from the source layer must fail';
  END IF;
END
$wrong_mapping_layer$;

-- Candidate state itself is fail-closed against accidental canonical promotion.
DO $candidate_promotion$
DECLARE
  g_id uuid;
  failed boolean := false;
BEGIN
  SELECT mapping_group_id INTO g_id
  FROM authoring.cross_annotation_mapping_groups
  WHERE review_status='CANDIDATE_AUTOMATED'
  LIMIT 1;

  BEGIN
    UPDATE authoring.cross_annotation_mapping_groups
    SET canonical=true
    WHERE mapping_group_id=g_id;
  EXCEPTION WHEN check_violation THEN
    failed := true;
  END;

  IF NOT failed THEN
    RAISE EXCEPTION 'CANDIDATE_AUTOMATED mapping must not become canonical without reviewed state';
  END IF;
END
$candidate_promotion$;

-- Rights boundary: WB-0 imports BHSA/bridging only into Authoring. No public
-- Serving corpus projection is written by the canary loader.
SELECT wb0_test.assert_true(
  (SELECT count(*) FROM serving.corpus_nodes) = 0,
  'WB-0 real corpus canary must not publish BHSA/bridging-derived data to Serving'
);

DROP SCHEMA wb0_test CASCADE;
