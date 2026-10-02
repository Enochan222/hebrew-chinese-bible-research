# Academic Source Taxonomy and Scholarly Positioning

## Status

This document defines the scholarly taxonomy and question-to-source routing principles for the Hebrew-Chinese Bible Research project.

It is a **scholarly taxonomy**, not the machine-readable retrieval-enum source. Canonical implementation vocabularies live in `contracts/v1.1/vocabulary.json`. Current physical holdings and missing evidence lanes are tracked separately in `docs/master-academic-source-inventory-and-gaps.md`.

This taxonomy began from the user's Google Drive holdings but the production academic knowledge base must not be limited to those holdings.

It is intentionally written before the storage and RAG architecture. Retrieval architecture must follow scholarly function. It must not impose one undifferentiated search model on sources that answer fundamentally different questions.

## 1. Core principle

There is no single universal ranking in which one book is always "better" than another.

A source has evidentiary weight only relative to the question being asked.

For example:

- a reference grammar is highly relevant to a syntactic question but not sufficient for a textual-critical decision;
- HALOT or DCH is highly relevant to lexical semantics but not a substitute for clause-level syntax;
- TDOT or TLOT may be valuable for semantic and theological history but should not override corpus usage or a general lexicon when establishing a basic lexical sense;
- a commentary may provide an important passage-specific interpretation but should not be treated as the primary authority for a general grammatical rule;
- an introductory grammar may explain a phenomenon very clearly but should not be given the same research weight as a major reference grammar when the issue is disputed;
- BHS or BHQ is primary textual-critical evidence, not prose RAG content of the same kind as a textbook.

Accordingly, the system must route questions by scholarly function.

## 2. Library-level assessment

### Consolidated master Drive library

The current primary private source library is the reorganized consolidated Drive folder.

It now contains five major evidence areas:

1. Hebrew language
2. Lexica and concordances
3. Texts and textual criticism
4. Commentaries and interpretation
5. Background and reference

Substantive holdings now include:

- major reference grammars;
- pedagogical grammars;
- diachronic Hebrew;
- BDB / DCH / HALOT holdings;
- theological lexica;
- Strong's and Hatch-Redpath concordances;
- BHS / Masorah support;
- BHQ Ruth materials;
- Tov / Brotzman-Tully / Wegner / LXX methodology;
- DSS/Judaean Desert sources;
- Genesis 1-11 commentaries and studies;
- exegesis methodology;
- rhetoric;
- archaeology / ANE background;
- Anchor Bible Dictionary.

This consolidated folder should now be treated as the primary **private acquisition library** for the first Research Compiler.

It must not be treated as:

- the production database;
- the complete universe of scholarship;
- evidence of redistribution/indexing/model-context rights;
- one undifferentiated RAG namespace.

The current inventory is maintained in:

- `docs/master-academic-source-inventory-and-gaps.md`

### Older Drive libraries

The older broad biblical-studies and Hebrew-specialist Drives remain useful for provenance, duplicate/edition comparison, course/user notes and material not yet deliberately moved into the consolidated library.

They should no longer define the primary folder taxonomy.

If the same work exists in both an older Drive and the consolidated master library, that is one scholarly work/edition lineage unless bibliographic comparison proves otherwise.

### Current major collection gaps

The consolidated library is now strong in traditional/core Hebrew Bible research tools.

The largest remaining collection gaps are:

- Chinese Bible translation history and documentation;
- target-language Chinese biblical style/linguistics;
- Hebrew-to-Chinese translation studies;
- recent specialist articles/chapters/dissertations;
- whole-Bible commentary coverage;
- whole-Bible BHQ coverage;
- machine-readable LXX corpus/annotation data.

These gaps must be represented as coverage metadata. The system must never equate "not in the current library" with "not present in scholarship."

## 3. Category A: major reference grammar and syntax sources

These are the main prose sources for difficult grammatical and syntactic analysis. They should be retrieved together with deterministic corpus evidence.

### A1. Joüon and Muraoka, A Grammar of Biblical Hebrew

Position:

- major comprehensive reference grammar;
- especially valuable for detailed traditional morphosyntactic categorisation and extensive examples;
- appropriate for advanced grammatical analysis and comparison with other reference grammars.

Use for:

- morphology;
- prepositions and particles;
- nominal and verbal syntax;
- clause-level grammatical categories;
- fine-grained traditional grammatical distinctions;
- cross-reference to biblical examples.

