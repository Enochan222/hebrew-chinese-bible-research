-- SEARCH-1 internal PostgreSQL primitive, not a separate public CorpusQuery DSL.
-- Operates only on already-publicly-servable release-pinned OSHB WORD nodes.
-- The production HTTP/MCP surface MUST validate canonical CorpusQuery v1.1 first.
BEGIN;

CREATE OR REPLACE FUNCTION publication_control.oshb_word_proximity_candidates(
  p_release_id uuid,
  p_action_terminal_lemma text,
  p_target_terminal_lemma text,
  p_min_intervening_words integer DEFAULT 0,
  p_max_intervening_words integer DEFAULT 3,
  p_direction text DEFAULT 'ACTION_BEFORE_TARGET',
  p_limit integer DEFAULT 100
)
RETURNS TABLE (
  reference_span_id uuid,
  action_node_id uuid,
  target_node_id uuid,
  action_segment_id uuid,
  target_segment_id uuid,
  action_segment_order bigint,
  target_segment_order bigint,
  intervening_words integer
)
LANGUAGE plpgsql
STABLE
SECURITY INVOKER
SET search_path = pg_catalog, serving
AS $search1_oshb_word_proximity$
BEGIN
  IF p_release_id IS NULL THEN
    RAISE EXCEPTION 'a pinned ResearchRelease is mandatory';
  END IF;
  IF p_action_terminal_lemma IS NULL OR btrim(p_action_terminal_lemma) = ''
     OR length(p_action_terminal_lemma) > 128 OR position('/' in p_action_terminal_lemma) > 0
     OR p_target_terminal_lemma IS NULL OR btrim(p_target_terminal_lemma) = ''
     OR length(p_target_terminal_lemma) > 128 OR position('/' in p_target_terminal_lemma) > 0 THEN
    RAISE EXCEPTION 'search lemma codes must be source-exact terminal OSHB lemma keys';
  END IF;
  IF p_min_intervening_words IS NULL OR p_max_intervening_words IS NULL
     OR p_min_intervening_words < 0
     OR p_max_intervening_words > 100
     OR p_max_intervening_words < p_min_intervening_words THEN
    RAISE EXCEPTION 'invalid intervening word-distance bounds';
  END IF;
  IF p_direction IS NULL OR p_direction NOT IN
    ('ACTION_BEFORE_TARGET','TARGET_BEFORE_ACTION','EITHER') THEN
    RAISE EXCEPTION 'unsupported word-order direction';
  END IF;
  IF p_limit IS NULL OR p_limit NOT BETWEEN 1 AND 500 THEN
    RAISE EXCEPTION 'candidate query limit must be in 1..500';
  END IF;

  RETURN QUERY
    WITH pinned_osHB AS (
      SELECT rc.component_research_object_id AS corpus_release_id
      FROM serving.research_release_components rc
      WHERE rc.research_release_id = p_release_id
        AND rc.component_kind = 'CORPUS'
        AND serving.release_is_publicly_servable(p_release_id)
    ),
    tokens AS (
      SELECT n.corpus_release_id,n.analysis_node_id,n.annotation_layer_id,n.reference_span_id,
             t.text_segment_id,t.segment_order::bigint AS segment_order,
             f_lemma.feature_value AS lemma_raw,
             f_morph.feature_value AS morph_raw
      FROM serving.corpus_nodes n
      JOIN pinned_osHB pin ON pin.corpus_release_id = n.corpus_release_id
      JOIN serving.corpus_node_segments ns
        ON ns.corpus_release_id = n.corpus_release_id
       AND ns.analysis_node_id = n.analysis_node_id
       AND ns.membership_role = 'ORTHOGRAPHIC_WORD'
      JOIN serving.corpus_text_segments t
        ON t.corpus_release_id = ns.corpus_release_id
       AND t.text_segment_id = ns.text_segment_id
       AND t.reference_span_id = n.reference_span_id
       AND t.segment_kind = 'WORD'
      JOIN serving.corpus_node_features f_lemma
        ON f_lemma.corpus_release_id = n.corpus_release_id
       AND f_lemma.analysis_node_id = n.analysis_node_id
       AND f_lemma.feature_key = 'LEMMA_RAW'
      JOIN serving.corpus_node_features f_morph
        ON f_morph.corpus_release_id = n.corpus_release_id
       AND f_morph.analysis_node_id = n.analysis_node_id
       AND f_morph.feature_key = 'MORPH_RAW'
      WHERE n.node_type = 'WORD'
        AND EXISTS (
          SELECT 1 FROM serving.corpus_node_features src
          WHERE src.corpus_release_id = n.corpus_release_id
            AND src.analysis_node_id = n.analysis_node_id
            AND src.feature_key = 'SOURCE_KEY'
            AND src.feature_value = 'OSHB_MORPHHB'
        )
    ),
    actions AS (
      SELECT * FROM tokens t
      WHERE regexp_replace(t.lemma_raw, '^.*/', '') = p_action_terminal_lemma
        AND t.morph_raw ~ '(^|/)(H?V)'
    ),
    targets AS (
      SELECT * FROM tokens t
      WHERE regexp_replace(t.lemma_raw, '^.*/', '') = p_target_terminal_lemma
        AND position('/l/' in '/' || t.lemma_raw || '/') > 0
    )
    SELECT a.reference_span_id,
           a.analysis_node_id, b.analysis_node_id,
           a.text_segment_id, b.text_segment_id,
           a.segment_order, b.segment_order,
           (abs(a.segment_order-b.segment_order)-1)::integer
    FROM actions a
    JOIN targets b
      ON b.corpus_release_id = a.corpus_release_id
     AND b.annotation_layer_id = a.annotation_layer_id
     AND b.reference_span_id = a.reference_span_id
     AND b.analysis_node_id <> a.analysis_node_id
     AND b.text_segment_id <> a.text_segment_id
    JOIN serving.reference_spans rs
      ON rs.reference_span_id = a.reference_span_id
    WHERE (abs(a.segment_order-b.segment_order)-1)
              BETWEEN p_min_intervening_words AND p_max_intervening_words
      AND (
        p_direction = 'EITHER'
        OR (p_direction='ACTION_BEFORE_TARGET' AND a.segment_order < b.segment_order)
        OR (p_direction='TARGET_BEFORE_ACTION' AND a.segment_order > b.segment_order)
      )
    ORDER BY rs.reference_sort_key,a.segment_order,b.segment_order,a.analysis_node_id,b.analysis_node_id
    LIMIT p_limit;
END
$search1_oshb_word_proximity$;

-- No direct public execution: the future CorpusQuery validator/compiler is the only product entry.
REVOKE ALL ON FUNCTION publication_control.oshb_word_proximity_candidates(
  uuid,text,text,integer,integer,text,integer
) FROM PUBLIC, anon, authenticated;
COMMIT;
