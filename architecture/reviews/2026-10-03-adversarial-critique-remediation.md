# Adversarial Critique Remediation Record

Date: 2026-10-03
Status: COMPLETED REVIEW LOOP FOR CURRENT CONTRACT REVISION

## Purpose

This record captures how the October 2026 critique set was evaluated. Suggestions were not accepted by default. Each material recommendation was classified by whether it corrected a load-bearing contract problem, improved the design but required modification, should be deferred until implementation evidence exists, or should be rejected because it would weaken the product model.

## MUST FIX NOW

The following were treated as contract blockers and were implemented:

- CorpusQuery JSON Schema overlap between `number` and `integer` under `oneOf`;
- empty quantifier bindings;
- release-resolution race between query validation and execution;
- explicit query resource policy, deterministic pagination, and semantic validation;
- RightsDecision default-deny outcomes with no winning rule;
- typed excerpt limits and restrictive handling of unregistered rights conditions;
- deterministic release component ordering;
- publication-form versus scholarly-role ontology drift;
- immutable DigitalExpression lineage and ReferenceAtom publication identity;
- Unicode normalization engine/version reproducibility;
- non-null AnnotationLayer versioning;
- stream-pinned alignment to prevent implicit Ketiv/Qere mixing;
- source-contextual textual-witness sigla and exact apparatus loci;
- typed scholarly dependency endpoints;
- review events rather than interpreting a generic `VERIFIED` status as universal scholarly approval;
- versioned ResearchIssue and ResearchPosition state;
- immutable Research Pro release snapshots that never dereference mutable `current_version_id` values;
- shared PublishedAssertion -> PublishedEvidenceItem semantics across passage analysis, commentary, and literature review;
- deterministic ProductEntitlement resolution subordinate to RightsPolicy and authorization;
- ResearchTarget registry with typed bridges rather than coercing every target into `research_objects`;
- provider-rights-aware DiscoveryRecord persistence;
- architecture authority manifest and unique ADR numbering;
- stable freeze-gate IDs and separation of Database Spike, Core freeze, Research Pro extension freeze, and BYOK shipping gates;
- executable positive, negative, semantic, vocabulary-drift, governance, secret-scan, and OpenAPI validation in CI.

## ADOPT WITH MODIFICATION

These recommendations were valid in direction but were deliberately narrowed:

### Separate Research Pro maturity from Core implementation

Adopted as separate **contract profiles/gates**, not as a second product, database, ontology, or truth state. Study and Research continue to share the same ResearchRelease and canonical object identities.

### Process provenance graph

Adopted as a lightweight provenance-agent/activity/input/output model that complements source locators. A full W3C PROV implementation is not required for Database Spike 001.

### Textual criticism richness

Added exact locus, source-contextual siglum identity, and bibliographic edition bridge. Exhaustive TEI parity remains deferred.

### Literature-search reproducibility

Changed the claim from universal reproducibility to **auditability**. Provider dataset/index/adapter/query/ranking metadata are stored where available. Exact replay is claimed only when the external provider actually supports it.

### MCP version formalization

Server target is the final 2026-07-28 revision. Client integrations should auto-negotiate where supported so legacy-era compatibility does not depend on implicit SDK defaults.

### BYOK hardening

Expanded from secret non-persistence to browser/network controls and explicit data-egress policy. Credential safety and research-source confidentiality are treated separately.

## DEFER

These are architecturally supported but must not block Database Spike 001:

- full population of the scholarly dependency/citation graph;
- complete retraction/correction propagation policy and live scholarly-integrity overlay;
- exhaustive TEI critical-apparatus parity;
- complete LXX morphology/syntax and all cross-framework adjudication;
- large 100+ research-question benchmark;
- complete Research Pro provider integrations and live discovery;
- final tenant/billing implementation;
- final production SQL/RLS/grants/RPC proof, which belongs to the database spike and subsequent implementation gates.

Deferred means the architecture must preserve an extension point. It does not mean the feature has been silently accepted as complete.

## REJECT

The following directions were rejected:

- making Research Pro a separate application/database or more authoritative truth state;
- treating citation count, work count, or ranking as scholarly correctness/consensus;
- collapsing publication form and scholarly function into one `work_type` enum;
- using external provider IDs as canonical scholarly primary keys;
- allowing discovery access level to imply permission to persist raw provider payloads;
- allowing ProductEntitlement to override source rights;
- treating generic `review_status`/`VERIFIED` as proof of all scholarly review dimensions;
- executing arbitrary SQL through Product MCP;
- making runtime AI a prerequisite for deterministic scholarly features;
- introducing a platform-owned model-provider fallback key.

## Independent review loop

### Review 1 findings

Found and repaired: machine-schema bugs, ontology drift, rights default-deny ambiguity, release ordering, Research Pro mutability, evidence-model duplication, ADR/freeze governance problems, and missing executable validation.

### Review 2 findings

Fresh-clone-style review found additional issues that the first pass missed:

- PublishedEvidenceItem prose required evidence stability but its schema did not;
- minority-within-snapshot classification allowed nullable evidence basis;
- some Research Pro reads did not expose the resolved ResearchRelease;
- free-form rights conditions could be misread as authoritative enforcement;
- commentary `source_payload` could become a public/private evidence escape hatch;
- ProductEntitlement source provenance was optional.

All were repaired.

### Machine verification

GitHub Actions run 37071301356 checked out commit `7bc46cdd41cd4403880c04b9038e5e50026d7cd3` in a clean runner and passed:

- 29 positive JSON Schema fixtures;
- negative fixtures;
- semantic validation;
- governance validation;
- vocabulary drift checks;
- secret scanning;
- Core OpenAPI validation;
- Research Pro OpenAPI validation.

The current main branch must continue to pass the same workflow after subsequent edits.

## Decision

The architecture is considered ready to proceed to **Database Spike 001** when the current main-head CI remains green.

This does not mean the complete product contract is frozen. Core freeze, Research Pro extension freeze, and optional BYOK shipping retain their own gates in `contracts/v1.1/freeze-checklist.md`.
