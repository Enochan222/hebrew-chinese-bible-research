# v1.1 Freeze and Database-Spike Checklist

Status: **CANONICAL GATE REGISTRY**

This file replaces duplicated numeric freeze lists in architecture prose.

Gate IDs are stable and must be referenced by fixtures/CI.

## Profiles

### CORE_SPIKE_V1_1

Minimum contract closure required before Database Spike 001 begins.

### REPOSITORY_GOVERNANCE

Operational source-of-truth protection. This profile does not block Database Spike 001, but it must be enforced before the repository is treated as production-governed.

### CORE_FREEZE_V1_1

Core Hebrew-Chinese scholarly data platform freeze.

### RESEARCH_PRO_EXTENSION_V1_1

Research Pro / Scholarly Intelligence extension over the same ResearchRelease.

Research Pro remains part of the same product and truth model. This profile separation is an engineering maturity boundary, not a second product/database.

### PUBLIC_AI_SHIP_V1_1

Additional gate only when optional public BYOK AI is shipped.

## REPOSITORY_GOVERNANCE

| Gate ID | Requirement | Current status | Evidence |
|---|---|---|---|
| REPO-GOV-001 | `main` requires PR-based changes and successful Contract validation before merge | PASS | re-verified 2026-10-04: active ruleset `Protect main` (ID 24409248); PR required; strict required checks `contracts` + `state-and-changelog`; no bypass actors; audited PRs #4/#5/#6 merged through protected flow |
| REPO-GOV-002 | force pushes and deletion of `main` are blocked by repository rules | PASS | re-verified 2026-10-04: ruleset `Protect main` has `non_fast_forward` + `deletion`; branch metadata reports `main protected = true` |
| REPO-GOV-003 | canonical product/architecture/contract/validator/workflow ownership is declared in CODEOWNERS | PASS | `.github/CODEOWNERS` |

All REPOSITORY_GOVERNANCE gates are now PASS. Live GitHub enforcement is documented in `architecture/reviews/2026-10-03-live-repository-governance-verification.md`.

## CORE_SPIKE_V1_1

| Gate ID | Requirement | Current status | Evidence |
|---|---|---|---|
| CORE-SPIKE-001 | Active v1.1 is self-contained and superseded contracts are non-authoritative | PASS | active v1.1 + architecture manifest |
| CORE-SPIKE-002 | Machine vocabulary and core JSON Schemas exist | PASS | `contracts/v1.1/` |
| CORE-SPIKE-003 | CorpusQuery scalar/binding semantics validate correctly | PASS | CorpusQuery schema + query semantics |
| CORE-SPIKE-004 | Draft query validation resolves and pins ResearchRelease before execution | PASS | normalized CorpusQuery contract |
| CORE-SPIKE-005 | Independent annotation layers can be pinned in one query | PASS | 1 Sam 16:7 fixture |
| CORE-SPIKE-006 | Rights default-deny is representable without inventing a winning rule | PASS | RightsDecisionSnapshot contract |
| CORE-SPIKE-007 | Release manifest component order is deterministic | PASS | componentOrder required + validator requirement |
| CORE-SPIKE-008 | ResearchRelease payload/lifecycle/channel pointer are separate | PASS | release schemas |
| CORE-SPIKE-009 | Public assertion evidence is assertion-level and public-safe | PASS | PublishedAssertion/Evidence contract |
| CORE-SPIKE-010 | BYOK introduces no shared model credential dependency into core | PASS | ADR-005 / BYOK policy |
| CORE-SPIKE-011 | Contract validation is executable from a fresh clone | PASS | GitHub Actions run 37071301356 checked out `7bc46c...`; validator + Core OpenAPI + Research Pro OpenAPI all succeeded |
| CORE-SPIKE-012 | Passage labels resolve through explicit ReferenceSystem and corpus pagination has an executable request contract | PASS | Contract validation run 37100959518 + panel review |
| CORE-SPIKE-013 | Official TranslationDecision pins immutable adopted source basis and exact TranslationPolicyVersion | PASS | Contract validation run 37100959518 + panel review |
| CORE-SPIKE-014 | Rights machine contract fails closed and typed condition/obligation negative fixtures pass | PASS | Contract validation run 37100959518 + adversarial negative fixtures |

Database Spike 001 may begin when all CORE-SPIKE gates are PASS. This does not declare v1.1 FROZEN.

## CORE_FREEZE_V1_1

