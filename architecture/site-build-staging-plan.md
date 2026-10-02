# Site Build Staging Plan

Status: **architecture-stage only**. This document defines the boundaries and dependency order for the future 5 Site Build prompts. It is not itself a Site Build prompt.

## Why the build must be staged

This project is a research-grade Hebrew–Chinese Bible translation environment. The build order must follow the evidence architecture already defined in:

- `architecture/academic-evidence-policy.md`
- `docs/academic-source-taxonomy.md`
- `architecture/academic-storage-and-rag.md`

The UI must not be built first and then force the data model to fit it. Each stage must expose only functionality that can be supported by an inspectable data contract.

The current Vercel application is treated as a **reference implementation**, not as source code. Its useful product ideas should be reconstructed and improved, especially:

- passage navigation and deep-linkable verse selection
- MT / LXX / Chinese translation parallel reading
- proposed translation area
- translation-analysis view
- BHSA / syntax view
- source-and-citation view

The new application should preserve the research workflow but use a new architecture suitable for corpus search, academic RAG, translation alignment, source provenance, rights control, and reproducibility.

## Global UX direction

The interface must look like a serious academic research instrument.

Avoid:
- chatbot-first layouts
- large "Ask AI" boxes dominating the product
- purple/blue AI gradients
- glassmorphism
- decorative floating cards
- generic dashboard KPI tiles
- unnecessary animation
- excessive icons
- marketing-style AI language

Prefer:
- editorial / scholarly visual hierarchy
- restrained neutral palette
- strong typography
- clear Hebrew rendering and RTL handling
- dense but readable evidence tables
- stable navigation
- citation-forward presentation
- side panels and split views for research
- explicit evidence labels
- professional desktop-first research workflow with responsive support

AI should appear as one research capability inside the application, not as the identity of the interface.

---

# Stage 1: Research Shell, Legacy Reconstruction, and Core Data Contracts

## Primary goal

Build the stable application shell and reconstruct the useful workflow of the existing Vercel reference app before adding real corpus or RAG intelligence.

## Scope

### Application areas

Create the permanent top-level research areas:

1. Passage Study
2. Corpus Lab
3. Academic Library
4. Translation Rules
5. Research Projects

The initial functional emphasis is Passage Study. The other areas may initially contain structured placeholders that already conform to the final navigation.

### Core layout

Desktop research layout:

- global top navigation
- left Bible / project navigator
- central research workspace
- right inspector / evidence panel
- optional bottom status / provenance area where useful

Do not make the product a generic admin dashboard.

### Legacy-app reconstruction

Recreate and improve the useful functions represented in the existing Vercel app:

- book / chapter / verse navigation
- verse deep linking
- parallel reading
- MT display
- LXX display
- multiple Chinese translations
- optional English witness such as KJV when retained
- user's proposed translation
- translation-analysis tab
- syntax / BHSA-style tab
- sources / citations tab

This stage may use fixture data. It must not pretend fixture data is live corpus data.

### Evidence labels

Build the visual system for:

- PRIMARY TEXT
- CORPUS ANNOTATION
- CORPUS OBSERVATION
- SCHOLARLY CLAIM
- TRANSLATION WITNESS
- DOCUMENTED TRANSLATOR NOTE
- USER HYPOTHESIS
- SYSTEM INFERENCE
- AI SYNTHESIS
- UNKNOWN

These labels must become reusable components.

### Core entity contracts

Define interfaces / schemas for at least:

- Work
- Edition
- SourceAsset
- BibleReference
- Passage
- CanonicalToken
- Morpheme
- TranslationVersion
- TranslationUnit
- TranslationAlignment
- CorpusAnnotation
- ScholarlyClaim
- UserRule
- ResearchProject
- AnalysisRun
- SourceCitation

Do not yet implement the complete production database.

### Storage boundaries

Code must already respect this architecture:

- GitHub: code, schemas, migrations, prompts, tests, public metadata
- Google Drive: source library, not production database
- Supabase/PostgreSQL: future structured production data
- Supabase Storage or equivalent: controlled source assets
- Vercel: stateless application/runtime, not permanent corpus storage

## Explicitly excluded

Do not yet:
- build AI translation judgments
- ingest all academic books
- implement semantic vector RAG
- implement whole-Bible structural corpus search
- hard-code a fixed list of Chinese translations
- dump copyrighted translations into the repository

## Acceptance gate

