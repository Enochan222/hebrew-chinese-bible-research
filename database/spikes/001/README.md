# Database Spike 001 executable harness

Status: **POSTGRESQL 17 INTEGRATION SPIKE**

This directory is the executable companion to
`architecture/database-spikes/001-scholarly-integrity-vertical-slice.md`.

## Safety boundary

No Supabase remote project is modified by this spike.

The connected Supabase account currently exposes one inactive, generically named
project, while the repository contains no project ref/link proving that it is the
intended target. The spike therefore uses a clean PostgreSQL 17 service in GitHub
Actions and keeps the SQL compatible with Supabase/PostgreSQL semantics.

A later remote-deployment gate must explicitly identify the intended Supabase
project before applying migrations.

## Files

- `00_bootstrap.sql` creates only CI compatibility roles and a minimal
  `auth.uid()` shim that already exists in Supabase.
- `../../migrations/001_database_spike_001.sql` is the actual versioned
  PostgreSQL schema migration exercised by the spike.
- `01_seed.sql` loads synthetic/controlled fixtures for 1 Samuel 16:7 plus
  adversarial reference/text/rights/publication cases.
- `02_tests.sql` executes positive and negative relational, RLS, rights,
  deterministic-query, translation, and publication tests.
- `03_query_plan.sql` records an `EXPLAIN (ANALYZE, BUFFERS)` probe for the
  representative deterministic corpus query.

## Run contract

The GitHub Actions job starts PostgreSQL 17 and executes, in order:

```text
00_bootstrap.sql
  -> 001_database_spike_001.sql
  -> 01_seed.sql
  -> 02_tests.sql
  -> 03_query_plan.sql
```

`ON_ERROR_STOP=1` is mandatory. Expected failures are caught and asserted
inside PL/pgSQL test blocks; unexpected failures fail the job.

## What this proves

When green, this harness is evidence for the PostgreSQL implementation layer,
including:

- reference-span order/book integrity;
- same-layer AnalysisEdge enforcement;
- node/segment corpus-expression compatibility;
- explicit cross-layer mappings;
- source/target alignment stream pinning;
- shared-PK research-object identity with subtype/object_type compatibility;
- ResearchPositionVersion -> exact ResearchIssueVersion compatibility;
- TranslationSourceBasis stream/locus integrity;
- TranslationDecision source-basis coverage and policy-language consistency;
- fail-closed rights decisions and winning-rule subset integrity;
- public excerpt rights, typed CitationLocator, and immutable-evidence hash requirements;
- user-workspace RLS isolation plus project-owner relational consistency;
- public denial of Authoring/Publication Control;
- Serving-owned projection identity with no Serving FK/function dependency on Authoring;
- anon deterministic corpus query over Serving-only projections;
- release and component-projection immutability after PUBLISHED;
- publication visibility atomicity, transactional first-PUBLISHED event creation, and rollback by channel pointer;
- deterministic, release-pinned corpus-query result membership in canonical reference order.

## What this does not prove

This harness does **not** yet prove:

- a specific remote Supabase project's Data API exposure/grants;
- Supabase Auth/JWT behavior beyond the compatible `auth.uid()` RLS contract;
- Supabase security/performance advisor results;
- remote migration history;
- production corpus scale/latency;
- the HTTP OpenAPI handlers;
- the full opaque cursor contract that binds researchReleaseId + normalized query hash + execution-policy version;
- real OSHB/MACULA/BHSA ingestion correctness;
- full textual-apparatus richness;
- every Core Freeze gate.

Those remain explicit follow-on evidence, not implied by a green SQL spike.
