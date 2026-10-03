# Integration Boundaries: MCP, API, and Database

Status: **CANDIDATE INTEGRATION ARCHITECTURE**

Date: 2026-10-03

This document defines how the product planes communicate and, critically, where MCP belongs.

It does not replace the database contract. It constrains how external tools, application services, providers, and databases may connect.

## 1. Core decision

MCP is an **agent-facing capability protocol**, not the product's internal database transport.

The core system must not be designed as:

```text
Browser -> MCP -> Database
Compiler -> MCP -> Database
Publication Worker -> MCP -> Database
```

Instead:

```text
External AI host
    -> MCP facade
        -> domain/application service
            -> API/database layer
```

The internal product continues to use:

- typed service calls;
- ordinary HTTP APIs where a network boundary exists;
- PostgreSQL/Data API/RPC access according to trust boundary;
- queues/jobs for long-running research compilation.

## 2. Three different meanings of "MCP" in this project

### 2.1 Provider MCP

Example: FHL MCP Server.

Purpose:

- expose an external provider's capabilities to an AI host;
- wrap provider API calls as MCP tools/resources/prompts.

This is useful for:

- private research agents;
- prototyping;
- interactive source exploration.

It is **not** the preferred canonical production integration with FHL.

For deterministic provider integration, the product should have its own FHL Provider Adapter that calls the provider API directly, validates the response, records provenance, applies rights policy, and exposes a typed internal result.

Reason:

The production application should not require an AI-oriented protocol hop in order to retrieve a normal upstream API response.

### 2.2 Product MCP

A future MCP server owned by this project.

Purpose:

- allow ChatGPT, Claude, Codex, research agents, IDEs, or other MCP hosts to query the published product.

The Product MCP is a facade over the same domain services used by the public HTTP API.

It must not query PostgreSQL directly.

Initial Product MCP should be read-only.

### 2.3 Supabase MCP / development MCP

Purpose:

- developer and agent tooling;
- inspect schema;
- execute controlled development SQL;
- run advisors;
- assist migrations and debugging.

It is **development infrastructure**, not a runtime product dependency.

No public end-user request should pass through Supabase MCP.

## 3. Logical topology

```text
                         PRIVATE / AUTHORING
┌──────────────────────────────────────────────────────────────┐
│ Google Drive                                                │
│ Academic-paper MCP/API                                      │
│ FHL API or optional provider MCP                            │
│ Open corpora / dataset releases                             │
└───────────────┬──────────────────────────────────────────────┘
                │ provider/source adapters
                v
┌──────────────────────────────────────────────────────────────┐
│ Research Compiler / Authoring Services                       │
│ - ingestion                                                  │
│ - extraction                                                 │
│ - AI-assisted candidate research                             │
│ - corpus compilation                                         │
│ - semantic-set compilation                                   │
│ - construction compilation                                   │
│ - rule review                                                │
│ - editorial decisions                                        │
└───────────────┬──────────────────────────────────────────────┘
                │ direct/pooled private DB access
                v
┌──────────────────────────────────────────────────────────────┐
│ AUTHORING DATABASE                                           │
│ private source metadata/text where permitted                 │
│ claims, mappings, review state, research builds              │
└───────────────┬──────────────────────────────────────────────┘
                │ read-only source role
                v
┌──────────────────────────────────────────────────────────────┐
│ Publication / Control Worker                                 │
│ rights -> citation -> benchmark -> projection -> manifest    │
└───────────────┬──────────────────────────────────────────────┘
                │ dedicated publish role, one-way
                v
                         PUBLIC / SERVING
┌──────────────────────────────────────────────────────────────┐
│ SERVING DATABASE                                             │
│ ResearchRelease, published evidence, corpus projections      │
│ + USER WORKSPACE schema/data                                 │
└───────────────┬──────────────────────────────────────────────┘
                │
       ┌────────┴───────────┐
       v                    v
┌───────────────┐     ┌─────────────────────┐
│ Public HTTP   │     │ Product MCP Server  │
│ API / Next.js │     │ read-only initially │
└───────┬───────┘     └──────────┬──────────┘
        │                         │
        v                         v
     Browser                External AI hosts
```

## 4. Database connection rules

### 4.1 Authoring Research Compiler

Recommended:

- long-running compiler/worker: direct PostgreSQL connection or an appropriate session pool;
- serverless/edge ingestion job: transaction pooler;
- bulk import/migration/backup: direct PostgreSQL connection.

Do not route high-volume compiler work through Product MCP.

Do not expose the authoring database Data API to public users.

Use a dedicated database role with only the schemas/tables the compiler requires.

### 4.2 Publication Worker

The Publication Worker is the only ordinary service allowed to bridge Authoring and Serving.

Credentials:

- Authoring DB: read-only publication-source role;
- Serving DB: restricted publication-writer role.

Avoid:

- public service-role credentials;
- browser credentials;
- direct database links such as a permanent cross-database FDW/dblink that defeats the publication firewall.

Publication should be an explicit application operation with:

- build ID;
- candidate release ID;
- validation record;
- audit log;
- component hashes;
- transaction boundary on target publication.

### 4.3 Public web application

For simple user workspace CRUD:

- browser -> Supabase client/Data API;
- RLS + grants required;
- only exposed schemas/tables.

For canonical public research reads:

either:

- Next.js/API -> Serving DB;
- or safe read-only Data API/views when the access pattern is simple.

For corpus search:

```text
Browser
 -> POST /api/v1/corpus/query/validate
 -> POST /api/v1/corpus/query/run
 -> application query service
 -> validated query plan
 -> Serving DB
```

Do not expose arbitrary SQL.

Do not let the browser directly assemble privileged RPC arguments that bypass application-level complexity limits.

### 4.4 Serverless connection mode

If the API is deployed as horizontally scaling serverless/edge functions, prefer transaction-pooled database access or the Supabase Data API/RPC instead of opening many direct long-lived PostgreSQL sessions.

### 4.5 Persistent service connection mode

For a long-running compiler, worker, or backend service, direct PostgreSQL connection is appropriate when network support permits it.

## 5. Public HTTP API versus Product MCP

These interfaces expose many of the same **domain capabilities** but serve different clients.

### Public HTTP API

Primary clients:

- first-party web app;
- mobile app;
- conventional third-party integrations.

Examples:

- `GET /api/v1/releases/current`
- `GET /api/v1/releases/{releaseId}/passages/{reference}`
- `GET /api/v1/releases/{releaseId}/passages/{reference}/analysis`
- `POST /api/v1/corpus/query/validate`
- `POST /api/v1/corpus/query/run`
- `GET /api/v1/constructions/{id}/instances`
- `GET /api/v1/evidence/{id}`

### Product MCP

Primary clients:

- model/agent hosts.

The MCP server should call the same application/domain service used by the HTTP API.

Do not implement separate scholarly logic inside MCP handlers.

Recommended initial MCP tools:

- `get_current_release`
- `get_passage`
- `get_published_analysis`
- `run_corpus_query`
- `get_construction_instances`
- `get_rule_applications`
- `get_evidence`
- `list_semantic_sets`

Recommended MCP resources:

- `hcbible://release/{releaseId}/passage/{reference}`
- `hcbible://release/{releaseId}/analysis/{reference}`
- `hcbible://release/{releaseId}/construction/{constructionId}`
- `hcbible://release/{releaseId}/evidence/{evidenceId}`

A resource URI must represent published/release-pinned data.

## 6. Product MCP permissions

Initial Product MCP:

- read-only;
- published data only;
- no authoring DB;
- no raw Drive source text;
- no publication action;
- no arbitrary SQL;
- no generic "run tool from text" endpoint.

If user-authenticated workspace MCP is added later, separate tools such as:

- `save_query`
- `create_translation_draft`
- `add_private_note`

must operate only on that user's workspace through normal authorization.

They must not mutate official ResearchRelease data.

## 7. Private Authoring MCP

A private Authoring MCP is optional.

Use only when a model/agent workbench genuinely benefits from agent-oriented access.

Potential tools:

- `search_registered_sources`
- `read_permitted_source_span`
- `find_passage_discussions`
- `propose_claim_extraction`
- `propose_concept_mapping`
- `list_review_queue`
- `submit_review_note`

Requirements:

- private network, secure tunnel, or authenticated remote MCP;
- rights resolver before source content is returned;
- audit every source span returned;
- no service-role secret in model-visible text;
- no tool may expand its own permissions because source content asks it to;
- source text is data, never instruction.

Publication is deliberately **not** an ordinary MCP tool in the first implementation.

If publication is ever exposed to an agent, it requires explicit human approval plus the same publication validation pipeline.

## 8. External scholarly discovery aggregation

Multi-provider scholarly discovery is a required private Authoring / Research Compiler capability.

Initial ensemble:

- OpenAlex;
- Semantic Scholar;
- CORE;
- Crossref;
- Scite.

Each provider may be reached by direct API or MCP, but both routes must pass through a project-owned adapter and normalize into the same internal contracts.

```text
ResearchIssue / ResearchTarget
   -> ResearchModelAdapter query expansion
   -> provider plan
      -> OpenAlex
      -> Semantic Scholar
      -> CORE
      -> Crossref
      -> Scite
   -> ScholarlyProviderRequest
   -> DiscoveryRecord
   -> Work identity resolution/dedup
   -> access + RightsPolicy
   -> evidence enrichment
   -> ResearchModelAdapter triage / claim candidates / synthesis
   -> review
   -> LiteratureSnapshot
   -> ResearchRelease
```

