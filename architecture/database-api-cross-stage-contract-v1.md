# Database, API, and Cross-Stage Contract v1

Status: **LOCKED ARCHITECTURE CONTRACT**

This document freezes the v1 data boundaries shared by the five Site Build stages. Future implementation prompts may add indexes, implementation-only columns, derived views, or new feature tables, but must not silently change the meaning of the identifiers, entities, relationships, API contracts, evidence types, or stage ownership defined here.

Any breaking change requires:
1. an explicit architecture decision record;
2. a database migration plan;
3. API versioning or backwards compatibility;
4. regression tests for all affected earlier stages.

This contract must be read together with:

- `architecture/academic-evidence-policy.md`
- `architecture/academic-storage-and-rag.md`
- `architecture/site-build-staging-plan.md`
- `docs/academic-source-taxonomy.md`

---

# 1. Non-negotiable design rules

## 1.1 PostgreSQL is the canonical structured store

Supabase/PostgreSQL is the intended production relational store.

GitHub is not a corpus database.
Google Drive is not a production query database.
Vercel filesystem is not persistent research storage.
Vector embeddings are not the canonical representation of scholarly content.

## 1.2 Canonical application IDs are internal

The application must never use an OSHB ID, MACULA ID, BHSA node ID, FHL version identifier, Drive file ID, or page label as its permanent primary key.

External identifiers are mappings.

Use application-owned UUIDs for primary entities.

Recommended implementation:
- UUIDv7 where available;
- UUIDv4 is acceptable if the chosen stack does not support UUIDv7 cleanly.

Human-readable references are never primary keys.

## 1.3 Source facts, user claims, and AI output are separate

Do not store:
- an AI inference in a corpus annotation row;
- a user rule as a scholarly claim;
- a translation witness as evidence of translator intention;
- a vector-search result as a verified citation.

## 1.4 Immutable historical versions

The following are append/version oriented:

- corpus releases;
- user translation versions;
- semantic-set versions;
- rule versions;
- prompt versions;
- analysis runs;
- source editions;
- extraction revisions.

Historical research must remain reproducible.

## 1.5 No destructive cascades across evidence layers

Deleting or replacing a source must not silently destroy historical analysis records.

Prefer:
- `status`
- `archived_at`
- immutable versions
- explicit supersession links

over destructive cascade deletion.

## 1.6 Rights filtering happens before retrieval output

Restricted evidence must be filtered before it enters an evidence packet.

The model must not retrieve restricted full text and then be asked to hide it afterward.

---

# 2. Common infrastructure conventions

All principal mutable tables should have where appropriate:

- `id uuid primary key`
- `created_at timestamptz`
- `updated_at timestamptz`
- `created_by uuid nullable`
- `status text`
- `row_version integer`

User-editable APIs should use optimistic concurrency.

Recommended contract:
- client supplies `expectedRowVersion`
- update succeeds only when current version matches
- conflict returns `409 VERSION_CONFLICT`

Use UTC in the database.

---

# 3. Global evidence vocabulary

The database and API must support these evidence classes without renaming their meaning:

- `PRIMARY_TEXT`
- `CORPUS_ANNOTATION`
- `CORPUS_OBSERVATION`
- `SCHOLARLY_CLAIM`
- `TRANSLATION_WITNESS`
- `DOCUMENTED_TRANSLATOR_NOTE`
- `USER_HYPOTHESIS`
- `SYSTEM_INFERENCE`
- `AI_SYNTHESIS`
- `UNKNOWN`

Do not use one generic `sourceType` field to collapse unrelated source semantics.

---

# 4. Stage ownership model

## Stage 1 owns

- reference systems;
- application passage identity;
- project shell;
- source registry;
- rights profiles;
- provenance primitives;
- evidence labels;
- API response conventions.

## Stage 2 owns

- translation providers;
- translation versions;
- translation retrieval/cache metadata;
- translation units;
- Hebrew-Chinese alignments;
- user-proposed translation versions;
- translation notes.

## Stage 3 owns

- corpus sources and releases;
- canonical Hebrew tokens and morphemes;
- corpus token mappings;
- phrases and clauses;
- syntax graph;
- structured corpus annotations;
- semantic sets;
- query DSL persistence;
- query runs and matches.

## Stage 4 owns

- bibliographic works and editions;
- source assets;
- ingestion jobs;
- document hierarchy;
- source spans;
- scholarly claims;
- concept graph;
- lexicon structures;
- commentary structures;
- textual-critical structures;
- retrieval units;
- embeddings.

## Stage 5 owns

- rule engine runtime;
- analysis plans;
- evidence packets;
- analysis runs;
- analysis conclusions;
- prompt versions;
- counterevidence records.

A later stage may reference earlier-stage entities, but must not redefine them.

---

# 5. Stage 1 database contract: reference, identity, provenance, projects

## 5.1 `reference_systems`

Purpose:
Defines a versification/reference namespace.

Fields:

- `reference_system_id uuid PK`
- `code text unique`
- `name text`
- `description text nullable`
- `version text nullable`
- `is_default boolean`

Examples of codes:
- `MT`
- `OSIS`
- `FHL`
- another explicit versification system

## 5.2 `biblical_books`

Purpose:
Canonical application book identity independent of provider naming.

Fields:

- `book_id uuid PK`
- `osis_code text unique`
- `canonical_order integer`
- `hebrew_name text nullable`
- `english_name text`
- `traditional_chinese_name text nullable`

Provider-specific book codes belong in mapping tables, not here.

## 5.3 `canonical_passages`

Purpose:
Internal passage unit used to link research objects.

Fields:

- `passage_id uuid PK`
- `book_id uuid FK biblical_books`
- `sequence_start integer`
- `sequence_end integer`
- `passage_kind text`
- `base_reference_label text nullable`

Important:
`base_reference_label` is display metadata, not identity.

This table must support reference systems in which one displayed verse maps to multiple canonical units or multiple displayed verses map to one canonical unit.

## 5.4 `passage_references`

Purpose:
Maps human/provider references to canonical passages.

Fields:

- `passage_reference_id uuid PK`
- `reference_system_id uuid FK`
- `book_id uuid FK`
- `chapter_number integer nullable`
- `verse_start text nullable`
- `verse_end text nullable`
- `reference_label text`
- `sort_key integer`

Unique constraint:
`(reference_system_id, reference_label)`

## 5.5 `passage_reference_members`

Purpose:
Many-to-many bridge for split/merged versification.

Fields:

- `passage_reference_id uuid FK`
- `passage_id uuid FK`
- `member_order integer`

Unique:
`(passage_reference_id, passage_id)`

## 5.6 `source_registry`

Purpose:
Global registry of providers/datasets/publications that can contribute evidence.

Fields:

- `source_registry_id uuid PK`
- `source_key text unique`
- `display_name text`
- `source_family text`
- `provider_name text nullable`
- `homepage_url text nullable`
- `default_evidence_class text nullable`
- `active boolean`

Examples:
- OSHB
- MACULA
- BHSA
- FHL
- Google Drive academic library
- user research

This is a registry, not a substitute for `works`, `editions`, or `corpus_releases`.

## 5.7 `rights_profiles`

Fields:

- `rights_profile_id uuid PK`
- `rights_status text`
- `license_name text nullable`
- `copyright_holder text nullable`
- `may_store_original boolean`
- `may_extract_text boolean`
- `may_store_extracted_text boolean`
- `may_embed boolean`
- `may_display_fulltext boolean`
- `may_display_excerpt boolean`
- `may_export boolean`
- `may_redistribute boolean`
- `may_use_commercially boolean`
- `notes text nullable`
- `verified_at timestamptz nullable`
- `verification_source text nullable`

Default for unknown rights:
restrictive.

## 5.8 `research_projects`

Fields:

- `project_id uuid PK`
- `owner_user_id uuid`
- `title text`
- `description text nullable`
- `visibility text`
- `status text`

## 5.9 `project_passages`

Fields:

- `project_id uuid FK`
- `passage_id uuid FK`
- `position integer`
- `note text nullable`

## 5.10 `provenance_records`

Purpose:
Reusable provenance locator for derived records.

Fields:

- `provenance_id uuid PK`
- `source_registry_id uuid FK nullable`
- `source_object_type text`
- `source_object_id text`
- `source_version text nullable`
- `retrieved_at timestamptz nullable`
- `content_hash text nullable`
- `derivation_method text nullable`
- `metadata jsonb`

No claim is academically auditable merely because it has a URL. Provenance should identify version and source object where possible.

---

# 6. Stage 2 database contract: Chinese translations and alignment

## 6.1 `translation_providers`

Fields:

- `translation_provider_id uuid PK`
- `provider_key text unique`
- `name text`
- `base_url text nullable`
- `provider_type text`
- `active boolean`

Example:
FHL.

## 6.2 `translation_versions`

Fields:

- `translation_version_id uuid PK`
- `translation_provider_id uuid FK`
- `provider_version_code text`
- `display_name text`
- `language_code text`
- `script_code text nullable`
- `publication_metadata jsonb nullable`
- `rights_profile_id uuid FK`
- `version_metadata jsonb`
- `active boolean`

Unique:
`(translation_provider_id, provider_version_code)`

Do not hard-code the number of versions.

## 6.3 `translation_units`

Purpose:
A retrieved/stored unit of translation text.

Fields:

- `translation_unit_id uuid PK`
- `translation_version_id uuid FK`
- `passage_reference_id uuid FK`
- `text_original text`
- `text_normalized text nullable`
- `content_hash text`
- `retrieval_mode text`
- `retrieved_at timestamptz`
- `cache_expires_at timestamptz nullable`
- `provenance_id uuid FK`

Important:
Permanent storage is allowed only when the version rights profile permits it.

For provider-only content, implementation may use an ephemeral/cache layer rather than persistent rows.

## 6.4 `translation_notes`

Fields:

- `translation_note_id uuid PK`
- `translation_version_id uuid FK`
- `passage_reference_id uuid FK`
- `note_type text`
- `note_text text`
- `is_documented_translator_note boolean`
- `provenance_id uuid FK`

Only direct publisher/translator/provider documentation may set documented translator note = true.

## 6.5 `translation_alignments`

Purpose:
Many-to-many source-target span alignment.

Fields:

- `alignment_id uuid PK`
- `passage_id uuid FK`
- `translation_version_id uuid FK`
- `source_span_type text`
- `source_start_id uuid nullable`
- `source_end_id uuid nullable`
- `target_unit_id uuid FK translation_units`
- `target_start_offset integer nullable`
- `target_end_offset integer nullable`
- `alignment_relation text`
- `method text`
- `confidence numeric nullable`
- `review_status text`
- `reviewed_by uuid nullable`
- `provenance_id uuid nullable`

This contract must support:
- one Hebrew token -> many Chinese characters/words;
- many Hebrew tokens -> one Chinese phrase;
- omission;
- addition;
- discontinuous relationships through multiple alignment rows.

## 6.6 `user_translation_proposals`

Represents the stable user-owned translation object.

Fields:

- `user_translation_id uuid PK`
- `project_id uuid FK`
- `passage_id uuid FK`
- `owner_user_id uuid`
- `current_version_id uuid nullable`
- `status text`

## 6.7 `user_translation_versions`

Append-only.

Fields:

- `user_translation_version_id uuid PK`
- `user_translation_id uuid FK`
- `version_number integer`
- `translation_text text`
- `translation_notes text nullable`
- `created_at timestamptz`
- `supersedes_version_id uuid nullable`

Unique:
`(user_translation_id, version_number)`

---

# 7. Stage 3 database contract: Hebrew corpus and deterministic search

## 7.1 `corpus_sources`

Fields:

- `corpus_source_id uuid PK`
- `source_registry_id uuid FK`
- `name text`
- `corpus_type text`
- `rights_profile_id uuid FK`

Examples:
OSHB, MACULA, BHSA.

## 7.2 `corpus_releases`

Immutable release identity.

Fields:

- `corpus_release_id uuid PK`
- `corpus_source_id uuid FK`
- `release_name text`
- `release_version text nullable`
- `release_date date nullable`
- `commit_sha text nullable`
- `source_checksum text nullable`
- `importer_version text`
- `imported_at timestamptz`
- `is_active boolean`

Never overwrite one release with another.

## 7.3 `canonical_tokens`

Application-owned orthographic token identity.

Fields:

- `token_id uuid PK`
- `passage_id uuid FK`
- `token_order integer`
- `surface_original text`
- `surface_nfc text`
- `surface_no_accents text`
- `surface_no_vowels text`
- `consonantal text`
- `ketiv_qere_status text`
- `display_reading text nullable`

Unique:
`(passage_id, token_order)`

Original form is preserved separately from search normalization.

## 7.4 `morphemes`

Fields:

- `morpheme_id uuid PK`
- `token_id uuid FK`
- `morpheme_order integer`
- `surface_original text`
- `surface_normalized text`
- `lemma_normalized text nullable`
- `morpheme_type text`

Unique:
`(token_id, morpheme_order)`

## 7.5 `corpus_object_mappings`

Purpose:
Maps application objects to provider/release identifiers.

Fields:

- `mapping_id uuid PK`
- `corpus_release_id uuid FK`
- `canonical_object_type text`
- `canonical_object_id uuid`
- `external_object_type text`
- `external_object_id text`
- `mapping_status text`
- `mapping_confidence numeric nullable`

Unique:
`(corpus_release_id, external_object_type, external_object_id)`

## 7.6 `phrases`

Fields:

- `phrase_id uuid PK`
- `passage_id uuid FK`
- `start_token_id uuid FK`
- `end_token_id uuid FK`
- `phrase_order integer`

Phrase identity is application-owned. Provider analyses belong in annotations/mappings.

## 7.7 `clauses`

Fields:

- `clause_id uuid PK`
- `passage_id uuid FK`
- `start_token_id uuid FK`
- `end_token_id uuid FK`
- `clause_order integer`

## 7.8 `syntax_nodes`

Fields:

- `syntax_node_id uuid PK`
- `corpus_release_id uuid FK`
- `node_kind text`
- `canonical_object_type text nullable`
- `canonical_object_id uuid nullable`
- `properties jsonb`

## 7.9 `syntax_edges`

Fields:

- `syntax_edge_id uuid PK`
- `corpus_release_id uuid FK`
- `parent_node_id uuid FK`
- `child_node_id uuid FK`
- `relation_type text`
- `properties jsonb`

Do not merge conflicting provider syntax into one edge without provenance.

## 7.10 `corpus_annotations`

Generic structured annotation fact with explicit provider.

Fields:

- `corpus_annotation_id uuid PK`
- `corpus_release_id uuid FK`
- `target_type text`
- `target_id uuid`
- `feature_key text`
- `feature_value_text text nullable`
- `feature_value_json jsonb nullable`
- `provenance_id uuid FK`

Examples:
- POS
- person
- gender
- number
- stem
- state
- phrase function
- clause type

Source disagreement is represented by multiple rows, not overwritten.

## 7.11 `semantic_sets`

Fields:

- `semantic_set_id uuid PK`
- `owner_user_id uuid nullable`
- `name text`
- `description text nullable`
- `visibility text`

## 7.12 `semantic_set_versions`

Append-only.

Fields:

- `semantic_set_version_id uuid PK`
- `semantic_set_id uuid FK`
- `version_number integer`
- `definition_json jsonb`
- `created_at timestamptz`

## 7.13 `semantic_set_members`

Fields:

- `semantic_set_version_id uuid FK`
- `member_type text`
- `member_key text`
- `inclusion_type text`

Research queries must pin a version.

