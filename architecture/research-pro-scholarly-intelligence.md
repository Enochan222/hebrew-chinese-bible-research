# Research Pro and Scholarly Intelligence Architecture

Status: **ACTIVE CANDIDATE DOMAIN CONTRACT**

This document adds a scholarly-intelligence layer to the v1.1 product architecture without creating a second application or a second scholarly database.

It must be read with:

- `architecture/database-api-cross-stage-contract-v1.1.md`
- `architecture/product-platform-and-publication-model.md`
- `architecture/ui-mode-cross-stage-contract.md`
- `contracts/v1.1/vocabulary.json`

## 1. Product principle

Research Pro is not "more AI".

It is deeper scholarly visibility and workflow over the same ResearchRelease.

The public product therefore has two experience modes:

- STUDY
- RESEARCH

Both consume the same published corpus, evidence graph, translations, rules, commentary and ResearchRelease.

Research mode exposes more depth, discovery and research tooling.

Study mode preserves minimum academic transparency.

No Research Pro feature may create a parallel ontology or duplicate canonical source data.

---

# 2. Three scholarly knowledge states

## 2.1 Core Scholarly Library

Private curated sources such as:

- reference grammars;
- lexica;
- BHS/BHQ;
- textual-criticism literature;
- commentaries;
- exegesis method;
- Chinese translation documentation when acquired.

These may be deeply structured and reviewed.

## 2.2 Scholarly Discovery Universe

External provider records that may include:

- journal articles;
- books;
- book chapters;
- dissertations;
- reviews;
- conference literature;
- citation/reference graph records;
- recent publications.

Discovery results are candidate metadata.

They are not automatically canonical ScholarlyWorks and do not enter published synthesis by discovery alone.

## 2.3 Curated Scholarly Knowledge Release

Reviewed structured objects published inside a ResearchRelease:

- canonical bibliographic works;
- approved claims;
- research issues;
- research positions;
- target links;
- literature snapshots;
- commentary entries;
- translation decisions;
- citations;
- public-safe excerpts.

Canonical commentary and state-of-research views use this layer.

---

# 3. ScholarlyDiscoveryProvider abstraction

External discovery must be provider-agnostic.

## 3.1 Provider capability contract

A provider adapter may declare support for capabilities such as:

- SEARCH_WORKS
- GET_WORK
- GET_AUTHORS
- GET_REFERENCES
- GET_CITATIONS
- GET_CITATION_CONTEXTS
- RESOLVE_DOI
- GET_ABSTRACT
- GET_FULLTEXT
- GET_OPEN_ACCESS_LOCATION
- GET_RETRACTION_OR_CORRECTION_STATUS
- SEARCH_BY_DATE
- SEARCH_BY_PUBLICATION_TYPE

No single provider is assumed to support all capabilities.

## 3.2 Provider identity

Provider IDs are external identifiers only.

They must never become the primary key of a canonical scholarly work.

---

# 4. DiscoveryRecord contract

External search results enter a staging/discovery layer before bibliographic resolution.

## 4.1 `scholarly_discovery_providers`

Fields:

- `scholarly_discovery_provider_id uuid PK`
- `provider_key text unique`
- `display_name text`
- `capabilities jsonb`
- `active boolean`
- `metadata jsonb`

## 4.2 `external_discovery_records`

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
- `citation_count_raw integer nullable`
- `retrieved_at timestamptz`
- `payload_hash text`
- `raw_payload jsonb nullable`
- `access_level text`
- `record_status text`

Unique where possible:

`(scholarly_discovery_provider_id, provider_record_id, payload_hash)`

A provider record is immutable as retrieved. Updated provider metadata creates a new payload version or explicit supersession.

## 4.3 `external_record_resolutions`

Maps discovery records to canonical works.

Fields:

- `external_record_resolution_id uuid PK`
- `external_discovery_record_id uuid FK`
- `work_id uuid FK`
- `resolution_method text`
- `resolution_confidence numeric nullable`
- `review_status text`
- `resolved_at timestamptz`
- `resolved_by uuid nullable`

