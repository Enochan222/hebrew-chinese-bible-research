# Site Build Staging Plan

Status: **ARCHITECTURE STAGING PLAN, IMPLEMENTATION HOLD UNTIL v1.1 CONTRACT FREEZE**

This document defines the five future Site Build stages. It is not itself a Site Build prompt.

Before Stage 1 production schema implementation begins, the candidate contract in `architecture/database-api-cross-stage-contract-v1.1-candidate.md` must pass its freeze preconditions.

The superseded `database-api-cross-stage-contract-v1.md` must not be implemented.

Canonical vocabularies are defined in:

- `contracts/v1.1/vocabulary.json`

Security and evaluation requirements are defined in:

- `architecture/security-trust-boundaries.md`
- `architecture/research-evaluation-and-benchmarks.md`

Academic evidence policy remains defined in:

- `architecture/academic-evidence-policy.md`
- `architecture/academic-storage-and-rag.md`
- `docs/academic-source-taxonomy.md`
- `docs/master-academic-source-inventory-and-gaps.md`

## Why the build must be staged

This project is a research-grade Hebrew-Chinese Bible translation environment.

The UI must not establish false ontological assumptions that the data layer later has to imitate.

In particular:

- a reference location may be application-canonical;
- a text expression is edition / expression specific;
- word / morpheme / phrase / clause analyses are framework-scoped unless explicitly curated;
- an FHL version code is provider-distribution identity, not automatically a print-edition identity;
- LXX is an ancient textual version / witness domain, not merely another modern translation column;
- scholarly propositions extracted by AI are representations that require attribution and review.

The current Vercel application remains a reference implementation, not a source-code dependency.

Useful workflow ideas to reconstruct and improve include:

- passage navigation and deep-linkable verse selection;
- MT / LXX / Chinese parallel reading;
- proposed translation area;
- translation-analysis view;
- syntax / BHSA-style view;
- source-and-citation view.

## Global UX direction

The product should look like a serious academic research instrument.

Avoid:

- chatbot-first layout;
- large "Ask AI" hero areas;
- purple/blue AI gradients;
- glassmorphism;
- decorative dashboard tiles;
- excessive animation;
- generic AI marketing language.

Prefer:

- editorial / scholarly hierarchy;
- restrained neutral palette;
- strong Hebrew and Chinese typography;
- research split views;
- source and edition metadata close to evidence;
- dense but readable comparison tables;
- explicit evidence labels;
- visible uncertainty / disagreement;
- professional desktop-first workflow with responsive support.

AI is a downstream research capability, not the visual identity of the product.

---

# Stage 1: Research Shell, Reference Identity, and Text-Expression Foundation

## Primary goal

Build the stable application shell and reconstruct the useful passage-study workflow without prematurely freezing a universal Hebrew tokenisation or syntax ontology.

## Permanent application areas

1. Passage Study
2. Corpus Lab
3. Academic Library
4. Translation Rules
5. Research Projects

## Core layout

Desktop research layout:

- top-level research navigation;
- left Bible / project navigator;
- central workspace;
- right inspector / evidence panel;
- optional provenance / source state area.

## Legacy-reference reconstruction

Using fixture data if necessary, reconstruct:

- book / chapter / verse navigation;
- deep links;
- parallel reading;
- MT display;
- LXX display;
- multiple Chinese translation slots;
- proposed translation;
- translation-analysis tab;
- syntax-analysis tab;
- source/citation tab.

Fixture content must be labelled as fixture data and must not pretend to be live corpus analysis.

## Stage 1 identity contracts

Stage 1 must reserve / implement shared contracts for:

- BiblicalBook
- CanonSystem
- ReferenceSystem
- ReferenceAtom
- ReferenceSpan
- ReferenceLabel
- TextualWork
- TextualEdition
- DigitalExpression
- ProviderDistribution
- SourceRegistry
- Provenance
- RightsPolicy
- EvidenceClass
- ResearchProject

Do **not** create a provider-independent CanonicalToken, CanonicalPhrase or CanonicalClause.

## Rights foundation

Stage 1 must support purpose-aware rights resolution.

At minimum the contract must distinguish:

- storage;
- extraction;
- embedding;
- AI model context;
- caching;
- full-text display;
- excerpt display / quotation;
- export;
- redistribution;
- commercial use.

"Readable by the user" must not automatically mean "permitted in external model context."

## Security foundation

Implement the project-level trust-boundary assumptions early:

- no secret/service key in browser;
- source text is data, not instruction;
- public/private data classes are explicit;
- provider payloads are untrusted;
- future RLS/view/RPC tests have clear extension points.