Stage 1 passes only when:
- navigation is stable
- deep-linked passage state is stable
- core research panels work with fixtures
- Hebrew RTL renders correctly
- Chinese and Hebrew coexist without layout bugs
- evidence-type components are implemented
- later stages can attach real data without redesigning the application shell

---

# Stage 2: Passage Study and Chinese Translation Corpus Layer

## Primary goal

Turn Passage Study into a serious translation-comparison workbench and connect translation witnesses through a rights-aware provider abstraction.

## FHL integration strategy

Use `ytssamuel/FHL-MCP-Server` as a technical reference for the Faith, Hope, Love Bible API interaction pattern.

Do not copy its AI translation-comparison logic as the academic method.

Use dynamic version discovery rather than hard-coding the final set of versions.

For each translation version, store metadata including:

- provider version code
- display name
- language
- copyright / rights status
- provider
- retrieval method
- display permission
- caching permission
- local-storage permission
- redistribution permission
- commercial-use status
- attribution requirements

The MIT licence of FHL-MCP-Server applies to its code, not automatically to Bible texts returned by FHL.

## Passage Study functionality

### Hebrew display

Make MT tokens individually selectable.

Selecting a token should open a Word Inspector contract capable of displaying:

- surface form
- normalized form
- lemma
- morpheme segmentation
- POS
- morphology
- phrase membership
- clause membership
- syntax
- semantic class
- annotation source and version

Real data may still be partial until Stage 3.

### Chinese translations

Support a variable number of translation witnesses.

Do not design the database around exactly seven versions.

Provide:
- parallel display
- version chooser
- footnote / note capability
- source metadata
- loading / unavailable states
- provider error handling

### User-proposed translation

Provide a versioned editable field for the user's proposed translation.

Do not overwrite old research versions.

### Translation alignment

Data model must support many-to-many span alignment:

- Hebrew source span
- Chinese target span
- alignment type
- method
- confidence
- review status
- provenance

Do not force one Hebrew word to one Chinese word.

### Translation-difference analysis surface

Build the structured comparison UI around dimensions such as:

- lexical choice
- syntactic relation
- explicitness
- omission
- addition
- semantic abstraction
- interpretive expansion
- idiomatic rendering
- lexical repetition
- parallelism
- word order
- ambiguity preserved / resolved

At this stage, the interface may show reviewed fixture analyses. It must not invent translator intention.

## Acceptance gate

Stage 2 passes only when:
- FHL/provider abstraction supports dynamic versions
- rights metadata is part of the data contract
- translations load independently and fail gracefully
- user translation is versioned
- alignment supports many-to-many spans
- the UI explicitly distinguishes documented reason, scholarly explanation, system inference, and unknown

---

# Stage 3: Hebrew Corpus Engine and Grammar Pattern Search

## Primary goal

Implement deterministic Hebrew corpus research. This stage is the evidence engine for "find all relevant Hebrew examples."

## Corpus architecture

Primary production-oriented corpus layers should be designed around open / usable datasets such as:

- OSHB
- MACULA Hebrew

BHSA / Text-Fabric may be used as an advanced academic supplementary layer subject to licence constraints.

Do not make an external corpus ID the application's permanent canonical ID.

Create canonical internal identifiers and mapping tables between:

- canonical token
- OSHB identifier
- MACULA identifier
- BHSA node where available

## Text model requirements

Support:

- orthographic token
- morpheme
- phrase
- clause
- sentence
- syntax node
- syntax edge
- Ketiv / Qere
- versification mappings
- Hebrew Unicode normalization variants

Preserve original display text separately from searchable normalized forms.

## Query DSL

Design the internal query representation before the visual builder.

It must distinguish relations such as:

- immediately_precedes
- precedes
- follows
- within_n_tokens
- same_phrase
- same_clause
- same_sentence
- attached_to
- governs
- dependent_of

Ambiguous terms such as "before" must never have undefined semantics.

## Visual Pattern Builder

Support nodes based on:

- surface
- lemma
- POS
- morphology
- stem / binyan
- person / gender / number
- state
- prefix / suffix
- phrase type
- phrase function
- clause type
- semantic set

Support user semantic sets and version them.

## Search levels

Keep distinct:

1. Exact lexical match
2. Structural analogue
3. Semantic analogue
4. Contrastive construction

The UI must not imply these are equivalent evidence.

## Explainability

Every result should support:

- Why matched?
- exact node matches
- relation matches
- distance
- scope
- source annotation

