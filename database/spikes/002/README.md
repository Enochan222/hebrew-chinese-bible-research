# Whole-Bible Corpus Foundation integration harness

Status: **REAL PINNED OSHB FULL-CORPUS IMPORT EVIDENCE**

This harness is the first product-scale bridge from the pinned Hebrew corpus source into the canonical PostgreSQL Authoring model.

Database Spike 001 proves relational/RLS/publication invariants with controlled adversarial fixtures. This harness separately proves that the canonical reference/text/annotation model can ingest the complete pinned OSHB baseline corpus through one deterministic path.

It does not yet publish the full corpus into Serving or connect a remote Supabase project.

## Flow

```text
fetch pinned OSHB
  -> build whole-Bible coverage index
  -> generate deterministic COPY loadset
  -> blank PostgreSQL 17 + migration 001
  -> import complete OSHB baseline
  -> relational checks
  -> reconcile database counts to source/import manifests
```

## Imported layer

- OSHB provider book divisions;
- OSHB_OSIS ReferenceSystem labels;
- verse ReferenceAtoms/ReferenceSpans;
- WLC/OSHB textual work/edition/digital expression;
- BASE TextStream;
- word TextSegments preserving source Unicode;
- OSHB provider-scoped morphology AnalysisNodes;
- provider word ID, reference label, word order, raw lemma and raw morphology features.

This is baseline text/morphology only. BHSA phrase/clause/syntax remains a separate framework-scoped layer.

## Acceptance

The harness fails if the provider book-file set is incomplete/unexpected, any verse imports no words, a provider word ID/reference duplicates, segment/node/membership counts diverge, database counts do not reconcile to the generated manifests, or the 1 Samuel 16:7 canary stops yielding 25 OSHB words.

No remote database is modified.
