# Hebrew-Chinese Bible Research Project Charter

Status: **CANONICAL PRODUCT INTENT AND REQUIREMENTS**
Version: 1.0
Date: 2026-10-03

## 0. Authority and reading order

This document defines **what the product is trying to achieve, what is mandatory, what is prohibited, and what remains an open implementation decision**.

It does not replace the detailed database/API contracts.

Required reading order for implementation:

1. `PROJECT_CHARTER.md` — product intent, scope, non-negotiable requirements and non-goals;
2. `architecture/manifest.json` — which architecture documents are active;
3. `architecture/database-api-cross-stage-contract-v1.1.md` — canonical data and cross-stage architecture;
4. `contracts/v1.1/` — machine-readable schemas, APIs, vocabularies and freeze gates;
5. specialised active architecture documents for evidence, rights, Research Pro, UI modes and BYOK.

If implementation prose conflicts with machine contracts, the applicable machine contract controls implementation detail.

If an implementation choice satisfies a schema but contradicts the purpose or a non-negotiable requirement in this charter, the implementation is still wrong.

---

# 1. Product mission

The project is a **database-backed, research-grade Hebrew Bible to Chinese translation research product**.

Its purpose is not merely to display Bible text and not merely to ask an LLM to translate Hebrew.

It should help a serious user move from the Hebrew text to a defensible Chinese translation decision through inspectable evidence.

Canonical research loop:

```text
Hebrew passage
  -> textual state / witnesses where relevant
  -> morphology and syntax
  -> whole-corpus parallels and counterexamples
  -> lexica and grammars
  -> scholarly commentary and specialist literature
  -> Chinese translation witnesses and translation documentation
  -> explicit alternatives and uncertainty
  -> translation decision / translation note
  -> citable, version-pinned published research
```

The long-term product is therefore both:

- a Hebrew-Chinese translation research environment;
- a scholarly data product with a persistent database, publication pipeline, versioning and provenance.

It is **not** a disposable single-page AI app.

---

# 2. Intended users

Primary intended users include:

- Hebrew Bible researchers;
- biblical scholars and postgraduate students;
- translators and translation researchers;
- serious users who need inspectable original-language and scholarly evidence.

The product may expose a lower-density Study experience, but Study mode must not become a devotional or academically opaque simplified Bible app.

Research mode provides the fuller professional scholarly environment.

Both modes use the same canonical scholarly data and the same ResearchRelease.

---

# 3. Core product surfaces

The product must support the following connected surfaces.

## 3.1 Passage Study

Required capabilities include:

- book/chapter/verse or equivalent passage navigation;
- Hebrew MT witness;
- LXX evidence where available and properly modelled;
- multiple Chinese translation witnesses;
- optional English/reference witnesses where useful;
- user/proposed Chinese translation;
- clickable Hebrew linguistic analysis;
- morphology, syntax and textual notes;
- published translation analysis;
- evidence and citations;
- passage commentary / translation note;
- navigation into corpus research and back.

## 3.2 Corpus Lab

The product must support deterministic whole-corpus research rather than LLM-generated examples.

Required direction includes:

- lemma/form search;
- morphology filters;
- structural pattern search;
- semantic-set constraints;
- relation-aware query patterns;
- exact / structural / broader analogue distinction;
- match explanation;
- counterexample discovery;
- reproducible counts and result sets;
- bidirectional navigation between corpus results and passages.

Natural-language search may compile to the same query contract, but AI never decides corpus membership.

## 3.3 Chinese Translation Research

Chinese translations are research witnesses, not flat strings placed beside Hebrew.

The product must support:

- dynamic translation witness identity and provenance;
- many-to-many Hebrew-to-Chinese alignment;
- lexical and grammatical comparison;
- omission / addition / explicitation analysis;
- word-order and discourse comparison where defensible;
- corpus-wide observation of how a version renders Hebrew forms/constructions;
- documented translator/project rationale where actual documentation exists;
- explicit distinction between documented rationale and system inference.

The application must never state an inferred translator intention as documented fact.

## 3.4 Academic Knowledge Compiler

The private research system must ingest and structure academic material beyond naive PDF chunking.

Required scholarly structures include, where applicable:

- Work -> Edition -> SourceAsset identity;
- document/chapter/section/paragraph hierarchy;
- exact source locator and page/section provenance;
- source-native terminology;
- claims;
- definitions;
- rules;
- qualifications;
- exceptions;
- examples;
- biblical references;
- cross-references;
- scholarly dependencies;
- review status and review events.

Original source text and AI-extracted/paraphrased representations must remain distinct.

## 3.5 Research Pro / Scholarly Intelligence

Research Pro is part of the same product, not a second product or second truth system.

It should support:

- ResearchIssue / ResearchPosition modelling;
- passage/book/lexeme/construction research targets;
- literature snapshots;
- state-of-research / literature-review artefacts;
- claim/evidence graphs;
- full bibliography;
- scholarly dependency/citation relationships;
- advanced textual criticism;
- recent/live literature discovery;
- research projects and export/citation workflows.

Live discovery is non-canonical until reviewed and incorporated into a later ResearchRelease.

## 3.6 Researcher Workspace

Users should be able to maintain private mutable research state such as:

- saved queries;
- annotations;
- translation drafts;
- saved result sets;
- user semantic sets;
- user rule/hypothesis drafts;
- project folders.

User workspace state must not silently become official published scholarship.

---

# 4. Translation-analysis standard

A translation recommendation must be **evidence-led**, not model-led.

For a materially disputed translation question, the analysis should consider the relevant lanes rather than pretending one source type settles the question:

1. Hebrew primary text;
2. textual variants where relevant;
3. morphology;
4. syntax and clause structure;
5. deterministic corpus parallels and counterexamples;
6. general lexica;
7. major grammars and syntax works;
8. passage commentary / specialist research;
9. Chinese translation witnesses;
10. documented Chinese translation principles/notes where available;
11. explicit alternative analyses;
12. translation implications and uncertainty.

Not every question requires every lane, but the system must make the omitted/relevant lanes intelligible.

A corpus construction is not itself a translation rule.

A grammar's classification is not automatically corpus fact.

A lexicon sense inventory is not automatically the correct sense in a specific passage.

A commentary conclusion is not primary textual evidence.

AI synthesis is not scholarly evidence.

---

# 5. Mandatory scholarly source basis

## 5.1 User-provided Google Drive library

The consolidated Google Drive academic library is a **mandatory curated scholarly source base for the private Academic Knowledge Compiler and translation research workflow**.

Relevant material in that library must not be ignored in favour of generic LLM memory.

For translation analysis, the system should retrieve and use relevant material from the curated library where available, preserving edition, source location, author terminology, qualification and disagreement.

However, the Drive library is **not the epistemic boundary of scholarship**.

If the curated library lacks relevant contemporary or specialist work, the correct system behaviour is to report the coverage limitation and, where supported, use reviewed external scholarly discovery rather than claim that no scholarship exists.

Drive folder placement is not the production ontology.

Possession of a Drive file is not permission to redistribute, publicly index, quote extensively or send it to an external model.

## 5.2 Chinese translation source/provider strategy

`ytssamuel/FHL-MCP-Server` and the underlying FHL ecosystem may be used as a technical/provider reference for Chinese Bible version discovery and retrieval.

FHL/provider data is not the scholarly authority for Hebrew grammar or translation rationale.

Provider identity must remain separate from Work / Edition / DigitalExpression identity.

The product should preserve the useful Chinese witness coverage of the reference application where rights and provider availability permit, but the ontology must not hard-code a supposedly permanent fixed number of Chinese versions.

## 5.3 Hebrew corpus and annotation sources

The architecture must support version-pinned Hebrew text and multiple annotation frameworks/layers.

No external framework-specific token/phrase/clause ID becomes the application's universal linguistic identity.

OSHB, MACULA/Clear, BHSA/ETCBC and other resources may have different roles, licensing and analytical structures.

Cross-framework equivalence is explicit mapped research data, never silently assumed.

---

# 6. Academic integrity requirements

The product must preserve epistemic type.

At minimum it must distinguish:

- primary/source text;
- corpus annotation;
- deterministic corpus observation;
- direct scholarly source text;
- scholarly-claim representation;
- documented translator note;
- user hypothesis;
- system inference;
- AI synthesis;
- unknown / unresolved.

