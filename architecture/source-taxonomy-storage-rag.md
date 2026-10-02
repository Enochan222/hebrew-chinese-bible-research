# Academic Source Taxonomy, Storage Model, and RAG Strategy

## Status

Research architecture document for the Hebrew–Chinese Bible Research project.

This document classifies the academic materials currently identified in the user's Google Drive and defines how they should and should not be used in a research-grade translation system. It also proposes the storage and retrieval architecture that should follow from that classification.

The classification is functional rather than confessional or prestige-based. There is no single global ranking of sources. A source may be primary for one research question and peripheral for another.

---

# 1. Governing principle

The application must not treat every academic book as equally relevant to every question.

A question such as:

> What is the syntactic function of לְ in this clause?

should not retrieve, with equal weight:

- a reference grammar,
- a theological wordbook,
- an Old Testament introduction,
- a preaching commentary,
- a historical-critical methodology book.

They are all academic books, but they answer different kinds of questions.

Therefore the knowledge base must classify each source by:

- source family
- academic function
- linguistic domain
- chronological scope
- methodological orientation
- intended audience
- edition
- applicability to translation decisions
- extraction quality
- rights status

The RAG system must route by research problem before it retrieves evidence.

---

# 2. Current Drive corpus: high-level map

The Drive corpus relevant to this project currently includes at least the following source families.

## A. Critical Hebrew texts and textual witnesses

Examples identified:

- Biblia Hebraica Stuttgartensia (BHS)
- Biblia Hebraica Quinta (BHQ), including General Introduction, Ruth text, Ruth critical apparatus, Masorah notes
- BHS Reader's Edition material
- Dead Sea Scrolls Study Edition, García Martínez and Tigchelaar
- Discoveries in the Judaean Desert related material
- Hatch–Redpath Septuagint concordance
- BHS / Masorah manuals and guides

Academic role:

These are not ordinary prose reference books. They belong to the textual evidence layer.

They should be used to establish:

- what text is being read
- textual variants
- manuscript evidence
- Masoretic information
- textual-critical apparatus data
- relations among witnesses

They should not be treated as generic vector-search books.

BHQ is especially important because it is the successor to BHS and its design explicitly focuses on documenting and evaluating textual variants relevant to translation and interpretation. The user's Drive contains BHQ material for Ruth and general materials, not a complete BHQ of the whole Hebrew Bible.

## B. Major reference grammars and advanced syntax

### Paul Joüon and Takamitsu Muraoka, A Grammar of Biblical Hebrew, 2006

Position:

Core comprehensive reference grammar.

The 2006 second revised edition is a major scientific reference grammar covering orthography, phonology, morphology, and syntax. It is exceptionally detailed and is especially valuable for source-native grammatical categories, rare constructions, qualifications, and examples.

Research use:

- morphology
- syntactic categories
- particles and prepositions
- verbal system
- clause-level phenomena
- detailed edge cases

Important methodological caution:

Independent scholarly discussion has noted that the grammar is predominantly synchronic and focused on the Tiberian Biblical Hebrew system. It should therefore not be used by itself to resolve diachronic, dialectal, or sociolinguistic questions.

RAG status:

CORE_REFERENCE_GRAMMAR

Default priority:

Very high for morphology and syntax.

Do not normalize its terminology silently into another grammar's taxonomy.

Extraction status:

The copies tested through the current Google Drive text-extraction path returned no usable text. This means it requires an alternate ingestion pipeline, likely raw-file extraction and, if necessary, layout-aware or image-based extraction.

### Bruce K. Waltke and Michael O'Connor, An Introduction to Biblical Hebrew Syntax, 1990

Position:

Advanced post-first-year teaching grammar and reference syntax.

The publisher describes it as a work integrating modern linguistic study of Hebrew with extensive teaching experience, using more than 3,500 Biblical Hebrew examples.

Research use:

- syntax
- verbal syntax
- noun syntax
- particles
- traditional-to-modern grammatical categories
- large example inventory

Strength:

Detailed explanation and strong exegetical usefulness.

Limitation:

Published in 1990. It remains important, but it should not be assumed to represent the final state of contemporary Hebrew linguistics.

RAG status:

CORE_REFERENCE_GRAMMAR

Default priority:

Very high for syntax; always retain section-level citation and examples.

Extraction status:

Excellent searchable text layer in the Drive copy.

### Christo H. J. van der Merwe, Jackie A. Naudé, and Jan H. Kroeze, A Biblical Hebrew Reference Grammar, 1999

Position:

Intermediate reference grammar oriented to translation and exegesis.

Important edition issue:

The user's Drive currently contains the 1999 edition. The substantially revised second edition appeared in 2017 under Christo H. van der Merwe and Jacobus A. Naudé. The current publisher describes the second edition as integrating morphology, syntax, semantics, pragmatics, word classes, and an extensive treatment of word order with contemporary linguistic approaches.

Implication:

The 1999 edition remains academically useful, but the system must never identify it simply as "the BHRG" without edition metadata.

RAG status:

CORE_REFERENCE_GRAMMAR_WITH_EDITION_WARNING

Default priority:

High for translation-oriented syntax and linguistic description.

Extraction status:

The Drive copy returned no usable text through the current text-extraction path and requires an alternate pipeline.

Source gap:

If the project later obtains the 2017 second edition legally, it should be ingested as a separate edition, not as an overwrite.

### Francis I. Andersen and A. Dean Forbes, Biblical Hebrew Grammar Visualized, 2012

Position:

Specialized corpus-linguistic and syntactic analysis.

The work explicitly approaches Biblical Hebrew from corpus linguistics and uses a fully analyzed Hebrew Bible corpus to discuss clause structures, grammatical functions, semantic roles, constituent order, verb corpora, verbless clauses, and supra-clausal structures.

Research use:

- clause structure
- corpus patterns
- grammatical functions
- semantic roles
- constituent order
- corpus-based structural generalizations

Major strength:

Uniquely relevant to this application's planned structural corpus search.

Major caution:

Its analyses are model-dependent. Andersen–Forbes parses and categories must be stored as an annotation system, not as the neutral or universal parse of Biblical Hebrew.

RAG status:

SPECIALIST_CORPUS_GRAMMAR

Default priority:

Very high for structural and corpus questions, lower for questions that require a different theoretical framework.

Extraction status:

Good searchable text layer.

### Bill T. Arnold and John H. Choi, A Guide to Biblical Hebrew Syntax, 2003

Position:

Intermediate-level syntax reference and teaching guide.

Cambridge describes it as an intermediate reference grammar designed to move readers from elementary morphology into syntactical relations involving words, phrases, clauses, and sentences.

Research use:

- concise syntax orientation
- nouns
- verbs
- particles
- phrase relations
- clause and sentence relations

Strength:

Clear, compact, exegetically oriented.

Limitation:

It is intentionally abridged relative to larger reference grammars.

Edition issue:

The user's Drive has the 2003 first edition. Cambridge published a second edition in 2018 incorporating newer research and a more explicitly linguistic treatment.

RAG status:

INTERMEDIATE_SYNTAX_REFERENCE

Default priority:

High as corroborating evidence and rapid orientation, but normally not the only source for a disputed advanced construction.

Extraction status:

Good searchable text layer.

### Gesenius–Kautzsch–Cowley, Gesenius' Hebrew Grammar, 1910

Position:

Classic historical reference grammar.

Research use:

- legacy grammatical categories
- detailed morphology
- syntax
- historical grammar
- old scholarly terminology
- large example inventory

Strength:

Extremely important for the history and traditional description of Biblical Hebrew grammar.

Limitation:

Its descriptive framework and terminology predate modern linguistics. It must not automatically overrule later linguistic descriptions.

RAG status:

CLASSIC_REFERENCE_GRAMMAR

Default priority:

High as historical/reference corroboration; lower as sole authority for a contested modern linguistic question.

Extraction status:

Good searchable text layer.

---

# 3. Intermediate, pedagogical, and specialist grammars

These books are useful, but they should not be put in the same retrieval tier as the major reference grammars for contested translation problems.

## C. L. Seow, A Grammar for Biblical Hebrew, revised edition, 1995

Position:

Introductory/pedagogical grammar with strong use of biblical text and attention to accents and reference tools.

Use:

- morphology
- basic syntax
- pedagogical explanation
- parsing explanations
- introductory accents

RAG role:

PEDAGOGICAL_GRAMMAR

Good for generating clear explanations after a claim has been established from stronger sources.

## Gary D. Pratico and Miles V. Van Pelt, Basics of Biblical Hebrew Grammar

Drive edition:

2001 first edition.

Current publisher edition:

Third edition.

Position:

Widely used introductory textbook.

Use:

- beginner morphology
- paradigms
- standard parsing
- simple grammatical explanation

RAG role:

PEDAGOGICAL_GRAMMAR

Do not use as the primary basis for disputed advanced syntax.

## John H. Sailhamer, A Grammar of Biblical Hebrew, 2000

The book's own introduction explicitly says it covers what first-year students need and omits many later details.

RAG role:

INTRODUCTORY_GRAMMAR

Useful for beginner explanations; low priority for advanced translation decisions.

## Frederic C. Putnam, A New Grammar of Biblical Hebrew, 2010

Position:

Pedagogical grammar with an explicitly discourse-based orientation.

Use:

- alternative conceptualization of the verbal system
- discourse-sensitive teaching
- narrative and poetry orientation
- Masora introduction

RAG role:

DISCOURSE_PEDAGOGICAL_GRAMMAR

Important as an alternative interpretive framework, but not a replacement for reference grammars.

## Eric D. Reymond, Intermediate Biblical Hebrew Grammar, 2018

Position:

Specialized intermediate/advanced grammar of phonology and morphology.

