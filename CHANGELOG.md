# Repository Change Log

Every push/PR must update this file together with `PROJECT_STATE.md`.

Entries record **what changed, why, intended effect, and validation**. The Git commit itself supplies the immutable SHA/timestamp linkage.


## 2026-10-04 — Begin executable Database Spike 001

### Push intent

Move the project from contract-only database design into a reproducible PostgreSQL implementation spike that can reject invalid scholarly states at real relational/RLS/publication trust boundaries.

### Why

Core contract gates permit Database Spike 001, but prior evidence was still synthetic JSON-schema/architecture validation. A database spike must execute real DDL, foreign keys, checks, triggers, RLS policies, security boundaries, deterministic corpus queries, and publication failure handling.

The connected Supabase account currently exposes one inactive, generically named project, and the repository contains no project ref/link proving that it is the target for this product. Writing DDL there would violate the project's no-guessing deployment rule.

### What changed

- added a versioned PostgreSQL migration for the critical v1.1 vertical slice;
- separated Authoring, Serving, Workspace, and Publication Control schemas;
- implemented reference-order/book constraints and deterministic multi-atom labels;
- implemented independent corpus annotation layers, same-layer edge FKs, explicit cross-layer mappings, and node/segment corpus-expression validation;
- implemented WRITTEN/READ stream identity and stream-pinned Hebrew-Chinese alignment;
- implemented shared-PK research-object identity for publishable/versioned objects used by the spike;
- implemented SemanticSet, ConstructionDefinition/CompilationRun/Instance, RuleVersion/Application, TranslationSourceBasis, TranslationPolicyVersion, TranslationDecision, ResearchIssue/Position versioning, public evidence, and release/channel objects;
- implemented fail-closed rights evaluation and rights-snapshot invariants;
- implemented Workspace RLS using the Supabase-compatible `auth.uid()` contract;
- kept Authoring and publication-control schemas unavailable to public/authenticated runtime roles;
- implemented a non-public SECURITY DEFINER publication function available only to `publication_worker`;
- implemented immutable ResearchRelease/component/event behavior and atomic visibility through a mutable release-channel pointer;
- implemented a deterministic release-pinned 1 Samuel 16:7 corpus-query analogue and query-plan probe;
- added controlled positive/adversarial SQL fixtures and negative tests;
- added GitHub Actions PostgreSQL 17 integration workflow;
- explicitly recorded that no remote Supabase project has been modified.

### First complete green harness and independent rejection

After the harness-syntax repairs, Database Spike run `37142607945` passed bootstrap, migration, seed, the full adversarial SQL suite, and the representative query-plan step. Required Contract validation and Project governance also passed on that head.

Independent architecture review nevertheless rejected the green harness as sufficient evidence for merge. The reason was structural: several `serving.*` foreign keys and `serving.spike_corpus_query()` still depended directly on `authoring.*`. That is legal inside one PostgreSQL database but contradicts the established production invariant that Public Serving must remain functional when Authoring is unavailable.

### Architecture correction from implementation evidence

The implementation is changed so that publication materializes Serving-owned projections rather than leaving runtime referential dependence on Authoring:

- Serving-owned research-object registry;
- Serving-owned reference-span projection;
- release-pinned corpus nodes, node features, relations, explicit cross-layer mappings, and semantic-set members;
- release components and published evidence terminate FKs in the Serving registry;
- public deterministic corpus query reads only Serving projections;
- TranslationDecision aggregate hashing moves to Publication Control;
- Workspace passage identity references the public-side reference projection;
- PostgreSQL catalog tests reject any Serving FK whose target schema is Authoring;
- PostgreSQL catalog tests reject any Serving function whose definition references `authoring.`;
- an `anon` execution test proves the corpus query works without Authoring privileges.

The active database/API contract and publication model are clarified accordingly.

### Serving-isolation executable run

