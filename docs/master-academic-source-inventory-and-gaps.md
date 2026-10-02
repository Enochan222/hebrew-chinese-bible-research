# Master Academic Source Inventory and Gap Audit

Status: **ACTIVE SOURCE-INVENTORY DOCUMENT**

Purpose: define what the consolidated research library currently contains, what is duplicated, what remains outside the consolidated folder, and how the source library should be regrouped before production ingestion.

This document intentionally records bibliographic titles and source roles, not private Google Drive URLs.

## 1. Main finding

The new consolidated folder is useful, but it is **not yet a complete master research library**.

At present it is heavily concentrated in:

- Biblical Hebrew grammar;
- syntax;
- introductory grammars;
- general lexica;
- theological lexica;
- etymological reference.

It currently omits several evidence lanes that the application architecture already requires:

- textual criticism;
- BHS / BHQ apparatus and Masorah;
- Dead Sea Scrolls / Judean Desert evidence;
- Hebrew language history / diachrony;
- passage-specific commentaries;
- exegesis methodology;
- rhetoric / literary method;
- concordances and LXX finding aids;
- archaeology / background;
- Chinese Bible translation studies and translator documentation;
- current journal articles, book chapters, dissertations and dataset publications.

Therefore the consolidated folder should become one **master library root with evidence-lane subfolders**, not one flat folder.

## 2. Recommended master folder structure

```text
Hebrew-Chinese-Bible-Research-Library/
  00_INBOX_UNCLASSIFIED/
  01_PRIMARY_TEXT_AND_EDITIONS/
    MT_WLC_OSHB/
    BHS/
    BHQ/
    ANCIENT_VERSIONS_LXX/
  02_REFERENCE_GRAMMARS/
  03_PEDAGOGICAL_GRAMMARS/
  04_MORPHOLOGY_PHONOLOGY/
  05_CORPUS_LINGUISTICS_SYNTAX_DISCOURSE/
  06_GENERAL_LEXICA/
  07_THEOLOGICAL_LEXICA/
  08_ETYMOLOGY_DIACHRONY/
  09_TEXTUAL_CRITICISM_METHOD/
  10_DSS_JUDEAN_DESERT/
  11_COMMENTARIES/
    GENESIS/
    RUTH/
    OTHER_BOOKS/
  12_EXEGESIS_METHOD/
  13_RHETORIC_LITERARY_METHOD/
  14_ARCHAEOLOGY_BACKGROUND/
  15_CONCORDANCES_FINDING_AIDS/
  16_CHINESE_BIBLE_TRANSLATION/
    TRANSLATION_HISTORY/
    TRANSLATOR_PREFACES/
    PUBLISHER_PRINCIPLES/
    TRANSLATION_STUDIES/
    CHINESE_LINGUISTICS_STYLE/
  17_JOURNAL_ARTICLES_CHAPTERS_DISSERTATIONS/
  18_USER_COURSE_NOTES/
  19_METADATA_RIGHTS_AND_BIBLIOGRAPHY/
  99_DUPLICATES_SUPERSEDED_FILES/
```

The folder layout is a human source-library convenience only. Production retrieval namespaces remain database metadata and must not be inferred only from folder path.

## 3. Sources currently present in the new consolidated folder

### 3.1 Major / reference grammar and syntax

Present:

- Bruce K. Waltke and M. O'Connor, *An Introduction to Biblical Hebrew Syntax* — multiple copies;
- Paul Joüon and Takamitsu Muraoka, *A Grammar of Biblical Hebrew* — multiple copies;
- Gesenius / Kautzsch / Cowley, *Gesenius' Hebrew Grammar*;
- Gesenius / Davidson syntax facsimile volume;
- van der Merwe / Naudé / Kroeze, *A Biblical Hebrew Reference Grammar* (1999 first edition);
- Andersen and Forbes, *Biblical Hebrew Grammar Visualized*;
- Arnold and Choi, *A Guide to Biblical Hebrew Syntax* (2003);
- Seow, *A Grammar for Biblical Hebrew* — multiple copies;
- Putnam, *A New Grammar of Biblical Hebrew*;
- Barrick and Busenitz, *A Grammar for Biblical Hebrew*.

Assessment:

Strong base, but editions must remain explicit. The folder contains older editions for several works and must not label them simply as the current form of the work.

### 3.2 Introductory / pedagogical grammar

Present:

- Pratico / Van Pelt, basic Biblical Hebrew textbook;
- Kutz / Josberger, *Learning Biblical Hebrew Reading for Comprehension*;
- Ellis, *Learning to Read Biblical Hebrew*;
- Cherryholmes, *The Seven Binyanim*;
- Seow and other pedagogical grammars also overlap this category.

Assessment:

Useful for teaching and morphology explanation. These should not receive the same retrieval role as major reference grammars for disputed syntax.

### 3.3 General lexical resources

