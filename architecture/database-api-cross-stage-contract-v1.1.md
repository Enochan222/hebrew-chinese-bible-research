# Database, API, and Cross-Stage Contract v1.1

Status: **ACTIVE SELF-CONTAINED CANDIDATE CONTRACT. NOT YET FROZEN FOR PRODUCTION IMPLEMENTATION.**

Amended 2026-10-03: the product is now explicitly modeled as a compiled scholarly data product with private authoring, publication control, deterministic public serving, and user workspace planes. See `architecture/product-platform-and-publication-model.md` and ADR-002.

This document supersedes both `database-api-cross-stage-contract-v1.md` and `database-api-cross-stage-contract-v1.1-candidate.md` for active implementation planning.

A developer must not need either superseded file in order to understand the active v1.1 contract.

Machine-readable companion contracts live under `contracts/v1.1/`.

The original v1 remains in the repository as design history. Do not implement its universal `canonical_tokens`, application-owned `phrases` / `clauses`, simplified translation identity, or simplified rights / apparatus models.

The v1.1 candidate preserves the project's strongest earlier decisions:

- deterministic corpus research is separate from academic RAG;
- translation witnesses do not prove translator intention;
- author-native scholarly terminology is preserved;
- Work -> Edition -> Asset identity is retained;
- evidence lanes remain separate;
- counterevidence is mandatory for disputed translation analysis;
- rights filtering occurs before restricted content reaches an AI model;
- important research inputs are version-pinned and auditable.

The load-bearing correction is:

> **Reference location may be application-canonical. Text expression must be edition-specific. Linguistic segmentation and structure must be framework-scoped. Translation witnesses must be expression-specific. Scholarly propositions must be agent-attributed.**

A second product-level rule now also applies:

> **Canonical public scholarship is compiled and published as a versioned ResearchRelease. Runtime AI/RAG is optional and non-authoritative; deterministic corpus search and published research data remain the core serving path.**

---

# 1. Architecture freeze policy

The canonical gate registry is:

- `contracts/v1.1/freeze-checklist.md`

Important distinction:

- passing `CORE_SPIKE_V1_1` permits Database Spike 001;
- it does **not** declare v1.1 FROZEN;
- Core v1.1 and Research Pro extension gates mature on separate engineering timelines but remain one product over one ResearchRelease;
- optional public AI has its own shipping gate and cannot block deterministic non-AI scholarship.

Only the canonical stable gate IDs in the checklist may be used by CI/fixtures.

---

# 2. System separation remains unchanged

The system still has four major evidence systems:

1. Biblical / versioned text and linguistic corpus system
2. Translation witness and alignment system
3. Academic literature and textual-criticism system
4. Research workspace, rules and analysis system

They share typed identifiers and provenance. They do not share one undifferentiated vector index and do not exchange unstructured AI prose as canonical data.

---

# 2A. Foundational registries, provenance, projects, and academic-source identity

The active v1.1 contract is self-contained. The entities in this section were previously defined mainly in superseded v1 or prose documents.

## 2A.1 `providers`

External or internal provider identity.

Fields:

- `provider_id uuid PK`
- `provider_key text unique`
- `name text`
- `provider_type text`
- `base_url text nullable`
- `active boolean`
- `metadata jsonb`

Provider identity is not textual-edition identity.

## 2A.2 `source_registry`

Global registry of datasets, providers, publications, libraries, and other evidence origins.

Fields:

- `source_registry_id uuid PK`
- `source_key text unique`
- `display_name text`
- `source_family text`
- `provider_id uuid nullable FK`
- `homepage_url text nullable`
- `default_evidence_class text nullable`
- `active boolean`
- `metadata jsonb`

This is a registry, not a substitute for Work, Edition, SourceAsset, DigitalExpression, or CorpusRelease.

## 2A.3 `provenance_records`

Reusable provenance locator.

Fields:

- `provenance_id uuid PK`
- `source_registry_id uuid nullable FK`
- `source_object_type text`
- `source_object_id text`
- `source_version text nullable`
- `retrieved_at timestamptz nullable`
- `content_hash text nullable`
- `derivation_method text nullable`
- `metadata jsonb`

A URL alone is not sufficient academic provenance.

## 2A.3A `provenance_agents`

Process provenance distinguishes who/what performed a derivation from the source locator itself.

Fields:

- `provenance_agent_id uuid PK`
- `agent_type text`
- `display_name text`
- `agent_version text nullable`
- `metadata jsonb nullable`

Agents may represent a human editor, deterministic software component, external provider, or AI model.

## 2A.3B `provenance_activities`

Fields:

- `provenance_activity_id uuid PK`
- `activity_type text`
- `activity_version text nullable`
- `started_at timestamptz nullable`
- `completed_at timestamptz nullable`
- `settings_hash text nullable`
- `metadata jsonb nullable`

Activity types come from canonical vocabulary and include ingestion, OCR, extraction, normalization, AI transformation, human review, mapping, query compilation, and publication.

## 2A.3C `provenance_activity_agents`

Fields:

- `provenance_activity_id uuid FK`
- `provenance_agent_id uuid FK`
- `agent_role text`

## 2A.3D `provenance_activity_inputs` / `provenance_activity_outputs`

Each links one provenance activity to a registered research object, source asset/span, or other explicitly typed input/output identity.

This process graph complements `provenance_records`; it does not replace source locators or evidence citations.


## 2A.4 `research_projects`

User workspace project container.

Fields:

- `project_id uuid PK`
- `owner_user_id uuid`
- `title text`
- `description text nullable`
- `visibility text`
- `status text`
- `created_at timestamptz`
- `updated_at timestamptz`

## 2A.5 `project_reference_spans`

Fields:

- `project_id uuid FK`
- `reference_span_id uuid FK`
- `position integer`
- `note text nullable`

## 2A.6 `works`

Bibliographic work identity.

Fields:

- `work_id uuid PK`
- `title text`
- `subtitle text nullable`
- `publication_type text`
- `language_code text nullable`
- `original_publication_year integer nullable`
- `doi text nullable`
- `isbn text nullable`
- `issn text nullable`
- `journal_title text nullable`
- `volume text nullable`
- `issue text nullable`
- `page_range text nullable`
- `publication_status text nullable`
- `metadata jsonb`

Publication form and scholarly role are separate axes.

## 2A.6A `work_source_roles`

A work may serve more than one scholarly role.

Fields:

- `work_id uuid FK`
- `source_role text`
- `is_primary boolean default false`

Unique:
`(work_id, source_role)`

`source_role` uses `contracts/v1.1/vocabulary.json -> sourceRole`.

## 2A.7 `authors` and `work_authors`

`authors`:

- `author_id uuid PK`
- `canonical_name text`
- `orcid text nullable`
- `metadata jsonb`

`work_authors`:

- `work_id uuid FK`
- `author_id uuid FK`
- `role text`
- `author_order integer`

## 2A.8 `editions`

Fields:

- `edition_id uuid PK`
- `work_id uuid FK`
- `edition_statement text nullable`
- `publication_year integer nullable`
- `publisher text nullable`
- `isbn text nullable`
- `language_code text nullable`
- `edition_status text`
- `newer_edition_known boolean`
- `bibliographic_notes text nullable`

## 2A.9 `source_assets`

Concrete file or remote source asset.

Fields:

- `source_asset_id uuid PK`
- `edition_id uuid nullable FK`
- `source_registry_id uuid FK`
- `external_locator_private text nullable`
- `mime_type text nullable`
- `byte_size bigint nullable`
- `sha256 text nullable`
- `content_hash text nullable`
- `extraction_status text`
- `extraction_quality text nullable`
- `rights_policy_id uuid nullable FK`
- `metadata jsonb`

Private Drive locators must never be exposed through public APIs.

## 2A.10 `ingestion_jobs`

Fields:

- `ingestion_job_id uuid PK`
- `source_asset_id uuid FK`
- `pipeline_type text`
- `pipeline_version text`
- `status text`
- `started_at timestamptz nullable`
- `completed_at timestamptz nullable`
- `diagnostics jsonb`
- `error_code text nullable`

Status values come from canonical vocabulary.

## 2A.11 `source_spans`

Fields:

- `source_span_id uuid PK`
- `source_asset_id uuid FK`
- `document_node_id uuid nullable FK`
- `source_text text nullable`
- `normalized_text text nullable`
- `printed_page_label text nullable`
- `source_asset_page_id uuid nullable FK`
- `bbox_json jsonb nullable`
- `text_start_offset integer nullable`
- `text_end_offset integer nullable`
- `extraction_method text`
- `extraction_confidence numeric nullable`
- `review_status text`
- `content_hash text nullable`

Rights may require `source_text` to remain private or absent while metadata and locators are retained.

## 2A.12 `source_inventory_snapshots`

Immutable inventory state used by a ResearchBuild.

Fields:

- `source_inventory_snapshot_id uuid PK`
- `created_at timestamptz`
- `inventory_schema_version text`
- `content_hash text`
- `metadata jsonb`

A ResearchBuild pins one snapshot where source inventory materially affects compilation.

---

# 3. Canonical reference layer

## 3.1 `biblical_books`

Represents an abstract biblical book identity.

Fields:

- `book_id uuid PK`
- `osis_code text unique`
- `hebrew_name text nullable`
- `english_name text`
- `traditional_chinese_name text nullable`

Removed from v1:
- universal `canonical_order`

Book order belongs to a canon system.

## 3.2 `canon_systems`

Fields:

- `canon_system_id uuid PK`
- `code text unique`
- `name text`
- `tradition text nullable`
- `description text nullable`

Examples may include a Jewish Tanakh ordering, a Protestant Old Testament ordering, or other explicit systems.

## 3.3 `canon_books`

Fields:

- `canon_system_id uuid FK`
- `book_id uuid FK`
- `book_order integer`
- `included boolean`

Unique:
`(canon_system_id, book_id)`

## 3.4 `reference_systems`

Defines chapter / verse addressing systems.

Fields:

- `reference_system_id uuid PK`
- `code text unique`
- `name text`
- `version text nullable`
- `description text nullable`

## 3.5 `reference_atoms`

Application-owned minimal reference anchors.

Important:
A reference atom is **not a linguistic token**.

Fields:

- `reference_atom_id uuid PK`
- `book_id uuid FK`
- `sequence integer`
- `atom_kind text`
- `metadata jsonb`

Its job is to support stable reference and span mapping across versification systems.

