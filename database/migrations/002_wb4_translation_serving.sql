\set ON_ERROR_STOP on

BEGIN;

-- WB-4 DB-1 provider identity remains distinct from textual identity.
CREATE TABLE authoring.providers (
  provider_id uuid PRIMARY KEY,
  provider_key text NOT NULL UNIQUE,
  name text NOT NULL,
  provider_type text NOT NULL,
  base_url text,
  active boolean NOT NULL DEFAULT true,
  metadata jsonb NOT NULL DEFAULT '{}'::jsonb
);

CREATE TABLE authoring.provider_distributions (
  provider_distribution_id uuid PRIMARY KEY,
  provider_id uuid NOT NULL REFERENCES authoring.providers(provider_id),
  digital_expression_id uuid NOT NULL REFERENCES authoring.digital_expressions(digital_expression_id),
  provider_version_code text NOT NULL,
  distribution_version text,
  availability_metadata jsonb NOT NULL DEFAULT '{}'::jsonb,
  rights_policy_id uuid REFERENCES authoring.rights_policies(rights_policy_id),
  active boolean NOT NULL DEFAULT true,
  UNIQUE (provider_id, provider_version_code),
  UNIQUE (provider_distribution_id, digital_expression_id)
);

CREATE TABLE authoring.translation_witness_coverage (
  provider_distribution_id uuid NOT NULL REFERENCES authoring.provider_distributions(provider_distribution_id),
  reference_span_id uuid NOT NULL REFERENCES authoring.reference_spans(reference_span_id),
  coverage_status text NOT NULL CHECK (coverage_status IN ('COVERED','NOT_COVERED','UNKNOWN')),
  PRIMARY KEY (provider_distribution_id, reference_span_id)
);

CREATE TABLE authoring.provider_witness_observations (
  provider_distribution_id uuid NOT NULL REFERENCES authoring.provider_distributions(provider_distribution_id),
  reference_span_id uuid NOT NULL REFERENCES authoring.reference_spans(reference_span_id),
  text_stream_id uuid REFERENCES authoring.text_streams(text_stream_id),
  binding_mode text NOT NULL CHECK (binding_mode IN ('SNAPSHOT_PINNED','LIVE_EXTERNAL')),
  segment_storage_mode text NOT NULL CHECK (segment_storage_mode IN ('PERSISTED_CONTENT','PROVIDER_LOCATOR','EPHEMERAL')),
  provider_reference text NOT NULL,
  provider_segment_key text,
  provider_version text,
  observed_hash text NOT NULL CHECK (observed_hash ~ '^[0-9a-fA-F]{64}$'),
  observed_at timestamptz NOT NULL,
  snapshot_content_hash text CHECK (snapshot_content_hash IS NULL OR snapshot_content_hash ~ '^[0-9a-fA-F]{64}$'),
  delivery_status text NOT NULL CHECK (delivery_status IN ('READY','PROVIDER_ERROR','STALE','NOT_RETRIEVED')),
  PRIMARY KEY (provider_distribution_id, reference_span_id),
  CHECK (
    (binding_mode='SNAPSHOT_PINNED'
      AND segment_storage_mode='PERSISTED_CONTENT'
      AND text_stream_id IS NOT NULL
      AND snapshot_content_hash IS NOT NULL)
    OR
    (binding_mode='LIVE_EXTERNAL'
      AND segment_storage_mode IN ('PROVIDER_LOCATOR','EPHEMERAL')
      AND snapshot_content_hash IS NULL)
  )
);

CREATE OR REPLACE FUNCTION authoring.validate_provider_observation_expression()
RETURNS trigger
LANGUAGE plpgsql
AS $wb4_provider_observation_expression$
DECLARE
  distribution_expression uuid;
  stream_expression uuid;
BEGIN
  SELECT digital_expression_id INTO distribution_expression
  FROM authoring.provider_distributions
  WHERE provider_distribution_id=NEW.provider_distribution_id;

  IF NEW.text_stream_id IS NOT NULL THEN
    SELECT digital_expression_id INTO stream_expression
    FROM authoring.text_streams
    WHERE text_stream_id=NEW.text_stream_id;

    IF stream_expression IS NULL OR stream_expression <> distribution_expression THEN
      RAISE EXCEPTION 'provider observation text stream must belong to provider distribution DigitalExpression';
    END IF;
  END IF;
  RETURN NEW;
