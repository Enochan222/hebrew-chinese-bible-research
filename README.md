# Hebrew-Chinese Bible Research

Research-grade Hebrew Bible and Chinese translation analysis platform.

## Current project status

**Architecture correction / pre-implementation stage.**

Do not implement the superseded v1 database contract.

The active architecture is the **v1.1 candidate**, which is not yet frozen. The project is intentionally delaying Site Build implementation until the load-bearing identity, rights, security and evaluation contracts pass the v1.1 freeze checks.

## Core research principle

The application separates:

1. Biblical / textual corpus evidence
2. Translation witnesses and alignments
3. Academic literature
4. User research and AI analysis

AI synthesis is downstream of retrieved evidence. It must not fabricate corpus membership, scholarly claims, translator intention or consensus.

## Active architecture documents

Start here:

- `architecture/database-api-cross-stage-contract-v1.1-candidate.md`
- `contracts/v1.1/vocabulary.json`
- `architecture/site-build-staging-plan.md`
- `architecture/academic-evidence-policy.md`
- `architecture/academic-storage-and-rag.md`
- `architecture/security-trust-boundaries.md`
- `architecture/research-evaluation-and-benchmarks.md`
- `docs/academic-source-taxonomy.md`
- `docs/master-academic-source-inventory-and-gaps.md`

Architecture decision history:

- `architecture/adr/001-framework-scoped-text-analysis.md`

Superseded design history:

- `architecture/database-api-cross-stage-contract-v1.md`
- `architecture/source-taxonomy-storage-rag.md`

## v1.1 load-bearing distinction

The current architecture distinguishes:

```text
Reference location
  != textual expression
  != linguistic segmentation
  != syntactic analysis
  != translation witness
  != scholarly interpretation
  != AI synthesis
```

In practical terms:

- reference anchors may be application-owned;
- textual expressions are edition/expression-specific;
- tokenisation, phrase/clause structure and dependency are framework-scoped;
- cross-corpus mappings are explicit research data;
- provider codes such as an FHL Bible version code are not assumed to equal a precise print edition;
- source text and AI-extracted scholarly propositions are distinct;
- final AI assertions should link to supporting, opposing and qualifying evidence.

## Academic source library

Google Drive remains the source/acquisition library, not the production RAG database.

The newly consolidated Drive folder is currently strongest in:
- Biblical Hebrew grammar;
- lexica;
- theological lexica.

It is not yet a complete master research library. See:
- `docs/master-academic-source-inventory-and-gaps.md`

Major remaining / separate evidence lanes include:
- BHS/BHQ and textual criticism;
- DSS/Judean Desert;
- historical/diachronic Hebrew;
- commentaries;
- exegesis and rhetoric methodology;
- Chinese Bible translation studies/documentation;
- current journal articles, chapters and dissertations.

## Future build stages

The project remains divided into five stages:

1. Research shell + reference/text-expression foundation
2. Passage Study + Chinese translation witnesses + alignment
3. Hebrew corpus + framework-aware query engine
4. Academic knowledge base + textual criticism + RAG + security/evaluation
5. Research orchestrator + rule engine + assertion-level synthesis

No Vercel deployment should be performed until explicitly requested.

## Development rule

A later build stage must extend the existing project. It must not silently replace canonical vocabularies, ontology, rights semantics, corpus-query semantics or earlier working functionality.