**Published ReferenceAtom identity is immutable.** Once referenced by a published ResearchRelease, an atom must not be split, merged, renumbered or repurposed in place. Finer future granularity creates new anchors plus explicit mappings while historical releases continue to resolve their original atom IDs.

## 3.6 `reference_spans`

Fields:

- `reference_span_id uuid PK`
- `start_atom_id uuid FK`
- `end_atom_id uuid FK`
- `span_kind text`
- `metadata jsonb`

A research passage, commentary range, corpus match or apparatus locus may point to a span.

## 3.7 `reference_labels`

Human / provider addressing.

Fields:

- `reference_label_id uuid PK`
- `reference_system_id uuid FK`
- `book_id uuid FK`
- `label text`
- `chapter_number integer nullable`
- `verse_label text nullable`
- `sort_key integer`

## 3.8 `reference_label_members`

Maps a label to one or more reference atoms.

Fields:

- `reference_label_id uuid FK`
- `reference_atom_id uuid FK`
- `member_order integer`

This supports split / merged verse numbering and subverse addressing.

---

# 4. General text identity model

The old model treated Hebrew tokens and Chinese translation versions too independently. v1.1 introduces a general versioned text-expression model usable for Hebrew source text, LXX, Chinese translations and other textual versions.

## 4.1 `textual_works`

Represents the conceptual textual / translation work or tradition.

Examples:
- a Masoretic textual tradition / WLC-based text lineage;
- Septuagint as a textual-version family where appropriate;
- Chinese Union Version as a translation work.

Fields:

- `textual_work_id uuid PK`
- `work_kind text`
- `canonical_name text`
- `language_code text`
- `script_code text nullable`
- `description text nullable`

## 4.2 `textual_editions`

Represents a publication, revision or critical edition.

Fields:

- `textual_edition_id uuid PK`
- `textual_work_id uuid FK`
- `edition_label text`
- `publication_year integer nullable`
- `publisher text nullable`
- `editorial_body text nullable`
- `edition_status text`
- `metadata jsonb`

Examples:
A 1919 Chinese Union Version edition and a later revision are not the same edition.

## 4.3 `digital_expressions`

Represents a concrete machine-readable expression / transcription / digital derivation.

Fields:

- `digital_expression_id uuid PK`
- `textual_edition_id uuid FK nullable`
- `textual_work_id uuid FK`
- `expression_label text`
- `expression_version text nullable`
- `derivation_description text nullable`
- `source_checksum text nullable`
- `rights_policy_id uuid nullable`
- `provenance_id uuid FK`
- `metadata jsonb`

Critical rule:
A provider's digital text must not automatically be identified with a print edition.

Example:
An FHL digital expression may be historically related to the Chinese Union Version while still differing from a particular published revision.

## 4.3A `expression_derivations`

Structured lineage between immutable digital expressions.

Fields:

- `expression_derivation_id uuid PK`
- `from_digital_expression_id uuid FK`
- `to_digital_expression_id uuid FK`
- `relation_type text`
- `provenance_id uuid nullable FK`
- `notes text nullable`

Relation types include TRANSCRIBED_FROM, NORMALIZED_FROM, CORRECTED_AGAINST, MERGED_FROM, and REVISED_FROM.

A digital expression whose content has been referenced by a ResearchRelease is immutable; correction creates a new expression identity.

## 4.4 `provider_distributions`

Binds an external provider / API code to a digital expression.

Fields:

- `provider_distribution_id uuid PK`
- `provider_id uuid FK`
- `digital_expression_id uuid FK`
- `provider_version_code text`
- `distribution_version text nullable`
- `availability_metadata jsonb`
- `rights_policy_id uuid nullable`
- `active boolean`

Provider code is distribution identity, not translation-edition identity.

---

# 5. Text streams, readings and segments

## 5.1 `text_streams`

A digital expression may expose more than one reading stream.

Fields:

- `text_stream_id uuid PK`
- `digital_expression_id uuid FK`
- `stream_type text`
- `stream_version text nullable`
- `normalization_profile_id uuid nullable`

Examples of stream type:
- BASE
- WRITTEN
- READ
- EDITORIAL

Ketiv/Qere must not be represented only by one token status flag.

## 5.2 `text_segments`

Provider / expression-specific orthographic or target-language segments.

Fields:

- `text_segment_id uuid PK`
- `text_stream_id uuid FK`
- `reference_span_id uuid FK`
- `segment_order integer`
- `segment_storage_mode text`
- `surface_original text nullable`
- `segment_kind text`
- `source_identifier text nullable`
- `content_hash text nullable`
- `metadata jsonb`

`segment_storage_mode` is one of:

- PERSISTED_CONTENT
- PROVIDER_LOCATOR
- EPHEMERAL

Rules:

- PERSISTED_CONTENT requires persistent-storage rights and may store `surface_original`;
- PROVIDER_LOCATOR may leave `surface_original` null and resolve content through an approved provider locator;
- EPHEMERAL content is never part of an immutable public scholarly payload.

A segment is not assumed to be universally identical across OSHB, MACULA, BHSA, FHL, or another expression.

## 5.2A `provider_segment_locators`

Used when provider content may be displayed/retrieved but may not be persistently stored.

Fields:

- `provider_segment_locator_id uuid PK`
- `text_segment_id uuid unique FK`
- `provider_distribution_id uuid FK`
- `provider_reference text`
- `provider_segment_key text nullable`
- `observed_hash text nullable`
- `observed_at timestamptz nullable`
- `provider_version text nullable`
- `provenance_id uuid nullable FK`

## 5.3 `reading_correspondences`

Maps WRITTEN and READ streams, or other alternate readings.

Fields:

- `reading_correspondence_id uuid PK`
- `from_segment_id uuid FK`
- `to_segment_id uuid FK`
- `relation_type text`
- `provenance_id uuid FK`
- `review_status text`

This supports Ketiv/Qere effects on morphology, alignment and syntax without special-casing one token row.

---

# 6. Hebrew normalization profiles

## 6.1 `normalization_profiles`

Fields:

- `normalization_profile_id uuid PK`
- `profile_key text`
- `profile_version text`
- `unicode_version text`
- `normalization_engine text`
- `normalization_engine_version text`
- `rules_json jsonb`
- `description text`

Required profile vocabulary should include representations equivalent to:

- SOURCE_EXACT
- UNICODE_NFC
- UNICODE_NFD
- REMOVE_CANTILLATION
- REMOVE_CANTILLATION_KEEP_METEG
- REMOVE_NIQQUD
- CONSONANTAL
- SEARCH_CANONICAL

## 6.2 `segment_normalizations`

Fields:

- `text_segment_id uuid FK`
- `normalization_profile_id uuid FK`
- `normalized_text text`
- `normalized_hash text`

Unique:
`(text_segment_id, normalization_profile_id)`

Never use NFC text as source identity.

---

# 7. Linguistic annotation frameworks and layers

Phrase, clause, dependency, semantic role, morphology, segmentation, and discourse structures are annotation claims unless explicitly curated otherwise.

A dataset release may contain multiple independently versioned annotation layers from different scholarly/data lineages.

## 7.1 `annotation_frameworks`

Fields:

- `annotation_framework_id uuid PK`
- `framework_key text`
- `name text`
- `description text`
- `ontology_version text nullable`
- `source_registry_id uuid nullable FK`

A framework defines an annotation ontology or analytical system. It does not by itself prove that every layer of a combined dataset comes from that same framework.

## 7.2 `corpus_releases`

Pins a versioned digital expression/dataset import.

Fields:

- `corpus_release_id uuid PK`
- `digital_expression_id uuid FK`
- `release_name text`
- `release_version text nullable`
- `release_date date nullable`
- `commit_sha text nullable`
- `source_checksum text nullable`
- `importer_version text`
- `imported_at timestamptz`
- `rights_policy_id uuid nullable FK`

A corpus release no longer carries one universal `annotation_framework_id`.

## 7.3 `annotation_layers`

First-class independently pinned analysis layer.

Fields:

- `annotation_layer_id uuid PK`
- `corpus_release_id uuid FK`
- `annotation_framework_id uuid FK`
- `layer_kind text`
- `layer_version text NOT NULL`
- `source_registry_id uuid nullable FK`
- `provenance_id uuid nullable FK`
- `rights_policy_id uuid nullable FK`
- `content_hash text nullable`
- `metadata jsonb`

`layer_kind` comes from the canonical `annotationLayerKind` vocabulary.

Examples:

- morphology from OSHB;
- morpheme segmentation from OSHB;
- clause structure from Clear/MACULA;
- dependency from another layer;
- semantic-role annotation from another source.

## 7.4 `analysis_nodes`

Layer-scoped linguistic objects.

Fields:

- `analysis_node_id uuid PK`
- `annotation_layer_id uuid FK`
- `node_type text`
- `reference_span_id uuid FK`
- `node_order integer nullable`
- `external_node_id text nullable`
- `metadata jsonb`

A phrase or clause exists according to its pinned annotation layer.

## 7.5 `analysis_node_segments`

Fields:

- `analysis_node_id uuid FK`
- `text_segment_id uuid FK`
- `member_order integer`
- `membership_role text nullable`

## 7.6 `analysis_edges`

Fields:

- `analysis_edge_id uuid PK`
- `annotation_layer_id uuid FK`
- `from_node_id uuid FK`
- `to_node_id uuid FK`
- `relation_type text`
- `relation_ontology text`
- `properties jsonb`
- `provenance_id uuid nullable FK`

An edge must not connect nodes from incompatible layer semantics unless the relation definition explicitly permits a cross-layer mapping.

## 7.7 `cross_annotation_mappings`

Mappings are research data, not identity assumptions.

Fields:

- `cross_annotation_mapping_id uuid PK`
- `from_annotation_layer_id uuid FK`
- `from_node_id uuid FK`
- `to_annotation_layer_id uuid FK`
- `to_node_id uuid FK`
- `mapping_type text`
- `confidence numeric nullable`
- `mapping_method text`
- `review_status text`
- `provenance_id uuid nullable FK`

## 7.8 `equivalence_hypotheses`

Optional curated cross-framework analytical equivalence.

Fields:

- `equivalence_hypothesis_id uuid PK`
- `hypothesis_type text`
- `statement text`
- `review_status text`
- `created_by uuid nullable`

These may support comparative research but must never make provider analyses silently identical.

---

# 8. Lexeme and feature identity

## 8.1 `lexemes`

Application-level linguistic identity used only where cross-source identification is defensible.

Fields:

- `lexeme_id uuid PK`
- `language_code text`
- `display_lemma text`
- `homonym_number text nullable`
- `lexeme_status text`
- `metadata jsonb`

## 8.2 `lexeme_identifiers`

Fields:

- `lexeme_identifier_id uuid PK`
- `lexeme_id uuid FK`
- `identifier_system text`
- `identifier_value text`
- `mapping_type text`
- `confidence numeric nullable`
- `source_registry_id uuid nullable`
- `review_status text`
- `version text nullable`

Possible systems:
- OSHB lemma
- BHSA lexeme
- Strong
- BDB locator
- HALOT locator
- DCH locator
- SDBH / other explicit systems

One Hebrew string is not sufficient to establish shared lexeme identity.

## 8.3 `lexeme_forms`

Fields:

- `lexeme_form_id uuid PK`
- `lexeme_id uuid FK`
- `form_text text`
- `normalization_profile_id uuid nullable`
- `form_type text`
- `provenance_id uuid nullable`

## 8.4 `analysis_node_lexemes`

Framework-scoped assignment.

Fields:

- `analysis_node_id uuid FK`
- `lexeme_id uuid FK`
- `assignment_type text`
- `confidence numeric nullable`
- `provenance_id uuid FK`

## 8.5 `feature_schemas`

Fields:

- `feature_schema_id uuid PK`
- `annotation_framework_id uuid FK`
- `schema_key text`
- `schema_version text`
- `definition_json jsonb`

## 8.6 `analysis_features`

Fields:

- `analysis_feature_id uuid PK`
- `analysis_node_id uuid FK`
- `feature_schema_id uuid FK`
- `feature_key text`
- `value_json jsonb`
- `provenance_id uuid FK`

## 8.7 `feature_mappings`

Cross-framework mapping of feature meanings.

Fields:

- `feature_mapping_id uuid PK`
- `from_feature_schema_id uuid FK`
- `from_feature_key text`
- `to_feature_schema_id uuid FK`
- `to_feature_key text`
- `mapping_type text`
- `confidence numeric nullable`
- `review_status text`

---

# 9. Alignment architecture

The old v1 multi-row span model is superseded.

## 9.1 `alignment_groups`

Fields:

- `alignment_group_id uuid PK`
- `source_expression_id uuid FK`
- `target_expression_id uuid FK`
- `source_text_stream_id uuid FK`
- `target_text_stream_id uuid FK`
- `reference_span_id uuid FK`
- `relation_type text`
- `method text`
- `algorithm_version text nullable`
- `confidence numeric nullable`
- `review_status text`
- `reviewed_by uuid nullable`
- `provenance_id uuid FK`

Relation types must be capable of representing:
- one-to-one
- one-to-many
- many-to-one
- many-to-many
- source-only / omission
- target-only / addition

## 9.2 `alignment_source_members`

Fields:

- `alignment_group_id uuid FK`
- `text_segment_id uuid FK`
- `member_order integer`

## 9.3 `alignment_target_members`

Same shape for target segments.

Primary alignment should use stable segment IDs.

Every source member segment must belong to `source_text_stream_id`; every target member segment must belong to `target_text_stream_id`. This prevents Ketiv WRITTEN and Qere READ alignment from being mixed implicitly inside one alignment group.

Raw character offsets are secondary locators only.

## 9.4 `text_offsets`

Where exact character localisation is required, record:

- `text_segment_id uuid FK`
- `offset_basis text`
- `start_offset integer`
- `end_offset integer`
- `text_revision_hash text`
- `normalization_profile_id uuid nullable`

Allowed coordinate systems must be explicit, for example:
- UTF8_BYTE
- UNICODE_CODEPOINT
- UTF16_CODEUNIT
- GRAPHEME_CLUSTER

Never store an integer offset without its coordinate system and source revision hash.

---

# 10. Translation research identity

Chinese translation research uses the general text model.

Additional translation-specific metadata may live in:

## 10.1 `translation_profiles`

Fields:

- `textual_work_id uuid FK`
- `translation_language text`
- `source_language text nullable`
- `stated_philosophy_status text`
- `metadata jsonb`

## 10.2 `translation_documentation`

Links a textual work / edition / expression to:
- prefaces;
- publisher statements;
- translator notes;
- revision documentation;
- style guides.

A provider distribution such as an FHL version code is never by itself sufficient to prove a print-edition reading or translator intention.

---

# 11. Ancient versions and LXX

LXX is a research domain, not merely a display column.

The general text model must support:

- Greek textual work / edition;
- digital expression;
- Greek text segments;
- Greek linguistic annotation when available;
- Hebrew-Greek alignment;
- textual-critical witness role.

Stage 1 may display an LXX witness with limited functionality, but the schema must not force LXX into a modern-Chinese-translation-only model.

---

# 12. Rights policy and deterministic rights resolution

A single asset-level boolean profile is insufficient.

## 12.1 `rights_policies`

Versioned policy / terms identity.

Fields:

- `rights_policy_id uuid PK`
- `policy_key text`
- `policy_version text`
- `rights_basis text`
- `copyright_holder text nullable`
- `terms_source text nullable`
- `terms_snapshot_hash text nullable`
- `effective_from timestamptz nullable`
- `effective_until timestamptz nullable`
- `territory text nullable`
- `notes text nullable`
- `verified_at timestamptz nullable`

## 12.2 `rights_policy_bindings`

Binds one policy to an explicit subject.

Fields:

- `rights_policy_binding_id uuid PK`
- `rights_policy_id uuid FK`
- `subject_type text`
- `subject_identifier uuid`
- `binding_priority integer default 0`
- `active boolean`

The publication/compiler layer must validate that the subject identifier exists in the corresponding typed table or controlled research-object registry.

## 12.3 `rights_rules`

Fields:

- `rights_rule_id uuid PK`
- `rights_policy_id uuid FK`
- `operation text`
- `decision text`
- `purpose_scope text nullable`
- `audience_scope text nullable`
- `commercial_context text nullable`
- `provider_constraint text nullable`
- `max_excerpt_value numeric nullable`
- `excerpt_unit text nullable`
- `conditions_json jsonb nullable`
- `attribution_requirement text nullable`

Operations and decisions come from canonical vocabulary.

Enforceable excerpt limits must always carry an explicit unit from `rightsExcerptUnit`. A bare integer excerpt limit is invalid.

Free-text scopes are no longer authoritative. Canonical scope values must come from:

- `rightsPurposeScope`;
- `rightsAudienceScope`;
- `rightsCommercialContext`.

## 12.4 Rights Resolution Contract

For every protected operation, the resolver must:

1. identify the concrete rights subject;
2. collect all active policies bound directly or inherited by explicit product rules;
3. filter by effective date and territory;
4. filter by requested operation;
5. filter by purpose, audience, commercial context, and provider constraint;
6. order applicable bindings by specificity/priority;
7. within the highest applicable specificity, resolve decisions using `DENY > CONDITIONAL > ALLOW`;
8. treat UNKNOWN or no applicable permission as DENY for restricted operations;
9. evaluate machine-readable conditions;
10. emit an immutable RightsDecisionSnapshot.

A less-specific ALLOW must never override a more-specific DENY.

## 12.5 `rights_decision_snapshots`

Fields:

- `rights_decision_snapshot_id uuid PK`
- `subject_type text`
- `subject_identifier uuid`
- `operation text`
- `purpose_scope text`
- `audience_scope text`
- `commercial_context text`
- `applicable_rule_ids jsonb`
- `winning_rule_ids jsonb`
- `decision text`
- `conditions_json jsonb nullable`
- `resolver_version text`
- `evaluated_at timestamptz`
- `decision_hash text`

Publication must pin the rights decision snapshots used for publishability.

Critical rule:

Permission to privately read or display a source does not automatically grant permission to persist it, embed it, redistribute it, or send full text to an external model provider.

---

# 12A. Review governance

`review_status` is a materialized summary, not the audit trail itself.

## 12A.1 `review_events`

Fields:

- `review_event_id uuid PK`
- `research_object_id uuid FK -> research_objects`
- `research_object_version text nullable`
- `review_type text`
- `reviewer_agent_id uuid nullable FK -> provenance_agents`
- `reviewer_role text`
- `criteria_version text`
- `decision text`
- `qualification text nullable`
- `source_basis jsonb nullable`
- `reviewed_at timestamptz`

Canonical review types distinguish bibliographic identity, source entailment, Hebrew linguistic analysis, translation judgment, rights review, and publication approval.

A generic `VERIFIED` flag must never be interpreted as proving all review dimensions.

---

# 13. Academic source model corrections

The Work -> Edition -> SourceAsset foundation remains.

## 13.1 Publication form and scholarly role remain separate

`works.publication_type` uses the canonical `publicationType` vocabulary.

Examples:

- MONOGRAPH
- REFERENCE_WORK
- JOURNAL_ARTICLE
- BOOK_CHAPTER
- EDITED_VOLUME
- CONFERENCE_PAPER
- DISSERTATION
- THESIS
- CRITICAL_EDITION
- DATASET_PUBLICATION
- DIGITAL_RESOURCE
- TRANSLATION_DOCUMENTATION
- CRITICAL_REVIEW
- COURSE_MATERIAL
- USER_NOTE

Scholarly function is many-to-many through `work_source_roles` and uses `sourceRole`.

Examples:

- REFERENCE_GRAMMAR
- CORPUS_LINGUISTICS
- GENERAL_LEXICON
- TEXTUAL_CRITICISM_METHOD
- COMMENTARY
- CHINESE_TRANSLATION_STUDIES

Do not recreate a mixed `work_type` enum.

## 13.2 Bibliographic identifiers

Add structured metadata for relevant types:

- DOI
- ISBN
- ISSN
- journal title
- volume
- issue
- page range
- series
- editors
- publication status
- correction / retraction status where relevant
- peer-review status where known

The Google Drive shelf is a source library, not the epistemic boundary of the application.

---
# 14. Edition structure versus asset location

The old v1 placed PDF-page coordinates partly on document nodes. This is superseded.

## 14.1 `document_nodes`

Edition-level intellectual structure:

- chapter
- section
- subsection
- paragraph
- footnote
- appendix

Fields include printed-page labels where those belong to the edition.

## 14.2 `source_asset_pages`

Asset-specific page identity.

Fields:

- `source_asset_page_id uuid PK`
- `source_asset_id uuid FK`
- `pdf_page_index integer`
- `page_label_detected text nullable`
- `image_hash text nullable`

## 14.3 `node_asset_locations`