END
$wb4_provider_observation_expression$;

CREATE TRIGGER provider_observation_expression_guard
BEFORE INSERT OR UPDATE ON authoring.provider_witness_observations
FOR EACH ROW EXECUTE FUNCTION authoring.validate_provider_observation_expression();

-- Serving is release-compiled and has no runtime FK/dependency on Authoring.
CREATE TABLE serving.translation_witnesses (
  research_release_id uuid NOT NULL REFERENCES serving.research_releases(research_release_id),
  reference_span_id uuid NOT NULL REFERENCES serving.reference_spans(reference_span_id),
  textual_work_id uuid NOT NULL,
  textual_edition_id uuid,
  digital_expression_id uuid NOT NULL,
  display_name text NOT NULL CHECK (length(display_name)>0),
  language_tag text NOT NULL CHECK (length(language_tag)>=2),
  coverage_status text NOT NULL CHECK (coverage_status IN ('COVERED','NOT_COVERED','UNKNOWN')),
  delivery_status text NOT NULL CHECK (delivery_status IN ('READY','PROVIDER_ERROR','STALE','NOT_RETRIEVED')),
  display_status text NOT NULL CHECK (display_status IN ('DISPLAYABLE','RIGHTS_RESTRICTED','METADATA_ONLY')),
  provider_distribution_id uuid NOT NULL,
  binding_mode text NOT NULL CHECK (binding_mode IN ('SNAPSHOT_PINNED','LIVE_EXTERNAL')),
  segment_storage_mode text NOT NULL CHECK (segment_storage_mode IN ('PERSISTED_CONTENT','PROVIDER_LOCATOR','EPHEMERAL')),
  provider_reference text NOT NULL,
  provider_segment_key text,
  provider_version text,
  observed_hash text NOT NULL CHECK (observed_hash ~ '^[0-9a-fA-F]{64}$'),
  observed_at timestamptz NOT NULL,
  snapshot_content_hash text CHECK (snapshot_content_hash IS NULL OR snapshot_content_hash ~ '^[0-9a-fA-F]{64}$'),
  display_rights_decision_snapshot_id uuid NOT NULL REFERENCES serving.rights_decision_snapshots(rights_decision_snapshot_id),
  storage_rights_decision_snapshot_id uuid REFERENCES serving.rights_decision_snapshots(rights_decision_snapshot_id),
  provenance_id uuid NOT NULL,
  attribution text,
  witness_order integer NOT NULL CHECK (witness_order >= 0),
  PRIMARY KEY (research_release_id, reference_span_id, digital_expression_id),
  UNIQUE (research_release_id, reference_span_id, witness_order),
  CHECK (
    (display_status='DISPLAYABLE'
      AND coverage_status='COVERED'
      AND delivery_status='READY'
      AND binding_mode='SNAPSHOT_PINNED'
      AND segment_storage_mode='PERSISTED_CONTENT'
      AND snapshot_content_hash IS NOT NULL
      AND storage_rights_decision_snapshot_id IS NOT NULL)
    OR display_status <> 'DISPLAYABLE'
  )
);

CREATE TABLE serving.translation_witness_segments (
  research_release_id uuid NOT NULL,
  reference_span_id uuid NOT NULL,
  digital_expression_id uuid NOT NULL,
  text_segment_id uuid NOT NULL,
  text_stream_id uuid NOT NULL,
  segment_order integer NOT NULL CHECK (segment_order >= 0),
  segment_kind text NOT NULL,
  text_content text NOT NULL CHECK (length(text_content)>0),
  content_hash text NOT NULL CHECK (content_hash ~ '^[0-9a-fA-F]{64}$'),
  PRIMARY KEY (research_release_id, reference_span_id, digital_expression_id, segment_order),
  UNIQUE (research_release_id, text_segment_id),
  FOREIGN KEY (research_release_id,reference_span_id,digital_expression_id)
    REFERENCES serving.translation_witnesses(research_release_id,reference_span_id,digital_expression_id)
    ON DELETE CASCADE
);