Cautions:

- the framework remains substantially traditional in several areas;
- it should not be treated as a complete representation of contemporary discourse linguistics or corpus linguistics;
- the source's own categories must be preserved instead of silently mapped into another grammar's taxonomy.

Edition issue:

The Drive contains a 2006-labelled copy and another unverified copy. Later corrected printings of the second edition exist. Edition identity must be verified at ingestion.

Retrieval priority:

High for grammar questions.

### A2. Waltke and O'Connor, An Introduction to Biblical Hebrew Syntax

Position:

- major reference work on Biblical Hebrew syntax despite the word "Introduction" in the title;
- combines extensive description with engagement with modern linguistic ideas available at the time of publication;
- particularly influential for verb syntax and syntactic categories.

Use for:

- verbal syntax;
- noun and particle syntax;
- syntactic categorisation;
- translation implications of grammatical construction;
- comparison with Joüon-Muraoka and later reference grammars.

Cautions:

- published in 1990, so it should not be treated as the endpoint of later linguistic research;
- some categories and explanations are disputed or have been reformulated in later work.

Retrieval priority:

High for grammar and syntax questions.

### A3. van der Merwe, Naudé and Kroeze, A Biblical Hebrew Reference Grammar

Drive edition:

1999 first edition.

Position:

- reference grammar designed for exegetes and translators;
- especially important because it explicitly integrates morphology, syntax, semantics, pragmatics and discourse-sensitive categories;
- later editions give substantial attention to word order and modern linguistic frameworks.

Important edition warning:

The Drive has the 1999 edition. A fully revised second edition appeared in 2017. For a research application, the 1999 text should be marked as an older edition rather than silently presented as current.

Recommendation:

Acquire or license the 2017 second edition if this source is to be a top-tier current reference.

Retrieval priority:

High, but edition-aware.

### A4. Arnold and Choi, A Guide to Biblical Hebrew Syntax

Drive edition:

2003 first edition.

Position:

- intermediate-level reference syntax;
- focused on helping readers move from morphology and syntax to meaning;
- covers nouns, verbs, particles and larger clause/sentence relations;
- generally shorter and easier to navigate than the large reference grammars.

Use for:

- rapid syntax lookup;
- cross-checking a category;
- accessible explanation;
- connecting formal syntax with exegetical significance.

Cautions:

- should not replace a larger reference grammar when a point is disputed;
- the Drive edition is the first edition, while a later second edition exists.

Retrieval priority:

Medium-high for syntax, especially as a corroborating reference.

## 4. Category B: corpus-linguistic and structural grammar

### B1. Andersen and Forbes, Biblical Hebrew Grammar Visualized

Position:

This should not be classified as simply another conventional grammar.

It is a corpus-linguistic and structural description associated with the Andersen-Forbes analysed Hebrew corpus. It explicitly models:

- phrase and clause structure;
- grammatical functions;
- semantic roles;
- constituent relationships;
- constituent order;
- verb corpora;
- supra-clausal structures.

Use for:

- corpus-based structural comparison;
- clause architecture;
- grammatical functions;
- semantic roles;
- word order;
- comparison of verb corpora;
- structural analogues.

Cautions:

- it uses its own analytical framework;
- its categories should not be silently equated with BHSA, MACULA, Joüon-Muraoka or Waltke-O'Connor categories;
- when the application presents an Andersen-Forbes analysis, the annotation framework must be named explicitly.

Retrieval priority:

Very high for structural/corpus questions, but framework-specific.

## 5. Category C: historical/classical reference grammars

### C1. Gesenius-Kautzsch-Cowley, Gesenius' Hebrew Grammar

Position:

- historically foundational and still useful;
- exceptionally rich in examples and traditional categories;
- important for understanding the history of Hebrew grammatical description.

Use for:

- traditional grammatical categories;
- locating classical discussions;
- historical comparison of analyses;
- additional biblical examples;
- checking terminology used in older scholarship.

Cautions:

- its linguistic framework is historical and in places outdated by contemporary linguistic analysis;
- it should not automatically outrank modern reference grammars on a contested linguistic question.

Retrieval priority:

Medium for current analysis, high when historical grammar or older scholarly terminology matters.

### C2. Davidson, Hebrew Syntax