Present:

- HALOT, currently represented by a volume/file rather than a clearly verified complete set;
- BDB;
- Dictionary of Classical Hebrew volumes 1–8;
- Klein, *Comprehensive Etymological Dictionary of the Hebrew Language*.

Assessment:

DCH appears substantially complete in the consolidated folder. HALOT completeness requires verification before the folder can be called a complete general-lexicon collection.

### 3.4 Theological / semantic word-study works

Present:

- TLOT;
- TWOT;
- TDOT volumes 1–15 with at least some numbering gaps requiring verification.

Assessment:

Keep in a separate namespace from HALOT / DCH / BDB. Theological lexica must not be allowed to dominate basic clause-level sense decisions.

### 3.5 Encyclopaedic reference

Present:

- Anchor Bible Dictionary.

Assessment:

Useful contextual reference, not a primary Hebrew lexicon.

## 4. Duplicate / edition issues already visible in the consolidated folder

Observed duplicate or near-duplicate holdings include:

- Waltke–O'Connor: at least two files;
- Joüon–Muraoka: at least two files;
- Seow: at least two files;
- potentially multiple historical Gesenius-related files.

Required handling:

```text
Work
  -> Edition
      -> FileAsset
          -> ContentHash
```

Do not delete older editions merely because a newer one exists.

Move true duplicate file assets to a duplicate/superseded holding area only after cryptographic hashing and edition comparison.

## 5. High-priority evidence lanes missing from the consolidated folder

The following materials are present in the older Drive libraries but are absent from the new consolidated folder and should be copied or represented in the master structure if they remain relevant and legally held.

### 5.1 Textual criticism methodology

Missing examples:

- Emanuel Tov, *Textual Criticism of the Hebrew Bible* and related textual-criticism material;
- Brotzman and Tully, *Old Testament Textual Criticism: A Practical Introduction*;
- Paul D. Wegner, *A Student's Guide to Textual Criticism of the Bible*;
- Natalio Fernández Marcos, *The Septuagint in Context*;
- G. D. Martin, *Multiple Originals*.

This is a major omission because translation analysis may depend on whether the Hebrew base reading is itself textually secure.

### 5.2 BHS / Masorah resources

Missing examples:

- BHS Ruth;
- sample BHS passage extracts;
- BHS Prolegomena;
- Wonneberger, *Understanding BHS*;
- Scott / Rüger, simplified BHS guide;
- Kelley / Crawford, *The Masorah of Biblia Hebraica Stuttgartensia*;
- Weil, *Massorah Gedolah*.

### 5.3 BHQ

Missing Ruth materials include:

- BHQ Ruth text;
- critical apparatus;
- Ruth introduction;
- Masorah Parva notes;
- Masorah Magna notes;
- general introduction;
- BHQ manual;
- scholarship on BHQ / critical-edition methodology.

The future database must treat apparatus as structured textual-critical data, not ordinary RAG prose.

### 5.4 Dead Sea Scrolls / Judean Desert

Missing examples:

- García Martínez / Tigchelaar, *Dead Sea Scrolls Study Edition*;
- DJD introduction / publication material;
- Tov DSS research;
- Ulrich;
- Lim / Collins;
- related Qumran material.

### 5.5 Historical / diachronic Hebrew

Missing:

- E. Y. Kutscher, *A History of the Hebrew Language*;
- Ángel Sáenz-Badillos, *A History of the Hebrew Language*;
- Dong-Hyuk Kim, *Early Biblical Hebrew, Late Biblical Hebrew, and Linguistic Variability*.

Also verify whether the Hurvitz Late Biblical Hebrew lexicon is present elsewhere and add it if legally available.

### 5.6 Morphology-specialist material

Missing:

- Gary Rendsburg, *Ancient Hebrew Morphology*.

Additional modern morphology / phonology work may be desirable later.

### 5.7 Exegesis methodology

Missing:

- Odil Hannes Steck, *Old Testament Exegesis*;
- Douglas Stuart, *Old Testament Exegesis*;
- Robert Chisholm, *From Exegesis to Exposition*.

These belong in methodology, not grammar evidence.

### 5.8 Passage-specific commentary

Missing from consolidated folder:

Genesis:
- Victor P. Hamilton, Genesis 1–17, NICOT;
- Bill T. Arnold, *Genesis*, New Cambridge Bible Commentary;
- E. A. Speiser, *Genesis*, Anchor Bible.

Ruth:
- Jeremy Schipper, *Ruth*, Anchor Yale / Anchor Bible;
- Robert Chisholm, Judges and Ruth commentary.

Other commentary collections exist in the older Drive library and should be admitted passage-first according to relevance and rights, not copied wholesale merely because they exist.

### 5.9 Concordances / finding aids

Missing:

- Strong's concordance as a legacy finding aid;
- Hatch and Redpath, Septuagint concordance.

