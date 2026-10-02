# ADR-002: Compile Scholarly Research into Immutable Published Releases

Status: **ACCEPTED**
Date: 2026-10-03

## Context

The project was initially framed primarily as a research application with runtime academic RAG and runtime AI synthesis.

The intended product is broader:

- a long-lived scholarly database;
- a deterministic Hebrew corpus query engine;
- a Chinese translation research corpus;
- a reviewed knowledge graph;
- a rule/translation-decision system;
- a public research product;
- private editorial and research tooling.

Most canonical translations and scholarly analyses are intended to be prepared before publication rather than regenerated for every page request.

The academic source library also contains copyrighted and private research material that should not be exposed to the public runtime merely because it is useful during research compilation.

## Decision

1. Runtime academic RAG and runtime AI synthesis are no longer core dependencies of the public scholarly product.
2. Academic retrieval, large-model research, embeddings and source-book processing are primarily authoring/build-time capabilities.
3. The public serving product reads versioned published research data and executes deterministic corpus queries.
4. Introduce first-class ResearchBuild and ResearchRelease concepts.
5. Published ResearchRelease payload is immutable.
6. Introduce a one-way publication firewall from private authoring data to public serving data.
7. Model four logical product planes:
   - Authoring / Research
   - Publication / Control
   - Public Serving
   - User Workspace
8. Physical authoring/serving database separation is recommended for public production, while local/early-alpha development may use separately secured schemas.
9. Add ConstructionDefinition and ConstructionInstance as corpus-pattern objects.
10. Keep interpretive Rule and RuleApplication separate from construction matching.
11. Add PublishedPassageAnalysis and TranslationDecision for reviewed editorial output.
12. Official semantic sets are versioned compiled research objects.
13. Public corpus search may use release-scoped compiled projections derived from canonical annotation data.
14. Optional natural-language search may compile language to a constrained query AST only.
15. The LLM never executes arbitrary SQL or determines corpus membership.

## Critical qualification

The decision does **not** mean every possible research interaction is precomputed.

The following remain dynamic:

- ad-hoc deterministic corpus queries;
- user workspace edits;
- saved searches;
- custom user translation drafts;
- optional natural-language-to-DSL interpretation;
- optional supplementary discovery over published/open literature.

Canonical published claims and analyses, however, must not depend on fresh runtime model synthesis.

## Why not call this a one-time Stage 0?

Research compilation is a continuing product operation.

New books, corrected claims, new corpus releases, revised rules and new translations will require future compilation and publication.

Therefore the Research Compiler is a persistent product plane, not merely a bootstrap stage.

## Why not only two databases?

A database-backed product also has mutable user state.

The architecture therefore distinguishes:

- private authoring research data;
- immutable published research data;
- user workspace data.

User workspace data may physically share the serving database in an MVP, but it remains a distinct schema/security domain.

## Why not remove pgvector entirely?

Vector retrieval is useful for:

- build-time candidate discovery;
- literature retrieval;
- similarity-based source exploration.

It is not authoritative for exhaustive Hebrew corpus membership.

The core serving product therefore has no hard dependency on vector search, while optional research/discovery features may use it.

## Consequences

### Positive

- lower runtime cost and latency;
- reduced rights leakage risk;
- stable and citable scholarly output;
- reproducible corpus search;
- easier release rollback;
- weaker dependence on external model vendors;
- clear separation of corpus facts, rules and editorial decisions.

### Costs

- publication compiler must be built;
- release management becomes a real subsystem;
- serving projections must be regenerated;
- private/public schema compatibility must be tested;
- editorial review becomes explicit operational work.

These costs are accepted because the project is a scholarly data product, not only an AI chat interface.

## Superseded assumptions

The following assumptions are no longer valid as core product architecture:

- public page loads should retrieve source books and synthesize analysis on demand;
- Stage 5 should primarily be a runtime AI research orchestrator;
- one database containing both private source books and public serving data is the preferred production topology;
- a search pattern and an interpretive research rule are the same domain object.

## Related documents

- `architecture/product-platform-and-publication-model.md`
- `architecture/database-api-cross-stage-contract-v1.1-candidate.md`
- `architecture/site-build-staging-plan.md`
- `architecture/security-trust-boundaries.md`
