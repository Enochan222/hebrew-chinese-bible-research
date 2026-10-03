# ADR-006: Multi-Provider Scholarly Discovery Compiler

Status: ACCEPTED
Date: 2026-10-03

## Context

The product must build a scholarly database that reaches beyond the curated private library and can discover current/specialist literature at scale.

The earlier Sacred Studies application demonstrated a useful pattern: model-assisted query formulation followed by aggregation across multiple academic providers. The Hebrew-Chinese Bible Research product needs the same method, but with stronger identity, rights, provenance, review, and publication controls.

## Decision

The private Research Compiler uses a multi-provider scholarly discovery ensemble with initial adapters for OpenAlex, Semantic Scholar, CORE, Crossref, and Scite.

Providers may be reached by direct API or MCP. Transport does not change domain semantics.

Model-assisted query expansion, triage, candidate claim extraction, counterevidence planning and synthesis use a replaceable ResearchModelAdapter. No build-time model vendor is canonical. GPT, Gemini, Claude, local models, or future approved models may be used without changing the database ontology.

All provider hits normalize to DiscoveryRecords, resolve to canonical Work identities, pass RightsPolicy, and enter LiteratureSnapshots only through review/compilation.

Live discovery never mutates an existing ResearchRelease.

## Consequences

- broad discovery does not depend on one provider;
- DOI/metadata, OA/fulltext, citation-context and integrity signals can be sourced from different specialists;
- the build can be executed by GPT in ChatGPT/Codex or another model host;
- model/provider provenance becomes part of the research audit trail;
- provider outages reduce documented coverage rather than causing silent model-memory substitution;
- provider credentials remain private authoring/MCP secrets and never enter source control or public BYOK flows.

## Rejected alternatives

- one-provider-only scholarly search;
- Gemini-hard-coded research compilation;
- model memory as a fallback literature database;
- direct provider results becoming public commentary without review;
- public passage rendering depending on five live academic providers.
