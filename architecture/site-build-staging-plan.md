# Product Build Staging Plan

## Global BYOK requirement

Every public runtime AI feature is BYOK-only, with Gemini as the first supported provider.

No build phase may add a shared model-provider credential to source code, environment variables, database, deployment secrets, fixtures, or fallback configuration.

The user-supplied provider credential is volatile in-memory runtime input only and must never be persisted or logged.

Core research functionality must pass acceptance tests with no BYOK credential present.

See `architecture/byok-credential-handling.md` and ADR-005.

Status: **ACTIVE STAGING PLAN; DATABASE SPIKE MAY PROCEED AFTER CORE_SPIKE_V1_1, FULL PRODUCT FREEZE REMAINS SEPARATE**

This project is a database-backed scholarly product platform, not a single runtime AI application.

Implementation phases are separate from the continuous product planes defined in:

- `architecture/product-platform-and-publication-model.md`
- `architecture/research-pro-scholarly-intelligence.md`
- `architecture/ui-mode-cross-stage-contract.md`

The product planes are:

1. Authoring / Research
2. Publication / Control
3. Public Serving
4. User Workspace

These continue to exist after launch. They are not one-time stages.

Implementation must follow the canonical product intent in `PROJECT_CHARTER.md`.

Database Spike 001 may begin when `CORE_SPIKE_V1_1` passes. Full Core freeze, Research Pro extension freeze, and public BYOK shipping remain separate gates:

- `contracts/v1.1/freeze-checklist.md`
- `architecture/database-api-cross-stage-contract-v1.1.md`

Canonical vocabularies:

- `contracts/v1.1/vocabulary.json`

## Governing build principle

The public scholarly product must primarily serve:

- compiled research releases;
- deterministic corpus search;
- published translation data;
- published analysis;
- approved rules and rule applications;
- citations and provenance.

Runtime AI/RAG is supplementary.

The core product must still work when no LLM provider is available.

The current Vercel application remains a reference implementation for useful interaction patterns, not an ontology or data-model authority.

---

# Phase 1: Product Foundation, Identity, Release Model, and Serving Shell

## Goal

Create the stable product shell and database contracts without introducing false canonical Hebrew segmentation.

## Product surfaces reserved from the beginning

### Public Research App
Two coordinated experience modes share one ResearchRelease:

- Study
- Research

Shared product areas include:
- Passage Study
- Corpus Lab
- Construction Browser
- Published Analysis
- Citations / Evidence

Research mode may expose additional scholarly-intelligence modules according to ProductEntitlement.

### Researcher Workspace
- saved queries
- draft translations
- annotations
- user semantic sets
- user rule drafts

### Editorial Console
Initially minimal/placeholder, but route and authorization boundaries must exist.

### Publication Console
Initially minimal/placeholder, but release state and current-release visibility must exist.

## Data contracts

Phase 1 must establish:

- BiblicalBook
- CanonSystem
- ReferenceSystem
- ReferenceAtom
- ReferenceSpan
- TextualWork
- TextualEdition
- DigitalExpression
- ProviderDistribution
- TextStream
- TextSegment
- SourceRegistry
- Provenance
- RightsPolicy
- ResearchBuild
- ResearchRelease
- ResearchReleaseComponent
- ResearchProject / workspace ownership
- ProductFeature / ProductEntitlement interface
- ExperienceMode / ExperienceCapabilities contract
- PassageExperienceCoreV1

Important correction:

TextStream/TextSegment must exist before Phase 2 because translation alignment requires stable segment identifiers.

Phase 1 still must **not** create universal application-owned Hebrew word/phrase/clause identity.

## Publication boundary

Implement the conceptual distinction:

```text
authoring candidate
    -> publication validation
    -> published release
    -> serving
```

The first phase may use fixture releases, but every public fixture response should already be release-pinned.

## UI

Reconstruct the useful passage workflow:

- book/chapter/verse navigation;
- deep link;
- MT witness;
- LXX witness placeholder or selected data;
- variable Chinese translation witnesses;
- published project rendering / suggested translation where available;
- proposed user translation workspace;
- analysis tab;
- syntax/corpus tab;
- source/citation tab.

Fixture data must be labelled.

## Security

- no service-role key in browser;
- public runtime has no authoring-DB credential;
- product plane is explicit in server modules;
- public/private/workspace schemas or logical boundaries are testable;
- source text is untrusted data, never instruction.

## Acceptance gate

Pass only when:

- release-pinned passage rendering works;
- text-expression identity is independent of provider code;
- stable text segments exist for later alignment;
- user workspace data is not mixed with published research;
- no UI component requires universal canonical phrase/clause IDs;
- research-release identifier is visible/debuggable.

---

# Phase 2: Published Passage Data, Translation Witnesses, Alignment, and Workspace

## Goal

Turn Passage Study into a research-grade published translation workbench.

## Provider identity

Use dynamic version discovery where possible.

Preserve:

```text
Textual Work
  -> Edition/Revision when established
    -> Digital Expression
      -> Provider Distribution
```

A provider code is never sufficient proof of print-edition identity.

## Translation witness contract

Each witness reports independently:

- provider/distribution;
- work/edition/expression;
- rights/display state;
- retrieval timestamp/version;
- provenance;
- loading/error state.

One provider failure must not fail the whole passage page.

## Alignment

Use:

- alignment group;
- source segment members;
- target segment members;
- relation type;
- method;
- algorithm version;
- confidence;
- review status;
- provenance.

Raw offsets are secondary locators only and must include coordinate basis and text revision hash.

## Project rendering

Support a distinct reviewed/versioned project Chinese rendering or suggested translation when available.

It must remain separate from:

- external Chinese translation witnesses;
- the user's private translation draft.

A project rendering must be linked to a TranslationDecision and published through ResearchRelease rather than generated ad hoc on page load.

## User workspace

Implement:

- versioned user translation proposals;
- annotations;
- saved passage state;
- saved comparison settings.

These are private workspace objects and must not become official published research automatically.

## Published analysis placeholder

Phase 2 may serve reviewed fixture PublishedPassageAnalysis objects.

It must not synthesize new official analysis at page load.

## Acceptance gate

Pass only when:

- source/target segments support many-to-many alignment;
- provider identity and translation identity remain separate;
- user draft data is isolated from official translation data;
- translator intention is never inferred as documentary fact;
- passage page can be rendered entirely from a pinned research release plus workspace state.

---

# Phase 3: Hebrew Corpus Engine, Semantic Sets, Constructions, and Deterministic Search

## Goal

Build the research-grade corpus query engine.

This is the main dynamic scholarly engine of the public product.

## Canonical source versus serving projection

Canonical source layer:

- corpus release;
- annotation framework;
- analysis nodes;
- analysis edges;
- source-specific features;
- cross-framework mappings.

Serving/query layer:

- serving_words;
- serving_morphemes;
- serving_relations;
- serving_semantic_memberships.

Serving projections are release-scoped compiler outputs.

## Corpus relations

### Text-stream relations

- IMMEDIATELY_PRECEDES
- PRECEDES
- FOLLOWS
- WITHIN_N_SEGMENTS
- SAME_REFERENCE_SPAN

### Framework-scoped morphology/structure relations

- MORPHEME_OF
- HAS_MORPHEME
- PREFIX_MORPHEME_OF
- SUFFIX_MORPHEME_OF
- SAME_PHRASE
- SAME_CLAUSE
- SAME_SENTENCE
- ATTACHED_TO
- GOVERNS
- DEPENDENT_OF
- SEMANTIC_ROLE

A prefixed ל must be queryable as a morpheme without pretending it is an independent orthographic word.

## CorpusQuery AST

Required in the first serious query version:

- typed nodes;
- typed relations;
- pinned corpus/framework context;
- normalization profile;
- semantic-set version;
- ALL_OF;
- ANY_OF;
- NOT;
- EXISTS;
- NOT_EXISTS;
- MIN_COUNT / MAX_COUNT / EXACT_COUNT.

A generic OPTIONAL operator is deferred until match enumeration/count semantics are specified.

## Complexity guard

No arbitrary SQL from an LLM.

The query planner enforces configurable limits such as:

- max pattern nodes;
- max relation depth;
- max candidate/result count;
- timeout;
- permitted relation combinations.

Exact values are benchmark-driven.

## Semantic sets

Official semantic sets are versioned compiled research data.

Examples:

- BODY_PART
- PERCEPTION_VERB
- SPEECH_VERB
- KINSHIP
- LOCATION

Membership stores evidence/reason/review.

Runtime LLM classification does not modify official membership.

## ConstructionDefinition

A named formal pattern uses the same CorpusQuery AST.

Compile important constructions against pinned corpus releases.

Store ConstructionInstances with:

- node bindings;
- reference span;
- match explanation;
- review status;
- result hash.

## Search modes

### Visual Pattern Builder
No LLM required.

### Advanced DSL
No LLM required.

