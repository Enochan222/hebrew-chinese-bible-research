# Corpus Source Integration: OSHB, BHSA, and ETCBC Bridging

Status: **ACTIVE WHOLE-BIBLE SOURCE-INTEGRATION CONTRACT**

This document defines how Open Scriptures Hebrew Bible morphology, ETCBC BHSA linguistic annotations, and ETCBC bridging data enter the Hebrew-Chinese Bible Research product.

It does not make any upstream corpus the project's universal linguistic truth.

## 1. Core rule

The product keeps these distinctions:

- canonical reference location is project-owned;
- source text is edition/expression-specific;
- morphology, segmentation, phrase/clause structure and syntax are framework-scoped;
- cross-framework mapping is explicit research data;
- project semantic sets are project-curated research objects;
- a ResearchRelease pins the exact upstream source versions used.

Therefore:

OSHB morphology != BHSA morphology != project adjudication.

BHSA phrase/clause structure != universal Hebrew phrase/clause structure.

ETCBC bridging != universal OSHB-word-ID to BHSA-node identity.

## 2. Pinned first integration

The machine authority is:

- `contracts/v1.1/corpus-source-registry.json`;
- validated by `contracts/v1.1/json-schema/corpus-source-registry.schema.json`.

Initial pins:

### OSHB / morphhb

Repository: `openscriptures/morphhb`

Commit: `3d15126fb1ef74867fc1434be1942e837932691f`

Role:

- Hebrew/WLC text-expression input;
- provider-scoped word identity;
- lemma input;
- morpheme segmentation;
- morphology.

OSHB is the default source for morphology and morpheme-sensitive search in the first Database Spike.

The source form must be preserved exactly. Do not NFC-normalize source identity. Any search-normalized derivative must be generated through a versioned NormalizationProfile.

### BHSA 2021

Repository: `ETCBC/bhsa`

Repository commit used to fetch the frozen data: `4db00e2157915495e1a4d3d57e41223df24775da`

Dataset version: `2021`

Role:

- independent lexical/morphological evidence;
- phrase structure;
- clause structure;
- phrase/clause function and relation;
- selected dependency-like structural relations;
- Ketiv/Qere-related features.

BHSA structures are imported as BHSA-scoped AnnotationLayers. They must not overwrite OSHB segmentation or become project-canonical phrase/clause identity.

### ETCBC bridging 2021

Repository: `ETCBC/bridging`

Commit: `324598bb3f9cb3a36543e77ac61e4b0f77addf82`

Dataset version: `2021`

The bridge compares BHSA and Open Scriptures and exposes Open Scriptures morphology on BHSA word nodes. In this product it is mapping/comparison evidence.

It is not treated as a complete provider-word-ID mapping and must not silently establish universal word identity.

The 2021 bridge artifact does not embed an immutable current Open Scriptures commit pin that can be assumed equivalent to this project's current OSHB pin. Therefore its `osm` / `osm_sf` features are valid as 2021 comparison evidence on BHSA nodes, but they do not authorize direct use of current OSHB provider word IDs as BHSA node mappings.

## 3. What is downloaded

Upstream corpora are not vendored into this GitHub repository.

Local source cache:

`.local/corpora/`

This directory is ignored by Git.

The fetcher downloads only the version-pinned material declared by the registry.

OSHB:

- README and licence;
- `wlc/*.xml`.

BHSA 2021:

- Text-Fabric structural features needed to load the graph;
- all features referenced by `otext.tf` text/lexical formats so Text-Fabric can initialize the pinned dataset without hidden upstream downloads;
- reference features;
- source Hebrew/text features;
- selected lexical and morphology features;
- phrase/clause function/type/relation features;
- selected language and Qere features;
- the Text-Fabric format dependency closure referenced by `otext.tf`, including transliterated/UTF-8 text, trailer, qere, and lexeme features required for Text-Fabric format initialization.

The fetch remains a bounded feature subset rather than a clone of the whole BHSA repository. The extra closure files are present because Text-Fabric loads the configured formats even when the exporter requests only a smaller analysis feature set.

ETCBC bridging 2021:

- README and licence;
- `osm.tf`;
- `osm_sf.tf`.

Every downloaded source directory receives a local `source-manifest.json` containing the source key, exact upstream commit, dataset version, per-file SHA-256 and byte counts.

The local cache is reproducible input, not canonical application data.

## 4. Fetch and export commands

Install corpus tooling when BHSA export is needed:

```bash
python -m pip install -r requirements-corpus.txt
```

