# Dry Run 001: 1 Samuel 16:7 across Source, Compiler, Database, API, and MCP

Status: **CONTRACT DRY RUN — NOT SCHOLARLY CONCLUSION**

Date: 2026-10-03

Purpose:

Run one representative use case through the proposed architecture before freezing v1.1.

Seed case:

~~~text
1 Samuel 16:7
ראה + prefixed ל + BODY_PART
~~~

This dry run tests data/interface boundaries.

It does **not** claim that the final grammatical or translation analysis of 1 Samuel 16:7 has been settled, and it does not claim that the construction query below already returns an exhaustive reviewed result set.

## 1. Target research workflow

The product should eventually support a user/researcher asking:

> Find occurrences where ראה participates in a clause containing a body-part noun with prefixed ל, show why each result matched, compare Chinese translation witnesses, and display the published scholarly analysis for 1 Samuel 16:7.

The architecture must answer this without giving an LLM authority to determine corpus membership.

## 2. Source acquisition

### Hebrew corpus data

Target source classes:

- a version-pinned Hebrew digital expression;
- morphology layer;
- clause/syntax layer;
- semantic-set release.

Interface:

~~~text
official dataset/repository/API
 -> corpus importer
 -> Authoring DB
~~~

Decision:

**Do not use MCP as the normal importer transport.**

Use a deterministic dataset/API adapter.

Reason:

Corpus ingestion is data engineering, not an agent interaction.

### FHL Chinese witness

Target:

- provider distribution;
- provider version code;
- returned passage text or provider locator;
- rights metadata.

Preferred production interface:

~~~text
FHL API
 -> FHLProviderAdapter
 -> typed provider response
~~~

Optional research interface:

~~~text
AI host -> FHL MCP -> FHL API
~~~

The MCP route is useful to an agent, but it must not be the canonical internal provider dependency.

### Academic books

Target:

- grammar/commentary/lexicon passages from the private source library.

Interface:

~~~text
Google Drive / registered source
 -> private ingestion/research service
 -> Authoring DB
~~~

An external academic-paper MCP may enter at this same private source-adapter boundary.

## 3. Canonical identity check

Required reference identity:

~~~text
ReferenceSpan = 1 Sam 16:7
~~~

Required Hebrew identity:

~~~text
TextualWork
 -> TextualEdition
 -> DigitalExpression
 -> TextStream
 -> TextSegment
~~~

Required linguistic identity:

~~~text
Corpus/Dataset Release
 -> Annotation Layer(s)
 -> Analysis Nodes / Edges / Features
~~~

### Dry-run result

**PARTIAL FAIL**

The current v1.1 correctly separates text expression from linguistic analysis, but it still models corpus releases with one annotation framework.

The dry run needs morphology, morpheme segmentation and clause structure to be independently pinned.

Therefore an annotation_layers or equivalent layer-level provenance model is required before this case is fully reproducible.

## 4. Semantic-set input

Required compiled object:

~~~text
BODY_PART <version>
~~~

The membership of עין must be explicit and versioned.

The query does not ask an LLM at runtime whether עין is a body part.

### Dry-run result

**PASS CONCEPTUALLY**

The current semantic-set/version model is suitable.

Machine-readable schema is still missing.

## 5. Provisional CorpusQuery

Illustrative only:

~~~json
{
  "queryVersion": "1.1-dry-run",
  "textContext": {
    "digitalExpressionId": "FIXTURE_HEBREW_EXPRESSION"
  },
  "analysisContext": {
    "morphologyLayerId": "FIXTURE_MORPHOLOGY_LAYER",
    "clauseLayerId": "FIXTURE_CLAUSE_LAYER"
  },
  "nodes": [
    {
      "id": "V",
      "type": "WORD",
      "constraints": {"lemma": "ראה"}
    },
    {
      "id": "P",
      "type": "MORPHEME",
      "constraints": {"lemma": "ל"}
    },
    {
      "id": "N",
      "type": "WORD",
      "constraints": {"semanticSetVersion": "BODY_PART:FIXTURE"}
    }
  ],
  "relations": [
    {"type": "PREFIX_MORPHEME_OF", "from": "P", "to": "N"},
    {"type": "SAME_CLAUSE", "from": "V", "to": "N"}
  ]
}
~~~

### Expected execution path

~~~text
CorpusQuery JSON
 -> JSON Schema / Zod validation
 -> dependency extraction
 -> complexity guard
 -> deterministic query planner
 -> compiled serving projections
 -> result bindings
~~~

### Dry-run result

**FAIL AS ENFORCEABLE CONTRACT**

The repository still lacks the machine-readable CorpusQuery schema.

The Markdown vocabulary is not enough to guarantee that web Pattern Builder, public HTTP API, Product MCP and optional natural-language compiler all mean the same thing.

