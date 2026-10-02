# ADR-004: Research Pro Is an Experience Layer, Not a Second Product

Status: **ACCEPTED**
Date: 2026-10-03

## Context

The product now supports a deeper professional scholarly experience including:

- advanced corpus research;
- ResearchIssue / ResearchPosition graphs;
- full bibliography;
- literature review;
- scholarly dependency graph;
- live literature discovery;
- advanced textual criticism;
- research export.

A naive implementation could split this into a second application, separate database or separate scholarly truth state.

That would create duplicated ontology, release drift, inconsistent citations and unclear rights handling.

## Decision

1. The user-facing experience modes are:
   - STUDY
   - RESEARCH

2. Both modes read the same canonical entities and the same active ResearchRelease.

3. Research mode exposes greater depth and additional workflow/tooling. It is not more authoritative than Study mode.

4. Research Pro is controlled through ProductEntitlement / feature capabilities, not by duplicating the data model.

5. ProductEntitlement is strictly separate from RightsPolicy.

6. A ProductEntitlement ALLOW can never override a RightsPolicy DENY.

7. Study mode retains minimum evidence transparency for substantive published claims:
   - key citations;
   - ResearchRelease identity;
   - material uncertainty/major alternatives;
   - bibliographic access links where permitted.

8. Live external discovery is normally a Research-mode feature and is explicitly non-canonical until incorporated into a later ResearchRelease.

9. Commentary has one published identity across both modes. Research mode expands its structured evidence and issue graph; it does not generate a different official commentary.

10. Mode switching preserves passage, release and relevant workspace state.

## Consequences

### Positive

- one scholarly truth state;
- one release history;
- less duplicated frontend/business logic;
- clean subscription/entitlement separation;
- consistent citation behaviour;
- safer rights enforcement;
- progressive disclosure for non-specialist users.

### Costs

- view-model composition must support different density levels;
- entitlement checks must be server-side and feature-based;
- Study UI needs careful minimum-transparency design;
- Research modules require lazy-loading/performance planning.

## Non-goal

This ADR does not decide pricing, subscription names, billing provider or which features are monetized.

Those are commercial/product decisions layered on top of ProductEntitlement.