Every material scholarly claim exposed as published research must be traceable to appropriate evidence.

A real citation that does not entail the claim is an academic failure.

AI-extracted propositions remain candidate representations until the required review is satisfied.

Different scholars' taxonomies must not be flattened into a fake single taxonomy merely for retrieval convenience.

Source diversity must not be converted mechanically into a consensus score.

Labels describing a field state must be bounded by a reviewed literature snapshot and coverage limitations.

Counterevidence, exceptions and alternative readings are first-class evidence, not noise to suppress.

---

# 7. Publication and reproducibility requirements

The public scholarly product is compiled and versioned.

Canonical flow:

```text
private authoring/research
  -> validation/review
  -> publication firewall
  -> immutable ResearchRelease
  -> deterministic serving
```

Published scholarly content must be reproducible enough to identify:

- ResearchRelease;
- corpus release;
- annotation layers;
- normalization profile;
- semantic-set version;
- construction/rule versions where used;
- source/evidence identities;
- relevant rights decision snapshots;
- compiler/query version where applicable.

Corrections create new versions/releases rather than silently rewriting historical published scholarship.

Core passage rendering must not re-run academic RAG and regenerate canonical conclusions on every request.

---

# 8. AI and RAG boundaries

AI is a research assistant and compiler aid, not the canonical scholarly authority.

Private authoring may use replaceable tools such as RAG, embeddings, Gemini File Search, external academic discovery or other model-assisted workflows.

AI may assist with:

- extraction candidates;
- concept mapping candidates;
- literature discovery/query expansion;
- natural-language-to-CorpusQuery interpretation;
- explanation of deterministic results;
- comparing a user's translation draft against already retrieved evidence;
- identifying possible counterarguments.

AI must not:

- fabricate corpus examples or counts;
- execute arbitrary model-generated SQL;
- invent scholarly citations;
- attribute a claim to a scholar without evidence;
- infer translator intention and present it as documented fact;
- silently turn a user hypothesis into consensus;
- silently publish claims/rules;
- modify a ResearchRelease through a public request;
- treat model memory as a substitute for the user's academic source base.

---

# 9. Public runtime AI and BYOK

All public runtime model use is **BYOK-only**.

Gemini is the first supported provider.

Non-negotiable requirements:

- no shared platform model API key;
- no hard-coded model credential;
- no Gemini/OpenAI/other fallback credential in code, Vercel, Supabase, GitHub Actions or database;
- user credential is volatile runtime input only;
- user credential is not persisted in localStorage, IndexedDB, cookies, database, logs, analytics, telemetry or evidence;
- missing/invalid BYOK disables only optional AI features;
- deterministic scholarly features continue to work without AI.

BYOK credential permission does not imply permission to send private academic source text to the provider.

Private/restricted source material may enter model context only when the feature explicitly requires it and RightsPolicy permits `MODEL_CONTEXT` for that use.

---

# 10. Rights, copyright and public-product constraints

The product must be designed under the assumption that it may become a public and commercial scholarly product.

Therefore rights are a first-class data and publication concern.

The system must not infer that:

- possession of a PDF permits redistribution;
- API retrieval permits permanent storage;
- display permission permits embedding/indexing;
- private research permission permits commercial/public use;
- an open-source connector's software licence covers the content returned by the provider.

Rights decisions must be operation-specific and default restrictive when permission is unresolved.

ProductEntitlement cannot override RightsPolicy.

Restricted source full text should normally remain outside the public serving datastore.

---

# 11. Technical product invariants

The product is database-supported and version-controlled.

Required architectural invariants include:

- PostgreSQL/Supabase-style relational database is the primary structured store;
- object/file storage is separate from structured scholarly identity;
- Git stores code, schemas, migrations, contracts, tests and small fixtures, not copyrighted source-book corpora;
- Vercel/public web runtime is stateless with respect to canonical scholarly compilation;
- authoring, publication, serving and user workspace are logically separate planes;
- production publication is one-way and validated;
- public runtime has no credential allowing direct access to private authoring sources;
- schema changes are migration/version controlled;
- release-pinned APIs support historical citation and reproduction;
- database identity is internal and stable; provider/framework identifiers are mappings.

Heavy source parsing/OCR/indexing belongs to ingestion/worker workflows, not ordinary page requests.