### Natural Language
Optional language-to-AST adapter.

The optional adapter cannot execute SQL directly and cannot decide result membership.

## Explainability

Each match exposes:

- why matched;
- bound nodes;
- matched features;
- relation evidence;
- framework/release;
- semantic-set version.

Where practical also support "why did expected verse not match?"

## Acceptance gate

Pass only when:

- same AST produces stable results;
- GUI and API AST are equivalent;
- morpheme-host search works;
- exact versus framework-complete versus heuristic candidate results are explicit;
- counts are not inflated by joins;
- semantic-set version is pinned;
- known construction definitions can be compiled and checked;
- core search works with LLM integration disabled.

---

# Phase 4: Private Academic Knowledge Compiler and Publication Pipeline

## Goal

Build the authoring-side scholarly compiler and Scholarly Intelligence layer.

This phase processes the user's academic library and other legitimate research sources.

It is **not** a public runtime chatbot/RAG endpoint.

## Research Pro scholarly-intelligence scope

Phase 4 owns:

- ScholarlyDiscoveryProvider abstraction;
- external DiscoveryRecords;
- bibliographic resolution;
- ScholarlyTargetLinks;
- ResearchIssues;
- ResearchPositions;
- LiteratureSnapshots;
- SourceAccessRoutes;
- editorial review of issue/position/debate structures.

External discovery results remain candidate/non-canonical until publication.

## Source inventory

Use:

- `docs/master-academic-source-inventory-and-gaps.md`

The Drive library is the acquisition/source library.

It is not the production query database.

## Ingestion model

Preserve:

```text
Work
  -> Edition
    -> SourceAsset
      -> SourceAssetPage
        -> SourceSpan
```

Then derive:

- claims;
- definitions;
- rules;
- qualifications;
- exceptions;
- examples;
- concept mappings;
- biblical-reference links;
- lexeme links;
- scholarly dependency;
- textual-critical structures.

## Claim integrity

Distinguish:

- DIRECT_QUOTE
- HUMAN_PARAPHRASE
- AI_EXTRACTED_PROPOSITION

AI-extracted propositions are candidate representations until reviewed.

A real citation that does not entail the claim is an academic failure.

## Source-type specialised processing

### Grammar
Preserve author-native terminology, rules, qualifications and examples.

### Lexica
Preserve source-specific sense inventories.

### Commentary
Passage-first structure.

### Textual criticism
Preserve raw apparatus before parsed interpretation.

### Chinese translation documentation
Preserve translation project, revision, preface and translator/publisher documentation separately from observed translation behaviour.

## AI/RAG tools

May include replaceable tools such as:

- internal hybrid retrieval;
- Gemini File Search;
- Notebook-style research workspaces;
- OpenAI-assisted extraction;
- batch model jobs;
- embeddings.

These are build tools, not canonical databases.

Google Gemini File Search currently imports/chunks/indexes sources and supports custom metadata filtering; this makes it useful for candidate discovery, not a replacement for the project's typed scholarly store.

## Review

Editorial console must support review of:

- document structure;
- citation location;
- extracted claims;
- claim-source entailment;
- concept mappings;
- examples;
- rule evidence;
- rights;
- publication eligibility.

## Publication compiler

A build produces:

- approved claims;
- approved mappings;
- approved citations;
- approved semantic-set updates;
- approved rules;
- approved textual-critical structures;
- public-safe excerpts;
- published analysis candidates;
- serving projections;
- release manifest.

## Publication firewall

Reject release candidate if:

- restricted/private text would leak;
- private Drive URL would leak;
- rights operation denies publication/model use;
- unreviewed mandatory item remains;
- citation missing or broken;
- benchmark gate fails;
- release component hash mismatches;
- serving projection is inconsistent with canonical source data.

## Acceptance gate

Pass only when:

- at least one representative source of each supported class can be processed;
- duplicate file does not create duplicate scholarly vote;
- rights filtering precedes publication;
- raw and derived scholarly layers remain separate;
- benchmark/evaluation is repeatable;
- ResearchBuild can become a CANDIDATE ResearchRelease;
- failed candidate does not modify the serving database.

---

# Phase 5: Rules, Published Analyses, Optional AI Adapter, Product Operations, and Full QA

## Goal

Complete the compiled scholarly product, Research Pro serving experience, and release operations.

## Rule system

Keep separate:

```text
ConstructionDefinition
  -> ConstructionInstance
  -> RuleVersion
  -> RuleApplication
  -> TranslationDecision
  -> PublishedPassageAnalysis
```