The SBL description explicitly emphasizes the history of Hebrew phonology and morphology and extensive paradigmatic comparison.

RAG role:

SPECIALIST_PHONOLOGY_MORPHOLOGY

Default priority:

Very high when the problem is phonological or morphological.

Low when the problem is syntax or discourse.

## Rendsburg, Ancient Hebrew Morphology

Position:

Specialist morphology / historical-linguistic resource.

RAG role:

SPECIALIST_DIACHRONIC_MORPHOLOGY

Use only when the question activates historical morphology, dialect, or diachrony.

## Barrick & Busenitz, Ellis, Cherryholmes and similar introductory material

RAG role:

SUPPLEMENTARY_PEDAGOGICAL

Use for explanation, paradigms, and teaching support, not for high-stakes adjudication among competing syntactic analyses.

---

# 4. Lexica: separate linguistic lexica from theological word studies

This distinction is mandatory.

## HALOT: Koehler–Baumgartner–Stamm, The Hebrew and Aramaic Lexicon of the Old Testament

Position:

Core modern Hebrew/Aramaic lexicon.

Brill describes HALOT as a standard modern English dictionary of Biblical Hebrew, informed by Semitic linguistics, difficult lexical problems, textual traditions, and related ancient sources.

Research use:

- lexical sense
- semantic range
- attestation
- cognates where relevant
- textual variants
- difficult words

RAG status:

CORE_LEXICON

Default priority:

Very high for lexical analysis.

Important caution:

A lexicon proposes senses and translations; it does not by itself establish the syntax of a construction.

Extraction status:

Excellent text layer in the Drive copy.

Copyright:

The Drive copy contains explicit restrictive copyright language. It must remain private and access-controlled unless licensing is obtained.

## Dictionary of Classical Hebrew (DCH)

Position:

Broad Classical Hebrew corpus lexicon.

The publisher highlights:
- Biblical Hebrew plus Ben Sira, Dead Sea Scrolls, and inscriptions
- exhaustive occurrence coverage
- syntagmatic analysis
- occurrence statistics

Research use:

- lexical meaning
- collocation
- subject/object patterns
- broader Classical Hebrew comparison
- distributional evidence

RAG status:

CORE_CLASSICAL_HEBREW_LEXICON

Default priority:

Very high when lexical distribution or syntagmatic behavior matters.

Storage implication:

DCH data should be represented by headword, sense, corpus, collocation/syntagmatic relation, not only arbitrary chunks.

## BDB, Brown–Driver–Briggs

Position:

Classic early twentieth-century Hebrew lexicon.

Research use:

- traditional root structure
- older lexical classifications
- exhaustive biblical usage
- history of scholarship
- comparison with later lexica

RAG status:

CLASSIC_LEXICON

Default priority:

High as a historical and corroborating lexicon.

It should not be the only modern lexical authority when HALOT or DCH are available.

Extraction status:

Good searchable text layer.

## TLOT, Theological Lexicon of the Old Testament

Position:

Selective theological lexicon with linguistic and statistical attention.

Its design is not simply a gloss dictionary. It gives discussions of derivation, occurrence statistics, general meaning, theological usage, and later reception for selected important terms.

RAG status:

THEOLOGICAL_LEXICON

Use:

- theological semantic development
- research history
- important lexical concepts
- statistical and semantic discussion

Do not use it as the first source for ordinary word meaning when HALOT/DCH are available.

Extraction status:

Good searchable text layer.

## TDOT, Theological Dictionary of the Old Testament

Position:

Large theological dictionary with extensive articles, bibliography, historical and theological development.

RAG status:

THEOLOGICAL_DICTIONARY

Use after core lexical evidence, especially for:
- conceptual history
- theological significance
- cultural background
- research bibliography

## TWOT, Theological Wordbook of the Old Testament

Position:

Practical theological word-study resource.

The book's own introduction and publisher positioning explicitly state that it is less exhaustive and designed for pastors and serious non-specialists who may not have the background for detailed technical linguistic study.

RAG status:

PASTORAL_THEOLOGICAL_WORDBOOK

Default priority:

Low for academic lexical adjudication.

Useful for:
- theological reception
- evangelical interpretive history
- accessible summaries
- bibliography discovery

It must never outrank HALOT, DCH, corpus data, or major grammars in a research-grade translation decision.

## Klein, Comprehensive Etymological Dictionary

RAG status:

ETYMOLOGICAL_REFERENCE

Use only when etymology or later Hebrew history is explicitly relevant.

Etymology must not be treated as current contextual meaning.

## Concise Lexicon of Late Biblical Hebrew

RAG status:

SPECIALIST_LATE_BIBLICAL_HEBREW_LEXICON

Use when a diachronic or Late Biblical Hebrew question is activated.

---

# 5. Textual criticism and textual history

## Emanuel Tov, Textual Criticism of the Hebrew Bible

Drive edition:

Second revised edition, 2001.