## Explicitly excluded

Do not yet:

- build final Hebrew morphology / syntax corpus;
- invent a universal token stream;
- implement academic RAG;
- implement AI translation judgments;
- dump copyrighted translations/books into GitHub;
- build final LXX linguistic research functionality.

## Stage 1 acceptance gate

Pass only when:

- navigation and deep links are stable;
- Hebrew RTL / Chinese layout is stable;
- reference identity is separate from text-expression identity;
- UI does not require universal token/phrase/clause IDs;
- LXX and Chinese witnesses can be represented without pretending they have the same epistemic role;
- evidence labels are reusable;
- rights resolver contracts exist;
- later stages can attach real data without redesigning the shell.

---

# Stage 2: Passage Study, Translation Witness Identity, and Alignment

## Primary goal

Build a serious translation-comparison workbench with edition-aware / expression-aware provider integration.

## FHL integration

Use `ytssamuel/FHL-MCP-Server` as a technical reference for FHL API interaction.

Do not copy its AI comparison logic as the academic method.

Use dynamic provider version discovery.

For each FHL witness preserve:

```text
Translation / Textual Work
    -> Edition / Revision when known
        -> Digital Expression
            -> Provider Distribution
                FHL code
```

If a provider text cannot be confidently mapped to a precise print edition, say so.

Do not label a provider transcription simply as "the 1988 edition" or similar unless evidence supports that identity.

## Translation witness view

Support a variable number of witnesses.

Each witness independently reports:

- availability;
- provider;
- work / edition / expression identity;
- rights/display state;
- source metadata;
- notes;
- provider error state.

One provider failure must not break the page.

## User proposed translation

Version the user's translation.

Do not overwrite historical research versions.

## Alignment

Use explicit alignment groups.

Model:

- alignment group;
- source segment members;
- target segment members;
- relation type;
- method;
- algorithm version;
- confidence;
- review status;
- provenance.

Primary alignment must use stable segment IDs.

Raw offsets are secondary and must state coordinate basis plus text revision hash.

## Translation analysis UI

Comparison dimensions may include:

- lexical choice;
- syntax;
- explicitness;
- omission/addition;
- semantic abstraction;
- interpretive expansion;
- idiom;
- repetition;
- parallelism;
- word order;
- ambiguity preserved/resolved.

Always distinguish:

- Documented translator/publisher reason
- Scholarly explanation
- System inference
- Unknown

## Stage 2 acceptance gate

Pass only when:

- provider code is not conflated with edition identity;
- rights metadata participates in provider resolution;
- translations fail independently;
- user translation is versioned;
- alignment represents many-to-many and discontinuous relations explicitly;
- target-segment identity is stable;
- translator intention is never inferred as documentary fact.

---

# Stage 3: Hebrew Corpus, Framework-Scoped Linguistic Analysis, and Pattern Search

## Primary goal

Implement deterministic Hebrew corpus research while making the scope of each linguistic claim explicit.

## Text and corpus model

Support:

- digital expression;
- text stream;
- text segment;
- alternate reading stream;
- normalization profile;
- corpus release;
- annotation framework;
- analysis node;
- analysis edge;
- feature schema;
- lexeme mapping;
- cross-annotation mapping.

OSHB / MACULA / BHSA structures must be allowed to disagree.

No universal app-owned phrase/clause structure is assumed.

## Ketiv/Qere

Represent alternate reading streams and correspondences.

Do not reduce Ketiv/Qere to one status flag on a token.

## Hebrew Unicode

Queries must pin or declare a normalization profile.

Preserve SOURCE_EXACT separately.

Provide regression fixtures for:
- traditional Biblical Hebrew combining mark ordering;
- NFC/NFD;
- cantillation removal;
- niqqud removal;
- consonantal matching.

## Lexeme identity

Introduce internal lexeme identity only through explicit mappings.

Do not join all lexical resources by Hebrew string alone.

Support identifiers such as:
- corpus lemma IDs;
- BHSA lexeme;
- Strong's legacy IDs;
- lexicon locators where legally / technically appropriate.

Mappings require source/version/review metadata.

## Query DSL

Design DSL before visual builder.

### Text-stream relations

Examples:
- immediately precedes;
- precedes;
- within N segments.

### Framework-scoped relations

Examples:
- same phrase;
- same clause;
- governs;
- dependent of;
- semantic role.

Framework-sensitive relations require an annotation framework and corpus release.

The same relation name must not silently change meaning across MACULA/BHSA.

