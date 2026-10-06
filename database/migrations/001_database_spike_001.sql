\set ON_ERROR_STOP on

BEGIN;

CREATE SCHEMA IF NOT EXISTS authoring;
CREATE SCHEMA IF NOT EXISTS serving;
CREATE SCHEMA IF NOT EXISTS workspace;
CREATE SCHEMA IF NOT EXISTS publication_control;

REVOKE ALL ON SCHEMA authoring FROM PUBLIC, anon, authenticated;
REVOKE ALL ON SCHEMA publication_control FROM PUBLIC, anon, authenticated;
GRANT USAGE ON SCHEMA serving TO anon, authenticated;
GRANT USAGE ON SCHEMA workspace TO authenticated;
GRANT USAGE ON SCHEMA publication_control TO publication_worker;

CREATE TABLE authoring.biblical_books (
  book_id uuid PRIMARY KEY,
  osis_code text NOT NULL UNIQUE,
  english_name text NOT NULL
);

CREATE TABLE authoring.canon_systems (
  canon_system_id uuid PRIMARY KEY,
  code text NOT NULL UNIQUE,
  name text NOT NULL,
  tradition text,
  description text
);

CREATE TABLE authoring.canon_books (
  canon_system_id uuid NOT NULL REFERENCES authoring.canon_systems(canon_system_id) ON DELETE CASCADE,
  book_id uuid NOT NULL REFERENCES authoring.biblical_books(book_id),
  book_order integer NOT NULL CHECK (book_order >= 1),
  included boolean NOT NULL DEFAULT true,
  PRIMARY KEY (canon_system_id, book_id),
  UNIQUE (canon_system_id, book_order)
);

CREATE TABLE authoring.reference_systems (
  reference_system_id uuid PRIMARY KEY,
  code text NOT NULL UNIQUE,
  name text NOT NULL
);

CREATE TABLE authoring.reference_atoms (
  reference_atom_id uuid PRIMARY KEY,
  book_id uuid NOT NULL REFERENCES authoring.biblical_books(book_id),
  sequence integer NOT NULL CHECK (sequence >= 0),
  atom_kind text NOT NULL,
  metadata jsonb NOT NULL DEFAULT '{}'::jsonb,
  UNIQUE (book_id, sequence),
  UNIQUE (reference_atom_id, book_id, sequence)
);

CREATE TABLE authoring.reference_spans (
  reference_span_id uuid PRIMARY KEY,
  book_id uuid NOT NULL REFERENCES authoring.biblical_books(book_id),
  start_atom_id uuid NOT NULL,
  start_sequence integer NOT NULL,
  end_atom_id uuid NOT NULL,
  end_sequence integer NOT NULL,
  span_kind text NOT NULL,
  metadata jsonb NOT NULL DEFAULT '{}'::jsonb,
  CHECK (start_sequence <= end_sequence),
  FOREIGN KEY (start_atom_id, book_id, start_sequence)
    REFERENCES authoring.reference_atoms(reference_atom_id, book_id, sequence),
  FOREIGN KEY (end_atom_id, book_id, end_sequence)
    REFERENCES authoring.reference_atoms(reference_atom_id, book_id, sequence),
  UNIQUE (reference_span_id, book_id, start_sequence, end_sequence)
);

CREATE TABLE authoring.reference_labels (
  reference_label_id uuid PRIMARY KEY,
  reference_system_id uuid NOT NULL REFERENCES authoring.reference_systems(reference_system_id),
  book_id uuid NOT NULL REFERENCES authoring.biblical_books(book_id),
  label text NOT NULL,
  chapter_number integer,
  verse_label text,
  sort_key integer NOT NULL,
  UNIQUE (reference_system_id, book_id, label),
  UNIQUE (reference_label_id, book_id)
);

CREATE TABLE authoring.reference_label_members (
  reference_label_id uuid NOT NULL,
  book_id uuid NOT NULL,
  reference_atom_id uuid NOT NULL,
  atom_sequence integer NOT NULL,
  member_order integer NOT NULL CHECK (member_order >= 0),
  PRIMARY KEY (reference_label_id, member_order),
  UNIQUE (reference_label_id, reference_atom_id),
  FOREIGN KEY (reference_label_id, book_id)
    REFERENCES authoring.reference_labels(reference_label_id, book_id),
  FOREIGN KEY (reference_atom_id, book_id, atom_sequence)
    REFERENCES authoring.reference_atoms(reference_atom_id, book_id, sequence)
);