Where feasible, build diagnostic support for "why did this expected verse not match?"

## Counting discipline

Keep separate:

- token-match count
- construction count
- clause count
- verse count
- passage count

Do not expose one ambiguous "N".

## Acceptance gate

Stage 3 passes only when:
- the same DSL query produces stable deterministic results
- GUI-generated and programmatically generated DSL are equivalent
- duplicate joins do not inflate counts
- exact, structural, semantic and contrastive result sets remain distinguishable
- Hebrew normalization, Ketiv/Qere and versification edge cases have regression tests

---

# Stage 4: Academic Knowledge Base, Structured Ingestion, and RAG

## Primary goal

Build the scholarly evidence system based primarily on the user's Google Drive library, while preserving source hierarchy, edition identity, rights restrictions and exact citations.

## Do not build one universal vector database

Route sources into distinct namespaces, including at minimum:

- REFERENCE_GRAMMAR
- PEDAGOGICAL_GRAMMAR
- MORPHOLOGY
- CORPUS_LINGUISTICS
- LEXICON
- THEOLOGICAL_LEXICON
- COMMENTARY
- TEXTUAL_CRITICISM
- DIACHRONIC_HEBREW
- EXEGESIS_METHOD
- TRANSLATION_DOCUMENTATION

## Work / edition / asset model

Deduplicate by:

Work
-> Edition
-> SourceAsset
-> ContentHash

Multiple copies of the same PDF must not create false scholarly consensus.

## Structured ingestion

Do not store only fixed-token chunks.

Target structure:

Document / Work
-> Edition
-> Chapter
-> Section
-> Subsection
-> Page
-> Paragraph / SourceSpan
-> Claim / Definition / Rule / Qualification / Exception / Example / CrossReference

Preserve:
- printed page
- PDF page index
- section identifiers
- exact source span
- extraction method
- extraction confidence
- review status

Original source text and generated summary must always remain separate.

## Source-specific retrieval structures

### Grammar

Retrieve rule + qualification + examples together where possible.

Preserve author-native terminology before cross-source conceptual mapping.

### Lexica

Model:

LexiconEntry
-> Sense
-> Usage
-> Examples

Do not flatten HALOT, DCH, BDB, TWOT, TLOT, TDOT into one authority level.

### Commentary

Passage-first retrieval:

BibleReference
-> eligible CommentaryUnit
-> hybrid retrieval within those units

Do not semantic-search the entire commentary library first when a passage is known.

### Textual criticism

Model textual evidence structurally:

Passage
-> ApparatusEntry
-> Witness
-> VariantReading
-> TextCriticalDiscussion

Do not treat BHS/BHQ apparatus as ordinary prose chunks.

## Ingestion pipelines

Classify source assets first:

- searchable PDF
- noisy / malformed-text PDF
- scanned / image PDF
- EPUB
- DOCX
- CHM
- image-only pages

Extraction failure must be visible and must never be interpreted as an empty source.

## Hybrid retrieval

Use:

1. exact citation / section lookup
2. Hebrew lemma / form lookup
3. full-text keyword retrieval
4. concept-graph traversal
5. semantic vector retrieval
6. reranking
7. deduplication
8. disagreement / counterevidence retrieval

Vector search is a discovery mechanism, not a source of truth.

## Rights gate

Every source must have a rights state, such as:

- VERIFIED_OPEN
- PUBLIC_DOMAIN
- LICENSED_FULLTEXT_PUBLIC
- LICENSED_INDEXING_PRIVATE
- LICENSED_PRIVATE_ONLY
- USER_SUPPLIED_RESEARCH_ONLY
- METADATA_ONLY
- RIGHTS_UNVERIFIED
- DO_NOT_INDEX

And granular permissions:

- may_extract
- may_embed
- may_store
- may_display
- may_quote
- may_redistribute
- may_commercialise

## Public and private research modes

Public Mode:
- open corpora
- public-domain sources
- appropriately licensed sources
- permitted translation text
- metadata and permitted excerpts

Private Research Mode:
- authenticated access to user-supplied research materials
- RLS-controlled retrieval
- private embeddings where permitted

## Acceptance gate

Stage 4 passes only when:
- duplicate works do not inflate retrieval evidence
- every scholarly claim is traceable to source / edition / location
- rights policy filters retrieval before evidence reaches the model
- retrieval respects namespace and question type
- rule / exception separation is regression-tested
- failed extraction is surfaced explicitly

