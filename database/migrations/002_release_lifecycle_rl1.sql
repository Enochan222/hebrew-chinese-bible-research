\set ON_ERROR_STOP on

BEGIN;

-- RL-1: split permanent post-publication immutability from current public
-- servability. Legacy multi-event histories cannot be ordered safely because
-- v1.1 previously had no sequence field, so migration fails closed rather than
-- inventing chronology from UUIDs or equal timestamps.
ALTER TABLE serving.research_release_events
  ADD COLUMN event_sequence bigint,
  ADD COLUMN changed_by uuid;

DO $rl1_legacy_event_order$
BEGIN
  IF EXISTS (
    SELECT 1
    FROM serving.research_release_events
    GROUP BY research_release_id
    HAVING count(*) > 1
  ) THEN
    RAISE EXCEPTION
      'RL-1 migration cannot order legacy ResearchRelease histories with multiple unsequenced events';
  END IF;

  UPDATE serving.research_release_events
  SET event_sequence = 1
  WHERE event_sequence IS NULL;
END
$rl1_legacy_event_order$;

ALTER TABLE serving.research_release_events
  ALTER COLUMN event_sequence SET NOT NULL,
  ADD CONSTRAINT research_release_event_sequence_positive
    CHECK (event_sequence > 0),
  ADD CONSTRAINT research_release_event_sequence_unique
    UNIQUE (research_release_id, event_sequence);

CREATE INDEX research_release_events_latest_idx
  ON serving.research_release_events(research_release_id, event_sequence DESC);

CREATE OR REPLACE FUNCTION serving.release_lifecycle_state(p_release_id uuid)
RETURNS text
LANGUAGE sql
STABLE
SECURITY DEFINER
SET search_path = pg_catalog, serving
AS $release_lifecycle_state$
  SELECT e.event_type
  FROM serving.research_release_events e
  WHERE e.research_release_id = p_release_id
  ORDER BY e.event_sequence DESC
  LIMIT 1
$release_lifecycle_state$;

CREATE OR REPLACE FUNCTION serving.release_was_published(p_release_id uuid)
RETURNS boolean
LANGUAGE sql
STABLE
SECURITY DEFINER
SET search_path = pg_catalog, serving
AS $release_was_published$
  SELECT EXISTS (
    SELECT 1
    FROM serving.research_release_events e
    WHERE e.research_release_id = p_release_id
      AND e.event_type = 'PUBLISHED'
  )
$release_was_published$;

CREATE OR REPLACE FUNCTION serving.release_is_publicly_servable(p_release_id uuid)
RETURNS boolean
LANGUAGE sql
STABLE
SECURITY DEFINER
SET search_path = pg_catalog, serving
AS $release_is_publicly_servable$
  SELECT COALESCE(
    serving.release_lifecycle_state(p_release_id)
      IN ('PUBLISHED','SUPERSEDED','REACTIVATED'),
    false
  )
$release_is_publicly_servable$;

CREATE OR REPLACE FUNCTION serving.component_was_published(p_research_object_id uuid)
RETURNS boolean
LANGUAGE sql
STABLE
SECURITY DEFINER
SET search_path = pg_catalog, serving
AS $component_was_published$
  SELECT EXISTS (
    SELECT 1
    FROM serving.research_release_components c
    JOIN serving.research_release_events e
      ON e.research_release_id = c.research_release_id
     AND e.event_type = 'PUBLISHED'
    WHERE c.component_research_object_id = p_research_object_id
  )
$component_was_published$;

CREATE OR REPLACE FUNCTION serving.component_is_publicly_servable(p_research_object_id uuid)
RETURNS boolean
LANGUAGE sql
STABLE
SECURITY DEFINER
SET search_path = pg_catalog, serving
AS $component_is_publicly_servable$
  SELECT EXISTS (
    SELECT 1
    FROM serving.research_release_components c
    WHERE c.component_research_object_id = p_research_object_id
      AND serving.release_is_publicly_servable(c.research_release_id)
  )
$component_is_publicly_servable$;