Resolution methods may include:

- DOI_EXACT
- ISBN_EXACT
- PROVIDER_CROSSWALK
- TITLE_AUTHOR_FINGERPRINT
- MANUAL
- AI_ASSISTED

AI-assisted resolution is not automatically VERIFIED.

## 4.4 Access level

Discovery and claim extraction must preserve source-access level:

- METADATA_ONLY
- ABSTRACT_ONLY
- CITATION_CONTEXT_ONLY
- FULLTEXT_OPEN
- FULLTEXT_LICENSED
- PRIVATE_FULLTEXT

A system may identify a possibly relevant work from metadata/abstract without pretending to have read its full text.

An AI_EXTRACTED_PROPOSITION must record the source access level and exact basis used.

---

# 5. Scholarly target-link contract

A work/claim may be relevant to a passage without explicitly naming that passage.

## 5.1 `scholarly_target_links`

Fields:

- `scholarly_target_link_id uuid PK`
- `source_object_id uuid FK research_objects`
- `target_object_id uuid FK research_objects`
- `target_type text`
- `relevance_type text`
- `directness text`
- `mapping_method text`
- `mapping_confidence numeric nullable`
- `source_span_id uuid nullable`
- `review_status text`
- `provenance_id uuid nullable`

Supported target types include:

- REFERENCE_SPAN
- BIBLICAL_BOOK
- LEXEME
- MORPHEME_OR_FORM
- CONSTRUCTION
- CONCEPT
- TEXTUAL_VARIANT
- RESEARCH_ISSUE
- TRANSLATION_ISSUE

Mapping methods include:

- EXPLICIT_REFERENCE
- SECTION_SCOPE
- AUTHOR_INDEX
- CITATION_CONTEXT
- LEXICAL_MAPPING
- CONSTRUCTION_MAPPING
- HUMAN_CURATED
- AI_INFERRED

An AI_INFERRED link must not be rendered as an explicit source citation.

---

# 6. ResearchIssue contract

A ResearchIssue represents a bounded scholarly question.

It is not merely a topic tag.

## 6.1 `research_issues`

Fields:

- `research_issue_id uuid PK`
- `issue_key text unique nullable`
- `title text`
- `question_text text`
- `issue_type text`
- `debate_status text`
- `current_snapshot_id uuid nullable`
- `review_status text`
- `created_at timestamptz`
- `updated_at timestamptz`

Possible issue types include:

- TEXTUAL
- MORPHOLOGICAL
- SYNTACTIC
- LEXICAL
- SEMANTIC
- DISCOURSE
- LITERARY
- COMPOSITIONAL
- HISTORICAL
- TRANSLATIONAL
- RECEPTION
- METHODOLOGICAL

## 6.2 `research_issue_scopes`

A ResearchIssue may have multiple scopes.

Fields:

- `research_issue_scope_id uuid PK`
- `research_issue_id uuid FK`
- `scope_object_id uuid FK research_objects`
- `scope_type text`
- `scope_role text`
- `review_status text`

Examples:

- 1 Sam 16:7 reference span;
- ל lexeme/morpheme concept;
- PERCEPTION_VERB_LAMED_BODY_PART construction;
- a textual variant;
- a whole book.

## 6.3 Debate status

Allowed values are descriptive and conservative:

- HISTORICAL
- ONGOING
- REFRAMED
- SPECIALIST_MINORITY
- INSUFFICIENT_COVERAGE
- NOT_CLASSIFIED

A debate status must come from a reviewed literature snapshot, not one model response.

Do not publish numeric consensus percentages unless a genuine survey supports them.

---

# 7. ResearchPosition contract

A ResearchPosition represents one analysable position within a ResearchIssue.

## 7.1 `research_positions`

Fields:

- `research_position_id uuid PK`
- `research_issue_id uuid FK`
- `position_key text nullable`
- `title text`
- `position_summary text`
- `position_status text`
- `review_status text`
- `created_at timestamptz`
- `updated_at timestamptz`