---

# Stage 5: Research Orchestrator, Translation Analysis, Rule System, and Full QA

## Primary goal

Only after the corpus engine and academic evidence system exist, add AI-assisted research synthesis.

AI must operate on retrieved evidence rather than model memory.

## Research-intent router

Classify questions such as:

- morphology
- syntax
- preposition / particle semantics
- lexical sense
- corpus parallel
- textual criticism
- translation comparison
- discourse
- diachronic Hebrew
- commentary interpretation

Then select eligible evidence namespaces.

## Research orchestration

For a translation question, the system should be capable of executing a research plan such as:

1. inspect current Hebrew form
2. retrieve morphology and syntax
3. run exact corpus query
4. run structural analogue query
5. run contrastive query
6. retrieve relevant reference-grammar sections
7. retrieve relevant lexicon senses
8. retrieve passage-specific commentary
9. retrieve textual-critical evidence where relevant
10. retrieve Chinese translation witnesses
11. retrieve documented translator notes where available
12. retrieve user's current translation and research rules
13. search for counterevidence
14. synthesize with explicit uncertainty

## Evidence matrix

Build an inspectable evidence matrix containing separate lanes for:

- morphology
- syntax
- corpus
- grammar
- lexicon
- commentary
- textual criticism
- translation witnesses
- user research
- AI synthesis

## Translation-analysis policy

Never state translator intention without direct evidence.

Distinguish:

- Documented reason
- Scholarly explanation
- System inference
- Unknown

A Chinese translation's existence is evidence of a translation choice, not proof that its underlying grammatical interpretation is correct.

## User rule system

User rules are versioned research objects.

A rule may be suggested from scholarly and corpus evidence, but must never silently become a "grammar fact".

Store:
- rule version
- trigger conditions
- evidence links
- exclusions
- counterexamples
- user approval / review state
- translation implications

## "Challenge my translation"

Build an adversarial research workflow that actively seeks:

- counterexamples
- competing syntax analyses
- conflicting grammar classifications
- lexicon senses that weaken the proposal
- translations that preserve different source features
- unsupported assumptions

The goal is not to confirm the user's preferred translation.

## Reproducibility

Each serious analysis run should persist:

- corpus versions
- query DSL
- semantic-set versions
- source editions
- retrieved source IDs
- rule versions
- user translation version
- model / prompt version
- evidence counts
- inclusion / exclusion logic
- timestamp

## Final QA

Run regression checks across all earlier stages.

Required QA areas include:

- Hebrew RTL
- Unicode normalization
- Ketiv/Qere
- versification
- Chinese text wrapping
- many-to-many alignment
- deep links
- back navigation
- provider failures
- empty states
- no-result searches
- stale cache
- stale embeddings
- source citation integrity
- rights filtering
- RLS
- duplicate evidence
- corpus count inflation
- long quotations / display rights
- responsive layouts
- no text overlap or clipping

Stage 5 must not redesign the application unless a verified usability defect requires it.

---

# Build sequencing rules for every future Site Build prompt

Every prompt after Stage 1 must begin from the existing project and must preserve prior working functionality.

The future prompt text should explicitly state:

> Continue modifying the existing project. Do not rebuild or replace the application. Preserve all existing working functionality, navigation, visual language, data contracts and interactions unless the current requirements explicitly require a change. Extend the existing architecture rather than creating parallel duplicate implementations.

Each stage must:

1. read and respect the existing architecture contracts
2. modify the existing project rather than create a parallel app
3. implement only its own scope
4. test its own acceptance criteria
5. rerun regression checks for earlier stages
6. avoid silently changing schemas established by earlier stages
7. leave clear extension points for the next stage

## GitHub checkpoint policy

After each completed build stage:

- inspect the resulting repository diff
- run relevant tests
- fix regressions
- commit the stage as a distinct checkpoint
- keep architecture documentation updated
- do not deploy to Vercel until the user explicitly requests deployment

Suggested stage checkpoint names:

- `build-01-foundation`
- `build-02-passage-translations`
- `build-03-hebrew-corpus`
- `build-04-academic-rag`
- `build-05-research-orchestrator`

## Current decision

The project should use **five** Site Build prompts, not four.

Reason:

Combining the Hebrew corpus engine and academic RAG into one prompt would put two fundamentally different search systems into the same implementation step:

- deterministic structural corpus search
- source-sensitive information retrieval

Keeping them separate materially reduces architectural and QA risk.
