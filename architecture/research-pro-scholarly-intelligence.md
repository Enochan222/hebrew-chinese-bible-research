# Research Pro and Scholarly Intelligence Architecture

Status: **ACTIVE CANDIDATE DOMAIN CONTRACT**

This document adds a scholarly-intelligence layer to the v1.1 product architecture without creating a second application or a second scholarly database.

It must be read with:

- `architecture/database-api-cross-stage-contract-v1.1.md`
- `architecture/product-platform-and-publication-model.md`
- `architecture/ui-mode-cross-stage-contract.md`
- `contracts/v1.1/vocabulary.json`

## 1. Product principle

Research Pro is not "more AI".

It is deeper scholarly visibility and workflow over the same ResearchRelease.

The public product therefore has two experience modes:

- STUDY
- RESEARCH

Both consume the same published corpus, evidence graph, translations, rules, commentary and ResearchRelease.

Research mode exposes more depth, discovery and research tooling.

Study mode preserves minimum academic transparency.

No Research Pro feature may create a parallel ontology or duplicate canonical source data.

---

# 2. Three scholarly knowledge states

## 2.1 Core Scholarly Library

Private curated sources such as:

- reference grammars;
- lexica;
- BHS/BHQ;
- textual-criticism literature;
- commentaries;
- exegesis method;
- Chinese translation documentation when acquired.

These may be deeply structured and reviewed.

## 2.2 Scholarly Discovery Universe

External provider records that may include:

- journal articles;
- books;
- book chapters;
- dissertations;
- reviews;
- conference literature;
- citation/reference graph records;
- recent publications.

Discovery results are candidate metadata.

They are not automatically canonical ScholarlyWorks and do not enter published synthesis by discovery alone.

## 2.3 Curated Scholarly Knowledge Release

Reviewed structured objects published inside a ResearchRelease:

- canonical bibliographic works;
- approved claims;
- research issues;
- research positions;
- target links;
- literature snapshots;
- commentary entries;
- translation decisions;
- citations;
- public-safe excerpts.

Canonical commentary and state-of-research views use this layer.

---

# 3. ScholarlyDiscoveryProvider abstraction

External discovery must be provider-agnostic.

## 3.1 Provider capability contract

A provider adapter may declare support for capabilities such as:

- SEARCH_WORKS
- GET_WORK
- GET_AUTHORS
- GET_REFERENCES
- GET_CITATIONS
- GET_CITATION_CONTEXTS
- RESOLVE_DOI
- GET_ABSTRACT
- GET_FULLTEXT
- GET_OPEN_ACCESS_LOCATION
- GET_RETRACTION_OR_CORRECTION_STATUS
- SEARCH_BY_DATE
- SEARCH_BY_PUBLICATION_TYPE

No single provider is assumed to support all capabilities.

## 3.2 Provider identity

Provider IDs are external identifiers only.

They must never become the primary key of a canonical scholarly work.

---

# 4. Structural contract authority

This document defines Research Pro scholarly semantics and guardrails.

Authoritative table/field definitions for DiscoveryRecord, ResearchTarget, ResearchIssue/Version, ResearchPosition/Version, LiteratureSnapshot, CommentaryEntry, ProductEntitlement, and SourceAccessRoute are maintained in:

- `architecture/database-api-cross-stage-contract-v1.1.md` sections 38-43;
- `contracts/v1.1/json-schema/` for machine wire contracts.

Do not duplicate mutable field lists here.

---

# 5. DiscoveryRecord semantics

External provider results are staging/discovery records, not canonical scholarly works.

Required invariants:

- provider IDs never become canonical Work primary keys;
- access level records what the system actually had: metadata, abstract, citation context, or full text;
- provider terms version and RightsPolicy are recorded;
- raw payload persistence requires a rights decision permitting that operation;
- METADATA_ONLY / ABSTRACT_ONLY must never be represented as full-text reading;
- AI-assisted bibliographic resolution remains reviewable and non-VERIFIED until the configured review rule is satisfied.

Live discovery remains outside a published ResearchRelease until promoted through authoring/review/publication.

---

# 6. ResearchTarget semantics

Research Pro uses a dedicated `ResearchTarget` registry.

A passage, book, lexeme, or construction does not become a `research_object` merely because scholarship can target it.

Typed bridges connect ResearchTarget IDs to native canonical identities.

An explicit source reference and an AI-inferred relevance mapping remain distinct mappings with different provenance and review status.

---

# 7. ResearchIssue and ResearchPosition semantics

`ResearchIssue` and `ResearchPosition` have stable identities plus append-only versions.

Mutable authoring convenience pointers such as `current_version_id` are never historical public truth.

A published ResearchRelease pins exact issue/position versions, directly or through an immutable SCHOLARLY_ISSUE_GRAPH component snapshot.

Debate-state labels are conservative and snapshot-bounded.

`MINORITY_WITHIN_REVIEWED_SNAPSHOT` means minority only within a defined reviewed snapshot/coverage scope. It is not an automatic claim about the entire field.