List configured sources:

```bash
python scripts/corpora/fetch_sources.py --list
```

Fetch all pinned sources:

```bash
python scripts/corpora/fetch_sources.py
```

Fetch only one source:

```bash
python scripts/corpora/fetch_sources.py --source OSHB_MORPHHB
python scripts/corpora/fetch_sources.py --source BHSA_2021
python scripts/corpora/fetch_sources.py --source ETCBC_BRIDGING_2021
```

Check whether upstream default branches have moved:

```bash
python scripts/corpora/fetch_sources.py --check-upstream
```

This command never updates the pinned versions.

Export OSHB 1 Samuel 16:7 as provider-scoped NDJSON:

```bash
python scripts/corpora/export_oshb_words.py \
  --reference 1Sam.16.7 \
  --output .local/exports/oshb-1sam16-7.ndjson
```

Export BHSA 2021 plus available bridging features:

```bash
python scripts/corpora/export_bhsa_features.py \
  --reference 1Sam.16.7 \
  --output .local/exports/bhsa-1sam16-7.ndjson
```

These exporters deliberately emit provider-scoped/raw fields first. Export scope is explicit: `--reference` is for canary/debug execution and `--all` is for complete pinned-provider execution. Database import/adjudication may derive normalized project fields only after the raw identities and provenance have been stored.

CLI passage filters normalize known provider book aliases only for comparison. For example, OSHB `1Sam`, BHSA Latin `Samuel_I`, and BHSA English `1_Samuel` compare as the same temporary canonical book key. The exporter still writes the exact provider-native `referenceLabel` and `referenceSystemCode`; alias normalization does not replace the project's ReferenceSystem/ReferenceSpan resolution layer.

When a requested passage yields zero OSHB or BHSA words, the relevant exporter exits with failure instead of silently treating an empty file as a successful source export. The BHSA error also reports the observed provider book labels at the requested chapter/verse.

Build a conservative current-OSHB to BHSA candidate crosswalk for the spike:

```bash
python scripts/corpora/build_candidate_crosswalk.py \
  --oshb .local/exports/oshb-1sam16-7.ndjson \
  --bhsa .local/exports/bhsa-1sam16-7.ndjson \
  --output .local/exports/crosswalk-1sam16-7.ndjson
```

The crosswalk does not require equal token counts. It aligns only contiguous text-bearing spans within the same normalized verse when the concatenated Hebrew-letter consonantal signatures are exactly equal. This allows conservative 1:1, 1:n, n:1, and n:m candidate mappings across framework-specific tokenization.

A BHSA node with no orthographic/consonantal value may be preserved as `ANNOTATION_ONLY_TARGET_NODE` only when it matches an explicitly reviewed source shape. The first implementation recognizes the observed unbridged Biblical Hebrew article shape: lexeme present, `sp=art`, `pdp=art`, `languageISO=hbo`, phrase and clause membership present, and no Qere or bridging morphology. Such a node is retained in the BHSA annotation graph but is not assigned an invented orthographic TextSegment or OSHB identity. Every other empty target node remains `NEEDS_REVIEW` until separately classified.

If the full text-bearing verse consonantal streams differ, a source token has an empty signature, or the two streams cease to be prefix-compatible, the whole reference becomes `NEEDS_REVIEW`. Candidate mappings remain `CANDIDATE_AUTOMATED` and `canonical = false` until Database Spike review promotes them through the project's typed mapping workflow.

## 5. Decision table: when to use which source

| Research need | Default source | Rule |
|---|---|---|
| exact OSHB provider word ID | OSHB | keep provider-scoped; do not turn into project canonical word identity |
| Hebrew surface/WLC input | OSHB | preserve source Unicode exactly |
| lemma/morphology | OSHB | default first implementation; BHSA may provide independent comparison |
| prefix/suffix/morpheme-sensitive query | OSHB | use MORPHEME_SEGMENTATION / MORPHOLOGY layer |
| phrase membership/function | BHSA 2021 | query must declare BHSA PHRASE_STRUCTURE layer |
| clause membership/type/relation | BHSA 2021 | query must declare BHSA CLAUSE_STRUCTURE layer |
| BHSA structural relation | BHSA 2021 | never describe as framework-independent fact |
| compare Open Scriptures morphology on BHSA nodes | ETCBC bridging 2021 | derived mapping/comparison evidence only |
| BODY_PART, PERCEPTION_VERB or other project semantic class | project SemanticSetVersion | upstream corpus labels do not replace project semantic-set authority |
| mixed morphology + clause query | OSHB + BHSA + explicit mapping | all participating layers and mapping version are pinned |
| source disagreement | preserve both | no silent merge; adjudication is a separate reviewed project object |

