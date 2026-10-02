# ADR-003: MCP Is an Agent Boundary, Not the Internal Data Bus

Status: **ACCEPTED**
Date: 2026-10-03

## Context

The product will interact with external providers such as FHL, private source libraries, future academic-paper databases, AI/model hosts, Supabase/PostgreSQL, and a first-party web application.

Several of these ecosystems may expose MCP servers.

This creates a risk of using MCP as a generic synonym for any system integration.

## Decision

1. MCP is used at agent/model-facing capability boundaries.
2. Internal service-to-service and service-to-database communication does not require MCP.
3. The first-party web app uses HTTP/domain APIs and database access appropriate to its trust boundary.
4. The Research Compiler uses direct/pooled private database connections and source adapters.
5. The Publication Worker reads Authoring and writes Serving using restricted database roles.
6. Product MCP is a facade over shared domain/application services; it does not directly query database tables.
7. Supabase MCP is development/admin tooling, not a runtime product gateway.
8. FHL MCP is useful for research-agent interaction, but production FHL integration uses a provider adapter over the underlying API.
9. Future academic-paper MCPs enter only through the private Authoring/Research source-adapter boundary unless a separate rights-approved public feature is explicitly designed.
10. Initial Product MCP is read-only over published ResearchRelease data.

## Rationale

MCP is designed to expose tools/resources/prompts to AI hosts.

The product's internal data path requires deterministic query semantics, release pinning, rights enforcement, stable first-party APIs, transaction control, database connection management, and predictable failure isolation.

Making MCP the internal data bus would add an unnecessary agent-protocol dependency and would make database/schema internals easier to expose accidentally.

## Consequences

Positive:

- one domain implementation serves HTTP and MCP;
- first-party app is independent of MCP availability;
- agents cannot bypass query validation;
- database schema can evolve behind the domain API;
- authoring data stays isolated;
- FHL/paper provider MCPs remain replaceable adapters.

Cost:

- HTTP API and MCP facade both need schemas/adapters;
- shared application service layer must be explicit;
- tool/resource versioning must track public API/release semantics.

The additional adapter cost is accepted because it preserves the product's security and research boundaries.
