# Product Platform and Publication Model

Status: **ACTIVE CANDIDATE PRODUCT ARCHITECTURE**

This document reframes the project as a database-backed scholarly product platform rather than a single runtime AI application.

It implements the product intent defined in `PROJECT_CHARTER.md`.

It complements:

- `architecture/database-api-cross-stage-contract-v1.1.md`
- `architecture/academic-evidence-policy.md`
- `architecture/security-trust-boundaries.md`
- `architecture/research-evaluation-and-benchmarks.md`
- `contracts/v1.1/vocabulary.json`

## 1. Product definition

The product is best understood as:

> an AI-assisted scholarly authoring and compilation platform that publishes immutable research releases to a deterministic Hebrew Bible research product.

The public product must not depend on runtime RAG or runtime generative synthesis for its core scholarly claims.

The core runtime should be able to serve:

- Hebrew text and linguistic annotations;
- published Chinese translation witnesses;
- reviewed project Chinese rendering / translation decision where available;
- published translation analyses;
- approved scholarly claims and citations;
- construction instances;
- approved rule applications;
- semantic-set memberships;
- deterministic corpus queries;
- saved user research objects.

An LLM may be used at runtime for optional natural-language-to-DSL interpretation or clearly labelled exploratory assistance. It is not the authority that determines corpus membership or the canonical published analysis.

## 2. Four product planes

Do not model the system as only "the app" plus "the database".

### 2.1 Authoring / Research Plane

Private and privileged.

Contains material such as:

- source PDFs / EPUB / DOCX;
- extracted source text;
- OCR output;
- academic retrieval indexes;
- embeddings where permitted;
- AI-extracted candidate claims;
- AI-proposed concept mappings;
- unreviewed and rejected mappings;
- research drafts;
- unpublished rule versions;
- unpublished translation decisions;
- benchmark/evaluation artefacts;
- private notes.

This plane is where RAG, Gemini File Search, Notebook-style research tools, batch model processing and other AI-assisted workflows may be used.

It is not the public serving database.

### 2.2 Publication / Control Plane

Privileged one-way publication layer.

Responsibilities:

- assemble a candidate research release;
- validate rights;
- validate citations;
- validate review status;
- run benchmark gates;
- check private-source leakage;
- check quotation/excerpt limits;
- build serving projections;
- generate release manifest and hashes;
- publish or reject the release;
- support rollback to an earlier release.

No public request may promote data directly into a published release.

### 2.3 Public Serving Plane

Optimized for deterministic reads and corpus search.

Contains only publishable/approved material such as:

- published corpus releases;
- published text expressions;
- published translation witnesses where permitted;
- approved semantic sets;
- construction definitions and instances;
- approved rule sets and rule applications;
- published passage analyses;
- bibliographic citations;
- legally displayable excerpts;
- compiled search projections;
- release metadata.

Restricted source-book full text does not need to exist here.

### 2.4 User Workspace Plane

Mutable user-scoped product data.

Examples:

- saved queries;
- saved result sets;
- private annotations;
- user translation drafts;
- user-created semantic sets;
- user-created rule drafts;
- project folders;
- preferences.

This plane is logically distinct from both published scholarly data and the private authoring corpus.

For an MVP it may share a Supabase project with the public serving plane under strict schema/RLS separation.

If future user uploads contain private copyrighted source material, those uploads require a separate private-source design and must not automatically enter the official authoring or published research graph.

## 3. Physical deployment recommendation

Logical separation is mandatory.

Physical separation should be staged.

### Development / early alpha

Acceptable:

- one local PostgreSQL instance;
- separate schemas for authoring, publication, serving and workspace;
- explicit database roles and tests.

### Public beta / production

Recommended:

- Authoring Research database/project
- Public Serving + User Workspace database/project

The publication worker has write access to Serving.

The public runtime does not have credentials for the Authoring Research database.

For higher assurance, the Publication/Control service may run in a separate environment with credentials for both source and target databases.

