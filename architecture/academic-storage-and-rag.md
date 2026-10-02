# Storage and RAG Architecture for Academic Hebrew Translation Research

## Status

This architecture follows the scholarly classification in `docs/academic-source-taxonomy.md`.

The central design rule is:

> Store sources according to what they are, retrieve them according to what question they can answer, and only then allow AI synthesis.

The application must not use a generic "PDF to chunks to vectors to chatbot" pipeline.

## 1. Separation of systems

The project has four fundamentally different evidence systems.

### 1.1 Biblical corpus system

Purpose:

- Hebrew text;
- tokenisation;
- morphemes;
- morphology;
- phrase and clause annotation;
- syntax;
- corpus frequency;
- structural queries;
- semantic sets.

Retrieval model:

Deterministic structured query, not RAG.

### 1.2 Translation corpus system

Purpose:

- Chinese translation witnesses;
- translation metadata;
- verse mappings;
- many-to-many Hebrew-Chinese alignment;
- footnotes;
- documented translation policy.

Retrieval model:

Reference/verse lookup plus structured alignment and comparison.

### 1.3 Academic literature system

Purpose:

- grammars;
- lexica;
- textual criticism;
- commentaries;
- language history;
- methodology;
- rhetorical/literary research.

Retrieval model:

Rights-aware, source-type-aware hybrid retrieval.

### 1.4 Research workspace system

Purpose:

- user translation proposals;
- user rules;
- semantic sets;
- annotations;
- saved queries;
- research projects;
- analysis runs.

Retrieval model:

User-scoped structured retrieval plus optional semantic search.

These systems may contribute to one analysis, but they must never be collapsed into one search index.

## 2. Recommended physical architecture

### 2.1 GitHub

Repository:

`Enochan222/hebrew-chinese-bible-research`

Store in GitHub:

- application code;
- database migrations;
- ingestion code;
- query DSL;
- prompts and prompt versions;
- test fixtures that are legally redistributable;
- architecture decisions;
- source metadata templates;
- public/open source manifests;
- schema documentation.

Do not store in GitHub:

- copyrighted textbook PDFs;
- copyrighted translation corpora;
- extracted full text from restricted books;
- secrets;
- Supabase service keys;
- Google Drive credentials;
- large corpus releases unless the licence explicitly allows redistribution and Git is appropriate.

### 2.2 Google Drive

Use Google Drive as the user's source library and acquisition layer, not as the production search database.

Keep:

- original PDFs;
- EPUB files;
- DOCX course notes;
- source folder organisation;
- user-owned reference files.

The application should record a private external source locator for each Drive item, but public GitHub documentation should not expose shared Drive URLs to copyrighted source files.

### 2.3 PostgreSQL / Supabase

Use PostgreSQL as the principal structured store for:

- bibliographic identity;
- edition identity;
- source provenance;
- rights metadata;
- document hierarchy;
- scholarly claims;
- grammatical examples;
- concept mappings;
- biblical-reference links;
- Hebrew-lemma links;
- retrieval units;
- embeddings when permitted;
- full-text indexes;
- user research;
- corpus data;
- translation metadata and alignments.

PostgreSQL should remain the canonical database even if other search infrastructure is introduced later.

### 2.4 Object storage

Use private object storage only for material whose rights permit copying to the application's infrastructure.

Possible stored objects:

- open corpus release archives;
- permitted original source files;
- permitted extracted derivatives;
- page thumbnails or OCR artefacts where legally allowed;
- ingestion diagnostics;
- parser reports.

Do not automatically mirror every Google Drive book into Supabase Storage.

For restricted books, the default architecture should support retaining the source only in the user's controlled source library and storing only the level of derived data that is legally permitted.

## 3. Rights gate before ingestion

Every source must have a `rights_profile` before entering persistent RAG.

Suggested values:

- VERIFIED_OPEN
- PUBLIC_DOMAIN
- LICENSED_FULLTEXT_PUBLIC
- LICENSED_INDEXING_PRIVATE
- LICENSED_PRIVATE_ONLY
- USER_SUPPLIED_RESEARCH_ONLY
- METADATA_ONLY
- RIGHTS_UNVERIFIED
- DO_NOT_INDEX

