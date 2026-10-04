# Database Spike 001: Scholarly Integrity Vertical Slice

Status: **POSTGRESQL 17 EXECUTABLE HARNESS PASS; REMOTE SUPABASE TARGET NOT YET DESIGNATED**

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

## 1.1 Pinned real-corpus inputs

Database Spike 001 now has concrete upstream inputs rather than placeholder corpus labels.

Machine authority:

- `contracts/v1.1/corpus-source-registry.json`.

Initial pins:

- OSHB/morphhb commit `3d15126fb1ef74867fc1434be1942e837932691f`;
- BHSA frozen dataset version `2021`, fetched from repository commit `4db00e2157915495e1a4d3d57e41223df24775da`;
- ETCBC bridging dataset `2021`, repository commit `324598bb3f9cb3a36543e77ac61e4b0f77addf82`.

Bootstrap and provider-scoped export tooling:

- `scripts/corpora/fetch_sources.py`;
- `scripts/corpora/export_oshb_words.py`;
- `scripts/corpora/export_bhsa_features.py`;
- `scripts/corpora/build_candidate_crosswalk.py`.

The source-adapter smoke proves acquisition, provider-scoped export and conservative OSHB/BHSA crosswalk behavior against the pinned data. WB-0 adds a second, independent clean-PostgreSQL job that imports the bounded real 1 Samuel 16:7 exports into Authoring while the original synthetic adversarial job remains intact. The WB-0 job is accepted only when exact-head CI proves the real relational assertions. It remains a canary, not whole-Bible ingestion evidence.

The spike must preserve the source roles defined in `architecture/corpus-source-integration.md`: OSHB is the initial morphology/morpheme baseline; BHSA phrase/clause/syntax stays framework-scoped; ETCBC bridging is derived comparison/mapping evidence; project SemanticSetVersion remains the authority for project-curated semantic classes.

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

The spike must also prove the complementary case exposed by real BHSA 2021 data: an annotation-only BHSA node may exist with provider identity, lexeme/POS/features and phrase/clause graph membership while having zero orthographic segment memberships. The database must allow that state without inventing a TextSegment, and orthographic cross-layer mapping must not treat that node as text-bearing.

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
- pinned OSHB morphology/morpheme layers and pinned BHSA 2021 phrase/clause layers can coexist without universal phrase/clause identity;
- a mixed OSHB + project SemanticSetVersion + BHSA clause query cannot execute without an explicit compatible cross-layer mapping;
- candidate crosswalk output remains non-canonical until reviewed/imported through the typed cross-annotation mapping boundary; any unresolved verse must not be guessed into a match.

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
- pinned source manifests / SHA-256 evidence for the OSHB, BHSA and bridging inputs used;
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

WB-0 specifically succeeds only if the real canary preserves the exact pinned provider counts/identity, the two evidenced BHSA annotation-only nodes, phrase/clause graph membership, project BODY_PART authority, bridging comparison features, and grouped non-canonical OSHB/BHSA mapping evidence. A successful WB-0 does **not** satisfy `CORE-FZ-WB-002`; WB-1 still requires the same importer design to be generalized and audited across the complete configured corpus.


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
- `database/spikes/001/04_real_corpus_tests.sql`;
- `scripts/corpora/load_wb0_postgres.py`;
- `.github/workflows/database-spike-001.yml`.

The workflow has two independent PostgreSQL jobs. The controlled-fixture job protects the broad adversarial integrity surface. The WB-0 job starts from another blank database, fetches the pinned real corpus sources, loads only the 1 Samuel 16:7 relational canary, and proves the real-provider invariants without writing a public Serving corpus projection.

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


## 12. Independent final critical review after Serving isolation

A green SQL harness is not sufficient by itself. After Serving/Authoring separation passed, a separate read-only review found further defects that were not covered by the earlier tests:

1. Workspace child rows could claim User A ownership while referencing User B's project because RLS checked the child owner but no composite FK tied project and owner.
2. Shared-PK subtype rows only proved that a research-object ID existed, not that its `object_type` matched the subtype table.
3. `citation_locator` was only checked as generic JSON rather than the locator-specific `CitationLocatorV1` contract.
4. A PUBLISHED ResearchRelease could still receive late release-payload/projection inserts from privileged publication code.
5. The first PUBLISHED event and production channel-pointer move were not created by one publication transaction.
6. The spike pagination cursor used UUID order rather than release-pinned canonical textual/reference order.
7. Repeated automated history updates duplicated and partially corrupted the Database Spike CHANGELOG entry.

The implementation now:

- uses composite `(project_id, owner_user_id)` Workspace FKs;
- enforces expected `research_objects.object_type` for every shared-PK subtype exercised by the spike;
- validates locator-specific CitationLocator requirements in PostgreSQL;
- locks release-owned payload and component projections after PUBLISHED;
- creates the first PUBLISHED event and channel-pointer move inside the same publication function transaction;
- orders deterministic results by a publication-projected canonical reference sort key plus stable ID;
- consolidates the Database Spike history into one chronological CHANGELOG entry.

These corrections must pass a new blank PostgreSQL 17 run before this review is considered closed.


## 13. PostgreSQL 17 verification result

Database Spike 001 reached a clean end-to-end PostgreSQL 17 run on PR #9.

Exact-head evidence:

- Database Spike 001 run `37195991129`: PASS;
- Project governance run `37195991176`: PASS;
- Contract validation run `37195991128`: PASS.

The database job passed, in order:

1. PostgreSQL client/runtime check;
2. migration transaction-boundary static guard;
3. Supabase-compatible test-role/bootstrap shim;
4. blank-database migration;
5. controlled fixture load;
6. adversarial SQL tests;
7. representative `EXPLAIN (ANALYZE, BUFFERS)` query-plan probe.

### 13.1 Proven by this executable spike

Within the PostgreSQL 17 / Supabase-compatible relational boundary, the spike now demonstrates:

- reference atom/span order and alternate multi-atom label integrity;
- shared-PK subtype registration/type enforcement;
- independent annotation layers and rejection of cross-layer AnalysisEdge misuse;
- analysis-node/text-segment corpus-expression compatibility;
- explicit cross-layer mapping;
- WRITTEN/READ stream separation and stream-pinned many-to-many alignment;
- exact ResearchPositionVersion -> ResearchIssueVersion compatibility;
- TranslationSourceBasis stream/locus integrity;
- TranslationDecision source-basis coverage and target-language/policy consistency;
- fail-closed default rights evaluation and same-specificity DENY precedence;
- rights winning-rule subset integrity;
- public evidence rejection for wrong operation, wrong subject, invalid CitationLocator, and missing immutable content hash;
- Workspace cross-user RLS isolation plus relational project/owner integrity;
- public/authenticated denial of Authoring and publication-only operations;
- no Serving foreign key or Serving runtime function dependency on Authoring;
- anonymous current-release and corpus-query reads while the Authoring schema is temporarily unavailable by name;
- immutable published release/component/payload projections;
- publication failure before pointer movement leaves PRODUCTION unchanged;
- successful first publication appends PUBLISHED and moves the channel pointer atomically;
- rollback is a later channel-pointer move rather than mutation of historical release payload;
- deterministic release-pinned corpus-query membership and stable canonical-reference cursor behavior;
- representative PostgreSQL query-plan execution.

### 13.2 Not proven by this result

A green PostgreSQL run does not prove:

- that the inactive connected Supabase project is the intended deployment target;
- remote Supabase migration history or schema parity;
- Supabase Auth/JWT behavior beyond the compatible `auth.uid()` contract;
- Supabase Data API exposure/grants;
- Supabase security/performance advisor cleanliness;
- production-scale whole-Bible corpus latency;
- full CorpusQuery AST/compiler coverage or exact-total API semantics;
- real OSHB/MACULA/BHSA ingestion and mapping correctness;
- complete Ketiv/Qere/textual-apparatus modelling;
- FHL/provider production identity/rights behavior;
- every CORE_FREEZE_V1_1 or RESEARCH_PRO_EXTENSION_V1_1 gate.

Therefore this result closes the **local executable PostgreSQL vertical slice**, not the entire v1.1 freeze and not remote Supabase deployment.
