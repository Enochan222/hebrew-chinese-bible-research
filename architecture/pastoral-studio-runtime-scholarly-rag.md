# Pastoral Studio Runtime-Derived Scholarly Retrieval and RAG Method

Status: **ACTIVE AUTHORING / RESEARCH-COMPILER METHOD**

Date: 2026-10-04

## 1. Decision

The Hebrew-Chinese Bible Research private database-build process adopts the scholarly retrieval orchestration verified in the deployed Pastoral Studio production workflow, while retaining this project's stronger database, provenance, rights, deduplication, review, and publication controls.

This is **behavioral/method parity**, not source-code copying.

The method to preserve is:

```text
ResearchTarget + ResearchIssue
  -> Text × Topic × Lens framing
  -> academic query planning / expansion
  -> source-specialized parallel retrieval
  -> provider-specific fallback/degraded-status handling
  -> bibliographic normalization + Work identity resolution
  -> content/access/rights resolution
  -> citation/integrity enrichment
  -> Librarian evidence dossier
  -> candidate claim extraction + counterevidence pass
  -> model-assisted synthesis
  -> critical review / revision
  -> human scholarly review
  -> LiteratureSnapshot / ResearchBuild
  -> immutable ResearchRelease
```

The deployed Pastoral Studio is a lineage/reference implementation for how retrieval is orchestrated. It is not a canonical datastore and is not a runtime dependency of this product.

## 2. Production-runtime behavior that informs this method

A production Academic Biblical Study run was verified against the deployed Pastoral Studio application using a Hebrew-Bible research question on 1 Samuel 16:7.

The visible production research log demonstrated a fan-out/enrichment pattern involving:

- Sefaria for Masoretic text / Jewish commentary retrieval;
- Scite for Smart Citation and citation-context/integrity enrichment;
- CORE for open-access retrieval, with explicit failure/fallback behavior when authentication failed;
- OpenAlex for broad academic discovery;
- Crossref for DOI/bibliographic metadata;
- Open Library / Internet Archive for digitized historical book/commentary discovery;
- a Librarian model stage after retrieval;
- a later Writer / synthesis stage with model fallback.

The production verification did not establish Semantic Scholar participation in that particular run. This project nevertheless keeps Semantic Scholar in the required initial scholarly-provider ensemble because it adds complementary paper/citation-graph coverage.

The architectural lesson is that retrieval happens before synthesis, providers have different roles, individual provider failure is recorded rather than silently replaced by model memory, and later model stages consume a gathered evidence dossier.

## 3. Retrieval stages

### 3.1 Primary-text and curated-library retrieval

Begin with deterministic/source-aware retrieval from:

- canonical Hebrew corpus and textual layers;
- the curated private Google Drive scholarly library where rights permit;
- source-specific biblical/reference systems such as Sefaria when relevant and permitted.

This stage is not generic vector RAG. Passage identity, edition, corpus layer, source role, and rights remain explicit.

### 3.2 Academic query planning

Use the canonical Text × Topic × Lens matrix.

The ResearchModelAdapter may produce exact, broader, terminology-variant, Hebrew/transliteration, historical, recent, counter-position, and known-author/work queries.

Queries should normally be concise English academic search strings with standard book names and approximately 3-6 key terms/phrases, while retaining useful Hebrew or technical terminology.

Query generation is search planning, not evidence.

### 3.3 Multi-provider fan-out

Required initial scholarly-provider ensemble:

- OpenAlex;
- Semantic Scholar;
- CORE;
- Crossref;
- Scite.

Auxiliary/source-specialized retrieval may include:

- Sefaria;
- Open Library / Internet Archive;
- the curated private Drive library;
- other approved specialist sources.

Typical routing:

```text
broad paper discovery
  -> OpenAlex + Semantic Scholar

bibliographic/DOI identity
  -> Crossref

OA location/full-text route
  -> CORE + OpenAlex OA locations

citation context / support-contrast / integrity
  -> Scite

Hebrew/Jewish source retrieval
  -> canonical corpus + Sefaria where appropriate

historical digitized monographs/commentaries
  -> Open Library / Internet Archive

private owned/curated scholarship
  -> Google Drive scholarly library
```

### 3.4 Explicit degraded-mode handling

One failed provider does not automatically abort the whole scholarly search when other evidence routes remain available.