Position summary is a reviewed representation, not automatically a quotation from any scholar.

## 7.2 `position_claim_links`

Fields:

- `position_claim_link_id uuid PK`
- `research_position_id uuid FK`
- `scholarly_claim_id uuid FK`
- `relationship text`
- `assertion_agent_type text`
- `review_status text`
- `notes text nullable`

Relationships:

- SUPPORTS
- OPPOSES
- QUALIFIES
- REFRAMES
- CONTEXTUALISES
- HISTORICALLY_PRECEDES

The number of linked claims or works must not be transformed directly into a consensus percentage.

## 7.3 `issue_relations`

Fields:

- `issue_relation_id uuid PK`
- `from_issue_id uuid FK`
- `to_issue_id uuid FK`
- `relation_type text`
- `assertion_agent_type text`
- `review_status text`

Examples:

- SUBISSUE_OF
- REFRAMES
- HISTORICALLY_FOLLOWS
- DEPENDS_ON
- OVERLAPS_WITH

---

# 8. LiteratureSnapshot contract

"Current scholarship" is always snapshot-bounded.

## 8.1 `literature_snapshots`

Fields:

- `literature_snapshot_id uuid PK`
- `snapshot_type text`
- `target_object_id uuid FK research_objects`
- `as_of_date date`
- `coverage_start_date date nullable`
- `coverage_end_date date nullable`
- `review_scope text`
- `coverage_note text nullable`
- `reviewer_id uuid nullable`
- `review_status text`
- `research_release_id uuid nullable`
- `created_at timestamptz`

Snapshot types:

- BOOK_STATE_OF_RESEARCH
- PASSAGE_LITERATURE
- ISSUE_LITERATURE
- CONSTRUCTION_LITERATURE
- TRANSLATION_ISSUE_LITERATURE

## 8.2 `literature_search_runs`

Fields:

- `literature_search_run_id uuid PK`
- `literature_snapshot_id uuid FK`
- `run_date timestamptz`
- `provider_ids uuid[]` conceptually; implementation should use a junction table
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

## 8.3 `literature_search_queries`

Fields:

- `literature_search_query_id uuid PK`
- `literature_search_run_id uuid FK`
- `language_code text`
- `query_text text`
- `query_type text`
- `generated_by text`
- `query_order integer`

Multilingual expansion is stored, not silently discarded.

## 8.4 `literature_inclusions`

Fields:

- `literature_snapshot_id uuid FK`
- `work_id uuid FK`
- `inclusion_role text`
- `relevance_type text`
- `reason text nullable`
- `review_status text`

Inclusion roles may include:

- KEY_WORK
- SEMINAL_WORK
- REPRESENTATIVE_WORK
- RECENT_DEVELOPMENT
- MINORITY_POSITION
- COUNTEREVIDENCE
- BACKGROUND

## 8.5 `literature_exclusions`

Fields:

- `literature_snapshot_id uuid FK`
- `external_discovery_record_id uuid nullable`
- `work_id uuid nullable`
- `exclusion_reason text`
- `review_status text`

The aim is auditability, not a biomedical-style systematic-review claim unless the methodology truly supports that description.

---

# 9. Literature review artifact contract

A literature review is a versioned rendering of structured research state.

## 9.1 `literature_review_snapshots`

Fields:

- `literature_review_snapshot_id uuid PK`
- `target_object_id uuid FK research_objects`
- `literature_snapshot_id uuid FK`
- `research_release_id uuid nullable`
- `review_structure jsonb`
- `review_summary text nullable`
- `coverage_limitations text nullable`
- `review_status text`
- `content_hash text`

A book-level literature review should normally be issue-organized rather than author-by-author.

The prose summary is derivative.

The underlying issues, positions, works and claims remain canonical research objects.

---

# 10. CommentaryEntry contract

Commentary is compiled published scholarship, not raw LLM prose.

## 10.1 `commentary_entries`

Fields:

- `commentary_entry_id uuid PK`
- `reference_span_id uuid FK`
- `research_release_id uuid FK`
- `commentary_kind text`
- `title text nullable`
- `summary text nullable`
- `review_status text`
- `content_hash text`
- `supersedes_commentary_entry_id uuid nullable`

Commentary kinds may include:

- PASSAGE_COMMENTARY
- TEXTUAL_NOTE
- GRAMMATICAL_NOTE
- LEXICAL_NOTE
- LITERARY_NOTE
- HISTORICAL_NOTE
- TRANSLATION_NOTE
- STATE_OF_RESEARCH_NOTE

## 10.2 `commentary_sections`

Fields:

- `commentary_section_id uuid PK`
- `commentary_entry_id uuid FK`
- `section_type text`
- `section_order integer`
- `rendered_text text`
- `source_payload jsonb nullable`
- `section_hash text`

Section types may include:

- TEXTUAL_STATE
- MORPHOLOGY
- LEXICON
- SYNTAX
- CORPUS
- TEXTUAL_CRITICISM
- LITERARY_CONTEXT
- HISTORICAL_CONTEXT
- SCHOLARLY_ISSUES
- TRANSLATION_IMPLICATIONS
- CHINESE_TRANSLATION_DECISION
- COUNTERARGUMENTS
- UNCERTAINTY

## 10.3 `commentary_section_evidence`

Fields:

- `commentary_section_id uuid FK`
- `research_object_id uuid FK`
- `stance text`
- `citation_locator jsonb nullable`
- `sort_order integer`

Commentary rendering is downstream of evidence.

The public Study mode may show a concise compiled commentary.

Research mode may expose section evidence, issue graph, literature snapshot and source lineage.

---

# 11. Translation Note versus Commentary

Do not merge these concepts.

Commentary answers:

- what scholarly questions arise;
- what the textual/linguistic/exegetical evidence indicates;
- where major positions differ.

Translation Note answers:

- why the project selected a particular Chinese rendering;
- which ambiguity was preserved or resolved;
- which editorial/translation policy was applied;
- what target-language trade-offs were accepted.

A Translation Note may cite commentary evidence but remains a separate published artifact.

---

# 12. Latest Research Discovery state

Live discovery and reviewed scholarship must be visibly separate.

## 12.1 Reviewed state

`CURATED_IN_RELEASE`

Characteristics:

- reviewed;
- release-pinned;
- may affect commentary / translation decisions;
- versioned;
- citable as product scholarship.

## 12.2 Live discovery state

`DISCOVERED_SINCE_RELEASE`

Characteristics:

- provider-discovered;
- metadata/abstract/fulltext access varies;
- not yet incorporated into reviewed synthesis;
- cannot silently change commentary or translation decision;
- may be promoted only through authoring/review/publication.

Research mode may display this state.

Study mode does not need to display live discovery.

---

# 13. ProductEntitlement contract

Product entitlements are commercial/product-access controls.

They are **not** source rights.

## 13.1 Separation rule

`RightsPolicy` answers:

> Is the product legally/contractually allowed to store, process, display, quote, export or send this source to a model?

`ProductEntitlement` answers:

> Is this user/account entitled to use this product feature?

A product entitlement can never override a DENY in RightsPolicy.

A RightsPolicy ALLOW does not mean every customer must receive the feature.

## 13.2 `product_features`

Fields:

- `product_feature_id uuid PK`
- `feature_key text unique`
- `display_name text`
- `description text`
- `feature_group text`
- `default_experience_mode text`
- `active boolean`

Candidate feature keys include:

- PASSAGE_STUDY
- KEY_SCHOLARSHIP
- BASIC_CORPUS_SEARCH
- ADVANCED_CORPUS_QUERY
- CONSTRUCTION_BROWSER
- SCHOLARLY_ISSUE_SUMMARY
- SCHOLARLY_DEBATE_GRAPH
- FULL_BIBLIOGRAPHY
- LITERATURE_REVIEW
- LIVE_LITERATURE_DISCOVERY
- CITATION_DEPENDENCY_GRAPH
- ADVANCED_TEXTUAL_CRITICISM
- RESEARCH_EXPORT
- SAVED_RESEARCH_PROJECTS
- OPTIONAL_AI_QUERY_INTERPRETATION

