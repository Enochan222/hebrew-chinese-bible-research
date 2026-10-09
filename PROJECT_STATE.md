# Project State

Status: **MANDATORY LIVING REPOSITORY STATE**
State Revision: **2026-10-10.1**

## Mandatory governance rule

Every push/PR that changes this repository must:

1. read `PROJECT_CHARTER.md`;
2. read this `PROJECT_STATE.md`;
3. read `architecture/manifest.json` and the latest `CHANGELOG.md` entry;
4. update this file to reflect the post-change repository state;
5. append/update `CHANGELOG.md` with what changed, why, intended effect, and validation;
6. run required validation before merge/push.

`PROJECT_CHARTER.md` is the stable product constitution. This file is the current operational/architectural state and therefore changes on every push.

## Current project AI execution policy

GitHub Copilot is not authorized for this repository's project work.

- do not request Copilot pull-request review;
- do not use Copilot Coding Agent, Autofix, Chat/code generation, or any operation that consumes Copilot quota/premium requests;
- do not treat Copilot output as merge or acceptance evidence;
- AI-assisted implementation, analysis, repository orchestration and code review are performed through the project's ChatGPT workflow;
- deterministic GitHub Actions and ordinary non-AI GitHub features remain allowed;
- an exception requires an explicit repository-owner policy change through the governed PR path.

Machine authority: `contracts/v1.1/github-ai-usage-policy.json`.

The repository owner reported on 2026-10-05 that GitHub account-level automatic Copilot code review was disabled. Repository metadata does not expose that user-level toggle, so this is recorded as owner-reported rather than independently verified.


## What this project is

A database-backed, research-grade whole-Hebrew-Bible to Chinese translation research product.

It combines:

- passage-centred Hebrew textual/linguistic study;
- deterministic whole-corpus research;
- Chinese translation-witness comparison;
- reviewed project Chinese rendering and translation decisions;
- structured academic knowledge compilation;
- multi-provider scholarly literature discovery;
- Research Pro literature/debate/commentary surfaces;
- immutable, citable ResearchRelease publication;
- optional public BYOK AI without a platform-funded model key.

## Why it exists

The product is intended to make Chinese Hebrew-Bible translation decisions inspectable and defensible. It must show the textual, corpus, grammatical, lexical, textual-critical, scholarly, translation-witness, counterevidence, and rights/provenance basis of a conclusion rather than outputting an unexplained AI translation.

## Current scholarly database-build method

The project now formally adopts the Sacred Studies-derived research method defined in `architecture/sacred-studies-research-method.md`.

Core method:

- Text × Topic × Lens research matrix;
- concise English academic query optimization using standard book names and academic terminology;
- seminal/all-era coverage plus rolling recent-scholarship emphasis;
- academic-source prioritization and non-academic exclusion;
- zero-hallucination bibliography rule;
- multi-provider discovery via OpenAlex, Semantic Scholar, CORE, Crossref, and Scite;
- curated Google Drive research library used as mandatory private scholarly base;
- model-neutral ResearchModelAdapter for query expansion, triage, claim extraction, counterevidence planning, and synthesis;
- research dossier -> candidate claims -> ResearchIssue/ResearchPosition -> LiteratureSnapshot;
- independent critical review with 88/100 authoring threshold and maximum 3 revision attempts;
- human/review/publication gates before ResearchRelease.

## Pastoral Studio production-runtime method verification

A real production Academic Biblical Study run against the deployed Pastoral Studio showed that its scholarly retrieval path executes multi-source retrieval before Librarian/Writer synthesis. The observed production flow included Sefaria, Scite, CORE, OpenAlex, Crossref, Open Library / Internet Archive, followed by a Librarian model stage and later synthesis. CORE demonstrated explicit degraded-mode fallback when authentication failed.

The repository therefore treats Pastoral Studio production behavior, not the earlier static-helper assumption, as the lineage reference for retrieval orchestration.

The Hebrew-Chinese Bible project adopts that method but strengthens it with canonical Work/Edition identity, DiscoveryRecord provenance, multi-provider deduplication, RightsPolicy, access-level truth, counterevidence, LiteratureSnapshot, human review, and immutable ResearchRelease publication.

Semantic Scholar remains part of this project's required first implementation as a deliberate coverage extension even though it was not observed in that specific Pastoral Studio runtime test.

