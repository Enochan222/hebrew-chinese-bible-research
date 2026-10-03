# Panel Contract-Closure Review

Date: 2026-10-03  
Status: **INDEPENDENT ADVERSARIAL REVIEW RECORD**

## Purpose

This record documents the independent panel review used to decide which proposed v1.1 changes were necessary before Database Spike 001, which proposals were modified, and which were intentionally deferred.

The review did not treat a longer architecture as automatically better. The governing question was whether a proposal closed a load-bearing scholarly, relational, API, rights, reproducibility, or governance defect that would otherwise be expensive to discover during implementation.

## Independent review seats

The panel used six separate lenses before adjudication:

1. Hebrew-Bible / translation-method integrity;
2. relational data integrity;
3. HTTP/MCP/machine-contract consistency;
4. rights, security, BYOK, and publication firewall;
5. Research Pro / scholarly-discovery / bibliography;
6. engineering governance, CI, and version control.

Findings were reconciled only after each lens had independently identified risks.

## Accepted now

The following were judged necessary before Database Spike 001:

- explicit ReferenceSystem-aware human passage resolution to canonical ReferenceSpan;
- executable CorpusQuery cursor/page request contract separate from normalized query meaning;
- explicit page-count versus exact-total count semantics;
- immutable TranslationSourceBasis identifying the actual textual state translated;
- actual adopted reading text for editorial/composite emendation;
- versioned TranslationPolicy using existing RuleVersion objects rather than a second rule engine;
- TranslationDecision pinning exact source basis and policy version;
- fail-closed RightsDecisionSnapshot semantics;
- typed/versioned rights conditions and typed obligations;
- resolved rights outcome restricted to ALLOW / DENY / CONDITIONAL;
- typed CitationLocator semantics;
- rights snapshot requirement for public excerpts and content hash requirement for immutable evidence;
- ResearchPositionVersion pinning exact ResearchIssueVersion framing;
- discovery persistence coupled to rights decisions;
- controlled ProductEntitlement source provenance;
- commentary substantive sections retaining assertion provenance;
- release-manifest logical component uniqueness;
- publication visibility atomicity for separate Authoring and Serving databases;
- adversarial Database Spike 001 relational/RLS/rights/publication tests;
- CODEOWNERS, governance contract, and immutable SHA pins for GitHub Actions.

## Accepted with modification

Several proposals were directionally correct but over-broad or over-strict in their first form:

- PassageCore is not fully closed yet. Canonical reference identity is closed, but content fields remain extensible until the serving projection is actually frozen.
- Direct ReferenceSpan requests do not invent a display ReferenceSystem. A resolved human label is optional metadata.
- TranslationSourceBasis does not create a second mutable “current source text” hierarchy.
- TranslationPolicy does not create a parallel rule ontology. It aggregates existing TRANSLATION_POLICY and EDITORIAL_CONVENTION RuleVersions.
- TranslationSourceBasis is normally sealed transitively by the published translation/analysis aggregate rather than emitted as one top-level release component per passage.
- Source-basis passage compatibility means the decision locus is covered by the basis, not that the two ReferenceSpan IDs must always be identical.
- Rights obligations are typed residual obligations; UNKNOWN permission resolves restrictively instead of becoming a final runtime outcome.
- Corpus totals are either exact or absent. A non-exact estimate, if later needed, must use a separately named field.

## Deferred or rejected for this closure

These proposals may be valuable later but were not judged necessary to begin the real database spike:

- large bibliographic identity redesign beyond the existing Work / Edition / SourceAsset / provider-resolution model;
- full API-wide cursor/error ontology;
- full TEI implementation;
- expanded OCR ontology before ingestion evidence;
- a second BYOK/security architecture layer where existing trust-boundary contracts already cover the requirement;
- provider-scale Research Pro normalization before real adapter/database evidence;
- speculative schema expansion that has no current fixture, query, UI, or publication use case.

These are not declared unnecessary forever. They are deliberately deferred until implementation evidence justifies them.

## Review loop findings and corrections

### Review round 1

Initial closure identified and implemented reference resolution, query execution pagination, source-basis/policy separation, rights fail-closed semantics, evidence locator typing, Research Pro version pinning, CI/governance, and the adversarial database spike.

### Review round 2

Independent re-review found over-constraint and dangling-contract defects:

- PassageCore had been closed before its real serving payload was defined;
- direct ReferenceSpan reads conflicted with a mandatory display ReferenceSystem;
- CitationLocator types did not yet require their type-specific identity;
- TranslationPolicy referenced an undefined target-language-profile object;
- source-basis evidence identity was ambiguous;
- final RightsDecisionSnapshot still allowed UNKNOWN;
- non-exact corpus totals could still carry a misleading total number.

All were corrected.

### Review round 3

Cross-file and relational review found additional issues:

- editorial emendation stored rationale but not the actual adopted source reading;
- winning rights rules were not required to be among applicable rules;
- release-manifest logical uniqueness allowed the same research object with conflicting version labels;
- query-semantics prose lagged behind the machine pagination/count contract;
- Database Spike source-basis test incorrectly required strict span equality rather than locus coverage;
- publication firewall tests needed to reject rights snapshots that exist but do not authorize the actual excerpt operation/audience/purpose.

All were corrected.

## Remaining open items

The following remain explicit rather than being disguised as completed work:

- live `main` branch protection / required status-check enforcement is still not enabled; tracked in GitHub issue #1;
- PostgreSQL/Supabase relational constraints, RLS/grants, query compiler, publication transaction behavior, and real corpus ingestion remain implementation work for Database Spike 001;
- publishable-object content-hash canonical projections still require golden-vector implementation evidence;
- Research Pro provider licence/quota decisions remain deployment/commercial decisions;
- full Core freeze remains pending real implementation evidence.

## Validation evidence before final governance-only closeout

At the end of the substantive contract loop:

- Contract validation run `37101013187`: PASS;
- Project governance run `37101013160`: PASS;
- PR remained mergeable against current `main`.

Merge is permitted only when the **latest** pull-request runs of both Contract validation and Project governance are successful. The PR checks are the authoritative final merge gate; this record deliberately does not pin a governance-only “last run” ID, so a documentation update cannot make the review text stale by definition.