## 13.3 `product_entitlements`

Fields:

- `product_entitlement_id uuid PK`
- `principal_type text`
- `principal_id uuid`
- `product_feature_id uuid FK`
- `entitlement_decision text`
- `source_type text`
- `source_reference text nullable`
- `valid_from timestamptz nullable`
- `valid_until timestamptz nullable`
- `metadata jsonb nullable`

Principal types may include:

- USER
- ORGANIZATION
- PLAN

Decision:

- ALLOW
- DENY

Subscription/billing implementation is intentionally separate from this domain contract.

## 13.4 Minimum academic transparency invariant

Entitlements must not hide the minimum evidence needed to verify a published claim shown in Study mode.

If Study mode displays a substantive published conclusion, it must remain able to show at least:

- evidence class;
- key citation(s);
- research release;
- main uncertainty/alternative where material;
- link to bibliographic metadata;
- rights-safe supporting excerpt where publication rights allow it.

Research Pro may expose the full graph and workflow depth.

---

# 14. AccessRoute contract

Bibliographic visibility and full-text access are separate.

## 14.1 `source_access_routes`

Fields:

- `source_access_route_id uuid PK`
- `work_id uuid FK`
- `edition_id uuid nullable`
- `route_type text`
- `url text nullable`
- `availability_scope text`
- `rights_policy_id uuid nullable`
- `active boolean`
- `verified_at timestamptz nullable`

Route types:

- OPEN_ACCESS_FULLTEXT
- DOI_PUBLISHER
- LIBRARY_RESOLVER
- LICENSED_PLATFORM
- PRIVATE_LIBRARY_COPY
- METADATA_ONLY

Public UI must never expose PRIVATE_LIBRARY_COPY routes.

---

# 15. Publication and ResearchRelease integration

The following become release components or release-pinned objects where applicable:

- approved ResearchIssues;
- approved ResearchPositions;
- reviewed target links;
- LiteratureSnapshots;
- LiteratureReviewSnapshots;
- CommentaryEntries;
- bibliographic/citation graph;
- published access routes;
- Study/Research serving projections.

Live DiscoveryRecords remain outside the immutable curated scholarly release until promoted.

---

# 16. Phase ownership

## Phase 1

Reserve:

- product feature/entitlement contract;
- Study/Research experience mode vocabulary;
- release-aware shared UI contracts.

No full scholarly-intelligence implementation required.

## Phase 2

Use:

- key scholarship summary;
- translation-note/public commentary placeholders;
- minimum evidence transparency.

## Phase 3

Expose Research mode links to:

- constructions;
- advanced corpus queries;
- saved research objects.

## Phase 4

Own:

- scholarly discovery provider abstraction;
- external discovery records;
- bibliographic resolution;
- scholarly target links;
- ResearchIssue;
- ResearchPosition;
- LiteratureSnapshot;
- source access routes;
- issue/debate editorial review.

## Phase 5

Own:

- published literature reviews;
- published CommentaryEntries;
- Study/Research serving projections;
- product feature entitlements;
- live-discovery Research mode integration;
- release compatibility and full QA.

---

# 17. Non-negotiable constraints

1. Research Pro is not a separate application.
2. Research Pro is not a separate scholarly database.
3. Study and Research use the same active ResearchRelease.
4. Live discovery cannot change a published conclusion.
5. External provider records are not canonical scholarly works until resolved.
6. Metadata-only/abstract-only access cannot be represented as full-text reading.
7. Work count is not consensus.
8. Citation count is not correctness.
9. Issue/Position summaries are reviewed representations.
10. Product entitlement never overrides source rights.
11. Study mode retains minimum evidence transparency.
12. Commentary prose is derivative from structured evidence.
13. Translation Note is distinct from Commentary.
14. Current scholarship claims are snapshot-bounded.