CREATE TABLE authoring.research_objects (
  research_object_id uuid PRIMARY KEY,
  object_type text NOT NULL,
  created_at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE authoring.textual_works (
  textual_work_id uuid PRIMARY KEY,
  work_kind text NOT NULL,
  canonical_name text NOT NULL,
  language_code text NOT NULL,
  script_code text,
  description text
);

CREATE TABLE authoring.textual_editions (
  textual_edition_id uuid PRIMARY KEY,
  textual_work_id uuid NOT NULL REFERENCES authoring.textual_works(textual_work_id),
  edition_label text NOT NULL,
  publication_year integer,
  edition_status text NOT NULL,
  metadata jsonb NOT NULL DEFAULT '{}'::jsonb
);

CREATE TABLE authoring.digital_expressions (
  digital_expression_id uuid PRIMARY KEY,
  textual_edition_id uuid REFERENCES authoring.textual_editions(textual_edition_id),
  textual_work_id uuid NOT NULL REFERENCES authoring.textual_works(textual_work_id),
  expression_label text NOT NULL,
  expression_version text,
  source_checksum text,
  metadata jsonb NOT NULL DEFAULT '{}'::jsonb
);

CREATE TABLE authoring.text_streams (
  text_stream_id uuid PRIMARY KEY,
  digital_expression_id uuid NOT NULL REFERENCES authoring.digital_expressions(digital_expression_id),
  stream_type text NOT NULL CHECK (stream_type IN ('BASE','WRITTEN','READ','EDITORIAL')),
  stream_version text,
  UNIQUE (text_stream_id, digital_expression_id)
);

CREATE TABLE authoring.text_segments (
  text_segment_id uuid PRIMARY KEY,
  text_stream_id uuid NOT NULL REFERENCES authoring.text_streams(text_stream_id),
  reference_span_id uuid NOT NULL REFERENCES authoring.reference_spans(reference_span_id),
  segment_order integer NOT NULL,
  segment_storage_mode text NOT NULL CHECK (segment_storage_mode IN ('PERSISTED_CONTENT','PROVIDER_LOCATOR','EPHEMERAL')),
  surface_original text,
  segment_kind text NOT NULL,
  content_hash text,
  metadata jsonb NOT NULL DEFAULT '{}'::jsonb,
  UNIQUE (text_stream_id, segment_order),
  UNIQUE (text_segment_id, text_stream_id)
);

CREATE TABLE authoring.annotation_frameworks (
  annotation_framework_id uuid PRIMARY KEY,
  framework_key text NOT NULL UNIQUE,
  name text NOT NULL,
  description text,
  ontology_version text
);

CREATE TABLE authoring.corpus_releases (
  corpus_release_id uuid PRIMARY KEY REFERENCES authoring.research_objects(research_object_id),
  digital_expression_id uuid NOT NULL REFERENCES authoring.digital_expressions(digital_expression_id),
  release_name text NOT NULL,
  release_version text,
  importer_version text NOT NULL,
  imported_at timestamptz NOT NULL DEFAULT now(),
  source_checksum text,
  UNIQUE (corpus_release_id, digital_expression_id)
);

CREATE TABLE authoring.annotation_layers (
  annotation_layer_id uuid PRIMARY KEY REFERENCES authoring.research_objects(research_object_id),
  corpus_release_id uuid NOT NULL REFERENCES authoring.corpus_releases(corpus_release_id),
  annotation_framework_id uuid NOT NULL REFERENCES authoring.annotation_frameworks(annotation_framework_id),
  layer_kind text NOT NULL CHECK (layer_kind IN (
    'ORTHOGRAPHIC_SEGMENTATION','MORPHEME_SEGMENTATION','MORPHOLOGY',
    'PHRASE_STRUCTURE','CLAUSE_STRUCTURE','DEPENDENCY','SEMANTIC_ROLE',
    'DISCOURSE','WORD_SENSE'
  )),
  layer_version text NOT NULL,
  content_hash text,
  metadata jsonb NOT NULL DEFAULT '{}'::jsonb
);

CREATE TABLE authoring.analysis_nodes (
  analysis_node_id uuid PRIMARY KEY,
  annotation_layer_id uuid NOT NULL REFERENCES authoring.annotation_layers(annotation_layer_id),
  node_type text NOT NULL,
  reference_span_id uuid NOT NULL REFERENCES authoring.reference_spans(reference_span_id),
  node_order integer,
  external_node_id text,
  metadata jsonb NOT NULL DEFAULT '{}'::jsonb,
  UNIQUE (analysis_node_id, annotation_layer_id)
);

CREATE TABLE authoring.analysis_node_features (
  analysis_node_id uuid NOT NULL REFERENCES authoring.analysis_nodes(analysis_node_id) ON DELETE CASCADE,
  feature_key text NOT NULL,
  feature_value text NOT NULL,
  PRIMARY KEY (analysis_node_id, feature_key, feature_value)
);

CREATE TABLE authoring.analysis_node_segments (
  analysis_node_id uuid NOT NULL REFERENCES authoring.analysis_nodes(analysis_node_id) ON DELETE CASCADE,
  text_segment_id uuid NOT NULL REFERENCES authoring.text_segments(text_segment_id),
  member_order integer NOT NULL,
  membership_role text,
  PRIMARY KEY (analysis_node_id, member_order),
  UNIQUE (analysis_node_id, text_segment_id)
);

CREATE OR REPLACE FUNCTION authoring.validate_node_segment_compatibility()
RETURNS trigger
LANGUAGE plpgsql
AS $wb1_node_segment_compat$
DECLARE
  node_expression uuid;
  segment_expression uuid;
  node_book uuid;
  segment_book uuid;
  node_start integer;
  node_end integer;
  segment_start integer;
  segment_end integer;
BEGIN
  SELECT cr.digital_expression_id, rs.book_id, rs.start_sequence, rs.end_sequence
    INTO node_expression, node_book, node_start, node_end
  FROM authoring.analysis_nodes n
  JOIN authoring.annotation_layers al ON al.annotation_layer_id = n.annotation_layer_id
  JOIN authoring.corpus_releases cr ON cr.corpus_release_id = al.corpus_release_id
  JOIN authoring.reference_spans rs ON rs.reference_span_id = n.reference_span_id
  WHERE n.analysis_node_id = NEW.analysis_node_id;

  SELECT ts.digital_expression_id, rs.book_id, rs.start_sequence, rs.end_sequence
    INTO segment_expression, segment_book, segment_start, segment_end
  FROM authoring.text_segments s
  JOIN authoring.text_streams ts ON ts.text_stream_id = s.text_stream_id
  JOIN authoring.reference_spans rs ON rs.reference_span_id = s.reference_span_id
  WHERE s.text_segment_id = NEW.text_segment_id;

  IF node_expression IS NULL OR segment_expression IS NULL OR node_expression <> segment_expression THEN
    RAISE EXCEPTION 'analysis node and text segment belong to incompatible digital expressions';
  END IF;

  IF node_book IS NULL OR segment_book IS NULL
     OR node_book <> segment_book
     OR segment_start < node_start
     OR segment_end > node_end THEN
    RAISE EXCEPTION 'analysis-node reference span must contain every member text-segment span';
  END IF;
  RETURN NEW;
END
$wb1_node_segment_compat$;

CREATE TRIGGER analysis_node_segments_compatibility
BEFORE INSERT OR UPDATE ON authoring.analysis_node_segments
FOR EACH ROW EXECUTE FUNCTION authoring.validate_node_segment_compatibility();

CREATE TABLE authoring.analysis_edges (
  analysis_edge_id uuid PRIMARY KEY,
  annotation_layer_id uuid NOT NULL REFERENCES authoring.annotation_layers(annotation_layer_id),
  from_node_id uuid NOT NULL,
  to_node_id uuid NOT NULL,
  relation_type text NOT NULL,
  relation_ontology text NOT NULL,
  properties jsonb NOT NULL DEFAULT '{}'::jsonb,
  FOREIGN KEY (from_node_id, annotation_layer_id)
    REFERENCES authoring.analysis_nodes(analysis_node_id, annotation_layer_id),
  FOREIGN KEY (to_node_id, annotation_layer_id)
    REFERENCES authoring.analysis_nodes(analysis_node_id, annotation_layer_id)
);

CREATE TABLE authoring.cross_annotation_mappings (
  cross_annotation_mapping_id uuid PRIMARY KEY,
  from_annotation_layer_id uuid NOT NULL REFERENCES authoring.annotation_layers(annotation_layer_id),
  from_node_id uuid NOT NULL,
  to_annotation_layer_id uuid NOT NULL REFERENCES authoring.annotation_layers(annotation_layer_id),
  to_node_id uuid NOT NULL,
  mapping_type text NOT NULL,
  confidence numeric CHECK (confidence IS NULL OR (confidence >= 0 AND confidence <= 1)),
  mapping_method text NOT NULL,
  review_status text NOT NULL,
  properties jsonb NOT NULL DEFAULT '{}'::jsonb,
  CHECK (from_annotation_layer_id <> to_annotation_layer_id),
  FOREIGN KEY (from_node_id, from_annotation_layer_id)
    REFERENCES authoring.analysis_nodes(analysis_node_id, annotation_layer_id),
  FOREIGN KEY (to_node_id, to_annotation_layer_id)
    REFERENCES authoring.analysis_nodes(analysis_node_id, annotation_layer_id)
);

-- Real OSHB/BHSA evidence requires preserving n:m candidate span boundaries.
-- A grouped candidate is research data in Authoring only; it is not a canonical
-- identity and must not be projected to Serving until reviewed.
CREATE TABLE authoring.cross_annotation_mapping_groups (
  mapping_group_id uuid PRIMARY KEY,
  from_annotation_layer_id uuid NOT NULL REFERENCES authoring.annotation_layers(annotation_layer_id),
  to_annotation_layer_id uuid NOT NULL REFERENCES authoring.annotation_layers(annotation_layer_id),
  reference_span_id uuid NOT NULL REFERENCES authoring.reference_spans(reference_span_id),
  mapping_type text NOT NULL,
  mapping_method text NOT NULL,
  review_status text NOT NULL,
  canonical boolean NOT NULL DEFAULT false,
  confidence numeric CHECK (confidence IS NULL OR (confidence >= 0 AND confidence <= 1)),
  properties jsonb NOT NULL DEFAULT '{}'::jsonb,
  CHECK (from_annotation_layer_id <> to_annotation_layer_id),
  CHECK (NOT (canonical AND review_status = 'CANDIDATE_AUTOMATED')),
  UNIQUE (mapping_group_id, from_annotation_layer_id),
  UNIQUE (mapping_group_id, to_annotation_layer_id)
);

CREATE TABLE authoring.cross_annotation_mapping_from_members (
  mapping_group_id uuid NOT NULL,
  from_annotation_layer_id uuid NOT NULL,
  from_node_id uuid NOT NULL,
  member_order integer NOT NULL CHECK (member_order >= 0),
  PRIMARY KEY (mapping_group_id, member_order),
  UNIQUE (mapping_group_id, from_node_id),
  FOREIGN KEY (mapping_group_id, from_annotation_layer_id)
    REFERENCES authoring.cross_annotation_mapping_groups(mapping_group_id, from_annotation_layer_id)
    ON DELETE CASCADE,
  FOREIGN KEY (from_node_id, from_annotation_layer_id)
    REFERENCES authoring.analysis_nodes(analysis_node_id, annotation_layer_id)
);

CREATE TABLE authoring.cross_annotation_mapping_to_members (
  mapping_group_id uuid NOT NULL,
  to_annotation_layer_id uuid NOT NULL,
  to_node_id uuid NOT NULL,
  member_order integer NOT NULL CHECK (member_order >= 0),
  PRIMARY KEY (mapping_group_id, member_order),
  UNIQUE (mapping_group_id, to_node_id),
  FOREIGN KEY (mapping_group_id, to_annotation_layer_id)
    REFERENCES authoring.cross_annotation_mapping_groups(mapping_group_id, to_annotation_layer_id)
    ON DELETE CASCADE,
  FOREIGN KEY (to_node_id, to_annotation_layer_id)
    REFERENCES authoring.analysis_nodes(analysis_node_id, annotation_layer_id)
);

CREATE OR REPLACE FUNCTION authoring.validate_cross_annotation_mapping_member_span()
RETURNS trigger
LANGUAGE plpgsql
AS $wb0_mapping_member_span$
DECLARE
  group_span uuid;
  node_span uuid;
BEGIN
  IF TG_TABLE_NAME = 'cross_annotation_mapping_from_members' THEN
    SELECT g.reference_span_id, n.reference_span_id
      INTO group_span, node_span
    FROM authoring.cross_annotation_mapping_groups g
    JOIN authoring.analysis_nodes n
      ON n.analysis_node_id = NEW.from_node_id
     AND n.annotation_layer_id = NEW.from_annotation_layer_id
    WHERE g.mapping_group_id = NEW.mapping_group_id
      AND g.from_annotation_layer_id = NEW.from_annotation_layer_id;
  ELSE
    SELECT g.reference_span_id, n.reference_span_id
      INTO group_span, node_span
    FROM authoring.cross_annotation_mapping_groups g
    JOIN authoring.analysis_nodes n
      ON n.analysis_node_id = NEW.to_node_id
     AND n.annotation_layer_id = NEW.to_annotation_layer_id
    WHERE g.mapping_group_id = NEW.mapping_group_id
      AND g.to_annotation_layer_id = NEW.to_annotation_layer_id;
  END IF;

  IF group_span IS NULL OR node_span IS NULL OR group_span <> node_span THEN
    RAISE EXCEPTION 'cross-annotation mapping member must share the mapping-group reference span';
  END IF;
  RETURN NEW;
END
$wb0_mapping_member_span$;

CREATE TRIGGER cross_annotation_mapping_from_member_span
BEFORE INSERT OR UPDATE ON authoring.cross_annotation_mapping_from_members
FOR EACH ROW EXECUTE FUNCTION authoring.validate_cross_annotation_mapping_member_span();

CREATE TRIGGER cross_annotation_mapping_to_member_span
BEFORE INSERT OR UPDATE ON authoring.cross_annotation_mapping_to_members
FOR EACH ROW EXECUTE FUNCTION authoring.validate_cross_annotation_mapping_member_span();

CREATE TABLE authoring.alignment_groups (
  alignment_group_id uuid PRIMARY KEY,
  source_expression_id uuid NOT NULL REFERENCES authoring.digital_expressions(digital_expression_id),
  target_expression_id uuid NOT NULL REFERENCES authoring.digital_expressions(digital_expression_id),
  source_text_stream_id uuid NOT NULL,
  target_text_stream_id uuid NOT NULL,
  reference_span_id uuid NOT NULL REFERENCES authoring.reference_spans(reference_span_id),
  relation_type text NOT NULL CHECK (relation_type IN ('ONE_TO_ONE','ONE_TO_MANY','MANY_TO_ONE','MANY_TO_MANY','SOURCE_ONLY','TARGET_ONLY')),
  method text NOT NULL,
  review_status text NOT NULL,
  FOREIGN KEY (source_text_stream_id, source_expression_id)
    REFERENCES authoring.text_streams(text_stream_id, digital_expression_id),
  FOREIGN KEY (target_text_stream_id, target_expression_id)
    REFERENCES authoring.text_streams(text_stream_id, digital_expression_id)
);

CREATE TABLE authoring.alignment_source_members (
  alignment_group_id uuid NOT NULL REFERENCES authoring.alignment_groups(alignment_group_id) ON DELETE CASCADE,
  text_segment_id uuid NOT NULL REFERENCES authoring.text_segments(text_segment_id),
  member_order integer NOT NULL,
  PRIMARY KEY (alignment_group_id, member_order)
);

CREATE TABLE authoring.alignment_target_members (
  alignment_group_id uuid NOT NULL REFERENCES authoring.alignment_groups(alignment_group_id) ON DELETE CASCADE,
  text_segment_id uuid NOT NULL REFERENCES authoring.text_segments(text_segment_id),
  member_order integer NOT NULL,
  PRIMARY KEY (alignment_group_id, member_order)
);

CREATE OR REPLACE FUNCTION authoring.validate_alignment_member()
RETURNS trigger
LANGUAGE plpgsql
AS $$
DECLARE
  required_stream uuid;
  actual_stream uuid;
BEGIN
  IF TG_TABLE_NAME = 'alignment_source_members' THEN
    SELECT source_text_stream_id INTO required_stream
    FROM authoring.alignment_groups WHERE alignment_group_id = NEW.alignment_group_id;
  ELSE
    SELECT target_text_stream_id INTO required_stream
    FROM authoring.alignment_groups WHERE alignment_group_id = NEW.alignment_group_id;
  END IF;

  SELECT text_stream_id INTO actual_stream
  FROM authoring.text_segments WHERE text_segment_id = NEW.text_segment_id;

  IF required_stream IS NULL OR actual_stream IS NULL OR required_stream <> actual_stream THEN
    RAISE EXCEPTION 'alignment member belongs to wrong text stream';
  END IF;
  RETURN NEW;
END
$$;

CREATE TRIGGER alignment_source_member_stream
BEFORE INSERT OR UPDATE ON authoring.alignment_source_members
FOR EACH ROW EXECUTE FUNCTION authoring.validate_alignment_member();

CREATE TRIGGER alignment_target_member_stream
BEFORE INSERT OR UPDATE ON authoring.alignment_target_members
FOR EACH ROW EXECUTE FUNCTION authoring.validate_alignment_member();

CREATE TABLE authoring.semantic_sets (
  semantic_set_id uuid PRIMARY KEY,
  name text NOT NULL,
  description text,
  owner_user_id uuid,
  set_scope text NOT NULL,
  official_status text NOT NULL,
  current_version_id uuid
);

CREATE TABLE authoring.semantic_set_versions (
  semantic_set_version_id uuid PRIMARY KEY REFERENCES authoring.research_objects(research_object_id),
  semantic_set_id uuid NOT NULL REFERENCES authoring.semantic_sets(semantic_set_id),
  version_number integer NOT NULL,
  definition_json jsonb NOT NULL,
  review_status text NOT NULL,
  created_at timestamptz NOT NULL DEFAULT now(),
  UNIQUE (semantic_set_id, version_number)
);

ALTER TABLE authoring.semantic_sets
  ADD CONSTRAINT semantic_sets_current_version_fk
  FOREIGN KEY (current_version_id) REFERENCES authoring.semantic_set_versions(semantic_set_version_id);

CREATE TABLE authoring.semantic_set_members (
  semantic_set_version_id uuid NOT NULL REFERENCES authoring.semantic_set_versions(semantic_set_version_id) ON DELETE CASCADE,
  member_object_type text NOT NULL,
  member_object_id uuid,
  member_key text,
  inclusion_type text NOT NULL,
  reason text,
  review_status text NOT NULL,
  CHECK (member_object_id IS NOT NULL OR member_key IS NOT NULL),
  PRIMARY KEY (semantic_set_version_id, member_object_type, member_key)
);

CREATE TABLE authoring.construction_definitions (
  construction_definition_id uuid PRIMARY KEY,
  name text NOT NULL,
  description text,
  current_version_id uuid,
  status text NOT NULL
);

CREATE TABLE authoring.construction_definition_versions (
  construction_definition_version_id uuid PRIMARY KEY REFERENCES authoring.research_objects(research_object_id),
  construction_definition_id uuid NOT NULL REFERENCES authoring.construction_definitions(construction_definition_id),
  version_number integer NOT NULL,
  dsl_version text NOT NULL,
  query_ast jsonb NOT NULL,
  query_ast_hash text NOT NULL,
  review_status text NOT NULL,
  created_at timestamptz NOT NULL DEFAULT now(),
  UNIQUE (construction_definition_id, version_number)
);

ALTER TABLE authoring.construction_definitions
  ADD CONSTRAINT construction_definitions_current_version_fk
  FOREIGN KEY (current_version_id) REFERENCES authoring.construction_definition_versions(construction_definition_version_id);

CREATE TABLE authoring.construction_compilation_runs (
  construction_compilation_run_id uuid PRIMARY KEY,
  construction_definition_version_id uuid NOT NULL REFERENCES authoring.construction_definition_versions(construction_definition_version_id),
  corpus_release_id uuid NOT NULL REFERENCES authoring.corpus_releases(corpus_release_id),
  query_ast_hash text NOT NULL,
  dependency_manifest jsonb NOT NULL,
  compiler_version text NOT NULL,
  started_at timestamptz NOT NULL,
  completed_at timestamptz,
  result_count integer,
  result_set_hash text,
  status text NOT NULL
);

CREATE TABLE authoring.construction_instances (
  construction_instance_id uuid PRIMARY KEY,
  construction_compilation_run_id uuid NOT NULL REFERENCES authoring.construction_compilation_runs(construction_compilation_run_id),
  reference_span_id uuid NOT NULL REFERENCES authoring.reference_spans(reference_span_id),
  node_bindings jsonb NOT NULL,
  match_explanation jsonb NOT NULL,
  review_status text NOT NULL,
  result_hash text NOT NULL,
  UNIQUE (construction_compilation_run_id, reference_span_id, result_hash)
);

CREATE TABLE authoring.rules (
  rule_id uuid PRIMARY KEY,
  name text NOT NULL,
  rule_kind text NOT NULL CHECK (rule_kind IN ('LINGUISTIC_HEURISTIC','TRANSLATION_POLICY','PASSAGE_OVERRIDE','EDITORIAL_CONVENTION')),
  status text NOT NULL,
  current_version_id uuid
);

CREATE TABLE authoring.rule_versions (
  rule_version_id uuid PRIMARY KEY REFERENCES authoring.research_objects(research_object_id),
  rule_id uuid NOT NULL REFERENCES authoring.rules(rule_id),
  version_number integer NOT NULL,
  scope_json jsonb NOT NULL,
  trigger_construction_version_id uuid REFERENCES authoring.construction_definition_versions(construction_definition_version_id),
  condition_ast jsonb,
  implication_json jsonb NOT NULL,
  priority integer,
  specificity integer,
  review_status text NOT NULL,
  created_at timestamptz NOT NULL DEFAULT now(),
  UNIQUE (rule_id, version_number)
);

ALTER TABLE authoring.rules
  ADD CONSTRAINT rules_current_version_fk
  FOREIGN KEY (current_version_id) REFERENCES authoring.rule_versions(rule_version_id);

CREATE TABLE authoring.rule_applications (
  rule_application_id uuid PRIMARY KEY,
  rule_version_id uuid NOT NULL REFERENCES authoring.rule_versions(rule_version_id),
  construction_instance_id uuid REFERENCES authoring.construction_instances(construction_instance_id),
  reference_span_id uuid NOT NULL REFERENCES authoring.reference_spans(reference_span_id),
  matched_conditions jsonb NOT NULL,
  failed_conditions jsonb,
  exception_status text NOT NULL,
  effect text NOT NULL CHECK (effect IN ('SUPPORTS','DISFAVOURS','REQUIRES','PROHIBITS','QUALIFIES','NO_DECISION')),
  result_json jsonb NOT NULL,
  review_status text NOT NULL,
  result_hash text NOT NULL
);

CREATE TABLE authoring.translation_source_bases (
  translation_source_basis_id uuid PRIMARY KEY REFERENCES authoring.research_objects(research_object_id),
  reference_span_id uuid NOT NULL REFERENCES authoring.reference_spans(reference_span_id),
  source_digital_expression_id uuid NOT NULL REFERENCES authoring.digital_expressions(digital_expression_id),
  source_text_stream_id uuid NOT NULL,
  basis_kind text NOT NULL CHECK (basis_kind IN ('STREAM_READING','APPARATUS_READING','EDITORIAL_EMENDATION','COMPOSITE_EDITORIAL_READING')),
  adopted_reading_text text,
  review_status text NOT NULL,
  content_hash text NOT NULL,
  created_at timestamptz NOT NULL DEFAULT now(),
  FOREIGN KEY (source_text_stream_id, source_digital_expression_id)
    REFERENCES authoring.text_streams(text_stream_id, digital_expression_id),
  CHECK (
    (basis_kind IN ('EDITORIAL_EMENDATION','COMPOSITE_EDITORIAL_READING') AND adopted_reading_text IS NOT NULL AND length(adopted_reading_text) > 0)
    OR
    (basis_kind IN ('STREAM_READING','APPARATUS_READING') AND adopted_reading_text IS NULL)
  )
);

CREATE TABLE authoring.translation_source_basis_segments (
  translation_source_basis_id uuid NOT NULL REFERENCES authoring.translation_source_bases(translation_source_basis_id) ON DELETE CASCADE,
  text_segment_id uuid NOT NULL REFERENCES authoring.text_segments(text_segment_id),
  member_order integer NOT NULL,
  PRIMARY KEY (translation_source_basis_id, member_order),
  UNIQUE (translation_source_basis_id, text_segment_id)
);

CREATE OR REPLACE FUNCTION authoring.span_covers(parent_span uuid, child_span uuid)
RETURNS boolean
LANGUAGE sql
STABLE
AS $$
  SELECT p.book_id = c.book_id
     AND p.start_sequence <= c.start_sequence
     AND p.end_sequence >= c.end_sequence
  FROM authoring.reference_spans p, authoring.reference_spans c
  WHERE p.reference_span_id = parent_span
    AND c.reference_span_id = child_span
$$;

CREATE OR REPLACE FUNCTION authoring.validate_source_basis_segment()
RETURNS trigger
LANGUAGE plpgsql
AS $$
DECLARE
  basis_stream uuid;
  basis_span uuid;
  segment_stream uuid;
  segment_span uuid;
BEGIN
  SELECT source_text_stream_id, reference_span_id
    INTO basis_stream, basis_span
  FROM authoring.translation_source_bases
  WHERE translation_source_basis_id = NEW.translation_source_basis_id;

  SELECT text_stream_id, reference_span_id
    INTO segment_stream, segment_span
  FROM authoring.text_segments
  WHERE text_segment_id = NEW.text_segment_id;

  IF basis_stream <> segment_stream THEN
    RAISE EXCEPTION 'translation source-basis segment belongs to wrong stream';
  END IF;
  IF NOT authoring.span_covers(basis_span, segment_span) THEN
    RAISE EXCEPTION 'translation source-basis segment falls outside basis locus';
  END IF;
  RETURN NEW;
END
$$;

CREATE TRIGGER translation_source_basis_segment_integrity
BEFORE INSERT OR UPDATE ON authoring.translation_source_basis_segments
FOR EACH ROW EXECUTE FUNCTION authoring.validate_source_basis_segment();

CREATE TABLE authoring.translation_policies (
  translation_policy_id uuid PRIMARY KEY,
  policy_key text NOT NULL UNIQUE,
  current_version_id uuid,
  created_at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE authoring.translation_policy_versions (
  translation_policy_version_id uuid PRIMARY KEY REFERENCES authoring.research_objects(research_object_id),
  translation_policy_id uuid NOT NULL REFERENCES authoring.translation_policies(translation_policy_id),
  version_number integer NOT NULL,
  target_language_tag text NOT NULL,
  audience_profile text NOT NULL,
  register text NOT NULL,
  ambiguity_policy text NOT NULL,
  policy_summary text,
  review_status text NOT NULL,
  content_hash text NOT NULL,
  supersedes_version_id uuid REFERENCES authoring.translation_policy_versions(translation_policy_version_id),
  UNIQUE (translation_policy_id, version_number)
);

ALTER TABLE authoring.translation_policies
  ADD CONSTRAINT translation_policies_current_version_fk
  FOREIGN KEY (current_version_id) REFERENCES authoring.translation_policy_versions(translation_policy_version_id);

CREATE TABLE authoring.translation_policy_rule_members (
  translation_policy_version_id uuid NOT NULL REFERENCES authoring.translation_policy_versions(translation_policy_version_id) ON DELETE CASCADE,
  rule_version_id uuid NOT NULL REFERENCES authoring.rule_versions(rule_version_id),
  member_kind text NOT NULL CHECK (member_kind IN ('TRANSLATION_POLICY','EDITORIAL_CONVENTION')),
  PRIMARY KEY (translation_policy_version_id, rule_version_id)
);

CREATE OR REPLACE FUNCTION authoring.validate_translation_policy_rule_member()
RETURNS trigger
LANGUAGE plpgsql
AS $$
DECLARE
  actual_kind text;
BEGIN
  SELECT r.rule_kind INTO actual_kind
  FROM authoring.rule_versions rv
  JOIN authoring.rules r ON r.rule_id = rv.rule_id
  WHERE rv.rule_version_id = NEW.rule_version_id;

  IF actual_kind <> NEW.member_kind THEN
    RAISE EXCEPTION 'translation policy member kind does not match RuleVersion kind';
  END IF;
  RETURN NEW;
END
$$;

CREATE TRIGGER translation_policy_rule_member_kind
BEFORE INSERT OR UPDATE ON authoring.translation_policy_rule_members
FOR EACH ROW EXECUTE FUNCTION authoring.validate_translation_policy_rule_member();

CREATE TABLE authoring.translation_decisions (
  translation_decision_id uuid PRIMARY KEY,
  reference_span_id uuid NOT NULL REFERENCES authoring.reference_spans(reference_span_id),
  translation_source_basis_id uuid NOT NULL REFERENCES authoring.translation_source_bases(translation_source_basis_id),
  translation_policy_version_id uuid NOT NULL REFERENCES authoring.translation_policy_versions(translation_policy_version_id),
  target_language_tag text NOT NULL,
  decision_kind text NOT NULL,
  selected_rendering text,
  ambiguity_strategy text,
  decision_schema_version text NOT NULL,
  decision_payload jsonb NOT NULL,
  review_status text NOT NULL,
  supersedes_decision_id uuid REFERENCES authoring.translation_decisions(translation_decision_id)
);

CREATE OR REPLACE FUNCTION authoring.validate_translation_decision()
RETURNS trigger
LANGUAGE plpgsql
AS $$
DECLARE
  basis_span uuid;
  policy_language text;
BEGIN
  SELECT reference_span_id INTO basis_span
  FROM authoring.translation_source_bases
  WHERE translation_source_basis_id = NEW.translation_source_basis_id;

  SELECT target_language_tag INTO policy_language
  FROM authoring.translation_policy_versions
  WHERE translation_policy_version_id = NEW.translation_policy_version_id;

  IF NOT authoring.span_covers(basis_span, NEW.reference_span_id) THEN
    RAISE EXCEPTION 'TranslationDecision locus is not covered by TranslationSourceBasis';
  END IF;
  IF policy_language <> NEW.target_language_tag THEN
    RAISE EXCEPTION 'TranslationDecision target language differs from TranslationPolicyVersion';
  END IF;
  RETURN NEW;
END
$$;

CREATE TRIGGER translation_decision_integrity
BEFORE INSERT OR UPDATE ON authoring.translation_decisions
FOR EACH ROW EXECUTE FUNCTION authoring.validate_translation_decision();

CREATE TABLE authoring.research_issues (
  research_issue_id uuid PRIMARY KEY,
  issue_key text UNIQUE,
  current_version_id uuid,
  created_at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE authoring.research_issue_versions (
  research_issue_version_id uuid PRIMARY KEY REFERENCES authoring.research_objects(research_object_id),
  research_issue_id uuid NOT NULL REFERENCES authoring.research_issues(research_issue_id),
  version_number integer NOT NULL,
  title text NOT NULL,
  question_text text NOT NULL,
  issue_type text NOT NULL,
  debate_status text NOT NULL,
  classification_basis text,
  review_status text NOT NULL,
  content_hash text NOT NULL,
  created_at timestamptz NOT NULL DEFAULT now(),
  UNIQUE (research_issue_id, version_number),
  UNIQUE (research_issue_version_id, research_issue_id)
);

ALTER TABLE authoring.research_issues
  ADD CONSTRAINT research_issues_current_version_fk
  FOREIGN KEY (current_version_id) REFERENCES authoring.research_issue_versions(research_issue_version_id);

CREATE TABLE authoring.research_positions (
  research_position_id uuid PRIMARY KEY,
  research_issue_id uuid NOT NULL REFERENCES authoring.research_issues(research_issue_id),
  position_key text,
  current_version_id uuid,
  created_at timestamptz NOT NULL DEFAULT now(),
  UNIQUE (research_position_id, research_issue_id)
);

CREATE TABLE authoring.research_position_versions (
  research_position_version_id uuid PRIMARY KEY REFERENCES authoring.research_objects(research_object_id),
  research_position_id uuid NOT NULL,
  research_issue_id uuid NOT NULL,
  research_issue_version_id uuid NOT NULL,
  version_number integer NOT NULL,
  title text NOT NULL,
  position_summary text NOT NULL,
  position_status text NOT NULL,
  review_status text NOT NULL,
  content_hash text NOT NULL,
  created_at timestamptz NOT NULL DEFAULT now(),
  FOREIGN KEY (research_position_id, research_issue_id)
    REFERENCES authoring.research_positions(research_position_id, research_issue_id),
  FOREIGN KEY (research_issue_version_id, research_issue_id)
    REFERENCES authoring.research_issue_versions(research_issue_version_id, research_issue_id),
  UNIQUE (research_position_id, version_number)
);

ALTER TABLE authoring.research_positions
  ADD CONSTRAINT research_positions_current_version_fk
  FOREIGN KEY (current_version_id) REFERENCES authoring.research_position_versions(research_position_version_id);

CREATE OR REPLACE FUNCTION authoring.enforce_research_object_type()
RETURNS trigger
LANGUAGE plpgsql
AS $research_object_type$
DECLARE
  object_id uuid;
  actual_type text;
BEGIN
  object_id := (to_jsonb(NEW)->>TG_ARGV[1])::uuid;
  SELECT object_type INTO actual_type
  FROM authoring.research_objects
  WHERE research_object_id = object_id;

  IF actual_type IS NULL THEN
    RAISE EXCEPTION 'research object % is not registered', object_id;
  END IF;

  IF actual_type <> TG_ARGV[0] THEN
    RAISE EXCEPTION 'research object % has type %, expected %',
      object_id, actual_type, TG_ARGV[0];
  END IF;

  RETURN NEW;
END
$research_object_type$;

CREATE TRIGGER corpus_release_object_type
BEFORE INSERT OR UPDATE ON authoring.corpus_releases
FOR EACH ROW EXECUTE FUNCTION authoring.enforce_research_object_type('CORPUS_RELEASE','corpus_release_id');

CREATE TRIGGER annotation_layer_object_type
BEFORE INSERT OR UPDATE ON authoring.annotation_layers
FOR EACH ROW EXECUTE FUNCTION authoring.enforce_research_object_type('ANNOTATION_LAYER','annotation_layer_id');

CREATE TRIGGER semantic_set_version_object_type
BEFORE INSERT OR UPDATE ON authoring.semantic_set_versions
FOR EACH ROW EXECUTE FUNCTION authoring.enforce_research_object_type('SEMANTIC_SET_VERSION','semantic_set_version_id');

CREATE TRIGGER construction_definition_version_object_type
BEFORE INSERT OR UPDATE ON authoring.construction_definition_versions
FOR EACH ROW EXECUTE FUNCTION authoring.enforce_research_object_type('CONSTRUCTION_DEFINITION_VERSION','construction_definition_version_id');

CREATE TRIGGER rule_version_object_type
BEFORE INSERT OR UPDATE ON authoring.rule_versions
FOR EACH ROW EXECUTE FUNCTION authoring.enforce_research_object_type('RULE_VERSION','rule_version_id');

CREATE TRIGGER translation_source_basis_object_type
BEFORE INSERT OR UPDATE ON authoring.translation_source_bases
FOR EACH ROW EXECUTE FUNCTION authoring.enforce_research_object_type('TRANSLATION_SOURCE_BASIS','translation_source_basis_id');

CREATE TRIGGER translation_policy_version_object_type
BEFORE INSERT OR UPDATE ON authoring.translation_policy_versions
FOR EACH ROW EXECUTE FUNCTION authoring.enforce_research_object_type('TRANSLATION_POLICY_VERSION','translation_policy_version_id');

CREATE TRIGGER research_issue_version_object_type
BEFORE INSERT OR UPDATE ON authoring.research_issue_versions
FOR EACH ROW EXECUTE FUNCTION authoring.enforce_research_object_type('RESEARCH_ISSUE_VERSION','research_issue_version_id');

CREATE TRIGGER research_position_version_object_type
BEFORE INSERT OR UPDATE ON authoring.research_position_versions
FOR EACH ROW EXECUTE FUNCTION authoring.enforce_research_object_type('RESEARCH_POSITION_VERSION','research_position_version_id');

CREATE OR REPLACE FUNCTION authoring.valid_rights_conditions(value jsonb)
RETURNS boolean
LANGUAGE plpgsql
IMMUTABLE
AS $rights_conditions$
DECLARE
  e jsonb;
  payload jsonb;
BEGIN
  IF value IS NULL THEN RETURN true; END IF;
  IF jsonb_typeof(value) <> 'array' THEN RETURN false; END IF;
  IF jsonb_array_length(value) <> (
    SELECT count(DISTINCT item) FROM jsonb_array_elements(value) AS x(item)
  ) THEN RETURN false; END IF;
  FOR e IN SELECT item FROM jsonb_array_elements(value) AS x(item)
  LOOP
    IF jsonb_typeof(e) <> 'object'
       OR NOT (e ?& ARRAY['conditionSchemaId','conditionSchemaVersion','evaluatorVersion','payload'])
       OR (SELECT count(*) FROM jsonb_object_keys(e)) <> 4
       OR jsonb_typeof(e->'conditionSchemaId') <> 'string'
       OR jsonb_typeof(e->'conditionSchemaVersion') <> 'string'
       OR e->>'conditionSchemaVersion' <> '1.0'
       OR jsonb_typeof(e->'evaluatorVersion') <> 'string'
       OR length(e->>'evaluatorVersion') = 0
       OR jsonb_typeof(e->'payload') <> 'object'
    THEN RETURN false; END IF;
    payload := e->'payload';
    CASE e->>'conditionSchemaId'
      WHEN 'AUTHENTICATED_AUDIENCE' THEN
        IF payload <> '{"required":true}'::jsonb THEN RETURN false; END IF;
      WHEN 'TERRITORY_ALLOWLIST' THEN
        IF NOT (payload ? 'territories')
           OR (SELECT count(*) FROM jsonb_object_keys(payload)) <> 1
           OR jsonb_typeof(payload->'territories') <> 'array'
           OR jsonb_array_length(payload->'territories') = 0
           OR jsonb_array_length(payload->'territories') <> (
             SELECT count(DISTINCT item) FROM jsonb_array_elements(payload->'territories') AS x(item))
           OR EXISTS (SELECT 1 FROM jsonb_array_elements(payload->'territories') AS x(item)
                      WHERE jsonb_typeof(item) <> 'string' OR length(item #>> '{}') < 2)
        THEN RETURN false; END IF;
      WHEN 'PURPOSE_ALLOWLIST' THEN
        IF NOT (payload ? 'purposes')
           OR (SELECT count(*) FROM jsonb_object_keys(payload)) <> 1
           OR jsonb_typeof(payload->'purposes') <> 'array'
           OR jsonb_array_length(payload->'purposes') = 0
           OR jsonb_array_length(payload->'purposes') <> (
             SELECT count(DISTINCT item) FROM jsonb_array_elements(payload->'purposes') AS x(item))
           OR EXISTS (SELECT 1 FROM jsonb_array_elements(payload->'purposes') AS x(item)
                      WHERE jsonb_typeof(item) <> 'string'
                         OR (item #>> '{}') NOT IN (
                           'PRIVATE_RESEARCH','RESEARCH_COMPILATION','PUBLICATION','PUBLIC_DISPLAY',
                           'USER_WORKSPACE','MODEL_ASSISTANCE','EXPORT'))
        THEN RETURN false; END IF;
      WHEN 'COMMERCIAL_CONTEXT_ALLOWLIST' THEN
        IF NOT (payload ? 'contexts')
           OR (SELECT count(*) FROM jsonb_object_keys(payload)) <> 1
           OR jsonb_typeof(payload->'contexts') <> 'array'
           OR jsonb_array_length(payload->'contexts') = 0
           OR jsonb_array_length(payload->'contexts') <> (
             SELECT count(DISTINCT item) FROM jsonb_array_elements(payload->'contexts') AS x(item))
           OR EXISTS (SELECT 1 FROM jsonb_array_elements(payload->'contexts') AS x(item)
                      WHERE jsonb_typeof(item) <> 'string'
                         OR (item #>> '{}') NOT IN ('NONCOMMERCIAL','COMMERCIAL','MIXED','UNKNOWN'))
        THEN RETURN false; END IF;
      WHEN 'PROVIDER_TERMS_VERSION' THEN
        IF NOT (payload ? 'providerTermsVersion')
           OR (SELECT count(*) FROM jsonb_object_keys(payload)) <> 1
           OR jsonb_typeof(payload->'providerTermsVersion') <> 'string'
           OR length(payload->>'providerTermsVersion') = 0
        THEN RETURN false; END IF;
      ELSE RETURN false;
    END CASE;
  END LOOP;
  RETURN true;
END
$rights_conditions$;

CREATE OR REPLACE FUNCTION authoring.valid_rights_obligations(value jsonb)
RETURNS boolean
LANGUAGE plpgsql
IMMUTABLE
AS $rights_obligations$
DECLARE
  e jsonb;
BEGIN
  IF value IS NULL THEN RETURN true; END IF;
  IF jsonb_typeof(value) <> 'array' THEN RETURN false; END IF;
  IF jsonb_array_length(value) <> (
    SELECT count(DISTINCT item) FROM jsonb_array_elements(value) AS x(item)
  ) THEN RETURN false; END IF;
  FOR e IN SELECT item FROM jsonb_array_elements(value) AS x(item)
  LOOP
    IF jsonb_typeof(e) <> 'object' OR NOT (e ? 'obligationType')
       OR jsonb_typeof(e->'obligationType') <> 'string' THEN RETURN false; END IF;
    CASE e->>'obligationType'
      WHEN 'ATTRIBUTION' THEN
        IF NOT (e ?& ARRAY['obligationType','value'])
           OR (SELECT count(*) FROM jsonb_object_keys(e)) <> 2
           OR jsonb_typeof(e->'value') <> 'string' OR length(e->>'value') = 0
        THEN RETURN false; END IF;
      WHEN 'MAX_EXCERPT' THEN
        IF NOT (e ?& ARRAY['obligationType','value','unit'])
           OR (SELECT count(*) FROM jsonb_object_keys(e)) <> 3
           OR jsonb_typeof(e->'value') <> 'number' OR (e->>'value')::numeric <= 0
           OR jsonb_typeof(e->'unit') <> 'string'
           OR e->>'unit' NOT IN ('WORD','UNICODE_CODEPOINT','GRAPHEME_CLUSTER','BYTE','PERCENT_OF_WORK')
        THEN RETURN false; END IF;
      WHEN 'RETENTION_LIMIT' THEN
        IF NOT (e ?& ARRAY['obligationType','value','unit'])
           OR (SELECT count(*) FROM jsonb_object_keys(e)) <> 3
           OR jsonb_typeof(e->'value') <> 'number' OR (e->>'value')::numeric < 0
           OR trunc((e->>'value')::numeric) <> (e->>'value')::numeric OR e->>'unit' <> 'DAY'
        THEN RETURN false; END IF;
      WHEN 'AUTHENTICATED_ONLY' THEN
        IF (SELECT count(*) FROM jsonb_object_keys(e)) <> 1 THEN RETURN false; END IF;
      WHEN 'TERRITORY_LIMIT' THEN
        IF NOT (e ?& ARRAY['obligationType','value'])
           OR (SELECT count(*) FROM jsonb_object_keys(e)) <> 2
           OR jsonb_typeof(e->'value') <> 'array' OR jsonb_array_length(e->'value') = 0
           OR jsonb_array_length(e->'value') <> (
             SELECT count(DISTINCT item) FROM jsonb_array_elements(e->'value') AS x(item))
           OR EXISTS (SELECT 1 FROM jsonb_array_elements(e->'value') AS x(item)
                      WHERE jsonb_typeof(item) <> 'string' OR length(item #>> '{}') < 2)
        THEN RETURN false; END IF;
      WHEN 'TEMPORARY_PROCESSING_ONLY' THEN
        IF (SELECT count(*) FROM jsonb_object_keys(e)) <> 1 THEN RETURN false; END IF;
      ELSE RETURN false;
    END CASE;
  END LOOP;
  RETURN true;
END
$rights_obligations$;

CREATE TABLE authoring.rights_policies (
  rights_policy_id uuid PRIMARY KEY,
  policy_key text NOT NULL,
  policy_version text NOT NULL,
  rights_basis text NOT NULL,
  effective_from timestamptz,
  effective_until timestamptz,
  territory text,
  verified_at timestamptz,
  UNIQUE (policy_key, policy_version),
  CHECK (effective_until IS NULL OR effective_from IS NULL OR effective_until >= effective_from)
);

CREATE TABLE authoring.rights_rules (
  rights_rule_id uuid PRIMARY KEY,
  rights_policy_id uuid NOT NULL REFERENCES authoring.rights_policies(rights_policy_id),
  operation text NOT NULL,
  decision text NOT NULL CHECK (decision IN ('ALLOW','DENY','CONDITIONAL','UNKNOWN')),
  purpose_scope text,
  audience_scope text,
  commercial_context text,
  max_excerpt_value numeric,
  excerpt_unit text,
  conditions_json jsonb,
  attribution_requirement text,
  CHECK ((max_excerpt_value IS NULL) = (excerpt_unit IS NULL)),
  CHECK (excerpt_unit IS NULL OR excerpt_unit IN ('WORD','UNICODE_CODEPOINT','GRAPHEME_CLUSTER','BYTE','PERCENT_OF_WORK')),
  CHECK (authoring.valid_rights_conditions(conditions_json))
);

CREATE OR REPLACE FUNCTION authoring.evaluate_rights(
  p_policy_id uuid,
  p_operation text,
  p_purpose text,
  p_audience text,
  p_commercial text
)
RETURNS text
LANGUAGE sql
STABLE
AS $$
  WITH candidates AS (
    SELECT rr.decision,
           ((rr.purpose_scope IS NOT NULL)::int +
            (rr.audience_scope IS NOT NULL)::int +
            (rr.commercial_context IS NOT NULL)::int) AS specificity
    FROM authoring.rights_rules rr
    WHERE rr.rights_policy_id = p_policy_id
      AND rr.operation = p_operation
      AND (rr.purpose_scope IS NULL OR rr.purpose_scope = p_purpose)
      AND (rr.audience_scope IS NULL OR rr.audience_scope = p_audience)
      AND (rr.commercial_context IS NULL OR rr.commercial_context = p_commercial)
  ),
  top_scope AS (
    SELECT * FROM candidates
    WHERE specificity = COALESCE((SELECT max(specificity) FROM candidates), -1)
  ),
  winner AS (
    SELECT decision
    FROM top_scope
    ORDER BY CASE decision
      WHEN 'UNKNOWN' THEN 4
      WHEN 'DENY' THEN 3
      WHEN 'CONDITIONAL' THEN 2
      WHEN 'ALLOW' THEN 1
      ELSE 0 END DESC
    LIMIT 1
  )
  SELECT COALESCE(
    (SELECT CASE WHEN decision = 'UNKNOWN' THEN 'DENY' ELSE decision END FROM winner),
    'DENY'
  )
$$;

CREATE OR REPLACE FUNCTION serving.valid_rights_conditions(value jsonb)
RETURNS boolean
LANGUAGE plpgsql
IMMUTABLE
AS $rights_conditions$
DECLARE
  e jsonb;
  payload jsonb;
BEGIN
  IF value IS NULL THEN RETURN true; END IF;
  IF jsonb_typeof(value) <> 'array' THEN RETURN false; END IF;
  IF jsonb_array_length(value) <> (
    SELECT count(DISTINCT item) FROM jsonb_array_elements(value) AS x(item)
  ) THEN RETURN false; END IF;
  FOR e IN SELECT item FROM jsonb_array_elements(value) AS x(item)
  LOOP
    IF jsonb_typeof(e) <> 'object'
       OR NOT (e ?& ARRAY['conditionSchemaId','conditionSchemaVersion','evaluatorVersion','payload'])
       OR (SELECT count(*) FROM jsonb_object_keys(e)) <> 4
       OR jsonb_typeof(e->'conditionSchemaId') <> 'string'
       OR jsonb_typeof(e->'conditionSchemaVersion') <> 'string'
       OR e->>'conditionSchemaVersion' <> '1.0'
       OR jsonb_typeof(e->'evaluatorVersion') <> 'string'
       OR length(e->>'evaluatorVersion') = 0
       OR jsonb_typeof(e->'payload') <> 'object'
    THEN RETURN false; END IF;
    payload := e->'payload';
    CASE e->>'conditionSchemaId'
      WHEN 'AUTHENTICATED_AUDIENCE' THEN
        IF payload <> '{"required":true}'::jsonb THEN RETURN false; END IF;
      WHEN 'TERRITORY_ALLOWLIST' THEN
        IF NOT (payload ? 'territories')
           OR (SELECT count(*) FROM jsonb_object_keys(payload)) <> 1
           OR jsonb_typeof(payload->'territories') <> 'array'
           OR jsonb_array_length(payload->'territories') = 0
           OR jsonb_array_length(payload->'territories') <> (
             SELECT count(DISTINCT item) FROM jsonb_array_elements(payload->'territories') AS x(item))
           OR EXISTS (SELECT 1 FROM jsonb_array_elements(payload->'territories') AS x(item)
                      WHERE jsonb_typeof(item) <> 'string' OR length(item #>> '{}') < 2)
        THEN RETURN false; END IF;
      WHEN 'PURPOSE_ALLOWLIST' THEN
        IF NOT (payload ? 'purposes')
           OR (SELECT count(*) FROM jsonb_object_keys(payload)) <> 1
           OR jsonb_typeof(payload->'purposes') <> 'array'
           OR jsonb_array_length(payload->'purposes') = 0
           OR jsonb_array_length(payload->'purposes') <> (
             SELECT count(DISTINCT item) FROM jsonb_array_elements(payload->'purposes') AS x(item))
           OR EXISTS (SELECT 1 FROM jsonb_array_elements(payload->'purposes') AS x(item)
                      WHERE jsonb_typeof(item) <> 'string'
                         OR (item #>> '{}') NOT IN (
                           'PRIVATE_RESEARCH','RESEARCH_COMPILATION','PUBLICATION','PUBLIC_DISPLAY',
                           'USER_WORKSPACE','MODEL_ASSISTANCE','EXPORT'))
        THEN RETURN false; END IF;
      WHEN 'COMMERCIAL_CONTEXT_ALLOWLIST' THEN
        IF NOT (payload ? 'contexts')
           OR (SELECT count(*) FROM jsonb_object_keys(payload)) <> 1
           OR jsonb_typeof(payload->'contexts') <> 'array'
           OR jsonb_array_length(payload->'contexts') = 0
           OR jsonb_array_length(payload->'contexts') <> (
             SELECT count(DISTINCT item) FROM jsonb_array_elements(payload->'contexts') AS x(item))
           OR EXISTS (SELECT 1 FROM jsonb_array_elements(payload->'contexts') AS x(item)
                      WHERE jsonb_typeof(item) <> 'string'
                         OR (item #>> '{}') NOT IN ('NONCOMMERCIAL','COMMERCIAL','MIXED','UNKNOWN'))
        THEN RETURN false; END IF;
      WHEN 'PROVIDER_TERMS_VERSION' THEN
        IF NOT (payload ? 'providerTermsVersion')
           OR (SELECT count(*) FROM jsonb_object_keys(payload)) <> 1
           OR jsonb_typeof(payload->'providerTermsVersion') <> 'string'
           OR length(payload->>'providerTermsVersion') = 0
        THEN RETURN false; END IF;
      ELSE RETURN false;
    END CASE;
  END LOOP;
  RETURN true;
END
$rights_conditions$;

CREATE OR REPLACE FUNCTION serving.valid_rights_obligations(value jsonb)
RETURNS boolean
LANGUAGE plpgsql
IMMUTABLE
AS $rights_obligations$
DECLARE
  e jsonb;
BEGIN
  IF value IS NULL THEN RETURN true; END IF;
  IF jsonb_typeof(value) <> 'array' THEN RETURN false; END IF;
  IF jsonb_array_length(value) <> (
    SELECT count(DISTINCT item) FROM jsonb_array_elements(value) AS x(item)
  ) THEN RETURN false; END IF;
  FOR e IN SELECT item FROM jsonb_array_elements(value) AS x(item)
  LOOP
    IF jsonb_typeof(e) <> 'object' OR NOT (e ? 'obligationType')
       OR jsonb_typeof(e->'obligationType') <> 'string' THEN RETURN false; END IF;
    CASE e->>'obligationType'
      WHEN 'ATTRIBUTION' THEN
        IF NOT (e ?& ARRAY['obligationType','value'])
           OR (SELECT count(*) FROM jsonb_object_keys(e)) <> 2
           OR jsonb_typeof(e->'value') <> 'string' OR length(e->>'value') = 0
        THEN RETURN false; END IF;
      WHEN 'MAX_EXCERPT' THEN
        IF NOT (e ?& ARRAY['obligationType','value','unit'])
           OR (SELECT count(*) FROM jsonb_object_keys(e)) <> 3
           OR jsonb_typeof(e->'value') <> 'number' OR (e->>'value')::numeric <= 0
           OR jsonb_typeof(e->'unit') <> 'string'
           OR e->>'unit' NOT IN ('WORD','UNICODE_CODEPOINT','GRAPHEME_CLUSTER','BYTE','PERCENT_OF_WORK')
        THEN RETURN false; END IF;
      WHEN 'RETENTION_LIMIT' THEN
        IF NOT (e ?& ARRAY['obligationType','value','unit'])
           OR (SELECT count(*) FROM jsonb_object_keys(e)) <> 3
           OR jsonb_typeof(e->'value') <> 'number' OR (e->>'value')::numeric < 0
           OR trunc((e->>'value')::numeric) <> (e->>'value')::numeric OR e->>'unit' <> 'DAY'
        THEN RETURN false; END IF;
      WHEN 'AUTHENTICATED_ONLY' THEN
        IF (SELECT count(*) FROM jsonb_object_keys(e)) <> 1 THEN RETURN false; END IF;
      WHEN 'TERRITORY_LIMIT' THEN
        IF NOT (e ?& ARRAY['obligationType','value'])
           OR (SELECT count(*) FROM jsonb_object_keys(e)) <> 2
           OR jsonb_typeof(e->'value') <> 'array' OR jsonb_array_length(e->'value') = 0
           OR jsonb_array_length(e->'value') <> (
             SELECT count(DISTINCT item) FROM jsonb_array_elements(e->'value') AS x(item))
           OR EXISTS (SELECT 1 FROM jsonb_array_elements(e->'value') AS x(item)
                      WHERE jsonb_typeof(item) <> 'string' OR length(item #>> '{}') < 2)
        THEN RETURN false; END IF;
      WHEN 'TEMPORARY_PROCESSING_ONLY' THEN
        IF (SELECT count(*) FROM jsonb_object_keys(e)) <> 1 THEN RETURN false; END IF;
      ELSE RETURN false;
    END CASE;
  END LOOP;
  RETURN true;
END
$rights_obligations$;

CREATE OR REPLACE FUNCTION serving.valid_citation_locator(value jsonb)
RETURNS boolean
LANGUAGE plpgsql
IMMUTABLE
AS $citation_locator$
DECLARE
  locator_type text;
  key_name text;
  uuid_pattern constant text :=
    '^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[1-5][0-9a-fA-F]{3}-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}$';
BEGIN
  IF value IS NULL THEN
    RETURN true;
  END IF;

  IF jsonb_typeof(value) <> 'object' THEN
    RETURN false;
  END IF;

  locator_type := value->>'locatorType';
  IF locator_type IS NULL OR locator_type NOT IN (
    'SOURCE_SPAN','PRINTED_PAGE','SOURCE_ASSET_PAGE','DOCUMENT_SECTION',
    'LEXICON_ENTRY','BIBLICAL_REFERENCE','CORPUS_RESULT'
  ) THEN
    RETURN false;
  END IF;

  FOR key_name IN SELECT jsonb_object_keys(value)
  LOOP
    IF key_name NOT IN (
      'locatorType','editionId','sourceAssetId','sourceSpanId','sourceAssetPageId',
      'printedPageLabel','sectionPath','entryLabel','referenceSpanId',
      'corpusQueryRunId','boundingBox'
    ) THEN
      RETURN false;
    END IF;
  END LOOP;

  IF value ? 'editionId' AND value->>'editionId' IS NOT NULL
     AND NOT ((value->>'editionId') ~* uuid_pattern) THEN RETURN false; END IF;
  IF value ? 'sourceAssetId' AND value->>'sourceAssetId' IS NOT NULL
     AND NOT ((value->>'sourceAssetId') ~* uuid_pattern) THEN RETURN false; END IF;
  IF value ? 'sourceSpanId' AND value->>'sourceSpanId' IS NOT NULL
     AND NOT ((value->>'sourceSpanId') ~* uuid_pattern) THEN RETURN false; END IF;
  IF value ? 'sourceAssetPageId' AND value->>'sourceAssetPageId' IS NOT NULL
     AND NOT ((value->>'sourceAssetPageId') ~* uuid_pattern) THEN RETURN false; END IF;
  IF value ? 'referenceSpanId' AND value->>'referenceSpanId' IS NOT NULL
     AND NOT ((value->>'referenceSpanId') ~* uuid_pattern) THEN RETURN false; END IF;
  IF value ? 'corpusQueryRunId' AND value->>'corpusQueryRunId' IS NOT NULL
     AND NOT ((value->>'corpusQueryRunId') ~* uuid_pattern) THEN RETURN false; END IF;

  CASE locator_type
    WHEN 'SOURCE_SPAN' THEN
      RETURN COALESCE(value->>'sourceSpanId','') ~* uuid_pattern;
    WHEN 'PRINTED_PAGE' THEN
      RETURN COALESCE(value->>'editionId','') ~* uuid_pattern
         AND length(COALESCE(value->>'printedPageLabel','')) > 0;
    WHEN 'SOURCE_ASSET_PAGE' THEN
      RETURN COALESCE(value->>'sourceAssetPageId','') ~* uuid_pattern;
    WHEN 'DOCUMENT_SECTION' THEN
      RETURN COALESCE(value->>'editionId','') ~* uuid_pattern
         AND jsonb_typeof(value->'sectionPath') = 'array'
         AND jsonb_array_length(value->'sectionPath') > 0
         AND NOT EXISTS (
           SELECT 1
           FROM jsonb_array_elements_text(value->'sectionPath') AS section_name
           WHERE length(section_name) = 0
         );
    WHEN 'LEXICON_ENTRY' THEN
      RETURN COALESCE(value->>'editionId','') ~* uuid_pattern
         AND length(COALESCE(value->>'entryLabel','')) > 0;
    WHEN 'BIBLICAL_REFERENCE' THEN
      RETURN COALESCE(value->>'referenceSpanId','') ~* uuid_pattern;
    WHEN 'CORPUS_RESULT' THEN
      RETURN COALESCE(value->>'corpusQueryRunId','') ~* uuid_pattern;
  END CASE;

  RETURN false;
END
$citation_locator$;

CREATE TABLE serving.research_objects (
  research_object_id uuid PRIMARY KEY,
  object_type text NOT NULL,
  source_content_hash text,
  published_at timestamptz NOT NULL
);

CREATE TABLE serving.reference_spans (
  reference_span_id uuid PRIMARY KEY,
  book_code text NOT NULL,
  start_sequence integer NOT NULL,
  end_sequence integer NOT NULL,
  reference_sort_key bigint NOT NULL UNIQUE,
  span_kind text NOT NULL,
  CHECK (start_sequence <= end_sequence)
);

CREATE TABLE serving.reference_systems (
  reference_system_id uuid PRIMARY KEY,
  code text NOT NULL UNIQUE,
  name text NOT NULL
);

CREATE TABLE serving.reference_labels (
  corpus_release_id uuid NOT NULL REFERENCES serving.research_objects(research_object_id),
  reference_label_id uuid NOT NULL,
  reference_system_id uuid NOT NULL REFERENCES serving.reference_systems(reference_system_id),
  reference_span_id uuid NOT NULL REFERENCES serving.reference_spans(reference_span_id),
  book_code text NOT NULL,
  label text NOT NULL,
  chapter_number integer,
  verse_label text,
  reference_sort_key bigint NOT NULL,
  PRIMARY KEY (corpus_release_id, reference_label_id),
  UNIQUE (corpus_release_id, reference_system_id, label),
  UNIQUE (corpus_release_id, reference_system_id, reference_sort_key)
);

CREATE TABLE serving.corpus_text_segments (
  corpus_release_id uuid NOT NULL REFERENCES serving.research_objects(research_object_id),
  text_segment_id uuid NOT NULL,
  reference_span_id uuid NOT NULL REFERENCES serving.reference_spans(reference_span_id),
  segment_order integer NOT NULL,
  surface_original text NOT NULL,
  segment_kind text NOT NULL,
  content_hash text,
  PRIMARY KEY (corpus_release_id, text_segment_id),
  UNIQUE (corpus_release_id, segment_order)
);

CREATE TABLE serving.corpus_nodes (
  corpus_release_id uuid NOT NULL REFERENCES serving.research_objects(research_object_id),
  analysis_node_id uuid NOT NULL,
  annotation_layer_id uuid NOT NULL,
  node_type text NOT NULL,
  reference_span_id uuid NOT NULL REFERENCES serving.reference_spans(reference_span_id),
  PRIMARY KEY (corpus_release_id, analysis_node_id)
);

CREATE TABLE serving.corpus_node_segments (
  corpus_release_id uuid NOT NULL,
  analysis_node_id uuid NOT NULL,
  text_segment_id uuid NOT NULL,
  member_order integer NOT NULL CHECK (member_order >= 0),
  membership_role text NOT NULL,
  PRIMARY KEY (corpus_release_id, analysis_node_id, text_segment_id, membership_role),
  FOREIGN KEY (corpus_release_id, analysis_node_id)
    REFERENCES serving.corpus_nodes(corpus_release_id, analysis_node_id) ON DELETE CASCADE,
  FOREIGN KEY (corpus_release_id, text_segment_id)
    REFERENCES serving.corpus_text_segments(corpus_release_id, text_segment_id) ON DELETE CASCADE
);

CREATE TABLE serving.corpus_node_features (
  corpus_release_id uuid NOT NULL,
  analysis_node_id uuid NOT NULL,
  feature_key text NOT NULL,
  feature_value text NOT NULL,
  PRIMARY KEY (corpus_release_id, analysis_node_id, feature_key, feature_value),
  FOREIGN KEY (corpus_release_id, analysis_node_id)
    REFERENCES serving.corpus_nodes(corpus_release_id, analysis_node_id) ON DELETE CASCADE
);

CREATE TABLE serving.corpus_edges (
  corpus_release_id uuid NOT NULL,
  from_node_id uuid NOT NULL,
  to_node_id uuid NOT NULL,
  relation_type text NOT NULL,
  PRIMARY KEY (corpus_release_id, from_node_id, to_node_id, relation_type),
  FOREIGN KEY (corpus_release_id, from_node_id)
    REFERENCES serving.corpus_nodes(corpus_release_id, analysis_node_id),
  FOREIGN KEY (corpus_release_id, to_node_id)
    REFERENCES serving.corpus_nodes(corpus_release_id, analysis_node_id)
);

CREATE TABLE serving.corpus_node_mappings (
  corpus_release_id uuid NOT NULL,
  source_node_id uuid NOT NULL,
  target_node_id uuid NOT NULL,
  mapping_type text NOT NULL,
  PRIMARY KEY (corpus_release_id, source_node_id, target_node_id, mapping_type),
  FOREIGN KEY (corpus_release_id, source_node_id)
    REFERENCES serving.corpus_nodes(corpus_release_id, analysis_node_id),
  FOREIGN KEY (corpus_release_id, target_node_id)
    REFERENCES serving.corpus_nodes(corpus_release_id, analysis_node_id)
);

CREATE TABLE serving.semantic_set_members (
  semantic_set_version_id uuid NOT NULL REFERENCES serving.research_objects(research_object_id),
  member_key text NOT NULL,
  inclusion_type text NOT NULL,
  PRIMARY KEY (semantic_set_version_id, member_key)
);

CREATE INDEX serving_corpus_nodes_release_span_idx
  ON serving.corpus_nodes(corpus_release_id, reference_span_id);
CREATE INDEX serving_corpus_features_lookup_idx
  ON serving.corpus_node_features(feature_key, feature_value, corpus_release_id, analysis_node_id);
CREATE INDEX serving_corpus_edges_lookup_idx
  ON serving.corpus_edges(relation_type, corpus_release_id, to_node_id, from_node_id);
CREATE INDEX serving_corpus_mappings_source_idx
  ON serving.corpus_node_mappings(corpus_release_id, source_node_id, target_node_id);
CREATE INDEX serving_semantic_members_lookup_idx
  ON serving.semantic_set_members(semantic_set_version_id, member_key);

CREATE TABLE serving.rights_decision_snapshots (
  rights_decision_snapshot_id uuid PRIMARY KEY,
  subject_type text NOT NULL,
  subject_identifier uuid NOT NULL,
  operation text NOT NULL,
  purpose_scope text NOT NULL,
  audience_scope text NOT NULL,
  commercial_context text NOT NULL,
  applicable_rule_ids uuid[] NOT NULL DEFAULT '{}',
  winning_rule_ids uuid[] NOT NULL DEFAULT '{}',
  decision text NOT NULL CHECK (decision IN ('ALLOW','DENY','CONDITIONAL')),
  decision_basis text NOT NULL CHECK (decision_basis IN ('RULE','DEFAULT_DENY','UNKNOWN_RESTRICTIVE')),
  conditions_json jsonb,
  obligations_json jsonb NOT NULL DEFAULT '[]'::jsonb,
  resolver_version text NOT NULL,
  evaluated_at timestamptz NOT NULL,
  decision_hash text NOT NULL,
  CHECK (winning_rule_ids <@ applicable_rule_ids),
  CHECK (serving.valid_rights_conditions(conditions_json)),
  CHECK (serving.valid_rights_obligations(obligations_json)),
  CHECK (
    (decision_basis = 'RULE' AND cardinality(winning_rule_ids) > 0)
    OR
    (decision_basis IN ('DEFAULT_DENY','UNKNOWN_RESTRICTIVE') AND decision = 'DENY' AND cardinality(winning_rule_ids) = 0)
  ),
  CHECK (
    decision <> 'CONDITIONAL'
    OR COALESCE(jsonb_array_length(conditions_json),0) > 0
    OR COALESCE(jsonb_array_length(obligations_json),0) > 0
  ),
  CHECK (
    decision <> 'ALLOW'
    OR (COALESCE(jsonb_array_length(conditions_json),0) = 0 AND COALESCE(jsonb_array_length(obligations_json),0) = 0)
  )
);

CREATE TABLE authoring.research_builds (
  research_build_id uuid PRIMARY KEY,
  build_version text NOT NULL,
  status text NOT NULL CHECK (status IN ('QUEUED','RUNNING','FAILED','READY_FOR_REVIEW','APPROVED','REJECTED','COMPLETED')),
  started_at timestamptz NOT NULL,
  completed_at timestamptz,
  compiler_version text NOT NULL,
  git_commit_sha text NOT NULL
);

CREATE TABLE serving.research_releases (
  research_release_id uuid PRIMARY KEY,
  release_label text NOT NULL UNIQUE,
  source_build_id uuid NOT NULL,
  published_at timestamptz NOT NULL,
  manifest_schema_version text NOT NULL,
  manifest_hash text NOT NULL,
  manifest_hash_algorithm text NOT NULL CHECK (manifest_hash_algorithm = 'SHA256'),
  manifest_canonical_serialization text NOT NULL CHECK (manifest_canonical_serialization = 'RFC8785_JSON_CANONICALIZATION_SCHEME'),
  git_commit_sha text NOT NULL,
  compiler_version text NOT NULL
);

CREATE TABLE serving.research_release_components (
  research_release_id uuid NOT NULL REFERENCES serving.research_releases(research_release_id),
  component_kind text NOT NULL,
  component_research_object_id uuid NOT NULL REFERENCES serving.research_objects(research_object_id),
  component_version text NOT NULL,
  content_hash text NOT NULL,
  component_order integer NOT NULL,
  PRIMARY KEY (research_release_id, component_order),
  UNIQUE (research_release_id, component_kind, component_research_object_id, component_version),
  UNIQUE (research_release_id, component_research_object_id)
);

CREATE TABLE serving.research_release_events (
  research_release_event_id uuid PRIMARY KEY,
  research_release_id uuid NOT NULL REFERENCES serving.research_releases(research_release_id),
  event_type text NOT NULL CHECK (event_type IN ('PUBLISHED','SUPERSEDED','REVOKED','REACTIVATED')),
  effective_at timestamptz NOT NULL,
  reason text
);

CREATE TABLE serving.release_channels (
  release_channel_id uuid PRIMARY KEY,
  channel_key text NOT NULL UNIQUE CHECK (channel_key IN ('PREVIEW','STAGING','PRODUCTION')),
  description text
);

CREATE TABLE serving.release_channel_pointers (
  release_channel_id uuid PRIMARY KEY REFERENCES serving.release_channels(release_channel_id),
  research_release_id uuid NOT NULL REFERENCES serving.research_releases(research_release_id),
  updated_at timestamptz NOT NULL,
  updated_by uuid,
  row_version integer NOT NULL DEFAULT 1 CHECK (row_version > 0)
);

CREATE OR REPLACE FUNCTION serving.reject_immutable_update()
RETURNS trigger
LANGUAGE plpgsql
AS $$
BEGIN
  RAISE EXCEPTION '% is immutable after materialization', TG_TABLE_NAME;
END
$$;

CREATE TRIGGER research_release_immutable
BEFORE UPDATE OR DELETE ON serving.research_releases
FOR EACH ROW EXECUTE FUNCTION serving.reject_immutable_update();

CREATE TRIGGER research_release_component_immutable
BEFORE UPDATE OR DELETE ON serving.research_release_components
FOR EACH ROW EXECUTE FUNCTION serving.reject_immutable_update();

CREATE TRIGGER research_release_event_append_only
BEFORE UPDATE OR DELETE ON serving.research_release_events
FOR EACH ROW EXECUTE FUNCTION serving.reject_immutable_update();

CREATE TABLE serving.published_passage_analyses (
  published_analysis_id uuid PRIMARY KEY,
  research_release_id uuid NOT NULL REFERENCES serving.research_releases(research_release_id),
  reference_span_id uuid NOT NULL REFERENCES serving.reference_spans(reference_span_id),
  analysis_type text NOT NULL,
  analysis_schema_version text NOT NULL,
  rendered_payload jsonb,
  analysis_hash text NOT NULL,
  review_status text NOT NULL
);

CREATE TABLE serving.published_evidence_packets (
  published_evidence_packet_id uuid PRIMARY KEY,
  research_release_id uuid NOT NULL REFERENCES serving.research_releases(research_release_id),
  packet_type text NOT NULL
);

CREATE TABLE serving.published_evidence_items (
  published_evidence_item_id uuid PRIMARY KEY,
  published_evidence_packet_id uuid NOT NULL REFERENCES serving.published_evidence_packets(published_evidence_packet_id),
  research_object_id uuid NOT NULL REFERENCES serving.research_objects(research_object_id),
  research_object_version text,
  evidence_content_hash text,
  evidence_class text NOT NULL,
  citation_locator jsonb,
  permitted_excerpt text,
  rights_decision_snapshot_id uuid REFERENCES serving.rights_decision_snapshots(rights_decision_snapshot_id),
  evidence_stability_class text NOT NULL CHECK (evidence_stability_class IN ('IMMUTABLE_SNAPSHOT','LIVE_EXTERNAL_OBSERVATION','METADATA_ONLY')),
  sort_order integer NOT NULL,
  CHECK (evidence_stability_class <> 'IMMUTABLE_SNAPSHOT' OR evidence_content_hash IS NOT NULL),
  CHECK (permitted_excerpt IS NULL OR citation_locator IS NOT NULL),
  CHECK (serving.valid_citation_locator(citation_locator))
);

CREATE OR REPLACE FUNCTION serving.validate_published_evidence_rights()
RETURNS trigger
LANGUAGE plpgsql
AS $$
DECLARE
  snap serving.rights_decision_snapshots%ROWTYPE;
BEGIN
  IF NEW.permitted_excerpt IS NULL THEN
    RETURN NEW;
  END IF;

  IF NEW.rights_decision_snapshot_id IS NULL THEN
    RAISE EXCEPTION 'published excerpt requires rights decision snapshot';
  END IF;

  SELECT * INTO snap
  FROM serving.rights_decision_snapshots
  WHERE rights_decision_snapshot_id = NEW.rights_decision_snapshot_id;

  IF snap.rights_decision_snapshot_id IS NULL
     OR snap.subject_type <> 'RESEARCH_OBJECT'
     OR snap.subject_identifier <> NEW.research_object_id
     OR snap.decision NOT IN ('ALLOW','CONDITIONAL')
     OR snap.operation NOT IN ('DISPLAY_EXCERPT','QUOTE')
     OR snap.purpose_scope NOT IN ('PUBLICATION','PUBLIC_DISPLAY')
     OR snap.audience_scope <> 'PUBLIC' THEN
    RAISE EXCEPTION 'rights snapshot is incompatible with public excerpt';
  END IF;
  RETURN NEW;
END
$$;

CREATE TRIGGER published_evidence_rights
BEFORE INSERT OR UPDATE ON serving.published_evidence_items
FOR EACH ROW EXECUTE FUNCTION serving.validate_published_evidence_rights();

CREATE TABLE serving.published_assertions (
  published_assertion_id uuid PRIMARY KEY,
  research_release_id uuid NOT NULL REFERENCES serving.research_releases(research_release_id),
  assertion_text text NOT NULL,
  assertion_type text NOT NULL,
  confidence_class text,
  assertion_hash text NOT NULL
);

CREATE TABLE serving.published_assertion_evidence (
  published_assertion_id uuid NOT NULL REFERENCES serving.published_assertions(published_assertion_id) ON DELETE CASCADE,
  published_evidence_item_id uuid NOT NULL REFERENCES serving.published_evidence_items(published_evidence_item_id),
  stance text NOT NULL,
  entailment_review_status text NOT NULL,
  weight_metadata jsonb,
  PRIMARY KEY (published_assertion_id, published_evidence_item_id)
);

CREATE UNIQUE INDEX research_release_single_published_event
  ON serving.research_release_events(research_release_id)
  WHERE event_type = 'PUBLISHED';

CREATE OR REPLACE FUNCTION serving.release_is_published(p_release_id uuid)
RETURNS boolean
LANGUAGE sql
STABLE
SECURITY DEFINER
SET search_path = pg_catalog, serving
AS $release_is_published$
  SELECT EXISTS (
    SELECT 1
    FROM serving.research_release_events
    WHERE research_release_id = p_release_id
      AND event_type = 'PUBLISHED'
  )
$release_is_published$;

CREATE OR REPLACE FUNCTION serving.component_is_published(p_research_object_id uuid)
RETURNS boolean
LANGUAGE sql
STABLE
SECURITY DEFINER
SET search_path = pg_catalog, serving
AS $component_is_published$
  SELECT EXISTS (
    SELECT 1
    FROM serving.research_release_components c
    JOIN serving.research_release_events e
      ON e.research_release_id = c.research_release_id
     AND e.event_type = 'PUBLISHED'
    WHERE c.component_research_object_id = p_research_object_id
  )
$component_is_published$;

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

  IF serving.release_is_published(release_id) THEN
    RAISE EXCEPTION 'release % payload is immutable after PUBLISHED', release_id;
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

  IF serving.release_is_published(release_id) THEN
    RAISE EXCEPTION 'release % evidence payload is immutable after PUBLISHED', release_id;
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

  IF serving.release_is_published(assertion_release) THEN
    RAISE EXCEPTION 'release % assertion/evidence links are immutable after PUBLISHED', assertion_release;
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

  IF serving.component_is_published(object_id) THEN
    RAISE EXCEPTION 'published component % projection is immutable', object_id;
  END IF;

  RETURN CASE WHEN TG_OP='DELETE' THEN OLD ELSE NEW END;
END
$guard_component_projection$;

CREATE TRIGGER release_component_insert_lock
BEFORE INSERT ON serving.research_release_components
FOR EACH ROW EXECUTE FUNCTION serving.guard_direct_release_payload();

CREATE TRIGGER passage_analysis_release_lock
BEFORE INSERT OR UPDATE OR DELETE ON serving.published_passage_analyses
FOR EACH ROW EXECUTE FUNCTION serving.guard_direct_release_payload();

CREATE TRIGGER evidence_packet_release_lock
BEFORE INSERT OR UPDATE OR DELETE ON serving.published_evidence_packets
FOR EACH ROW EXECUTE FUNCTION serving.guard_direct_release_payload();

CREATE TRIGGER assertion_release_lock
BEFORE INSERT OR UPDATE OR DELETE ON serving.published_assertions
FOR EACH ROW EXECUTE FUNCTION serving.guard_direct_release_payload();

CREATE TRIGGER evidence_item_release_lock
BEFORE INSERT OR UPDATE OR DELETE ON serving.published_evidence_items
FOR EACH ROW EXECUTE FUNCTION serving.guard_evidence_item_payload();

CREATE TRIGGER assertion_evidence_release_lock
BEFORE INSERT OR UPDATE OR DELETE ON serving.published_assertion_evidence
FOR EACH ROW EXECUTE FUNCTION serving.guard_assertion_evidence_payload();

CREATE TRIGGER corpus_nodes_component_lock
BEFORE INSERT OR UPDATE OR DELETE ON serving.corpus_nodes
FOR EACH ROW EXECUTE FUNCTION serving.guard_component_projection('corpus_release_id');

CREATE TRIGGER corpus_features_component_lock
BEFORE INSERT OR UPDATE OR DELETE ON serving.corpus_node_features
FOR EACH ROW EXECUTE FUNCTION serving.guard_component_projection('corpus_release_id');

CREATE TRIGGER corpus_edges_component_lock
BEFORE INSERT OR UPDATE OR DELETE ON serving.corpus_edges
FOR EACH ROW EXECUTE FUNCTION serving.guard_component_projection('corpus_release_id');

CREATE TRIGGER corpus_mappings_component_lock
BEFORE INSERT OR UPDATE OR DELETE ON serving.corpus_node_mappings
FOR EACH ROW EXECUTE FUNCTION serving.guard_component_projection('corpus_release_id');

CREATE TRIGGER semantic_members_component_lock
BEFORE INSERT OR UPDATE OR DELETE ON serving.semantic_set_members
FOR EACH ROW EXECUTE FUNCTION serving.guard_component_projection('semantic_set_version_id');

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
AS $$
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

  IF NOT serving.release_is_published(p_release_id) THEN
    INSERT INTO serving.research_release_events(
      research_release_event_id,research_release_id,event_type,effective_at,reason
    ) VALUES (
      pg_catalog.gen_random_uuid(),p_release_id,'PUBLISHED',now(),'publication_control.publish_release_to_channel'
    );
  END IF;

  IF p_inject_failure THEN
    RAISE EXCEPTION 'SPIKE_INJECTED_FAILURE_BEFORE_POINTER_MOVE';
  END IF;

  INSERT INTO serving.release_channel_pointers(
    release_channel_id, research_release_id, updated_at, updated_by, row_version
  )
  VALUES (channel_id, p_release_id, now(), p_updated_by, 1)
  ON CONFLICT (release_channel_id) DO UPDATE
  SET research_release_id = EXCLUDED.research_release_id,
      updated_at = EXCLUDED.updated_at,
      updated_by = EXCLUDED.updated_by,
      row_version = serving.release_channel_pointers.row_version + 1;
END
$$;

REVOKE ALL ON FUNCTION publication_control.publish_release_to_channel(text,uuid,uuid,boolean)
  FROM PUBLIC, anon, authenticated;
GRANT EXECUTE ON FUNCTION publication_control.publish_release_to_channel(text,uuid,uuid,boolean)
  TO publication_worker;

CREATE VIEW serving.current_release
WITH (security_invoker = true)
AS
SELECT c.channel_key, p.research_release_id, r.release_label, r.published_at
FROM serving.release_channels c
JOIN serving.release_channel_pointers p USING (release_channel_id)
JOIN serving.research_releases r USING (research_release_id);

CREATE OR REPLACE FUNCTION serving.read_passage_core(
  p_release_id uuid,
  p_reference_system_code text,
  p_reference_label text
)
RETURNS jsonb
LANGUAGE sql
STABLE
SECURITY INVOKER
AS $passage_core$
  WITH pinned_corpus AS (
    SELECT component_research_object_id AS corpus_release_id
    FROM serving.research_release_components
    WHERE research_release_id = p_release_id
      AND component_kind = 'CORPUS'
      AND serving.release_is_published(p_release_id)
    ORDER BY component_order
    LIMIT 1
  ),
  resolved AS (
    SELECT
      rl.corpus_release_id,
      rl.reference_label_id,
      rl.reference_system_id,
      rsys.code AS reference_system_code,
      rl.reference_span_id,
      rl.book_code,
      rl.chapter_number,
      rl.label,
      rl.reference_sort_key
    FROM pinned_corpus pc
    JOIN serving.reference_labels rl ON rl.corpus_release_id = pc.corpus_release_id
    JOIN serving.reference_systems rsys ON rsys.reference_system_id = rl.reference_system_id
    WHERE rsys.code = p_reference_system_code
      AND rl.label = p_reference_label
  ),
  token_features AS (
    SELECT
      n.corpus_release_id,
      n.analysis_node_id,
      ns.text_segment_id,
      ts.segment_order,
      ts.surface_original,
      COALESCE(jsonb_object_agg(f.feature_key, f.feature_value)
        FILTER (WHERE f.feature_key IS NOT NULL), '{}'::jsonb) AS features
    FROM resolved r
    JOIN serving.corpus_nodes n
      ON n.corpus_release_id = r.corpus_release_id
     AND n.reference_span_id = r.reference_span_id
     AND n.node_type = 'WORD'
    JOIN serving.corpus_node_segments ns
      ON ns.corpus_release_id = n.corpus_release_id
     AND ns.analysis_node_id = n.analysis_node_id
    JOIN serving.corpus_text_segments ts
      ON ts.corpus_release_id = ns.corpus_release_id
     AND ts.text_segment_id = ns.text_segment_id
    LEFT JOIN serving.corpus_node_features f
      ON f.corpus_release_id = n.corpus_release_id
     AND f.analysis_node_id = n.analysis_node_id
    GROUP BY n.corpus_release_id,n.analysis_node_id,ns.text_segment_id,ts.segment_order,ts.surface_original
  )
  SELECT jsonb_build_object(
    'dataSource', 'SERVING',
    'researchReleaseId', p_release_id::text,
    'referenceSpanId', r.reference_span_id::text,
    'resolvedReference', jsonb_build_object(
      'referenceSystemId', r.reference_system_id::text,
      'referenceSystemCode', r.reference_system_code,
      'referenceLabel', r.label
    ),
    'textReconstructionStatus', 'OSHB_WORD_TOKENS_ONLY',
    'hebrewText', COALESCE((
      SELECT string_agg(tf.surface_original, ' ' ORDER BY tf.segment_order)
      FROM token_features tf
    ), ''),
    'tokens', COALESCE((
      SELECT jsonb_agg(
        jsonb_build_object(
          'analysisNodeId', tf.analysis_node_id::text,
          'textSegmentId', tf.text_segment_id::text,
          'surface', tf.surface_original,
          'lemmaRaw', tf.features->>'LEMMA_RAW',
          'morphRaw', tf.features->>'MORPH_RAW'
        )
        ORDER BY tf.segment_order
      )
      FROM token_features tf
    ), '[]'::jsonb),
    'navigation', jsonb_build_object(
      'currentBookCode', r.book_code,
      'currentChapter', r.chapter_number,
      'previousReference', (
        SELECT p.label
        FROM serving.reference_labels p
        WHERE p.corpus_release_id = r.corpus_release_id
          AND p.reference_system_id = r.reference_system_id
          AND p.reference_sort_key < r.reference_sort_key
        ORDER BY p.reference_sort_key DESC
        LIMIT 1
      ),
      'nextReference', (
        SELECT n.label
        FROM serving.reference_labels n
        WHERE n.corpus_release_id = r.corpus_release_id
          AND n.reference_system_id = r.reference_system_id
          AND n.reference_sort_key > r.reference_sort_key
        ORDER BY n.reference_sort_key
        LIMIT 1
      ),
      'books', COALESCE((
        SELECT jsonb_agg(
          jsonb_build_object(
            'bookCode', b.book_code,
            'firstReference', b.first_reference
          )
          ORDER BY b.first_sort
        )
        FROM (
          SELECT
            x.book_code,
            min(x.reference_sort_key) AS first_sort,
            (array_agg(x.label ORDER BY x.reference_sort_key))[1] AS first_reference
          FROM serving.reference_labels x
          WHERE x.corpus_release_id = r.corpus_release_id
            AND x.reference_system_id = r.reference_system_id
          GROUP BY x.book_code
        ) b
      ), '[]'::jsonb),
      'chapters', COALESCE((
        SELECT jsonb_agg(
          jsonb_build_object(
            'chapterNumber', c.chapter_number,
            'firstReference', c.first_reference
          )
          ORDER BY c.chapter_number
        )
        FROM (
          SELECT
            x.chapter_number,
            (array_agg(x.label ORDER BY x.reference_sort_key))[1] AS first_reference
          FROM serving.reference_labels x
          WHERE x.corpus_release_id = r.corpus_release_id
            AND x.reference_system_id = r.reference_system_id
            AND x.book_code = r.book_code
            AND x.chapter_number IS NOT NULL
          GROUP BY x.chapter_number
        ) c
      ), '[]'::jsonb),
      'passages', COALESCE((
        SELECT jsonb_agg(
          jsonb_build_object(
            'referenceLabel', p.label,
            'verseLabel', p.verse_label
          )
          ORDER BY p.reference_sort_key
        )
        FROM serving.reference_labels p
        WHERE p.corpus_release_id = r.corpus_release_id
          AND p.reference_system_id = r.reference_system_id
          AND p.book_code = r.book_code
          AND p.chapter_number = r.chapter_number
      ), '[]'::jsonb)
    ),
    'attribution', 'Open Scriptures Hebrew Bible / Westminster Leningrad Codex; source and morphology attribution required.'
  )
  FROM resolved r
$passage_core$;

REVOKE ALL ON FUNCTION serving.read_passage_core(uuid,text,text) FROM PUBLIC;
GRANT EXECUTE ON FUNCTION serving.read_passage_core(uuid,text,text) TO anon, authenticated;

CREATE OR REPLACE FUNCTION serving.spike_corpus_query(
  p_release_id uuid,
  p_semantic_set_version_id uuid,
  p_after_reference_span_id uuid DEFAULT NULL,
  p_limit integer DEFAULT 50
)
RETURNS TABLE(reference_span_id uuid)
LANGUAGE sql
STABLE
SECURITY INVOKER
AS $corpus_query$
  WITH pinned_corpus AS (
    SELECT component_research_object_id AS corpus_release_id
    FROM serving.research_release_components
    WHERE research_release_id = p_release_id AND component_kind = 'CORPUS'
  ),
  pinned_semantic_set AS (
    SELECT 1 FROM serving.research_release_components
    WHERE research_release_id = p_release_id
      AND component_kind = 'SEMANTIC_SET'
      AND component_research_object_id = p_semantic_set_version_id
  ),
  cursor_key AS (
    SELECT reference_sort_key, reference_span_id
    FROM serving.reference_spans
    WHERE reference_span_id = p_after_reference_span_id
  ),
  verb_nodes AS (
    SELECT n.corpus_release_id, n.analysis_node_id, n.reference_span_id
    FROM serving.corpus_nodes n
    JOIN pinned_corpus pc ON pc.corpus_release_id = n.corpus_release_id
    JOIN serving.corpus_node_features f
      ON f.corpus_release_id=n.corpus_release_id AND f.analysis_node_id=n.analysis_node_id
     AND f.feature_key='LEMMA' AND f.feature_value='ראה'
  ),
  body_nodes AS (
    SELECT n.corpus_release_id, n.analysis_node_id, n.reference_span_id
    FROM serving.corpus_nodes n
    JOIN pinned_corpus pc ON pc.corpus_release_id = n.corpus_release_id
    JOIN serving.corpus_node_features f
      ON f.corpus_release_id=n.corpus_release_id AND f.analysis_node_id=n.analysis_node_id
     AND f.feature_key='LEMMA'
    JOIN serving.semantic_set_members sm
      ON sm.semantic_set_version_id=p_semantic_set_version_id AND sm.member_key=f.feature_value
    JOIN pinned_semantic_set ps ON true
  ),
  prefixed_body AS (
    SELECT mp.corpus_release_id, mp.source_node_id AS body_node_id
    FROM serving.corpus_node_mappings mp
    JOIN serving.corpus_edges e
      ON e.corpus_release_id=mp.corpus_release_id AND e.to_node_id=mp.target_node_id
    JOIN serving.corpus_node_features pf
      ON pf.corpus_release_id=e.corpus_release_id AND pf.analysis_node_id=e.from_node_id
     AND pf.feature_key='SURFACE' AND pf.feature_value='ל'
    WHERE e.relation_type='PREFIX_MORPHEME_OF'
  ),
  matches AS (
    SELECT DISTINCT v.reference_span_id
    FROM verb_nodes v
    JOIN body_nodes b
      ON b.corpus_release_id=v.corpus_release_id AND b.reference_span_id=v.reference_span_id
    JOIN prefixed_body pb
      ON pb.corpus_release_id=b.corpus_release_id AND pb.body_node_id=b.analysis_node_id
  )
  SELECT m.reference_span_id
  FROM matches m
  JOIN serving.reference_spans rs USING (reference_span_id)
  WHERE p_after_reference_span_id IS NULL
     OR EXISTS (
       SELECT 1
       FROM cursor_key ck
       WHERE (rs.reference_sort_key,rs.reference_span_id) >
             (ck.reference_sort_key,ck.reference_span_id)
     )
  ORDER BY rs.reference_sort_key,rs.reference_span_id
  LIMIT LEAST(GREATEST(p_limit,1),200)
$corpus_query$;

CREATE OR REPLACE FUNCTION publication_control.translation_aggregate_hash(p_translation_decision_id uuid)
RETURNS text
LANGUAGE sql
STABLE
SECURITY DEFINER
SET search_path = pg_catalog, authoring
AS $$
  SELECT encode(sha256(convert_to(concat_ws('|',
    td.translation_decision_id::text,
    td.translation_source_basis_id::text,
    td.translation_policy_version_id::text,
    td.target_language_tag,
    COALESCE(td.selected_rendering,''),
    tsb.content_hash,
    tpv.content_hash
  ),'UTF8')),'hex')
  FROM authoring.translation_decisions td
  JOIN authoring.translation_source_bases tsb
    ON tsb.translation_source_basis_id=td.translation_source_basis_id
  JOIN authoring.translation_policy_versions tpv
    ON tpv.translation_policy_version_id=td.translation_policy_version_id
  WHERE td.translation_decision_id=p_translation_decision_id
$$;

REVOKE ALL ON FUNCTION publication_control.translation_aggregate_hash(uuid)
  FROM PUBLIC, anon, authenticated;
GRANT EXECUTE ON FUNCTION publication_control.translation_aggregate_hash(uuid)
  TO publication_worker;

CREATE TABLE workspace.research_projects (
  project_id uuid PRIMARY KEY,
  owner_user_id uuid NOT NULL,
  title text NOT NULL,
  description text,
  visibility text NOT NULL,
  status text NOT NULL,
  created_at timestamptz NOT NULL DEFAULT now(),
  updated_at timestamptz NOT NULL DEFAULT now(),
  UNIQUE (project_id, owner_user_id)
);

CREATE TABLE workspace.saved_queries (
  saved_query_id uuid PRIMARY KEY,
  owner_user_id uuid NOT NULL,
  project_id uuid NOT NULL,
  query_json jsonb NOT NULL,
  created_at timestamptz NOT NULL DEFAULT now(),
  FOREIGN KEY (project_id, owner_user_id)
    REFERENCES workspace.research_projects(project_id, owner_user_id) ON DELETE CASCADE
);

CREATE TABLE workspace.user_translation_drafts (
  draft_id uuid PRIMARY KEY,
  owner_user_id uuid NOT NULL,
  project_id uuid NOT NULL,
  reference_span_id uuid NOT NULL REFERENCES serving.reference_spans(reference_span_id),
  rendering text NOT NULL,
  updated_at timestamptz NOT NULL DEFAULT now(),
  FOREIGN KEY (project_id, owner_user_id)
    REFERENCES workspace.research_projects(project_id, owner_user_id) ON DELETE CASCADE
);

ALTER TABLE workspace.research_projects ENABLE ROW LEVEL SECURITY;
ALTER TABLE workspace.saved_queries ENABLE ROW LEVEL SECURITY;
ALTER TABLE workspace.user_translation_drafts ENABLE ROW LEVEL SECURITY;

CREATE POLICY workspace_projects_owner_select
ON workspace.research_projects FOR SELECT TO authenticated
USING ((SELECT auth.uid()) = owner_user_id);

CREATE POLICY workspace_projects_owner_insert
ON workspace.research_projects FOR INSERT TO authenticated
WITH CHECK ((SELECT auth.uid()) = owner_user_id);

CREATE POLICY workspace_projects_owner_update
ON workspace.research_projects FOR UPDATE TO authenticated
USING ((SELECT auth.uid()) = owner_user_id)
WITH CHECK ((SELECT auth.uid()) = owner_user_id);

CREATE POLICY workspace_projects_owner_delete
ON workspace.research_projects FOR DELETE TO authenticated
USING ((SELECT auth.uid()) = owner_user_id);

CREATE POLICY workspace_saved_queries_owner_all
ON workspace.saved_queries FOR ALL TO authenticated
USING ((SELECT auth.uid()) = owner_user_id)
WITH CHECK ((SELECT auth.uid()) = owner_user_id);

CREATE POLICY workspace_translation_drafts_owner_all
ON workspace.user_translation_drafts FOR ALL TO authenticated
USING ((SELECT auth.uid()) = owner_user_id)
WITH CHECK ((SELECT auth.uid()) = owner_user_id);

GRANT SELECT, INSERT, UPDATE, DELETE ON workspace.research_projects TO authenticated;
GRANT SELECT, INSERT, UPDATE, DELETE ON workspace.saved_queries TO authenticated;
GRANT SELECT, INSERT, UPDATE, DELETE ON workspace.user_translation_drafts TO authenticated;

ALTER TABLE serving.research_objects ENABLE ROW LEVEL SECURITY;
ALTER TABLE serving.reference_spans ENABLE ROW LEVEL SECURITY;
ALTER TABLE serving.reference_systems ENABLE ROW LEVEL SECURITY;
ALTER TABLE serving.reference_labels ENABLE ROW LEVEL SECURITY;
ALTER TABLE serving.corpus_text_segments ENABLE ROW LEVEL SECURITY;
ALTER TABLE serving.corpus_nodes ENABLE ROW LEVEL SECURITY;
ALTER TABLE serving.corpus_node_segments ENABLE ROW LEVEL SECURITY;
ALTER TABLE serving.corpus_node_features ENABLE ROW LEVEL SECURITY;
ALTER TABLE serving.corpus_edges ENABLE ROW LEVEL SECURITY;
ALTER TABLE serving.corpus_node_mappings ENABLE ROW LEVEL SECURITY;
ALTER TABLE serving.semantic_set_members ENABLE ROW LEVEL SECURITY;
ALTER TABLE serving.rights_decision_snapshots ENABLE ROW LEVEL SECURITY;
ALTER TABLE serving.research_releases ENABLE ROW LEVEL SECURITY;
ALTER TABLE serving.research_release_components ENABLE ROW LEVEL SECURITY;
ALTER TABLE serving.release_channels ENABLE ROW LEVEL SECURITY;
ALTER TABLE serving.release_channel_pointers ENABLE ROW LEVEL SECURITY;
ALTER TABLE serving.published_passage_analyses ENABLE ROW LEVEL SECURITY;
ALTER TABLE serving.published_evidence_packets ENABLE ROW LEVEL SECURITY;
ALTER TABLE serving.published_evidence_items ENABLE ROW LEVEL SECURITY;
ALTER TABLE serving.published_assertions ENABLE ROW LEVEL SECURITY;
ALTER TABLE serving.published_assertion_evidence ENABLE ROW LEVEL SECURITY;

CREATE POLICY public_read_reference_spans ON serving.reference_spans
FOR SELECT TO anon, authenticated USING (true);
CREATE POLICY public_read_reference_systems ON serving.reference_systems
FOR SELECT TO anon, authenticated USING (true);
CREATE POLICY public_read_reference_labels ON serving.reference_labels
FOR SELECT TO anon, authenticated
USING (serving.component_is_published(corpus_release_id));
CREATE POLICY public_read_corpus_text_segments ON serving.corpus_text_segments
FOR SELECT TO anon, authenticated
USING (serving.component_is_published(corpus_release_id));
CREATE POLICY public_read_corpus_node_segments ON serving.corpus_node_segments
FOR SELECT TO anon, authenticated
USING (serving.component_is_published(corpus_release_id));

-- Release-scoped Serving rows remain physically materialized before publication,
-- but public roles must not observe them until the release has a committed
-- PUBLISHED event. The publication function creates that event and moves the
-- channel pointer in one transaction, so visibility changes atomically.
CREATE POLICY public_read_corpus_nodes ON serving.corpus_nodes
FOR SELECT TO anon, authenticated
USING (serving.component_is_published(corpus_release_id));
CREATE POLICY public_read_corpus_node_features ON serving.corpus_node_features
FOR SELECT TO anon, authenticated
USING (serving.component_is_published(corpus_release_id));
CREATE POLICY public_read_corpus_edges ON serving.corpus_edges
FOR SELECT TO anon, authenticated
USING (serving.component_is_published(corpus_release_id));
CREATE POLICY public_read_corpus_node_mappings ON serving.corpus_node_mappings
FOR SELECT TO anon, authenticated
USING (serving.component_is_published(corpus_release_id));
CREATE POLICY public_read_semantic_set_members ON serving.semantic_set_members
FOR SELECT TO anon, authenticated
USING (serving.component_is_published(semantic_set_version_id));

CREATE POLICY public_read_releases ON serving.research_releases
FOR SELECT TO anon, authenticated
USING (serving.release_is_published(research_release_id));
CREATE POLICY public_read_release_components ON serving.research_release_components
FOR SELECT TO anon, authenticated
USING (serving.release_is_published(research_release_id));
CREATE POLICY public_read_release_channels ON serving.release_channels
FOR SELECT TO anon, authenticated USING (true);
CREATE POLICY public_read_release_channel_pointers ON serving.release_channel_pointers
FOR SELECT TO anon, authenticated
USING (serving.release_is_published(research_release_id));
CREATE POLICY public_read_passage_analyses ON serving.published_passage_analyses
FOR SELECT TO anon, authenticated
USING (serving.release_is_published(research_release_id));
CREATE POLICY public_read_evidence_packets ON serving.published_evidence_packets
FOR SELECT TO anon, authenticated
USING (serving.release_is_published(research_release_id));
CREATE POLICY public_read_evidence_items ON serving.published_evidence_items
FOR SELECT TO anon, authenticated
USING (
  EXISTS (
    SELECT 1
    FROM serving.published_evidence_packets p
    WHERE p.published_evidence_packet_id = published_evidence_items.published_evidence_packet_id
      AND serving.release_is_published(p.research_release_id)
  )
);
CREATE POLICY public_read_assertions ON serving.published_assertions
FOR SELECT TO anon, authenticated
USING (serving.release_is_published(research_release_id));
CREATE POLICY public_read_assertion_evidence ON serving.published_assertion_evidence
FOR SELECT TO anon, authenticated
USING (
  EXISTS (
    SELECT 1
    FROM serving.published_assertions a
    WHERE a.published_assertion_id = published_assertion_evidence.published_assertion_id
      AND serving.release_is_published(a.research_release_id)
  )
);

GRANT SELECT ON serving.reference_spans, serving.reference_systems,
  serving.reference_labels, serving.corpus_text_segments, serving.corpus_node_segments,
  serving.corpus_nodes, serving.corpus_node_features, serving.corpus_edges,
  serving.corpus_node_mappings, serving.semantic_set_members,
  serving.research_releases, serving.research_release_components,
  serving.release_channels, serving.release_channel_pointers,
  serving.published_passage_analyses, serving.published_evidence_packets,
  serving.published_evidence_items, serving.published_assertions,
  serving.published_assertion_evidence, serving.current_release
TO anon, authenticated;

GRANT EXECUTE ON FUNCTION serving.spike_corpus_query(uuid,uuid,uuid,integer)
TO anon, authenticated;
REVOKE ALL ON FUNCTION serving.valid_rights_conditions(jsonb) FROM PUBLIC, anon, authenticated;
REVOKE ALL ON FUNCTION serving.valid_rights_obligations(jsonb) FROM PUBLIC, anon, authenticated;
REVOKE ALL ON FUNCTION serving.valid_citation_locator(jsonb) FROM PUBLIC, anon, authenticated;
REVOKE ALL ON FUNCTION serving.release_is_published(uuid) FROM PUBLIC, anon, authenticated;
REVOKE ALL ON FUNCTION serving.component_is_published(uuid) FROM PUBLIC, anon, authenticated;
GRANT EXECUTE ON FUNCTION serving.valid_rights_conditions(jsonb),
  serving.valid_rights_obligations(jsonb),
  serving.valid_citation_locator(jsonb),
  serving.release_is_published(uuid),
  serving.component_is_published(uuid)
TO publication_worker;

GRANT EXECUTE ON FUNCTION serving.release_is_published(uuid),
  serving.component_is_published(uuid)
TO anon, authenticated;

DO $authoring_rls$
DECLARE
  r record;
BEGIN
  FOR r IN SELECT schemaname, tablename
           FROM pg_tables
           WHERE schemaname = 'authoring'
  LOOP
    EXECUTE format('ALTER TABLE %I.%I ENABLE ROW LEVEL SECURITY', r.schemaname, r.tablename);
  END LOOP;
END
$authoring_rls$;

REVOKE ALL ON ALL TABLES IN SCHEMA authoring FROM PUBLIC, anon, authenticated;
REVOKE ALL ON ALL FUNCTIONS IN SCHEMA authoring FROM PUBLIC, anon, authenticated;

COMMIT;
