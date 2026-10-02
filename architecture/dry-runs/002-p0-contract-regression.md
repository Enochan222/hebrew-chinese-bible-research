# Dry Run 002: P0 Contract Closure Regression

Status: **PASSED AT ARCHITECTURE + MACHINE-CONTRACT LEVEL; DATABASE IMPLEMENTATION NOT YET CLAIMED**

Date: 2026-10-03

Baseline: `architecture/dry-runs/001-1sam16-7-mcp-api-db.md`

Active contract: `architecture/database-api-cross-stage-contract-v1.1.md`

Machine-readable contracts: `contracts/v1.1/`

## 1. Objective

Re-run the Dry Run 001 failure list after closing the identified P0 contract gaps.

Seed use case remains:

~~~text
1 Samuel 16:7
ראה + prefixed ל + BODY_PART
~~~

This is a contract/reproducibility fixture. It is not a claim that the final scholarly interpretation or translation of 1 Samuel 16:7 has been decided.

## 2. P0 closure matrix

| Dry Run 001 gap | Dry Run 002 result | Contract change |
|---|---|---|
| v1.1 not self-contained | PASS at architecture-contract level | self-contained active v1.1 with foundational provider/source/provenance/project/source-asset definitions |
| CorpusQuery not machine-readable | PASS | JSON Schema + normative query semantics |
| Annotation model flattened to one framework | PASS at contract level | first-class annotation_layers |
| Rights resolver not deterministic | PASS at contract level | resolution algorithm + RightsDecisionSnapshot |
| Persistent TextSegment conflicts with provider rights | PASS at contract level | PERSISTED_CONTENT / PROVIDER_LOCATOR / EPHEMERAL |
| ResearchRelease immutable/lifecycle conflict | PASS at contract level | immutable release + append-only events |
| Active release pointer absent | PASS | PREVIEW / STAGING / PRODUCTION pointer |
| Release components used unchecked UUID | PASS at contract level | FK to registered research_objects |
| Published analysis collapsed to prose JSON | PASS | published assertions + public evidence items |
| Authoring/public evidence ambiguity | PASS | authoring and published evidence packets separated |
| TranslationDecision JSONB too loose | PASS at wire-contract level | versioned TranslationDecision schema |
| Construction dependencies incomplete | PASS | ConstructionCompilationRun + derived dependency manifest |
| Rule effect/conflict semantics incomplete | PASS | explicit RuleApplication effects + rule_conflicts |
| Current API not citation-stable | PASS at API-contract level | current and pinned ResearchRelease routes |
| MCP boundary ambiguous | PASS | Product MCP is read-only domain-service facade |

## 3. CorpusQuery regression

Files:

- `contracts/v1.1/json-schema/corpus-query.schema.json`
- `contracts/v1.1/query-semantics.md`
- `contracts/v1.1/fixtures/corpus-query-1sam16-7.json`

The fixture pins a digital expression, corpus release, normalization profile, MORPHEME_SEGMENTATION layer, MORPHOLOGY layer, CLAUSE_STRUCTURE layer, BODY_PART semantic-set version, PREFIX_MORPHEME_OF, and SAME_CLAUSE.

Important correction: `LEMMA_TEXT` and `LEXEME_ID` are distinct query fields.

Binding semantics are now fixed for ALL_OF, ANY_OF, NOT, EXISTS, NOT_EXISTS, and COUNT. COUNT operates on distinct binding tuples rather than SQL rows.

Result: **PASS**

## 4. Annotation-layer and semantic-set regression

Fixtures now exist for morpheme segmentation, morphology, clause structure, and BODY_PART.

Semantic regression confirmed:

- every query layer ID resolves;
- all layers belong to the pinned corpus release;
- PREFIX_MORPHEME_OF uses MORPHEME_SEGMENTATION;
- SAME_CLAUSE uses CLAUSE_STRUCTURE;
- morphology is independently pinned;
- BODY_PART is version-pinned and contains fixture member עין.

Result: **PASS**

## 5. Construction and RuleApplication regression