---

# 12. UX and product-design requirements

The product should look and behave like a serious scholarly research tool, not a generic AI chat product.

Required direction:

- passage-centric workflow;
- dense information made navigable rather than hidden;
- inspectable evidence;
- clear provenance/status labels;
- Hebrew RTL correctness;
- stable navigation between passage, corpus, scholarly evidence and translation decision;
- Study and Research modes over the same canonical state;
- loading/empty/error/restricted-source states handled explicitly.

The existing Vercel prototype is a **reference implementation for useful workflow and interaction patterns only**.

It is not an authority for ontology, database design, licensing assumptions or scholarly conclusions.

Later build phases must extend working functionality rather than silently replace earlier stages.

A professional visual language should be maintained; avoid gratuitous 'AI app' aesthetics.

---

# 13. Explicit non-goals

The project is not:

- a devotional chatbot;
- a generic Bible Q&A bot;
- an LLM-first Hebrew translator;
- a PDF-chat wrapper;
- a flat vector database over academic books;
- a Strong's-number lookup application;
- an app that treats one annotation framework as canonical truth;
- a system that produces a single unexplained 'best translation';
- a runtime system that regenerates canonical scholarship on every request;
- a public redistribution archive of copyrighted academic books;
- a product where Research mode contains different scholarly truth from Study mode;
- a system that requires the product owner to pay for public users' model API calls.

---

# 14. Product success criteria

The project has reached its intended product direction only when a user can do the following without relying on uninspectable model assertions:

1. open a passage and inspect the relevant Hebrew textual and linguistic evidence;
2. compare permitted Chinese translation witnesses with stable provenance;
3. click a Hebrew form/construction and search meaningful whole-corpus parallels/counterexamples;
4. see exactly why corpus examples matched;
5. retrieve relevant grammar/lexicon/commentary/specialist evidence with source location;
6. distinguish the scholar's source text from system paraphrase/AI representation;
7. inspect competing scholarly analyses rather than only one generated answer;
8. draft a Chinese translation and test it against corpus and scholarship;
9. see a reviewed translation note/commentary with assertion-level citations;
10. reproduce/cite the ResearchRelease and versions that supported the conclusion;
11. continue using the core research system when no model provider/BYOK credential is present;
12. trust that restricted private source material is not leaked through public serving or model context.

---

# 15. Fixed requirements versus open decisions

## 15.1 Fixed / non-negotiable

- research-grade Hebrew-to-Chinese focus;
- database-backed product, not throwaway app;
- evidence-led translation analysis;
- Google Drive scholarly library is a mandatory curated authoring source base;
- deterministic corpus evidence;
- Chinese translation comparison;
- assertion-level citation/provenance;
- immutable/versioned ResearchRelease;
- Study + Research as views of the same canonical truth;
- Research Pro remains part of the product architecture;
- rights-first public/commercial readiness;
- strict public BYOK-only runtime AI;
- no model API credential embedded or centrally supplied;
- AI cannot become corpus/citation/scholarly authority;
- source/framework/provider identities remain separate.

## 15.2 Open or deliberately not hard-coded yet

The following must not be guessed by builders unless a later contract freezes them:

- final exact list of Chinese translation witnesses available at launch;
- final provider used for every translation witness;
- final production set/version of Hebrew corpus annotation resources;
- final set of academic discovery providers/MCPs;
- final commercial entitlement plans/pricing;
- final public availability of particular copyrighted source excerpts;
- final hosting region/topology beyond the security/data-boundary requirements;
- final optional AI model list beyond Gemini-first BYOK;
- full Research Pro feature rollout order;
- final visual details within the professional scholarly UX direction.

Open decisions must be resolved through explicit contract/ADR updates, not silently chosen in generated application code.

---

# 16. Current delivery state

The project is currently in architecture-contract closure / pre-database-implementation stage.

Core contract gates permit proceeding to Database Spike 001, but this does not mean the entire v1.1 product is frozen.

Database implementation, RLS/grants, real corpus ingestion, query compilation, rights enforcement and publication transactions still require implementation evidence.

Research Pro and public BYOK shipping retain their own freeze/acceptance gates.

Do not deploy to Vercel until explicitly requested.