Work count and citation count must never be converted automatically into consensus or correctness scores.

---

# 8. LiteratureSnapshot semantics

Claims about current scholarship are bounded by a LiteratureSnapshot.

A snapshot preserves enough search audit data to explain what was searched and when, including provider/version/adapter/query/ranking metadata where available.

External literature search is described as auditable. Exact reproducibility is claimed only where provider/index behavior supports it.

Editorial inclusion labels such as SEMINAL_WORK, REPRESENTATIVE_WORK, or MINORITY_WITHIN_REVIEWED_SNAPSHOT retain a classification basis.

---

# 9. Literature review artifact semantics

A LiteratureReviewSnapshot is a versioned derivative rendering over structured issues, positions, works, claims, and a LiteratureSnapshot.

Substantive public claims reuse the shared:

`PublishedAssertion -> PublishedEvidenceItem`

provenance model.

Review prose must not become a citation-free alternative truth layer.

---

# 10. Commentary semantics

Commentary is compiled published scholarship, not raw LLM prose.

Commentary sections render structured PublishedAssertions.

Assertion-level evidence remains authoritative; optional section-level evidence is only a navigation/bibliographic aid.

Study and Research modes point to the same CommentaryEntry identity.

Translation Note remains distinct from general Commentary because it records the project's translation decision and target-language trade-offs.

---

# 11. Reviewed versus live research state

Reviewed state:

- CURATED_IN_RELEASE;
- release-pinned;
- citable;
- may support published conclusions.

Live state:

- DISCOVERED_SINCE_RELEASE;
- provider-dependent;
- explicitly non-canonical;
- cannot silently mutate published commentary or translation decisions.

---

# 12. ProductEntitlement semantics

Product entitlement is a product-access control, not a content-rights grant.

Resolution is deterministic and server-side.

Specificity:

`USER > ORGANIZATION > PLAN`

At the same specificity:

`DENY > ALLOW`

If no active entitlement exists, the feature's configured default decision applies.

RightsPolicy and tenant authorization are evaluated before ProductEntitlement.

Study mode retains the minimum evidence required to verify any substantive conclusion it displays.

---

# 13. Source access semantics

Bibliographic relevance and full-text access are separate.

`SourceAccessRoute` uses the bibliographic `academic_edition_id` where an edition is referenced.

PRIVATE_LIBRARY_COPY routes are never exposed to ordinary public/customer clients.

---

# 14. Machine-contract profile

Research Pro remains part of the same product architecture but has its own extension freeze profile:

- `RESEARCH_PRO_EXTENSION_V1_1` in `contracts/v1.1/freeze-checklist.md`.

This is an engineering maturity boundary, not a second ontology, database, or scholarly truth state.

Core Database Spike 001 may proceed when the Core spike profile passes; that does not claim the Research Pro extension is frozen.

---

# 15. Publication and ResearchRelease integration

The following become release components or release-pinned objects where applicable:

- approved ResearchIssues;
- approved ResearchPositions;
- reviewed target links;
- LiteratureSnapshots;
- LiteratureReviewSnapshots;
- CommentaryEntries;
- bibliographic/citation graph;
- published access routes;
- Study/Research serving projections.

Live DiscoveryRecords remain outside the immutable curated scholarly release until promoted.

---

# 16. Phase ownership

## Phase 1

Reserve:

- product feature/entitlement contract;
- Study/Research experience mode vocabulary;
- release-aware shared UI contracts.

No full scholarly-intelligence implementation required.

## Phase 2

Use:

- key scholarship summary;
- translation-note/public commentary placeholders;
- minimum evidence transparency.

## Phase 3

Expose Research mode links to:

- constructions;
- advanced corpus queries;
- saved research objects.

## Phase 4

Own:

- scholarly discovery provider abstraction;
- external discovery records;
- bibliographic resolution;
- scholarly target links;
- ResearchIssue;
- ResearchPosition;
- LiteratureSnapshot;
- source access routes;
- issue/debate editorial review.

## Phase 5

Own:

- published literature reviews;
- published CommentaryEntries;
- Study/Research serving projections;
- product feature entitlements;
- live-discovery Research mode integration;
- release compatibility and full QA.

---

# 17. Non-negotiable constraints

1. Research Pro is not a separate application.
2. Research Pro is not a separate scholarly database.
3. Study and Research use the same active ResearchRelease.
4. Live discovery cannot change a published conclusion.
5. External provider records are not canonical scholarly works until resolved.
6. Metadata-only/abstract-only access cannot be represented as full-text reading.
7. Work count is not consensus.
8. Citation count is not correctness.
9. Issue/Position summaries are reviewed representations.
10. Product entitlement never overrides source rights.
11. Study mode retains minimum evidence transparency.
12. Commentary prose is derivative from structured evidence.
13. Translation Note is distinct from Commentary.
14. Current scholarship claims are snapshot-bounded.
