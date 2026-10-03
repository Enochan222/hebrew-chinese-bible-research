# Hebrew-Chinese Bible Research

Research-grade Hebrew Bible and Chinese translation **data product and research platform**.

## Current project status

**Core contract closure complete for Database Spike 001; full v1.1 product freeze still pending.**

Do not implement the superseded v1 database contract.

The active architecture is the amended **v1.1 candidate**, which is not yet frozen.

## Canonical project intent

Read first:

- `PROJECT_CHARTER.md`
- `PROJECT_STATE.md`
- `CHANGELOG.md`

This is the canonical product-intent and requirements document. Architecture and machine contracts implement it; they do not redefine the product goal.

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
Study / Research experience modes
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

## Architecture and contract authority

Read in this order:

- `PROJECT_CHARTER.md`
- `architecture/manifest.json`
- `architecture/product-platform-and-publication-model.md`
- `architecture/database-api-cross-stage-contract-v1.1.md`
- `contracts/v1.1/README.md`
- `contracts/v1.1/freeze-checklist.md`

Other active specialised architecture:

- `architecture/integration-boundaries-mcp-api-database.md`
- `architecture/academic-evidence-policy.md`
- `architecture/academic-storage-and-rag.md`
- `architecture/research-pro-scholarly-intelligence.md`
- `architecture/scholarly-discovery-aggregation.md`
- `architecture/pastoral-studio-runtime-scholarly-rag.md`
- `architecture/sacred-studies-research-method.md`
- `architecture/ui-mode-cross-stage-contract.md`
- `architecture/security-trust-boundaries.md`
- `architecture/byok-credential-handling.md`
- `architecture/research-evaluation-and-benchmarks.md`
- `architecture/site-build-staging-plan.md`

Architecture decisions:

- `architecture/adr/001-framework-scoped-text-analysis.md`
- `architecture/adr/002-compiled-research-product.md`
- `architecture/adr/003-mcp-agent-boundary.md`
- `architecture/adr/004-research-pro-experience-layer.md`
- `architecture/adr/005-public-ai-byok-only.md`
- `architecture/adr/006-multi-provider-scholarly-discovery-compiler.md`

Current validation records:

- `architecture/dry-runs/002-p0-contract-regression.md`
- `architecture/reviews/2026-10-03-adversarial-critique-remediation.md`

Historical / superseded design records are listed in `architecture/manifest.json` and are not implementation authority.

## Study and Research experiences

The public product has two coordinated experience modes over the same active ResearchRelease:

### Study

Lower-density passage/translation research:

- text and translations;
- concise morphology/syntax;
- published translation note;
- reviewed commentary;
- key scholarship;
- key citations and major alternatives.

Study is not academically opaque. It preserves minimum evidence transparency.

### Research

Professional research workspace:

- full Corpus Lab;
- construction browser;
- ResearchIssue / ResearchPosition graph;
- full bibliography;
- literature snapshots/reviews;
- scholarly dependency graph;
- advanced textual criticism;
- live recent literature discovery;
- research export/citation workflows.

Research Pro is controlled by ProductEntitlement.

ProductEntitlement is separate from RightsPolicy and cannot override source/content restrictions.

Live discovery is labelled as non-canonical until incorporated into a later ResearchRelease.

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
4. Private academic knowledge compiler + Scholarly Intelligence + publication pipeline
5. Rules + published commentary/literature review + Research serving + optional NL-to-DSL + product operations

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


## Public AI / BYOK policy

All public runtime AI is **BYOK-only**.

Gemini is the first supported provider.

The repository and deployed public app must contain no shared model-provider credential in source code, environment variables, Vercel secrets, Supabase secrets, GitHub Actions secrets, database rows, fixtures, or fallback configuration.

User-supplied provider credentials are session-only volatile secrets and are not stored in the database, cookies, localStorage, IndexedDB, logs, analytics, telemetry, evidence packets, or audit records.

Without BYOK, the deterministic scholarly product remains functional. Only optional AI-assisted features are unavailable.

See:

- `architecture/byok-credential-handling.md`
- `architecture/adr/005-public-ai-byok-only.md`


## Mandatory repository governance

`main` is protected by the active `Protect main` repository ruleset.

Normal changes require:

- a pull request;
- synchronization with latest `main` when required;
- `contracts` PASS;
- `state-and-changelog` PASS;
- resolved review conversations;
- squash merge.

No second-person approval is required by default, so collaborators can independently complete compliant PRs.

Force pushes and deletion of `main` are blocked, linear history is required, and there are no bypass actors.

Every push/PR must update both `PROJECT_STATE.md` and `CHANGELOG.md`.

See:

- `AGENTS.md`
- `.github/workflows/project-governance.yml`
- `architecture/repository-governance.md`
- `architecture/reviews/2026-10-03-live-repository-governance-verification.md`
