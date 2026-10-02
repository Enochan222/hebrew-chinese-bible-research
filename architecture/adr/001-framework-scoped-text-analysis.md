# ADR-001: Revoke Premature v1 Freeze and Adopt Framework-Scoped Text Analysis

Status: **ACCEPTED**
Date: 2026-10-03

## Context

The first architecture contract treated application-owned tokens, phrases and clauses as canonical objects to which OSHB, MACULA and BHSA could be mapped.

A subsequent adversarial review identified a load-bearing problem: reference location, textual expression and linguistic analysis were being treated as if they had the same kind of identity.

They do not.

- A biblical reference locus can reasonably have an application-owned anchor.
- A text is edition / expression specific.
- Tokenisation and morpheme segmentation may differ by dataset.
- Phrase, clause, dependency and semantic-role structures are analytical framework claims.
- Cross-framework correspondence is itself research data.

The review also identified related problems in translation-edition identity, rights modelling, textual criticism, RAG security, alignment, assertion-level provenance and evaluation.

## Decision

1. The original database-api-cross-stage-contract-v1.md is superseded and retained only as design history.
2. The active candidate contract is database-api-cross-stage-contract-v1.1-candidate.md.
3. The architecture now distinguishes:

Reference Atom / Span
    -> Textual Work
       -> Textual Edition
          -> Digital Expression
             -> Text Stream
                -> Text Segment

Corpus Release
    -> Annotation Framework
       -> Analysis Node / Edge

Cross-provider / cross-framework mappings
    -> explicit mappings with provenance and review

4. No universal application-owned phrase or clause identity is assumed.
5. Provider distribution identity is distinct from translation work / edition / digital expression identity.
6. Canonical implementation vocabularies come from contracts/v1.1/vocabulary.json.
7. Rights are operation- and purpose-aware, including model-context permission.
8. Textual criticism preserves raw apparatus separately from parsed interpretation.
9. AI-generated scholarly proposition extraction is not identical to source-author wording.
10. Final synthesis will support assertion-level evidence links.
11. Security trust boundaries and research benchmarks are architecture requirements, not launch-afterthoughts.

## Consequences

### Positive

- Prevents false cross-corpus linguistic identity.
- Makes corpus query semantics academically explicit.
- Avoids FHL digital text being mislabelled as a precise print edition.
- Supports LXX as a real textual-version research domain.
- Improves legal/rights control.
- Improves citation and synthesis auditability.
- Reduces architecture drift through machine-readable vocabulary.

### Cost

- More entities and mappings.
- Stage 1 identity model is more abstract.
- Cross-framework comparison requires explicit mapping.
- Some future data must remain unresolved rather than forced into one ontology.

These costs are accepted because silent false equivalence would be a higher research risk.

## Deferred, not rejected

The architecture does **not** require the following to be fully implemented before Stage 1:

- exhaustive TEI critical-apparatus parity;
- complete LXX morphology/syntax;
- complete scholarly citation graph;
- complete cross-framework manual adjudication;
- 100+ question benchmark.

The model must support them cleanly, but staged implementation remains the project strategy.

## Freeze rule

v1.1 may be declared frozen only after the preconditions listed in database-api-cross-stage-contract-v1.1-candidate.md have been tested.