Separate permissions:

- may_store_original
- may_extract_text
- may_store_extracted_text
- may_embed
- may_display_fulltext
- may_display_excerpt
- may_export
- may_redistribute
- may_use_commercially

A source with `RIGHTS_UNVERIFIED` must default to restrictive behaviour.

The system must not infer permission from the fact that a PDF exists in Drive.

## 4. Public mode and private research mode

The project should support two evidence modes.

### 4.1 Public product mode

May use:

- open/licensed Hebrew corpora;
- public-domain sources;
- licensed scholarly sources;
- externally retrieved translation text where provider terms permit display;
- bibliographic metadata for restricted works;
- permitted short citations/excerpts.

Must not expose:

- unlicensed textbook full text;
- unlicensed translation full corpora;
- private course notes;
- user Drive URLs.

### 4.2 Private research mode

May access user-authorised private sources subject to the user's lawful rights.

Private retrieval must still obey:

- source attribution;
- access control;
- no accidental public caching;
- no cross-user retrieval;
- no public export of restricted text.

The database should not assume that private access automatically authorises persistent full-text indexing. Rights metadata still applies.

## 5. Bibliographic identity model

Do not model a book as one row called `document`.

Use at least:

### `works`

Represents the intellectual work.

Fields:

- work_id
- canonical_title
- work_type
- primary_author_ids
- original_publication_year
- scholarly_domain
- methodological_orientation

Example:

Joüon and Muraoka, `A Grammar of Biblical Hebrew`.

### `editions`

Represents a particular edition/revision.

Fields:

- edition_id
- work_id
- edition_statement
- publication_year
- publisher
- ISBN
- language
- edition_status
- newer_edition_known
- bibliographic_notes

### `source_assets`

Represents a concrete file or licensed digital source.

Fields:

- asset_id
- edition_id
- provider
- external_locator
- mime_type
- byte_size
- sha256
- extraction_status
- extraction_quality
- rights_profile_id
- source_created_at
- ingested_at

Multiple Drive copies may map to the same edition.

## 6. Duplicate prevention

Deduplication must happen before embeddings.

### Level 1: exact file duplicate

Use:

- SHA-256;
- file size.

### Level 2: same edition, different file

Match:

- title;
- author;
- publisher;
- year;
- ISBN;
- pagination where possible.

### Level 3: text duplicate

Use normalized hashes of:

- section text;
- paragraph text;
- lexicon entry text.

Never let duplicate source files create multiple independent evidence votes.

The retrieval system should count scholarly works, not file copies.

## 7. Edition-aware retrieval

All retrieval units inherit edition identity.

A query result must be able to say:

- Joüon-Muraoka, edition X;
- van der Merwe et al., 1999 first edition;
- Arnold-Choi, 2003 first edition.

If a newer edition is known but unavailable, expose that fact.

Suggested fields:

- `edition_status`
- `superseded_by_edition_id`
- `edition_warning`

The synthesiser must not call an older Drive edition "the latest edition."

## 8. Document hierarchy model

Use a generic tree for structural navigation:

### `document_nodes`

Fields:

- node_id
- edition_id
- parent_node_id
- node_type
- ordinal
- title
- section_label
- logical_page_start
- logical_page_end
- physical_page_start
- physical_page_end
- source_text
- normalized_text
- source_span_start
- source_span_end
- extraction_method
- extraction_confidence
- review_status

Possible `node_type`:

- PART
- CHAPTER
- SECTION
- SUBSECTION
- ENTRY
- ARTICLE
- PERICOPE
- VERSE_NOTE
- PARAGRAPH
- FOOTNOTE
- APPARATUS_ENTRY
- TABLE
- EXAMPLE_BLOCK

Printed page and PDF page must remain separate.

## 9. Source text and interpretation must be separate

Never overwrite source text with AI interpretation.

At minimum:

- `source_text`
- `normalized_text`
- `ai_summary`
- `ai_summary_model`
- `ai_summary_prompt_version`
- `review_status`

An AI summary can be regenerated.

The source span is immutable evidence.

## 10. Claim-level model