Chain:

~~~text
CorpusQuery
 -> ConstructionCompilationRun
 -> ConstructionInstance
 -> RuleApplication
 -> editorial TranslationDecision
~~~

The compilation dependency manifest includes all query annotation layers, semantic-set version, normalization profile, and relation types.

The RuleApplication fixture uses effect QUALIFIES and exceptionStatus UNRESOLVED. It does not directly assert a final translation.

Result: **PASS**

## 6. Rights and provider-storage regression

Two provider cases are intentionally distinct.

Case A:

~~~text
STORE_EXTRACTED_TEXT = ALLOW
bindingMode = SNAPSHOT_PINNED
segmentStorageMode = PERSISTED_CONTENT
~~~

Case B:

~~~text
STORE_EXTRACTED_TEXT = DENY
bindingMode = LIVE_EXTERNAL
segmentStorageMode = PROVIDER_LOCATOR
~~~

Result: **PASS**

The architecture no longer treats display permission as equivalent to persistent-storage permission.

## 7. ResearchRelease regression

Machine contracts now distinguish:

~~~text
ResearchBuild
  !=
ResearchRelease payload
  !=
ResearchReleaseEvent
  !=
ReleaseChannelPointer
~~~

ResearchBuild lifecycle no longer contains PUBLISHED. Release payload is immutable. Rollback changes the channel pointer.

Result: **PASS AT CONTRACT LEVEL**

## 8. Published evidence regression

PublishedPassageAnalysis now resolves assertion-level public evidence. Authoring evidence packets are not public API objects.

Semantic regression confirmed that the analysis, evidence item, and manifest share the same ResearchRelease.

Result: **PASS**

## 9. Public API and MCP regression

OpenAPI now defines current-release analysis, pinned-release analysis, CorpusQuery validate/run, and public evidence.

Product MCP is read-only, reuses the same CorpusQuery schema, exposes no arbitrary SQL, no publication tool, and no authoring-database access.

Result: **PASS AT CONTRACT LEVEL**

## 10. Structural validation suite

Fixture suite result:

~~~text
18 schema/fixture validations
18 passed
0 failed
~~~

Coverage includes CorpusQuery, release manifest, rights ALLOW/DENY, published analysis, translation decision, three annotation layers, snapshot/live provider witnesses, release event/channel pointer, semantic set, construction compilation/instance, rule application, and published evidence.

## 11. Cross-fixture semantic regression

Checked:

1. query node references;
2. annotation-layer declarations and kinds;
3. semantic-set version pinning;
4. construction dependency-manifest parity;
5. ConstructionInstance -> CompilationRun linkage;
6. RuleApplication -> ConstructionInstance linkage;
7. published assertion/evidence/release linkage;
8. rights DENY -> LIVE_EXTERNAL flow;
9. rights ALLOW -> SNAPSHOT_PINNED flow;
10. TranslationDecision selected-rendering integrity.

Result: **PASS**

## 12. What this test does not prove

This regression does not yet prove:

- PostgreSQL migrations execute successfully;
- all FKs, RLS, and grants are correct in Supabase;
- the actual FHL rights situation for a specific Chinese version;
- actual provider response stability;
- actual OSHB/MACULA/BHSA layer mappings;
- real corpus-query completeness;
- real 1 Samuel 16:7 match membership;
- real RFC 8785/SHA-256 implementation parity;
- OpenAPI-generated server/client compatibility;
- Product MCP runtime conformance;
- query latency under production load;
- publication-worker transaction/rollback behaviour.

Synthetic fixtures prove contract coherence, not scholarly truth or production correctness.

## 13. New gate status

The P0 contract-design failures from Dry Run 001 are now substantially closed.

v1.1 should remain CANDIDATE until the next gate:

> **Database Spike 001**

That spike should instantiate the critical contract in PostgreSQL/Supabase and execute the same fixture chain through real FKs, constraints, transactions, RLS/grants, query validation, and release publication/rollback.

Do not build the full product UI before this database spike passes.