See `architecture/pastoral-studio-runtime-scholarly-rag.md`.

## Current contract-closure state

The 2026-10-03 independent contract-closure panel has accepted a deliberately bounded set of changes before Database Spike 001:

- human passage labels resolve through an explicit ReferenceSystem to canonical ReferenceSpan identity;
- corpus query meaning is separated from pagination state through CorpusQueryExecutionRequest;
- result pages distinguish page count from defensible exact total count;
- official project TranslationDecision pins an immutable TranslationSourceBasis and exact TranslationPolicyVersion;
- TranslationPolicy reuses existing RuleVersion infrastructure instead of creating a second rule engine;
- passage-level TranslationSourceBasis is sealed through published translation/analysis aggregates rather than emitted as one top-level release component per passage;
- rights snapshots fail closed, use typed conditions/obligations, and cannot resolve to UNKNOWN;
- CitationLocator has locator-specific required identity;
- public excerpts require rights snapshots and immutable evidence requires content hashes;
- ResearchPositionVersion pins exact ResearchIssueVersion framing;
- publication across Authoring/Serving guarantees atomic visibility by inactive materialization plus an atomic Serving pointer move, not a fictional distributed ACID transaction;
- Database Spike 001 now attacks cross-layer, cross-stream, cross-issue-version, translation-policy, rights, RLS, query and publication invariants.

Deliberately deferred rather than added to the Core closure patch:

- large bibliographic ontology redesign;
- full API-wide pagination/error ontology;
- OCR ontology expansion;
- full TEI modelling;
- another BYOK architecture layer;
- Research Pro provider-scale production normalization.

Live repository governance is now enforced and independently verified. The active `Protect main` ruleset requires pull requests, strict `contracts` and `state-and-changelog` checks, linear history, review-thread resolution, and blocks deletion/force-push without any bypass actors.

## Latest live repository-governance audit

Re-verified on 2026-10-04 against live GitHub repository metadata.

Current audited main:

- `3d2dc4d8f07b67f3be44f9fedc69a60acb775405`;
- produced by merged PR #6 rather than a direct push;
- PR #6 head passed `contracts` and `state-and-changelog`;
- post-merge main also passed both workflows.

The active `Protect main` ruleset remains:

- active on the default branch;
- PR-required;
- required approvals = 0;
- review-thread resolution required;
- squash-only;
- strict latest-main status checks required;
- `contracts` and `state-and-changelog` required from GitHub Actions;
- deletion and force-push blocked;
- linear history required;
- bypass actors empty.

A recent protected-main history audit verified PR provenance for PR #4, #5, and #6. No bypass evidence was found.

Repository visibility remains public as observed state; this audit does not change visibility.

## Current architecture state

- `PROJECT_CHARTER.md` is canonical product intent.
- `PROJECT_STATE.md` is mandatory living state and must change every push.
- `CHANGELOG.md` is mandatory push history.
- `architecture/manifest.json` controls active/superseded/historical authority.
- Core Database Spike 001 is permitted by current Core gates.
- Full Core freeze remains pending implementation evidence.
- Research Pro remains the same product/truth model with a separate maturity gate.
- Multi-provider scholarly discovery is mandatory for Research Pro/database compilation.
- Public runtime AI remains BYOK-only and Gemini-first, but private database-build ResearchModelAdapter is vendor-neutral.
- Public passage rendering remains release-pinned and does not depend on live academic providers.
- Human-readable passage labels resolve through an explicit ReferenceSystem to canonical ReferenceSpan identity.
- Official project TranslationDecision pins an immutable TranslationSourceBasis and exact TranslationPolicyVersion.
- Corpus query execution separates scholarly query meaning from cursor/page retrieval state and distinguishes exact from unavailable total counts.
- RightsDecisionSnapshot is fail-closed: unresolved/unknown permission cannot surface as an UNKNOWN final outcome or ALLOW.
- Public evidence uses typed CitationLocator semantics whose required identity cannot be null or empty; excerpts require rights snapshots and immutable evidence requires content hashes.
- Passage-scoped rule-application MCP reads use the shared ReferenceSystem-aware PassageLocator contract rather than an ambiguous bare reference string.
- ResearchPositionVersion pins the exact ResearchIssueVersion framing used for that scholarly position.
- Database Spike 001 is specified as an adversarial scholarly-integrity vertical slice, not a table-creation demo.
- `main` is live-protected by active repository ruleset `Protect main` (ID `24409248`).
- `REPO-GOV-001`, `REPO-GOV-002`, and `REPO-GOV-003` are PASS in the canonical freeze checklist.
- Normal changes require PR + latest-main synchronization + `contracts` PASS + `state-and-changelog` PASS + resolved conversations + squash merge.
- Panel contract-closure adjudication is recorded in `architecture/reviews/2026-10-03-panel-contract-closure.md` and registered as current validation authority.

