# Multi-Provider Scholarly Discovery and Research Compilation

Status: **ACTIVE AUTHORING / RESEARCH-COMPILER ARCHITECTURE**

Date: 2026-10-03

This document makes the Sacred Studies multi-provider research pattern a formal part of the Hebrew-Chinese Bible Research product.

It does **not** make Sacred Studies a runtime dependency and does **not** copy its credential handling or runtime synthesis design.

The product requirement is the method:

```text
ResearchTarget / ResearchIssue
  -> query planning and expansion
  -> OpenAlex
  -> Semantic Scholar
  -> CORE
  -> Crossref
  -> Scite
  -> normalized DiscoveryRecords
  -> identity resolution / deduplication
  -> access + rights resolution
  -> evidence enrichment
  -> model-assisted triage / synthesis
  -> ResearchIssue / ResearchPosition / claims
  -> LiteratureSnapshot
  -> human/review gates
  -> ResearchRelease
```

The model used for query expansion, triage, claim extraction, clustering, counterevidence planning, or synthesis is replaceable. It may be GPT in ChatGPT/Codex, Gemini, Claude, another approved hosted model, or a local model. Gemini is **not** a build-time architecture dependency.

---

## Sacred Studies method parity

The exact scholarly-search/questioning method used for this compiler is defined in `architecture/sacred-studies-research-method.md` and `contracts/v1.1/scholarly-research-method.json`.

The method preserves the Sacred Studies Text × Topic × Lens search matrix, concise English academic query optimization, all-era + recent-scholarship coverage, academic-source filtering, zero-hallucination librarian dossier, evidence-grounded synthesis, and three-attempt 88/100 critical review/revision loop.

Implementation defects in the reference app are not normative. In particular, disconnected provider helpers, hard-coded credentials, stale date windows, and reviewer-parse auto-pass behavior are explicitly rejected.

# 1. Why this exists

The curated Google Drive library is mandatory but cannot represent the entire scholarly universe.

The database-building process must also search current and specialist scholarship across large external scholarly indexes.

The initial provider ensemble is:

1. OpenAlex
2. Semantic Scholar
3. CORE
4. Crossref
5. Scite

Additional API or MCP providers may be added without changing canonical Work, DiscoveryRecord, ResearchIssue, ResearchPosition, or LiteratureSnapshot identity.

A provider is a discovery/evidence source, not the canonical scholarly database.

---

# 2. Provider roles are complementary

The system must not treat every provider as interchangeable.

## 2.1 OpenAlex

Primary role:

- broad scholarly discovery;
- works/authors/sources/institutions graph;
- citation/reference graph enrichment;
- open-access locations;
- large-scale search and filtering.

## 2.2 Semantic Scholar

Primary role:

- paper and author discovery;
- abstract/citation metadata;
- citation/reference graph enrichment;
- complementary ranking and bibliographic cross-check.

## 2.3 CORE

Primary role:

- open-access discovery;
- repository coverage;
- full-text/open-copy resolution where available;
- machine-readable OA metadata/full text.

## 2.4 Crossref

Primary role:

- DOI resolution;
- authoritative DOI registration metadata;
- bibliographic identity verification;
- publication type, licence and post-publication metadata where deposited.

Crossref is an identity/metadata authority, not the preferred full-text search engine.

## 2.5 Scite

Primary role:

- full-text/citation-statement search where licensed/available;
- citation context;
- supporting / contrasting / mentioning evidence;
- editorial/retraction/correction signals;
- access resolution and full-text evidence where entitlement permits.

## 2.6 Provider capability routing

A research run does not have to issue the same query to every provider mechanically.

The orchestrator builds a provider plan from declared capabilities.

Example:

```text
broad discovery
  -> OpenAlex + Semantic Scholar

DOI identity check
  -> Crossref

OA/full-text route
  -> CORE + OpenAlex locations

citation-context / support-contrast check
  -> Scite

coverage gap / cross-check
  -> fan out to remaining eligible providers
```

However, a LiteratureSnapshot claiming multi-provider coverage must record which providers were queried, skipped, unavailable, rate-limited, or excluded by rights/entitlement.

---

# 3. API and MCP are transport choices, not domain semantics

A provider may be connected through:

- direct REST/API adapter;
- provider MCP;
- an MCP wrapper around the provider API;
- another authenticated machine interface.

All routes normalize into the same internal ScholarlyDiscoveryProvider contract.