-- Compatibility names retain runtime/public-visibility semantics only. New
-- immutability code must call *_was_published explicitly.
CREATE OR REPLACE FUNCTION serving.release_is_published(p_release_id uuid)
RETURNS boolean
LANGUAGE sql
STABLE
SECURITY DEFINER
SET search_path = pg_catalog, serving
AS $release_is_published_compat$
  SELECT serving.release_is_publicly_servable(p_release_id)
$release_is_published_compat$;

CREATE OR REPLACE FUNCTION serving.component_is_published(p_research_object_id uuid)
RETURNS boolean
LANGUAGE sql
STABLE
SECURITY DEFINER
SET search_path = pg_catalog, serving
AS $component_is_published_compat$
  SELECT serving.component_is_publicly_servable(p_research_object_id)
$component_is_published_compat$;

CREATE OR REPLACE FUNCTION serving.validate_release_lifecycle_event()
RETURNS trigger
LANGUAGE plpgsql
AS $validate_release_lifecycle_event$
DECLARE
  previous_sequence bigint;
  previous_type text;
  previous_effective_at timestamptz;
BEGIN
  -- Serialize lifecycle appends per release.
  PERFORM 1
  FROM serving.research_releases
  WHERE research_release_id = NEW.research_release_id
  FOR UPDATE;

  IF NOT FOUND THEN
    RAISE EXCEPTION 'ResearchRelease % does not exist', NEW.research_release_id;
  END IF;

  SELECT e.event_sequence,e.event_type,e.effective_at
  INTO previous_sequence,previous_type,previous_effective_at
  FROM serving.research_release_events e
  WHERE e.research_release_id = NEW.research_release_id
  ORDER BY e.event_sequence DESC
  LIMIT 1;

  IF previous_sequence IS NULL THEN
    IF NEW.event_sequence <> 1 OR NEW.event_type <> 'PUBLISHED' THEN
      RAISE EXCEPTION
        'first lifecycle event must be PUBLISHED with event_sequence=1';
    END IF;
  ELSE
    IF NEW.event_sequence <> previous_sequence + 1 THEN
      RAISE EXCEPTION
        'lifecycle event_sequence must be contiguous: expected %, received %',
        previous_sequence + 1, NEW.event_sequence;
    END IF;

    IF NEW.effective_at < previous_effective_at THEN
      RAISE EXCEPTION
        'lifecycle effective_at cannot move backwards; event_sequence resolves equal timestamps';
    END IF;

    IF previous_type = 'PUBLISHED'
       AND NEW.event_type NOT IN ('SUPERSEDED','REVOKED') THEN
      RAISE EXCEPTION 'invalid lifecycle transition PUBLISHED -> %', NEW.event_type;
    ELSIF previous_type = 'SUPERSEDED'
       AND NEW.event_type <> 'REVOKED' THEN
      RAISE EXCEPTION 'invalid lifecycle transition SUPERSEDED -> %', NEW.event_type;
    ELSIF previous_type = 'REVOKED'
       AND NEW.event_type <> 'REACTIVATED' THEN
      RAISE EXCEPTION 'invalid lifecycle transition REVOKED -> %', NEW.event_type;
    ELSIF previous_type = 'REACTIVATED'
       AND NEW.event_type NOT IN ('SUPERSEDED','REVOKED') THEN
      RAISE EXCEPTION 'invalid lifecycle transition REACTIVATED -> %', NEW.event_type;
    END IF;
  END IF;

  IF NEW.event_type <> 'PUBLISHED'
     AND length(trim(COALESCE(NEW.reason,''))) = 0 THEN
    RAISE EXCEPTION '% lifecycle event requires a non-empty reason', NEW.event_type;
  END IF;

  RETURN NEW;
END
$validate_release_lifecycle_event$;

CREATE TRIGGER research_release_event_lifecycle_guard
BEFORE INSERT ON serving.research_release_events
FOR EACH ROW EXECUTE FUNCTION serving.validate_release_lifecycle_event();

CREATE OR REPLACE FUNCTION serving.cleanup_revoked_release_channels()
RETURNS trigger
LANGUAGE plpgsql
AS $cleanup_revoked_release_channels$
BEGIN
  IF NEW.event_type = 'REVOKED' THEN
    DELETE FROM serving.release_channel_pointers
    WHERE research_release_id = NEW.research_release_id;
  END IF;
  RETURN NEW;
