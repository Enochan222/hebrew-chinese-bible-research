# WB-1 Whole-Bible PostgreSQL Import Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox syntax for tracking.

**Goal:** Generalize the accepted WB-0 relational importer across the complete WB-CORPUS-001 source foundation without creating a second ontology or silently dropping unresolved provider data.

**Architecture:** Preserve WB-0 UUID/provider identity semantics, but replace giant INSERT statements with deterministic TSV loadsets consumed by PostgreSQL COPY. Verse ReferenceSpans come from the independently derived OSHB_OSIS inventory; BHSA phrase/clause nodes that cross verse boundaries use range ReferenceSpans in the same schema. Crosswalk unresolved records remain explicit exceptions: raw provider nodes still load, while only candidate mapping groups are omitted for unresolved references.

**Tech Stack:** Python 3.12, NDJSON/JSON, PostgreSQL 17 psql COPY, unittest, GitHub Actions.

**Spec:** architecture/whole-bible-base-product.md; architecture/corpus-source-integration.md; contracts/v1.1/freeze-checklist.md

## Global Constraints

- Preserve ReferenceSpan/TextSegment/AnalysisNode/AnnotationLayer ontology.
- Preserve OSHB and BHSA as separate provider/framework layers.
- Automatic OSHB/BHSA mappings remain non-canonical CANDIDATE_AUTOMATED.
- Provider book-division counts are provenance only, never the whole-Bible gate.
- WB-CORPUS-001 gatePass and zero silent reference loss are prerequisites.
- Unresolved mapping references may not delete source/provider records.
- No Serving projection or ResearchRelease is written by WB-1.
- CanonSystem persistence is not invented until the schema implements canon_systems/canon_books.

## Review Focus

- Repeated per-verse word order must not violate stream-global text_segments uniqueness.
- BHSA phrase/clause nodes spanning more than one verse must resolve to range ReferenceSpans.
- Annotation-only BHSA nodes must load without fabricated text segments.
- Unresolved crosswalk references must preserve both providers while creating no false canonical mappings.
- WB-0 UUID identities must remain stable for the accepted 1 Samuel 16:7 canary.

### Task 1: Identity compatibility and loadset contract

- [ ] Write failing tests for stable UUID compatibility and a two-verse synthetic WB-1 loadset.
- [ ] Verify RED on the branch before production files exist.
- [ ] Add corpus_identity.py and load_wb1_postgres.py with deterministic TSV/COPY output.
- [ ] Verify unit tests GREEN.

### Task 2: Real PostgreSQL whole-corpus execution

- [ ] Add a dedicated WB-1 workflow that builds WB-CORPUS-001, initializes PostgreSQL, imports the full loadset, and runs relational count/exception assertions.
- [ ] Keep the existing WB-0 real-corpus job as an independent regression.
- [ ] Verify exact-head Actions on real pinned sources.

### Task 3: Authority/state synchronization

- [ ] Update README, corpus docs, architecture, PROJECT_STATE and CHANGELOG with measured WB-1 evidence only after execution.
- [ ] Keep CORE-FZ-WB-002 bounded to the evidence actually produced.
- [ ] Run governance/contracts/database/whole-corpus gates and review the final diff.