## 6. Example: 1 Samuel 16:7

The live PR smoke observed 25 OSHB word records and 34 BHSA word records for this verse. Two BHSA slots, nodes `150439` and `150445`, carry article (`art`) lexical/syntactic annotation and phrase/clause membership but no `g_word_utf8` or `g_cons_utf8` orthographic content. The normalized full-verse consonantal streams remain identical after excluding no characters from either provider. These nodes are therefore preserved as annotation-only BHSA nodes and excluded only from the orthographic crosswalk; they are not deleted and are not attached arbitrarily to neighbouring OSHB tokens.

That is direct implementation evidence that the two providers cannot be connected through a universal 1:1 word identity. The project therefore treats segmentation divergence as normal framework-scoped data and uses explicit many-to-many cross-annotation mappings where the textual evidence supports them.

For a query such as:

`ראה + ל-prefixed BODY_PART + SAME_CLAUSE`

the first implementation should resolve it as a multi-layer query:

1. OSHB identifies provider-scoped words, lemmas and morphology.
2. OSHB morphology/morpheme data identifies the relevant prefixed form.
3. the project SemanticSetVersion determines BODY_PART membership.
4. BHSA 2021 supplies the declared clause-structure relation.
5. an explicit reviewed mapping establishes which objects may participate in the cross-layer query; the candidate span crosswalk may propose many-to-many mappings but cannot promote itself to canonical/reviewed state.
6. CorpusQuery executes against one ResearchRelease that pins all dependencies.

The query result must disclose the annotation layers used.

If the OSHB/BHSA mapping is absent or disputed, the engine must not invent a cross-layer match.

## 6A. WB-CORPUS-001 whole-Bible source foundation

WB-0 has already proved that the relational model can preserve the difficult 1 Samuel 16:7 canary. Before WB-1 scales that importer to the complete configured corpus, the source/build layer must establish a deterministic whole-Bible input boundary:

```text
pinned OSHB source XML
  -> independent OSHB_OSIS reference inventory
  -> complete OSHB provider export

pinned BHSA + ETCBC bridging
  -> complete BHSA provider export

provider exports
  -> reference reconciliation
  -> conservative candidate crosswalk
  -> deterministic WB-CORPUS-001 coverage manifest
```

Run:

```bash
python scripts/corpora/build_whole_bible_corpus.py
```

The expected-reference inventory is generated directly from the exact pinned OSHB XML and source manifest, independently of `export_oshb_words.py`. This prevents a source exporter omission from shrinking the denominator used to judge its own completeness.

At this stage `OSHB_OSIS` is explicitly a **bootstrap source-derived ReferenceSystem snapshot**. It does not replace project-owned CanonSystem/ReferenceSystem/ReferenceSpan adjudication in PostgreSQL.

Whole-Bible coverage is reference-set based. A fixed provider division count such as 39 or 24 is not a canonical completeness gate. Provider book divisions remain useful provenance/diagnostics only.

The machine-readable manifest records:

- exact OSHB/BHSA/bridging pins;
- selected ReferenceSystem reference-set hash and expected spans;
- OSHB/BHSA record and reference counts;
- candidate mapping and annotation-only counts;
- unresolved mapping reasons;
- missing/provider-only references by source;
- per-book diagnostics;
- artifact hashes;
- explicit silent-reference-loss status.

Known provider/reference mismatches may remain explicit exceptions. A reference that disappears without an explicit crosswalk/provider record is a gate failure.

WB-CORPUS-001 stops before PostgreSQL. WB-1 must consume this source foundation through the same corpus-wide importer architecture proven by WB-0.

## 7. Database mapping contract

Downloaded records enter authoring ingestion as provider-scoped source objects.

Minimum provenance carried forward:

- sourceKey;
- provider;
- repository;
- exact commit SHA;
- dataset version where applicable;
- provider-scoped node/word identity;
- source reference label/system;
- source-exact surface;
- raw upstream morphology/features;
- ingestion activity and compiler version.

Project tables then map those inputs to:

- DigitalExpression / TextStream / TextSegment;
- CorpusRelease;
- AnnotationLayer;
- AnalysisNode / AnalysisFeature / AnalysisEdge;
- cross_annotation_mappings;
- Lexeme mappings;
- ReferenceSpan;
- SemanticSetVersion.

