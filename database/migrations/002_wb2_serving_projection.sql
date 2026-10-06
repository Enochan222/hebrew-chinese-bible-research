\set ON_ERROR_STOP on

BEGIN;

-- WB-2 aligns the database rights-obligation validator with the canonical
-- RightsDecisionSnapshot JSON Schema. Migration 001 still recognized an older
-- "type" key; the contract uses "obligationType".
CREATE OR REPLACE FUNCTION serving.valid_rights_obligations(value jsonb)
RETURNS boolean
LANGUAGE plpgsql
IMMUTABLE
AS $rights_obligations_v11$
DECLARE
  obligation jsonb;
  obligation_type text;
  key_name text;
BEGIN
  IF value IS NULL THEN
    RETURN true;
  END IF;
  IF jsonb_typeof(value) <> 'array' THEN
    RETURN false;
  END IF;

  FOR obligation IN SELECT * FROM jsonb_array_elements(value)
  LOOP
    IF jsonb_typeof(obligation) <> 'object' THEN
      RETURN false;
    END IF;
    obligation_type := obligation->>'obligationType';
    IF obligation_type NOT IN (
      'ATTRIBUTION','MAX_EXCERPT','RETENTION_LIMIT',
      'AUTHENTICATED_ONLY','TERRITORY_LIMIT','TEMPORARY_PROCESSING_ONLY'
    ) THEN
      RETURN false;
    END IF;

    IF obligation_type = 'ATTRIBUTION' THEN
      IF jsonb_typeof(obligation->'value') <> 'string'
         OR length(COALESCE(obligation->>'value','')) = 0 THEN
        RETURN false;
      END IF;
      FOR key_name IN SELECT jsonb_object_keys(obligation)
      LOOP
        IF key_name NOT IN ('obligationType','value') THEN RETURN false; END IF;
      END LOOP;

    ELSIF obligation_type = 'MAX_EXCERPT' THEN
      IF jsonb_typeof(obligation->'value') <> 'number'
         OR (obligation->>'value')::numeric <= 0
         OR COALESCE(obligation->>'unit','') NOT IN (
           'WORD','UNICODE_CODEPOINT','GRAPHEME_CLUSTER','BYTE','PERCENT_OF_WORK'
         ) THEN
        RETURN false;
      END IF;
      FOR key_name IN SELECT jsonb_object_keys(obligation)
      LOOP
        IF key_name NOT IN ('obligationType','value','unit') THEN RETURN false; END IF;
      END LOOP;

    ELSIF obligation_type = 'RETENTION_LIMIT' THEN
      IF jsonb_typeof(obligation->'value') <> 'number'
         OR NOT ((obligation->>'value') ~ '^[0-9]+$')
         OR (obligation->>'value')::numeric < 0
         OR obligation->>'unit' <> 'DAY' THEN
        RETURN false;
      END IF;
      FOR key_name IN SELECT jsonb_object_keys(obligation)
      LOOP
        IF key_name NOT IN ('obligationType','value','unit') THEN RETURN false; END IF;
      END LOOP;

    ELSIF obligation_type = 'AUTHENTICATED_ONLY' THEN
      FOR key_name IN SELECT jsonb_object_keys(obligation)
      LOOP
        IF key_name <> 'obligationType' THEN RETURN false; END IF;
      END LOOP;

    ELSIF obligation_type = 'TERRITORY_LIMIT' THEN
      IF jsonb_typeof(obligation->'value') <> 'array'
         OR jsonb_array_length(obligation->'value') = 0
         OR EXISTS (
           SELECT 1
           FROM jsonb_array_elements(obligation->'value') territory
           WHERE jsonb_typeof(territory) <> 'string'
              OR length(trim(both '"' from territory::text)) < 2
         ) THEN
        RETURN false;
      END IF;
      FOR key_name IN SELECT jsonb_object_keys(obligation)
      LOOP
        IF key_name NOT IN ('obligationType','value') THEN RETURN false; END IF;
      END LOOP;

    ELSIF obligation_type = 'TEMPORARY_PROCESSING_ONLY' THEN
      FOR key_name IN SELECT jsonb_object_keys(obligation)
      LOOP
        IF key_name <> 'obligationType' THEN RETURN false; END IF;
      END LOOP;
    END IF;
  END LOOP;

  RETURN true;
END
$rights_obligations_v11$;

CREATE TABLE serving.corpus_projection_rights (
  corpus_release_id uuid NOT NULL REFERENCES serving.research_objects(research_object_id),
  operation text NOT NULL CHECK (operation IN ('STORE_EXTRACTED_TEXT','DISPLAY_FULLTEXT')),
  rights_decision_snapshot_id uuid NOT NULL REFERENCES serving.rights_decision_snapshots(rights_decision_snapshot_id),
  PRIMARY KEY (corpus_release_id, operation),
  UNIQUE (rights_decision_snapshot_id)
);