Position:

Core reference work in Hebrew Bible textual criticism.

The Hebrew University describes the current fourth edition (2022) as an indispensable authoritative resource and explicitly notes the previous 2012 third edition.

RAG status:

CORE_TEXTUAL_CRITICISM_REFERENCE

Default priority:

Very high for:
- textual witnesses
- scribal transmission
- textual variants
- relations among MT, Qumran, LXX and other witnesses
- methodology of textual criticism

Edition warning:

The user's copy is 2001. It remains important but should be marked as an older edition.

Source gap:

If legally acquired later, the 2022 fourth edition should be ingested separately.

Extraction status:

Good searchable text layer.

## Brotzman & Tully, Old Testament Textual Criticism, 2016

Position:

Practical student/intermediate introduction.

The publisher specifically presents it as a clear practical introduction, updated for developments such as BHQ, with a textual commentary on Ruth.

RAG status:

PRACTICAL_TEXTUAL_CRITICISM_GUIDE

Use:

- explaining method
- BHS/BHQ apparatus orientation
- step-by-step text-critical workflow

Not a replacement for Tov or the primary witnesses.

Drive format:

EPUB. The current connector does not expose readable text directly. Use native EPUB parsing rather than OCR.

## Paul Wegner, A Student's Guide to Textual Criticism of the Bible, 2006

Position:

Introductory guide spanning textual criticism more broadly.

RAG status:

INTRODUCTORY_TEXTUAL_CRITICISM

Useful for explanation and historical overview.

## BHS/BHQ manuals, Scott, Wonneberger, Masorah guides

RAG status:

EDITION_USAGE_MANUAL

Route only when:
- decoding sigla
- using Masorah
- understanding apparatus conventions
- explaining edition mechanics

Do not treat these as evidence for a specific reading unless they are discussing that specific reading.

## Dead Sea Scrolls material

Includes:
- García Martínez and Tigchelaar
- DJD-related materials
- Tov
- Ulrich
- Qumran-specific scholarship

RAG status:

TEXTUAL_WITNESS_AND_SECOND_TEMPLE_HEBREW

Use when:
- a relevant textual witness exists
- a linguistic feature needs comparison with Qumran Hebrew
- textual history is part of the translation problem

---

# 6. History of Hebrew and diachronic linguistics

## Eduard Y. Kutscher, A History of the Hebrew Language, 1982

Position:

Historical Hebrew linguistics.

Use:
- phonology
- morphology
- stages of Hebrew
- historical change
- comparative Semitic background

RAG status:

CORE_DIACHRONIC_REFERENCE

Not a default source for ordinary synchronic verse translation.

## Angel Sáenz-Badillos, A History of the Hebrew Language

Position:

Broad history of Hebrew from Semitic origins through Biblical, post-biblical, medieval, and modern Hebrew.

Cambridge explicitly positions it as a comprehensive historical description.

RAG status:

CORE_LANGUAGE_HISTORY

Use when historical stage, post-exilic Hebrew, diachrony, or comparative language history matters.

## Dong-Hyuk Kim, Early Biblical Hebrew, Late Biblical Hebrew, and Linguistic Variability, 2012

Position:

Specialist monograph in historical sociolinguistics and linguistic dating.

The book explicitly addresses the debate between strong Early/Late Biblical Hebrew chronological models and the counter-view that many differences may reflect style, using variationist sociolinguistics.

RAG status:

SPECIALIST_DIACHRONIC_DEBATE

Important rule:

The app must not make simplistic claims such as "this form proves the passage is late" without retrieving competing positions.

---

# 7. Exegesis methodology and discourse/rhetoric

## Odil Hannes Steck, Old Testament Exegesis: A Guide to the Methodology

Position:

Advanced methodological guide rooted in German-speaking historical-critical practice.

Covers:
- literary criticism
- transmission history
- redaction history
- form criticism
- tradition history
- historical setting

RAG status:

EXEGESIS_METHODOLOGY

Use for research-method planning.

Do not use it as grammatical evidence for a Hebrew construction unless the relevant passage explicitly discusses grammar.

## Douglas Stuart, Old Testament Exegesis

Position:

Step-by-step exegesis handbook for students and pastors.

RAG status:

PRACTICAL_EXEGESIS_WORKFLOW

Useful for:
- planning research sequence
- paper workflow
- bibliographic method

Not a grammar authority.

## Robert Chisholm, From Exegesis to Exposition

Position:

Bridge between Biblical Hebrew analysis, exegesis, and exposition.

RAG status:

APPLIED_HEBREW_EXEGESIS

Useful for:
- demonstrating how Hebrew observations affect interpretation
- translation/exegetical workflow

But individual grammatical claims should still be cross-checked against reference grammars and corpus evidence.

## Roland Meynet, Rhetorical Analysis

Position:

Methodological work on biblical rhetoric, parallelism, compositional figures and rhetorical structures.

RAG status:

RHETORICAL_STRUCTURE_METHOD

Use when:
- parallelism
- chiasm
- compositional structure
- macro-syntactic literary organization
are relevant.

Do not invoke it automatically for lexical or morphological questions.

## Habel, Barton, historical/literary criticism materials

RAG status:

BIBLICAL_CRITICISM_METHODOLOGY

Use when the user asks questions of:
- method
- literary history
- criticism
- canon
- historical reconstruction

Normally exclude from first-pass translation decisions.

---

# 8. Commentaries

Commentaries must be indexed by series, author, biblical book, passage, methodological orientation, and technical level.

They are verse-specific scholarly interpretations, not neutral grammar databases.

## Anchor / Anchor Yale Bible

Position:

High-level academic translation and exegesis, explicitly including new translations, alternative translations, competing theories, annotations, and historical research.

RAG status:

TECHNICAL_ACADEMIC_COMMENTARY

High value for verse-specific translation problems.

## Word Biblical Commentary

Position:

Technical commentary designed for trained students and scholars, with author translation, textual analysis, grammar, structure, historical setting and interpretation.

RAG status:

TECHNICAL_COMMENTARY

High value for:
- translation decisions
- text-critical discussion
- grammar in context
- alternative renderings

## NICOT

Position:

Scholarly commentary combining original-language translation and technical exegesis with theological exposition.

RAG status:

SCHOLARLY_EXEGETICAL_COMMENTARY

High value verse-specifically, but its theological framing should remain distinct from grammatical evidence.

## New Cambridge Bible Commentary

Position:

Academically rigorous but deliberately accessible, drawing on contemporary methods without requiring advanced original-language competence.

RAG status:

ACADEMIC_ACCESSIBLE_COMMENTARY

Useful secondary commentary layer, normally below the most technical commentary for fine grammatical adjudication.

## IVP Bible Background Commentary

RAG status:

HISTORICAL_CULTURAL_BACKGROUND

Use for cultural and ancient-world context, not as direct Hebrew grammatical authority.

## Interpretation / preaching-oriented commentaries and theological treatments

RAG status:

THEOLOGICAL_HOMILETICAL_COMMENTARY

Useful for theological reception and interpretation.

Low priority for determining the grammar of a Hebrew construction.

---

# 9. Broad introductions, theology, archaeology, historical studies

The first Drive contains many important books that are academically valuable but not direct translation references, including:

- John J. Collins, Introduction to the Hebrew Bible
- John Barton works on biblical criticism and interpretation
- Jon D. Levenson
- Brueggemann
- Old Testament theology
- Genesis / creation studies
- archaeology
- comparative Ancient Near Eastern studies
- broader theological works

These should form contextual namespaces, not default translation RAG.

Suggested categories:

- HEBREW_BIBLE_INTRODUCTION
- HISTORICAL_CRITICISM
- BIBLICAL_THEOLOGY
- ANCIENT_NEAR_EAST
- ARCHAEOLOGY
- RECEPTION_HISTORY
- JEWISH_INTERPRETATION
- CREATION_STUDIES
- CANON_AND_INTERPRETATION

Use them only when the research question activates those domains.

---

# 10. User-created notes and course material

Examples identified:

- Preliminary Interpretation.docx
- Hebrew III lessons
- Psalm notes
- Genesis research notes
- Practico & Van Pelt summaries
- course lecture PDFs
- personal/reference Word documents

These are not automatically scholarly sources.

Store them as:

USER_NOTE
COURSE_NOTE
USER_SUMMARY
LECTURE_MATERIAL

Rules:

- Never attribute their content to a published scholar unless the note contains a verified citation.
- Never let user summaries override the source book.
- Preserve links back to the original source where available.
- A user note may become a research hypothesis or translation rule, but it must remain labelled as such.

---

# 11. Retrieval-priority matrix

There should be no single "authority score".

Use domain-specific applicability.

## Morphology

First lane:
- corpus morphology
- Joüon–Muraoka
- Reymond
- GKC
- Waltke–O'Connor

Second lane:
- Seow
- Pratico–Van Pelt
- Sailhamer

Specialist lane:
- Rendsburg / diachronic morphology

## Syntax / particles / prepositions

First lane:
- Joüon–Muraoka
- Waltke–O'Connor
- van der Merwe et al. 1999, with edition warning
- corpus evidence

Second lane:
- Arnold–Choi
- Andersen–Forbes where its model applies
- GKC

Discourse alternatives:
- Putnam
- Andersen–Forbes
- van der Merwe

## Lexical semantics

First lane:
- corpus distribution
- HALOT
- DCH

Second lane:
- BDB
- TLOT

Third / theological lane:
- TDOT
- TWOT

Etymological questions:
- Klein
- comparative/historical sources

## Textual variants

First lane:
- BHQ / BHS apparatus
- extant witnesses
- Tov
- relevant DSS / LXX evidence

Second lane:
- Brotzman–Tully
- edition manuals