The main security objective is not merely RLS. It is reducing blast radius by ensuring restricted source content is absent from the public serving datastore.

## 4. One-way publication firewall

Canonical flow:

```text
PRIVATE AUTHORING
    |
    | candidate build
    v
PUBLICATION VALIDATION
    |
    | PUBLISHABLE only
    v
IMMUTABLE RESEARCH RELEASE
    |
    v
PUBLIC SERVING DATABASE
```

Publication validation must check at least:

- source/asset rights;
- model-context rights where AI was used;
- citation existence;
- citation-source entailment status;
- review requirements;
- unpublished/private object references;
- private Drive URLs;
- quotation/excerpt limits;
- unsupported AI assertions;
- benchmark gates;
- schema compatibility;
- compiled-search projection consistency;
- release manifest integrity.

## 4A. Publication visibility atomicity

When Authoring and Public Serving are physically separate databases, the product does **not** claim one distributed PostgreSQL ACID transaction across both systems.

The same boundary also forbids public runtime referential dependence on Authoring. Publication therefore materializes a **Serving-owned projection registry** containing the release-visible research-object identities, reference spans, compiled corpus/search rows, and other public dependencies required by that ResearchRelease. Public APIs and deterministic corpus queries resolve only against Serving-owned data. Cross-database provenance is checked before publication and copied as immutable identity/hash metadata; it is not implemented as a runtime FK to the Authoring database.

Required publication sequence:

1. compile an immutable candidate package in Authoring;
2. complete rights, citation, review, benchmark and hash validation;
3. materialize the complete candidate ResearchRelease in the Serving database while inactive;
4. verify Serving parity, foreign keys, projections and hashes;
5. in one Serving-database transaction, finalize the release's publishable state and move the selected release-channel pointer;
6. only then expose the new release.

The atomic guarantee is **publication visibility**: clients observe the complete old release or the complete new release, never a partially materialized release.

A failed candidate load or validation leaves the existing PRODUCTION pointer unchanged.

---

## 5. ResearchBuild and ResearchRelease

Build attempts, immutable published payloads, and release lifecycle events are separate objects.

### 5.1 `research_builds`

Mutable build/compilation attempt.

Fields:

- `research_build_id uuid PK`
- `build_version text`
- `status text`
- `started_at timestamptz`
- `completed_at timestamptz nullable`
- `compiler_version text`
- `git_commit_sha text`
- `source_inventory_snapshot_id uuid nullable`
- `benchmark_version text nullable`
- `notes text nullable`

Canonical build lifecycle:

- QUEUED
- RUNNING
- FAILED
- READY_FOR_REVIEW
- APPROVED
- REJECTED
- COMPLETED

A ResearchBuild is never PUBLISHED. Publication creates a ResearchRelease.

### 5.2 `research_releases`

Immutable release payload.

Fields include:

- `research_release_id uuid PK`
- `release_label text unique`
- `published_at timestamptz`
- `source_build_id uuid FK`
- `manifest_schema_version text`
- `manifest_hash text`
- `manifest_hash_algorithm text`
- `manifest_canonical_serialization text`
- `git_commit_sha text`
- `compiler_version text`
- `benchmark_version text nullable`

After publication, the scholarly payload and manifest are immutable.

Corrections create a new release.

### 5.3 `research_release_components`

Release-manifest components point to registered `research_objects`, not unchecked naked UUIDs.

Fields:

- `research_release_id uuid FK`
- `component_kind text`
- `component_research_object_id uuid FK -> research_objects`
- `component_version text`
- `content_hash text`
- `component_order integer NOT NULL`

The publication compiler validates component-kind/subtype compatibility.

Components are serialized in ascending unique `component_order`; duplicate or missing order values fail publication.

### 5.4 `research_release_events`

Append-only lifecycle history:

- PUBLISHED
- SUPERSEDED
- REVOKED
- REACTIVATED

RL-1 separates two different predicates that must never be conflated:

1. **ever published / permanently immutable**: once a ResearchRelease receives its first PUBLISHED event, the release, components and compiled payload/projections remain immutable forever, including while REVOKED;
2. **currently publicly servable**: public RLS, pinned passage reads and channel eligibility depend on the latest lifecycle event.

Every event carries a positive per-release `event_sequence`. Sequence starts at 1 and is contiguous. `effective_at` is nondecreasing, but equal timestamps are explicitly allowed; `event_sequence`, never UUID ordering, resolves equal-time chronology.

Canonical transition graph:

```text
(no event) -> PUBLISHED
PUBLISHED  -> SUPERSEDED | REVOKED
SUPERSEDED -> REVOKED
REVOKED    -> REACTIVATED
REACTIVATED -> SUPERSEDED | REVOKED
```

Public servability policy:

- PUBLISHED: servable;
- SUPERSEDED: servable as a citation-stable historical pinned release;
- REVOKED: not servable;
- REACTIVATED: servable again.

Superseding, revoking or reactivating a release never mutates its scholarly payload.

Machine authority: `contracts/v1.1/release-lifecycle-policy.json`.

### 5.5 Release channels

`release_channels` and `release_channel_pointers` separate deployment selection from release identity.

Canonical channels:

- PREVIEW
- STAGING
- PRODUCTION

A channel pointer may target only a currently publicly servable ResearchRelease. REVOKED atomically removes any pointer to that release. REACTIVATED restores servability but never restores a channel pointer automatically.

Rollback updates a channel pointer to an earlier currently servable ResearchRelease. It does not append lifecycle events or mutate either release.

## 6. Manifest integrity

The release manifest payload excludes its own `manifest_hash`.

Canonical hashing contract:

- RFC 8785 JSON Canonicalization Scheme;
- UTF-8;
- SHA-256.

The public site exposes the resolved `research_release_id`, and citation-stable APIs allow a caller to pin a historical release explicitly.

## 7. Runtime model: deterministic by default

Core public request path:

```text
Browser
  -> API
  -> active ResearchRelease
  -> compiled serving tables/indexes
  -> deterministic response
```

Opening a passage should not trigger:

- PDF retrieval;
- academic book RAG;
- embedding search across the source library;
- fresh translation generation;
- fresh canonical scholarly synthesis.

Published passage analysis is read from the active release.

## 8. Optional runtime AI

Optional runtime LLM functionality may exist in a separate adapter.

Primary approved use:

```text
natural-language query
    -> constrained CorpusQuery AST
    -> schema validation
    -> complexity validation
    -> deterministic query engine
```

The LLM must not:

- generate arbitrary SQL for execution;
- decide which corpus rows match;
- modify rights scope;
- access authoring-source full text;
- silently create published rules or claims.

If the LLM provider is unavailable, visual pattern search and DSL search must continue to work.

## 9. Runtime scholarly discovery is supplementary

Demoting runtime RAG does not mean all runtime literature search is forbidden.

A future public feature may search:

- published claim representations;
- bibliographic metadata;
- legally displayable excerpts;
- public/open literature.

This is supplementary scholarly discovery.

It must not be the source of canonical published analysis.

Restricted private academic source text remains in the authoring plane.

## 10. Construction model

A corpus construction is not the same thing as an interpretive rule.

### 10.1 `construction_definitions`

Represents a named formal pattern.

Examples:

- PERCEPTION_VERB_LAMED_BODY_PART
- INFINITIVE_ABSOLUTE_PLUS_FINITE_VERB
- WAYYIQTOL_CHAIN
- LAMED_NORM_CRITERION_CANDIDATE

Fields:

- `construction_definition_id uuid PK`
- `name text`
- `description text`
- `current_version_id uuid nullable`
- `status text`

### 10.2 `construction_definition_versions`

Append-only.

Fields:

- `construction_definition_version_id uuid PK`
- `construction_definition_id uuid FK`
- `version_number integer`
- `dsl_version text`
- `query_ast jsonb`
- `framework_requirements jsonb`
- `semantic_set_requirements jsonb`
- `created_at timestamptz`
- `review_status text`