Database Spike run `37143183450`, the first clean run after the Serving-isolation correction:
- bootstrap: PASS;
- migration: FAIL at the newly added Serving rights-validator functions because their SQL dollar-quote delimiters were serialized as a single `# Repository Change Log

Every push/PR must update this file together with `PROJECT_STATE.md`.

Entries record **what changed, why, intended effect, and validation**. The Git commit itself supplies the immutable SHA/timestamp linkage.


## 2026-10-04 — Begin executable Database Spike 001

### Push intent

Move the project from contract-only database design into a reproducible PostgreSQL implementation spike that can reject invalid scholarly states at real relational/RLS/publication trust boundaries.

### Why

Core contract gates permit Database Spike 001, but prior evidence was still synthetic JSON-schema/architecture validation. A database spike must execute real DDL, foreign keys, checks, triggers, RLS policies, security boundaries, deterministic corpus queries, and publication failure handling.

The connected Supabase account currently exposes one inactive, generically named project, and the repository contains no project ref/link proving that it is the target for this product. Writing DDL there would violate the project's no-guessing deployment rule.

### What changed

- added a versioned PostgreSQL migration for the critical v1.1 vertical slice;
- separated Authoring, Serving, Workspace, and Publication Control schemas;
- implemented reference-order/book constraints and deterministic multi-atom labels;
- implemented independent corpus annotation layers, same-layer edge FKs, explicit cross-layer mappings, and node/segment corpus-expression validation;
- implemented WRITTEN/READ stream identity and stream-pinned Hebrew-Chinese alignment;
- implemented shared-PK research-object identity for publishable/versioned objects used by the spike;
- implemented SemanticSet, ConstructionDefinition/CompilationRun/Instance, RuleVersion/Application, TranslationSourceBasis, TranslationPolicyVersion, TranslationDecision, ResearchIssue/Position versioning, public evidence, and release/channel objects;
- implemented fail-closed rights evaluation and rights-snapshot invariants;
- implemented Workspace RLS using the Supabase-compatible `auth.uid()` contract;
- kept Authoring and publication-control schemas unavailable to public/authenticated runtime roles;
- implemented a non-public SECURITY DEFINER publication function available only to `publication_worker`;
- implemented immutable ResearchRelease/component/event behavior and atomic visibility through a mutable release-channel pointer;
- implemented a deterministic release-pinned 1 Samuel 16:7 corpus-query analogue and query-plan probe;
- added controlled positive/adversarial SQL fixtures and negative tests;
- added GitHub Actions PostgreSQL 17 integration workflow;
- explicitly recorded that no remote Supabase project has been modified.

### First complete green harness and independent rejection

After the harness-syntax repairs, Database Spike run `37142607945` passed bootstrap, migration, seed, the full adversarial SQL suite, and the representative query-plan step. Required Contract validation and Project governance also passed on that head.

Independent architecture review nevertheless rejected the green harness as sufficient evidence for merge. The reason was structural: several `serving.*` foreign keys and `serving.spike_corpus_query()` still depended directly on `authoring.*`. That is legal inside one PostgreSQL database but contradicts the established production invariant that Public Serving must remain functional when Authoring is unavailable.

### Architecture correction from implementation evidence

The implementation is changed so that publication materializes Serving-owned projections rather than leaving runtime referential dependence on Authoring:

- Serving-owned research-object registry;
- Serving-owned reference-span projection;
- release-pinned corpus nodes, node features, relations, explicit cross-layer mappings, and semantic-set members;
- release components and published evidence terminate FKs in the Serving registry;
- public deterministic corpus query reads only Serving projections;
- TranslationDecision aggregate hashing moves to Publication Control;
- Workspace passage identity references the public-side reference projection;
- PostgreSQL catalog tests reject any Serving FK whose target schema is Authoring;
- PostgreSQL catalog tests reject any Serving function whose definition references `authoring.`;
- an `anon` execution test proves the corpus query works without Authoring privileges.

The active database/API contract and publication model are clarified accordingly.

;
- seed/tests/query plan: not reached.

Both functions now use named PostgreSQL dollar quotes. No relational/security invariant was relaxed.

### Intended effect

Database Spike 001 now has executable evidence rather than prose-only expectations. CI should expose relational assumptions that JSON Schema cannot prove and provide a repeatable base for correcting the active v1.1 contract before Core Freeze.

### First executable finding

The first clean PostgreSQL 17 run applied the full migration successfully but failed while loading the SemanticSet fixture because the stable `semantic_sets.current_version_id` FK pointed to a version row that had not yet been inserted. Independent inspection found the same latent ordering pattern in ConstructionDefinition, Rule, TranslationPolicy, ResearchIssue, and ResearchPosition fixtures.

The correction retains the FK model. Stable rows are inserted with a null current pointer, immutable version rows are inserted next, and the stable current pointer is then updated. This is an implementation-order correction, not a weakening of the contract.

### Validation

First Database Spike run `37142212945`:
- bootstrap: PASS;
- full migration: PASS;
- seed: FAIL at the pre-version SemanticSet current pointer;
- adversarial tests/query plan: not reached.

Second Database Spike run `37142329963`:
- bootstrap: PASS;
- full migration: PASS;
- seed: PASS;
- adversarial suite progressed through relational/translation/rights checks and failed at the deterministic-query assertion because PostgreSQL has no `min(uuid)` aggregate;
- query plan: not reached.

The failure is a test-expression defect, not a schema relaxation. The assertion now orders UUID rows and selects the first result directly.

Third Database Spike run `37142397559`:
- bootstrap: PASS;
- full migration: PASS;
- seed: PASS;
- adversarial suite progressed through deterministic corpus-query assertions and reached Workspace RLS;
- failure: the switched `authenticated` test role lacked USAGE/EXECUTE on the temporary `spike_test.assert_true()` helper;
- query plan: not reached.

The fix grants only the disposable test helper to test roles. Production Authoring/Serving/Workspace grants are unchanged.

Independent review also identified a non-test concern not yet closed: `serving.spike_corpus_query` currently depends on Authoring tables. A later green test run is not sufficient to claim Serving-plane independence until that coupling is removed or the gate is explicitly left unproven.

Fourth Database Spike run `37142489342`:
- bootstrap: PASS;
- full migration: PASS;
- seed: PASS;
- adversarial suite: stopped immediately because the disposable assertion helper had an invalid single-`# Repository Change Log

