# Database Spike 001: Scholarly Integrity Vertical Slice

Status: **IMPLEMENTATION IN PROGRESS — POSTGRESQL 17 EXECUTABLE HARNESS ADDED; REMOTE SUPABASE TARGET NOT YET DESIGNATED**

## 1. Purpose

This spike is not a schema-creation demo.

Its purpose is to test whether the current architecture can represent valid scholarly states and reject invalid states at the correct trust boundary using real PostgreSQL/Supabase constraints, transactions, RLS and deterministic queries.

Primary research path:

```text
Reference label + ReferenceSystem
  -> ReferenceSpan
  -> Hebrew DigitalExpression / TextStream / TextSegments
  -> CorpusRelease
  -> multiple AnnotationLayers
  -> SemanticSet
  -> normalized CorpusQuery + execution request
  -> ConstructionInstance
  -> scholarly/corpus evidence
  -> TranslationSourceBasis
  -> TranslationPolicyVersion
  -> TranslationDecision
  -> PublishedAssertion / PublishedEvidenceItem
  -> ResearchBuild
  -> publication validation
  -> inactive ResearchRelease
  -> Serving DB validation
  -> atomic PRODUCTION pointer move
  -> Study-mode passage read
```

1 Samuel 16:7 remains the primary vertical case because existing fixtures and scholarly work already exercise the translation-analysis domain. It is not sufficient as the only adversarial case.

## 2. Explicit non-goals

This spike does not:

- implement the whole UI;
- ingest the whole Hebrew Bible;
- finish Research Pro scholarly-provider integration;
- normalize millions of bibliographic records;
- implement full TEI;
- finalize every public API pagination/error contract;
- ship runtime AI;
- deploy production Vercel infrastructure.

## 3. Relational-integrity attacks

### 3.1 Annotation-layer integrity

Test that an AnalysisEdge cannot claim one AnnotationLayer while either endpoint node belongs to another layer.

Preferred database shape should prove same-layer membership, for example by composite uniqueness/FK or an equally enforceable relational design.

Attack:

- edge declares Layer A;
- from-node belongs Layer A;
- to-node belongs Layer B;
- INSERT must fail.

Apply the same principle to cross-annotation mappings where the mapping contract pins source/target framework/layer identities.

### 3.2 Analysis-node/text-context integrity

An AnalysisNode mapped to TextSegment must be compatible with the corpus release / digital expression / text stream being analysed.

Attack:

- node belongs CorpusRelease A;
- segment belongs unrelated DigitalExpression/CorpusRelease B;
- database or controlled compiler boundary must reject the mapping.

### 3.3 Alignment-stream integrity

AlignmentGroup pins source and target TextStream.

Attack:

- source stream is WRITTEN/Ketiv;
- source alignment member references a READ/Qere segment;
- insertion must fail.

Many-to-many alignment remains legal when all members belong to the pinned streams.

### 3.4 Reference integrity

At minimum prove:

- `reference_atoms(book_id, sequence)` uniqueness;
- ReferenceSpan start/end atoms are compatible;
- start sequence cannot be after end sequence;
- ReferenceLabel members have deterministic order;
- superscription / split / merged labels resolve through explicit ReferenceSystem.

### 3.5 Research-issue version compatibility

Attack:

- ResearchPositionVersion references ResearchIssue stable identity A;
- its `research_issue_version_id` belongs to stable ResearchIssue B;
- database insertion or publication validation must fail.

### 3.6 Translation reproducibility

Attack:

- official TranslationDecision without TranslationSourceBasis;
- official TranslationDecision without TranslationPolicyVersion;
- TranslationDecision passage locus is not contained within / covered by the pinned TranslationSourceBasis reference span;
- TranslationDecision target language differs from pinned TranslationPolicyVersion target language;
- source basis stream and source basis segments do not agree;
- apparatus-based basis names a reading outside the passage/locus;
- editorial/composite emendation lacks the actual adopted source reading text.

All invalid states must fail before publication.

## 4. Rights and evidence attacks

Test:

- no applicable rule -> default DENY;
- UNKNOWN_RESTRICTIVE -> DENY;
- same-specificity ALLOW and DENY -> DENY wins;
- CONDITIONAL with no typed condition or obligation -> reject;
- MAX_EXCERPT without unit -> reject;
- display permitted but persistence denied -> provider content is not copied into persistent public store;
- permitted public excerpt without rights snapshot -> publication reject;
- permitted public excerpt linked to a DENY snapshot, wrong operation, wrong audience/purpose, expired policy, or otherwise incompatible rights decision -> publication reject;
- RightsDecisionSnapshot winning rule not among applicable rules -> reject;
- IMMUTABLE_SNAPSHOT evidence without content hash -> publication reject.

## 5. Corpus-query attacks

Prove:

- one normalized query + same ResearchRelease + same dependency versions produces the same result set/hash;
- page 2 is requested through CorpusQueryExecutionRequest cursor rather than mutating query semantics;
- `pageMatchCount == len(matches)`;
- exact total is reported only when defensible;
- join expansion does not inflate construction/clause/reference counts;
- query execution policy enforces `defaultPageSize <= maxPageSize <= hardResultCap`;
- OSHB and a structurally different layer can coexist without universal phrase/clause identity.

## 6. RLS / authorization attacks

At minimum:

- User A cannot read User B private workspace project, draft translation, saved query or annotation;
- public runtime cannot read Authoring/private source tables;
- public role cannot call publication-only RPC/function;
- service/public views do not bypass intended RLS;
- ProductEntitlement cannot override RightsPolicy denial.

## 7. Publication visibility atomicity

When Authoring and Serving are physically/logically separate, do not attempt a fake cross-database global transaction.

Test the required guarantee:

1. materialize candidate release while inactive;
2. validate FK/projection/hash/rights parity;
3. inject failure before pointer move;
4. confirm current PRODUCTION remains unchanged;
5. retry successful publication;
6. move PRODUCTION pointer in one Serving-database transaction;
7. confirm clients observe complete old or complete new release, never partial new release;
8. prove that changing a TranslationDecision's source-basis identity changes the canonical published translation/analysis aggregate hash and therefore cannot remain hidden under the same release component hash.

Rollback moves a pointer and does not mutate historical release payload.

## 8. Adversarial scholarly fixtures

The spike must contain multiple assumption attacks, not only one happy-path verse:

1. 1 Samuel 16:7: main translation-analysis vertical slice;
2. Psalm superscription / alternate reference numbering;
3. Ketiv/Qere WRITTEN versus READ source basis;
4. Hebrew-Chinese many-to-many alignment;
5. OSHB versus structurally different MACULA/BHSA-style segmentation/layer;
6. textual variant requiring an explicit adopted reading;
7. incomplete semantic-set coverage;
8. provider display allowed but persistent storage denied;
9. project Chinese rendering that deliberately preserves source ambiguity;
10. invalid cross-layer AnalysisEdge;
11. invalid cross-stream alignment member;
12. publication failure before pointer movement;
13. cross-user RLS leakage attempt.

## 9. Required outputs

The spike should produce:

- real PostgreSQL migrations;
- constraint/index definitions;
- seed fixtures for the adversarial cases;
- pgTAP or equivalent SQL-level tests where suitable;
- RLS/grants/RPC tests;
- publication-worker transaction/failure tests;
- deterministic CorpusQuery compiler/execution test;
- query-plan/latency notes for the representative patterns;
- a spike review recording every contract assumption that failed or required modification.

## 10. Success criterion

Success is not "all tables CREATE successfully."

Success means:

> valid scholarly states are representable, invalid scholarly states are rejected at the correct trust boundary, and a release-pinned result can be reproduced from the stored dependencies.

Any load-bearing contract contradicted by PostgreSQL or real corpus data must be corrected before CORE_FREEZE_V1_1.


## 11. Executable implementation boundary

The first implementation round is intentionally executed against clean PostgreSQL 17 in GitHub Actions.

Reason:

- the connected Supabase account currently exposes one inactive, generically named project;
- the repository contains no Supabase project ref/link identifying that project as this product's target;
- Database Spike 001 must not write DDL to an arbitrary remote project.

Executable files:

- `database/migrations/001_database_spike_001.sql`;
- `database/spikes/001/00_bootstrap.sql`;
- `database/spikes/001/01_seed.sql`;
- `database/spikes/001/02_tests.sql`;
- `database/spikes/001/03_query_plan.sql`;
- `.github/workflows/database-spike-001.yml`.

The CI bootstrap creates only the Supabase-compatible roles and `auth.uid()` shim needed by plain PostgreSQL. Those are not production schema objects to recreate in a real Supabase project.

A green PostgreSQL job is implementation evidence, but it does not by itself prove Supabase Data API configuration, remote Auth/JWT behavior, advisor cleanliness, remote migration history, or production-scale performance.


### 11.1 First independent implementation-review finding

The initial one-database migration allowed several `serving.*` objects and the deterministic corpus-query function to reference `authoring.*` directly. That was relationally valid in one PostgreSQL instance but contradicted the stronger product invariant that Public Serving must continue when Authoring is unavailable.

The spike therefore corrects the implementation boundary:

- Serving has its own release-visible research-object registry;
- Serving has its own reference-span projection;
- Serving has release-pinned corpus node/feature/edge/mapping and semantic-set-member projections;
- public deterministic corpus queries read only those Serving projections;
- public evidence/release component FKs terminate in Serving-owned registries;
- TranslationDecision aggregate hashing is a Publication Control operation, not a public Serving runtime operation;
- CI inspects PostgreSQL catalog metadata to reject any Serving FK or Serving function that reaches back into Authoring.

This is a contract clarification derived from implementation evidence, not merely an implementation refactor.