END
$cleanup_revoked_release_channels$;

CREATE TRIGGER research_release_event_revoke_channel_cleanup
AFTER INSERT ON serving.research_release_events
FOR EACH ROW EXECUTE FUNCTION serving.cleanup_revoked_release_channels();

CREATE OR REPLACE FUNCTION serving.validate_release_channel_pointer()
RETURNS trigger
LANGUAGE plpgsql
AS $validate_release_channel_pointer$
BEGIN
  IF NOT serving.release_is_publicly_servable(NEW.research_release_id) THEN
    RAISE EXCEPTION
      'release % is not currently publicly servable and cannot receive a channel pointer',
      NEW.research_release_id;
  END IF;
  RETURN NEW;
END
$validate_release_channel_pointer$;

CREATE TRIGGER release_channel_pointer_servable_guard
BEFORE INSERT OR UPDATE ON serving.release_channel_pointers
FOR EACH ROW EXECUTE FUNCTION serving.validate_release_channel_pointer();

CREATE OR REPLACE FUNCTION publication_control.transition_release_lifecycle(
  p_release_id uuid,
  p_event_type text,
  p_effective_at timestamptz DEFAULT now(),
  p_reason text DEFAULT NULL,
  p_changed_by uuid DEFAULT NULL
)
RETURNS bigint
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = pg_catalog, serving
AS $transition_release_lifecycle$
DECLARE
  next_sequence bigint;
BEGIN
  IF p_event_type NOT IN ('PUBLISHED','SUPERSEDED','REVOKED','REACTIVATED') THEN
    RAISE EXCEPTION 'unknown ResearchRelease lifecycle event type %', p_event_type;
  END IF;

  PERFORM 1
  FROM serving.research_releases
  WHERE research_release_id = p_release_id
  FOR UPDATE;

  IF NOT FOUND THEN
    RAISE EXCEPTION 'release does not exist';
  END IF;

  SELECT COALESCE(max(event_sequence),0) + 1
  INTO next_sequence
  FROM serving.research_release_events
  WHERE research_release_id = p_release_id;

  INSERT INTO serving.research_release_events(
    research_release_event_id,research_release_id,event_type,
    effective_at,reason,event_sequence,changed_by
  ) VALUES (
    pg_catalog.gen_random_uuid(),p_release_id,p_event_type,
    p_effective_at,p_reason,next_sequence,p_changed_by
  );

  RETURN next_sequence;
END
$transition_release_lifecycle$;

-- Post-publication immutability is permanent, including while REVOKED.
CREATE OR REPLACE FUNCTION serving.guard_direct_release_payload()
RETURNS trigger
LANGUAGE plpgsql
AS $guard_direct_release_payload$
DECLARE
  release_id uuid;
BEGIN
  release_id := CASE
    WHEN TG_OP = 'DELETE' THEN (to_jsonb(OLD)->>'research_release_id')::uuid
    ELSE (to_jsonb(NEW)->>'research_release_id')::uuid
  END;

  IF serving.release_was_published(release_id) THEN
    RAISE EXCEPTION 'release % payload is immutable after first PUBLISHED', release_id;
  END IF;

  RETURN CASE WHEN TG_OP = 'DELETE' THEN OLD ELSE NEW END;
END
$guard_direct_release_payload$;

CREATE OR REPLACE FUNCTION serving.guard_evidence_item_payload()
RETURNS trigger
LANGUAGE plpgsql
AS $guard_evidence_item_payload$
DECLARE
  packet_id uuid;
  release_id uuid;
BEGIN
  packet_id := CASE
    WHEN TG_OP = 'DELETE' THEN OLD.published_evidence_packet_id
    ELSE NEW.published_evidence_packet_id
  END;

  SELECT research_release_id INTO release_id
  FROM serving.published_evidence_packets
  WHERE published_evidence_packet_id = packet_id;

  IF release_id IS NULL THEN
    RAISE EXCEPTION 'evidence packet % does not resolve to a release', packet_id;
  END IF;

  IF serving.release_was_published(release_id) THEN
    RAISE EXCEPTION 'release % evidence payload is immutable after first PUBLISHED', release_id;
  END IF;

  RETURN CASE WHEN TG_OP = 'DELETE' THEN OLD ELSE NEW END;