## Current product execution boundary

The product baseline is now explicitly the **whole Hebrew Bible**, with academic intelligence layered on top.

- 1 Samuel 16:7 and other named passages are acceptance/edge-case fixtures, not content scope;
- the next corpus milestone is real relational ingestion followed by a whole-corpus load and coverage audit, not manual passage-by-passage expansion;
- the whole-Bible reader must become database-backed before Research Pro depth is treated as the primary implementation frontier;
- selected translation witnesses, comparison/alignment and project/user translation form the next base-product layer after Hebrew corpus serving;
- deterministic Corpus Lab capability belongs to the base scholarly product;
- Research Pro literature/debate/commentary enrichment may be progressive by target and must not block base passage availability;
- missing academic coverage is an explicit availability state, never an invitation to synthesize unreviewed scholarship from model memory.

Authority: `architecture/whole-bible-base-product.md`.

## Current pinned Hebrew corpus integration

The first corpus-source adapter integration intended for Database Spike 001 is now machine-pinned and reproducible:

- OSHB/morphhb commit `3d15126fb1ef74867fc1434be1942e837932691f` is the initial text/word/lemma/morpheme/morphology baseline;
- BHSA frozen dataset `2021`, fetched from repository commit `4db00e2157915495e1a4d3d57e41223df24775da`, is an independent framework-scoped phrase/clause/syntactic annotation source;
- ETCBC bridging `2021`, commit `324598bb3f9cb3a36543e77ac61e4b0f77addf82`, is 2021-derived morphology-comparison evidence on BHSA word nodes and is not assumed to map the current OSHB pin's provider word IDs;
- project SemanticSetVersion remains the authority for project-curated semantic categories such as BODY_PART;
- upstream corpus data is downloaded on demand into gitignored `.local/corpora/`, never vendored as the repository's canonical data; cache manifests bind source pin, registry schema, acquisition method/path set, exact file set, byte counts and SHA-256, and any mismatch fails closed;
- BHSA local cache is now required to contain every feature referenced by its pinned `otext.tf` formats and section configuration; the fetcher rejects incomplete caches before Text-Fabric loading;
- source exact Unicode is preserved; OSHB source identity is not NFC-normalized;
- provider book-name aliases are normalized only for passage filtering/candidate comparison; emitted provider reference labels remain source-native and canonical project passage identity still resolves through ReferenceSystem/ReferenceSpan;
- live 1 Samuel 16:7 smoke evidence shows OSHB and BHSA do not share 1:1 tokenization (25 OSHB word records versus 34 BHSA word records);
- a conservative candidate crosswalk compiler therefore proposes contiguous many-to-many span mappings only when normalized verse identity and concatenated consonantal signatures agree; mismatch is `NEEDS_REVIEW`, and automatic canonical promotion is forbidden;
- source pins never auto-advance and every upstream change requires reviewed PR, corpus diff, spike rerun and a new ResearchBuild/ResearchRelease;
- OSHB public serving defaults to attribution-compatible use under its upstream terms;
- BHSA public/commercial serving requires an explicit RightsDecision;
- bridging-derived public serving is denied until its mixed upstream rights are reviewed;
- WB-0 now has a dedicated clean-PostgreSQL real-corpus canary path: exact pinned 1 Samuel 16:7 OSHB/BHSA/bridging exports are loaded into Authoring, with provider identity, BHSA phrase/clause graph membership, annotation-only nodes and grouped non-canonical cross-framework candidates asserted relationally; this remains bounded canary evidence and is not whole-Bible WB-1 coverage.

See `architecture/corpus-source-integration.md` and `contracts/v1.1/corpus-source-registry.json`.

## Current data/research boundaries