Every push/PR must update this file together with `PROJECT_STATE.md`.

Entries record **what changed, why, intended effect, and validation**. The Git commit itself supplies the immutable SHA/timestamp linkage.


## 2026-10-04 — Begin executable Database Spike 001

### Push intent

Move the project from contract-only database design into a reproducible PostgreSQL implementation spike that can reject invalid scholarly states at real relational/RLS/publication trust boundaries.

### Why

Core contract gates permit Database Spike 001, but prior evidence was still synthetic JSON-schema/architecture validation. A database spike must execute real DDL, foreign keys, checks, triggers, RLS policies, security boundaries, deterministic corpus queries, and publication failure handling.

The connected Supabase account currently exposes one inactive, generically named project, and the repository contains no project ref/link proving that it is the target for this product. Writing DDL there would violate the project's no-guessing deployment rule.

### What changed

- added a versioned PostgreSQL migration for the critical v1.1 vertical slice;
- separated Authoring, Serving, Workspace, and Publication Control schemas;
- implemented reference-order/book constraints and deterministic multi-atom labels;
- implemented independent corpus annotation layers, same-layer edge FKs, explicit cross-layer mappings, and node/segment corpus-expression validation;
- implemented WRITTEN/READ stream identity and stream-pinned Hebrew-Chinese alignment;
- implemented shared-PK research-object identity for publishable/versioned objects used by the spike;
- implemented SemanticSet, ConstructionDefinition/CompilationRun/Instance, RuleVersion/Application, TranslationSourceBasis, TranslationPolicyVersion, TranslationDecision, ResearchIssue/Position versioning, public evidence, and release/channel objects;
- implemented fail-closed rights evaluation and rights-snapshot invariants;
- implemented Workspace RLS using the Supabase-compatible `auth.uid()` contract;
- kept Authoring and publication-control schemas unavailable to public/authenticated runtime roles;
- implemented a non-public SECURITY DEFINER publication function available only to `publication_worker`;
- implemented immutable ResearchRelease/component/event behavior and atomic visibility through a mutable release-channel pointer;
- implemented a deterministic release-pinned 1 Samuel 16:7 corpus-query analogue and query-plan probe;
- added controlled positive/adversarial SQL fixtures and negative tests;
- added GitHub Actions PostgreSQL 17 integration workflow;
- explicitly recorded that no remote Supabase project has been modified.

### Intended effect

Database Spike 001 now has executable evidence rather than prose-only expectations. CI should expose relational assumptions that JSON Schema cannot prove and provide a repeatable base for correcting the active v1.1 contract before Core Freeze.

### First executable finding

The first clean PostgreSQL 17 run applied the full migration successfully but failed while loading the SemanticSet fixture because the stable `semantic_sets.current_version_id` FK pointed to a version row that had not yet been inserted. Independent inspection found the same latent ordering pattern in ConstructionDefinition, Rule, TranslationPolicy, ResearchIssue, and ResearchPosition fixtures.