CREATE TABLE serving.corpus_attributions (
  corpus_release_id uuid NOT NULL REFERENCES serving.research_objects(research_object_id),
  source_key text NOT NULL,
  attribution_text text NOT NULL CHECK (length(attribution_text) > 0),
  license_label text NOT NULL CHECK (length(license_label) > 0),
  PRIMARY KEY (corpus_release_id, source_key)
);

CREATE TABLE serving.corpus_text_segments (
  corpus_release_id uuid NOT NULL REFERENCES serving.research_objects(research_object_id),
  text_segment_id uuid NOT NULL,
  reference_span_id uuid NOT NULL REFERENCES serving.reference_spans(reference_span_id),
  segment_order integer NOT NULL,
  source_key text NOT NULL,
  surface_original text NOT NULL CHECK (length(surface_original) > 0),
  segment_kind text NOT NULL,
  content_hash text NOT NULL CHECK (content_hash ~ '^[0-9a-fA-F]{64}$'),
  storage_rights_decision_snapshot_id uuid NOT NULL REFERENCES serving.rights_decision_snapshots(rights_decision_snapshot_id),
  display_rights_decision_snapshot_id uuid NOT NULL REFERENCES serving.rights_decision_snapshots(rights_decision_snapshot_id),
  PRIMARY KEY (corpus_release_id, text_segment_id),
  UNIQUE (corpus_release_id, segment_order)
);

CREATE TABLE serving.corpus_node_segments (
  corpus_release_id uuid NOT NULL,
  analysis_node_id uuid NOT NULL,
  text_segment_id uuid NOT NULL,
  member_order integer NOT NULL CHECK (member_order >= 0),
  membership_role text,
  PRIMARY KEY (corpus_release_id, analysis_node_id, member_order),
  UNIQUE (corpus_release_id, analysis_node_id, text_segment_id),
  FOREIGN KEY (corpus_release_id, analysis_node_id)
    REFERENCES serving.corpus_nodes(corpus_release_id, analysis_node_id) ON DELETE CASCADE,
  FOREIGN KEY (corpus_release_id, text_segment_id)
    REFERENCES serving.corpus_text_segments(corpus_release_id, text_segment_id) ON DELETE CASCADE
);

CREATE TABLE serving.passage_reference_index (
  corpus_release_id uuid NOT NULL REFERENCES serving.research_objects(research_object_id),
  reference_system_id uuid NOT NULL,
  reference_system_code text NOT NULL,
  reference_label text NOT NULL,
  reference_span_id uuid NOT NULL REFERENCES serving.reference_spans(reference_span_id),
  book_code text NOT NULL,
  chapter_number integer,
  verse_label text,
  reference_sort_key bigint NOT NULL,
  PRIMARY KEY (corpus_release_id, reference_system_code, reference_label),
  UNIQUE (corpus_release_id, reference_system_id, reference_label)
);

CREATE INDEX serving_corpus_text_segments_span_idx
  ON serving.corpus_text_segments(corpus_release_id, reference_span_id, segment_order);
CREATE INDEX serving_corpus_node_segments_segment_idx
  ON serving.corpus_node_segments(corpus_release_id, text_segment_id);
CREATE INDEX serving_passage_reference_index_span_idx
  ON serving.passage_reference_index(corpus_release_id, reference_span_id);
CREATE INDEX serving_passage_reference_index_sort_idx
  ON serving.passage_reference_index(corpus_release_id, reference_sort_key);

CREATE OR REPLACE FUNCTION serving.validate_corpus_projection_rights_binding()
RETURNS trigger
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = pg_catalog, serving
AS $wb2_projection_rights$
DECLARE
  snap serving.rights_decision_snapshots%ROWTYPE;
BEGIN
  SELECT * INTO snap
  FROM serving.rights_decision_snapshots
  WHERE rights_decision_snapshot_id = NEW.rights_decision_snapshot_id;

  IF snap.rights_decision_snapshot_id IS NULL
     OR snap.subject_type <> 'CORPUS_RELEASE'
     OR snap.subject_identifier <> NEW.corpus_release_id
     OR snap.operation <> NEW.operation
     OR snap.decision NOT IN ('ALLOW','CONDITIONAL')
     OR snap.commercial_context <> 'COMMERCIAL' THEN
    RAISE EXCEPTION 'rights snapshot is incompatible with corpus Serving projection';
  END IF;

  IF NEW.operation = 'STORE_EXTRACTED_TEXT'
     AND (snap.purpose_scope <> 'PUBLICATION' OR snap.audience_scope <> 'INTERNAL_SERVICE') THEN
    RAISE EXCEPTION 'storage rights snapshot has incompatible scope';
  END IF;

  IF NEW.operation = 'DISPLAY_FULLTEXT'
     AND (snap.purpose_scope <> 'PUBLIC_DISPLAY' OR snap.audience_scope <> 'PUBLIC') THEN
    RAISE EXCEPTION 'display rights snapshot has incompatible scope';
  END IF;

  RETURN NEW;