## 7.14 `corpus_queries`

Represents a saved query definition.

Fields:

- `corpus_query_id uuid PK`
- `owner_user_id uuid nullable`
- `name text nullable`
- `dsl_version text`
- `query_json jsonb`
- `query_hash text`
- `created_at timestamptz`

## 7.15 `corpus_query_runs`

Immutable run.

Fields:

- `query_run_id uuid PK`
- `corpus_query_id uuid FK nullable`
- `dsl_version text`
- `query_json jsonb`
- `corpus_release_ids uuid[]`
- `semantic_set_version_ids uuid[]`
- `started_at timestamptz`
- `completed_at timestamptz nullable`
- `status text`
- `result_summary jsonb`
- `engine_version text`

## 7.16 `corpus_matches`

Fields:

- `corpus_match_id uuid PK`
- `query_run_id uuid FK`
- `passage_id uuid FK`
- `clause_id uuid nullable`
- `match_kind text`
- `matched_node_bindings jsonb`
- `relation_evidence jsonb`
- `match_order integer`

Do not infer count semantics from row count alone.

`result_summary` must separately report:
- token_match_count
- construction_count
- clause_count
- verse/reference count
- passage_count

---

# 8. Corpus Query DSL v1 contract

The DSL is a stable cross-stage interface.

Example shape:

```json
{
  "version": "1.0",
  "scope": {
    "corpusReleaseIds": [],
    "referenceRange": null
  },
  "nodes": [
    {
      "id": "A",
      "type": "word",
      "constraints": {
        "lemma": "ראה",
        "pos": "verb"
      }
    }
  ],
  "relations": [],
  "resultMode": "construction"
}
```

Allowed node types in v1:

- `word`
- `morpheme`
- `phrase`
- `clause`

Core relation names in v1:

- `immediately_precedes`
- `precedes`
- `follows`
- `within_n_tokens`
- `same_phrase`
- `same_clause`
- `same_sentence`
- `attached_to`
- `governs`
- `dependent_of`

A relation may contain explicit parameters such as:
- `maxDistance`
- `minDistance`
- `direction`

Never redefine `precedes` to mean immediately-precedes.

Unknown relation type returns validation error, not best-effort interpretation.

---

# 9. Stage 4 database contract: academic knowledge and RAG

## 9.1 `authors`

Fields:

- `author_id uuid PK`
- `display_name text`
- `authority_key text nullable`
- `metadata jsonb`

## 9.2 `works`

Fields:

- `work_id uuid PK`
- `canonical_title text`
- `work_type text`
- `scholarly_domain text`
- `methodological_orientation text nullable`
- `original_publication_year integer nullable`

## 9.3 `work_authors`

Fields:
- `work_id uuid FK`
- `author_id uuid FK`
- `role text`
- `author_order integer`

## 9.4 `editions`

Fields:

- `edition_id uuid PK`
- `work_id uuid FK`
- `edition_statement text nullable`
- `publication_year integer nullable`
- `publisher text nullable`
- `isbn text nullable`
- `language_code text`
- `edition_status text`
- `newer_edition_known boolean`
- `bibliographic_notes text nullable`

## 9.5 `source_assets`

Concrete file/source.

Fields:

- `source_asset_id uuid PK`
- `edition_id uuid FK nullable`
- `source_registry_id uuid FK`
- `external_locator_private text nullable`
- `mime_type text nullable`
- `byte_size bigint nullable`
- `sha256 text nullable`
- `content_hash text nullable`
- `extraction_status text`
- `extraction_quality text`
- `rights_profile_id uuid FK`
- `metadata jsonb`

Do not expose private Drive locators through public APIs.

## 9.6 `ingestion_jobs`

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

Required states include:

- PENDING
- CLASSIFYING
- EXTRACTING
- STRUCTURING
- ENRICHING
- VALIDATING
- READY_TO_COMMIT
- COMPLETED
- FAILED

Partial extraction must not be marked COMPLETED.

## 9.7 `document_nodes`

Hierarchical document structure.

Fields:

- `document_node_id uuid PK`
- `edition_id uuid FK`
- `parent_node_id uuid nullable`
- `node_type text`
- `title text nullable`
- `section_label text nullable`
- `sort_order integer`
- `printed_page_start text nullable`
- `printed_page_end text nullable`
- `pdf_page_start integer nullable`
- `pdf_page_end integer nullable`

Node types may include:
- chapter
- section
- subsection
- paragraph
- footnote
- appendix

## 9.8 `source_spans`

Fields:

- `source_span_id uuid PK`
- `source_asset_id uuid FK`
- `document_node_id uuid FK nullable`
- `source_text text`
- `normalized_text text nullable`
- `printed_page_label text nullable`
- `pdf_page_index integer nullable`
- `bbox jsonb nullable`
- `text_start_offset integer nullable`
- `text_end_offset integer nullable`
- `extraction_method text`
- `extraction_confidence numeric nullable`
- `review_status text`
- `content_hash text`

AI summary must not replace `source_text`.

## 9.9 `scholarly_claims`

Fields:

- `scholarly_claim_id uuid PK`
- `edition_id uuid FK`
- `source_span_id uuid FK`
- `claim_type text`
- `claim_text_normalized text`
- `author_terminology text nullable`
- `certainty_marker text nullable`
- `extraction_method text`
- `review_status text`
- `provenance_id uuid FK`