The combined Gorgias PDF in Drive Group C contains a facsimile of Davidson's *Hebrew Syntax* together with GKC.

Position:

- historical syntax reference;
- useful for older descriptions and examples.

Retrieval priority:

Supplementary / historical.

## 6. Category D: pedagogical and reading grammars

These books are valuable but should not be treated as equal research authorities merely because they explain a rule clearly.

### D1. Seow, A Grammar for Biblical Hebrew

Position:

- pedagogical grammar;
- comprehensive for learners;
- gives early exposure to biblical text and pays attention to accents and practical reading.

Use for:

- beginner/intermediate explanation;
- paradigms;
- morphology;
- pedagogical reformulation of complex concepts.

Research weighting:

Supplementary for disputed translation questions.

### D2. Pratico and Van Pelt, Basics of Biblical Hebrew Grammar

Position:

- widely used beginning textbook;
- designed for structured language learning.

Use for:

- foundational morphology;
- terminology;
- paradigms;
- accessible explanation.

Caution:

A later third edition exists. The Drive files appear older and include duplicates.

Research weighting:

Pedagogical, not primary evidence for a contested advanced syntactic claim.

### D3. Kutz and Josberger, Learning Biblical Hebrew: Reading for Comprehension

Position:

- introductory grammar designed around reading comprehension, extensive reading and long-term retention.

Use for:

- pedagogy;
- reading strategies;
- beginner/intermediate explanation.

Research weighting:

Pedagogical.

### D4. Putnam, A New Grammar of Biblical Hebrew

Position:

- pedagogically oriented grammar with discourse-sensitive organisation and attention to prose, poetry and Masoretic features.

Use for:

- pedagogical explanation;
- discourse-aware reading;
- cross-checking broader patterns.

Research weighting:

Medium-low for disputed technical questions unless the relevant section presents a distinctive argument.

### D5. Sailhamer, Barrick-Busenitz, Ellis and other learning grammars

Position:

Primarily instructional.

Use:

- explanatory support;
- morphology;
- paradigms;
- teaching language.

Research weighting:

Low to medium depending on the exact issue.

### D6. Fuller, Invitation to Biblical Hebrew

Position:

Beginning grammar with a strong rules-based instructional orientation.

Research weighting:

Pedagogical.

## 7. Category E: morphology and phonology specialists

### E1. Eric D. Reymond, Intermediate Biblical Hebrew Grammar

Position:

Specialist intermediate/advanced resource focusing particularly on:

- history of Hebrew;
- phonology;
- morphology;
- inflectional patterns;
- relative frequency of phenomena.

Use for:

- phonological explanation;
- morphological formation;
- unusual inflections;
- historical explanation of forms.

Do not use as:

A primary source for broad clause syntax or translation semantics unless the issue is directly morphological.

Retrieval priority:

High for morphology/phonology, low for unrelated syntax.

### E2. Gary Rendsburg, Ancient Hebrew Morphology

Position:

Specialised morphology / historical-linguistic resource.

Retrieval priority:

Question-specific.

### E3. Cherryholmes, The Seven Binyanim

Position:

Narrow pedagogical/special-topic source.

Retrieval priority:

Low except for its specific subject.

## 8. Category F: general scholarly lexica

Lexical retrieval must distinguish dictionary type. "Dictionary" does not mean all sources answer the same question.

### F1. HALOT

Position:

- major modern Hebrew and Aramaic lexicon for the Old Testament;
- strong philological and comparative-Semitic orientation;
- important for lexical senses, difficult words and lexical bibliography.

Use for:

- lemma lookup;
- lexical senses;
- philological notes;
- cognate comparison;
- textual and semantic problems.

Cautions:

- a lexicon proposes and organises senses; it does not independently prove that a particular syntactic analysis applies in a verse;
- the Drive PDF contains an explicit restrictive copyright notice regarding reproduction and storage in retrieval systems.

Retrieval priority:

Very high for lexical questions, subject to rights restrictions.

### F2. Dictionary of Classical Hebrew, original eight-volume edition

Drive holdings:

All eight original volumes appear present.

Position:

- corpus-oriented dictionary of Classical Hebrew extending beyond the biblical corpus;
- includes Biblical Hebrew, Ben Sira, Dead Sea Scrolls and inscriptions;
- valuable for lexical distribution, collocation and syntagmatic information.

Use for:

- lexical range;
- wider Classical Hebrew evidence;
- collocations;
- syntagmatic patterns;
- comparison with extra-biblical Hebrew.

Edition note:

A revised DCH project exists. The Drive holds the original eight-volume DCH, not the newer revised dictionary.

Retrieval priority:

Very high for lexical/collocational research.

### F3. Brown-Driver-Briggs

Position:

- classical major Hebrew-English lexicon;
- exceptionally influential and still useful;
- older than HALOT and modern corpus-based lexicography.

Use for:

- historical lexical analysis;
- traditional sense classification;
- cross-checking older scholarship;
- public-domain/open alternatives may be available depending on edition.

Caution:

Do not treat an older BDB sense taxonomy as current consensus solely because it is widely cited.

Retrieval priority:

Medium-high, generally after or alongside HALOT/DCH for current research.

## 9. Category G: theological and semantic dictionaries

These must be separated from general lexical dictionaries.

### G1. TDOT, Theological Dictionary of the Old Testament

Drive holdings:

Fifteen volumes are present.

Position:

- large theological word-study reference;
- substantial research history, semantic discussion and theological interpretation.

Use for:

- history of interpretation;
- semantic fields;
- theological development;
- extended word studies.

Do not use as:

The sole basis for deciding the basic lexical sense of a word in a specific clause.

Retrieval priority:

Secondary after corpus and general lexica when the question is lexical; high when the question is explicitly theological-semantic.

### G2. TLOT, Theological Lexicon of the Old Testament

Position:

- root-oriented theological/semantic lexicon;
- useful for history of research and semantic-theological synthesis.

Use:

- semantic development;
- word-field discussion;
- theological implications.

Retrieval priority:

Secondary to HALOT/DCH for base lexical sense.

### G3. TWOT

Position:

- theological wordbook written to be usable by serious students and pastors;
- Strong's-keyed and intentionally less technically linguistic than the major scholarly lexica.

Use:

- accessible theological summary;
- supplementary word-study context.

Research weighting:

Lower than HALOT, DCH, BDB, TLOT and TDOT for rigorous lexical decisions.

### G4. Anchor Bible Dictionary

Position:

Encyclopaedic biblical studies reference rather than a Hebrew lexicon.

Use:

- people;
- places;
- concepts;
- historical context;
- archaeology;
- major scholarly topics.

Do not route routine Hebrew lemma questions here first.

### G5. Klein, Comprehensive Etymological Dictionary

Position:

Etymological dictionary.

Use:

- diachronic and etymological comparison.

Caution:

Etymology is not automatically the meaning of a word in a biblical context.

## 10. Category H: diachronic and historical Hebrew linguistics

### H1. E. Y. Kutscher, A History of the Hebrew Language

Position:

Broad historical Hebrew language reference.

Use for:

- development of Hebrew;
- historical language stages;
- Semitic context;
- linguistic background.

Not a default source for:

ordinary clause-level translation decisions.

### H2. Sáenz-Badillos, A History of the Hebrew Language

Position:

Broad history of Hebrew from Semitic origins through biblical and later Hebrew.

Use:

- historical linguistic context;
- post-exilic and later Hebrew;
- broader history of the language.

### H3. Dong-Hyuk Kim, Early Biblical Hebrew, Late Biblical Hebrew, and Linguistic Variability

Position:

Specialist sociolinguistic intervention in a contested debate over linguistic dating of biblical texts.

Use:

- linguistic dating;
- EBH/LBH variation;
- sociolinguistic method;
- evaluating chronological claims based on linguistic features.

Caution:

The application must show that linguistic dating is contested. It must not convert one model into settled chronology.

### H4. Hurvitz et al., A Concise Lexicon of Late Biblical Hebrew

Position:

Specialised diachronic lexicon for Late Biblical Hebrew, not a general Hebrew dictionary.

Use:

- LBH features;
- linguistic dating evidence;
- diachronic lexical analysis.

## 11. Category I: primary textual-critical editions and apparatus

### I1. Biblia Hebraica Stuttgartensia

Position:

Scholarly critical edition based on Codex Leningradensis with critical apparatus.

Use:

- base-text comparison;
- apparatus;
- Masoretic notes;
- textual-critical starting point.

Do not process like:

A normal prose textbook.

Data model should be passage- and apparatus-oriented.

### I2. Biblia Hebraica Quinta

Drive holdings:

Substantial Ruth materials, including text, critical apparatus, introductions and Masorah notes.

Position:

Successor critical edition project to BHS with a different and richer apparatus strategy.

Use:

- primary textual-critical evidence;
- passage-specific variant analysis;
- Masorah.

Retrieval priority:

Very high when the selected biblical passage is covered by a Drive BHQ fascicle.

### I3. Guides to BHS and Masorah

Examples:

- Wonneberger;
- Scott and Rüger;
- Kelley / Crawford;
- Weil, Massorah Gedolah;
- BHS accent notes.

Position:

Technical aids for interpreting the critical edition and Masoretic information.

Use only when relevant to apparatus, Masorah or accentuation.

## 12. Category J: textual criticism methodology and witnesses

### J1. Emanuel Tov, Textual Criticism of the Hebrew Bible and related Tov materials

Position:

Advanced scholarly methodology and reference for Hebrew Bible textual criticism.

Use for:

- textual witnesses;
- transmission;
- evaluation of variants;
- relation of MT, DSS, ancient versions and other textual traditions;
- methodological issues.

Retrieval priority:

High for textual-critical questions.

### J2. Brotzman and Tully, Old Testament Textual Criticism, second edition

Position:

Practical and pedagogically accessible introduction, updated for BHS/BHQ and current textual-critical discussion.

Use for:

- procedure;
- explaining apparatus;
- teaching textual-critical reasoning;
- Ruth-specific textual commentary.

Retrieval priority:

High for workflow/explanation, below primary apparatus and advanced specialised literature for disputed technical conclusions.

### J3. Wegner

Position:

Student-oriented textual-criticism guide.

Retrieval priority:

Pedagogical / supplementary.

### J4. Fernández Marcos, The Septuagint in Context

Position:

Specialist introduction to the Greek versions and Septuagint context.

Use:

- LXX history;
- Greek version evidence;
- translation history.

### J5. Martin, Multiple Originals

Position:

Specialist scholarly argument within textual criticism.

Use:

Question-specific and explicitly attributed, not as neutral methodological consensus.

## 13. Category K: Dead Sea Scrolls and Judean Desert material

### K1. García Martínez and Tigchelaar, Dead Sea Scrolls Study Edition

Position:

Reference edition and translation of relevant non-biblical Qumran texts, with bibliographic value for DSS study.

Use:

- Qumran parallels;
- Second Temple Hebrew/Aramaic context;
- manuscript and textual research.

Caution:

It is not simply an extension of the Biblical Hebrew corpus.

### K2. DJD material

Position:

Primary publication series and scholarly reference for Judean Desert manuscripts.

Use:

Manuscript-specific textual work.

### K3. Ulrich, Tov, Lim/Collins and Qumran studies

Position:

Specialist secondary scholarship on DSS, textual development and research history.

Retrieval:

Only when a query involves manuscript evidence, textual pluriformity, DSS language or Second Temple context.

## 14. Category L: exegesis methodology

### L1. Odil Hannes Steck, Old Testament Exegesis

Position:

Methodological guide with strong historical-exegetical orientation.

Use:

- research workflow;
- methodological sequencing;
- historical-critical procedures.

Do not use as:

Direct proof that a Hebrew construction has a specific meaning.

### L2. Douglas Stuart, Old Testament Exegesis

Position:

Practical handbook for students and pastors, focused on performing exegesis and using research tools.

Use:

- workflow;
- research checklist;
- teaching exegesis.

### L3. Robert Chisholm, From Exegesis to Exposition

Position:

Bridge from Hebrew exegesis to exposition.

Use:

- exegetical workflow;
- communicating results;
- relation between language analysis and exposition.

These books should live in a methodology namespace, not in the same retrieval pool as grammar rules.

## 15. Category M: rhetorical, literary and historical methods

### M1. Roland Meynet, Rhetorical Analysis

Position:

Methodological resource for biblical rhetoric and rhetorical composition.

Use:

- parallelism;
- composition;
- rhetorical units;
- structural literary analysis.

Do not use as:

A default source for morphology or lexical meaning.

### M2. Literary Criticism / Habel / course materials

Position:

Literary and historical-critical method.

Use:

When the research question involves source, composition, literary structure or historical setting.

### M3. Archaeology and historical background

Position:

Contextual evidence.

Use:

- geography;
- material culture;
- historical setting;
- ancient Near Eastern context.