Commentaries:
- only after the primary textual evidence is assembled

## Diachrony / dating / dialect

First lane:
- Kutscher
- Sáenz-Badillos
- specialist articles/monographs
- Dong-Hyuk Kim
- Rendsburg where relevant

Never infer dating from one lexical or morphological feature without competing evidence.

## Verse-specific translation

Evidence assembly order:
1. Hebrew text and morphology
2. syntax
3. corpus parallels
4. lexica
5. major grammars
6. textual criticism if relevant
7. technical commentaries
8. other commentaries
9. Chinese translations
10. documented translator notes
11. user's proposed translation
12. AI synthesis and counter-analysis

---

# 12. Storage architecture

The Drive should remain a source repository, not the runtime RAG database.

Recommended architecture:

Google Drive
-> ingestion pipeline
-> immutable source snapshot
-> structured document store
-> scholarly knowledge layer
-> search indexes
-> RAG router

## 12.1 Original file store

Use private object storage for imported source snapshots.

For every source file store:

- source_file_id
- original_drive_file_id
- original_drive_url
- source_document_id
- edition_id
- filename
- MIME type
- byte size
- SHA-256 checksum
- import timestamp
- extraction pipeline version
- rights status
- access scope

Never depend on the live Google Drive path as the permanent identifier.

A file may be renamed or moved in Drive.

## 12.2 Bibliographic layer

Tables/entities:

source_work
source_edition
source_file
source_author
source_publisher
source_series
source_category
source_rights

Important:

Work and edition must be separate.

Examples:
- Arnold–Choi 2003 != Arnold–Choi 2018
- van der Merwe et al. 1999 != van der Merwe–Naudé 2017
- Tov 2001 != Tov 2012 != Tov 2022

## 12.3 Document structural layer

Do not store books as arbitrary chunks only.

Minimum hierarchy:

Document
-> front matter
-> part
-> chapter
-> section
-> subsection
-> page
-> block / paragraph
-> footnote

Fields should preserve:

- printed page number
- PDF page index
- section number
- section heading
- paragraph order
- bounding box where obtainable
- language
- script
- original extracted text
- normalized search text
- extraction confidence
- review status

## 12.4 Scholarly knowledge layer

Extract structured units from the source without deleting the source text.

Suggested scholarly unit types:

- DEFINITION
- GRAMMATICAL_RULE
- DESCRIPTION
- CLAIM
- QUALIFICATION
- EXCEPTION
- COUNTEREXAMPLE
- BIBLICAL_EXAMPLE
- CROSS_REFERENCE
- LEXICAL_SENSE
- ETYMOLOGICAL_CLAIM
- TEXTUAL_VARIANT
- TRANSLATION_PROPOSAL
- COMMENTARY_INTERPRETATION
- METHODOLOGICAL_RULE

Each unit must point to an exact source span.

Required provenance:

- work
- edition
- section
- printed page
- PDF page
- source block IDs
- extraction method
- extraction confidence
- human review status

## 12.5 Biblical-reference links

Bible references must be extracted as first-class relations.

Example:

scholarly_unit
-> CITES_BIBLE_PASSAGE
-> canonical_passage_id

This enables:

"show every grammar discussion in the library that cites 1 Samuel 16:7"

without semantic-vector search.

## 12.6 Hebrew linguistic links

Where possible, source units should link to:

- lemma
- surface form
- morpheme
- grammatical category
- syntax concept
- semantic concept

Hebrew must be stored both as source form and normalized search forms.

Do not use embedding similarity to identify exact Hebrew lexemes.

## 12.7 Concept graph

Use relational graph tables in PostgreSQL first.

Concept examples:

PREPOSITION_LAMED
REFERENCE
RESPECT
NORM
INSTRUMENT
PERCEPTION_VERB
BODY_PART
DUAL_NUMBER
WAYYIQTOL

Relations:

- source_calls_this
- broader_than
- narrower_than
- overlaps_with
- contrasts_with
- example_of
- disputes
- qualifies

Critical rule:

Keep source-native terminology and canonical cross-source concepts separate.

Example:

Source A term
-> mapped_to
Canonical concept X

Source B term
-> partially_overlaps
Canonical concept X

Never rewrite both sources into the same label and discard the originals.

---

# 13. Rights and public deployment

Many Drive files are clearly copyrighted academic books, and several filenames indicate copies sourced from Z-Library.

Because the project is assumed to become public, default to the most restrictive safe access model until rights are verified.

Suggested fields:

rights_status
license
copyright_holder
public_full_text
public_snippet
model_context_allowed
persistent_storage_allowed
redistribution_allowed
commercial_use_allowed
max_quote_length
notes

Important architecture rule:

The user's private source copy may be available to a private ingestion system, but that does not automatically make the source text redistributable to public users.

The public application should normally expose:

- bibliographic citation
- page / section reference
- short permitted snippet where allowed
- paraphrased scholarly claim with citation