| Gate ID | Requirement |
|---|---|
| CORE-FZ-REF-001 | ReferenceAtom identity and PassageLocator resolution are tested against superscription/split-merge/alternate-versification edge cases |
| CORE-FZ-TEXT-001 | Ketiv/Qere fixture uses WRITTEN/READ streams and alignment stream pinning |
| CORE-FZ-CORPUS-001 | OSHB plus structurally different MACULA/BHSA layer coexist without forced phrase/clause identity |
| CORE-FZ-TRANS-001 | FHL/provider distribution is distinct from work/edition/expression identity |
| CORE-FZ-ALIGN-001 | Hebrew-Chinese many-to-many alignment fixture passes |
| CORE-FZ-TC-001 | Grouped apparatus reading retains raw apparatus, witness uncertainty, siglum source context, and exact locus |
| CORE-FZ-RIGHTS-001 | Conflicting rights + default/unknown restrictive deny + typed conditions/obligations fixtures pass |
| CORE-FZ-RELEASE-001 | Real database publication provides visibility atomicity; partial failure cannot move production pointer |
| CORE-FZ-RLS-001 | RLS/grants/views/RPC negative tests pass |
| CORE-FZ-QUERY-001 | Real deterministic query compiler reproduces fixture results with stable cursor pagination and explicit page/total count semantics |
| CORE-FZ-VOCAB-001 | Active docs/vocabulary/schema enum drift check passes |
| CORE-FZ-API-001 | Core OpenAPI validates and generated/client compatibility smoke test passes |
| CORE-FZ-EVIDENCE-001 | CitationLocator is typed; public excerpts require rights snapshots; immutable evidence requires content hash |
| CORE-FZ-HASH-001 | Publishable subtype content-hash canonical projections have versioned golden vectors |

## RESEARCH_PRO_EXTENSION_V1_1

| Gate ID | Requirement |
|---|---|
| PRO-FZ-001 | DiscoveryRecord can resolve to canonical Work without duplicate identity |
| PRO-FZ-002 | ResearchIssue/ResearchPosition are versioned, PositionVersion pins exact IssueVersion framing, and historical releases never dereference mutable current rows |
| PRO-FZ-003 | ResearchTarget registry supports passage/book/lexeme/construction target identities with typed bridges |
| PRO-FZ-004 | LiteratureSnapshot records provider/query/version/coverage audit data |
| PRO-FZ-005 | Commentary and LiteratureReview reuse PublishedAssertion -> PublishedEvidenceItem semantics |
| PRO-FZ-006 | ProductEntitlement resolves deterministically and remains subordinate to RightsPolicy |
| PRO-FZ-007 | Study and Research pin the same ResearchRelease and canonical object IDs |
| PRO-FZ-008 | Live discovery remains non-canonical and cannot mutate release-pinned synthesis |
| PRO-FZ-009 | Research Pro machine schemas/OpenAPI extension validate representative fixtures |
| PRO-FZ-010 | Snapshot-bounded field-state labels preserve classification basis and coverage limitations |
| PRO-FZ-011 | Database build supports OpenAlex + Semantic Scholar + CORE + Crossref + Scite through typed provider adapters and records unavailable/skipped providers |
| PRO-FZ-012 | Query expansion/synthesis uses a model-neutral ResearchModelAdapter and records model/prompt/input/output provenance |
| PRO-FZ-013 | DiscoveryRecords are traceable to provider requests and multi-provider duplicates resolve to one canonical Work without losing provider provenance |
| PRO-FZ-014 | Academic-provider credentials are absent from source, fixtures, logs and public runtime paths |

## PUBLIC_AI_SHIP_V1_1

| Gate ID | Requirement |
|---|---|
| BYOK-FZ-001 | No shared model-provider credential in code/config/env/deployment |
| BYOK-FZ-002 | BYOK credential persists only in volatile memory |
| BYOK-FZ-003 | Proxy/CDN/APM/log/telemetry layers redact BYOK credential |
| BYOK-FZ-004 | Strict origin/CORS/CSRF/rate/body-size/egress allowlist controls pass |
| BYOK-FZ-005 | BYOK data-egress policy sends minimum rights-approved context only |
| BYOK-FZ-006 | Core scholarly product works with BYOK absent |

## Status semantics

- PASS: contract/evidence currently satisfies the gate.
- PENDING: required evidence is not yet produced.
- DEFERRED: intentionally outside the named profile.
- FAIL: evidence demonstrates the gate is not satisfied.

A PASS in a synthetic contract fixture is not equivalent to a PASS in PostgreSQL/Supabase implementation.