- Google Drive: curated private scholarly source base, subject to operation-specific rights.
- OpenAlex/Semantic Scholar/CORE/Crossref/Scite: required external scholarly discovery/evidence ensemble.
- Sefaria and Open Library / Internet Archive: auxiliary source-specialized retrieval routes where relevant and rights-permitted.
- PostgreSQL/Supabase-style relational storage: canonical structured database.
- Object storage: permitted source assets/extractions.
- GitHub: code/contracts/migrations/docs/tests, not copyrighted source corpora. Current repository visibility is public and is recorded as observed state, not changed by this update.
- Vercel/public app: stateless serving layer for compiled scholarship.

## Current non-negotiables

- whole Hebrew Bible long-term scope;
- research-grade Hebrew-to-Chinese focus;
- deterministic corpus evidence;
- assertion-level provenance;
- counterevidence first-class;
- no invented citations or translator intention;
- no source-taxonomy flattening;
- rights before storage/model/publication;
- immutable/versioned ResearchRelease;
- no public shared/fallback model API key;
- no academic-provider keys in source control;
- provider IDs never become canonical Work IDs;
- build-time model vendor may change without ontology change.

## Current open decisions

- exact Chinese translation witness launch list;
- final provider for each translation witness;
- final production/public-serving mix of OSHB/MACULA/BHSA layers after real-corpus relational evidence and BHSA/MACULA rights review; the initial OSHB/BHSA/bridging source pins and roles are fixed in the corpus source registry;
- commercial provider licences/quotas for Scite/CORE/Semantic Scholar where applicable;
- final Research Pro rollout sequence;
- final entitlement/pricing model;
- detailed visual system within scholarly UX constraints.

## Phase 1 fixture serving-shell implementation state

P1-VS-001A–F introduces the first executable public-serving shell under `apps/web` as a deliberately fixture-backed implementation boundary.

Current bounded state:

- Next.js App Router + strict TypeScript is used for the fixture serving shell only; this does not select a cloud provider or database platform;
- current passage navigation resolves the fixture PRODUCTION ResearchRelease once and redirects to a citation-stable pinned-release route;
- pinned passage reads never re-resolve the current release;
- Study and Research mode switching preserves the same ResearchRelease, human reference and ReferenceSystem;
- human reference labels and ReferenceSystem codes are opaque contract values; the fixture shell validates presence but does not impose OSIS-only syntax before deterministic resolution;
- the canonical v1.1 release-pointer, passage-core and experience-capabilities fixture chain is runtime-validated before rendering;
- the UI visibly labels all data as fixture/non-production and does not claim database-backed passage content;
- application/features depend on domain ports/services rather than fixture adapter implementations;
- no PostgreSQL/Supabase/ORM/auth/cloud SDK, migration, publication worker, CorpusQuery, translation workbench or annotation storage is introduced;
- scoped npm lint uses a deterministic source/import/SQL/dependency boundary scanner rather than a framework lint preset, minimizing transitive tooling surface;
- the rich PassageExperience projection remains deliberately unfrozen;
- DB-0 remains responsible for real relational constraints, RLS/grants, ReferenceSystem resolution against persisted data, ResearchRelease/channel persistence and publication visibility atomicity.

This is fixture-shell implementation evidence only. It does not satisfy real-database CORE_FREEZE gates or complete Phase 1.

## WB-0 real-corpus relational canary state

WB-0 is implemented as an independent PostgreSQL 17 job alongside the existing synthetic Database Spike:

- fetch exact immutable OSHB/morphhb, BHSA 2021 and ETCBC bridging pins;
- export real 1 Samuel 16:7 provider records;
- build the conservative grouped OSHB/BHSA candidate crosswalk;
- load the canary with `scripts/corpora/load_wb0_postgres.py`;
- preserve 25 OSHB word nodes and 34 BHSA word nodes as provider-scoped AnalysisNodes;
- preserve BHSA nodes `150439` and `150445` with zero invented TextSegments and with phrase/clause graph membership;
- preserve bridging morphology as comparison features on BHSA nodes, not current OSHB provider-ID identity;
- keep project BODY_PART SemanticSetVersion separate from provider lexical features;
- store 25 span candidates as grouped Authoring mappings so 1:n/n:1/n:m evidence is not flattened into false pairwise equivalence;
- enforce `CANDIDATE_AUTOMATED` plus `canonical=false` and reject accidental candidate promotion;
- run a real multi-layer OSHB morphology -> explicit grouped mapping -> BHSA BODY_PART/clause relational query;
- first real execution loaded successfully and observed 22 BHSA phrase nodes, 7 clause nodes, 90 graph-membership edges, 35 bridging feature values and 7 non-1:1 mapping groups in addition to the pinned 25/34 word counts;
- the first assertion run exposed a test-boundary defect rather than a data-model failure: wrong-layer membership was correctly rejected by the earlier span/layer trigger before PostgreSQL reached the expected composite FK; the negative test now accepts only those two intended rejection boundaries;
- write no real BHSA/bridging corpus projection into Serving because public/commercial rights remain unresolved.