Claim types may include:
- definition
- rule
- qualification
- exception
- interpretation
- methodological claim

## 9.10 `claim_relations`

Fields:

- `claim_relation_id uuid PK`
- `from_claim_id uuid FK`
- `to_claim_id uuid FK`
- `relation_type text`

Examples:
- QUALIFIES
- EXCEPTS
- SUPPORTS
- CONTRADICTS
- RESTATES
- DEPENDS_ON

This table is critical for preventing rule-without-exception retrieval.

## 9.11 `claim_biblical_examples`

Fields:

- `scholarly_claim_id uuid FK`
- `passage_reference_id uuid nullable`
- `cited_reference_text text`
- `example_role text`
- `source_span_id uuid FK`

## 9.12 `concepts`

Fields:

- `concept_id uuid PK`
- `canonical_label text`
- `concept_domain text`
- `description text nullable`

Canonical concepts are application navigation aids, not replacements for author-native terminology.

## 9.13 `concept_aliases`

Fields:

- `concept_alias_id uuid PK`
- `concept_id uuid FK`
- `alias_text text`
- `edition_id uuid nullable`
- `author_specific boolean`

## 9.14 `concept_relations`

Fields:

- `concept_relation_id uuid PK`
- `from_concept_id uuid FK`
- `to_concept_id uuid FK`
- `relation_type text`
- `provenance_id uuid nullable`

## 9.15 `source_concept_links`

Fields:

- `source_concept_link_id uuid PK`
- `concept_id uuid FK`
- `source_span_id uuid FK nullable`
- `scholarly_claim_id uuid FK nullable`
- `link_type text`
- `confidence numeric nullable`
- `review_status text`

## 9.16 `lexicon_entries`

Fields:

- `lexicon_entry_id uuid PK`
- `edition_id uuid FK`
- `lemma_key text`
- `headword_display text`
- `source_span_id uuid FK`

## 9.17 `lexicon_senses`

Fields:

- `lexicon_sense_id uuid PK`
- `lexicon_entry_id uuid FK`
- `sense_label text nullable`
- `sense_text text`
- `source_span_id uuid FK`
- `sort_order integer`

Do not merge senses from different lexica into a single asserted sense.

## 9.18 `commentary_units`

Fields:

- `commentary_unit_id uuid PK`
- `edition_id uuid FK`
- `source_span_id uuid FK`
- `passage_start_id uuid FK`
- `passage_end_id uuid FK`
- `commentary_type text`
- `summary_generated text nullable`

Passage-first filter precedes semantic retrieval when passage is known.

## 9.19 `textual_witnesses`

Fields:

- `textual_witness_id uuid PK`
- `witness_key text unique`
- `display_name text`
- `witness_type text`
- `metadata jsonb`

## 9.20 `apparatus_entries`

Fields:

- `apparatus_entry_id uuid PK`
- `edition_id uuid FK`
- `passage_id uuid FK`
- `source_span_id uuid FK nullable`
- `lemma_text text nullable`
- `apparatus_text text nullable`
- `review_status text`

## 9.21 `variant_readings`

Fields:

- `variant_reading_id uuid PK`
- `apparatus_entry_id uuid FK`
- `reading_text text`
- `reading_type text`
- `notes text nullable`

## 9.22 `variant_witnesses`

Fields:

- `variant_reading_id uuid FK`
- `textual_witness_id uuid FK`
- `support_type text`
- `metadata jsonb`

## 9.23 `retrieval_units`

Purpose:
Searchable academic retrieval object, not canonical source.

Fields:

- `retrieval_unit_id uuid PK`
- `namespace text`
- `edition_id uuid FK`
- `source_span_start_id uuid FK`
- `source_span_end_id uuid FK nullable`
- `retrieval_text text`
- `unit_type text`
- `content_hash text`
- `rights_profile_id uuid FK`
- `active boolean`

Retrieval unit boundaries are source-type-aware:
- grammar: rule + qualification + examples
- lexicon: entry/sense
- commentary: verse/pericope note
- textual criticism: apparatus/discussion unit

## 9.24 `embeddings`

Fields:

- `embedding_id uuid PK`
- `retrieval_unit_id uuid FK`
- `embedding_model text`
- `embedding_version text`
- `dimensions integer`
- `embedding vector`
- `source_content_hash text`
- `created_at timestamptz`
- `stale_at timestamptz nullable`

Unique:
`(retrieval_unit_id, embedding_model, embedding_version)`

Never mix vector spaces in one similarity operation.

---

# 10. Stage 5 database contract: rules, evidence packets, analysis

## 10.1 `user_rules`

Fields:

- `user_rule_id uuid PK`
- `owner_user_id uuid`
- `name text`
- `rule_kind text`
- `status text`
- `current_version_id uuid nullable`

## 10.2 `user_rule_versions`

Append-only.

Fields:

- `user_rule_version_id uuid PK`
- `user_rule_id uuid FK`
- `version_number integer`
- `trigger_definition jsonb`
- `rule_statement text`
- `translation_implications jsonb nullable`
- `exclusions jsonb nullable`
- `review_status text`
- `created_at timestamptz`
- `supersedes_version_id uuid nullable`

## 10.3 `rule_evidence_links`

