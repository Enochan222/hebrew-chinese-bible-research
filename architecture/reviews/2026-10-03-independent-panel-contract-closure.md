# Independent Panel Contract-Closure Review

Date: 2026-10-03  
Status: **CONTRACT CLOSURE COMPLETE; LIVE REPOSITORY PROTECTION STILL PENDING**

## 1. Review method

The critique set was not implemented wholesale. It was separated into independent review lenses:

1. Hebrew Bible / translation methodology;
2. relational data integrity;
3. HTTP/MCP machine-contract semantics;
4. rights, security, and publication firewall;
5. Research Pro / scholarly-intelligence compatibility;
6. engineering governance, CI, and reproducibility.

Each lens first evaluated whether a recommendation identified a real load-bearing gap, a useful later hardening item, an unnecessary duplicate abstraction, or an over-constraint. Changes were then implemented, validated, and re-reviewed adversarially.

The review loop deliberately allowed reversal of first-pass changes. A change was not retained merely because it had already been implemented.

## 2. Accepted now

### 2.1 Reference resolution

Accepted.

Human-readable passage labels are addresses, not canonical identities. Passage requests now resolve either:

- direct ReferenceSpan identity; or
- explicit ReferenceSystem + human label.

This closes alternate-versification and superscription ambiguity without replacing the existing ReferenceAtom / ReferenceSpan ontology.

### 2.2 Corpus-query execution request and count semantics

Accepted.

The normalized scholarly query is now distinct from retrieval state. Cursor/page-size execution state belongs in CorpusQueryExecutionRequest rather than changing the CorpusQuery itself.

Result contracts now distinguish:

- current-page match count;
- exact total match count when actually computed;
- whether the total is exact.

A non-exact result cannot carry a number that looks like an exact total.

### 2.3 TranslationSourceBasis

Accepted with scope correction.

An official project TranslationDecision must identify the exact adopted source-text state it translates, including textual-critical decisions where relevant.

TranslationSourceBasis is immutable passage/decision-level research data.

It is **not** emitted one-by-one as a top-level ResearchRelease component across the whole Bible. The published translation/analysis aggregate seals the exact decision -> source-basis identities transitively.

### 2.4 TranslationPolicyVersion

Accepted, but no second rule engine was created.

Hebrew evidence does not mechanically determine one Chinese rendering. The project therefore needs a versioned target-language/editorial policy.

TranslationPolicyVersion aggregates the existing:

- TRANSLATION_POLICY RuleVersions;
- EDITORIAL_CONVENTION RuleVersions.

The two membership sets are disjoint and are validated as such.

### 2.5 Rights fail-closed machine semantics

Accepted as a pre-spike requirement.

RightsDecisionSnapshot now:

- cannot resolve to UNKNOWN;
- resolves UNKNOWN_RESTRICTIVE to DENY;
- requires typed/versioned conditions;
- requires typed obligations with units where applicable;
- rejects empty CONDITIONAL decisions;
- keeps DEFAULT_DENY / UNKNOWN_RESTRICTIVE obligation-free;
- distinguishes rule-level UNKNOWN from resolved decision state.

Provider/discovery persistence and public excerpt publication remain operation-specific and must validate the referenced rights decision, not merely the presence of a snapshot ID.

### 2.6 CitationLocator and public evidence invariants

Accepted.

Citation locators now have locator-specific required identity.

A published excerpt must be:

- rights-approved;
- citable through a non-null typed locator.

Immutable published evidence must carry a content hash.

### 2.7 Exact ResearchIssueVersion framing for ResearchPositionVersion

Accepted.

ResearchPositionVersion now pins the exact ResearchIssueVersion under whose framing the position was formulated. The stable issue identity remains for grouping, but mismatched stable/version parentage is an invalid database state.

### 2.8 Publication visibility atomicity

Accepted as a correction to terminology.

With physically/logically separate Authoring and Serving databases, the system does not claim a distributed PostgreSQL ACID transaction.

The required guarantee is atomic **publication visibility**:

1. fully materialize candidate release while inactive;
2. validate;
3. atomically move the Serving release-channel pointer.

Clients must see the complete old release or the complete new release, never a partial new release.

### 2.9 Adversarial Database Spike 001

Accepted.

Database Spike 001 is a scholarly-integrity vertical slice rather than a CREATE TABLE exercise. It attacks:

- cross-layer analysis edges;
- cross-corpus/text-context node mappings;
- cross-stream Hebrew-Chinese alignment;
- reference-system edge cases;
- issue/version mismatches;
- source-basis/policy mismatch;
- wrong-operation rights reuse;
- excerpt publication with DENY/wrong rights;
- query count/pagination determinism;
- RLS leakage;
- publication failure before pointer movement;
- transitive hash sealing of TranslationDecision -> TranslationSourceBasis.

## 3. Accepted only after modifying the recommendation

### 3.1 Strict PassageCore closure

The original tightening direction was reasonable, but the first implementation was too strict.

PassageCore now closes canonical reference identity while leaving passage-content fields extensible until the actual Serving projection is frozen. This avoids inventing an incomplete “final” payload too early.

### 3.2 TargetLanguageProfile

Not introduced in v1.1.

The first pass referenced an undefined TargetLanguageProfileVersion. That created a dangling contract and was removed.

Target-language policy remains represented by BCP-47 target language plus versioned TranslationPolicy fields. A richer target-language profile may be added later only when its real domain requirements are known.

### 3.3 Commentary assertion provenance

The recommendation was accepted only as a shared-provenance rule.

Commentary continues to reuse PublishedAssertion -> PublishedEvidenceItem semantics. No separate commentary evidence ontology was introduced.

### 3.4 Release component pinning

TranslationPolicy is an appropriate shared release dependency.

Passage-level TranslationSourceBasis is not a top-level component per passage. Its immutable identity is sealed through the published translation/analysis aggregate.

## 4. Deferred, not blockers for Database Spike 001

The following ideas may be useful later but do not justify another Core contract expansion now:

- comprehensive bibliographic ontology redesign;
- API-wide pagination/error object normalization;
- OCR-specific ontology expansion;
- full TEI modelling;
- another BYOK/security architecture layer beyond the current trust-boundary contracts;
- provider-scale Research Pro production normalization;
- complete canonical hash golden vectors for every publishable subtype.

These remain freeze/production-hardening work where applicable.

## 5. Rejected

The panel rejected:

- building a second translation rule engine;
- treating every critique item as a Core freeze blocker;
- making every passage-level source basis a direct top-level ResearchRelease component;
- claiming cross-database distributed ACID publication;
- closing PassageCore around an incomplete payload;
- retaining an undefined TargetLanguageProfile dependency;
- allowing UNKNOWN as a final resolved rights decision;
- treating a page count or estimate as an exact corpus total;
- treating the presence of any rights snapshot as sufficient authorization for a different operation;
- claiming branch protection is complete merely because governance files exist.

## 6. Independent revision-loop findings

The post-change critical review found and corrected several first-pass defects:

1. PassageCore had been closed before its content projection was actually defined.
2. Direct ReferenceSpan requests conflicted with a response that required an invented display ReferenceSystem.
3. CitationLocator type initially did not require the identity appropriate to its locator type.
4. TranslationPolicy initially referenced an undefined TargetLanguageProfileVersion.
5. TranslationSourceBasis initially used an ambiguous assertion-ID field.
6. Passage-level source bases were initially added to release-component vocabulary, creating avoidable whole-Bible manifest growth.
7. Rights snapshots still allowed UNKNOWN as a final decision.
8. Non-exact query totals could still carry misleading numeric totals.
9. TranslationSourceBasis kinds could initially contain mutually contradictory fields.
10. Published excerpts could initially carry rights approval without a usable citation locator.
11. TranslationPolicy rule and editorial-convention memberships could overlap.
12. Concurrent main-branch scholarly-provider and Sacred Studies/governance work had to be three-way merged rather than overwritten.
13. The new mandatory PROJECT_STATE/CHANGELOG gate correctly exposed that the panel branch had started before the governance rule landed.

## 7. Validation state

The contract closure has passed clean pull-request validation after the main concurrency merge.

Evidence already observed during the loop includes:

- Contract validation run 37099589859: PASS;
- Contract validation run 37100959518: PASS;
- Project governance run 37100959521: PASS.

The final PR head must retain both Contract validation and Project governance as green before merge.

## 8. Remaining operational item

Live GitHub repository protection is still not enabled:

- main is currently reported as unprotected;
- repository rulesets are empty.

This is tracked by issue #1 and REPO-GOV-001 / REPO-GOV-002.

The connected GitHub tool exposes protection/ruleset reads but no repository-administration write capability. Therefore this item is kept explicitly PENDING rather than being falsely marked complete.

This operational gate does not change the scholarly/database contract closure above, but it remains necessary before the repository should be treated as fully production-governed.