The correction retains the FK model. Stable rows are inserted with a null current pointer, immutable version rows are inserted next, and the stable current pointer is then updated. This is an implementation-order correction, not a weakening of the contract.

### Validation

First Database Spike run `37142212945`:
- bootstrap: PASS;
- full migration: PASS;
- seed: FAIL at the pre-version SemanticSet current pointer;
- adversarial tests/query plan: not reached.

Second Database Spike run `37142329963`:
- bootstrap: PASS;
- full migration: PASS;
- seed: PASS;
- adversarial suite progressed through relational/translation/rights checks and failed at the deterministic-query assertion because PostgreSQL has no `min(uuid)` aggregate;
- query plan: not reached.

The failure is a test-expression defect, not a schema relaxation. The assertion now orders UUID rows and selects the first result directly.

Third Database Spike run `37142397559`:
- bootstrap: PASS;
- full migration: PASS;
- seed: PASS;
- adversarial suite progressed through deterministic corpus-query assertions and reached Workspace RLS;
- failure: the switched `authenticated` test role lacked USAGE/EXECUTE on the temporary `spike_test.assert_true()` helper;
- query plan: not reached.

The fix grants only the disposable test helper to test roles. Production Authoring/Serving/Workspace grants are unchanged.

Independent review also identified a non-test concern not yet closed: `serving.spike_corpus_query` currently depends on Authoring tables. A later green test run is not sufficient to claim Serving-plane independence until that coupling is removed or the gate is explicitly left unproven.

 PL/pgSQL delimiter;
- query plan: not reached.

The helper now uses a named dollar quote. No production constraint or grant is weakened.

A fresh run is required after this correction, and the independent Serving-plane coupling finding remains open.

This is the first implementation round. The new `Database Spike 001 / postgres-spike` workflow must apply the migration from a blank PostgreSQL 17 database, load fixtures, pass all expected-failure assertions, and emit a representative query plan. Existing required `contracts` and `state-and-changelog` checks remain mandatory. Any SQL/contract defect found by the first clean run must be corrected before merge.

## 2026-10-04 — Re-verify live repository protection and PR enforcement

### Push intent

Perform a fresh live audit of repository governance after branch protection was enabled and subsequent protected-main work was merged.

### Why

The repository already recorded `REPO-GOV-001/002/003` as PASS, but the canonical verification evidence still centred on earlier main commits. Because repository rulesets are external live state, their correctness should be periodically re-read rather than inferred from repository prose.

### What changed

- re-read the live `Protect main` ruleset and confirmed:
  - enforcement active on the default branch;
  - no bypass actors;
  - deletion blocked;
  - non-fast-forward/force-push blocked;
  - linear history required;
  - PR required;
  - required approvals = 0;
  - review conversation resolution required;
  - squash-only merge;
  - strict required checks `contracts` and `state-and-changelog`;
- re-read repository merge settings and confirmed squash enabled, merge-commit/rebase disabled, update-branch enabled, and merged branches auto-deleted;
- confirmed latest audited main `3d2dc4d8f07b67f3be44f9fedc69a60acb775405` is associated with PR #6;
- confirmed PR #6 head passed both required checks before merge and the post-merge main commit also passed both checks;
- audited recent protected-main history and confirmed PR provenance for PR #4, PR #5, and PR #6;
- refreshed the live-governance verification record, repository-governance contract, canonical freeze-gate evidence, README validation index, and living project state;
- retained repository visibility as public observed state without changing it.

### Intended effect

Keep the repository's canonical governance evidence synchronized with actual GitHub enforcement and prove that the ruleset is not merely configured but is being used by recent main-branch changes.

### Validation

This PR must itself pass:

- `contracts`;
- `state-and-changelog`;

against latest `main` before squash merge. Post-merge main checks will be re-read as the final verification.



## 2026-10-04 — Adopt production-verified Pastoral Studio scholarly retrieval/RAG method

### Push intent

Make the private Hebrew-Bible Research Compiler use the scholarly retrieval method actually observed in the deployed Pastoral Studio Academic Biblical Study workflow, while preserving this project's stronger research-grade database and publication controls.

### Why

Earlier architecture correctly preserved the Sacred Studies Text × Topic × Lens, Librarian, synthesis, and review ideas, but one state record still relied on a static-code conclusion that several provider helpers were not wired into runtime.