CREATE INDEX translation_witnesses_release_span_idx
  ON serving.translation_witnesses(research_release_id, reference_span_id, witness_order);
CREATE INDEX translation_witness_segments_lookup_idx
  ON serving.translation_witness_segments(research_release_id, reference_span_id, digital_expression_id, segment_order);

CREATE OR REPLACE FUNCTION serving.validate_translation_witness_segment_insert()
RETURNS trigger
LANGUAGE plpgsql
AS $wb4_translation_segment_guard$
DECLARE
  status text;
BEGIN
  SELECT display_status INTO status
  FROM serving.translation_witnesses
  WHERE research_release_id=NEW.research_release_id
    AND reference_span_id=NEW.reference_span_id
    AND digital_expression_id=NEW.digital_expression_id;

  IF status IS DISTINCT FROM 'DISPLAYABLE' THEN
    RAISE EXCEPTION 'translation text segments may exist only for DISPLAYABLE witnesses';
  END IF;
  RETURN NEW;
END
$wb4_translation_segment_guard$;

CREATE TRIGGER translation_witness_segment_display_guard
BEFORE INSERT OR UPDATE ON serving.translation_witness_segments
FOR EACH ROW EXECUTE FUNCTION serving.validate_translation_witness_segment_insert();

CREATE TRIGGER translation_witness_release_lock
BEFORE INSERT OR UPDATE OR DELETE ON serving.translation_witnesses
FOR EACH ROW EXECUTE FUNCTION serving.guard_direct_release_payload();

CREATE TRIGGER translation_witness_segment_release_lock
BEFORE INSERT OR UPDATE OR DELETE ON serving.translation_witness_segments
FOR EACH ROW EXECUTE FUNCTION serving.guard_direct_release_payload();

ALTER TABLE serving.translation_witnesses ENABLE ROW LEVEL SECURITY;
ALTER TABLE serving.translation_witness_segments ENABLE ROW LEVEL SECURITY;
ALTER TABLE serving.translation_witnesses FORCE ROW LEVEL SECURITY;
ALTER TABLE serving.translation_witness_segments FORCE ROW LEVEL SECURITY;

CREATE POLICY public_read_translation_witnesses ON serving.translation_witnesses
FOR SELECT TO anon, authenticated
USING (serving.release_is_publicly_servable(research_release_id));

CREATE POLICY public_read_translation_witness_segments ON serving.translation_witness_segments
FOR SELECT TO anon, authenticated
USING (serving.release_is_publicly_servable(research_release_id));

GRANT SELECT ON serving.translation_witnesses, serving.translation_witness_segments
TO anon, authenticated;

CREATE OR REPLACE FUNCTION publication_control.materialize_translation_witness_candidate(
  p_release_id uuid,
  p_reference_span_id uuid,
  p_provider_distribution_id uuid,
  p_display_rights_snapshot_id uuid,
  p_storage_rights_snapshot_id uuid,
  p_display_name text,
  p_language_tag text,
  p_attribution text,
  p_provenance_id uuid,
  p_witness_order integer DEFAULT 0
)
RETURNS void
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = pg_catalog, authoring, serving
AS $wb4_materialize_translation_witness$
DECLARE
  dist authoring.provider_distributions%ROWTYPE;
  expr authoring.digital_expressions%ROWTYPE;
  work authoring.textual_works%ROWTYPE;
  coverage text;
  obs authoring.provider_witness_observations%ROWTYPE;
  display_snap serving.rights_decision_snapshots%ROWTYPE;
  storage_snap serving.rights_decision_snapshots%ROWTYPE;
  computed_status text;
  segment_count integer;
  seq integer := 0;
  seg record;