WB-0 implementation acceptance is now PASS on the reviewed PR head: the original synthetic `postgres-spike` regression and the independent `wb0-real-corpus-canary` job both completed successfully, alongside Contract validation, Project governance, Corpus source smoke and the P1 shell regression. The protected merge remains the repository publication action for this change. This PASS is bounded to the pinned 1 Samuel 16:7 canary and does not satisfy `CORE-FZ-WB-002`. WB-1 remains responsible for generalizing this importer and producing complete configured-corpus coverage/error evidence.

## WB-CORPUS-001 source-foundation state

This revision introduces the whole-corpus source/build boundary that WB-1 must consume:

- full OSHB and BHSA export modes are explicit through `--all`; canary/debug execution remains `--reference`;
- an independent `OSHB_OSIS` reference inventory is scanned directly from the exact pinned OSHB source XML/source manifest rather than inferred from exporter success;
- the inventory is labelled as a source-derived bootstrap ReferenceSystem snapshot, not final CanonSystem adjudication;
- the conservative OSHB/BHSA crosswalk runs across the complete provider exports and keeps candidate mappings non-canonical;
- recognized annotation-only BHSA nodes remain explicit even when another node in the same reference forces that reference into unresolved review;
- the deterministic coverage manifest records pins, reference-set hash, provider/reference counts, annotation-only/mapping counts, unresolved reasons, per-book diagnostics, explicit provider gaps and artifact hashes;
- silent reference loss is a build failure;
- provider book-division counts are diagnostic provenance only, not a fixed 39/24 completeness criterion;
- no PostgreSQL, Serving projection or ResearchRelease is written by WB-CORPUS-001.

The dedicated whole-Bible workflow is the executable acceptance authority for this source foundation. Its first exact-head execution completed the full corpus build successfully and observed 23,213 selected-reference spans, 306,785 OSHB word records, 426,590 BHSA word nodes, 287,216 candidate span mappings, 1,138 explicitly unresolved references and zero silent reference loss. The generated manifest returned `gatePass=true` and `COMPLETE_WITH_EXPLICIT_EXCEPTIONS`. That run then failed only in the separate schema-validation step because the workflow had installed corpus dependencies but not the repository's pinned `jsonschema` validator. The workflow now installs both `requirements-corpus.txt` and `requirements-contracts.txt` and also runs on relevant pushes to `main`, so validation is repeated after merge. WB-0's exact 1 Samuel 16:7 export shape/hashes remain regression evidence; the new BHSA `--all` mode does not change the canary record shape.

## WB-1 relational whole-corpus implementation state

WB-1 is now implemented as a relational consumer of WB-CORPUS-001 rather than a competing second whole-source build.

Current review-branch implementation:

- selected navigation/relational CanonSystem `TANAKH_OSIS_39` is machine-declared and contract-validated;
- source completeness remains anchored to the independent WB-CORPUS-001 `OSHB_OSIS` ReferenceSystem inventory, not to the CanonSystem's book count;
- accepted WB-CORPUS-001 OSHB/BHSA/crosswalk artifacts are hash-verified and partitioned per configured book only to bound memory and database transactions;
- exact source provider-book codes are reconciled to the selected CanonSystem before import;
- PostgreSQL now implements `canon_systems` / `canon_books`;
- AnalysisNode/TextSegment integrity is generalized from WB-0 exact-span equality to same-expression, same-book span containment;
- synthetic SQL regression proves a multi-atom AnalysisNode accepts contained verse-local members and rejects an out-of-span segment;
- each book imports transactionally with PostgreSQL COPY;
- all OSHB and BHSA provider word records must remain represented as provider-scoped AnalysisNodes;
- BHSA TextSegments are created only where source text is present; reviewed annotation-only and other empty-source states remain explicit in the audit;
- BHSA phrase/clause provider nodes, features, range spans, direct segment memberships and graph edges are retained;
- grouped cross-framework candidates remain `CANDIDATE_AUTOMATED` and non-canonical;
- unresolved cross-framework references are carried as explicit research exceptions and are not counted as silent source-ingestion loss;
- relational counts are reconciled per book/framework/node type back to the source-foundation artifacts and selected reference inventory;
- any missing configured source division, duplicate provider identity, OSHB source-surface loss, importer failure or database/source parity drift fails the WB-1 gate;
- real BHSA/bridging-derived rows remain absent from Serving in WB-1;
- `.github/workflows/wb1-relational-whole-corpus.yml` rebuilds WB-CORPUS-001, imports the relational corpus and uploads the machine-auditable WB-1 report.

WB-1 acceptance is **PASS** for `CORE-FZ-WB-002`. The synchronized implementation head `6ec515067f05a901667e4d1f783329f0ee46a53a` passed the complete pinned-source relational workflow and every independent regression gate. Machine evidence reconciles 39/39 configured books, 23,213 selected/reference atoms, 306,785 OSHB words, 426,590 BHSA words, 253,203 BHSA phrases, 88,131 BHSA clauses, 1,106,383 graph-membership edges, 469,484 bridging feature values, 287,216 grouped candidate mappings, 6,409 reviewed annotation-only BHSA nodes and 79 explicit unclassified empty-source BHSA nodes. It reports zero missing configured books, provider-ID duplicates, importer errors, source/database parity failures, OSHB missing-surface records or real-corpus Serving rows. The 1,138 unresolved cross-framework references exactly match WB-CORPUS-001 and remain explicit research/mapping exceptions rather than silent source-record drops.

## Current implementation priority

1. Preserve contract/governance consistency, the ChatGPT-only project AI policy and the whole-Bible scope guard.
2. Treat WB-2/WB-3 and RL-1 as accepted infrastructure and preserve their exact-head regression suites.
3. Implement Issue #32 as the single WB-4 DB-1 frontier: normalized provider identity, synthetic/right-safe release-compiled translation witnesses, exact RightsDecisionSnapshot linkage, RLS/RPC and lifecycle immutability.
4. Keep `CORE-FZ-TRANS-002` PENDING until the database projection and runtime/reader evidence pass; do not publish any real copyrighted translation merely because provider delivery exists.
5. After WB-4 DB-1, wire the reader comparison surface and then implement many-to-many Hebrew-Chinese alignment.
6. Complete WB-5 deterministic whole-corpus analysis after the WB-4 serving/alignment boundary is proven.
7. Only then make Research Pro provider adapters, ResearchModelAdapter and end-to-end literature builds the primary product implementation frontier; academic enrichment may proceed in parallel where it does not block the base path.

## RL-1 release lifecycle hardening acceptance

PR #28 established the lifecycle split between permanent ever-published immutability and current public servability. Post-merge adversarial review then found three release-keyed CORPUS Serving projections that were still missing the permanent component mutation guard: `serving.reference_labels`, `serving.corpus_text_segments` and `serving.corpus_node_segments`. Issue #25 was therefore reopened and PR #30 hardens the actual compiled projection boundary before WB-4 publication work expands Serving.

Accepted PR #30 behavior:

- `guard_component_projection('corpus_release_id')` protects every current Serving table carrying `corpus_release_id`, including reference labels, text segments, node/segment memberships, nodes, features, edges and mappings;
- a catalog-level regression fails when a future `serving` table with `corpus_release_id` lacks the permanent component guard;
- explicit post-REVOKED mutation attacks against reference labels, Hebrew text segments and node/segment membership fail;
- the real whole-Bible OSHB Serving release is exercised through PUBLISHED -> REVOKED -> REACTIVATED;
- REVOKED removes current and pinned public serving without reopening historical payload mutability;
- explicit REACTIVATED plus channel reassignment restores Gen.1.1 serving;
- the active database/API contract now uses canonical `eventSequence` ordering and enumerates the immutable CORPUS Serving projection surface.