END
$guard_evidence_item_payload$;

CREATE OR REPLACE FUNCTION serving.guard_assertion_evidence_payload()
RETURNS trigger
LANGUAGE plpgsql
AS $guard_assertion_evidence_payload$
DECLARE
  assertion_id uuid;
  evidence_id uuid;
  assertion_release uuid;
  evidence_release uuid;
BEGIN
  assertion_id := CASE WHEN TG_OP='DELETE' THEN OLD.published_assertion_id ELSE NEW.published_assertion_id END;
  evidence_id := CASE WHEN TG_OP='DELETE' THEN OLD.published_evidence_item_id ELSE NEW.published_evidence_item_id END;

  SELECT research_release_id INTO assertion_release
  FROM serving.published_assertions
  WHERE published_assertion_id = assertion_id;

  SELECT p.research_release_id INTO evidence_release
  FROM serving.published_evidence_items i
  JOIN serving.published_evidence_packets p
    ON p.published_evidence_packet_id = i.published_evidence_packet_id
  WHERE i.published_evidence_item_id = evidence_id;

  IF assertion_release IS NULL OR evidence_release IS NULL OR assertion_release <> evidence_release THEN
    RAISE EXCEPTION 'assertion and evidence must belong to the same ResearchRelease';
  END IF;

  IF serving.release_was_published(assertion_release) THEN
    RAISE EXCEPTION 'release % assertion/evidence links are immutable after first PUBLISHED', assertion_release;
  END IF;

  RETURN CASE WHEN TG_OP='DELETE' THEN OLD ELSE NEW END;
END
$guard_assertion_evidence_payload$;

CREATE OR REPLACE FUNCTION serving.guard_component_projection()
RETURNS trigger
LANGUAGE plpgsql
AS $guard_component_projection$
DECLARE
  object_id uuid;
BEGIN
  object_id := CASE
    WHEN TG_OP='DELETE' THEN (to_jsonb(OLD)->>TG_ARGV[0])::uuid
    ELSE (to_jsonb(NEW)->>TG_ARGV[0])::uuid
  END;

  IF serving.component_was_published(object_id) THEN
    RAISE EXCEPTION 'ever-published component % projection is immutable', object_id;
  END IF;

  RETURN CASE WHEN TG_OP='DELETE' THEN OLD ELSE NEW END;
END
$guard_component_projection$;

CREATE OR REPLACE FUNCTION publication_control.publish_release_to_channel(
  p_channel_key text,
  p_release_id uuid,
  p_updated_by uuid DEFAULT NULL,
  p_inject_failure boolean DEFAULT false
)
RETURNS void
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = pg_catalog, serving
AS $publish_release_to_channel_rl1$
DECLARE
  channel_id uuid;
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM serving.research_releases r
    WHERE r.research_release_id = p_release_id
  ) THEN
    RAISE EXCEPTION 'release does not exist';
  END IF;

  IF NOT EXISTS (
    SELECT 1 FROM serving.research_release_components c
    WHERE c.research_release_id = p_release_id
  ) THEN
    RAISE EXCEPTION 'release has no components';
  END IF;

  IF EXISTS (
    SELECT 1
    FROM serving.research_release_components c
    WHERE c.research_release_id = p_release_id
      AND c.component_kind = 'CORPUS'
      AND NOT EXISTS (
        SELECT 1
        FROM serving.rights_decision_snapshots rds
        WHERE rds.subject_type = 'CORPUS_RELEASE'
          AND rds.subject_identifier = c.component_research_object_id
          AND rds.operation = 'DISPLAY_FULLTEXT'
          AND rds.purpose_scope = 'PUBLIC_DISPLAY'
          AND rds.audience_scope = 'PUBLIC'
          AND rds.commercial_context IN ('MIXED','COMMERCIAL')
          AND rds.decision IN ('ALLOW','CONDITIONAL')
          AND rds.decision_basis = 'RULE'
      )
  ) THEN
    RAISE EXCEPTION 'corpus component lacks a public DISPLAY_FULLTEXT rights decision';
  END IF;

  SELECT release_channel_id INTO channel_id
  FROM serving.release_channels
  WHERE channel_key = p_channel_key;

  IF channel_id IS NULL THEN
    RAISE EXCEPTION 'release channel does not exist';
  END IF;

  IF NOT serving.release_was_published(p_release_id) THEN
    PERFORM publication_control.transition_release_lifecycle(
      p_release_id,'PUBLISHED',now(),
      'publication_control.publish_release_to_channel',p_updated_by
    );
  ELSIF NOT serving.release_is_publicly_servable(p_release_id) THEN
    RAISE EXCEPTION
      'release % is not publicly servable; append a valid REACTIVATED event before channel assignment',
      p_release_id;
  END IF;

  IF p_inject_failure THEN
    RAISE EXCEPTION 'SPIKE_INJECTED_FAILURE_BEFORE_POINTER_MOVE';
  END IF;

  INSERT INTO serving.release_channel_pointers(
    release_channel_id,research_release_id,updated_at,updated_by,row_version
  )
  VALUES (channel_id,p_release_id,now(),p_updated_by,1)
  ON CONFLICT (release_channel_id) DO UPDATE
  SET research_release_id = EXCLUDED.research_release_id,
      updated_at = EXCLUDED.updated_at,
      updated_by = EXCLUDED.updated_by,
      row_version = serving.release_channel_pointers.row_version + 1;