Fields:

- `rule_evidence_link_id uuid PK`
- `user_rule_version_id uuid FK`
- `evidence_type text`
- `evidence_object_id uuid`
- `relationship text`
- `notes text nullable`

Relationships:
- SUPPORTS
- OPPOSES
- QUALIFIES
- EXCEPTION
- ORIGIN

## 10.4 `prompt_templates`

Fields:

- `prompt_template_id uuid PK`
- `prompt_key text unique`
- `purpose text`

## 10.5 `prompt_versions`

Append-only.

Fields:

- `prompt_version_id uuid PK`
- `prompt_template_id uuid FK`
- `version_number integer`
- `template_text text`
- `model_constraints jsonb nullable`
- `created_at timestamptz`
- `active boolean`

## 10.6 `analysis_runs`

Immutable research execution record.

Fields:

- `analysis_run_id uuid PK`
- `project_id uuid FK nullable`
- `passage_id uuid FK nullable`
- `analysis_type text`
- `status text`
- `question_text text nullable`
- `user_translation_version_id uuid nullable`
- `analysis_plan_json jsonb`
- `model_identifier text nullable`
- `prompt_version_id uuid nullable`
- `started_at timestamptz`
- `completed_at timestamptz nullable`
- `failure_code text nullable`

## 10.7 `analysis_dependencies`

Pins reproducibility inputs.

Fields:

- `analysis_dependency_id uuid PK`
- `analysis_run_id uuid FK`
- `dependency_type text`
- `dependency_id uuid nullable`
- `dependency_version text nullable`
- `metadata jsonb nullable`

Examples:
- CORPUS_RELEASE
- QUERY_RUN
- SEMANTIC_SET_VERSION
- USER_RULE_VERSION
- USER_TRANSLATION_VERSION
- SOURCE_EDITION
- PROMPT_VERSION

## 10.8 `analysis_evidence_items`

The persisted evidence packet.

Fields:

- `analysis_evidence_item_id uuid PK`
- `analysis_run_id uuid FK`
- `evidence_class text`
- `evidence_object_type text`
- `evidence_object_id uuid nullable`
- `citation_locator jsonb nullable`
- `display_excerpt text nullable`
- `stance text nullable`
- `rights_profile_id uuid nullable`
- `sort_order integer`

Stance may include:
- SUPPORTING
- OPPOSING
- QUALIFYING
- CONTEXT
- NEUTRAL

## 10.9 `analysis_outputs`

Fields:

- `analysis_output_id uuid PK`
- `analysis_run_id uuid FK`
- `output_type text`
- `content_json jsonb`
- `created_at timestamptz`

Output types may include:
- EVIDENCE_MATRIX
- TRANSLATION_COMPARISON
- SYNTHESIS
- COUNTERARGUMENTS
- UNCERTAINTIES
- TRANSLATION_IMPLICATIONS

Do not store model prose as if it were a scholarly claim.

---

# 11. Stable API conventions

Base path:

`/api/v1`

All v1 build stages must use the same response envelope.

Success:

```json
{
  "data": {},
  "meta": {
    "apiVersion": "1",
    "requestId": "uuid"
  }
}
```

Error:

```json
{
  "error": {
    "code": "MACHINE_READABLE_CODE",
    "message": "Human readable message",
    "retryable": false,
    "details": {}
  },
  "meta": {
    "apiVersion": "1",
    "requestId": "uuid"
  }
}
```

Do not return 200 with an embedded error object.

Core status semantics:

- 200 successful read/run result
- 201 created
- 202 async job accepted
- 400 malformed request
- 401 unauthenticated
- 403 not permitted / rights restricted
- 404 not found
- 409 version/state conflict
- 422 semantically invalid query
- 429 rate limited/provider limited
- 502 upstream provider failure
- 503 temporarily unavailable

---

# 12. Stage 1 API contracts

## GET `/api/v1/passages/resolve`

Query:
- `ref`
- `referenceSystem` optional

Returns `PassageResolutionV1`:

```json
{
  "passageId": "uuid",
  "canonicalReference": "1Sam 16:7",
  "inputReference": "1 Sam 16:7",
  "referenceSystem": "MT",
  "memberPassageIds": ["uuid"]
}
```

## GET `/api/v1/passages/{passageId}`

Returns `PassageShellV1`.

Must remain lightweight. It does not need to include all translations, corpus analysis, and academic evidence in one payload.

## GET `/api/v1/projects/{projectId}`

Returns project metadata and passage references, not full research history by default.

---

# 13. Stage 2 API contracts

## GET `/api/v1/translations/versions`

Optional query:
- language
- provider
- passageId
- includeUnavailable

Returns dynamic version metadata including rights/display status.

## GET `/api/v1/passages/{passageId}/translations`

Query:
- `versionIds[]`

Returns `TranslationWitnessBundleV1`.

Each witness independently reports:
- AVAILABLE
- UNAVAILABLE
- RIGHTS_RESTRICTED
- PROVIDER_ERROR
- STALE_CACHE

One provider failure must not fail the whole bundle.

## GET `/api/v1/passages/{passageId}/translation-alignments`

Filters:
- versionId
- reviewStatus

## POST `/api/v1/projects/{projectId}/translations`

Creates a user translation proposal or new version.