## Result epistemic class

Every query reports whether its result is:

- corpus-complete within pinned scope;
- framework-complete;
- curated-set complete;
- heuristic candidate;
- incomplete coverage.

Semantic analogues must not be displayed as exhaustive linguistic facts.

## Corpus analysis protocol

For frequency/comparison research preserve:

- population;
- inclusion/exclusion criteria;
- denominator;
- coverage;
- genre / book grouping where relevant;
- query sensitivity;
- framework.

Separate:
- token count;
- construction count;
- clause count;
- reference count;
- span/passsage count.

## Explainability

Each match should expose why it matched.

Diagnostic tooling should support why an expected example did not match where feasible.

## Stage 3 acceptance gate

Pass only when:

- provider frameworks can coexist without forced canonical syntax;
- GUI query and DSL are equivalent;
- query scope/release/framework is pinned;
- result completeness class is explicit;
- counts are not inflated by joins;
- Hebrew normalization tests pass;
- Ketiv/Qere fixtures pass;
- semantic analogue provenance is visible.

---

# Stage 4: Academic Knowledge Base, Structured Ingestion, Textual Criticism, Security, and RAG

## Primary goal

Build the scholarly evidence system from the user's source library and future current scholarship without turning the Drive shelf into one flat RAG corpus.

## Source library role

Google Drive is a source/acquisition library, not the production search database.

Use `docs/master-academic-source-inventory-and-gaps.md` as the current inventory / gap map.

The scholarly system must support books **and**:

- journal articles;
- book chapters;
- dissertations/theses;
- conference papers;
- critical reviews;
- dataset publications;
- digital scholarly resources;
- translation documentation.

## Retrieval namespaces

Use only vocabulary from `contracts/v1.1/vocabulary.json`.

Do not invent near-synonymous names in individual implementation modules.

## Work / Edition / Asset

Maintain:

```text
Work
 -> Edition
   -> SourceAsset
     -> ContentHash
```

Deduplicate file assets without erasing historical editions.

## Document structure and source locations

Edition structure and PDF physical location are separate.

Use:

- document nodes for chapter/section/paragraph structure;
- source-asset pages for physical PDF page;
- node-asset locations for mapping;
- source spans for exact citable text.

## Claim extraction

Preserve:

- original source span;
- direct quote where allowed;
- human paraphrase;
- AI-extracted proposition;
- assertion agent;
- modal force;
- scope;
- entailment review status.

An AI paraphrase is not automatically "what the scholar said."

## Claim relationships

Distinguish:
- author-explicit relationships;
- human analytical relationships;
- system/AI inferred relationships.

Rule/qualification/exception relationships must be retrievable together.

## Lexica

Model entry and sense structure.

Do not merge HALOT/DCH/BDB/TWOT/TLOT/TDOT senses into one source-neutral asserted meaning.

## Commentary

Passage-first retrieval before semantic ranking where passage is known.

## Textual criticism

Preserve:
- raw apparatus;
- parsed apparatus entry;
- reading groups;
- readings;
- witness attestations;
- responsibility;
- certainty;
- reading type;
- variant sequence / grouped subvariation where relevant.

Do not pretend first-pass parsing is raw textual fact.

## Scholarly lineage

Support incremental relations such as:
- cites;
- adopts classification;
- revises;
- critiques;
- uses dataset;
- derived from.

Do not infer consensus from distinct work count alone.

## Ingestion pipelines

Classify:

- searchable PDF;
- noisy PDF;
- scanned PDF;
- EPUB;
- DOCX;
- CHM;
- image-based source.

Extraction failure must be explicit.

## Rights

Use purpose-aware rights policies and rules from v1.1 contract.

Rights check precedes:
- persistent storage;
- embedding;
- cache;
- display;
- quotation;
- model context.

## Security

Stage 4 must implement / test the requirements in `architecture/security-trust-boundaries.md`.

Especially:
- grants + RLS;
- safe views;
- RPC/function grants;
- tenant isolation;
- prompt injection;
- source-as-data isolation;
- vector filtered recall;
- retrieval audit.

## RAG

Hybrid retrieval:

1. exact section/reference;
2. Hebrew lemma/form;
3. full-text;
4. concept links;
5. semantic candidates;
6. reranking;
7. deduplication;
8. disagreement / counterevidence pass.

Vector top-k is candidate retrieval, never "all relevant literature."

## Evaluation

Begin / run the benchmark in `architecture/research-evaluation-and-benchmarks.md`.

Stage 4 is not research-ready based only on manual impression.