END
$publish_release_to_channel_rl1$;

CREATE OR REPLACE VIEW serving.current_release
WITH (security_invoker = true)
AS
SELECT c.channel_key,p.research_release_id,r.release_label,r.published_at
FROM serving.release_channels c
JOIN serving.release_channel_pointers p USING (release_channel_id)
JOIN serving.research_releases r USING (research_release_id)
WHERE serving.release_is_publicly_servable(p.research_release_id);

-- Public RLS follows current servability, not permanent immutability.
DROP POLICY IF EXISTS public_read_reference_labels ON serving.reference_labels;
CREATE POLICY public_read_reference_labels ON serving.reference_labels
FOR SELECT TO anon, authenticated
USING (serving.component_is_publicly_servable(corpus_release_id));

DROP POLICY IF EXISTS public_read_corpus_text_segments ON serving.corpus_text_segments;
CREATE POLICY public_read_corpus_text_segments ON serving.corpus_text_segments
FOR SELECT TO anon, authenticated
USING (serving.component_is_publicly_servable(corpus_release_id));

DROP POLICY IF EXISTS public_read_corpus_node_segments ON serving.corpus_node_segments;
CREATE POLICY public_read_corpus_node_segments ON serving.corpus_node_segments
FOR SELECT TO anon, authenticated
USING (serving.component_is_publicly_servable(corpus_release_id));

DROP POLICY IF EXISTS public_read_corpus_nodes ON serving.corpus_nodes;
CREATE POLICY public_read_corpus_nodes ON serving.corpus_nodes
FOR SELECT TO anon, authenticated
USING (serving.component_is_publicly_servable(corpus_release_id));

DROP POLICY IF EXISTS public_read_corpus_node_features ON serving.corpus_node_features;
CREATE POLICY public_read_corpus_node_features ON serving.corpus_node_features
FOR SELECT TO anon, authenticated
USING (serving.component_is_publicly_servable(corpus_release_id));

DROP POLICY IF EXISTS public_read_corpus_edges ON serving.corpus_edges;
CREATE POLICY public_read_corpus_edges ON serving.corpus_edges
FOR SELECT TO anon, authenticated
USING (serving.component_is_publicly_servable(corpus_release_id));

DROP POLICY IF EXISTS public_read_corpus_node_mappings ON serving.corpus_node_mappings;
CREATE POLICY public_read_corpus_node_mappings ON serving.corpus_node_mappings
FOR SELECT TO anon, authenticated
USING (serving.component_is_publicly_servable(corpus_release_id));

DROP POLICY IF EXISTS public_read_semantic_set_members ON serving.semantic_set_members;
CREATE POLICY public_read_semantic_set_members ON serving.semantic_set_members
FOR SELECT TO anon, authenticated
USING (serving.component_is_publicly_servable(semantic_set_version_id));