For reproducible batch compilation, direct provider APIs are preferred when stable and licensed.

MCP is appropriate when:

- the provider officially exposes MCP;
- the authoring host already has a connected MCP;
- the MCP exposes the required evidence with sufficient provenance;
- the adapter records the provider/tool/version and returned evidence.

No canonical object may depend on whether transport was API or MCP.

---

# 4. Private database-build workflow

## 4.1 Seed research target

Every run begins from one or more typed targets:

- passage/reference span;
- biblical book;
- lexeme;
- morpheme/form;
- construction;
- concept;
- textual variant;
- translation issue;
- existing ResearchIssue.

## 4.2 Seed research question

A human, rule, previous snapshot, or build model creates a bounded seed question.

Example:

```text
ResearchTarget:
1 Samuel 16:7

ResearchIssue seed:
What semantic/syntactic functions have scholars assigned to ל in לַעֵינַיִם,
and what comparative Biblical Hebrew evidence is used?
```

## 4.3 Query expansion

The ResearchModelAdapter may generate multiple search formulations.

Typical expansion dimensions:

- standard English biblical reference;
- Hebrew lemma/form;
- transliteration variants;
- grammatical terminology;
- historical terminology used by older grammars;
- modern linguistic terminology;
- translation-studies terminology;
- construction-level terminology;
- broader and narrower synonyms;
- author/work names already known from the curated library;
- counter-position / disagreement terms.

The output is a **query plan**, not scholarly evidence.

Each expanded query records:

- seed query;
- expanded query;
- language;
- query purpose;
- generated_by;
- research model run ID where AI-assisted;
- prompt/template version;
- query order;
- intended provider capabilities.

## 4.4 Multi-provider fan-out

The query plan is executed against the eligible provider ensemble.

Each provider request records:

- provider;
- adapter version;
- transport mode: DIRECT_API or MCP;
- provider dataset/index version where exposed;
- provider query syntax version where exposed;
- exact query;
- filters;
- sort/ranking mode;
- pagination/cursor;
- requested limit;
- execution timestamp;
- response hash;
- returned count;
- error/rate-limit state.

Provider failure never authorizes the model to fill missing records from memory.

## 4.5 Normalize into DiscoveryRecord

Every provider hit becomes or updates an ExternalDiscoveryRecord.

The record preserves:

- provider identity;
- provider record ID;
- raw title/authors/year/type identifiers;
- DOI/ISBN where supplied;
- abstract only when actually supplied;
- source/access URL;
- access level;
- retrieval timestamp;
- payload hash;
- raw-payload storage policy;
- rights decision snapshot where persistence requires one;
- originating provider request/query provenance.

A result with only metadata remains METADATA_ONLY.

A result with only abstract remains ABSTRACT_ONLY.

A result with citation context remains CITATION_CONTEXT_ONLY unless separate full-text access is established.

## 4.6 Identity resolution and deduplication

The same paper returned by five providers must become one canonical Work/Edition identity, not five scholarly works.

Resolution precedence:

1. exact DOI/PID match;
2. exact ISBN/edition identifier where applicable;
3. trusted provider crosswalk;
4. normalized title + author + year fingerprint;
5. manual resolution;
6. AI-assisted resolution as candidate only.

AI-assisted resolution cannot become VERIFIED solely because the model is confident.

All contributing DiscoveryRecords remain attached to the canonical Work for provenance.

## 4.7 Access and rights resolution

Bibliographic discovery and content permission are separate.

For each work/source route determine:

- metadata available;
- abstract available;
- citation context available;
- open full text available;
- licensed full text available;
- private-library copy available;
- no readable content available.

RightsPolicy decides independently whether content may be:

- stored;
- extracted;
- embedded;
- sent to a research model;
- quoted;
- displayed;
- exported;
- published.

Provider search access never implies permission to persist provider raw payload/full text.

## 4.8 Evidence enrichment

After identity resolution, adapters may enrich selected works with:

- references;
- citations;
- citation contexts;
- supporting/contrasting/mentioning tallies;
- retraction/correction/expression-of-concern status;
- OA locations;
- permitted full text or excerpts;
- related works.

Enrichment is selective and auditable. It is not a requirement to download every result.

## 4.9 Model-assisted relevance triage

A ResearchModelAdapter may classify candidate works by:

- direct passage relevance;
- lexical relevance;
- grammatical relevance;
- construction relevance;
- textual-critical relevance;
- historical/literary relevance;
- translation relevance;
- methodological context;
- likely counterevidence;
- irrelevant/noise.