BEGIN
  IF serving.release_ever_published(p_release_id) THEN
    RAISE EXCEPTION 'translation witness candidate must be materialized before first PUBLISHED';
  END IF;

  SELECT * INTO dist
  FROM authoring.provider_distributions
  WHERE provider_distribution_id=p_provider_distribution_id;
  IF dist.provider_distribution_id IS NULL THEN
    RAISE EXCEPTION 'provider distribution does not exist';
  END IF;

  SELECT * INTO expr
  FROM authoring.digital_expressions
  WHERE digital_expression_id=dist.digital_expression_id;
  SELECT * INTO work
  FROM authoring.textual_works
  WHERE textual_work_id=expr.textual_work_id;

  SELECT coverage_status INTO coverage
  FROM authoring.translation_witness_coverage
  WHERE provider_distribution_id=p_provider_distribution_id
    AND reference_span_id=p_reference_span_id;
  IF coverage IS NULL THEN
    coverage := 'UNKNOWN';
  END IF;

  SELECT * INTO obs
  FROM authoring.provider_witness_observations
  WHERE provider_distribution_id=p_provider_distribution_id
    AND reference_span_id=p_reference_span_id;

  IF obs.provider_distribution_id IS NULL THEN
    RAISE EXCEPTION 'provider witness observation is required';
  END IF;

  -- Provider rights do not authorize attaching a translation to an arbitrary
  -- ResearchRelease. The release manifest must explicitly pin this exact
  -- DigitalExpression and the passage must resolve in its pinned corpus.
  IF NOT EXISTS (
    SELECT 1
    FROM serving.research_release_components component
    WHERE component.research_release_id=p_release_id
      AND component.component_kind='TRANSLATION_WITNESS'
      AND component.component_research_object_id=expr.digital_expression_id
  ) THEN
    RAISE EXCEPTION 'ResearchRelease lacks the exact translation DigitalExpression component';
  END IF;

  IF NOT EXISTS (
    SELECT 1
    FROM serving.research_release_components corpus_component
    JOIN serving.reference_labels ref
      ON ref.corpus_release_id=corpus_component.component_research_object_id
    WHERE corpus_component.research_release_id=p_release_id
      AND corpus_component.component_kind='CORPUS'
      AND ref.reference_span_id=p_reference_span_id
  ) THEN
    RAISE EXCEPTION 'translation witness reference does not belong to the pinned corpus';
  END IF;

  SELECT * INTO display_snap
  FROM serving.rights_decision_snapshots
  WHERE rights_decision_snapshot_id=p_display_rights_snapshot_id;

  IF display_snap.rights_decision_snapshot_id IS NULL
     OR display_snap.subject_type <> 'DIGITAL_EXPRESSION'
     OR display_snap.subject_identifier <> expr.digital_expression_id
     OR display_snap.operation <> 'DISPLAY_FULLTEXT'
     OR display_snap.purpose_scope <> 'PUBLIC_DISPLAY'
     OR display_snap.audience_scope <> 'PUBLIC'
     OR display_snap.commercial_context NOT IN ('MIXED','COMMERCIAL')
     OR display_snap.decision_basis <> 'RULE' THEN
    RAISE EXCEPTION 'display RightsDecisionSnapshot is incompatible with exact translation DigitalExpression';
  END IF;

  IF display_snap.decision='CONDITIONAL'
     AND COALESCE(jsonb_array_length(display_snap.conditions_json),0)>0 THEN
    RAISE EXCEPTION 'conditional translation display rights contain unresolved conditions';
  END IF;

  IF display_snap.decision='CONDITIONAL'
     AND EXISTS (
       SELECT 1 FROM jsonb_array_elements(display_snap.obligations_json) o
       WHERE o->>'obligationType' <> 'ATTRIBUTION'
          OR COALESCE(o->>'value','') <> COALESCE(p_attribution,'')
     ) THEN
    RAISE EXCEPTION 'translation display rights obligations are not fully materialized';
  END IF;

  computed_status := CASE
    WHEN coverage <> 'COVERED' THEN 'METADATA_ONLY'
    WHEN obs.delivery_status <> 'READY' THEN 'METADATA_ONLY'
    WHEN display_snap.decision='DENY' THEN 'RIGHTS_RESTRICTED'
    WHEN obs.binding_mode <> 'SNAPSHOT_PINNED' THEN 'METADATA_ONLY'
    ELSE 'DISPLAYABLE'
  END;

  IF computed_status='DISPLAYABLE'
     AND NOT EXISTS (
       SELECT 1
       FROM serving.research_release_components component
       WHERE component.research_release_id=p_release_id
         AND component.component_kind='TRANSLATION_WITNESS'
         AND component.component_research_object_id=expr.digital_expression_id
         AND component.content_hash=obs.snapshot_content_hash
     ) THEN
    RAISE EXCEPTION 'translation snapshot hash is not pinned by the ResearchRelease component';
  END IF;

  IF computed_status='DISPLAYABLE' THEN
    SELECT * INTO storage_snap
    FROM serving.rights_decision_snapshots
    WHERE rights_decision_snapshot_id=p_storage_rights_snapshot_id;

    IF storage_snap.rights_decision_snapshot_id IS NULL
       OR storage_snap.subject_type <> 'PROVIDER_DISTRIBUTION'
       OR storage_snap.subject_identifier <> p_provider_distribution_id
       OR storage_snap.operation <> 'STORE_EXTRACTED_TEXT'
       OR storage_snap.purpose_scope <> 'PUBLICATION'
       OR storage_snap.audience_scope <> 'INTERNAL_SERVICE'
       OR storage_snap.commercial_context NOT IN ('MIXED','COMMERCIAL')
       OR storage_snap.decision <> 'ALLOW'
       OR storage_snap.decision_basis <> 'RULE'
       OR COALESCE(jsonb_array_length(storage_snap.conditions_json),0) > 0
       OR COALESCE(jsonb_array_length(storage_snap.obligations_json),0) > 0 THEN
      RAISE EXCEPTION 'storage RightsDecisionSnapshot is incompatible with persisted translation snapshot';
    END IF;
  END IF;

  INSERT INTO serving.translation_witnesses(
    research_release_id,reference_span_id,textual_work_id,textual_edition_id,digital_expression_id,
    display_name,language_tag,coverage_status,delivery_status,display_status,
    provider_distribution_id,binding_mode,segment_storage_mode,provider_reference,
    provider_segment_key,provider_version,observed_hash,observed_at,snapshot_content_hash,
    display_rights_decision_snapshot_id,storage_rights_decision_snapshot_id,
    provenance_id,attribution,witness_order
  ) VALUES (
    p_release_id,p_reference_span_id,expr.textual_work_id,expr.textual_edition_id,expr.digital_expression_id,
    p_display_name,p_language_tag,coverage,obs.delivery_status,computed_status,
    p_provider_distribution_id,obs.binding_mode,obs.segment_storage_mode,obs.provider_reference,
    obs.provider_segment_key,obs.provider_version,obs.observed_hash,obs.observed_at,obs.snapshot_content_hash,
    p_display_rights_snapshot_id,
    CASE WHEN computed_status='DISPLAYABLE' THEN p_storage_rights_snapshot_id ELSE NULL END,
    p_provenance_id,p_attribution,p_witness_order
  );

  IF computed_status='DISPLAYABLE' THEN
    FOR seg IN
      SELECT s.*
      FROM authoring.text_segments s
      WHERE s.text_stream_id=obs.text_stream_id
        AND s.reference_span_id=p_reference_span_id
        AND s.segment_storage_mode='PERSISTED_CONTENT'
      ORDER BY s.segment_order,s.text_segment_id
    LOOP
      IF seg.surface_original IS NULL
         OR seg.content_hash IS NULL
         OR seg.content_hash !~ '^[0-9a-fA-F]{64}

      INSERT INTO serving.translation_witness_segments(
        research_release_id,reference_span_id,digital_expression_id,
        text_segment_id,text_stream_id,segment_order,segment_kind,text_content,content_hash
      ) VALUES (
        p_release_id,p_reference_span_id,expr.digital_expression_id,
        seg.text_segment_id,obs.text_stream_id,seq,seg.segment_kind,seg.surface_original,seg.content_hash
      );
      seq := seq + 1;
    END LOOP;

    SELECT count(*) INTO segment_count
    FROM serving.translation_witness_segments
    WHERE research_release_id=p_release_id
      AND reference_span_id=p_reference_span_id
      AND digital_expression_id=expr.digital_expression_id;

    IF segment_count=0 THEN
      RAISE EXCEPTION 'DISPLAYABLE translation witness requires at least one persisted segment';
    END IF;
  END IF;
