# Academic Evidence and Translation Analysis Policy

## 1. Purpose

This project is a research-grade Hebrew Bible translation environment, not a devotional Bible chatbot and not a generic AI translation assistant.

The system must support rigorous, auditable analysis of Biblical Hebrew, Chinese Bible translations, corpus parallels, grammar, lexicography, textual criticism, and scholarly interpretation. Any proposed translation must be grounded in explicit evidence that can be inspected and traced back to its source.

The application must never present a model-generated explanation as if it were a scholarly claim, corpus fact, translator intention, or grammatical fact.

## 2. Source hierarchy

The system must distinguish source categories and never collapse them into one undifferentiated RAG corpus.

### Tier A: Primary textual evidence

Examples:
- Hebrew Bible base text
- OSHB
- MACULA Hebrew
- BHSA where licensing permits the intended use
- BHS / BHQ material when legally usable
- textual variants and apparatus data
- Chinese Bible translation texts retrieved through permitted sources

Use:
- exact wording
- morphology
- syntax
- textual variants
- corpus occurrence counts
- translation comparison

These sources provide evidence. They do not by themselves decide the final translation.

### Tier B: Reference grammars and syntax works

Core materials currently identified in the user's Google Drive include:
- Bruce K. Waltke and M. O'Connor, *An Introduction to Biblical Hebrew Syntax*
- Paul Joüon and Takamitsu Muraoka, *A Grammar of Biblical Hebrew*
- Gesenius, Kautzsch, Cowley, *Gesenius' Hebrew Grammar*
- Christo H. J. van der Merwe, Jacobus A. Naudé, Jan H. Kroeze, *A Biblical Hebrew Reference Grammar*
- Bill T. Arnold and John H. Choi, *A Guide to Biblical Hebrew Syntax*
- C. L. Seow, *A Grammar for Biblical Hebrew*
- John H. Sailhamer, *A Grammar of Biblical Hebrew*
- other grammar and morphology resources in the Drive library

Use:
- grammatical categories
- syntactic functions
- semantic functions of particles and prepositions
- clause and phrase analysis
- qualifications and exceptions
- author-specific terminology
- cited biblical examples

The system must preserve each author's own taxonomy. It must not silently normalize different authors into one category.

### Tier C: Lexica and lexical reference works

Core materials currently identified include:
- HALOT
- BDB
- TWOT
- TLOT
- Dictionary of Classical Hebrew
- Theological Dictionary of the Old Testament
- other lexica in the Drive library

Use:
- lexical range
- senses
- collocations
- semantic development
- etymological information where relevant
- usage examples

Lexical claims must be attributed to the specific lexicon. A lexicon entry must not be treated as proof of a syntactic interpretation without additional evidence.

### Tier D: Commentary and exegesis

Examples currently present in the Drive library include:
- NICOT
- New Cambridge Bible Commentary
- Anchor Bible
- other commentary collections

Use:
- verse-specific interpretations
- translation arguments
- textual-critical discussion
- discourse and literary observations
- history of interpretation

Commentary opinion must be labelled as commentary or scholarly interpretation, not as grammar fact.

### Tier E: User research

Includes:
- user-created translation rules
- research hypotheses
- annotations
- semantic sets
- preferred translation principles
- manually reviewed alignments

These are first-class research objects but must be clearly labelled as user hypotheses or decisions.

### Tier F: AI synthesis

AI may:
- plan retrieval
- map a natural-language question into a structured corpus query
- compare retrieved evidence
- identify disagreements
- generate a provisional synthesis
- identify counterexamples
- challenge a proposed translation

AI may not:
- invent a grammar rule
- attribute a view to an author without retrieved evidence
- infer translator intention and present it as documented fact
- fabricate corpus counts
- turn a user hypothesis into scholarly consensus
- silently merge conflicting scholarly taxonomies

## 3. Chinese Bible translation source strategy

The project may use the public GitHub repository:

- ytssamuel/FHL-MCP-Server

as a technical reference for interacting with the Faith, Hope, Love Bible API.

Relevant capabilities in that project include:
- listing available Bible versions
- retrieving verses and chapters
- searching Bible text
- obtaining some Strong's-linked data
- retrieving some translation footnotes
- querying FHL resources through structured endpoints

The FHL MCP project itself is MIT-licensed code, but the Bible contents returned by the FHL API are not covered by that MIT license.

The FHL MCP README and LICENSE explicitly state that:
- some Bible translations are licensed only for use on FHL
- the MCP server does not redistribute the Bible text
- users must follow the copyright restrictions of each translation

Therefore this project must not copy the FHL translation corpus into a public database merely because the API can return it.

For each translation, store rights metadata separately:
- version code
- version name
- copyright holder if known
- source provider
- retrieval method
- allowed display scope
- redistribution permission
- public availability
- commercial-use status
- caching permission
- local-storage permission
- attribution requirements

Until rights are verified, prefer API retrieval or restricted caching over permanent public redistribution.

## 4. FHL is not the scholarly authority for translation analysis

FHL is useful as a translation text and metadata provider.

It must not be used as the principal academic basis for explaining why a Hebrew construction should be translated in a particular way.

For example, if a Chinese translation renders a Hebrew phrase as "外貌", the analysis must not simply say that this is correct because the translation does so.