END
$wb2_projection_rights$;

CREATE TRIGGER corpus_projection_rights_compatibility
BEFORE INSERT OR UPDATE ON serving.corpus_projection_rights
FOR EACH ROW EXECUTE FUNCTION serving.validate_corpus_projection_rights_binding();

CREATE OR REPLACE FUNCTION serving.validate_corpus_text_segment_rights()
RETURNS trigger
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = pg_catalog, serving
AS $wb2_segment_rights$
DECLARE
  expected_storage uuid;
  expected_display uuid;
  display_snap serving.rights_decision_snapshots%ROWTYPE;
BEGIN
  SELECT rights_decision_snapshot_id INTO expected_storage
  FROM serving.corpus_projection_rights
  WHERE corpus_release_id = NEW.corpus_release_id
    AND operation = 'STORE_EXTRACTED_TEXT';

  SELECT rights_decision_snapshot_id INTO expected_display
  FROM serving.corpus_projection_rights
  WHERE corpus_release_id = NEW.corpus_release_id
    AND operation = 'DISPLAY_FULLTEXT';

  IF expected_storage IS NULL OR expected_storage <> NEW.storage_rights_decision_snapshot_id THEN
    RAISE EXCEPTION 'corpus text segment lacks matching storage RightsDecision';
  END IF;
  IF expected_display IS NULL OR expected_display <> NEW.display_rights_decision_snapshot_id THEN
    RAISE EXCEPTION 'corpus text segment lacks matching display RightsDecision';
  END IF;

  SELECT * INTO display_snap
  FROM serving.rights_decision_snapshots
  WHERE rights_decision_snapshot_id = expected_display;

  IF EXISTS (
    SELECT 1
    FROM jsonb_array_elements(display_snap.obligations_json) obligation
    WHERE obligation->>'obligationType' = 'ATTRIBUTION'
  ) AND NOT EXISTS (
    SELECT 1
    FROM serving.corpus_attributions attribution,
         jsonb_array_elements(display_snap.obligations_json) obligation
    WHERE attribution.corpus_release_id = NEW.corpus_release_id
      AND obligation->>'obligationType' = 'ATTRIBUTION'
      AND attribution.attribution_text = obligation->>'value'
  ) THEN
    RAISE EXCEPTION 'corpus text segment attribution obligation is not materialized';
  END IF;

  RETURN NEW;
END
$wb2_segment_rights$;

CREATE TRIGGER corpus_text_segment_rights
BEFORE INSERT OR UPDATE ON serving.corpus_text_segments
FOR EACH ROW EXECUTE FUNCTION serving.validate_corpus_text_segment_rights();

CREATE TRIGGER corpus_projection_rights_component_lock
BEFORE INSERT OR UPDATE OR DELETE ON serving.corpus_projection_rights
FOR EACH ROW EXECUTE FUNCTION serving.guard_component_projection('corpus_release_id');

CREATE TRIGGER corpus_attributions_component_lock
BEFORE INSERT OR UPDATE OR DELETE ON serving.corpus_attributions
FOR EACH ROW EXECUTE FUNCTION serving.guard_component_projection('corpus_release_id');

CREATE TRIGGER corpus_text_segments_component_lock
BEFORE INSERT OR UPDATE OR DELETE ON serving.corpus_text_segments
FOR EACH ROW EXECUTE FUNCTION serving.guard_component_projection('corpus_release_id');

CREATE TRIGGER corpus_node_segments_component_lock
BEFORE INSERT OR UPDATE OR DELETE ON serving.corpus_node_segments
FOR EACH ROW EXECUTE FUNCTION serving.guard_component_projection('corpus_release_id');

CREATE TRIGGER passage_reference_index_component_lock
BEFORE INSERT OR UPDATE OR DELETE ON serving.passage_reference_index
FOR EACH ROW EXECUTE FUNCTION serving.guard_component_projection('corpus_release_id');

ALTER TABLE serving.corpus_projection_rights ENABLE ROW LEVEL SECURITY;
ALTER TABLE serving.corpus_attributions ENABLE ROW LEVEL SECURITY;
ALTER TABLE serving.corpus_text_segments ENABLE ROW LEVEL SECURITY;
ALTER TABLE serving.corpus_node_segments ENABLE ROW LEVEL SECURITY;
ALTER TABLE serving.passage_reference_index ENABLE ROW LEVEL SECURITY;