A production browser run against the deployed Pastoral Studio showed a real multi-source retrieval phase before model synthesis, including Sefaria, Scite, CORE, OpenAlex, Crossref, and Open Library / Internet Archive, with explicit degraded-mode fallback when CORE authentication failed.

### What changed

- added `architecture/pastoral-studio-runtime-scholarly-rag.md` as the active retrieval-orchestration reference;
- defined Pastoral Studio parity as behavioral/method parity, not code copying;
- formalized source-specialized parallel retrieval before Librarian synthesis;
- retained OpenAlex, Semantic Scholar, CORE, Crossref, and Scite as the required scholarly-provider ensemble;
- documented Sefaria and Open Library / Internet Archive as auxiliary source-specialized retrieval routes;
- formalized explicit degraded-mode fallback and prohibited model-memory substitution for failed providers;
- formalized normalization, Work/Edition deduplication, access/rights resolution, enrichment, Librarian dossier, candidate claims, counterevidence, review, LiteratureSnapshot, ResearchBuild, and ResearchRelease;
- updated the machine-readable scholarly research method, active architecture, living state, README, and contract validation.

### Intended effect

Future GPT/Codex/Gemini/Claude database builds should search academic material using the same practical retrieval pattern that proved operational in Pastoral Studio, but persist and govern the results as research-grade data instead of immediately turning provider output into an unversioned answer.

### Validation

- contract validation asserts the production-runtime reference, capability-routed fan-out, degraded-mode policy, Librarian-after-retrieval ordering, model-memory prohibition, and auxiliary source routes;
- existing provider-ensemble, model-neutrality, rights, schema, OpenAPI, and governance checks remain mandatory;
- GitHub PR checks are the merge authority.

## 2026-10-03 — Post-protection governance consistency audit

### Push intent

Independently re-check the live GitHub protection state and reconcile every current governance authority after the `Protect main` ruleset and governance-sync PR were already in place.

### Why

The live repository, freeze checklist, PROJECT_STATE, repository-governance contract, README, and closed issue #1 all reported governance as enforced. However, `architecture/reviews/2026-10-03-panel-contract-closure.md` is still registered as a current validation record and retained one sentence saying live branch protection was not enabled. That made the validation chain internally inconsistent even though the live GitHub configuration itself was correct.

Historical CHANGELOG entries that recorded the repository before protection was enabled are valid historical evidence and must not be rewritten as though protection had always existed.

### What changed

- re-read live `main` metadata and confirmed `protected = true`;
- re-read ruleset `Protect main` (ID `24409248`) and confirmed enforcement remains active on the default branch;
- re-confirmed PR-only updates, `0` required approvals, conversation resolution, squash-only merge, strict latest-main checks, no bypass actors, linear history, deletion protection, and force-push/non-fast-forward protection;
- re-confirmed required GitHub Actions checks are `contracts` and `state-and-changelog`;
- re-confirmed post-merge push runs for governance-sync commit `14cb67e9c70fa92c0dc629c0e8efcf6e4dc5659c`: Project governance `37102653272` PASS and Contract validation `37102653290` PASS;
- corrected the stale branch-protection sentence in the current panel review and pointed it to the later live-governance verification record;
- appended an independent post-sync re-audit section to the canonical live-governance verification;
- updated PROJECT_STATE revision and latest push intent;
- deliberately left older CHANGELOG PENDING/unprotected-state statements untouched because they describe historical state rather than current authority.

### Intended effect

All current governance authorities now agree with actual GitHub enforcement while the repository retains an honest history of the earlier unprotected period. Future agents should not misread an old panel-review sentence as the current branch-protection state.

### Validation

- live GitHub ruleset and branch metadata were read directly during this audit;
- canonical current-state files were checked individually rather than relying on GitHub search-index snippets;
- freeze checklist already had `REPO-GOV-001/002/003` PASS and required no change;
- issue #1 was already closed as completed and required no change;
- first PR-head Project governance run `37103129603`: PASS;
- first PR-head Contract validation run `37103129599`: PASS;
- independent diff review found one documentation-structure defect: the now-resolved governance item still sat under a “Remaining open items” heading;
- second reviewed PR-head Project governance run `37103197575`: PASS;
- second reviewed PR-head Contract validation run `37103197574`: PASS;
- the final merge gate is the latest GitHub-required `contracts` and `state-and-changelog` result against latest `main`; no CHANGELOG entry claims a permanently “final” run ID because editing this record itself creates a newer head.