The `query_ast` uses the same validated CorpusQuery AST as ad-hoc search.

### 10.3 `construction_instances`

Materialized build-time results for named constructions.

Fields:

- `construction_instance_id uuid PK`
- `construction_definition_version_id uuid FK`
- `corpus_release_id uuid FK`
- `reference_span_id uuid FK`
- `node_bindings jsonb`
- `match_explanation jsonb`
- `review_status text`
- `result_hash text`

Construction instances are corpus-analysis results within a pinned release/framework.

They are not translation conclusions.

## 11. Rule model

Formal corpus pattern and interpretive rule must remain separate.

### 11.1 Rule kinds

Recommended official-rule kinds:

- LINGUISTIC_HEURISTIC
- TRANSLATION_POLICY
- PASSAGE_OVERRIDE
- EDITORIAL_CONVENTION

Do not use SEARCH_PATTERN as a rule kind. A search pattern belongs to `construction_definitions`.

### 11.2 `rules`

Stable rule identity.

Fields:

- `rule_id uuid PK`
- `name text`
- `rule_kind text`
- `status text`
- `current_version_id uuid nullable`

### 11.3 `rule_versions`

Append-only.

Fields:

- `rule_version_id uuid PK`
- `rule_id uuid FK`
- `version_number integer`
- `scope_json jsonb`
- `trigger_construction_version_id uuid nullable`
- `condition_ast jsonb nullable`
- `implication_json jsonb`
- `priority integer nullable`
- `specificity integer nullable`
- `review_status text`
- `created_at timestamptz`

A rule trigger should reuse construction/query semantics rather than invent arbitrary trigger JSON.

### 11.4 `rule_evidence`

Fields:

- `rule_version_id uuid FK`
- `research_object_id uuid FK`
- `stance text`
- `citation_locator jsonb nullable`
- `notes text nullable`

Stance:
- SUPPORTS
- OPPOSES
- QUALIFIES
- CONTEXT

### 11.5 `rule_applications`

Build-time or deterministic runtime application of a rule to a passage/construction instance.

Fields:

- `rule_application_id uuid PK`
- `rule_version_id uuid FK`
- `construction_instance_id uuid nullable`
- `reference_span_id uuid FK`
- `matched_conditions jsonb`
- `failed_conditions jsonb nullable`
- `exception_status text`
- `result_json jsonb`
- `review_status text`
- `result_hash text`

A rule application is not automatically the final translation decision.

## 12. Translation decisions and published analysis

### 12.0 Adopted source text and project policy

An official project rendering must pin:

- an immutable TranslationSourceBasis identifying the exact source text stream/segments and adopted textual-critical reading;
- an exact TranslationPolicyVersion describing the project target-language/editorial policy.

TranslationPolicyVersion aggregates existing TRANSLATION_POLICY / EDITORIAL_CONVENTION RuleVersions; it does not create a parallel rule engine.

Source-basis objects are immutable passage-level dependencies reached through TranslationDecision and the published translation/analysis aggregate. They are not required to appear one-by-one as top-level ResearchRelease manifest components. The aggregate's canonical hash/projection must seal the exact decision -> source-basis identities it contains.

### 12.1 `translation_decisions`

Records an editorial/research decision.

Suggested fields:

- `translation_decision_id uuid PK`
- `reference_span_id uuid FK`
- `translation_source_basis_id uuid FK`
- `translation_policy_version_id uuid FK`
- `target_language_tag text`
- `decision_type text`
- `decision_payload jsonb`
- `rule_application_ids uuid[]` only as a conceptual shape; implementation should use a junction table;
- `review_status text`
- `supersedes_decision_id uuid nullable`

A translation decision may draw on several rules, textual-critical evidence and passage-specific reasoning.

### 12.2 `published_passage_analyses`

Precompiled, reviewable public analysis.

Fields:

- `published_analysis_id uuid PK`
- `research_release_id uuid FK`
- `reference_span_id uuid FK`
- `analysis_type text`
- `analysis_payload jsonb`
- `analysis_hash text`
- `review_status text`
- `evidence_packet_id uuid nullable`

Public passage pages read this object instead of rebuilding the analysis from source books on every request.

## 13. Semantic sets

Semantic sets are compiled research objects.

### `semantic_sets`

- stable identity;
- name;
- description;
- owner/source type;
- official/user status.

### `semantic_set_versions`

Append-only definition.

### `semantic_set_members`

Each membership records:

- lexeme/object;
- inclusion/exclusion status;
- reason;
- source/evidence;
- confidence where appropriate;
- review status.

Official public search must pin a published semantic-set version.

Do not ask an LLM at query time whether a lexeme belongs to BODY_PART, PERCEPTION_VERB or another official set.

## 14. Compiled serving projections

The canonical annotation model may remain normalized and source-faithful.

The public search hot path should use compiled projections.

Possible release-scoped tables:

### `serving_words`

- research_release_id
- corpus_release_id
- annotation_framework_id
- word_node_id
- reference_span_id
- global_position
- surface
- lexeme_id
- pos
- stem
- person
- gender
- number
- state
- phrase_node_id nullable
- clause_node_id nullable

### `serving_morphemes`

- research_release_id
- corpus_release_id
- annotation_framework_id
- morpheme_node_id
- host_word_node_id
- lexeme_id
- morpheme_type
- position_within_host
- features

### `serving_relations`

- research_release_id
- corpus_release_id
- annotation_framework_id
- from_node_id
- to_node_id
- relation_type

### `serving_semantic_memberships`

- research_release_id
- semantic_set_version_id
- member_object_id

These are compiler outputs, not the scholarly source of truth.

They can be regenerated from canonical corpus/annotation data.

## 15. Query API surface

Core public APIs should prioritize deterministic serving.

Examples:

- `GET /api/v1/releases/current`
- `GET /api/v1/passages/{reference}`
- `GET /api/v1/passages/{reference}/translations`
- `GET /api/v1/passages/{reference}/analysis`
- `GET /api/v1/passages/{reference}/rule-applications`
- `GET /api/v1/constructions/{id}/instances`
- `POST /api/v1/corpus/query/validate`
- `POST /api/v1/corpus/query/run`
- `GET /api/v1/evidence/{id}`

Optional:

- `POST /api/v1/query/interpret`

The optional endpoint returns a validated candidate CorpusQuery AST and never executes arbitrary generated SQL.

Research compilation APIs belong to privileged admin/internal tooling, not the public runtime contract.

## 16. Product surfaces

The product is larger than one website.

Recommended product surfaces:

### Public Research App
Passage Study, Corpus Lab, published analyses, citations, construction browsing.

### Researcher Workspace
Saved queries, notes, draft translations, user semantic sets/rules.

### Editorial Console
Source registration, extraction review, claim review, rule review, translation decisions, release candidate inspection.

### Research Compiler Workers
Batch ingestion, extraction, AI-assisted mapping, construction compilation, rule evaluation, benchmark execution.

### Publication Console / Service
Release manifest, validation failures, release publish, supersede, rollback.

## 17. RAG and AI positioning

RAG is a tool in the Authoring/Research Plane.

It may assist with:

- candidate source discovery;
- source-span retrieval;
- claim extraction;
- concept mapping;
- cross-source comparison;
- disagreement discovery;
- commentary retrieval;
- benchmark generation.

The output remains candidate data until validated.

Gemini File Search, Notebook-style systems, OpenAI tools or another provider may be used as replaceable workbench components.

The canonical knowledge store remains the project's own database.

## 18. Embedding policy

Embeddings are disposable derived data.

Core public corpus search must not depend on embeddings.

Reasons:

- corpus membership requires deterministic predicates;
- embedding models can be replaced;
- embedding spaces can be incompatible across model generations;
- filtered ANN recall must be measured;
- private vector stores create additional rights/security concerns.