The academically useful unit is often a claim, not a chunk.

### `scholarly_claims`

Fields:

- claim_id
- node_id
- claim_type
- claim_text
- source_span_id
- author_id
- confidence
- extraction_method
- review_status

Possible claim types:

- DEFINITION
- GRAMMAR_RULE
- CLASSIFICATION
- QUALIFICATION
- EXCEPTION
- LEXICAL_SENSE
- TEXT_CRITICAL_JUDGMENT
- INTERPRETIVE_CLAIM
- METHODOLOGICAL_CLAIM
- HISTORICAL_CLAIM

### `claim_relations`

Possible relations:

- QUALIFIES
- EXCEPTS
- SUPPORTS
- DISAGREES_WITH
- REVISES
- DEPENDS_ON
- EXAMPLE_OF
- ALTERNATIVE_TO

This allows the system to preserve disagreement instead of averaging it away.

## 11. Biblical example model

Grammar examples must be structured.

### `source_biblical_examples`

Fields:

- example_id
- source_node_id
- claim_id
- canonical_passage_id
- quoted_hebrew
- author_analysis
- example_role
- source_order
- verified_against_corpus

Possible roles:

- POSITIVE_EXAMPLE
- COUNTEREXAMPLE
- EXCEPTION
- COMPARATIVE_EXAMPLE
- AMBIGUOUS_EXAMPLE

The author's cited example and the application's corpus analysis must remain separate.

## 12. Grammar-specific storage

For grammars, preserve:

- source-native taxonomy;
- section hierarchy;
- grammatical labels;
- rule statements;
- qualifications;
- exceptions;
- examples;
- cross-references.

Add:

### `grammar_terms`

Fields:

- grammar_term_id
- edition_id
- source_term
- source_definition
- source_node_id

### `concept_mappings`

Maps a source-specific term to an application concept without replacing it.

Example:

- source: "lamed of norm"
- canonical concept: LAMED_NORM_CRITERION
- mapping confidence
- mapping rationale
- reviewed_by

The UI must be able to show both.

## 13. Lexicon-specific storage

Do not arbitrarily chunk lexica.

Use:

### `lexicon_entries`

- entry_id
- edition_id
- headword
- normalized_headword
- root
- homonym_number
- grammatical_category
- source_node_id

### `lexicon_senses`

- sense_id
- entry_id
- source_sense_label
- gloss
- definition
- usage_notes
- diachronic_label
- register_label
- source_span_id

### `lexicon_examples`

- sense_id
- biblical_reference
- extra_biblical_reference
- quoted_form
- context_note

Important:

HALOT, DCH and BDB must remain independent sense taxonomies.

Do not create one universal sense inventory and erase the differences.

A cross-lexicon semantic mapping may exist as an additional layer.

## 14. Commentary-specific storage

Commentary retrieval should begin from biblical reference.

### `commentary_units`

- unit_id
- edition_id
- canonical_passage_start
- canonical_passage_end
- unit_type
- heading
- source_node_id

Possible types:

- TRANSLATION
- TEXTUAL_NOTE
- PHILOLOGICAL_NOTE
- STRUCTURE
- COMPOSITION
- COMMENT
- THEOLOGY
- EXCURSUS

This matters because a vector search over a 600-page commentary is inferior to first selecting the passage and then searching the relevant commentary units.

## 15. Textual-criticism-specific storage

BHS/BHQ and critical apparatus require specialised structures.

Possible tables:

### `textual_witnesses`

- witness_id
- siglum
- witness_type
- language
- date_range

### `textual_variants`

- variant_id
- canonical_passage_id
- base_reading
- variant_reading
- witness_id
- source_edition_id

### `apparatus_entries`

- apparatus_entry_id
- passage_id
- edition_id
- sigla_raw
- parsed_data
- source_span

### `text_critical_discussions`

For Tov, Brotzman-Tully, commentary discussions and other secondary analysis.

Do not vector-search apparatus notation as if it were normal prose.

## 16. User and course material storage

Course notes and user files should be stored in a separate namespace.

Fields should include:

- owner_id
- source_type = USER_NOTE / COURSE_NOTE / RESEARCH_DRAFT
- author if known
- course
- date
- confidence
- citation_eligible