## 6. ConstructionDefinition

Named construction:

~~~text
PERCEPTION_VERB_LAMED_BODY_PART
~~~

The authoritative data should be:

- versioned query AST;
- compiler-generated dependency manifest;
- compilation run;
- result-set hash.

Required compilation record:

~~~text
ConstructionCompilationRun
  construction_definition_version
  corpus/dataset release
  annotation layer versions
  semantic-set versions
  normalization profile
  query AST hash
  compiler version
  result count
  result-set hash
~~~

### Dry-run result

**PARTIAL FAIL**

ConstructionDefinition/Instance exist conceptually.

The current contract does not yet fully model the compilation run and all derived dependencies.

## 7. Construction match

If 1 Samuel 16:7 satisfies the pinned query, the compiler creates a ConstructionInstance.

That instance states only that this pinned corpus/annotation/query combination matched this passage.

It does not yet state how ל should be translated.

### Dry-run result

**PASS CONCEPTUALLY**

This separation is one of the strongest current architecture decisions.

## 8. Scholarly rule

Example type:

~~~text
LINGUISTIC_HEURISTIC
~~~

The rule may consider the construction together with other reviewed conditions and evidence.

It may support, disfavour, qualify, or leave an interpretation unresolved.

A RuleApplication must not automatically become a TranslationDecision.

### Dry-run result

**PARTIAL PASS**

The Rule/RuleApplication distinction is sound.

Conflict/effect semantics still need a machine contract before automatic compilation is safe.

## 9. Academic evidence

Private research may retrieve relevant grammar sections, corpus observations, lexicon material, commentary and counterevidence.

Authoring evidence packet may include restricted material.

It must not be copied directly into public serving.

Publication must compile:

~~~text
PublishedEvidencePacket
 -> PublishedEvidenceItem
 -> PublishedAnalysisAssertion
~~~

with permitted citations/excerpts only.

### Dry-run result

**FAIL IN CURRENT ACTIVE CONTRACT**

A published analysis should not collapse back into one opaque analysis payload plus a private evidence packet ID.

Assertion-level public provenance is required.

## 10. Chinese translation witness

### Rights-permitted snapshot case

~~~text
FHL/provider response
 -> rights resolver = snapshot storage allowed
 -> snapshot text/segments
 -> content hash
 -> ResearchRelease binding = SNAPSHOT_PINNED
~~~

### Non-persistable case

~~~text
FHL/provider response
 -> rights resolver = persistent storage denied
 -> ProviderLocator
 -> observed metadata/hash where allowed
 -> ResearchRelease binding = LIVE_EXTERNAL
~~~

### Dry-run result

**FAIL UNTIL RIGHTS/STORAGE CONTRACT IS CLOSED**

The current TextSegment surface-content assumption conflicts with providers for which display may be allowed but persistent extracted-text storage may not be.

A segment storage mode / provider-locator strategy is required.

## 11. ResearchBuild

The private compiler assembles corpus dependency snapshot, construction compilation, semantic-set versions, rule applications, translation decision, scholarly evidence, public-safe evidence projection and serving projections.

Recommended build lifecycle:

- QUEUED
- RUNNING
- FAILED
- READY_FOR_REVIEW
- APPROVED
- REJECTED
- COMPLETED

Do not use PUBLISHED as a ResearchBuild state.

## 12. Publication validation

Input: approved ResearchBuild.

Publication worker checks:

- rights decision snapshots;
- public/private leakage;
- citations;
- assertion/evidence integrity;
- schema versions;
- benchmark gates;
- serving projection parity;
- component hashes.

The worker reads Authoring DB with a restricted read role and writes Serving DB with a dedicated publication role.

No public API or MCP tool may call this database role.

## 13. ResearchRelease

Payload:

- immutable component manifest;
- immutable component hashes;
- immutable published research payload.

Lifecycle:

use append-only release events or equivalent lifecycle metadata:

- PUBLISHED
- SUPERSEDED
- REVOKED
- optionally REACTIVATED

The immutable release payload itself is not updated to REVOKED.

Add release_channels and release_channel_pointers, for example PRODUCTION -> Release A and STAGING -> Release B.

Rollback changes the pointer, not the release payload.

### Dry-run result

**FAIL UNTIL RELEASE LIFECYCLE IS SPLIT**

Immutable payload and mutable lifecycle state must not be the same field semantics.

## 14. Serving DB publication

Public Serving receives only publishable objects:

- release;
- passage/text data where rights allow;
- semantic sets;
- construction definitions/instances;
- rule applications;
- structured published assertions;
- published evidence items;
- compiled search projections.

It does not receive raw private source text, Drive file locators, private embeddings, rejected AI candidates, or authoring evidence packets.