## 2026-10-03 — Live repository protection enabled and verified

### Push intent

Synchronize repository governance documents with the live GitHub `Protect main` ruleset after repository-admin protection was enabled.

### Why

The repository previously documented branch protection as an unresolved operational gap:

- `main protected = false`;
- no repository ruleset;
- required CI existed but did not prevent direct updates.

Live GitHub state has now changed. Leaving `REPO-GOV-001/002`, PROJECT_STATE, issue #1, and repository-governance prose in PENDING state would make the repository's canonical governance record false.

### What changed

- verified live `main protected = true`;
- verified active repository ruleset `Protect main` (ID `24409248`);
- verified pull requests are mandatory with `0` required approvals;
- verified unresolved review conversations block merge;
- verified squash is the only allowed merge method;
- verified required GitHub Actions checks are `contracts` and `state-and-changelog`;
- verified strict required-status-check mode is enabled, requiring validation against latest `main`;
- verified branch deletion and non-fast-forward/force-push updates are blocked;
- verified linear history is required;
- verified there are no bypass actors;
- verified CODEOWNERS remains present;
- recorded current repository visibility as public without changing it;
- changed `REPO-GOV-001` and `REPO-GOV-002` from PENDING to PASS;
- retained `REPO-GOV-003` as PASS;
- replaced stale pending-state text in `architecture/repository-governance.md` and `PROJECT_STATE.md`;
- added `architecture/reviews/2026-10-03-live-repository-governance-verification.md` as the auditable live-state record;
- updated README/manifest to expose the verified governance state.

### Intended effect

The repository's canonical state now matches actual GitHub enforcement. Contributors can work independently without mandatory mutual approval, but ordinary changes cannot bypass pull requests, latest-main validation, required CI, conversation resolution, or squash-only protected-main history.

### Validation

- live GitHub ruleset API verified ruleset ID `24409248`, enforcement `active`, default-branch target, no bypass actors;
- live branch API verified `main protected = true`;
- latest `main` commit `7923a56e9bce4046363834071ba625c28db2980b` had successful `contracts` and `state-and-changelog` GitHub Actions checks before this governance-sync PR;
- this PR must itself pass the same required checks before merge;
- after merge, issue #1 should be closed as completed and main push checks re-verified.

## 2026-10-03 — Independent contract-closure panel

### Push intent

Critically evaluate three architecture critique sets with independent academic, database/API, rights/security, Research Pro, and engineering/governance review lenses; accept only changes that close real load-bearing gaps; then independently re-review the modified contracts before Database Spike 001.

### Why

The pre-spike v1.1 contract was already strong, so indiscriminately implementing every critique would have increased ontology and API surface without proving scholarly or engineering value. The panel therefore separated true contract holes from production hardening, deferred work, and over-design.

### What changed

- added explicit ReferenceSystem-aware PassageLocator and PassageRequest contracts;
- separated normalized CorpusQuery meaning from execution cursor/page state;
- made corpus page-count versus exact-total semantics explicit;
- added immutable TranslationSourceBasis and versioned TranslationPolicyVersion while reusing the existing RuleVersion engine;
- required TranslationDecision to pin exact source basis and policy version;
- removed the first-pass undefined TargetLanguageProfile dependency;
- kept PassageCore content extensible until the serving projection is actually frozen;
- kept passage-level TranslationSourceBasis out of top-level release-manifest enumeration to avoid whole-Bible manifest explosion;
- hardened RightsDecisionSnapshot so UNKNOWN_RESTRICTIVE resolves DENY, final snapshots cannot remain UNKNOWN, conditions/obligations are typed, and permissive public evidence requires the right snapshot/hash state;
- added typed CitationLocator with locator-specific required identity;
- tightened DiscoveryRecord persistence rights, ProductEntitlement provenance vocabulary, ResearchPositionVersion issue-version framing, and commentary assertion provenance;
- clarified publication visibility atomicity across separate Authoring and Serving stores;
- defined Database Spike 001 as an adversarial scholarly-integrity vertical slice rather than a table-creation demo;
- added CODEOWNERS/repository-governance documentation and pinned GitHub Actions used by panel-modified workflows to immutable SHAs;
- synchronized the concurrent multi-provider scholarly discovery and Sacred Studies research-method work from latest main rather than overwriting it;
- extended contract validation with new positive/negative fixtures, local-ref checks, vocabulary drift checks, provider/method checks, and second-pass adversarial invariants.

