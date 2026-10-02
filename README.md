# Hebrew-Chinese Bible Research

Research-grade Hebrew Bible and Chinese translation **data product and research platform**.

## Current project status

**Architecture correction / pre-implementation stage.**

Do not implement the superseded v1 database contract.

The active architecture is the amended **v1.1 candidate**, which is not yet frozen.

## Product definition

This project is not primarily a runtime AI/RAG app.

It is designed as:

```text
Private Scholarly Authoring / Research Compiler
        ↓
Publication Validation / Firewall
        ↓
Immutable ResearchRelease
        ↓
Deterministic Public Research Product
        +
User Workspace
        +
Optional Natural-Language Query Adapter
```

Core public research must remain usable without an LLM provider.

## Four logical product planes

1. **Authoring / Research**
   - source books
   - extraction/OCR
   - RAG/embeddings
   - AI candidate extraction/mapping
   - editorial review

2. **Publication / Control**
   - rights/citation/benchmark validation
   - serving projection compilation
   - release manifest
   - publish/supersede/revoke/rollback

3. **Public Serving**
   - versioned Hebrew corpus
   - published translations
   - published analyses
   - semantic sets
   - constructions
   - rule applications
   - deterministic search

4. **User Workspace**
   - saved queries
   - annotations
   - translation drafts
   - user semantic sets/rule drafts

## Core research distinction

```text
Reference location
  != textual expression
  != linguistic segmentation
  != syntactic analysis
  != corpus construction
  != interpretive rule
  != translation decision
  != published analysis
  != AI synthesis
```

In practical terms:

- reference anchors may be application-owned;
- textual expressions are edition/expression-specific;
- tokenisation, phrase/clause structure and dependency are framework-scoped;
- cross-corpus mappings are explicit research data;
- provider codes do not automatically equal print editions;
- source text and AI-extracted scholarly propositions are distinct;
- corpus pattern matching is not itself a translation conclusion;
- canonical public analysis is release-pinned.

## Active architecture documents

Start here:

- `architecture/product-platform-and-publication-model.md`
- `architecture/database-api-cross-stage-contract-v1.1-candidate.md`
- `architecture/site-build-staging-plan.md`
- `contracts/v1.1/vocabulary.json`
- `architecture/academic-evidence-policy.md`
- `architecture/academic-storage-and-rag.md`
- `architecture/security-trust-boundaries.md`
- `architecture/research-evaluation-and-benchmarks.md`
- `docs/academic-source-taxonomy.md`
- `docs/master-academic-source-inventory-and-gaps.md`

Architecture decisions:

- `architecture/adr/001-framework-scoped-text-analysis.md`
- `architecture/adr/002-compiled-research-product.md`

Superseded design history:

- `architecture/database-api-cross-stage-contract-v1.md`
- `architecture/source-taxonomy-storage-rag.md`

## Academic source library

The reorganized Google Drive library now contains substantial coverage in:

- major Hebrew reference grammars;
- learning grammars;
- morphology and language history;
- BDB / DCH / HALOT holdings;
- theological lexica;
- concordances;
- BHS / Masorah;
- BHQ Ruth materials;
- textual criticism;
- DSS/Judaean Desert;
- Genesis 1-11 commentary;
- exegesis method;
- archaeology/background.

The current largest source gaps are:

- Chinese Bible translation scholarship/documentation;
- current specialist article-level research;
- whole-Bible commentary coverage;
- whole-Bible BHQ coverage;
- machine-readable LXX corpus resources;
- formal rights/edition metadata.

See:

- `docs/master-academic-source-inventory-and-gaps.md`

## Product build phases

1. Product foundation + release model + serving shell
2. Passage translations + alignment + workspace
3. Hebrew corpus + semantic sets + construction/query engine
4. Private academic knowledge compiler + publication pipeline
5. Rules + published analyses + optional NL-to-DSL + product operations

The Research Compiler remains a permanent subsystem after Phase 5.

## Runtime AI policy

Optional runtime AI may interpret natural language into a constrained CorpusQuery AST.

It must not:

- generate arbitrary SQL for execution;
- determine corpus membership;
- access private authoring source books through public runtime;
- silently create canonical claims/rules;
- modify the active research release.

Visual Pattern Builder and DSL search must work without AI.

## Development rule

A later build phase must extend the existing product.

It must not silently replace:

- canonical vocabulary;
- ontology;
- rights semantics;
- product-plane boundaries;
- release semantics;
- corpus-query relations;
- rule kinds;
- earlier working functionality.

Do not deploy to Vercel until explicitly requested.