END
$wb4_materialize_translation_witness$;

REVOKE ALL ON FUNCTION publication_control.materialize_translation_witness_candidate(
  uuid,uuid,uuid,uuid,uuid,text,text,text,uuid,integer
) FROM PUBLIC, anon, authenticated;
GRANT EXECUTE ON FUNCTION publication_control.materialize_translation_witness_candidate(
  uuid,uuid,uuid,uuid,uuid,text,text,text,uuid,integer
) TO publication_worker;

CREATE OR REPLACE FUNCTION serving.read_translation_witnesses(
  p_release_id uuid,
  p_reference_system_code text,
  p_reference_label text
)
RETURNS jsonb
LANGUAGE sql
STABLE
SECURITY INVOKER
AS $wb4_read_translation_witnesses$
  WITH pinned_corpus AS (
    SELECT component_research_object_id AS corpus_release_id
    FROM serving.research_release_components
    WHERE research_release_id=p_release_id
      AND component_kind='CORPUS'
      AND serving.release_is_publicly_servable(p_release_id)
    ORDER BY component_order
    LIMIT 1
  ),
  resolved AS (
    SELECT rl.reference_span_id,rl.reference_system_id,rs.code AS reference_system_code,rl.label
    FROM pinned_corpus pc
    JOIN serving.reference_labels rl ON rl.corpus_release_id=pc.corpus_release_id
    JOIN serving.reference_systems rs USING (reference_system_id)
    WHERE rs.code=p_reference_system_code AND rl.label=p_reference_label
  ),
  witness_payload AS (
    SELECT
      w.witness_order,
      jsonb_build_object(
        'schemaVersion','1.1',
        'textualWorkId',w.textual_work_id::text,
        'textualEditionId',CASE WHEN w.textual_edition_id IS NULL THEN NULL ELSE to_jsonb(w.textual_edition_id::text) END,
        'digitalExpressionId',w.digital_expression_id::text,
        'displayName',w.display_name,
        'languageTag',w.language_tag,
        'coverageStatus',w.coverage_status,
        'deliveryStatus',w.delivery_status,
        'displayStatus',w.display_status,
        'binding',jsonb_build_object(
          'schemaVersion','1.1',
          'bindingMode',w.binding_mode,
          'segmentStorageMode',w.segment_storage_mode,
          'providerDistributionId',w.provider_distribution_id::text,
          'reference',w.provider_reference,
          'providerSegmentKey',w.provider_segment_key,
          'providerVersion',w.provider_version,
          'observedHash',w.observed_hash,
          'observedAt',to_char(w.observed_at AT TIME ZONE 'UTC','YYYY-MM-DD"T"HH24:MI:SS"Z"'),
          'snapshotContentHash',w.snapshot_content_hash
        ),
        'rightsDecisionSnapshotId',w.display_rights_decision_snapshot_id::text,
        'provenanceId',w.provenance_id::text,
        'segments',COALESCE((
          SELECT jsonb_agg(
            jsonb_build_object(
              'schemaVersion','1.1',
              'textSegmentId',s.text_segment_id::text,
              'textStreamId',s.text_stream_id::text,
              'referenceSpanId',s.reference_span_id::text,
              'segmentOrder',s.segment_order,
              'segmentKind',s.segment_kind,
              'text',s.text_content,
              'contentHash',s.content_hash
            )
            ORDER BY s.segment_order
          )
          FROM serving.translation_witness_segments s
          WHERE s.research_release_id=w.research_release_id
            AND s.reference_span_id=w.reference_span_id
            AND s.digital_expression_id=w.digital_expression_id
        ),'[]'::jsonb),
        'attribution',w.attribution
      ) AS payload
    FROM resolved r
    JOIN serving.translation_witnesses w
      ON w.research_release_id=p_release_id
     AND w.reference_span_id=r.reference_span_id
  )
  SELECT jsonb_build_object(
    'schemaVersion','1.1',
    'researchReleaseId',p_release_id::text,
    'referenceSpanId',r.reference_span_id::text,
    'resolvedReference',jsonb_build_object(
      'referenceSystemId',r.reference_system_id::text,
      'referenceSystemCode',r.reference_system_code,
      'referenceLabel',r.label
    ),
    'witnesses',COALESCE(
      (SELECT jsonb_agg(payload ORDER BY witness_order) FROM witness_payload),
      '[]'::jsonb
    )
  )
  FROM resolved r