### Intended effect

Database Spike 001 can now test a smaller, more coherent contract surface in which the most important scholarly identities, rights outcomes, query semantics, translation dependencies, release boundaries, and governance assumptions are explicit without prematurely freezing every future API or bibliographic detail.

### Validation

- earlier clean PR Contract validation run 37099589859 passed after the first closure pass;
- later Project governance run 37099830333 correctly failed because the new mandatory PROJECT_STATE/CHANGELOG rule landed concurrently on main and the panel branch had not yet adopted it;
- the branch synchronized that governance baseline and updated both living governance documents;
- Contract validation runs 37100959518, 37101013187, and 37101156060 passed during successive review rounds;
- Project governance runs 37100959521, 37101013160, and 37101156012 passed during successive review rounds;
- the final independent adversarial review found no further load-bearing domain-model defect;
- `architecture/reviews/2026-10-03-panel-contract-closure.md` is the canonical panel adjudication record;
- live branch protection remains the only unresolved repository-governance item and is tracked in issue #1.

## 2026-10-03 — Sacred Studies method parity + mandatory push governance

### Push intent

Make the Hebrew-Bible research database use the full Sacred Studies scholarly-search/research method while correcting defects, and make project state/version history mandatory on every future push.

### Why

Two risks were identified:

1. `Sacred Studies-style` had been documented mainly as a provider-aggregation concept, without fully pinning the exact query/search/dossier/synthesis/review method.
2. Product intent and architecture were well documented, but there was no mechanically enforced rule requiring every push to update a living repository-state record and a human-readable reasoned change history.

### What changed

- added `architecture/sacred-studies-research-method.md`;
- added `contracts/v1.1/scholarly-research-method.json`;
- defined Text × Topic × Lens search matrix;
- preserved concise English academic-query generation, standard English book naming, and 3-6 term/phrase query design;
- preserved all-era + modern scholarship search policy, replacing stale 2015-2025 hard-coding with a rolling recent window;
- preserved academic-source prioritization and zero-hallucination bibliography rule;
- preserved Librarian dossier -> synthesis -> critical review/revision loop;
- preserved 88/100 review threshold and maximum three attempts;
- corrected Sacred Studies defects: invalid review output cannot auto-pass; provider failure cannot fall back to model-memory evidence;
- documented that current Sacred Studies provider helper wiring is incomplete and therefore is not copied literally;
- added `PROJECT_STATE.md` as mandatory living repository state;
- added `CHANGELOG.md` as mandatory reasoned push history;
- added `AGENTS.md` with read-before-change and update-before-push rules;
- added GitHub Actions governance check requiring every push/PR to modify both `PROJECT_STATE.md` and `CHANGELOG.md`;
- updated README, charter, manifest, discovery architecture, and contract validator to point to/enforce the new method/governance.

### Intended effect

Any future GPT/Codex/Gemini/developer build should be able to reconstruct both the product's current state and the exact scholarly search method without relying on chat history. No future push should silently change architecture without also updating project state and explaining why.

### Validation

- project-governance workflow introduced in this push;
- contract validator extended to verify Sacred Studies-derived method parameters;
- existing Core and Research Pro OpenAPI validation remains required;
- post-push GitHub Actions result is the authoritative execution record.


## 2026-10-03 — Panel contract closure + adversarial re-review

### Push intent

Close the remaining load-bearing architecture and machine-contract gaps before Database Spike 001 without expanding v1.1 into another speculative redesign.

### Why

Independent review of the active v1.1 architecture found several real pre-spike defects: ambiguous human-reference resolution, a corpus-query cursor response without an executable page-request contract, no explicit adopted source-text state for official translation decisions, no versioned project translation policy, permissive rights snapshot edge cases, under-specified citation locators, and several Research Pro/versioning/governance inconsistencies.

The same review also rejected lower-value proposals that would over-expand v1.1 before real PostgreSQL/corpus evidence, including a large bibliographic redesign, full TEI/OCR ontology work, another BYOK architecture layer, and exhaustive API error/pagination standardization.

### What changed