not entire book pages or long extracted passages.

---

# 14. Ingestion pipelines by file type and quality

The current Drive has heterogeneous source quality.

Observed examples:

Good searchable text:
- Waltke–O'Connor
- GKC
- Arnold–Choi
- Andersen–Forbes
- Seow
- Sailhamer
- Putnam
- Reymond
- Pratico–Van Pelt
- HALOT
- BDB
- TLOT
- TWOT
- Tov 2001
- Wegner
- Steck
- Chisholm
- Meynet
- Kutscher
- Sáenz-Badillos

Failed current text extraction:
- Joüon–Muraoka copies tested
- van der Merwe et al. 1999

Native EPUB:
- Brotzman & Tully 2016
- some commentaries

Other:
- CHM files
- DOCX notes
- XLSX
- images
- scanned materials

Required pipelines:

### Pipeline A: native searchable PDF

- extract text with page boundaries
- retain reading order
- detect headings
- detect footnotes
- detect Hebrew spans
- detect Bible references
- validate page count

### Pipeline B: malformed or inaccessible PDF text layer

- inspect raw PDF objects
- try alternate PDF extractor
- run layout-aware extraction
- use image/vision fallback only where necessary
- validate Hebrew against page image

### Pipeline C: scanned PDF

- page image extraction
- OCR / vision
- language/script-aware cleanup
- human review on Hebrew-heavy pages

### Pipeline D: EPUB

- parse package / spine
- preserve XHTML hierarchy
- map digital locations to chapters and sections
- do not OCR

### Pipeline E: CHM

- extract HTML contents and TOC
- preserve native hierarchy

### Pipeline F: DOCX / user notes

- parse headings and paragraphs
- mark as user/course material
- do not promote claims to scholarly-source status

---

# 15. RAG architecture

Do not build one global vector index and call it "the RAG".

Use a routed hybrid retrieval system.

## Stage 1: research-question decomposition

Classify the question into one or more domains:

- morphology
- syntax
- lexical semantics
- textual criticism
- diachrony
- discourse/pragmatics
- rhetoric
- commentary
- historical/cultural background
- translation comparison

The classifier does not answer the question.

It builds a retrieval plan.

## Stage 2: deterministic evidence retrieval

Before vector search:

- current Hebrew passage
- morphology
- syntax annotation
- exact lemma
- exact Bible-reference index
- corpus query
- text-critical witness data

## Stage 3: source-routed academic retrieval

Retrieve only from relevant source families.

Example for a disputed preposition:

Lane 1:
major reference grammars

Lane 2:
corpus grammar / discourse grammar

Lane 3:
lexica if lexical sense matters

Lane 4:
technical commentary on the verse

Do not retrieve theology books unless the user asks a theological question.

## Stage 4: hybrid search inside each lane

Use:

1. exact section / reference lookup
2. Hebrew lemma lookup
3. Bible-reference lookup
4. keyword / PostgreSQL full-text retrieval
5. concept-graph expansion
6. vector semantic search
7. reranking

Vector search is last-mile discovery, not the first source of evidence.

## Stage 5: evidence balancing

Prevent one large or highly chunked book from dominating retrieval.

Use per-source or per-family caps.

For example:

- maximum N top units from one grammar before reranking
- ensure at least two independent reference grammars where possible
- preserve disagreement
- prefer a precise relevant section over many vague semantically similar chunks

## Stage 6: claim reconstruction

For each retrieved unit, return:

- exact scholarly claim
- source type
- author
- edition
- section
- page
- source text span
- biblical examples cited
- qualifications
- confidence in extraction

## Stage 7: contradiction / disagreement pass

Before synthesis, search for:

- alternate terminology
- competing classification
- explicit exceptions
- counterexamples
- later correction
- different editions

## Stage 8: AI synthesis

Only now may the model write an analysis.

The model must distinguish:

- SOURCE TEXT
- CORPUS FACT
- SCHOLARLY CLAIM
- COMMENTARY INTERPRETATION
- USER HYPOTHESIS
- AI INFERENCE

---

# 16. Chunking policy

Avoid a fixed "800-token chunk" strategy.

## Grammar

Primary retrieval unit:
section / subsection

Secondary:
paragraph

Attach:
- preceding heading
- section path
- local examples
- footnotes

## Lexicon

Primary retrieval unit:
headword + numbered sense / subentry

Never cut one lexical sense across arbitrary chunks.

Attach:
- lemma
- root
- POS
- sense number
- examples
- cognates
- bibliography

## Commentary

Primary unit:
verse / verse range / pericope subsection

Attach:
- commentator translation
- textual note
- grammatical note
- exposition

Separate these if the commentary itself has distinct sections.

## Textual criticism

Do not rely on vector chunks for the apparatus.

Model the variant structurally:

passage
reading
witness
support
editorial comment
source

## Methodology books

Use section-level retrieval.

## User notes

Use paragraph / heading retrieval but assign USER_NOTE status.