Requires optimistic version handling on update.

---

# 14. Stage 3 API contracts

## GET `/api/v1/passages/{passageId}/tokens`

Returns `TokenInspectionBundleV1` with canonical tokens and currently eligible annotations.

It must preserve source provenance per annotation.

## POST `/api/v1/corpus/query/validate`

Input:
`CorpusQueryV1`

Returns:
- valid boolean
- normalized query
- validation errors
- warnings
- referenced semantic-set versions

No corpus execution.

## POST `/api/v1/corpus/query/run`

Input:
`CorpusQueryV1`

Returns:
- 200 with completed result for fast execution, or
- 202 with queryRunId for async execution.

## GET `/api/v1/corpus/query-runs/{queryRunId}`

Returns:
- status
- pinned corpus releases
- normalized DSL
- count summary
- pagination metadata

## GET `/api/v1/corpus/query-runs/{queryRunId}/matches`

Paginated `CorpusMatchV1`.

Every match includes explainable bindings.

---

# 15. Stage 4 API contracts

## POST `/api/v1/library/retrieve`

This is a typed academic retrieval API, not a chatbot endpoint.

Input `AcademicRetrievalRequestV1`:

```json
{
  "intent": "PREPOSITION_SEMANTICS",
  "queryText": "semantic functions of ל",
  "passageId": null,
  "lemmaKeys": ["ל"],
  "eligibleNamespaces": ["REFERENCE_GRAMMAR"],
  "rightsMode": "PRIVATE_RESEARCH",
  "limit": 20
}
```

The server, not the client, enforces final eligible namespaces and rights.

Returns `AcademicRetrievalResultV1` with:
- retrievalUnitId
- work / edition identity
- source locator
- evidence class
- match channels
- score components
- rights-safe excerpt
- linked claims
- qualifications/exceptions
- citation locator

## GET `/api/v1/library/works/{workId}`

Bibliographic identity and available editions.

## GET `/api/v1/library/editions/{editionId}/structure`

Returns document hierarchy.

## GET `/api/v1/library/source-spans/{sourceSpanId}`

Must enforce rights and visibility.

Public mode may return metadata-only or excerpt-only response.

## POST `/api/v1/admin/ingestion/jobs`

Privileged.

Input:
- sourceAssetId
- requested pipeline

Returns 202.

## GET `/api/v1/admin/ingestion/jobs/{jobId}`

Returns explicit pipeline status and diagnostics.

---

# 16. Stage 5 API contracts

## POST `/api/v1/research/plan`

Input:
- question
- passageId optional
- projectId optional
- userTranslationVersionId optional

Returns a proposed `ResearchPlanV1`.

This endpoint plans research. It does not make a final translation claim.

## POST `/api/v1/research/runs`

Starts a reproducible research run.

The server pins:
- corpus releases
- query definitions
- semantic-set versions
- relevant source editions
- rule versions
- prompt version
- user translation version

Returns 202 or completed run for small jobs.

## GET `/api/v1/research/runs/{analysisRunId}`

Returns status, dependency pins and output summaries.

## GET `/api/v1/research/runs/{analysisRunId}/evidence`

Returns the persisted `EvidencePacketV1`.

## GET `/api/v1/research/runs/{analysisRunId}/outputs`

Returns synthesis structures.

## POST `/api/v1/research/challenge`

Creates an analysis run with mandatory counterevidence strategy.

It must not simply call the standard synthesis prompt with a different title.

---

# 17. Stable cross-stage TypeScript/domain interfaces

Implementation should eventually expose equivalent runtime-validated schemas, for example using Zod or another schema validator.

The names below are contract names.

## `CitationLocatorV1`

Fields may include:

- workId
- editionId
- sourceSpanId
- sectionLabel
- printedPage
- pdfPage
- passageReference
- providerReference

It must be possible to cite without exposing a private storage URL.

## `EvidenceItemV1`

Required:

- evidenceClass
- sourceIdentity
- citationLocator
- content or rights-safe excerpt
- stance
- provenance
- review status where relevant

## `PassageBundleV1`

Contains:
- passage identity
- references
- book identity
- navigation links

Does not automatically contain all evidence domains.

## `TokenInspectionV1`

Contains:
- canonical token
- morphemes
- annotations grouped by corpus source/release
- syntax relationships
- disagreement indicators

## `TranslationWitnessV1`

Contains:
- translation version metadata
- text if display permitted
- availability state
- notes
- rights status
- provenance

## `CorpusQueryV1`

The v1 DSL defined above.

## `CorpusMatchV1`

Contains:
- matchId
- passage
- matched bindings
- relation evidence
- match kind
- explain-why payload

## `AcademicRetrievalResultV1`

Contains:
- namespace
- work / edition
- source locator
- retrieval channels
- linked claims
- qualifications
- citation
- rights-safe display content

## `EvidencePacketV1`

Contains evidence in separate lanes:

- morphology
- syntax
- corpus
- grammar
- lexicon
- textualCriticism
- commentary
- translationWitnesses
- userResearch
- counterevidence

Do not flatten into one ranked list before synthesis.

## `AnalysisRunSnapshotV1`

Contains:
- run identity
- status
- pinned dependencies
- evidence packet identity
- output identities
- model/prompt version
- reproducibility metadata

---

# 18. Cache and invalidation contracts