Do not use as:

Grammar evidence.

## 16. Category N: passage-specific commentaries

Commentaries are high-value secondary evidence but are inherently author- and series-specific.

The system must index commentary by biblical reference and commentary subsection, not as a generic semantic vector pool.

### N1. Anchor / Anchor Yale Bible

Drive examples:

- Speiser, Genesis;
- Schipper, Ruth;
- other volumes may be present.

Position:

Typically detailed historical-critical academic commentary with substantial attention to philology, textual criticism, composition and scholarly debate. Methodology varies by author and period.

Use:

- passage-specific philological arguments;
- textual criticism;
- translation notes;
- composition/history;
- scholarly alternatives.

Caution:

Older volumes may be historically important but superseded in particular areas by later scholarship.

### N2. Word Biblical Commentary

Drive examples include:

- Wenham, Genesis;
- Hartley, Leviticus;
- Clines, Job;
- multiple NT volumes.

Position:

Technical or semi-technical commentary series, generally with attention to original languages, textual issues, form/structure and detailed notes.

Use:

Passage-specific exegesis and translation discussion.

### N3. NICOT

Drive example:

Victor Hamilton, Genesis 1-17.

Position:

Evangelical scholarly commentary series combining technical exegesis with theological exposition.

Use:

- passage exegesis;
- lexical/syntactic discussion;
- theological interpretation.

Caution:

Its theological commitments and the author's individual method should remain visible metadata.

### N4. New Cambridge Bible Commentary

Drive example:

Bill T. Arnold, Genesis.

Position:

Scholarly commentary intended to make current academic discussion accessible.

Use:

Passage-level secondary analysis.

### N5. IVP Bible Background Commentary and similar background works

Position:

Background reference, not a linguistic commentary.

Use:

Ancient Near Eastern, cultural and historical context.

## 17. Category O: Hebrew Bible introductions and theology

Examples in Drive Group A include:

- John J. Collins, Introduction to the Hebrew Bible;
- Old Testament theology volumes;
- Pentateuch research collections;
- Chinese-language Hebrew Bible studies.

Position:

Broad orientation, literary history, theology and research context.

Use:

- book-level context;
- history of scholarship;
- theological synthesis;
- composition and historical setting.

Default translation-analysis weight:

Low unless the question explicitly concerns those domains.

## 18. Category P: course notes, user notes and internal reference files

Examples include:

- Hebrew III lesson documents;
- Psalm assignment documents;
- preliminary interpretation files;
- English-Chinese terminology lists;
- accent notes;
- course outlines.

These are not equivalent to published peer-reviewed or scholarly reference sources.

They must be stored separately as:

- USER NOTE;
- COURSE MATERIAL;
- INTERNAL TERMINOLOGY;
- RESEARCH DRAFT.

They may be useful to personalise workflow, but they must never be cited as an academic authority unless their authorship and status justify that use.

## 19. Category Q: concordances and finding aids

### Strong's

Position:

Concordance / identifier system and basic lookup aid.

Use:

- navigation;
- legacy identifiers;
- basic cross-reference.

Do not use as:

A primary scholarly basis for a difficult translation decision.

### Hatch and Redpath

Position:

Septuagint concordance.

Use:

Greek/LXX lexical occurrence lookup and cross-reference.

## 20. Duplicate and edition management

The Drive libraries contain multiple copies of the same work.

Observed examples include:

- Waltke-O'Connor in more than one Drive;
- Joüon-Muraoka in more than one Drive;
- Seow in more than one Drive;
- multiple HALOT files;
- multiple Pratico-Van Pelt files;
- multiple editions or copies of textual-criticism textbooks.

This creates a serious retrieval bug if untreated.

If duplicate copies are independently embedded, an answer may appear to have multiple supporting sources when it really has repeated copies of one work.

Required deduplication levels:

1. Work identity
   - title;
   - author;
   - canonical bibliographic identifier.

2. Edition identity
   - edition;
   - publication year;
   - publisher;
   - ISBN where available.

3. File identity
   - cryptographic checksum;
   - file size;
   - source location.

4. Content identity
   - normalized section or paragraph hash.

The UI should cite the work/edition, not the number of duplicate Drive files.

## 21. Edition obsolescence flags

The system must not imply that every Drive copy is the latest edition.

Known examples:

- van der Merwe et al.: Drive has 1999 first edition; fully revised second edition is 2017;
- Arnold-Choi: Drive has 2003 first edition; later second edition exists;
- Joüon-Muraoka: Drive copies require edition verification; corrected later reprints exist;
- Pratico-Van Pelt: Drive copies appear older than the 2019 third edition;
- DCH: Drive contains original eight-volume DCH, while a revised project exists;
- GKC and Davidson: intentionally historical sources rather than current linguistic descriptions.

Recommended metadata:

- `edition_status = current | superseded | historical | unknown`
- `newer_edition_known = true/false`
- `replacement_recommended = true/false`

Older editions should not be deleted. They remain valuable for history of scholarship and reproducibility.

## 22. Question-to-source routing matrix

### Morphological parsing

Primary:
- corpus morphology;
- Reymond;
- major reference grammars.

Secondary:
- Seow;
- Pratico-Van Pelt;
- other pedagogical grammars.

### Clause syntax / preposition function

Primary:
- deterministic corpus evidence;
- Joüon-Muraoka;
- Waltke-O'Connor;
- van der Merwe / Naudé;
- Andersen-Forbes where the structural framework is relevant.

Secondary:
- Arnold-Choi;
- GKC for traditional/historical comparison.

Do not route first to:
- TWOT;
- theological dictionaries;
- general commentaries.

### Lexical semantics

Primary:
- actual corpus usage;
- HALOT;
- DCH;
- BDB as an important classical comparator.

Secondary:
- TLOT;
- TDOT;
- specialised lexica.

Low-priority:
- TWOT;
- Strong's.

### Diachronic / linguistic dating

Primary:
- Kutscher;
- Sáenz-Badillos;
- Hurvitz specialised material;
- Dong-Hyuk Kim;
- relevant corpus distribution.

Must show:
- scholarly disagreement;
- genre and register effects;
- uncertainty of dating conclusions.

### Textual criticism

Primary:
- BHS/BHQ apparatus;
- manuscript witness data;
- Tov;
- relevant DSS / LXX evidence.

Secondary:
- Brotzman-Tully;
- Wegner;
- Fernández Marcos.

### Passage translation

Minimum evidence lanes:

1. Hebrew primary text;
2. morphology;
3. syntax;
4. deterministic corpus parallels and counterexamples;
5. major grammars;
6. general lexica;
7. textual criticism if variants affect the reading;
8. passage commentaries;
9. Chinese translation witnesses and notes;
10. user translation;
11. AI synthesis with uncertainty.

No single source lane should be allowed to masquerade as the whole argument.

### Rhetorical / literary structure

Primary:
- Hebrew text;
- Masoretic accents where relevant;
- rhetorical/literary methodology;
- passage commentaries.

Grammar is supportive but not sufficient.

## 23. Source diversity rule

For a disputed translation question, retrieval should not return five passages from one book and present them as five independent scholarly confirmations.

The system should distinguish:

- independent works;
- multiple editions of the same work;
- one author repeated in different publications;
- a commentary citing a grammar;
- a secondary source summarising another scholar.

Where feasible, the synthesis layer should report source diversity.

## 24. Copyright and public-product constraint

Many Drive files are copyrighted academic books, and a number of filenames indicate unofficial download provenance.

The future public application must not assume that possession of a PDF grants permission to:

- redistribute it;
- expose full text;
- build a public full-text database;
- create a persistent retrieval index;
- provide substantial extracts;
- commercialise the content.

The HALOT PDF sampled from the Drive is especially explicit in restricting reproduction and storage in retrieval systems without permission.

Therefore every source must receive a rights status before production ingestion.

Recommended statuses:

- VERIFIED_OPEN;
- LICENSED_FOR_INDEXING;
- LICENSED_PRIVATE_ONLY;
- USER_SUPPLIED_RESEARCH_ONLY;
- METADATA_ONLY;
- RIGHTS_UNVERIFIED;
- DO_NOT_INDEX.

Until rights are verified, default to restrictive treatment.

## 25. Extractability findings

Current sampling shows heterogeneous file quality.

Good text extraction observed:
- Waltke-O'Connor;
- GKC;
- Arnold-Choi;
- HALOT;
- TLOT;
- the Gorgias GKC/Davidson facsimile;
- Seow, although formatting is noisy.