Default:

`citation_eligible = false`

unless deliberately promoted and reviewed.

## 17. Retrieval unit is not the same as source node

A `document_node` preserves source structure.

A `retrieval_unit` is a search representation.

### `retrieval_units`

Fields:

- retrieval_unit_id
- node_id
- namespace
- retrieval_text
- title_path
- keyword_text
- language
- content_hash
- embedding_status
- FTS status
- rights_profile_id
- active
- generation_method

This lets the app change retrieval strategy without altering source structure.

## 18. No universal fixed-size chunking

Do not make 500-token chunks the canonical representation.

### Grammar

Preferred retrieval unit:

- section or subsection;
- claim plus immediate qualification;
- rule plus attached examples.

If a section is too large, create retrieval windows but preserve the structural parent.

### Lexicon

Preferred unit:

- lexical entry;
- individual sense where sufficiently self-contained.

### Commentary

Preferred unit:

- verse note;
- pericope section;
- technical note.

### Textual criticism

Preferred unit:

- passage-specific apparatus/discussion.

### Methodology

Preferred unit:

- coherent section or procedural step.

### Historical/diachronic works

Preferred unit:

- argument subsection;
- study result;
- explicit methodological claim.

## 19. Extraction pipeline

### Stage 0: source registration

Record:

- work;
- edition;
- asset;
- rights;
- checksum.

### Stage 1: file classification

Detect:

- searchable PDF;
- noisy text PDF;
- image-only PDF;
- EPUB;
- DOCX;
- CHM;
- image.

### Stage 2: deterministic extraction

Extract where possible:

- page boundaries;
- headings;
- paragraphs;
- footnotes;
- tables;
- Hebrew spans;
- Bible references.

### Stage 3: structural reconstruction

Build the source hierarchy.

### Stage 4: scholarly object extraction

Identify:

- claims;
- definitions;
- rules;
- qualifications;
- exceptions;
- examples;
- cross-references.

### Stage 5: entity linking

Link to:

- Hebrew lemmas;
- grammatical concepts;
- biblical passages;
- scholars;
- other works.

### Stage 6: validation

Run:

- section continuity check;
- page coverage check;
- duplicate check;
- Hebrew corruption check;
- Bible-reference validation;
- extraction confidence review.

### Stage 7: retrieval publication

Only after validation and rights checks:

- create retrieval units;
- create FTS representation;
- generate embeddings if allowed;
- mark source searchable.

## 20. Extraction quality should not change scholarly authority

Maintain separate values:

- `scholarly_role`
- `extraction_quality`

Joüon-Muraoka may have extraction quality = poor while scholarly role = major reference grammar.

A low extraction score means "needs a better parser," not "low academic value."

## 21. Recommended RAG namespaces

At minimum:

- GRAMMAR_REFERENCE
- GRAMMAR_CORPUS
- GRAMMAR_PEDAGOGICAL
- MORPHOLOGY_PHONOLOGY
- LEXICON_GENERAL
- LEXICON_CLASSICAL_HEBREW
- LEXICON_THEOLOGICAL
- LEXICON_DIACHRONIC
- TEXTUAL_CRITICISM
- CRITICAL_EDITION_GUIDE
- DSS_QUMRAN
- SEPTUAGINT_STUDIES
- COMMENTARY
- EXEGESIS_METHOD
- RHETORICAL_LITERARY
- HEBREW_LANGUAGE_HISTORY
- HISTORICAL_BACKGROUND
- USER_RESEARCH
- COURSE_MATERIAL

Do not search all namespaces for every query.

## 22. Query-intent router

Before literature retrieval, classify the research request.

Possible intents:

- MORPHOLOGY
- PHONOLOGY
- SYNTAX
- PREPOSITION_SEMANTICS
- LEXICAL_SEMANTICS
- WORD_ORDER
- DISCOURSE
- DIACHRONY
- TEXTUAL_CRITICISM
- MASORAH
- LXX
- DSS
- RHETORIC
- PASSAGE_EXEGESIS
- TRANSLATION_COMPARISON
- TRANSLATION_JUDGMENT
- METHODOLOGY