PR #30 implementation head `cedeaa20baa90284fa9f063ef3f1ced943ca7061` passed Database Spike `37669525047`, WB-2/WB-3 `37669525095`, WB-1 `37669524878`, Whole-Bible corpus foundation `37669524970`, P1 fixture shell `37669524947`, Contract validation `37669525237` and Project governance `37669524996`.

The synchronized PR #30 head `6573807a7cd199847f70ea42d54f584809f84601` independently passed Database Spike `37671312879`, WB-2/WB-3 `37671312984`, WB-1 `37671312895`, Whole-Bible corpus foundation `37671312907`, P1 fixture shell `37671312868`, Contract validation `37671312863` and Project governance `37671312967`.

`CORE-FZ-RELEASE-002` is **PASS** on that evidence. PR #30 still requires the merge-resolved head, which also contains merged PR #29 WB-4 contract work, to remain green before merge. Issue #25 remains open until PR #30 is merged and `main` is verified.

## WB-4 DB-1 translation Serving candidate state

Issue #32 is now the single active WB-4 database frontier. Overlapping Issue #31 has been closed as a duplicate so provider identity and translation publication are not developed as parallel truths.

Current candidate implementation:

- adds normalized `authoring.providers` and `authoring.provider_distributions`, with every ProviderDistribution bound to one exact DigitalExpression;
- records coverage separately from provider observation/delivery;
- models SNAPSHOT_PINNED versus LIVE_EXTERNAL storage semantics without granting rights from provider availability;
- adds release-compiled `serving.translation_witnesses` and `serving.translation_witness_segments` with no runtime dependency on Authoring;
- requires exact DigitalExpression public-display rights and exact ProviderDistribution storage rights before persisted translation text may enter Serving;
- fails closed on wrong subject, operation, purpose, audience, commercial scope, unresolved conditional rights, missing storage permission or unhashable persisted segments;
- exposes current and release-pinned translation witness RPCs resolved through the release's corpus ReferenceSystem/ReferenceSpan;
- keeps non-displayable states segment-empty;
- preserves RL-1 revocation/public-servability and permanent post-publication immutability;
- uses only the existing synthetic Chinese spike text for executable acceptance. No real copyrighted translation content is added.

`database/migrations/002_wb4_translation_serving.sql` and `database/spikes/001/06_translation_witness_tests.sql` are the current executable candidate. `CORE-FZ-TRANS-002` remains **PENDING** until exact-head Database Spike, WB-1, WB-2/WB-3, whole-Bible, contract/governance and relevant app regressions pass.

## WB-4 contract-first implementation state

PR #29 remains contract-first and contains no real copyrighted translation publication.

The public witness contract is now designed to survive the next database/alignment frontier without changing field meaning:

- TranslationWitnessList pins ResearchRelease, canonical ReferenceSpan and resolved ReferenceSystem identity;
- each witness identifies TextualWork, optional TextualEdition and exact DigitalExpression rather than treating provider code as translation identity;
- displayed witness text is an ordered array of content-hashed TextSegments with stable TextStream/TextSegment IDs suitable for later many-to-many alignment;
- coverageStatus, deliveryStatus and displayStatus are independent;
- DISPLAYABLE requires covered + delivery-ready + at least one segment;
- rights-restricted, metadata-only, stale, provider-error, not-retrieved, uncovered and unknown-coverage states expose zero text segments;
- each witness carries the display RightsDecisionSnapshot ID and provenance ID;
- ProviderWitnessBinding remains delivery/storage mechanics and now requires observation hash/time plus an explicit providerVersion field, which may be null if the provider supplies none;
- `SNAPSHOT_PINNED` additionally requires a non-null SHA-256 `snapshotContentHash`; a null hash is rejected because a persisted release snapshot must remain verifiable.
- `LIVE_EXTERNAL` may not carry a non-null `snapshotContentHash`; live observations can expose observed hashes but must not masquerade as immutable persisted snapshots.
- duplicate DigitalExpression witnesses and non-contiguous segment order are semantic contract failures;
- all fixtures remain synthetic and do not assert that any real Chinese translation is licensed or selected.

`CORE-FZ-TRANS-002` is **PENDING** until a real PostgreSQL Serving projection, rights/RLS/RPC path and reader/alignment implementation pass exact-head regression evidence.