$wb4_read_translation_witnesses$;

CREATE OR REPLACE FUNCTION serving.read_current_translation_witnesses(
  p_channel_key text,
  p_reference_system_code text,
  p_reference_label text
)
RETURNS jsonb
LANGUAGE sql
STABLE
SECURITY INVOKER
AS $wb4_read_current_translation_witnesses$
  SELECT serving.read_translation_witnesses(
    c.research_release_id,p_reference_system_code,p_reference_label
  )
  FROM serving.current_release c
  WHERE c.channel_key=p_channel_key
$wb4_read_current_translation_witnesses$;

REVOKE ALL ON FUNCTION serving.read_translation_witnesses(uuid,text,text) FROM PUBLIC;
REVOKE ALL ON FUNCTION serving.read_current_translation_witnesses(text,text,text) FROM PUBLIC;
GRANT EXECUTE ON FUNCTION serving.read_translation_witnesses(uuid,text,text) TO anon, authenticated;
GRANT EXECUTE ON FUNCTION serving.read_current_translation_witnesses(text,text,text) TO anon, authenticated;

COMMIT;

         OR lower(seg.content_hash) <> encode(
           sha256(convert_to(seg.surface_original, 'UTF8')), 'hex'
         ) THEN
        RAISE EXCEPTION 'persisted translation segment text and SHA-256 content hash must agree';
      END IF;

      INSERT INTO serving.translation_witness_segments(
        research_release_id,reference_span_id,digital_expression_id,
        text_segment_id,text_stream_id,segment_order,segment_kind,text_content,content_hash
      ) VALUES (
        p_release_id,p_reference_span_id,expr.digital_expression_id,
        seg.text_segment_id,obs.text_stream_id,seq,seg.segment_kind,seg.surface_original,seg.content_hash
      );
      seq := seq + 1;
    END LOOP;

    SELECT count(*) INTO segment_count
    FROM serving.translation_witness_segments
    WHERE research_release_id=p_release_id
      AND reference_span_id=p_reference_span_id
      AND digital_expression_id=expr.digital_expression_id;

    IF segment_count=0 THEN
      RAISE EXCEPTION 'DISPLAYABLE translation witness requires at least one persisted segment';
    END IF;
  END IF;