Instead the system should retrieve and compare:
1. Hebrew morphology and syntax
2. corpus parallels and contrastive constructions
3. relevant grammar discussions from the user's Drive
4. relevant lexicon entries
5. relevant commentary discussions
6. the Chinese translation wording
7. any documented translator notes or translation principles
8. the user's proposed translation

Only after those retrieval steps may the AI produce a synthesis.

## 5. Translation comparison model

For every selected passage, the system should compare:

- Hebrew source expression
- user's proposed translation
- each Chinese translation
- optional LXX / English comparison where relevant

Comparison dimensions may include:
- lexical choice
- syntactic relation
- semantic role
- explicitness
- omission
- addition
- semantic abstraction
- interpretive expansion
- idiomatic rendering
- preservation of lexical repetition
- preservation of parallelism
- word order
- discourse effect
- ambiguity preserved or resolved

The system must distinguish:

### Documented reason
The translator, publisher, translation notes, preface, or other primary documentation explicitly states the reason.

### Scholarly explanation
A scholar provides an explanation for the translation.

### System inference
The system infers a plausible explanation from the Hebrew and the translation.

### Unknown
There is insufficient evidence to determine the translator's actual reason.

The UI must not use language such as "the translators intended..." unless direct evidence supports that claim.

## 6. Evidence matrix for a proposed translation

Any serious translation recommendation should be based on an inspectable evidence matrix.

Suggested evidence groups:

### Morphology
- token
- morpheme segmentation
- lemma
- POS
- inflection
- state
- suffixes / prefixes

### Syntax
- phrase type
- phrase function
- clause relation
- dependency
- government
- constituent relationships

### Corpus
- exact lexical parallels
- structural parallels
- semantic analogues
- contrastive constructions
- counterexamples
- frequency by book / genre / construction

### Grammar
- source
- author
- edition
- section
- page
- original terminology
- extracted claim
- qualifications
- examples

### Lexicon
- source
- lemma
- sense
- usage notes
- examples

### Commentary
- scholar
- work
- passage
- interpretation
- translation implication

### Translation witnesses
- translation name
- exact wording
- alignment to Hebrew spans
- footnotes
- documented translation policy where available

### User research
- user's proposed translation
- user rule
- notes
- confidence

### AI synthesis
- conclusion
- uncertainty
- strongest supporting evidence
- strongest opposing evidence
- unresolved questions

## 7. Retrieval architecture

The academic library must not be one large vector collection.

Use separate retrieval namespaces at minimum:
- Grammar
- Lexica
- Commentary
- Textual Criticism
- Exegesis Methodology
- Bible Translation Documentation

Use hybrid retrieval:
1. exact section / citation lookup
2. Hebrew lemma and phrase lookup
3. keyword / full-text retrieval
4. structured concept graph traversal
5. semantic vector retrieval
6. reranking

Vector retrieval is a discovery layer, not a source of truth.

When a source uses section numbering, paragraph numbering, or stable headings, exact retrieval should receive priority over semantic similarity.

## 8. Structured ingestion requirements

Do not store only PDF chunks.

The target hierarchy should support:

Document
-> Edition
-> Chapter
-> Section
-> Subsection
-> Page
-> Paragraph
-> Claim / Definition / Rule / Qualification / Exception / Example / Cross-reference

Every extracted scholarly claim should retain:
- source document
- edition
- printed page
- PDF page
- section identifier
- source text span
- extraction method
- extraction confidence
- review status

The original source text and AI-generated summary must always be stored separately.

## 9. PDF quality handling

The current Drive corpus is heterogeneous.

Initial sampling shows:
- Waltke-O'Connor: large readable text layer
- GKC: readable text layer
- Arnold-Choi: readable text layer
- Joüon-Muraoka: current Drive text extraction returned no text
- Van der Merwe et al.: current Drive text extraction returned no text

Therefore ingestion must first classify source quality.

Possible pipelines:
- searchable PDF -> structured text extraction
- malformed text encoding -> normalization and repair
- scanned PDF -> page-image / OCR or vision-assisted extraction
- EPUB -> native structural parsing
- CHM -> dedicated extraction
- image-only page -> image-based fallback

The system must never silently treat an extraction failure as an empty scholarly source.

## 10. Research integrity labels

Every visible analytical statement should be capable of carrying one of the following evidence labels:

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

This distinction is mandatory in both data modelling and UI design.

## 11. Counterevidence requirement

The system should not be optimized to confirm the user's preferred translation.

When evaluating a translation, retrieval should actively search for:
- counterexamples
- competing syntactic analyses
- other grammatical categories
- corpus examples that behave differently
- scholarly disagreement
- translations that preserve a different feature of the source

A future "Challenge my translation" function should be built on this principle.

## 12. Reproducibility

Any research-grade analysis should preserve:
- corpus source and version
- corpus query definition
- semantic-set version
- grammar-source version / edition
- retrieved source IDs
- rule version
- user translation version
- AI model and prompt version
- timestamp
- result counts
- inclusion and exclusion logic

A result such as "37 parallels" must be reproducible and must specify whether 37 means:
- token matches
- construction matches
- clauses
- verses
- passages

## 13. Non-negotiable rule

The final application must be academically conservative.

When evidence is incomplete, the system should say that the evidence is incomplete.

When scholars disagree, the system should show the disagreement.

When a translation is possible but not demonstrable, the system should call it plausible rather than proven.

When translator intention is unknown, the system should say it is unknown.

The product goal is not to make AI sound confident. The goal is to make the research process inspectable, reproducible, and defensible.