## WB-2 / WB-3 implementation state

WB-2/WB-3 is accepted on PR #23 exact head `21a2cedafb394b84d51e244de6ff37bbac4d6a82` for the whole-Bible base-reader gates.

Current branch implementation includes:

- complete canonical `obligationType` rights payload validation across all current v1.1 RightsCondition and obligation variants;
- a rights-safe OSHB-only Serving projection compiled from the accepted WB-1 Authoring corpus;
- a release-pinned ResearchRelease and atomic PRODUCTION publication path;
- Serving ReferenceSystem/label, text-segment, node, feature and membership projections for the complete accepted OSHB corpus;
- a `serving.read_passage_core` RPC returning real release-pinned Hebrew word tokens, basic OSHB morphology, attribution and data-driven navigation;
- a real Book / Chapter / Passage selector derived from the Serving ReferenceSystem, plus previous/next traversal, without hard-coded React book arrays;
- PostgREST Serving adapters behind the existing ReleaseReadPort / PassageReadPort boundary, while fixture adapters remain a regression mode;
- runtime AJV validation of external Serving passage/release/capability payloads so TypeScript casts cannot bypass canonical machine contracts;
- conditional PassageCore validation requiring complete Hebrew/tokens/navigation/attribution fields for `dataSource=SERVING`;
- hostile malformed-Serving-response regression that must fail closed as `CONTRACT_VIOLATION`;
- explicit non-exposure of BHSA and ETCBC bridging rows in public Serving.

Exact-head machine evidence is complete. WB-2/WB-3 Serving Reader run `37424398827` passed whole-corpus rebuild/parity, rights-safe OSHB publication, anon RLS public passage reads, 39-book navigation, Genesis 50-chapter and 31-passage indexing, Gen.50.26 -> Exod.1.1 cross-book traversal, non-fixture Isa.6.1 retrieval, OSHB-only public Serving and evidence upload. P1 fixture shell validation `37424398799` passed typecheck, lint/boundaries, unit, integration, fixture E2E, Serving visual E2E and production build. WB-1 `37424398811`, Whole-Bible corpus foundation `37424398932`, Database Spike 001 `37424398816`, Contract validation `37424398834` and Project governance `37424398970` all passed on the same head.

`CORE-FZ-WB-001` and `CORE-FZ-WB-003` are now **PASS**.

## WB-4 immutability review companion

A separate review-fix branch protects two load-bearing DB-1 guarantees while PR #34 is being updated in parallel. `serving.rights_decision_snapshots` entries referenced by staged translation witnesses cannot be UPDATEd or DELETEd. Translation rows check the original and the destination release on every UPDATE, closing the relocation case in which the generic guard checked only NEW.release_id.

SQL acceptance tests must reject mutation/deletion of compiled display/storage decisions and migration of published witness/segment rows into an unpublished release. This is an implementation candidate, not completed acceptance. No actual copyrighted Chinese translation data is added.

## Latest push intent

Harden WB-4 DB-1 exact-release integrity before merge. Although the previous exact head passed all seven workflows, independent review found that a valid ProviderDistribution and operation-scoped RightsDecisionSnapshot did not prove a translation witness belonged to the chosen ResearchRelease. The compiler now also requires the exact DigitalExpression in that ResearchRelease's TRANSLATION_WITNESS components, the canonical ReferenceSpan in its pinned CORPUS component, and a matching component/snapshot content hash for DISPLAYABLE text. Three adversarial candidates prove rejection of missing translation component, missing pinned corpus, and inconsistent snapshot hash. A separate forged-hash regression now requires compiler-time recomputation of SHA-256 from each persisted UTF-8 translation segment; a correctly shaped hash that disagrees with its text fails closed. These invariants do not add any real copyrighted translation data. The first CI run on the digest hardening failed during PostgreSQL migration because a JavaScript string replacement token truncated the SQL regex/function body. The complete function was restored using callback-safe replacement. A second CI run then identified a duplicated SQL suffix after the first COMMIT from the same earlier replacement token; the 6 KB duplicate tail is now removed. Database Spike now statically verifies the full function body, exactly one COMMIT, and no trailing SQL after COMMIT before applying the migration. CORE-FZ-TRANS-002 remains PENDING until repaired exact-head CI and merge verification complete. 