END
$wb4_materialize_translation_witness$;

REVOKE ALL ON FUNCTION publication_control.materialize_translation_witness_candidate(
  uuid,uuid,uuid,uuid,uuid,text,text,text,uuid,integer
) FROM PUBLIC, anon, authenticated;
GRANT EXECUTE ON FUNCTION publication_control.materialize_translation_witness_candidate(
  uuid,uuid,uuid,uuid,uuid,text,text,text,uuid,integer
) TO publication_worker;

CREATE OR REPLACE FUNCTION serving.read_translation_witnesses(
  p_release_id uuid,
  p_reference_system_code text,
  p_reference_label text
)
RETURNS jsonb
LANGUAGE sql
STABLE
SECURITY INVOKER
AS $wb4_read_translation_witnesses$
  WITH pinned_corpus AS (
    SELECT component_research_object_id AS corpus_release_id
    FROM serving.research_release_components
    WHERE research_release_id=p_release_id
      AND component_kind='CORPUS'
      AND serving.release_is_publicly_servable(p_release_id)
    ORDER BY component_order
    LIMIT 1
  ),
  resolved AS (
    SELECT rl.reference_span_id,rl.reference_system_id,rs.code AS reference_system_code,rl.label
    FROM pinned_corpus pc
    JOIN serving.reference_labels rl ON rl.corpus_release_id=pc.corpus_release_id
    JOIN serving.reference_systems rs USING (reference_system_id)
    WHERE rs.code=p_reference_system_code AND rl.label=p_reference_label
  ),
  witness_payload AS (
    SELECT
      w.witness_order,
      jsonb_build_object(
        'schemaVersion','1.1',
        'textualWorkId',w.textual_work_id::text,
        'textualEditionId',CASE WHEN w.textual_edition_id IS NULL THEN NULL ELSE to_jsonb(w.textual_edition_id::text) END,
        'digitalExpressionId',w.digital_expression_id::text,
        'displayName',w.display_name,
        'languageTag',w.language_tag,
        'coverageStatus',w.coverage_status,
        'deliveryStatus',w.delivery_status,
        'displayStatus',w.display_status,
        'binding',jsonb_build_object(
          'schemaVersion','1.1',
          'bindingMode',w.binding_mode,
          'segmentStorageMode',w.segment_storage_mode,
          'providerDistributionId',w.provider_distribution_id::text,
          'reference',w.provider_reference,
          'providerSegmentKey',w.provider_segment_key,
          'providerVersion',w.provider_version,
          'observedHash',w.observed_hash,
          'observedAt',to_char(w.observed_at AT TIME ZONE 'UTC','YYYY-MM-DD"T"HH24:MI:SS"Z"'),
          'snapshotContentHash',w.snapshot_content_hash
        ),
        'rightsDecisionSnapshotId',w.display_rights_decision_snapshot_id::text,
        'provenanceId',w.provenance_id::text,
        'segments',COALESCE((
          SELECT jsonb_agg(
            jsonb_build_object(
              'schemaVersion','1.1',
              'textSegmentId',s.text_segment_id::text,
              'textStreamId',s.text_stream_id::text,
              'referenceSpanId',s.reference_span_id::text,
              'segmentOrder',s.segment_order,
              'segmentKind',s.segment_kind,
              'text',s.text_content,
              'contentHash',s.content_hash
            )
            ORDER BY s.segment_order
          )
          FROM serving.translation_witness_segments s
          WHERE s.research_release_id=w.research_release_id
            AND s.reference_span_id=w.reference_span_id
            AND s.digital_expression_id=w.digital_expression_id
        ),'[]'::jsonb),
        'attribution',w.attribution
      ) AS payload
    FROM resolved r
    JOIN serving.translation_witnesses w
      ON w.research_release_id=p_release_id
     AND w.reference_span_id=r.reference_span_id
  )
  SELECT jsonb_build_object(
    'schemaVersion','1.1',
    'researchReleaseId',p_release_id::text,
    'referenceSpanId',r.reference_span_id::text,
    'resolvedReference',jsonb_build_object(
      'referenceSystemId',r.reference_system_id::text,
      'referenceSystemCode',r.reference_system_code,
      'referenceLabel',r.label
    ),
    'witnesses',COALESCE(
      (SELECT jsonb_agg(payload ORDER BY witness_order) FROM witness_payload),
      '[]'::jsonb
    )
  )
  FROM resolved r
$wb4_read_translation_witnesses$;

CREATE OR REPLACE FUNCTION serving.read_current_translation_witnesses(
  p_channel_key text,
  p_reference_system_code text,
  p_reference_label text
)
RETURNS jsonb
LANGUAGE sql
STABLE
SECURITY INVOKER
AS $wb4_read_current_translation_witnesses$
  SELECT serving.read_translation_witnesses(
    c.research_release_id,p_reference_system_code,p_reference_label
  )
  FROM serving.current_release c
  WHERE c.channel_key=p_channel_key
$wb4_read_current_translation_witnesses$;

REVOKE ALL ON FUNCTION serving.read_translation_witnesses(uuid,text,text) FROM PUBLIC;
REVOKE ALL ON FUNCTION serving.read_current_translation_witnesses(text,text,text) FROM PUBLIC;
GRANT EXECUTE ON FUNCTION serving.read_translation_witnesses(uuid,text,text) TO anon, authenticated;
GRANT EXECUTE ON FUNCTION serving.read_current_translation_witnesses(text,text,text) TO anon, authenticated;

COMMIT;