## 15. Public HTTP request

Current release route:

~~~text
GET /api/v1/passages/1Sam.16.7/analysis
~~~

must resolve the active production release and return that release ID.

Pinned scholarly route:

~~~text
GET /api/v1/releases/{releaseId}/passages/1Sam.16.7/analysis
~~~

must remain stable for that release.

### Dry-run result

**PASS AS DESIGN, MISSING MACHINE CONTRACT**

Pinned release API is required before the product can honestly claim citation-stable computational commentary.

## 16. Ad-hoc corpus query

User submits the same formal query to POST /api/v1/corpus/query/run.

Request includes or resolves research release, corpus/dataset release, annotation layers, semantic-set versions and normalized AST.

The query service executes deterministic search.

No LLM determines result membership.

## 17. Product MCP call

External AI host asks to find occurrences matching ראה + prefixed ל + BODY_PART.

MCP tool: run_corpus_query.

Input: the same CorpusQuery schema used by the public HTTP API.

Execution:

~~~text
MCP host
 -> Product MCP
 -> CorpusQuery Domain Service
 -> validation / complexity guard
 -> Serving DB
 -> structured result
~~~

Forbidden:

~~~text
MCP host
 -> Product MCP
 -> arbitrary SQL
 -> PostgreSQL
~~~

### Dry-run result

**PASS IF MCP IS ONLY A FACADE**

This is the recommended MCP position.

## 18. Optional natural-language query

~~~text
User Chinese
 -> LLM query interpreter
 -> candidate CorpusQuery AST
 -> same validator
 -> same deterministic query service
~~~

The LLM has no database credentials and never executes SQL.

## 19. User workspace

User writes a private proposed Chinese rendering.

Storage:

~~~text
User Workspace
 -> user_translation_proposal/version
~~~

It is not part of the official ResearchRelease.

Optional AI comparison may use the user's draft and published corpus/evidence, but the output is non-canonical until promoted through authoring/review/publication.

## 20. Interface matrix

| From | To | Interface | Allowed? | Reason |
|---|---|---|---|---|
| Browser | Serving DB simple workspace CRUD | Supabase Data API/client + RLS | Yes | Normal user data path |
| Browser | Corpus search | Public HTTP API | Yes | Validator/complexity guard required |
| Browser | PostgreSQL arbitrary SQL | Direct | No | Security/query semantics |
| Public API | Serving DB | Data API/RPC or pooled DB | Yes | Server-side domain path |
| Product MCP | Serving DB | Direct DB | No | MCP must use domain services |
| Product MCP | Public/domain service | Internal typed call/HTTP | Yes | Shared business semantics |
| Research Compiler | Authoring DB | Direct/pool | Yes | Bulk/private processing |
| Publication Worker | Authoring DB | Restricted direct read | Yes | Publication source |
| Publication Worker | Serving DB | Restricted direct write | Yes | One-way publication |
| Serving DB | Authoring DB | DB link/FDW | No | Breaks firewall |
| FHL Provider Adapter | FHL API | HTTP | Yes | Deterministic provider integration |
| Private research agent | FHL MCP | MCP | Optional | Agent convenience |
| Future paper source | Private compiler | MCP/API adapter | Yes | Private research input |
| Public app | Future paper MCP | Direct | No by default | Runtime rights/stability risk |
| Developer agent | Supabase MCP | MCP | Yes, dev/admin only | Development tooling |
| End user | Supabase MCP | MCP | No | Not a product interface |

## 21. Overall dry-run verdict

### Architecture direction

**PASS**

The four-plane product model and compiled-release model are compatible with a clean MCP/API/database topology.

### MCP placement

**PASS WITH STRONG CONSTRAINT**

MCP is appropriate at agent-facing boundaries.

It is not appropriate as the internal application/database bus.

### Public HTTP/API placement

**PASS**

The first-party product should use ordinary typed APIs/domain services.

Pinned-release endpoints must be added.

### Database placement

**PASS**

Private Authoring and Public Serving separation remains justified.

The Publication Worker is the deliberate bridge.

### v1.1 freeze readiness

**FAIL**

The dry run still exposes load-bearing gaps:

1. v1.1 is not self-contained;
2. machine-readable CorpusQuery/API/schema contracts are absent;
3. annotation layers are not first-class;
4. rights resolution algorithm/snapshot is missing;
5. provider-locator versus persisted segment storage is unresolved;
6. ResearchRelease payload/lifecycle/pointer semantics are incomplete;
7. release-component referential integrity remains weak;
8. published assertion/evidence model is incomplete;
9. important JSON payloads lack versioned schemas;
10. pinned release public API is not machine-defined.

The next implementation work should close these contract gaps before building the full product.