The model must receive the actual provider metadata/abstract/permitted source text used for the classification.

It must not classify from title-only evidence while recording abstract/full-text review.

## 4.10 Candidate claim extraction

Where rights and access permit, the model may propose:

- claims;
- definitions;
- qualifications;
- exceptions;
- methodological commitments;
- biblical examples;
- ResearchIssue mappings;
- ResearchPosition mappings;
- scholarly dependencies.

These are candidate scholarly representations.

They preserve source spans/locators and remain unreviewed until the required review event is satisfied.

## 4.11 Counterevidence pass

Every material research issue requires an explicit counterevidence/disagreement pass.

The model may generate additional queries such as:

- critique terms;
- alternative terminology;
- opposing interpretation labels;
- later reassessment;
- response/rejoinder;
- correction/retraction;
- competing grammatical classifications.

A one-direction search is not sufficient for a field-state claim.

## 4.12 ResearchIssue / ResearchPosition compilation

Reviewed candidate evidence is organized into versioned ResearchIssues and ResearchPositions.

The model may propose clustering, but:

- work count is not correctness;
- citation count is not correctness;
- Scite supporting/contrasting classification is evidence about citation context, not a final theological/linguistic verdict;
- consensus/minority language remains snapshot-bounded and reviewed.

## 4.13 LiteratureSnapshot compilation

A LiteratureSnapshot freezes:

- search run identities;
- provider requests;
- exact expanded queries;
- date coverage;
- languages/publication types;
- inclusion/exclusion decisions;
- canonical included Works;
- provider/index/adapter metadata;
- model-run provenance;
- coverage limitations;
- unresolved access gaps;
- review status.

The snapshot is auditable. Exact provider result replay is claimed only when the provider supports it.

## 4.14 Publication

Only reviewed scholarly objects cross the publication firewall.

Live provider output never directly rewrites:

- CommentaryEntry;
- TranslationDecision;
- project Chinese rendering;
- ResearchPosition;
- published LiteratureReviewSnapshot.

A new discovery cycle produces a new candidate build and, after review, a new ResearchRelease.

---

# 5. ResearchModelAdapter

## 5.1 Core rule

The research model is replaceable infrastructure.

The architecture must never contain:

```text
Gemini is the scholarly engine
```

Instead:

```text
ResearchCompiler
  -> ResearchModelAdapter
      -> GPT / Gemini / Claude / local / future approved model
```

## 5.2 Build-time model tasks

Allowed task types include:

- QUERY_EXPANSION;
- QUERY_NORMALIZATION;
- SEARCH_STRATEGY_DRAFT;
- RESULT_TRIAGE;
- RELEVANCE_CLASSIFICATION;
- BIBLIOGRAPHIC_RESOLUTION_SUGGESTION;
- COUNTEREVIDENCE_QUERY_GENERATION;
- CANDIDATE_CLAIM_EXTRACTION;
- ISSUE_CLUSTERING;
- POSITION_CLUSTERING;
- SCHOLARLY_DEPENDENCY_SUGGESTION;
- SYNTHESIS_DRAFT;
- LITERATURE_REVIEW_DRAFT.

## 5.3 Build-time model provenance

Every material model operation records:

- research_model_run_id;
- task type;
- provider/model family where available;
- concrete model ID/version where exposed;
- host environment, e.g. ChatGPT/Codex, Gemini API, Claude, local worker;
- prompt/template version;
- input object IDs/evidence IDs;
- input hash;
- output hash;
- execution timestamp;
- provenance activity ID;
- review status;
- failure/partial status.

If the site/database is being built by GPT in ChatGPT/Codex, that is a valid ResearchModelAdapter execution.

If another build uses Gemini, the same contracts apply.

Model replacement must not require database ontology changes.

## 5.4 Model limitations

The build model must never:

- invent provider results not returned by a provider;
- invent inaccessible full-text reading;
- turn title/abstract evidence into a full-text claim;
- create a canonical Work solely from model memory;
- silently merge ambiguous bibliographic identities;
- mark its own claims VERIFIED;
- infer field consensus from ranking/citation count alone;
- bypass RightsPolicy;
- write directly to a published ResearchRelease.

---

# 6. Initial provider ensemble requirement

The first Research Pro scholarly-discovery implementation must include adapters for:

- OPENALEX;
- SEMANTIC_SCHOLAR;
- CORE;
- CROSSREF;
- SCITE.