CREATE POLICY public_read_corpus_attributions ON serving.corpus_attributions
FOR SELECT TO anon, authenticated
USING (serving.component_is_published(corpus_release_id));

CREATE POLICY public_read_corpus_text_segments ON serving.corpus_text_segments
FOR SELECT TO anon, authenticated
USING (serving.component_is_published(corpus_release_id));

CREATE POLICY public_read_corpus_node_segments ON serving.corpus_node_segments
FOR SELECT TO anon, authenticated
USING (serving.component_is_published(corpus_release_id));

CREATE POLICY public_read_passage_reference_index ON serving.passage_reference_index
FOR SELECT TO anon, authenticated
USING (serving.component_is_published(corpus_release_id));

CREATE OR REPLACE FUNCTION serving.get_passage_core(
  p_release_id uuid,
  p_reference_system_code text,
  p_reference_label text
)
RETURNS jsonb
LANGUAGE sql
STABLE
SECURITY INVOKER
AS $wb2_get_passage_core$
  WITH resolved AS (
    SELECT c.component_order,
           i.corpus_release_id,
           i.reference_system_id,
           i.reference_system_code,
           i.reference_label,
           i.reference_span_id,
           i.book_code,
           i.reference_sort_key
    FROM serving.research_release_components c
    JOIN serving.passage_reference_index i
      ON i.corpus_release_id = c.component_research_object_id
    WHERE c.research_release_id = p_release_id
      AND c.component_kind = 'CORPUS'
      AND i.reference_system_code = p_reference_system_code
      AND i.reference_label = p_reference_label
    ORDER BY c.component_order
    LIMIT 1
  ),
  resolved_span AS (
    SELECT r.*, rs.start_sequence, rs.end_sequence
    FROM resolved r
    JOIN serving.reference_spans rs USING (reference_span_id)
  ),
  segment_payload AS (
    SELECT r.corpus_release_id,
           jsonb_agg(
             jsonb_build_object(
               'textSegmentId', s.text_segment_id::text,
               'sourceKey', s.source_key,
               'surfaceOriginal', s.surface_original,
               'segmentKind', s.segment_kind,
               'contentHash', s.content_hash
             )
             ORDER BY s.segment_order, s.text_segment_id
           ) AS segments
    FROM resolved_span r
    JOIN serving.corpus_text_segments s
      ON s.corpus_release_id = r.corpus_release_id
    JOIN serving.reference_spans segment_span
      ON segment_span.reference_span_id = s.reference_span_id
     AND segment_span.book_code = r.book_code
     AND segment_span.start_sequence >= r.start_sequence
     AND segment_span.end_sequence <= r.end_sequence
    GROUP BY r.corpus_release_id
  ),
  attribution_payload AS (
    SELECT r.corpus_release_id,
           jsonb_agg(
             jsonb_build_object(
               'sourceKey', a.source_key,
               'attributionText', a.attribution_text,
               'licenseLabel', a.license_label
             )
             ORDER BY a.source_key
           ) AS attributions
    FROM resolved_span r
    JOIN serving.corpus_attributions a USING (corpus_release_id)
    GROUP BY r.corpus_release_id
  )
  SELECT jsonb_build_object(
    'researchReleaseId', p_release_id::text,
    'referenceSpanId', r.reference_span_id::text,
    'resolvedReference', jsonb_build_object(
      'referenceSystemId', r.reference_system_id::text,
      'referenceSystemCode', r.reference_system_code,
      'referenceLabel', r.reference_label
    ),
    'segments', COALESCE(s.segments, '[]'::jsonb),
    'attributions', COALESCE(a.attributions, '[]'::jsonb)
  )
  FROM resolved_span r
  LEFT JOIN segment_payload s USING (corpus_release_id)
  LEFT JOIN attribution_payload a USING (corpus_release_id)
$wb2_get_passage_core$;

GRANT SELECT ON
  serving.corpus_attributions,
  serving.corpus_text_segments,
  serving.corpus_node_segments,
  serving.passage_reference_index
TO anon, authenticated;

GRANT EXECUTE ON FUNCTION serving.get_passage_core(uuid,text,text)
TO anon, authenticated;

REVOKE ALL ON serving.corpus_projection_rights FROM PUBLIC, anon, authenticated;
REVOKE ALL ON FUNCTION serving.validate_corpus_projection_rights_binding()
  FROM PUBLIC, anon, authenticated;
REVOKE ALL ON FUNCTION serving.validate_corpus_text_segment_rights()
  FROM PUBLIC, anon, authenticated;

GRANT EXECUTE ON FUNCTION serving.valid_rights_obligations(jsonb)
TO publication_worker;

COMMIT;