Strong's must remain low-authority for difficult translation decisions.

### 5.10 Rhetorical / literary method

Missing:

- Roland Meynet, *Rhetorical Analysis*;
- course materials should remain separated from published scholarship.

### 5.11 Archaeology / historical background

The older library contains archaeology/background material, including NEAEHL-related holdings.

Only material relevant to a research question should be indexed into the academic system.

### 5.12 Additional grammar / lexical holdings not yet consolidated

A direct comparison with the older specialist folders shows additional omissions inside the same broad categories.

Grammar / morphology resources present in the older library but not currently visible in the consolidated folder include:

- John H. Sailhamer, *A Grammar of Biblical Hebrew*;
- Eric D. Reymond, *Intermediate Biblical Hebrew Grammar: A Student's Guide to Phonology and Morphology*;
- *Invitation to Biblical Hebrew: A Beginning Grammar*.

Lexical / diachronic resources present in the older library but not currently visible in the consolidated folder include:

- HALOT CD-ROM edition / digital resource;
- Avi Hurvitz, Leeor Gottlieb and Aaron Hornkohl/Mastey-associated *A Concise Lexicon of Late Biblical Hebrew* holding;
- a concise Hebrew-English / English-Hebrew lexicon.

The consolidated folder currently shows only `HALOT I.pdf`; therefore HALOT completeness must be treated as **unverified**, not complete.

The consolidated TDOT sequence also requires a volume-level completeness check before it is registered as a complete set. File presence must be verified by volume identity rather than inferred from the series name.

## 6. Missing from all current Drive-focused collections or insufficiently represented

These are not necessarily missing files in the user's possession; they are research-domain gaps.

### 6.1 Chinese Bible translation scholarship

This is the largest domain gap relative to the product's title and purpose.

Needed source classes:

- histories of Chinese Bible translation;
- formal translation prefaces;
- Bible society / publisher translation principles;
- translator notes and revision documentation;
- studies of Chinese biblical style and syntax;
- Hebrew-to-Chinese translation studies;
- modern translation theory relevant to biblical translation;
- historical Chinese Bible versions and their editorial histories.

Without this lane, the system can become very strong at Hebrew source analysis while remaining comparatively weak at evaluating target-language Chinese decisions.

### 6.2 Specialist Biblical Hebrew research

Comparatively underrepresented:

- prepositions and particles;
- valency;
- discourse and information structure;
- word order;
- tense / aspect / modality;
- construction grammar;
- corpus linguistics;
- pragmatics;
- recent specialist syntax.

Reference grammars should not be treated as the end of the scholarly literature.

### 6.3 Current scholarly publication types

The academic knowledge model must support:

- journal article;
- book chapter;
- edited-volume contribution;
- conference paper;
- dissertation / thesis;
- critical review;
- dataset publication;
- digital scholarly resource.

Bibliographic metadata should support DOI, journal, ISSN, volume, issue, pages, editors, series, publication status, correction/retraction status where relevant.

## 7. Recommended immediate regrouping action

Do **not** place all files into one flat folder.

Use one master folder with the evidence-lane subfolders listed in section 2.

Immediate priority for consolidation:

1. keep the current grammar and lexicon files, but add the missing Sailhamer, Reymond, relevant pedagogical grammar, HALOT digital/remaining holdings and Hurvitz diachronic lexicon only after edition/rights verification;
2. move verified duplicates into a duplicate holding folder rather than deleting them;
3. add Textual Criticism, BHS and BHQ;
4. add History of Hebrew Language;
5. add key commentaries for the passages/books the app will initially support;
6. add Hebrew Exegesis methodology;
7. add DSS/Judean Desert material;
8. add concordances/LXX finding aids;
9. create an empty dedicated Chinese Bible Translation folder now, even before sources are acquired;
10. create a Current Research folder for articles/chapters/dissertations rather than treating the Drive bookshelf as epistemically complete.

## 8. Database principle

Physical folder grouping must not determine academic authority.

A file can sit under a convenient Drive folder while its database metadata independently records:

- source type;
- scholarly domain;
- intended audience;
- level;
- methodology;
- work;
- edition;
- publication status;
- rights;
- extraction quality;
- retrieval namespace;
- citation eligibility;
- current/superseded status.

## 9. Current completeness judgement

The consolidated folder is currently:

- **strong** for general Biblical Hebrew grammar;
- **strong** for lexica / theological lexica;
- **moderate** for pedagogy;
- **weak / absent** for textual criticism;
- **absent** for BHS/BHQ as structured research evidence;
- **weak / absent** for DSS;
- **weak / absent** for diachronic Hebrew;
- **absent** for passage commentaries;
- **absent** for exegesis method;
- **absent** for rhetoric/literary method;
- **absent** for Chinese translation studies;
- **absent** for current journal/article-level specialist scholarship.

Therefore it should not yet be treated as the complete source corpus for the application.