DROP POLICY IF EXISTS public_read_releases ON serving.research_releases;
CREATE POLICY public_read_releases ON serving.research_releases
FOR SELECT TO anon, authenticated
USING (serving.release_is_publicly_servable(research_release_id));

DROP POLICY IF EXISTS public_read_release_components ON serving.research_release_components;
CREATE POLICY public_read_release_components ON serving.research_release_components
FOR SELECT TO anon, authenticated
USING (serving.release_is_publicly_servable(research_release_id));

DROP POLICY IF EXISTS public_read_release_channel_pointers ON serving.release_channel_pointers;
CREATE POLICY public_read_release_channel_pointers ON serving.release_channel_pointers
FOR SELECT TO anon, authenticated
USING (serving.release_is_publicly_servable(research_release_id));

DROP POLICY IF EXISTS public_read_passage_analyses ON serving.published_passage_analyses;
CREATE POLICY public_read_passage_analyses ON serving.published_passage_analyses
FOR SELECT TO anon, authenticated
USING (serving.release_is_publicly_servable(research_release_id));

DROP POLICY IF EXISTS public_read_evidence_packets ON serving.published_evidence_packets;
CREATE POLICY public_read_evidence_packets ON serving.published_evidence_packets
FOR SELECT TO anon, authenticated
USING (serving.release_is_publicly_servable(research_release_id));

DROP POLICY IF EXISTS public_read_evidence_items ON serving.published_evidence_items;
CREATE POLICY public_read_evidence_items ON serving.published_evidence_items
FOR SELECT TO anon, authenticated
USING (
  EXISTS (
    SELECT 1
    FROM serving.published_evidence_packets p
    WHERE p.published_evidence_packet_id = published_evidence_items.published_evidence_packet_id
      AND serving.release_is_publicly_servable(p.research_release_id)
  )
);

DROP POLICY IF EXISTS public_read_assertions ON serving.published_assertions;
CREATE POLICY public_read_assertions ON serving.published_assertions
FOR SELECT TO anon, authenticated
USING (serving.release_is_publicly_servable(research_release_id));

DROP POLICY IF EXISTS public_read_assertion_evidence ON serving.published_assertion_evidence;
CREATE POLICY public_read_assertion_evidence ON serving.published_assertion_evidence
FOR SELECT TO anon, authenticated
USING (
  EXISTS (
    SELECT 1
    FROM serving.published_assertions a
    WHERE a.published_assertion_id = published_assertion_evidence.published_assertion_id
      AND serving.release_is_publicly_servable(a.research_release_id)
  )
);

REVOKE ALL ON FUNCTION publication_control.transition_release_lifecycle(uuid,text,timestamptz,text,uuid)
  FROM PUBLIC, anon, authenticated;
GRANT EXECUTE ON FUNCTION publication_control.transition_release_lifecycle(uuid,text,timestamptz,text,uuid)
  TO publication_worker;

REVOKE ALL ON FUNCTION serving.release_lifecycle_state(uuid) FROM PUBLIC, anon, authenticated;
REVOKE ALL ON FUNCTION serving.release_was_published(uuid) FROM PUBLIC, anon, authenticated;
REVOKE ALL ON FUNCTION serving.component_was_published(uuid) FROM PUBLIC, anon, authenticated;
REVOKE ALL ON FUNCTION serving.release_is_publicly_servable(uuid) FROM PUBLIC, anon, authenticated;
REVOKE ALL ON FUNCTION serving.component_is_publicly_servable(uuid) FROM PUBLIC, anon, authenticated;

GRANT EXECUTE ON FUNCTION serving.release_lifecycle_state(uuid),
  serving.release_was_published(uuid),
  serving.component_was_published(uuid),
  serving.release_is_publicly_servable(uuid),
  serving.component_is_publicly_servable(uuid)
TO publication_worker;

GRANT EXECUTE ON FUNCTION serving.release_is_publicly_servable(uuid),
  serving.component_is_publicly_servable(uuid)
TO anon, authenticated;

COMMIT;