Maps edition structure to asset pages / coordinates.

Fields:

- `document_node_id uuid FK`
- `source_asset_id uuid FK`
- `start_page_id uuid FK`
- `end_page_id uuid FK nullable`
- `bbox_json jsonb nullable`

One printed edition may have several PDF assets with different physical page indices.

---

# 15. Scholarly claims are representations, not automatically the author's exact proposition

## 15.1 `scholarly_claims`

Add:

- `claim_representation_type`
- `assertion_agent_type`
- `assertion_agent_id nullable`
- `claim_source_text nullable`
- `claim_paraphrase nullable`
- `claim_scope jsonb nullable`
- `claim_modal_force text nullable`
- `entailed_by_source_review_status text`
- `reviewed_by uuid nullable`

Representation types:

- DIRECT_QUOTE
- HUMAN_PARAPHRASE
- AI_EXTRACTED_PROPOSITION

Only a source span is the author's actual text.

An AI-extracted proposition must not silently become equivalent to author wording.

## 15.2 `claim_relations`

Also record:
- relation assertion agent;
- evidence / source for the relation;
- review status.

A system-inferred CONTRADICTS edge is not the same as one author explicitly criticising another.

---

# 16. Scholarly lineage and evidence independence

## 16.1 `scholarly_dependencies`

Fields:

- `scholarly_dependency_id uuid PK`
- `from_research_object_id uuid FK -> research_objects`
- `to_research_object_id uuid FK -> research_objects`
- `relation_type text`
- `source_span_id uuid nullable`
- `assertion_agent_type text`
- `review_status text`

Allowed endpoint subtypes are constrained to scholarly works, claims, datasets, and other explicitly approved scholarly objects. Generic UUIDs without registry-level identity are not permitted.

Possible relations:

- CITES
- ADOPTS_CLASSIFICATION_FROM
- REVISES
- CRITIQUES
- USES_DATASET
- DERIVED_FROM
- SUMMARISES

Distinct work count must not be treated as a direct measure of independent corroboration.

This graph may be populated incrementally and does not block Stage 1.

---

# 17. Textual criticism v1.1

The system must preserve raw apparatus before interpreting it.

## 17.1 `apparatus_sources`

Identifies BHS, BHQ or another apparatus edition / source.

## 17.2 `apparatus_raw_entries`

Fields:

- `apparatus_raw_entry_id uuid PK`
- `apparatus_source_id uuid FK`
- `reference_span_id uuid FK`
- `raw_text text nullable`
- `source_span_id uuid nullable`
- `content_hash text nullable`

Parsed structures are derived from this representation.

## 17.3 `apparatus_entries`

Fields include:
- locus;
- lemma;
- entry type;
- responsible editor where encoded;
- certainty;
- parsing review status.

## 17.4 `apparatus_reading_groups`

Supports grouped / subvariant readings.

## 17.5 `apparatus_readings`

Fields may include:
- reading text;
- reading type;
- cause;
- variation sequence;
- responsibility;
- certainty;
- conjectural / reconstructed status.

## 17.6 `textual_witnesses`

Witness identity and type.

## 17.6A `textual_witness_identifiers`

A siglum is source-contextual, not a universal witness identity.

Fields:

- `textual_witness_identifier_id uuid PK`
- `textual_witness_id uuid FK`
- `apparatus_source_id uuid FK`
- `siglum text`
- `identifier_note text nullable`

Unique:
`(apparatus_source_id, siglum)`

## 17.6B `apparatus_loci`

Exact apparatus anchoring may be narrower than a verse/reference span.

Fields:

- `apparatus_locus_id uuid PK`
- `apparatus_entry_id uuid FK`
- `base_text_stream_id uuid FK`
- `start_text_segment_id uuid FK`
- `end_text_segment_id uuid FK`
- `start_offset integer nullable`
- `end_offset integer nullable`
- `offset_basis text nullable`
- `anchoring_method text`
- `review_status text`

## 17.6C `textual_edition_publications`

Bridges a textual-critical edition identity to its bibliographic publication/edition identity.

Fields:

- `textual_edition_id uuid FK`
- `academic_edition_id uuid FK -> editions`
- `relation_type text`

## 17.7 `witness_attestations`

Fields:

- `apparatus_reading_id uuid FK`
- `textual_witness_id uuid FK`
- `attestation_status text`
- `certainty text nullable`
- `notes text nullable`

Attestation status must be able to distinguish uncertainty, lacuna, fragmentary evidence, retroversion and similar conditions where appropriate.

The goal is TEI-compatible conceptual richness, not mandatory one-to-one implementation of all TEI elements in the first MVP.

---

# 18. Research-object registry and referential integrity

The old v1 relied too heavily on `object_type + uuid` without database-enforced existence.

v1.1 uses a controlled supertype registry for first-class publishable/evidence objects.

## 18.1 `research_objects`

Fields:

- `research_object_id uuid PK`
- `object_type text`
- `created_at timestamptz`

For first-class publishable version objects, prefer **shared primary-key identity**:

```text
subtype_version_id
  PK
  FK -> research_objects.research_object_id
```

This allows `research_release_components.component_research_object_id` to have a real FK while preserving subtype tables.

Objects expected to participate as release components or public evidence should use this pattern, including where applicable:

- corpus release;
- annotation layer;
- translation release/expression snapshot;
- semantic-set version;
- construction-definition version;
- rule-set/rule version aggregate;
- knowledge-graph release;
- published analysis set;
- citation/bibliography release;
- compiled-search release;
- scholarly issue graph;
- literature snapshot/review;
- commentary release.

Generic edges may point to `research_objects`, guaranteeing registry-level existence.

The publication compiler additionally validates that `object_type` is compatible with the requested release `component_kind`.

Use dedicated typed bridge tables where the relation is structurally central.

Do not replace every ordinary FK with the object registry.

---

# 19. Corpus Query DSL v1.1

## 19.1 Scope must pin text and analysis context

A query must declare:

- digital expression or corpus release;
- annotation framework where framework-sensitive relations are used;
- normalization profile where text matching depends on it;
- semantic-set versions where applicable.

Example:

```json
{
  "version": "1.1",
  "textContext": {
    "digitalExpressionId": "...",
    "normalizationProfile": "SEARCH_CANONICAL"
  },
  "analysisContext": {
    "annotationFrameworkId": "...",
    "corpusReleaseId": "..."
  },
  "nodes": [],
  "relations": [],
  "resultMode": "construction"
}
```

## 19.2 Relation classes

### Text-stream relations

Potentially comparable when their text model is compatible:

- immediately_precedes
- precedes
- follows
- within_n_segments
- same_reference_span

### Framework-scoped relations

Require `analysisContext`:

- same_phrase
- same_clause
- same_sentence
- attached_to
- governs
- dependent_of
- semantic_role
- morpheme_of
- has_morpheme
- prefix_morpheme_of
- suffix_morpheme_of

Morpheme-host relations are framework/release-scoped analytical relations. A prefixed ל must not be modeled as an independent orthographic word merely to simplify search.

Do not execute a framework-scoped relation over multiple frameworks unless an explicit mapping / comparative mode is requested.

### Boolean and quantifier expression layer

The query AST must support a constrained expression tree using the canonical vocabulary:

- ALL_OF
- ANY_OF
- NOT
- EXISTS
- NOT_EXISTS
- MIN_COUNT
- MAX_COUNT
- EXACT_COUNT

General SQL-like arbitrary expressions are not allowed.

A generic OPTIONAL binding is deliberately deferred until its result-set and counting semantics are specified and benchmarked. Use EXISTS/NOT_EXISTS/count constraints for v1.1 where possible.

## 19.3 Result epistemic class

Every query run reports one:

- `CORPUS_COMPLETE`
- `FRAMEWORK_COMPLETE`
- `CURATED_SET_COMPLETE`
- `HEURISTIC_CANDIDATE`
- `INCOMPLETE_COVERAGE`

Examples:

A fully enumerated lemma query over a pinned release may be corpus-complete for that release.

A semantic analogue set derived from a user semantic taxonomy is normally taxonomy-dependent and should not be presented as linguistically exhaustive.

"Find all" language in the UI must be bounded by corpus, release, framework and query definition.

---

# 20. Corpus analysis protocol

Frequency and count claims require research-design metadata.

## 20.1 `corpus_analysis_protocols`

Fields:

- `corpus_analysis_protocol_id uuid PK`
- `population_definition text`
- `inclusion_criteria jsonb`
- `exclusion_criteria jsonb`
- `grouping_variables jsonb nullable`
- `denominator_definition text nullable`
- `coverage_notes text nullable`
- `genre_controls jsonb nullable`
- `review_status text`

## 20.2 Query-run dependency tables

Replace UUID arrays with junction tables:

- `query_run_corpus_releases`
- `query_run_semantic_set_versions`
- `query_run_normalization_profiles`

All receive proper FKs.

Counts remain separated:

- token matches;
- construction matches;
- clause matches;
- reference / verse matches;
- passage spans.

---

# 20A. Semantic sets

The v1.1 candidate previously referenced semantic-set versions without redefining their tables. This section closes that contract gap.

## 20A.1 `semantic_sets`

Fields:

- `semantic_set_id uuid PK`
- `name text`
- `description text nullable`
- `owner_user_id uuid nullable`
- `set_scope text`
- `official_status text`
- `current_version_id uuid nullable`

## 20A.2 `semantic_set_versions`

Append-only.

Fields:

- `semantic_set_version_id uuid PK`
- `semantic_set_id uuid FK`
- `version_number integer`
- `definition_json jsonb`
- `review_status text`
- `created_at timestamptz`

## 20A.3 `semantic_set_members`

Fields:

- `semantic_set_version_id uuid FK`
- `member_object_type text`
- `member_object_id uuid nullable`
- `member_key text nullable`
- `inclusion_type text`
- `reason text nullable`
- `provenance_id uuid nullable`
- `confidence numeric nullable`
- `review_status text`

Official public queries must pin a published semantic-set version.

Semantic-set membership is compiled research data. Runtime LLM classification must not silently alter official set membership.

---

# 21. Retrieval namespaces and canonical vocabulary

The project must have one machine-readable vocabulary source.

Do not use near-synonymous enum names in different architecture documents.

A canonical vocabulary artifact is stored under:

`contracts/v1.1/vocabulary.json`

Markdown documents must defer to that file where a vocabulary conflicts.

Important conceptual separation:

- SOURCE_ROLE: scholarly classification of a work;
- RETRIEVAL_NAMESPACE: where a retrieval request is routed;
- EVIDENCE_CLASS: epistemic role in an answer;
- LIFECYCLE_STATUS: operational workflow.

These are not interchangeable.

---

# 22. Security and RAG trust boundaries

The detailed security model lives in:

`architecture/security-trust-boundaries.md`

Required principles include:

- retrieved documents are untrusted DATA, never instructions;
- document content cannot change tool permissions or rights mode;
- service credentials never reach the browser;
- grants and RLS are both tested;
- views use safe invoker semantics or are kept unexposed;
- security-definer functions and RPC EXECUTE grants are explicitly reviewed;
- ingestion origin and hash are recorded;
- hidden / suspicious content is detectable;
- retrieval access is logged;
- cross-tenant leakage tests are mandatory;
- vector retrieval filtered recall is tested under tenant / rights filters.

---

# 23. Research evaluation

The architecture must include a gold-set evaluation system before academic RAG / orchestration is considered production-ready.

Detailed plan:

`architecture/research-evaluation-and-benchmarks.md`

Minimum metrics include:

- exact citation recall;
- retrieval Recall@k;
- Precision@k;
- MRR / nDCG where appropriate;
- counterevidence recall;
- source diversity;
- rule + qualification co-retrieval;
- citation-source entailment;
- unsupported-claim rate;
- rights leakage rate;
- filtered vector recall under RLS / rights constraints.

The benchmark may start small and grow. It does not need to block early UI scaffolding, but Stage 4/5 cannot be judged ready by subjective answer quality alone.

---

# 24. Analysis assertion ledger

Evidence packet provenance is necessary but not sufficient.

## 24.0 `analysis_runs`

Private authoring analysis execution.

Fields:

- `analysis_run_id uuid PK`
- `analysis_type text`
- `reference_span_id uuid nullable FK`
- `model_provider text nullable`
- `model_version text nullable`
- `prompt_version text nullable`
- `evidence_packet_hash text nullable`
- `settings_json jsonb nullable`
- `started_at timestamptz`
- `completed_at timestamptz nullable`
- `output_hash text nullable`
- `status text`

## 24.0A `authoring_evidence_packets`

Private evidence assembly used during research compilation.

Fields:

- `authoring_evidence_packet_id uuid PK`
- `analysis_run_id uuid nullable FK`
- `packet_schema_version text`
- `packet_hash text`
- `created_at timestamptz`

Private source spans, private locators, embeddings, or model notes may be associated through authoring-only typed junction tables.

An authoring evidence packet is never a public API object.

## 24.1 `analysis_assertions`

Fields:

- `analysis_assertion_id uuid PK`
- `analysis_run_id uuid FK`
- `assertion_text text`
- `assertion_type text`
- `inference_type text`
- `confidence_class text nullable`
- `sort_order integer`

## 24.2 `analysis_assertion_evidence`

Fields:

- `analysis_assertion_id uuid FK`
- `research_object_id uuid FK`
- `research_object_version text nullable`
- `evidence_content_hash text nullable`
- `stance text`
- `citation_locator jsonb nullable`
- `entailment_review_status text`
- `weight_metadata jsonb nullable`

Historical analyses should pin immutable evidence versions/hashes where the evidence object itself is versioned.

## 24.3 `analysis_assertion_relations`

Fields:

- `from_assertion_id uuid FK`
- `to_assertion_id uuid FK`
- `relation_type text`

Citation must follow the individual analytical assertion, not only the analysis run.

---

# 25. Reproducibility terminology

Do not promise bit-for-bit deterministic LLM reproducibility.

Use three concepts:

## 25.1 Research-input reproducibility

Can reconstruct:
- text / corpus release;
- query;
- semantic set;
- evidence sources;
- rights mode;
- rule versions;
- user translation version;
- prompt template;
- retrieval plan.

## 25.2 Model-execution auditability

Store where available:
- provider;
- exact model identifier / snapshot;
- sampling parameters;
- request payload hash;
- tool-call log;
- response snapshot;
- response hash;
- evidence packet hash.

## 25.3 Deterministic output reproducibility

Not guaranteed for hosted generative models unless the serving system explicitly provides that guarantee.

The academically important guarantee is that the evidence state and research process are replayable and auditable.

---

# 26. Stage-boundary corrections

The product planes are continuous operational boundaries; the five build stages are implementation sequencing only.

## Stage 1

Must establish:
- canon/reference atoms and spans;
- general textual work / edition / digital-expression identity;
- provider distribution abstraction;
- **minimal text stream and text segment identity required by Stage 2 alignment**;
- source registry / provenance;
- rights-policy framework;
- product-plane boundaries;
- ResearchBuild / ResearchRelease foundation;
- canonical vocabulary;
- evidence labels;
- trust-boundary scaffolding.

Stage 1 must not create universal Hebrew linguistic tokens, phrases or clauses.

## Stage 2

Passage / translation workspace:
- versioned text expressions;
- provider distributions;
- stable text segments for source/target alignment;
- translation profiles;
- alignment groups and segment members;
- user translation proposal/version contracts;
- documented translator-note identity;
- published passage/translation read contracts.

## Stage 3

Hebrew corpus and search:
- normalization profiles;
- reading correspondences;
- annotation frameworks;
- analysis nodes / edges;
- explicit morpheme-host relations;
- lexeme identity;
- feature schemas;
- semantic sets and versions;
- framework-aware CorpusQuery AST;
- Boolean/negation/quantifier expression layer;
- bounded completeness classes;
- corpus-analysis protocols;
- ConstructionDefinition / ConstructionInstance;
- compiled serving projections.

## Stage 4

Private academic knowledge compilation and publication:
- expanded bibliographic types;
- source assets and asset pages;
- structured claims with representation status;
- lexica / commentary / textual-critical specialised models;
- scholarly dependency;
- rights-aware private retrieval;
- AI-assisted candidate extraction/mapping;
- rule evidence;
- editorial review;
- publication validation;
- security testing;
- benchmark evaluation;
- release candidate creation.

Stage 4 RAG is primarily authoring/build-time infrastructure, not a required public runtime dependency.

## Stage 5

Rule compilation, published analysis and serving completion:
- official rule/version model;
- build-time rule applications where compilable;
- translation decisions;
- published passage analyses;
- release manifest finalization;
- deterministic public query APIs;
- optional natural-language-to-DSL adapter;
- user workspace integration;
- full regression / product QA.

The public core must remain functional when the optional LLM adapter is unavailable.

---

# 27. Deferred features that must not block early implementation

The following are architecturally supported but do not need full population in Stage 1:

- complete scholarly citation dependency graph;
- complete LXX morphology / syntax corpus;
- exhaustive TEI critical-apparatus parity;
- complete Chinese translation-history library;
- large 100-question benchmark;
- human adjudication of all cross-framework mappings.

The architecture must leave clean extension points without pretending those datasets already exist.

---

# 28. Freeze-gate governance

Do not maintain a second numbered freeze list here.

All preconditions are identified by stable IDs in:

- `contracts/v1.1/freeze-checklist.md`

Core implementation may proceed to Database Spike only after `CORE_SPIKE_V1_1` passes.

Full Core freeze, Research Pro extension freeze, and BYOK shipping remain separate gates.

---

# 29. Product execution and release contract

Detailed topology is defined in `architecture/product-platform-and-publication-model.md`.

The active contract recognizes four logical product planes:

- AUTHORING_RESEARCH
- PUBLICATION_CONTROL
- PUBLIC_SERVING
- USER_WORKSPACE

These are not evidence classes.

## 29.1 `research_builds`

Mutable compilation attempt.

Fields:

- `research_build_id uuid PK`
- `build_version text`
- `status text`
- `started_at timestamptz`
- `completed_at timestamptz nullable`
- `compiler_version text`
- `git_commit_sha text`
- `source_inventory_snapshot_id uuid nullable FK`
- `benchmark_version text nullable`

Build status comes from `researchBuildStatus`.

A ResearchBuild never has PUBLISHED as its lifecycle state.

## 29.2 `research_releases`

Immutable release payload identity.

Fields:

- `research_release_id uuid PK`
- `release_label text unique`
- `source_build_id uuid FK`
- `published_at timestamptz`
- `manifest_schema_version text`
- `manifest_hash text`
- `manifest_hash_algorithm text`
- `manifest_canonical_serialization text`
- `git_commit_sha text`
- `compiler_version text`
- `benchmark_version text nullable`

After creation/publication, release payload and manifest are immutable.

Lifecycle availability is not stored as a mutable status on this row.

## 29.3 `research_release_components`

Fields:

- `research_release_id uuid FK`
- `component_kind text`
- `component_research_object_id uuid FK -> research_objects`
- `component_version text`
- `content_hash text`
- `component_order integer NOT NULL`

The publication compiler must validate compatibility between `component_kind` and the registered research-object subtype.

Do not use an unchecked naked UUID as release-manifest provenance.

## 29.4 `research_release_events`

Append-only lifecycle history.

Fields:

- `research_release_event_id uuid PK`
- `research_release_id uuid FK`
- `event_type text`
- `effective_at timestamptz`
- `reason text nullable`
- `changed_by uuid nullable`
- `metadata jsonb`

Event type comes from `researchReleaseEventType`.

## 29.5 `release_channels`

Fields:

- `release_channel_id uuid PK`
- `channel_key text unique`
- `description text nullable`

Canonical keys:

- PREVIEW
- STAGING
- PRODUCTION

## 29.6 `release_channel_pointers`

Mutable deployment pointer, separate from release immutability.

Fields:

- `release_channel_id uuid PK/FK`
- `research_release_id uuid FK`
- `updated_at timestamptz`
- `updated_by uuid nullable`
- `row_version integer`

Rollback changes a channel pointer. It does not mutate historical release payloads.

## 29.7 Release manifest hashing

The canonical release manifest payload excludes `manifest_hash` itself.

Required algorithm:

- canonical serialization: RFC 8785 JSON Canonicalization Scheme;
- encoding: UTF-8;
- hash: SHA-256.

The manifest includes at minimum:

- manifest schema version;
- research release ID/label;
- source build ID;
- compiler version;
- Git commit SHA;
- benchmark version where applicable;
- ordered release components;
- each component kind;
- each registered research-object ID;
- component version;
- component content hash.

Release components are serialized in ascending unique `component_order`. The publication validator rejects duplicate/missing order values. RFC 8785 canonicalizes object representation but does not reorder semantic arrays.

A public response containing canonical published scholarship must be resolvable to a research release.