The build model is provider-neutral. GPT in ChatGPT/Codex, Gemini, Claude, local models, or future approved models may perform the model-assisted steps through the same ResearchModelAdapter.

Provider/API credentials remain private authoring secrets or MCP-managed credentials and never enter Git, DiscoveryRecords, LiteratureSnapshots, public responses, or the public BYOK path.

Do not make external paper search a hidden dependency of opening a public passage.

Canonical public research remains release-pinned.

See `architecture/scholarly-discovery-aggregation.md`.
## 9. FHL integration

Recommended production path:

```text
FHL API
  -> FHLProviderAdapter
      -> schema validation
      -> provider distribution mapping
      -> rights resolver
      -> snapshot/live binding decision
      -> application domain object
```

Optional research-agent path:

```text
AI Host
  -> FHL MCP
      -> FHL API
```

The FHL MCP implementation is therefore useful as:

- reference code;
- research tooling;
- an external MCP option.

It should not become the product's canonical internal provider abstraction.

## 10. Live provider versus release-pinned witness

The architecture must support:

- `SNAPSHOT_PINNED`
- `LIVE_EXTERNAL`

If rights permit storing the provider text:

- persist the approved snapshot;
- hash it;
- bind the ResearchRelease to that snapshot.

If rights do not permit persistent content:

- store provider locator;
- provider distribution/version metadata;
- observed hash where allowed;
- observed timestamp;
- mark the public witness as `LIVE_EXTERNAL`.

A release containing a live external witness must not claim that the witness text itself is byte-for-byte immutable.

## 11. API/MCP idempotency and traceability

Every state-changing internal API must support:

- request ID;
- actor/service identity;
- idempotency key where retry is possible;
- audit record;
- explicit build/release/workspace target.

Every public/MCP read response should expose where relevant:

- `research_release_id`;
- source/corpus component versions;
- evidence IDs;
- result epistemic class.

## 12. Why MCP should not connect directly to PostgreSQL

Direct database MCP exposure would create several problems:

- duplicates authorization logic;
- bypasses domain validation;
- risks arbitrary query generation;
- makes release pinning optional;
- weakens complexity guards;
- couples protocol surface to schema internals;
- makes schema refactors public API breaking changes;
- increases accidental access to private authoring data.

The Product MCP should expose **research capabilities**, not database tables.

## 13. Supabase MCP scope

Supabase MCP may be used by developers/agents for:

- schema inspection;
- development SQL;
- advisors;
- migration/debug workflows.

It is not:

- the public Product MCP;
- a provider MCP;
- a runtime database gateway for end users.

This distinction must be explicit in documentation and environment configuration.

## 14. Failure containment

### FHL unavailable

Public release-pinned local data still works.

A `LIVE_EXTERNAL` witness reports provider unavailable without breaking passage analysis.

### LLM unavailable

Pattern Builder, DSL, published analysis, corpus search, citations and Product MCP deterministic tools continue to work.

Natural-language query interpretation is unavailable/degraded only.

### Authoring DB unavailable

Public Serving remains available.

### Product MCP unavailable

First-party web app remains available through HTTP API.

### Public HTTP API unavailable

Product MCP may also be unavailable if both share the same domain service deployment. This is acceptable; deploy separate gateways only if availability requirements justify it.

## 15. Current decision

Use MCP at **agent boundaries**.

Use HTTP/service APIs at **application boundaries**.

Use PostgreSQL/Data API/RPC at **data boundaries**.

Use a publication worker at the **private-to-public trust boundary**.

Do not use MCP as the internal application bus.


## 16. Public runtime AI BYOK boundary

Runtime AI is optional and BYOK-only.

Approved flow:

```text
Browser
 -> user enters Gemini/provider credential
 -> volatile browser memory
 -> AI-specific HTTPS request
 -> ephemeral BYOK relay / provider adapter
 -> selected provider
```

The BYOK relay is not a credential vault.

It must not:

- store provider credentials;
- create database rows for provider credentials;
- read a platform model credential;
- use a Vercel/Supabase/shared model secret;
- enqueue provider credentials;
- log provider credentials;
- silently fall back to a product-funded provider key.

The first-party non-AI APIs do not accept provider credentials.

The Product MCP also does not carry the user's Gemini credential by default. If a future MCP host supplies its own provider credential, that is the host/provider relationship and requires a separate tool-auth design.

Runtime AI states are explicit:

- BYOK_AVAILABLE
- BYOK_MISSING
- BYOK_INVALID
- PROVIDER_UNAVAILABLE
- FEATURE_DISABLED

Gemini is the first provider implementation, but provider credentials remain opaque and provider-neutral at the domain layer.
