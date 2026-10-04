# Whole-Bible Base Product Foundation

Status: **ACTIVE PRODUCT/IMPLEMENTATION AUTHORITY**
Date: 2026-10-04

## 1. Purpose

The base product is a whole-Hebrew-Bible research reader. Research Pro is an enrichment layer over that base, not the definition of the base.

The minimum useful product path is:

```text
pinned Hebrew source
  -> deterministic whole-corpus import
  -> canonical reference/text/annotation identities
  -> immutable ResearchRelease components
  -> release-pinned passage serving
  -> whole-Bible reader
  -> translation witnesses / comparison
  -> project translation
  -> Research Pro scholarly overlay
```

A passage-specific fixture is successful only when it exposes a reusable invariant and the same importer can then run over the complete pinned corpus.

## 2. Base product versus overlays

### Base product

The base must ultimately provide, across the whole Hebrew Bible:

- book/chapter/verse navigation through explicit ReferenceSystem identity;
- pinned Hebrew source text;
- provider-scoped word identity;
- baseline lemma/morphology;
- stable passage deep links;
- release-pinned serving;
- translation-witness slots with independent loading/rights states;
- a project-translation slot that is empty unless a reviewed TranslationDecision is published;
- visible provenance/release identity.

### Deterministic analysis overlay

Adds:

- BHSA/Clear or other framework-scoped phrase/clause/syntax;
- cross-framework mappings;
- Hebrew/Chinese alignment;
- semantic sets;
- constructions;
- CorpusQuery and match explanations.

### Research Pro overlay

Adds:

- ResearchIssue / ResearchPosition;
- LiteratureSnapshot / literature review;
- commentary and advanced textual criticism;
- full bibliography and evidence graph;
- live non-canonical discovery.

A passage may be BASE_READY while its Research Pro state is NOT_COMPILED. The UI must report that distinction instead of inventing scholarship.

## 3. Coverage states

Coverage is tracked independently by layer, not as one misleading percentage.

Operational coverage labels may include:

- `SOURCE_READY`;
- `BASE_IMPORTED`;
- `SERVING_READY`;
- `TRANSLATION_WITNESSES_PARTIAL` / `TRANSLATION_WITNESSES_READY`;
- `DETERMINISTIC_ANALYSIS_PARTIAL` / `DETERMINISTIC_ANALYSIS_READY`;
- `RESEARCH_PRO_NOT_COMPILED` / `RESEARCH_PRO_REVIEWED`.

These are operational coverage labels, not new scholarly ontology or ResearchRelease lifecycle states.

## 4. Initial whole-corpus baseline

OSHB/morphhb is the initial whole-corpus baseline because the active corpus source registry already assigns it the text/word/lemma/morpheme/morphology role and its public-serving terms are attribution-compatible.

The full-corpus importer must:

1. use the exact reviewed OSHB commit pin;
2. fail if the expected provider book-file set is incomplete or unexpected;
3. preserve source codepoint order without NFC normalization;
4. generate stable project UUIDs deterministically from provider/source identities;
5. represent each imported provider verse through ReferenceSystem/ReferenceAtom/ReferenceSpan/ReferenceLabel;
6. store source words as TextSegments;
7. store morphology as provider-scoped AnalysisNodes/features linked to those segments;
8. emit an import manifest containing source pin/hash and exact row counts;
9. reconcile database counts to that manifest in CI.

This baseline is not a universal linguistic ontology. BHSA and other frameworks remain independent annotation layers.

## 5. Acceptance vectors

Passage fixtures remain deliberately small and adversarial:

- 1 Samuel 16:7: OSHB/BHSA segmentation mismatch and annotation-only BHSA nodes;
- Psalm 3:1 and other superscription/versification cases: ReferenceSystem/ReferenceAtom stress tests;
- future Ketiv/Qere cases: WRITTEN/READ stream tests.

Passing one vector is necessary but never sufficient evidence for whole-Bible coverage.

## 6. Build order

Current build order:

1. whole-Bible OSHB source coverage/index;
2. whole-Bible OSHB relational Authoring import;
3. release-scoped Serving passage projection and navigation API;
4. whole-Bible reader UI;
5. translation-witness adapters and comparison;
6. BHSA/framework-scoped deterministic analysis;
7. project TranslationDecision/rendering workflow;
8. Research Pro scholarly enrichment.

Research Pro contracts remain active while implementation proceeds in this order.

## 7. What remains prohibited

- hand-maintaining one row/page per verse;
- treating fixture coverage as product coverage;
- using an LLM to generate missing Hebrew/corpus rows;
- flattening OSHB/BHSA identities;
- making academic enrichment availability determine canonical passage existence;
- publishing an ad-hoc AI Chinese translation as the project rendering;
- bypassing ResearchRelease/rights/provenance boundaries for convenience.