No importer may create a project-canonical phrase/clause simply because BHSA has a phrase/clause node.

## 8. Rights and publication boundary

OSHB:

- upstream identifies WLC text as public domain;
- lemma and morphology are CC BY 4.0;
- attribution is required for the licensed data.

BHSA:

- BHSA data documentation identifies the data as CC BY-NC 4.0;
- commercial application requires separate permission;
- the repository software licence must not be confused with the dataset licence.

ETCBC bridging:

- repository code is MIT;
- the produced data derives from BHSA and Open Scriptures;
- this project applies the most restrictive relevant upstream rights until a reviewed RightsDecision permits a broader operation.

Consequences:

- local/private Database Spike use is allowed only within the applicable upstream terms;
- raw BHSA/bridging data is not committed to this public repository;
- BHSA-derived public/commercial serving is `RIGHTS_DECISION_REQUIRED`;
- bridging-derived public serving defaults to DENY until rights review;
- ProductEntitlement can never override these rights decisions.

## 9. Upstream update policy

Never follow `master`, `main`, `latest` or `hot` automatically in a ResearchRelease.

When upstream moves:

1. run `fetch_sources.py --check-upstream`;
2. inspect upstream release/commit changes;
3. update the source registry in a PR;
4. fetch into a clean cache;
5. compare source manifests and record changed files/counts;
6. rerun OSHB/BHSA mapping validation and Database Spike fixtures;
7. review changed corpus results, especially 1 Samuel 16:7 and known edge cases;
8. publish only through a new ResearchBuild / ResearchRelease.

Old releases continue to pin their old source versions.

## 10. Database Spike 001 requirement

**WB-0 implementation boundary:** the Database Spike retains its independent controlled-fixture job and now adds a second clean PostgreSQL real-corpus canary. The WB-0 job fetches the exact registry pins, exports real OSHB/BHSA 1 Samuel 16:7 records, builds the conservative candidate crosswalk, loads those records into Authoring through `scripts/corpora/load_wb0_postgres.py`, and runs `database/spikes/001/04_real_corpus_tests.sql`. This proves only the bounded relational canary when the exact-head CI job is green; it does not prove whole-Bible WB-1 coverage or public Serving rights.

The first real corpus vertical slice must use these pinned sources.

Minimum test:

- OSHB 1 Samuel 16:7 import;
- BHSA 2021 1 Samuel 16:7 import;
- bridging 2021 comparison features where available;
- project BODY_PART semantic set;
- grouped explicit non-canonical mapping evidence;
- a multi-layer OSHB morphology -> grouped mapping -> BHSA BODY_PART/clause relational query;
- an invalid cross-layer mapping that the database rejects.

The spike must record any mismatch between source tokenization/reference labels and the current contract. It must change the contract if real corpus evidence disproves an assumption.

## 10.1 WB-1 relational whole-corpus execution

WB-CORPUS-001 is the only complete-source input authority for WB-1. WB-1 does not run an independent second coverage model.

Execution:

1. rebuild and validate WB-CORPUS-001 from exact pins;
2. bind the relational run to its build ID, ReferenceSystem hash and artifact hashes;
3. partition the accepted artifacts by the selected `TANAKH_OSIS_39` CanonSystem only to bound memory/transaction size;
4. import each configured book transactionally into PostgreSQL Authoring;
5. reconcile PostgreSQL counts back to the source-foundation records and selected ReferenceSystem inventory;
6. retain unresolved cross-framework references as explicit non-canonical research exceptions;
7. fail on silent source-record loss, missing configured source divisions, duplicate provider identities, OSHB source-surface loss, importer failure or database/source parity drift;
8. keep real BHSA/bridging corpus data out of Serving until WB-2 rights-safe compilation.

Whole-corpus data also disproves the WB-0-only equality assumption for direct node/segment spans. A phrase or clause may cover multiple ReferenceAtoms. The relational invariant is therefore same-expression, same-book containment of each member TextSegment span within its AnalysisNode span.

Provider-only BHSA reference addresses may be represented relationally with explicit source-coverage metadata; they do not silently expand the selected OSHB_OSIS source inventory.

## 11. What this integration does not decide

This integration does not yet declare:

- BHSA licensed for commercial public serving;
- BHSA syntax superior to MACULA or another framework;
- OSHB morphology infallible;
- ETCBC bridging complete for current OSHB/BHSA versions beyond its pinned 2021 comparison;
- a final production corpus mix for every feature;
- a universal canonical token, phrase or clause layer.

Those remain evidence-driven decisions.