A research query may activate more than one intent.

The router output must be visible in debug/research mode.

## 23. Retrieval plan by intent

### Syntax / preposition semantics

1. deterministic Hebrew corpus query;
2. exact grammar term search;
3. major reference grammar retrieval;
4. corpus-linguistic grammar retrieval;
5. intermediate syntax reference;
6. historical grammar for comparison;
7. passage commentary only after grammar evidence.

### Lexical semantics

1. corpus distribution;
2. exact lemma lookup;
3. HALOT / DCH / BDB if permitted;
4. semantic/collocational search;
5. theological lexica only as secondary layer;
6. commentary for contextual interpretation.

### Textual criticism

1. exact passage;
2. BHS/BHQ apparatus;
3. witness data;
4. Tov / specialist methodology;
5. DSS/LXX sources;
6. passage commentary.

### Diachronic question

1. exact linguistic feature;
2. Hebrew language history;
3. specialist EBH/LBH literature;
4. corpus distribution;
5. competing scholarly positions.

### Passage translation

Run multiple evidence lanes in parallel:

- text/morphology;
- syntax;
- lexical;
- corpus parallels;
- textual criticism if relevant;
- commentary;
- Chinese translation witnesses;
- translator notes;
- user rules.

The final synthesis happens only after the evidence packet is complete.

## 24. Exact retrieval must precede semantic retrieval when possible

Examples:

If query contains:

- `JM §133`
- `WOC 11.2`
- `HALOT עין`
- `1 Sam 16:7`

use exact lookup first.

Semantic retrieval should not compete with an exact bibliographic or lexical target.

Priority order:

1. stable identifier;
2. exact biblical reference;
3. Hebrew lemma/root;
4. source-native terminology;
5. keyword/full-text;
6. semantic vector search.

## 25. Hybrid retrieval within a namespace

Where rights permit persistent indexing, combine:

- PostgreSQL full-text search;
- semantic vector search;
- metadata filters.

Use rank fusion rather than adding incompatible raw scores.

Postgres/Supabase can support:

- `tsvector` for full-text search;
- `pgvector` for vector similarity;
- HNSW indexes;
- Reciprocal Rank Fusion.

However, this is only the low-level retrieval mechanism.

The scholarly router must decide which namespace is eligible before hybrid search runs.

## 26. Multilingual retrieval

Users may ask in Hong Kong Traditional Chinese while sources are primarily English and Hebrew.

The retrieval layer should support:

### Query normalisation

Input:

"呢度個 ל 可唔可以係工具用法？"

Structured query expansion:

- Hebrew: ל
- English terms: instrumental, means, instrument
- Chinese aliases: 工具、手段、藉着、用
- related source terms: instrument, means, instrumental lamed

Do not replace the user's wording. Create an auditable search expansion.

### Embeddings

If embeddings are used, choose a model that performs adequately for:

- Chinese;
- English;
- Hebrew technical terms.

Store:

- embedding model;
- dimensions;
- embedding version;
- input hash.

Never mix embeddings from incompatible models in one vector column/index.

## 27. Reranking policy

A result's rank must not depend only on semantic similarity.

Possible ranking signals:

- exact section match;
- exact Hebrew lemma;
- exact biblical reference;
- scholarly namespace fit;
- source role;
- edition status;
- section title match;
- lexical/technical keyword match;
- semantic similarity;
- passage proximity;
- extraction confidence;
- review status.

Do not use an opaque universal "authority score."

Instead use question-specific source fitness.

## 28. Source diversity control

Before synthesis:

- collapse duplicate files;
- collapse duplicate editions where the content is identical;
- identify same-author repetition;
- cap excessive results from one work;
- require multiple independent works for a claim of broad agreement.

Example:

Five retrieved chunks from Waltke-O'Connor are still one scholarly source, not five votes.

## 29. Contradiction-aware retrieval

The retrieval system should actively search for:

- alternative categories;
- qualifications;
- exceptions;
- competing grammatical analyses;
- negative evidence;
- counterexamples.

For a disputed construction, a second retrieval pass should ask:

"Which retrieved sources or corpus results would make the proposed analysis less likely?"

This is mandatory for the future `Challenge my translation` function.

## 30. Evidence packet before generation

The model should receive an explicit structured packet such as:

```
Research question
Current passage
Current Hebrew tokens
Morphology evidence
Syntax evidence
Corpus exact matches
Corpus structural analogues
Corpus counterexamples
Grammar claims
Lexicon senses
Text-critical evidence
Commentary claims
Chinese translation witnesses
Documented translator notes
User hypothesis
Known disagreements
Missing evidence
```

Every item carries source IDs and provenance.

The language model does not decide which verses "exist." That comes from the corpus engine.

## 31. Citation contract

Every scholarly claim used in final analysis must be traceable to:

- work;
- edition;
- section;
- printed page where available;
- PDF page;
- source span.

The UI should allow "View source" when rights permit.

If full source display is restricted, the UI can still show bibliographic citation and a legally permitted excerpt or reference.

## 32. Evidence labels in generation

Statements should be tagged internally as:

- PRIMARY_TEXT
- CORPUS_ANNOTATION
- CORPUS_OBSERVATION
- SCHOLARLY_CLAIM
- TRANSLATION_WITNESS
- DOCUMENTED_TRANSLATOR_NOTE
- USER_HYPOTHESIS
- SYSTEM_INFERENCE
- AI_SYNTHESIS
- UNKNOWN

The frontend may display these as subtle professional badges rather than colourful AI-style labels.

## 33. No hallucinated consensus

The synthesis layer must not say:

"Scholars agree..."

unless a consensus claim is actually supported by a sufficiently diverse source set.

Preferred formulations:

- "Joüon-Muraoka classifies..."
- "Waltke-O'Connor treats..."
- "These two sources converge on..."
- "The retrieved sources disagree..."
- "The current library does not provide enough evidence to establish..."

## 34. Embedding lifecycle

Embeddings are disposable derived data.

### `embeddings`

Fields:

- embedding_id
- retrieval_unit_id
- model_provider
- model_name
- model_version
- dimensions
- input_hash
- created_at
- stale_at
- status

If retrieval text changes:

1. invalidate old embedding;
2. queue a new embedding job;
3. do not serve the stale vector as current evidence.

An asynchronous queue is preferable to doing embedding generation synchronously inside a user request.

## 35. Search-index lifecycle

Maintain:

- ACTIVE
- STALE
- PENDING_REINDEX
- FAILED
- DISABLED_RIGHTS
- DISABLED_QUALITY

A parser failure must not silently leave stale searchable text in production.

## 36. Ingestion job state machine

Use:

- REGISTERED
- RIGHTS_CHECK
- EXTRACTING
- STRUCTURING
- LINKING
- VALIDATING
- READY_FOR_REVIEW
- APPROVED
- INDEXING
- ACTIVE
- FAILED
- BLOCKED_RIGHTS

Ingestion should be idempotent.

Re-running the same asset with the same parser version must not create duplicate document trees.

## 37. Parser versioning

Store:

- parser_name;
- parser_version;
- extraction_config;
- source checksum;
- extraction timestamp.

If the parser improves, create a new extraction version before promoting it.

Do not mutate the only copy of extracted text without history.

## 38. Review workflow

Important academic sources should support review at:

- document structure level;
- section heading level;
- claim extraction level;
- Hebrew example level;
- citation/page level.

Review status:

- UNREVIEWED
- AUTO_VALIDATED
- HUMAN_REVIEWED
- NEEDS_CORRECTION
- REJECTED

The application should prioritise human-reviewed evidence when otherwise comparable.

## 39. Hebrew-aware indexing for literature

Standard English full-text search is not enough.

Store searchable representations separately:

- Hebrew original;
- Unicode-normalised Hebrew;
- consonantal form;
- no-cantillation form;
- lemma;
- transliteration aliases;
- English technical term;
- Chinese technical term.

Do not strip the source text itself.

## 40. Bible-reference parser

Every literature ingestion should detect biblical references and resolve them to canonical passage IDs.

Examples:

- 1 Sam 16:7
- 1 Samuel xvi 7
- 1 S 16,7
- שמ״א טז 7 where supported