---

# 30. User translation workspace contract

The v1.1 candidate previously referred to user translation versioning without redefining the old v1 tables.

## 30.1 `user_translation_proposals`

Fields:

- `user_translation_id uuid PK`
- `project_id uuid FK`
- `reference_span_id uuid FK`
- `owner_user_id uuid`
- `current_version_id uuid nullable`
- `status text`

## 30.2 `user_translation_versions`

Append-only.

Fields:

- `user_translation_version_id uuid PK`
- `user_translation_id uuid FK`
- `version_number integer`
- `translation_text text`
- `translation_notes text nullable`
- `created_at timestamptz`
- `supersedes_version_id uuid nullable`

User drafts are workspace data. They are not official published translation data unless promoted through authoring/review/publication.

---

# 31. Construction contract

## 31.1 `construction_definitions`

Stable formal pattern identity.

Fields:

- `construction_definition_id uuid PK`
- `name text`
- `description text nullable`
- `current_version_id uuid nullable`
- `status text`

## 31.2 `construction_definition_versions`

Fields:

- `construction_definition_version_id uuid PK`
- `construction_definition_id uuid FK`
- `version_number integer`
- `dsl_version text`
- `query_ast jsonb`
- `query_ast_hash text`
- `review_status text`
- `created_at timestamptz`

The Query AST is authoritative.

Framework/layer, semantic-set, normalization, and relation dependencies are compiler-derived rather than manually duplicated.

## 31.3 `construction_compilation_runs`

Fields:

- `construction_compilation_run_id uuid PK`
- `construction_definition_version_id uuid FK`
- `corpus_release_id uuid FK`
- `query_ast_hash text`
- `dependency_manifest jsonb`
- `compiler_version text`
- `started_at timestamptz`
- `completed_at timestamptz nullable`
- `result_count integer nullable`
- `result_set_hash text nullable`
- `status text`

The dependency manifest must include every annotation-layer version, semantic-set version, normalization profile, and relation ontology actually used.

## 31.4 `construction_instances`

Fields:

- `construction_instance_id uuid PK`
- `construction_compilation_run_id uuid FK`
- `reference_span_id uuid FK`
- `node_bindings jsonb`
- `match_explanation jsonb`
- `review_status text`
- `result_hash text`

A construction instance is a corpus-analysis result, not a translation conclusion.

---

# 32. Official rule contract

## 32.1 `rules`

Fields:

- `rule_id uuid PK`
- `name text`
- `rule_kind text`
- `status text`
- `current_version_id uuid nullable`

Official rule kinds are defined in canonical vocabulary.

A SEARCH_PATTERN is not a rule kind; formal patterns belong to constructions.

## 32.2 `rule_versions`

Append-only.

Fields:

- `rule_version_id uuid PK`
- `rule_id uuid FK`
- `version_number integer`
- `scope_json jsonb`
- `trigger_construction_version_id uuid nullable FK`
- `condition_ast jsonb nullable`
- `implication_json jsonb`
- `priority integer nullable`
- `specificity integer nullable`
- `review_status text`
- `created_at timestamptz`

## 32.3 `rule_evidence`

Fields:

- `rule_version_id uuid FK`
- `research_object_id uuid FK`
- `research_object_version text nullable`
- `evidence_content_hash text nullable`
- `stance text`
- `citation_locator jsonb nullable`
- `notes text nullable`

## 32.4 `rule_applications`

Fields:

- `rule_application_id uuid PK`
- `rule_version_id uuid FK`
- `construction_instance_id uuid nullable FK`
- `reference_span_id uuid FK`
- `matched_conditions jsonb`
- `failed_conditions jsonb nullable`
- `exception_status text`
- `effect text`
- `result_json jsonb`
- `review_status text`
- `result_hash text`

`effect` comes from `ruleApplicationEffect`:

- SUPPORTS
- DISFAVOURS
- REQUIRES
- PROHIBITS
- QUALIFIES
- NO_DECISION

## 32.5 `rule_conflicts`

Records unresolved or editorially resolved tension between rule applications.

Fields:

- `rule_conflict_id uuid PK`
- `reference_span_id uuid FK`
- `left_rule_application_id uuid FK`
- `right_rule_application_id uuid FK`
- `conflict_type text`
- `resolution_status text`
- `resolved_by_translation_decision_id uuid nullable`
- `notes text nullable`

The rule engine must not silently implement "highest priority wins" as scholarly truth.

Rule application remains distinct from final translation decision.

---

# 33. Translation decision and published analysis contract

## 33.1 `translation_decisions`

First-class editorial scholarly object.

Fields:

- `translation_decision_id uuid PK`
- `reference_span_id uuid FK`
- `source_digital_expression_id uuid FK`
- `target_language_code text`
- `decision_kind text`
- `selected_rendering text nullable`
- `ambiguity_strategy text nullable`
- `decision_schema_version text`
- `decision_payload jsonb`
- `review_status text`
- `supersedes_decision_id uuid nullable FK`

`decision_payload` must validate against a versioned schema. It is not an untyped escape hatch.

Typed junction tables must link:

- candidate renderings;
- rule applications;
- corpus evidence;
- scholarly evidence;
- textual-critical evidence;
- rejected/alternative renderings.

## 33.2 `published_passage_analyses`

Published container, not the primary provenance unit.

Fields:

- `published_analysis_id uuid PK`
- `research_release_id uuid FK`
- `reference_span_id uuid FK`
- `analysis_type text`
- `analysis_schema_version text`
- `rendered_payload jsonb nullable`
- `analysis_hash text`
- `review_status text`

`rendered_payload` may be a display cache. The source of truth is structured published assertions and evidence below.

## 33.3 `published_evidence_packets`

Public-safe compiled evidence packet.

Fields:

- `published_evidence_packet_id uuid PK`
- `research_release_id uuid FK`
- `packet_schema_version text`
- `packet_hash text`

An AuthoringEvidencePacket is never reused as a PublishedEvidencePacket.

## 33.4 `published_evidence_items`

Fields:

- `published_evidence_item_id uuid PK`
- `published_evidence_packet_id uuid FK`
- `research_object_id uuid FK`
- `research_object_version text nullable`
- `evidence_content_hash text nullable`
- `evidence_class text`
- `citation_locator jsonb nullable`
- `permitted_excerpt text nullable`
- `rights_decision_snapshot_id uuid nullable FK`
- `evidence_stability_class text`
- `sort_order integer`

No private Drive URL, private source locator, restricted full text, private embedding, or unreviewed AI note may appear here.

## 33.5 `published_assertions`

Generic release-published scholarly assertion reused by passage analysis, commentary, and literature review.

Fields:

- `published_assertion_id uuid PK`
- `research_release_id uuid FK`
- `assertion_text text`
- `assertion_type text`
- `confidence_class text nullable`
- `assertion_hash text`

## 33.6 `published_assertion_evidence`

Fields:

- `published_assertion_id uuid FK`
- `published_evidence_item_id uuid FK`
- `stance text`
- `entailment_review_status text`
- `weight_metadata jsonb nullable`

## 33.7 `published_analysis_assertion_members`

Fields:

- `published_analysis_id uuid FK`
- `published_assertion_id uuid FK`
- `sort_order integer`

Passage analysis, commentary, and literature review must not maintain incompatible citation semantics.

Published public analysis is read from a pinned ResearchRelease rather than regenerated from source books on every page request.

---

# 34. Compiled serving projections

Canonical scholarly/corpus structures may be normalized and flexible.

The public query hot path may use release-scoped generated projections such as:

- `serving_words`
- `serving_morphemes`
- `serving_relations`
- `serving_semantic_memberships`

Every row must pin:

- research release;
- corpus release;
- annotation framework where relevant.

Serving projections are disposable compiler outputs and may be regenerated from canonical data.

They must not silently introduce framework-neutral phrase or clause identity.

---

# 35. Public runtime API contract

Core public runtime APIs serve published research and deterministic search.

Current-release convenience endpoints:

- `GET /api/v1/releases/current`
- `GET /api/v1/passages/{reference}`
- `GET /api/v1/passages/{reference}/translations`
- `GET /api/v1/passages/{reference}/analysis`
- `GET /api/v1/passages/{reference}/rule-applications`

Citation-stable pinned-release endpoints:

- `GET /api/v1/releases/{releaseId}/passages/{reference}`
- `GET /api/v1/releases/{releaseId}/passages/{reference}/translations`
- `GET /api/v1/releases/{releaseId}/passages/{reference}/analysis`
- `GET /api/v1/releases/{releaseId}/passages/{reference}/rule-applications`

Other core endpoints:

- `GET /api/v1/constructions/{id}/instances`
- `POST /api/v1/corpus/query/validate`
- `POST /api/v1/corpus/query/run`
- `GET /api/v1/evidence/{id}`

Optional:

- `POST /api/v1/query/interpret`

The optional interpreter returns a candidate constrained CorpusQuery AST. It never executes generated SQL.

Every canonical response must include `research_release_id`.

The same CorpusQuery JSON Schema is used by:

- Pattern Builder;
- public HTTP API;
- Product MCP;
- optional natural-language query interpreter.

Private research compilation endpoints belong to privileged internal tooling and are not part of the public core API.

Machine-readable HTTP contract:

- `contracts/v1.1/openapi.yaml`

---

# 36. Machine-contract freeze requirements

Machine-contract requirements are registered under stable IDs in `contracts/v1.1/freeze-checklist.md`.

Normative machine files for the Core profile include:

- `contracts/v1.1/vocabulary.json`
- `contracts/v1.1/json-schema/corpus-query.schema.json`
- `contracts/v1.1/json-schema/corpus-query-normalized.schema.json`
- `contracts/v1.1/query-semantics.md`
- `contracts/v1.1/json-schema/query-execution-policy.schema.json`
- `contracts/v1.1/json-schema/corpus-query-result.schema.json`
- `contracts/v1.1/json-schema/annotation-layer.schema.json`
- `contracts/v1.1/json-schema/semantic-set-version.schema.json`
- `contracts/v1.1/json-schema/construction-compilation-run.schema.json`
- `contracts/v1.1/json-schema/construction-instance.schema.json`
- `contracts/v1.1/json-schema/rule-application.schema.json`
- `contracts/v1.1/json-schema/rights-decision-snapshot.schema.json`
- `contracts/v1.1/json-schema/provider-witness-binding.schema.json`
- `contracts/v1.1/json-schema/release-manifest.schema.json`
- `contracts/v1.1/json-schema/release-event.schema.json`
- `contracts/v1.1/json-schema/release-channel-pointer.schema.json`
- `contracts/v1.1/json-schema/published-evidence-item.schema.json`
- `contracts/v1.1/json-schema/published-passage-analysis.schema.json`
- `contracts/v1.1/json-schema/translation-decision.schema.json`
- `contracts/v1.1/product-mcp-tools.json`
- `contracts/v1.1/openapi.yaml`