## Stage 4 acceptance gate

Pass only when:

- duplicated files do not create false consensus;
- every scholarly claim remains traceable to source/edition/location;
- claim representation type is visible;
- rights filter precedes model context;
- textual criticism preserves raw + parsed layers;
- passage-first commentary retrieval works;
- rule + qualification / exception co-retrieval is tested;
- RLS/view/RPC negative tests pass;
- prompt injection tests pass;
- filtered retrieval recall is measured;
- extraction failure is surfaced.

---

# Stage 5: Research Orchestrator, Rules, Assertion-Level Provenance, and Full QA

## Primary goal

Add AI-assisted research synthesis only after corpus and academic evidence systems exist.

## Research orchestration

For a translation question, the system may:

1. inspect text expression / reading;
2. retrieve morphology / syntax;
3. run exact corpus query;
4. run structural query;
5. run contrastive query;
6. retrieve major grammar;
7. retrieve lexicon senses;
8. retrieve textual-critical evidence;
9. retrieve passage commentary;
10. retrieve translation witnesses;
11. retrieve documented translation principles;
12. retrieve user translation/rules;
13. retrieve counterevidence;
14. synthesize with bounded uncertainty.

## Evidence packet

Preserve separate lanes:

- text / reading;
- morphology;
- syntax;
- corpus;
- grammar;
- lexicon;
- textual criticism;
- commentary;
- ancient version evidence;
- translation witnesses;
- translation documentation;
- user research;
- counterevidence.

Do not flatten lanes into one ranked list before synthesis.

## Assertion ledger

Every substantive final analytical assertion should be representable separately.

Example assertion:

> "In this construction, ל is better explained as X than Y."

That assertion must link to:
- supporting evidence;
- opposing evidence;
- qualifying evidence;
- citation locators;
- inference type;
- confidence class;
- entailment review status.

Citation belongs to the assertion, not only to the analysis run.

## User rule system

Rules are versioned user research objects.

They may link to:
- supporting corpus runs;
- opposing corpus cases;
- scholarly claims;
- qualifications/exceptions;
- translation implications.

User rules never become grammar facts merely because they are repeatedly used.

## Challenge My Translation

Must execute a genuinely adversarial retrieval plan:

- counterexamples;
- competing syntax;
- conflicting grammar classifications;
- lexical alternatives;
- textual variants;
- alternative translation witnesses;
- target-language trade-offs;
- unsupported assumptions.

It must not be the normal synthesis prompt with a different label.

## Auditability, not bit-for-bit reproducibility

Persist:

- evidence state;
- pinned corpus/retrieval inputs;
- rule versions;
- user translation version;
- prompt version;
- provider/model identifier;
- sampling parameters when available;
- request/output hashes;
- tool calls;
- evidence packet hash;
- output snapshot.

Do not promise deterministic regeneration of hosted model prose.

## Final QA

Regression areas:

- RTL / bidi;
- Unicode;
- reading streams;
- reference/versification;
- provider identity;
- translation alignment;
- corpus framework scope;
- query count integrity;
- source citation;
- citation entailment;
- rights;
- RLS/views/RPC;
- prompt injection;
- filtered vector recall;
- duplicate evidence;
- stale cache/embedding;
- responsive layout;
- no clipping/overlap.

Stage 5 must not redesign the app unless a verified usability problem requires it.

---

# Build sequencing rule

Every later Site Build prompt must explicitly say:

> Continue modifying the existing project. Do not rebuild or replace the application. Preserve prior working functionality and the active architecture contracts. Do not introduce a new canonical token/phrase/clause ontology, translation-edition identity, rights vocabulary, or retrieval namespace outside the v1.1 contract and canonical vocabulary without an explicit architecture revision.

Each stage must:

1. read the active architecture contract;
2. read the canonical vocabulary;
3. modify the existing project;
4. stay within stage scope;
5. validate its acceptance gate;
6. regression-test earlier stages;
7. preserve source/edition/provenance;
8. update architecture docs when implementation exposes a genuine mismatch.

## GitHub checkpoints

Suggested:

- `build-01-foundation`
- `build-02-passage-translations`
- `build-03-hebrew-corpus`
- `build-04-academic-rag`
- `build-05-research-orchestrator`

Do not deploy to Vercel until explicitly requested.

## Current decision

Keep five stages.

The reason remains structural:

- corpus search is deterministic/framework-scoped data querying;
- academic retrieval is source-sensitive information retrieval;
- AI synthesis is downstream of both.

Combining these systems into one build stage materially increases academic and implementation risk.