Every provider attempt must resolve to a recorded state such as SUCCEEDED, FAILED, RATE_LIMITED, UNAVAILABLE, or SKIPPED.

Fallback is permitted only as an explicit retrieval-route change.

Forbidden:

```text
provider failed
  -> ask model to invent/remember what provider would have returned
```

Permitted:

```text
CORE unavailable
  -> record CORE failure
  -> continue other eligible retrieval routes
  -> record coverage limitation in LiteratureSnapshot
```

### 3.5 Normalization and deduplication

Unlike Pastoral Studio's immediate-generation workflow, this project must normalize provider hits before synthesis.

Each returned item becomes a DiscoveryRecord and resolves toward canonical Work, Edition/publication expression where applicable, and SourceAsset/provider locator.

The same DOI/paper returned by multiple providers remains one scholarly Work with multiple provider records.

### 3.6 Access and rights resolution

Before content enters model context, determine whether the project has metadata only, abstract, citation context, open full text, licensed full text, or private full text.

RightsPolicy independently decides model context, extraction, storage, embedding, quotation, display, and publication.

Discovery is not permission.

### 3.7 Evidence enrichment

After identity resolution, perform appropriate enrichment:

- DOI metadata reconciliation;
- citation/reference graph;
- citation-context retrieval;
- supporting/contrasting/mentioning signals;
- retraction/correction/integrity checks;
- OA/full-text location resolution;
- passage/source-specific commentary retrieval.

Scite-style enrichment is a later evidence layer, not a substitute for reading the underlying work where content access permits.

### 3.8 Librarian dossier

Only after retrieval/normalization should the Librarian model assemble an evidence dossier containing canonical Works, provider provenance, access level, locators, actually accessible evidence, relevance, source-specific findings, disagreement, coverage gaps, and provider failures.

The Librarian may organize and triage evidence but cannot create missing sources.

### 3.9 Claim extraction, counterevidence, and synthesis

Model-assisted steps may extract candidate claims with locators, classify relevance, cluster ResearchPositions, generate counterevidence searches, draft literature reviews, and draft translation/exegetical synthesis.

All outputs remain candidate scholarly objects until review.

A material ResearchIssue must include an explicit counterevidence/disagreement pass before representing a field state.

### 3.10 Review and publication

Retain the Sacred Studies/Pastoral Studio critical-review loop as an authoring QA layer:

- threshold 88/100;
- maximum three model review/revision attempts;
- malformed reviewer output = REVIEW_INCOMPLETE;
- model pass != human scholarly approval.

Publication still requires human/review/publication gates and an immutable ResearchRelease.

## 4. What is deliberately improved over Pastoral Studio

Pastoral Studio-style immediate output:

```text
retrieve
  -> Librarian
  -> Writer
  -> result
```

Hebrew-Chinese Bible Research:

```text
retrieve
  -> provider request provenance
  -> DiscoveryRecord
  -> Work/Edition identity
  -> dedup
  -> access + RightsPolicy
  -> evidence enrichment
  -> Librarian dossier
  -> candidate claims / issues / positions
  -> counterevidence
  -> review
  -> LiteratureSnapshot
  -> ResearchBuild
  -> ResearchRelease
```

This distinction is mandatory.

## 5. RAG definition in this project

RAG does not mean one vector database.

The authoring compiler uses hybrid retrieval:

- deterministic biblical corpus query;
- reference-aware commentary lookup;
- structured lexicon/grammar lookup;
- private-library full-text/section retrieval where permitted;
- scholarly-provider metadata/abstract/full-text retrieval;
- citation-context enrichment;
- embeddings/semantic search only where useful and legally permitted.

AI synthesis occurs after these retrieval lanes have been assembled.

## 6. Model neutrality

The retrieval method is independent of model vendor.

ResearchModelAdapter may be implemented by GPT/ChatGPT/Codex, Gemini, Claude, a local model, or another approved model.

The model receives only evidence that the build actually retrieved and is permitted to send to model context.

## 7. Reproducibility requirement

Every literature build must preserve enough data to reconstruct the ResearchIssue/version, query plan, exact provider requests, provider statuses and failures, DiscoveryRecords, Work-resolution decisions, access/rights decisions, enrichment operations, model runs/prompt versions, included/excluded evidence, counterevidence pass, LiteratureSnapshot, and final ResearchRelease linkage.

A public passage request must never rerun this whole pipeline merely to display canonical scholarship.