---

# 17. Search and embedding strategy

Use PostgreSQL as the central research database.

Recommended capabilities:

- relational data
- JSONB for source-specific structures
- full-text indexes
- trigram indexes where needed
- pgvector for semantic retrieval
- graph-like relation tables

A separate vector database is not necessary at this scale.

## Embeddings

Store:

- embedding model
- embedding version
- dimensions
- source content hash
- chunk / scholarly-unit ID
- generation timestamp

Never mix vectors generated by incompatible embedding models in one search space without explicit handling.

## Multilingual issue

The user may query in Cantonese / Traditional Chinese while the sources are largely English with Hebrew examples.

Therefore retrieval must support multilingual semantic discovery.

However:

Hebrew lexical identity, morphology and syntactic structure must be handled by exact normalized identifiers and corpus data, not by embedding similarity.

---

# 18. Known failure modes to test

## Source duplication

The Drive contains duplicate copies of some books and research files.

Solution:

deduplicate by content hash before indexing.

Do not let duplicates double the retrieval weight of one scholarly position.

## Edition collision

Never merge editions under one source ID.

## PDF-page collision

Printed page != PDF page.

Store both.

## Footnote detachment

Do not lose which paragraph a footnote belongs to.

## Hebrew OCR corruption

Common errors:
- similar letters
- missing niqqud
- reversed ordering
- lost combining marks

For Hebrew-heavy scholarly evidence, validate against the page image.

## Section-boundary failure

Never separate a grammatical rule from the qualification or exception immediately following it.

## Taxonomy collapse

Do not map Joüon–Muraoka, Waltke–O'Connor, GKC and van der Merwe terminology into one canonical label without preserving the source-specific term and relation type.

## Commentary dominance

Technical commentary text is often more verbose and semantically similar to natural-language questions than grammar entries. Without source routing, it can swamp the grammar evidence.

## Theological-wordbook dominance

TWOT or TDOT may rank highly for words with theological importance. They must not displace core lexical evidence for ordinary semantic questions.

## User-note contamination

Personal notes and course summaries must not be presented as published scholarly claims.

## Stale-edition invisibility

The system must tell the user when the library contains an older edition and a newer edition is known to exist.

## Extraction failure interpreted as no evidence

An empty extracted document means "ingestion failed", not "the author says nothing about this topic".

---

# 19. Recommended initial source set for the first production-grade RAG

Do not ingest the whole Drive at once.

Start with a controlled academically coherent set.

## Grammar core

1. Joüon–Muraoka 2006
2. Waltke–O'Connor 1990
3. van der Merwe–Naudé–Kroeze 1999, clearly edition-labelled
4. Andersen–Forbes 2012
5. Arnold–Choi 2003
6. GKC 1910
7. Reymond 2018

## Lexical core

1. HALOT
2. DCH where available
3. BDB
4. TLOT

Keep TDOT and TWOT as separate secondary theological lanes.

## Text-critical core

1. available BHQ material
2. BHS
3. Tov 2001
4. Brotzman–Tully 2016
5. relevant DSS material

## Exegetical method

1. Steck
2. Stuart
3. Chisholm
4. Meynet

## Commentary pilot

Use a small number of technical commentaries on books actually used for testing:
- Anchor / Anchor Yale
- WBC
- NICOT
- NCBC as a secondary layer

This is enough to validate the architecture before indexing the entire library.

---

# 20. Current edition gaps worth tracking

Do not silently replace the user's sources with web material. Web research is being used only to understand positioning and edition status.

Known relevant gaps:

- van der Merwe et al.: Drive 1999; substantially revised 2017 second edition exists
- Arnold–Choi: Drive 2003; second edition published 2018
- Tov: Drive includes 2001 second edition; 2012 third and 2022 fourth editions exist
- Pratico–Van Pelt: Drive includes early edition; third edition exists

These should be represented in the source registry as:

newer_edition_known = true

but the newer text must not be treated as part of the user's academic corpus until it is legally acquired and ingested.

---

# 21. Practical conclusion

The correct architecture is not:

PDFs
-> chunks
-> embeddings
-> chatbot

It is:

Academic source registry
-> edition-aware ingestion
-> structured document hierarchy
-> source-native scholarly units
-> biblical-reference and Hebrew-concept links
-> domain-specific retrieval lanes
-> deterministic corpus evidence
-> hybrid retrieval
-> disagreement/counterevidence pass
-> citation-grounded synthesis

The Drive library is strong enough to support a serious research application, but only if its different types of scholarship remain differentiated.

The application should be conservative by design:

- no source-type collapse
- no edition collapse
- no unsupported translator-intention claims
- no grammar claims from theological wordbooks
- no lexical claims from commentary alone
- no historical dating from isolated forms
- no "absence of retrieved text" interpreted as absence of scholarly discussion

The system's academic value will come primarily from provenance, routing, reproducibility, and disagreement handling, not from the size of the vector index.