Embeddings remain useful for authoring-side discovery and optional published-literature discovery.

## 19. Product release versus software release

Keep these separate.

### Software release

Application code/API/UI version.

### Research release

Published scholarly/data state.

The same application version may serve different research releases.

A research release should record the Git commit and compiler version used to create it, but it must not be identified only by the software version.

## 20. Product-level rollback

Rollback should normally mean:

- switch active research release pointer to a previous published release;
- do not mutate the older release;
- preserve user workspace data;
- preserve audit log explaining the rollback.

Software rollback and research-data rollback are separate operations.

## 21. What is deliberately not required for initial launch

Do not block the first serving product on:

- complete processing of every book;
- complete commentary coverage for every biblical book;
- full LXX linguistic annotation;
- a graph database;
- runtime academic RAG;
- all user-created rule promotion workflows;
- generic optional-pattern semantics in the first DSL version.

The first launch should prove:

- publication firewall;
- release pinning;
- deterministic corpus search;
- selected high-quality published passage analyses;
- rights-safe evidence display;
- repeatable compilation.

## 22. Final product principle

The authoritative public answer path is:

```text
sources
  -> private research compilation
  -> reviewed structured evidence
  -> reviewed rules/decisions
  -> immutable research release
  -> deterministic serving product
```

Optional AI sits around this pipeline.

It must not replace it.


## 23. Research Pro experience layer

Research Pro is not a fifth product plane.

It is a feature-entitled Research experience rendered primarily from:

- PUBLIC_SERVING;
- USER_WORKSPACE;
- optional live Scholarly Discovery providers.

The canonical scholarly state remains the active ResearchRelease.

The detailed domain contract is:

- `architecture/research-pro-scholarly-intelligence.md`

The detailed UI/cross-stage contract is:

- `architecture/ui-mode-cross-stage-contract.md`

The accepted architecture decision is:

- `architecture/adr/004-research-pro-experience-layer.md`

Study and Research modes therefore share:

- reference identity;
- textual witnesses;
- published translation decisions;
- commentary identity;
- ResearchIssues;
- ResearchPositions;
- citations;
- ResearchRelease.

Research mode exposes additional depth rather than a different scholarly truth.

## 24. Scholarly discovery state

External live discovery is outside the immutable curated ResearchRelease until reviewed and published.

The product distinguishes:

- `CURATED_IN_RELEASE`
- `DISCOVERED_SINCE_RELEASE`

The latter may be displayed in Research mode as recent discovery.

It must not change:

- published commentary;
- translation decisions;
- issue/debate status;
- canonical literature review;

until a later authoring/review/publication cycle.

## 25. Entitlement versus rights

Product feature entitlement is resolved after source/content rights.

Conceptually:

```text
RightsPolicy
    ↓
ProductEntitlement
    ↓
Experience visibility
```

Research entitlement cannot reveal a source whose RightsPolicy prohibits that operation.

Conversely, a source may be legally displayable while a high-depth workflow remains a paid/limited product feature.

This distinction is mandatory across API, UI and server authorization.


## 23. Public runtime AI billing/auth model

Public runtime AI is strictly BYOK.

The product does not fund or centrally authenticate public Gemini/model usage.

Core product capability is independent of BYOK.

Optional runtime model features may require the user to supply a valid provider credential for the current session.

The product must not ship a shared provider secret or platform fallback credential.

Gemini is the first supported provider.

This requirement does not apply to private internal research-compilation credentials used by the product owner in the Authoring / Research Plane; those are separate private infrastructure and must never be embedded in the public application or exposed to public users.


## 24. Research Pro extension profile

Research Pro remains part of the same product and ResearchRelease.

Its engineering freeze state is tracked separately in `contracts/v1.1/profiles.json` and `contracts/v1.1/freeze-checklist.md` so Core Database Spike work is not blocked by later scholarly-intelligence surfaces.

This separation must never create a second ontology, database, commentary truth state, or ResearchRelease.