An adapter may initially support only the subset of provider capabilities actually available under the project's account/terms.

The implementation must expose capability discovery rather than pretending unsupported operations exist.

A provider being temporarily unavailable may degrade coverage but must be recorded in the LiteratureSnapshot.

---

# 7. Database contract additions

The database contract extends the existing Research Pro objects with:

## 7.1 scholarly_discovery_provider_adapters

Tracks one implementation of one provider connection.

Fields conceptually include:

- provider adapter ID;
- scholarly discovery provider ID;
- adapter version;
- transport mode;
- capability set;
- active state;
- configuration profile ID/reference excluding raw credentials;
- implementation metadata.

Raw credentials are never stored in this table.

## 7.2 research_model_runs

Records model-assisted authoring operations.

This is provenance, not a model credential store.

## 7.3 literature_search_queries

Existing table remains authoritative for generated queries and gains a link to research_model_run_id when AI-assisted.

## 7.4 literature_search_provider_requests

Existing table remains authoritative for per-provider execution and gains adapter/transport traceability.

## 7.5 DiscoveryRecord provenance

Every discovery record created through a literature search must be traceable to the provider request that produced it.

Direct one-off provider retrievals use the same provider-request abstraction.

---

# 8. Credentials and secrets

The Sacred Studies reference implementation must **not** be copied literally in credential handling.

Rules:

- no OpenAlex/Semantic Scholar/CORE/Crossref/Scite secret in Git;
- no hard-coded provider key;
- no example file containing a live-looking real key;
- no provider credential in DiscoveryRecord, LiteratureSnapshot, provenance text, log, fixture or public response;
- private authoring credentials live only in approved secret/config infrastructure;
- MCP-managed credentials remain inside the MCP/provider connection;
- public runtime does not inherit private scholarly-provider credentials.

Provider credentials and public model BYOK are separate security domains.

---

# 9. Private build versus public runtime

## Private database/research build

May use:

- all five scholarly providers;
- provider APIs/MCPs;
- the curated Drive library;
- approved private full text;
- a ResearchModelAdapter such as GPT or Gemini;
- large batch jobs;
- human review.

## Public app

Primarily serves:

- release-pinned LiteratureSnapshots;
- reviewed ResearchIssues/Positions;
- reviewed CommentaryEntries;
- published evidence;
- release-pinned bibliography and access routes.

Optional live Research Pro discovery is explicitly marked DISCOVERED_SINCE_RELEASE and cannot alter the release.

The public app must not depend on all five providers being online to open a passage.

---

# 10. Sacred Studies lineage

The design deliberately preserves the useful architectural idea demonstrated in:

`AvodaConsulting/sacred-studies-2`

namely:

```text
academic question
 -> model-assisted query formulation
 -> multiple academic providers
 -> aggregated scholarly results
 -> model-assisted synthesis
```

This project strengthens that pattern by adding:

- canonical bibliographic identity;
- explicit provider capabilities;
- complete search-run provenance;
- access-level honesty;
- rights enforcement;
- deduplication;
- counterevidence;
- ResearchIssue/ResearchPosition versioning;
- LiteratureSnapshot;
- review gates;
- immutable ResearchRelease;
- model-provider neutrality.

The old application is a design reference, not a runtime dependency.

---

# 11. Acceptance criteria

The scholarly-discovery database-build method is not considered implemented until a test research issue can:

1. generate multiple expanded queries from one seed issue;
2. record which research model produced the expansions;
3. execute against OpenAlex, Semantic Scholar, CORE, Crossref and Scite adapters, with explicit unavailable/skipped states;
4. persist normalized DiscoveryRecords without persisting forbidden raw payloads;
5. resolve duplicate records from multiple providers to one canonical Work;
6. preserve every contributing provider record;
7. distinguish metadata/abstract/citation-context/full-text evidence;
8. resolve access and rights before model-context/full-text processing;
9. extract candidate claims with source locators where content access permits;
10. perform a counterevidence/disagreement search pass;
11. compile reviewed evidence into ResearchIssue/ResearchPosition objects;
12. build a LiteratureSnapshot containing search/model/provider provenance and coverage limitations;
13. produce a new candidate ResearchBuild without mutating an existing ResearchRelease;
14. pass with GPT, Gemini, or another approved ResearchModelAdapter without schema changes;
15. contain no academic-provider or model-provider secret in source code or fixtures.
