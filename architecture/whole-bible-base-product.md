# Whole-Bible Base Product Architecture

Status: **ACTIVE PRODUCT EXECUTION AUTHORITY**

This document fixes the implementation scope and ordering of the public Hebrew-Bible product. It does not replace the canonical data model, ResearchRelease model, rights model, corpus-source contract, or Research Pro contract.

Read with:

- `PROJECT_CHARTER.md`;
- `architecture/corpus-source-integration.md`;
- `architecture/database-api-cross-stage-contract-v1.1.md`;
- `architecture/site-build-staging-plan.md`;
- `architecture/ui-mode-cross-stage-contract.md`;
- `architecture/research-pro-scholarly-intelligence.md`.

## 1. Product baseline

The base product is a **whole-Hebrew-Bible digital research edition**, not a collection of passage demos and not an academic-RAG product with a Bible viewer attached.

Whole-Bible coverage is the baseline product scope.

The base product should eventually let a user navigate the canonical Hebrew Bible and, for every ingested passage, inspect the release-pinned Hebrew text and the deterministic linguistic data available for that passage. Where rights and launch coverage permit, the same passage experience also exposes translation witnesses, translation comparison, project translation decisions and user translation workspace state.

Research Pro is an academic overlay on this base. It is not a prerequisite for the base passage to exist or render.

## 2. Base product capability stack

The implementation dependency order is:

```text
whole-Bible reference coverage
  -> pinned Hebrew text / textual streams
  -> word / morpheme / morphology
  -> framework-scoped phrase / clause / syntax
  -> release-pinned passage API
  -> whole-Bible reader/navigation
  -> translation witnesses
  -> Hebrew-to-translation alignment and comparison
  -> project/user translation workflow
  -> deterministic corpus/construction analysis
  -> academic / Research Pro overlay
```

The base product therefore includes, as coverage becomes available:

- book/chapter/verse or equivalent ReferenceSystem-aware navigation across the whole Hebrew Bible;
- Hebrew textual witness data and stable ReferenceSpan identity;
- word and morpheme inspection;
- morphology;
- framework-scoped phrase/clause/syntax without inventing universal phrase or clause identity;
- selected Chinese translation witnesses and other permitted comparison witnesses;
- translation-difference and alignment views;
- reviewed project Chinese rendering / TranslationDecision where available;
- user translation workspace;
- deterministic Corpus Lab and construction evidence;
- release, provenance, rights and evidence metadata.

The base product must remain usable when:

- Research Pro has no dossier for the passage;
- live scholarly providers are unavailable;
- no BYOK model credential is supplied.

## 3. Academic overlay

Academic enrichment is progressive.

ResearchIssue, ResearchPosition, LiteratureSnapshot, LiteratureReviewSnapshot, CommentaryEntry and live scholarly discovery attach to canonical native targets such as passage, book, lexeme or construction.

A passage with no compiled academic dossier still belongs to the whole-Bible base product.

The public product must distinguish:

- base passage data available;
- academic material available in the current ResearchRelease;
- academic material not yet compiled/reviewed;
- source access restricted;
- temporary provider/runtime failure.

It must never fill a missing scholarly dossier with model-memory prose and present that as reviewed scholarship.

Academic depth may increase passage by passage or target by target across later ResearchReleases without reducing whole-Bible base coverage.

## 4. Fixture policy

Passage-specific fixtures are **acceptance vectors**, not product scope.

Examples:

- 1 Samuel 16:7 exercises OSHB/BHSA segmentation disagreement, annotation-only BHSA nodes and many-to-many cross-framework mapping;
- Psalm superscription / Psalm 3:1-style cases exercise ReferenceSystem, superscription and alternate-versification behavior;
- a Ketiv/Qere fixture exercises WRITTEN/READ streams and alignment-stream pinning.

A fixture may prove an invariant before full-corpus execution.

Passing a fixture never proves whole-Bible coverage.

No production importer, API route, navigation model, release compiler or UI may be hard-coded so that these fixture passages define the available corpus.

## 5. Whole-corpus ingestion pipeline

The intended corpus path is:

```text
immutable upstream pin
  -> bounded fetch
  -> source-manifest integrity verification
  -> provider-scoped export
  -> relational import
  -> explicit cross-framework mappings
  -> whole-corpus QA / coverage report
  -> release-scoped serving projection
  -> ResearchRelease
  -> public passage API / reader
```

The current 1 Samuel 16:7 corpus smoke is the first importer/crosswalk canary.

Once the relational importer passes that canary, the next acceptance target is not another hand-picked passage. It is a whole-corpus import and coverage audit.

## 6. Whole-Bible coverage evidence

A whole-Bible claim requires corpus-level evidence rather than representative screenshots.

At minimum, acceptance evidence must record:

- canonical book coverage for the selected CanonSystem;
- ReferenceSystem/reference-label coverage;
- per-book and aggregate source record counts;
- imported TextSegment / AnalysisNode counts by source/framework;
- passages or nodes intentionally excluded, with reason;
- unresolved cross-framework mappings separately from source-ingestion failures;
- annotation-only nodes separately from missing text;
- duplicate/stale provider identities;
- importer errors and retries;
- deterministic hashes/version pins for the imported source release;
- serving/API traversal checks across the corpus rather than only one fixture.

Known upstream irregularities may be represented as explicit reviewed exceptions.

They must not be silently dropped to make a nominal 100% figure.

## 7. Execution milestones

### WB-0: relational importer canary

Import the pinned real OSHB/BHSA/bridging data needed for the established 1 Samuel 16:7 canary into the Database Spike schema.

Prove the database preserves:

- provider identity;
- framework scoping;
- annotation-only nodes;
- non-canonical candidate mappings;
- release pinning;
- fail-closed mapping/query behavior.

### WB-1: whole-Bible corpus load

Run the same importer across the complete configured Hebrew-Bible source coverage.

Machine configuration:

- CanonSystem contract: `contracts/v1.1/hebrew-bible-canon-system.json`;
- current code: `TANAKH_OSIS_39`;
- source pins remain those in `contracts/v1.1/corpus-source-registry.json`.

Produce a machine-auditable coverage/error report.

The WB-1 importer is book-bounded so one source irregularity cannot require holding the entire corpus in memory. Each book imports transactionally. Coverage evidence must distinguish:

- source-ingestion failure;
- provider record retained without an orthographic TextSegment;
- reviewed annotation-only node;
- unresolved cross-framework mapping;
- explicit source-only or framework-only reference address.

Only source-ingestion parity, duplicate identity, configured-book coverage and database reconciliation are load-bearing for `CORE-FZ-WB-002`. Cross-framework disagreement may remain unresolved if it is explicitly reported and no source record is silently discarded.

### WB-2: whole-Bible release-pinned passage serving

Serve the ingested corpus through ReferenceSystem-aware, ResearchRelease-pinned passage APIs.

Prove navigation and reads are not fixture-bound.

### WB-3: whole-Bible reader

Replace fixture-only passage content with database-backed Hebrew passage rendering and navigation while retaining visible provenance/release state.

### WB-4: translation-witness base

Add selected permitted Chinese/ancient/reference witnesses, many-to-many alignment, comparison and project/user translation workflows.

Coverage is tracked per witness and must not be inferred from provider availability.

### WB-5: deterministic analysis base

Enable whole-corpus morphology/syntax/construction/query workflows over the same release-pinned data.

### WB-6: academic enrichment

Add scholarly discovery, literature review, debate/position graphs, commentary and other Research Pro modules as overlays on canonical targets.

Academic enrichment may be sparse at first; base passage serving may not be.

## 8. Architectural guardrails

This execution clarification does not weaken existing invariants:

- ResearchRelease remains the publication boundary;
- rights remain operation-specific and fail closed;
- OSHB/BHSA/MACULA-style annotation frameworks remain distinct;
- cross-framework mappings remain explicit;
- provider IDs remain external identities;
- AI output remains non-canonical until reviewed;
- public runtime AI remains optional and BYOK-only;
- historical releases remain immutable.

The purpose of this document is to prevent implementation order from accidentally turning a whole-Bible product into a passage-demo or research-provider-first product.