Do not rely only on embeddings to discover passage-specific discussion.

## 41. Concept graph

Concepts should not replace source terminology.

Possible canonical concepts:

- PREPOSITION_LAMED
- INSTRUMENT
- MEANS
- REFERENCE_RESPECT
- NORM_CRITERION
- BENEFICIARY
- GOAL
- BODY_PART
- PERCEPTION_VERB

Relations:

- BROADER_THAN
- NARROWER_THAN
- RELATED_TO
- CONTRASTS_WITH
- SOURCE_CALLS_THIS
- EXAMPLE_OF

Source-specific mappings remain explicit and reviewable.

## 42. Corpus engine remains separate from RAG

Never ask document RAG to find all Hebrew Bible examples of a construction.

Correct flow:

Natural-language research question
-> validated query DSL
-> corpus database
-> exact result set
-> statistics
-> literature retrieval
-> synthesis

RAG may explain the construction.

RAG must not decide the exhaustive corpus membership.

## 43. Chinese translation corpus remains separate from RAG

FHL and other permitted sources provide translation witnesses.

Store:

- translation version;
- verse text or provider reference according to rights;
- verse mapping;
- footnotes;
- source/provider;
- rights.

Alignment:

- Hebrew source span;
- Chinese target span;
- alignment confidence;
- method;
- review status.

Do not use embeddings as the primary method for translation alignment.

## 44. Translation-analysis retrieval protocol

When analysing a user's proposed translation:

### Lane 1: Hebrew form

Retrieve:

- token;
- morpheme;
- lemma;
- morphology;
- phrase;
- clause;
- syntax.

### Lane 2: corpus

Retrieve:

- exact parallels;
- structural parallels;
- semantic analogues;
- contrastive constructions;
- counterexamples.

### Lane 3: grammar

Retrieve at least two relevant independent major grammar sources when available.

### Lane 4: lexicon

Retrieve appropriate general lexica.

### Lane 5: textual criticism

Only activate if textual variation could affect interpretation.

### Lane 6: commentary

Retrieve passage-specific technical discussion.

### Lane 7: translation witnesses

Retrieve Chinese renderings and notes.

### Lane 8: user rules

Apply versioned user hypotheses.

### Lane 9: challenge pass

Search for evidence against the provisional analysis.

### Lane 10: synthesis

Only now generate an assessment.

## 45. Translation explanation policy

The system must distinguish:

### Documented translator reason

Primary translation documentation explicitly explains the choice.

### Scholarly explanation

A scholar explains or defends a translation.

### System inference

The system observes that a translation is compatible with a particular analysis.

### Unknown

There is no adequate evidence for why the translator chose the wording.

The phrase "the translator intended" is prohibited unless supported by documentation.

## 46. Suggested core tables

### Source and bibliography

- authors
- works
- work_authors
- editions
- source_assets
- rights_profiles
- ingestion_runs
- extraction_versions

### Document structure

- document_nodes
- source_spans
- footnotes
- cross_references

### Scholarly knowledge

- scholarly_claims
- claim_relations
- source_biblical_examples
- grammar_terms
- concepts
- concept_relations
- concept_mappings

### Lexica

- lexicon_entries
- lexicon_senses
- lexicon_examples

### Commentary

- commentary_units
- commentary_passage_links

### Textual criticism

- textual_witnesses
- textual_variants
- apparatus_entries
- text_critical_discussions

### Retrieval

- retrieval_units
- embeddings
- retrieval_aliases
- search_logs

### Research workspace

- projects
- user_annotations
- translation_proposals
- rules
- rule_versions
- saved_queries
- analysis_runs
- evidence_packets

## 47. Supabase security model

Use Row Level Security on:

- private source metadata;
- private retrieval units;
- user research projects;
- user annotations;
- saved translations;
- private source assets.

Never expose a service-role key to the browser.

Vector search must respect the same permissions as ordinary document access.

Separate:

- public/open evidence;
- licensed shared evidence;
- private user evidence.

## 48. Backup model

Database backup and object backup are separate concerns.

Maintain:

- PostgreSQL backup;
- object-storage backup;
- source Drive provenance;
- GitHub repository history.

A database restore alone must not be assumed to restore storage objects.

## 49. Caching

Safe caches:

- open corpus query results;
- public bibliographic metadata;
- rights-permitted translation API responses within provider rules.

Sensitive caches:

- restricted textbook excerpts;
- private user notes;
- private research evidence packets.

Every cache entry should carry:

- source version;
- rights scope;
- user scope;
- expiry;
- content hash.

Do not cache restricted source text into a public CDN.

## 50. Failure modes to test

### Duplicate evidence inflation

Same book exists in two Drive folders and appears twice in retrieval.

Expected:

One scholarly work, one evidence lineage.

### Edition confusion

1999 van der Merwe retrieved and described as latest.

Expected:

Explicit old-edition warning.

### Broken PDF extraction

Joüon-Muraoka produces empty text.

Expected:

`EXTRACTION_FAILED` / alternate parser required, not "no relevant content."

### Rule separated from exception

Chunking places a grammar rule in one retrieval unit and its qualification in another.

Expected:

Structural retrieval includes the qualification.

### Lexicon sense collapse

HALOT and DCH senses are merged into one synthetic list.

Expected:

Independent sense inventories plus optional mapping.

### Commentary domination

Five commentary chunks outrank exact grammar evidence for a syntax question.

Expected:

Namespace routing prevents this.

### Theological lexicon domination

TDOT appears before HALOT/DCH for a basic lexical sense question.

Expected:

General lexica and corpus evidence first.

### Stale embedding

Source correction is made but old embedding remains active.

Expected:

Embedding invalidated until regenerated.

### Rights leak

Private/unverified PDF text appears to anonymous user.

Expected:

RLS and rights filters block retrieval before ranking.

### Translator intention hallucination

System explains why a translation was chosen without documentary evidence.

Expected:

Label as SYSTEM INFERENCE or UNKNOWN.

## 51. Initial ingestion order

Do not ingest the whole Drive at once.

### Phase A: establish pipeline

Use a small representative set:

1. Waltke-O'Connor, searchable grammar PDF;
2. Seow, noisy searchable PDF;
3. Joüon-Muraoka, failed text extraction case;
4. Kutz-Josberger, EPUB case;
5. BDB or an open/public-domain lexical source;
6. one commentary;
7. one textual-criticism source;
8. one user/course note.

This tests every major ingestion path.

### Phase B: core grammar shelf

Then process:

- Joüon-Muraoka;
- Waltke-O'Connor;
- van der Merwe;
- Andersen-Forbes;
- Arnold-Choi;
- GKC;
- Reymond.

### Phase C: lexical layer

Process only according to rights permissions.

Priority conceptually:

- HALOT;
- DCH;
- BDB;
- specialised lexical sources;
- theological lexica.

### Phase D: textual criticism

- BHS/BHQ support material;
- Tov;
- Brotzman-Tully;
- DSS/LXX materials.

### Phase E: book-specific commentaries

Index by biblical reference.

### Phase F: broad background library

Only after routing and quality controls work.

## 52. Recommended development rule

For the first Site Build versions, use a small, legally safe sample corpus and mocked bibliographic records.

Do not block frontend architecture on full extraction of copyrighted books.

The production ingestion pipeline can be developed independently while the web application uses the same data contracts.

## 53. Why PostgreSQL plus pgvector is sufficient initially

The research library and Hebrew Bible corpus are not large enough to justify introducing multiple search databases at the start.

PostgreSQL can provide:

- relational scholarly metadata;
- JSONB;
- recursive relationships;
- full-text search;
- `pgvector`;
- HNSW vector indexing;
- RLS;
- transactions;
- reproducible SQL queries.

A dedicated graph database or search cluster should only be added after measured limitations appear.

## 54. Final RAG principle

The application should not ask:

> "Which chunk is most similar to this question?"

It should ask:

> "What kind of scholarly question is this, which evidence classes are competent to answer it, which exact sources and sections address it, what does the primary corpus show, what contradicts the proposed answer, and what can responsibly be concluded from that evidence?"

That distinction is the core of the research architecture.