Research Pro extension machine contracts are tracked by `PRO-FZ-*` gates and do not block Core Database Spike 001.

---

# 37. Research Pro / Scholarly Intelligence contract

Detailed domain semantics are defined in:

- `architecture/research-pro-scholarly-intelligence.md`
- `architecture/ui-mode-cross-stage-contract.md`

Research Pro is an expanded research experience over the same ResearchRelease and the same canonical scholarly objects.

It is not:
- a separate app;
- a separate ontology;
- a second scholarly database;
- a more authoritative truth state.

The active v1.1 contract now includes six first-class domain groups:

1. DiscoveryRecord
2. ResearchIssue
3. ResearchPosition
4. LiteratureSnapshot
5. CommentaryEntry
6. ProductEntitlement

Supporting first-class contracts include:
- ScholarlyDiscoveryProvider
- ScholarlyTargetLink
- LiteratureReviewSnapshot
- SourceAccessRoute

---

# 38. DiscoveryRecord contract

## 38.1 `scholarly_discovery_providers`

Fields:

- `scholarly_discovery_provider_id uuid PK`
- `provider_key text unique`
- `display_name text`
- `capabilities jsonb`
- `provider_terms_version text nullable`
- `rights_policy_id uuid nullable FK`
- `active boolean`
- `metadata jsonb`

Provider capability names are controlled by canonical vocabulary.

## 38.2 `external_discovery_records`

External records are staging/discovery objects and must not automatically become canonical works.

Fields:

- `external_discovery_record_id uuid PK`
- `scholarly_discovery_provider_id uuid FK`
- `provider_record_id text`
- `title_raw text nullable`
- `authors_raw jsonb nullable`
- `publication_year_raw text nullable`
- `publication_type_raw text nullable`
- `doi_raw text nullable`
- `isbn_raw text nullable`
- `abstract_raw text nullable`
- `source_url text nullable`
- `language_raw text nullable`
- `retrieved_at timestamptz`
- `payload_hash text`
- `raw_payload jsonb nullable`
- `access_level text`
- `record_status text`
- `rights_decision_snapshot_id uuid nullable FK`
- `payload_storage_mode text`

`access_level` describes what the provider exposed. It does not by itself authorize persistent storage.

`raw_payload` may be persisted only when the rights decision snapshot permits that operation. Otherwise the record stores rights-safe normalized metadata plus hashes/locators allowed by provider terms.

## 38.3 `external_record_resolutions`

Fields:

- `external_record_resolution_id uuid PK`
- `external_discovery_record_id uuid FK`
- `work_id uuid FK`
- `resolution_method text`
- `resolution_confidence numeric nullable`
- `review_status text`
- `resolved_at timestamptz`
- `resolved_by uuid nullable`

AI-assisted bibliographic resolution never becomes VERIFIED without configured review.

## 38.4 Discovery access invariant

A record must preserve whether the system had metadata, abstract, citation context, open full text, licensed full text, or private full text.

An AI-extracted scholarly proposition must never imply full-text reading when its evidence basis was metadata/abstract only.

Provider terms and rights decisions are version-pinned research inputs.

---

# 39. ResearchTarget, ResearchIssue, and ResearchPosition contracts

## 39.0 `research_targets`

A ResearchTarget is a stable scholarly target registry. It prevents passages, books, lexemes, and constructions from being forced into the `research_objects` supertype merely to become research targets.

Fields:

- `research_target_id uuid PK`
- `target_type text`
- `target_key text nullable`
- `created_at timestamptz`

Typed bridge tables bind exactly one target identity, for example:

- `research_target_reference_spans(research_target_id PK/FK, reference_span_id unique FK)`
- `research_target_books(research_target_id PK/FK, book_id unique FK)`
- `research_target_lexemes(research_target_id PK/FK, lexeme_id unique FK)`
- `research_target_constructions(research_target_id PK/FK, construction_definition_id unique FK)`
- `research_target_research_issues(research_target_id PK/FK, research_issue_id unique FK)`

Additional target types require a typed bridge before production use.

## 39.1 `research_issues`

Stable identity only.

Fields:

- `research_issue_id uuid PK`
- `issue_key text unique nullable`
- `current_version_id uuid nullable`
- `created_at timestamptz`

## 39.2 `research_issue_versions`

Append-only scholarly state.

Fields:

- `research_issue_version_id uuid PK/FK -> research_objects.research_object_id`
- `research_issue_id uuid FK`
- `version_number integer`
- `title text`
- `question_text text`
- `issue_type text`
- `debate_status text`
- `classification_basis text nullable`
- `literature_snapshot_id uuid nullable FK`
- `review_status text`
- `content_hash text`
- `created_at timestamptz`
- `supersedes_version_id uuid nullable FK`

A debate-status label such as MINORITY_WITHIN_REVIEWED_SNAPSHOT is valid only with snapshot-bounded classification basis and coverage limitations.

## 39.3 `research_issue_scopes`

Fields:

- `research_issue_scope_id uuid PK`
- `research_issue_version_id uuid FK`
- `research_target_id uuid FK`
- `scope_role text`
- `review_status text`

## 39.4 `research_positions`

Stable identity within one ResearchIssue.

Fields:

- `research_position_id uuid PK`
- `research_issue_id uuid FK`
- `position_key text nullable`
- `current_version_id uuid nullable`
- `created_at timestamptz`

## 39.5 `research_position_versions`

Fields:

- `research_position_version_id uuid PK/FK -> research_objects.research_object_id`
- `research_position_id uuid FK`
- `version_number integer`
- `title text`
- `position_summary text`
- `position_status text`
- `classification_basis text nullable`
- `review_status text`
- `content_hash text`
- `created_at timestamptz`
- `supersedes_version_id uuid nullable FK`

## 39.6 `position_claim_links`

Fields:

- `position_claim_link_id uuid PK`
- `research_position_version_id uuid FK`
- `scholarly_claim_id uuid FK`
- `relationship text`
- `assertion_agent_type text`
- `review_status text`
- `notes text nullable`

## 39.7 `issue_relations`

Fields:

- `issue_relation_id uuid PK`
- `from_issue_version_id uuid FK`
- `to_issue_version_id uuid FK`
- `relation_type text`
- `assertion_agent_type text`
- `review_status text`

## 39.8 `scholarly_target_links`

Fields:

- `scholarly_target_link_id uuid PK`
- `source_object_id uuid FK -> research_objects`
- `research_target_id uuid FK`
- `relevance_type text`
- `directness text`
- `mapping_method text`
- `mapping_confidence numeric nullable`
- `source_span_id uuid nullable`
- `review_status text`
- `provenance_id uuid nullable`

An explicit biblical reference and an AI-inferred construction relevance are distinct mappings.

## 39.9 Immutable scholarly issue graph release

Public ResearchRelease components must pin exact ResearchIssueVersion and ResearchPositionVersion identities, either individually or through an immutable SCHOLARLY_ISSUE_GRAPH component snapshot with a content hash.

Pinned releases never dereference `current_version_id` from mutable authoring rows.

---

# 40. LiteratureSnapshot contract

"Current scholarship" is snapshot-bounded and search-auditable.

## 40.1 `literature_snapshots`

Fields:

- `literature_snapshot_id uuid PK/FK -> research_objects.research_object_id`
- `snapshot_type text`
- `research_target_id uuid FK`
- `as_of_date date`
- `coverage_start_date date nullable`
- `coverage_end_date date nullable`
- `review_scope text`
- `coverage_note text nullable`
- `reviewer_id uuid nullable`
- `review_status text`
- `research_release_id uuid nullable`
- `content_hash text`
- `created_at timestamptz`

## 40.2 `literature_search_runs`

Fields:

- `literature_search_run_id uuid PK`
- `literature_snapshot_id uuid FK`
- `run_date timestamptz`
- `date_range jsonb nullable`
- `languages text[]`
- `publication_types text[]`
- `citation_expansion_depth integer nullable`
- `dedup_method text`
- `dedup_version text nullable`
- `retrieved_count integer`
- `included_count integer`
- `excluded_count integer`
- `coverage_limitations text nullable`
- `status text`

## 40.2A `literature_search_provider_requests`

Per-provider execution audit.

Fields:

- `literature_search_provider_request_id uuid PK`
- `literature_search_run_id uuid FK`
- `scholarly_discovery_provider_id uuid FK`
- `provider_dataset_version text nullable`
- `provider_index_version text nullable`
- `adapter_version text`
- `provider_query_syntax_version text nullable`
- `sort_ranking_mode text nullable`
- `request_cursor text nullable`
- `requested_limit integer nullable`
- `raw_response_hash text nullable`
- `executed_at timestamptz`

## 40.3 `literature_search_queries`

Fields:

- `literature_search_query_id uuid PK`
- `literature_search_run_id uuid FK`
- `language_code text`
- `query_text text`
- `query_type text`
- `generated_by text`
- `query_order integer`
- `ai_expansion_model text nullable`
- `ai_expansion_prompt_version text nullable`

## 40.4 `literature_inclusions`

Fields:

- `literature_snapshot_id uuid FK`
- `work_id uuid FK`
- `inclusion_role text`
- `relevance_type text`
- `reason text nullable`
- `classification_basis text nullable`
- `review_status text`

Editorial labels such as SEMINAL_WORK, REPRESENTATIVE_WORK, or MINORITY_WITHIN_REVIEWED_SNAPSHOT must retain their classification basis.

## 40.5 `literature_exclusions`

Fields:

- `literature_snapshot_id uuid FK`
- `external_discovery_record_id uuid nullable`
- `work_id uuid nullable`
- `exclusion_reason text`
- `review_status text`

## 40.6 `literature_review_snapshots`

Fields:

- `literature_review_snapshot_id uuid PK/FK -> research_objects.research_object_id`
- `research_target_id uuid FK`
- `literature_snapshot_id uuid FK`
- `research_release_id uuid nullable`
- `review_structure jsonb`
- `review_summary text nullable`
- `coverage_limitations text nullable`
- `review_status text`
- `content_hash text`

## 40.7 `literature_review_assertions`