A corpus match is not a translation conclusion.

Official rule kinds:

- LINGUISTIC_HEURISTIC
- TRANSLATION_POLICY
- PASSAGE_OVERRIDE
- EDITORIAL_CONVENTION

Rule trigger reuses construction/query semantics.

## Build-time rule execution

Rules marked as compilable and having clear corpus scope may be evaluated across the pinned corpus during ResearchBuild.

Do **not** blindly run every editorial/passsage-specific rule across the entire Bible.

Only rules whose trigger/conditions have defined deterministic scope are materialized globally.

## Research Pro publication and serving

Phase 5 owns:

- LiteratureReviewSnapshots;
- CommentaryEntries and CommentarySections;
- StudyPassageProjectionV1;
- ResearchPassageProjectionV1;
- feature entitlement enforcement;
- debate/evidence graph serving;
- live `DISCOVERED_SINCE_RELEASE` literature surface;
- Research export/citation workflows;
- Study/Research cross-mode QA.

Study and Research must use the same active ResearchRelease.

Study must retain minimum evidence transparency even where Research features are not entitled.

## Published analysis

Serve:

- approved analysis;
- supporting evidence;
- opposing evidence;
- qualifications;
- counterexamples;
- uncertainty;
- citations.

Do not regenerate canonical analysis from private academic books at page load.

## Optional runtime AI

Primary initial use:

- natural-language-to-CorpusQuery AST.

Possible later non-canonical uses:

- explain a user's ad-hoc search;
- help compare a private user translation;
- explore published/open literature.

Any such output is clearly labelled as non-canonical and does not modify published research.

## Product operations

Implement:

- current research release pointer;
- release history;
- supersede;
- revoke;
- rollback;
- release manifest verification;
- user-workspace migration compatibility;
- software-version/research-release compatibility matrix;
- audit log.

## Public API emphasis

Core:

- current release;
- passage;
- translations;
- published analysis;
- rule applications;
- construction instances;
- query validate/run;
- evidence/citation.

Optional:

- query interpret.

Private compiler endpoints remain admin/internal.

## Full QA

Include:

- Hebrew RTL/bidi;
- Unicode normalization;
- Ketiv/Qere reading streams;
- versification/reference mapping;
- translation/provider identity;
- many-to-many alignment;
- corpus-framework scoping;
- morpheme-host relations;
- Boolean/negation query semantics;
- count integrity;
- semantic-set pinning;
- construction compilation;
- rule application;
- citation entailment;
- rights leakage;
- publication firewall;
- RLS/views/RPC;
- prompt injection;
- release rollback;
- stale projections;
- workspace isolation;
- responsive layout;
- no clipping/overlap.

## Final acceptance gate

The public product is ready only when:

- a complete sample ResearchBuild can be validated and published;
- public serving can be rebuilt from release components;
- public runtime has no authoring credentials;
- a release can be rolled back without losing user workspace data;
- deterministic corpus search remains functional without LLM;
- one optional natural-language query compiles to AST and yields exactly the same results as manually supplied AST;
- published analysis is release-pinned and auditable.

---

# Implementation rule for all phases

Every implementation prompt must state:

> Continue modifying the existing project. Do not rebuild or replace the product. Preserve prior working functionality and active architecture contracts. Do not introduce new canonical ontology, rights semantics, query relations, rule kinds, release states or evidence classes outside the canonical vocabulary without an explicit architecture revision.

After each phase:

1. inspect repository diff;
2. run schema/contracts tests;
3. run phase acceptance tests;
4. rerun earlier regressions;
5. update architecture docs if implementation exposes a genuine mismatch;
6. commit a distinct checkpoint;
7. do not deploy to Vercel unless explicitly requested.

Suggested checkpoints:

- `build-01-product-foundation`
- `build-02-passage-translations`
- `build-03-corpus-search`
- `build-04-research-compiler`
- `build-05-product-release`

The research compiler continues operating after Phase 5. It is a permanent product subsystem, not a bootstrap stage.


## Security acceptance tests added to every AI-capable phase

- no shared Gemini/model credential exists in source/config/deployment;
- no environment fallback is present;
- BYOK credential is absent from localStorage/IndexedDB/cookies;
- BYOK credential is absent from server logs and error telemetry;
- refresh/sign-out/Forget key clears volatile credential state;
- invalid BYOK cannot trigger a platform fallback key;
- non-AI research functions remain available without BYOK;
- CI secret scan blocks likely model-provider secret leakage.
