# Repository Change Log

Every push/PR must update this file together with `PROJECT_STATE.md`.

Entries record **what changed, why, intended effect, and validation**. The Git commit itself supplies the immutable SHA/timestamp linkage.

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
- the branch has now synchronized that governance baseline and updated both living governance documents;
- final Contract validation + Project governance runs remain required before merge, followed by one more independent read-only adversarial review.

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
- one final CI run is required after these governance-only status/manifest updates before merge;
- live GitHub branch protection remains unresolved and is tracked in issue #1 rather than falsely marked complete.
