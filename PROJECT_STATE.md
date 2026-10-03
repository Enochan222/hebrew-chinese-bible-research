# Project State

Status: **MANDATORY LIVING REPOSITORY STATE**
State Revision: **2026-10-03.8**

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

## Important Sacred Studies audit finding

The current Sacred Studies repository contains useful search prompts, Librarian/Writer/Reviewer method, provider UI/config, and some provider helper implementations, but not all provider helpers are fully wired into its main generation path.

This project therefore preserves the **full intended research method** and completes the provider aggregation path, while rejecting dead-code, credential, stale-date, and auto-pass defects.

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
- Public evidence uses typed CitationLocator semantics; excerpts require rights snapshots and immutable evidence requires content hashes.
- ResearchPositionVersion pins the exact ResearchIssueVersion framing used for that scholarly position.
- Database Spike 001 is specified as an adversarial scholarly-integrity vertical slice, not a table-creation demo.
- `main` is live-protected by active repository ruleset `Protect main` (ID `24409248`).
- `REPO-GOV-001`, `REPO-GOV-002`, and `REPO-GOV-003` are PASS in the canonical freeze checklist.
- Normal changes require PR + latest-main synchronization + `contracts` PASS + `state-and-changelog` PASS + resolved conversations + squash merge.
- Panel contract-closure adjudication is recorded in `architecture/reviews/2026-10-03-panel-contract-closure.md` and registered as current validation authority.

## Current data/research boundaries

- Google Drive: curated private scholarly source base, subject to operation-specific rights.
- OpenAlex/Semantic Scholar/CORE/Crossref/Scite: external discovery/evidence providers.
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
- final production mix/releases of OSHB/MACULA/BHSA layers;
- commercial provider licences/quotas for Scite/CORE/Semantic Scholar where applicable;
- final Research Pro rollout sequence;
- final entitlement/pricing model;
- detailed visual system within scholarly UX constraints.

## Current implementation priority

1. Preserve contract/governance consistency.
2. Database Spike 001 for real PostgreSQL/Supabase schema and constraints.
3. Implement provider adapters and ResearchModelAdapter interfaces.
4. Validate one end-to-end literature-discovery build against a real Hebrew-Bible ResearchIssue.
5. Continue later application stages without weakening publication/rights/reproducibility boundaries.

## Latest push intent

This revision completes the post-activation governance consistency audit and its independent diff review. Live protection remains unchanged and correct. The follow-up review separates the panel's subsequently resolved repository-governance item from genuinely remaining implementation work, preserving the panel record's chronology without leaving a resolved condition under a “Remaining open items” heading. The first PR-head validation passed both required checks: Project governance run `37103129603` and Contract validation run `37103129599`. Exact-head checks must pass again after this review correction before merge.