Current Drive extraction returned no text for:
- Joüon-Muraoka copies tested;
- van der Merwe 1999 copy;
- Kutz-Josberger EPUB through the Drive text endpoint.

This means ingestibility is not the same as scholarly quality.

An academically important source must not be demoted merely because its PDF has a poor text layer. Extraction quality and scholarly role are separate metadata fields.

## 26. Gaps revealed by the audit

The existing library is strong in:

- large reference grammars;
- basic/intermediate grammars;
- lexica;
- theological word studies;
- textual criticism;
- selected commentaries.

It is comparatively less complete in some areas important for a research-grade translation engine:

- recent specialist work on Biblical Hebrew discourse;
- dedicated monographs on individual prepositions and particles;
- newer specialised work on tense, aspect and modality;
- contemporary corpus-driven studies tied directly to open machine-readable datasets;
- explicit translation-studies literature on Hebrew-to-Chinese translation;
- documented translation principles and translator notes for the Chinese versions.

These gaps do not prevent development. They mean the system must distinguish "not retrieved from the current library" from "scholarship does not exist."

## 27. Final classification rule

The application must classify every ingested scholarly object by at least:

- scholarly domain;
- source type;
- intended audience;
- level: introductory / intermediate / advanced / specialist;
- methodological orientation;
- publication year;
- edition;
- edition status;
- biblical scope;
- language scope;
- rights status;
- extraction quality;
- retrieval eligibility;
- citation eligibility.

The goal is not to make all books searchable.

The goal is to make the right books searchable for the right question, with their methodological identity, limitations and provenance preserved.


## 28. Current scholarly publication layer

The production knowledge base must not equate "academic sources" with books currently present in Google Drive.

Supported source types must include:

- journal article;
- book chapter;
- edited-volume contribution;
- conference paper;
- dissertation / thesis;
- critical review;
- dataset publication;
- digital scholarly resource.

Where applicable, preserve:

- DOI;
- ISSN;
- journal title;
- volume;
- issue;
- page range;
- editors;
- series;
- peer-review status where known;
- publication status;
- correction / retraction metadata.

Reason:

Reference grammars are foundational, but specialist questions in discourse, prepositions, valency, tense/aspect/modality, corpus linguistics or Hebrew-Chinese translation may be treated more directly in recent articles or monographs.

The system must distinguish:

> "not present in the current library"

from:

> "scholarship does not exist."

## 29. Chinese Bible translation scholarship and documentation

Because the product is specifically a Hebrew–Chinese Bible translation research environment, Chinese translation evidence must extend beyond translation witnesses.

Create a dedicated scholarly lane for:

- histories of Chinese Bible translation;
- translator / reviser prefaces;
- Bible society and publisher translation principles;
- revision documentation;
- translator notes;
- Chinese biblical style / syntax studies;
- Hebrew-to-Chinese translation studies;
- translation theory relevant to biblical translation;
- historical Chinese Bible editions and editorial history.

This lane answers questions such as:

- what a translation project explicitly says its principles are;
- how target-language Chinese constrains a rendering;
- whether a translation choice is idiomatic, explanatory, literary or structurally conservative;
- how historical revisions differ.

It does **not** replace Hebrew grammar or corpus evidence.

A Chinese translation witness proves what a digital expression currently reads. It does not, by itself, prove why the translators chose that rendering.

## 30. Scholarly dependency and source independence

Distinct works are not automatically independent corroboration.

Where evidence matters materially, the system should be able to record or infer cautiously whether one work:

- cites another;
- adopts a classification from another;
- revises another;
- critiques another;
- uses the same underlying corpus or dataset;
- summarises another source.

The application must never derive a quantitative "consensus score" from the number of distinct retrieved works alone.

Statements such as "multiple scholars agree" require source diversity appropriate to the claim.

## 31. Taxonomy versus implementation vocabulary

This document may use descriptive scholarly category names in prose.

Implementation must use the canonical machine-readable dimensions separately:

- sourceRole: what kind of scholarly source this is;
- retrievalNamespace: which retrieval lane is eligible;
- evidenceClass: what epistemic role the retrieved item plays in an answer;
- lifecycle vocabularies: operational workflow only.

These dimensions must not be collapsed into one generic source-type enum.

Where terminology in this document conflicts with `contracts/v1.1/vocabulary.json`, the machine-readable vocabulary controls implementation naming while this document controls the scholarly rationale.