- added ReferenceSystem-aware PassageLocator/PassageRequest contracts while keeping canonical ReferenceSpan identity primary;
- added CorpusQueryExecutionRequest with cursor/page state separate from normalized query semantics;
- clarified page versus exact total match-count semantics;
- added immutable TranslationSourceBasis for the exact textual state translated;
- added versioned TranslationPolicy that reuses existing RuleVersion objects rather than creating a parallel rule engine;
- required TranslationDecision to pin exact source basis and policy version;
- made RightsDecisionSnapshot fail closed and typed conditions/obligations;
- rejected UNKNOWN as a final resolved rights outcome;
- typed CitationLocator and required locator-specific identity;
- required rights snapshot for published excerpts and content hash for immutable evidence;
- pinned ResearchPositionVersion to exact ResearchIssueVersion;
- tightened discovery persistence/rights coupling, entitlement vocabulary, commentary assertion provenance, and release component semantics;
- clarified publication visibility atomicity for separate Authoring/Serving databases;
- defined Database Spike 001 as an adversarial scholarly-integrity vertical slice with relational, RLS, publication, corpus, rights and textual-state attacks;
- added CODEOWNERS and repository-governance contract;
- pinned GitHub Actions dependencies used by contract/project governance to immutable commit SHAs;
- synchronized all changes with the newer multi-provider scholarly-discovery and Sacred Studies-derived research-method work already added to main;
- added/expanded positive and negative fixtures plus schema, vocabulary, local-ref and semantic validation.

### Intended effect

Database Spike 001 can now test a narrower, more explicit set of scholarly invariants instead of discovering preventable domain/API contradictions mid-migration. The project retains extension space where the serving DTO is not yet frozen and avoids inventing new ontologies before real implementation evidence.

### Validation

- six-role panel review used separate academic/method, relational-data, API/contract, rights/security, Research Pro/bibliography, and engineering/governance lenses;
- first clean PR Contract validation run 37099589859 passed before the second adversarial review;
- subsequent review corrected over-constraint in PassageCore, incomplete CitationLocator semantics, a dangling target-language-profile dependency, ambiguous source-basis evidence identity, UNKNOWN final rights decisions, and ambiguous non-exact totals;
- substantive closeout Contract validation run 37101013187 passed;
- substantive closeout Project governance run 37101013160 passed;
- CORE-SPIKE-012/013/014 are therefore marked PASS with explicit CI evidence;
- the panel adjudication record is stored at `architecture/reviews/2026-10-03-panel-contract-closure.md`;
- merge is allowed only when the latest PR Contract validation and Project governance runs are both successful; the PR checks are the authoritative final gate rather than a hard-coded “last run” ID in this changelog;
- live GitHub branch protection remains unresolved and is tracked in issue #1 rather than falsely marked complete.


## 2026-10-03 — Repository governance gate registry correction

### Push intent

Repair a post-merge source-of-truth inconsistency found by the final independent read-only review.

### Why

`architecture/repository-governance.md` explicitly required live branch-protection/ruleset state to be tracked as `REPO-GOV-001/002` in the canonical freeze checklist, but those gate rows were absent after PR #2 merged. The operational state itself was already documented correctly as pending, but the canonical gate registry did not contain the promised IDs.

### What changed

- restored `REPO-GOV-001` for PR + required Contract validation enforcement on `main`;
- restored `REPO-GOV-002` for force-push/deletion protection;
- recorded both as PENDING using live GitHub evidence: `main protected = false`, repository rulesets empty;
- recorded `REPO-GOV-003` as PASS because `.github/CODEOWNERS` exists;
- updated PROJECT_STATE to distinguish Database Spike readiness from repository production-governance readiness.

### Intended effect

The governance architecture, live repository state, and canonical freeze registry now say the same thing. Database Spike 001 remains unblocked, while branch protection is not falsely represented as complete.

### Validation

- PR #2 post-merge Contract validation push run `37101307953`: PASS;
- PR #2 post-merge Project governance push run `37101307963`: PASS;
- this follow-up PR must pass both latest PR checks before merge.


### Independent self-review correction

The first follow-up patch inserted the repository-governance gate table at an ambiguous Markdown anchor and accidentally displaced the `CORE_SPIKE_V1_1` profile heading. Independent PR diff review caught this before merge. The freeze checklist was rebuilt from current `main`, preserving the original Profiles taxonomy and adding a separate `## REPOSITORY_GOVERNANCE` gate section before the Core Spike gate table.
