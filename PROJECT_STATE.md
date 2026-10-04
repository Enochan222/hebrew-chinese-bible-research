# Project State

Status: **MANDATORY LIVING REPOSITORY STATE**
State Revision: **2026-10-05.1**

## Mandatory governance rule

Every push/PR that changes this repository must:

1. read `PROJECT_CHARTER.md`;
2. read this `PROJECT_STATE.md`;
3. read `architecture/manifest.json` and the latest `CHANGELOG.md` entry;
4. update this file to reflect the post-change repository state;
5. append/update `CHANGELOG.md` with what changed, why, intended effect, and validation;
6. run required validation before merge/push.

`PROJECT_CHARTER.md` is the stable product constitution. This file is the current operational/architectural state and therefore changes on every push.

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
- the source smoke has **not** yet loaded these real OSHB/BHSA exports into the merged PostgreSQL Database Spike 001 schema; that relational real-corpus ingestion remains the next integration gate.

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
- the canonical v1.1 release-pointer, passage-core and experience-capabilities fixture chain is runtime-validated before rendering;
- the UI visibly labels all data as fixture/non-production and does not claim database-backed passage content;
- application/features depend on domain ports/services rather than fixture adapter implementations;
- no PostgreSQL/Supabase/ORM/auth/cloud SDK, migration, publication worker, CorpusQuery, translation workbench or annotation storage is introduced;
- scoped npm lint uses a deterministic source/import/SQL/dependency boundary scanner rather than a framework lint preset, minimizing transitive tooling surface;
- the rich PassageExperience projection remains deliberately unfrozen;
- DB-0 remains responsible for real relational constraints, RLS/grants, ReferenceSystem resolution against persisted data, ResearchRelease/channel persistence and publication visibility atomicity.

This is fixture-shell implementation evidence only. It does not satisfy real-database CORE_FREEZE gates or complete Phase 1.

## Current implementation priority

1. Preserve contract/governance consistency and the whole-Bible scope guard.
2. Complete WB-0: import the pinned real OSHB/BHSA/ETCBC-bridging 1 Samuel 16:7 acceptance canary into the merged PostgreSQL schema without promoting unreviewed mappings.
3. Complete WB-1/WB-2: run the same importer across the complete configured Hebrew Bible, produce auditable coverage/exception evidence, and serve it through release-pinned passage APIs.
4. Complete WB-3: replace fixture-only Hebrew passage content with a database-backed whole-Bible reader and navigation.
5. Complete WB-4/WB-5: add selected translation witnesses, alignment/comparison, project/user translation workflow and deterministic whole-corpus analysis.
6. Only then make Research Pro provider adapters, ResearchModelAdapter and end-to-end literature builds the primary product implementation frontier; academic enrichment may proceed in parallel where it does not block the base path.

## Latest push intent

Realign implementation sequencing with the product's already-declared whole-Hebrew-Bible scope. The repository now has an explicit Whole-Bible Base Product authority, scope guard for agents, whole-Bible Core freeze gates and a Phase 2A corpus/reader milestone ahead of Phase 2B translation workbench and later Research Pro depth. Existing 1 Samuel 16:7 / other passage fixtures remain valuable acceptance vectors, but they no longer risk being read as the product scope. No database schema, source pin, rights rule, ResearchRelease semantic or runtime feature is changed by this architecture/roadmap correction.