## Translation cache

Key includes:
- provider
- version code
- provider reference
- content version/hash if known

Do not serve stale cached translation text indefinitely when provider terms or source updates require refresh.

## Corpus query cache

Cache key must include:
- normalized DSL hash
- corpus release IDs
- semantic-set version IDs
- query-engine version

## Academic retrieval cache

Cache key must include:
- intent
- normalized query
- eligible namespace set
- rights mode
- source edition filters
- retrieval-engine version

## Embedding invalidation

When `retrieval_units.content_hash` changes:
- old embeddings become stale;
- new embedding job is queued;
- stale vectors must not be silently treated as current.

---

# 19. Background-job contract

Use a shared job-state vocabulary where applicable:

- PENDING
- RUNNING
- COMPLETED
- FAILED
- CANCELLED
- PARTIAL_RETRYABLE

Background work should expose:
- job ID
- current state
- progress metadata where meaningful
- failure code
- retryable flag
- diagnostics

Do not block normal user requests on full-book extraction or embedding generation.

---

# 20. Security and RLS contract

At minimum, distinguish:

- public corpus data
- public/licensed bibliographic metadata
- provider-restricted translation text
- private source assets
- private extracted scholarly content
- private user projects
- private user translations
- private rules
- private analysis runs

Supabase service-role credentials must never reach the browser.

RLS should apply to retrieval-facing tables/views so that private evidence cannot be returned to another user.

Do not depend solely on UI hiding.

---

# 21. Cross-stage invariants

These rules are frozen.

## Invariant A

`passage_id` is the shared biblical anchor across translation, corpus, commentary, textual criticism and research systems.

## Invariant B

`token_id` and `morpheme_id` are application-owned, not provider IDs.

## Invariant C

Corpus annotations always carry corpus release provenance.

## Invariant D

Translation text and translation explanation are separate objects.

## Invariant E

Author-native scholarly terminology is preserved.

Concept mapping is additive and does not overwrite source terminology.

## Invariant F

Every serious analysis run pins its dependencies.

## Invariant G

Evidence packets preserve evidence lanes.

AI synthesis is downstream of evidence retrieval.

## Invariant H

Rights restrictions can reduce storage/display/retrieval capability without breaking entity identity.

## Invariant I

No later Site Build stage may replace a deterministic corpus query with LLM recall.

## Invariant J

No later Site Build stage may replace structured academic retrieval with "send all PDF chunks to the model."

---

# 22. Schema-change policy during Site Build

Allowed without architectural approval:

- adding indexes;
- adding non-semantic timestamps;
- adding performance/materialized views;
- adding nullable implementation metadata;
- adding a new table for a genuinely new feature that does not redefine existing contracts.

Requires explicit architecture change:

- changing meaning of a primary entity;
- switching canonical ID source;
- collapsing source and AI claims;
- changing passage identity model;
- changing CorpusQuery relation semantics;
- removing edition identity;
- changing rights behavior;
- making translation alignment one-to-one;
- replacing immutable version history with in-place overwrite;
- flattening evidence lanes;
- changing an API field's meaning while retaining v1 name.

---

# 23. Stage handoff gates

## Stage 1 -> Stage 2

Must exist:
- passage resolution
- passage identity
- source registry
- rights profiles
- evidence labels
- research project shell

## Stage 2 -> Stage 3

Must exist:
- translation provider abstraction
- translation version identity
- user translation versioning
- many-to-many alignment contract

No corpus-specific provider ID may be required by Stage 2 UI state.

## Stage 3 -> Stage 4

Must exist:
- canonical token/morpheme identity
- passage-token relationship
- corpus release provenance
- deterministic Query DSL
- semantic-set versioning

Academic RAG may link to lemmas/passages but must not be required for corpus correctness.

## Stage 4 -> Stage 5

Must exist:
- work/edition identity
- source span citations
- structured claims
- source-specific retrieval units
- rights-aware retrieval
- concept graph
- retrieval namespaces
- source deduplication

AI synthesis must not launch before these are available.

---

# 24. First implementation artifacts required from Stage 1

The first Site Build prompt should create or reserve the following code-level contracts, even if some implementations are fixtures:

- `src/contracts/passage.ts`
- `src/contracts/evidence.ts`
- `src/contracts/translation.ts`
- `src/contracts/corpus-query.ts`
- `src/contracts/academic.ts`
- `src/contracts/research.ts`
- `src/lib/api/client.ts`
- `src/lib/api/errors.ts`

Actual folder names may vary with the generated framework, but one shared contract layer must exist.

Do not duplicate competing types separately inside page components.

---

# 25. Final architectural decision

The project uses one shared relational identity model with four specialised evidence systems:

1. Biblical corpus system
2. Translation corpus system
3. Academic literature system
4. Research workspace / analysis system

They communicate through explicit IDs and typed APIs.

They do **not** communicate by passing unstructured model prose between stages.

The core flow is:

```
Passage identity
    |
    +--> Translation witnesses / alignments
    |
    +--> Hebrew tokens / corpus structures
    |
    +--> Academic passage / lemma / concept links
    |
    +--> User research objects
                |
                v
        Reproducible analysis run
                |
                v
          Evidence packet
                |
                v
            AI synthesis
```

This contract is the baseline for all five future Site Build prompts.