Fields:

- `literature_review_snapshot_id uuid FK`
- `published_assertion_id uuid FK`
- `section_key text nullable`
- `sort_order integer`

Literature-review prose is derivative rendering. Substantive public claims reuse the same PublishedAssertion -> PublishedEvidenceItem graph as passage analysis and commentary.

Search history is auditable. Exact external-provider result reproduction is claimed only where provider/version behavior makes that defensible.

---

# 41. CommentaryEntry contract

## 41.1 `commentary_entries`

Fields:

- `commentary_entry_id uuid PK/FK -> research_objects.research_object_id`
- `reference_span_id uuid FK`
- `research_release_id uuid FK`
- `commentary_kind text`
- `title text nullable`
- `summary text nullable`
- `review_status text`
- `content_hash text`
- `supersedes_commentary_entry_id uuid nullable`

## 41.2 `commentary_sections`

Fields:

- `commentary_section_id uuid PK`
- `commentary_entry_id uuid FK`
- `section_type text`
- `section_order integer`
- `rendered_text text`
- `source_payload jsonb nullable`
- `section_hash text`

## 41.3 `commentary_section_assertions`

Fields:

- `commentary_section_id uuid FK`
- `published_assertion_id uuid FK`
- `sort_order integer`

Rendered prose is derivative from structured assertions.

## 41.4 `commentary_section_evidence`

Optional direct section-level bibliography/navigation aid only.

Fields:

- `commentary_section_id uuid FK`
- `published_evidence_item_id uuid FK`
- `sort_order integer`

Substantive claims must use `published_assertion_evidence`; section-level evidence must not replace assertion-level provenance.

Translation Note remains a distinct artifact kind from general exegetical commentary.

---

# 42. ProductEntitlement contract

Product entitlement is not source rights.

## 42.1 `product_features`

Fields:

- `product_feature_id uuid PK`
- `feature_key text unique`
- `display_name text`
- `description text`
- `feature_group text`
- `default_experience_mode text`
- `default_decision text`
- `active boolean`

## 42.2 `entitlement_principals`

Stable registry preventing one generic UUID from pretending to FK to USER, ORGANIZATION, or PLAN tables.

Fields:

- `entitlement_principal_id uuid PK`
- `principal_type text`
- `created_at timestamptz`

Typed bridge tables bind USER, ORGANIZATION, and PLAN identities.

## 42.3 `product_entitlements`

Fields:

- `product_entitlement_id uuid PK`
- `entitlement_principal_id uuid FK`
- `product_feature_id uuid FK`
- `entitlement_decision text`
- `source_type text`
- `source_reference text nullable`
- `valid_from timestamptz nullable`
- `valid_until timestamptz nullable`
- `metadata jsonb nullable`

## 42.4 Deterministic entitlement resolution

After RightsPolicy and tenant authorization:

1. filter entitlements active at evaluation time;
2. select the highest principal specificity: USER > ORGANIZATION > PLAN;
3. at equal specificity, DENY overrides ALLOW;
4. if no active entitlement exists, use `product_features.default_decision`;
5. emit the resolved decision and reason/source references server-side.

The browser never infers entitlement from plan names.

## 42.5 Rights-before-entitlement invariant

Resolution order:

1. RightsPolicy
2. tenant/user authorization
3. ProductEntitlement
4. experience-mode projection

ProductEntitlement can never override content rights.

## 42.6 Minimum evidence transparency invariant

Research entitlement is never required merely to verify a substantive published conclusion already shown in Study mode.

---

# 43. SourceAccessRoute contract

## 43.1 `source_access_routes`

Fields:

- `source_access_route_id uuid PK`
- `work_id uuid FK`
- `academic_edition_id uuid nullable FK -> editions`
- `route_type text`
- `url text nullable`
- `availability_scope text`
- `rights_policy_id uuid nullable`
- `active boolean`
- `verified_at timestamptz nullable`

Route type is controlled by canonical vocabulary.

PRIVATE_LIBRARY_COPY must never be exposed to ordinary public/customer clients.

Bibliographic relevance and full-text access are independent.

---

# 44. Study / Research UI cross-stage contract

The authoritative UI-mode contract is:

- `architecture/ui-mode-cross-stage-contract.md`

The modes are:

- STUDY
- RESEARCH

Both use:

- the same active ResearchRelease;
- the same canonical entity IDs;
- the same passage/reference identity;
- the same published commentary identity;
- the same translation decisions;
- the same rights resolver.

Research mode exposes deeper projections.

It does not use a different scholarly truth state.

## 44.1 Stable domain interfaces

Reserve equivalent runtime-validated contracts for:

- `PassageExperienceCoreV1`
- `StudyPassageProjectionV1`
- `ResearchPassageProjectionV1`
- `ExperienceCapabilitiesV1`
- `ResearchIssueV1`
- `ResearchPositionV1`
- `LiteratureSnapshotV1`
- `CommentaryEntryV1`
- `DiscoveryRecordV1`
- `ProductEntitlementV1`

## 44.2 API additions

### GET `/api/v1/experience/capabilities`

Returns server-resolved experience/feature capability decisions.

### GET `/api/v1/passages/{reference}/experience`

Query:
- `mode=STUDY|RESEARCH`
- optional `researchReleaseId`

Returns a release-pinned projection.

An implementation may internally compose several domain endpoints rather than physically materializing one giant response.

### GET `/api/v1/research-issues`

Filters may include:
- targetObjectId
- referenceSpanId
- issueType
- debateStatus
- researchReleaseId

### GET `/api/v1/research-issues/{researchIssueId}`

Returns issue identity, scopes, snapshot metadata and position summaries.

### GET `/api/v1/research-issues/{researchIssueId}/positions`

Returns position objects and reviewed claim-link summaries.

### GET `/api/v1/literature/snapshots/{literatureSnapshotId}`

Returns reviewed snapshot methodology and included bibliography according to entitlement/rights.

### GET `/api/v1/passages/{reference}/commentary`

Returns the release-pinned CommentaryEntry and Study-safe summary.

Research mode may request section/evidence expansion.

### GET `/api/v1/scholarly-discovery/recent`

Research feature only.

Returns live discovery records explicitly labelled DISCOVERED_SINCE_RELEASE.

It must not merge them into release-pinned synthesis.

## 44.3 Availability/error distinctions

The API/UI must distinguish:

- FEATURE_NOT_ENTITLED
- SOURCE_RIGHTS_RESTRICTED
- NOT_IN_RESEARCH_RELEASE
- NOT_YET_REVIEWED
- DISCOVERY_PROVIDER_UNAVAILABLE
- COVERAGE_NOT_AVAILABLE
- DATA_TEMPORARILY_UNAVAILABLE

Do not collapse these into one "Pro required" state.

---

# 45. Research Pro phase ownership

## Phase 1

Reserve:
- experience mode vocabulary;
- ProductEntitlement schema/interface;
- shared PassageExperienceCore;
- capability resolver;
- same-release mode switching.

## Phase 2

Study receives:
- key scholarship;
- published commentary summary;
- translation note;
- minimum evidence transparency.

Research may use placeholders for deep scholarly modules.

## Phase 3

Research receives:
- advanced corpus query;
- construction browser;
- semantic-set detail;
- full linguistic/corpus evidence.

## Phase 4

Research Pro scholarly-intelligence compilation owns:
- discovery providers;
- DiscoveryRecords;
- bibliographic resolution;
- scholarly target links;
- ResearchIssues;
- ResearchPositions;
- LiteratureSnapshots;
- access routes.

## Phase 5

Publication/serving owns:
- LiteratureReviewSnapshots;
- CommentaryEntries;
- full Research projections;
- scholarly dependency/debate graphs;
- live discovery surface;
- ProductEntitlement enforcement;
- full Study/Research QA.

---

# 46. Research Pro extension freeze governance

Research Pro remains an active product domain over the same ResearchRelease, not a second product.

Its machine-contract maturity is tracked independently from the Core Database Spike gate.

Canonical Research Pro requirements use `PRO-FZ-*` IDs in:

- `contracts/v1.1/freeze-checklist.md`

Do not reintroduce duplicate numeric freeze conditions in this document.

---

# 47. Public runtime AI / BYOK contract

Public runtime AI is BYOK-only.

Gemini is the first supported provider.

## 47.1 No shared model credential

The public product must not contain or retrieve a platform-owned Gemini/OpenAI/Anthropic/other model credential from source code, environment variables, Vercel secrets, Supabase secrets, GitHub Actions secrets, database rows, fixtures, or fallback configuration.

There is deliberately no database table for raw provider credentials.

## 47.2 User BYOK credential

A user-supplied credential is ephemeral runtime input.

The implementation may contain generic code that accepts and forwards a user-supplied credential. It must never contain an actual credential value.

The credential is opaque and provider validation determines validity.

Default persistence mode:

- VOLATILE_MEMORY_ONLY

Forbidden persistence:

- database;
- object storage;
- cookies;
- localStorage;
- IndexedDB;
- analytics;
- telemetry;
- logs;
- audit records;
- evidence packets.

## 47.3 Ephemeral relay

The preferred public-web path is:

~~~text
browser volatile memory
 -> AI-specific HTTPS relay
 -> fixed provider adapter
 -> Gemini
~~~

The relay must not persist, log, enqueue, cache, echo, or return the credential.

The relay must have no shared model-provider fallback secret.

## 47.4 No-BYOK behaviour

Without BYOK, the following remain functional:

- Passage Study;
- CorpusQuery;
- Corpus Lab;
- semantic sets;
- constructions;
- rule applications;
- published commentary;
- evidence and citations;
- ResearchRelease browsing.

Only optional runtime AI features are unavailable.

## 47.5 Canonical vocabulary

Runtime AI auth mode:

- BYOK_ONLY

Credential states:

- BYOK_AVAILABLE
- BYOK_MISSING
- BYOK_INVALID
- PROVIDER_UNAVAILABLE
- FEATURE_DISABLED

Credential persistence mode:

- VOLATILE_MEMORY_ONLY

## 47.6 Freeze gate

Before any public AI feature ships:

1. secret scanning confirms no shared model-provider credential in source/config/build artifacts;
2. browser storage inspection confirms no BYOK credential persistence;
3. valid and invalid BYOK requests produce no raw credential in logs/telemetry;
4. provider errors do not echo the credential;
5. no platform fallback key is reachable;
6. refresh/sign-out/Forget key clears volatile state;
7. all non-AI scholarly features work without BYOK.
