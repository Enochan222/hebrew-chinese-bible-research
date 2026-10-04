# Repository Change Log

Every push/PR must update this file together with `PROJECT_STATE.md`.

Entries record **what changed, why, intended effect, and validation**. The Git commit itself supplies the immutable SHA/timestamp linkage.


## 2026-10-04 — Make whole-Bible coverage the base product and add full OSHB relational import

### Push intent

Correct the implementation emphasis after product clarification: the project is a whole-Hebrew-Bible reader/research platform first, with academic Research Pro enrichment layered on top. Passage fixtures remain adversarial verification vectors rather than product scope.

### Why

The charter already named the whole Hebrew Bible as the long-term scope, but the staging plan and executable evidence could still be read as though a handful of deeply analysed passages were the primary build target and real corpus ingestion belonged only to a later advanced-search phase. That risks over-investing in Research Pro architecture while the base reader still lacks a product-scale corpus path.

### What changed

- strengthened the canonical charter so whole-Bible base coverage is an implementation baseline and Research Pro can be progressively enriched without blocking passage existence;
- added `architecture/whole-bible-base-product.md` as active authority separating base reader, deterministic-analysis overlay and Research Pro overlay;
- moved baseline whole-corpus ingestion into Phase 1 while retaining advanced multi-framework CorpusQuery work in Phase 3;
- added a deterministic OSHB whole-Bible coverage index that fails on missing/unexpected provider book files, duplicate/non-monotonic references or zero-word verses;
- added a deterministic PostgreSQL COPY loadset generator for all pinned OSHB books/verses/words using stable UUIDv5 project IDs;
- import the OSHB baseline into canonical ReferenceSystem, ReferenceAtom/Span/Label, TextualWork/Edition/Expression, TextStream/TextSegment, CorpusRelease, AnnotationLayer and AnalysisNode structures;
- preserve exact OSHB source Unicode and provider word IDs without promoting provider identity to universal canonical identity;
- added a PostgreSQL 17 whole-Bible integration harness that reconciles source coverage, import-manifest and database counts and retains 1 Samuel 16:7 as a 25-word canary.

### Intended effect

The repository now has an executable path from the exact pinned OSHB source to product-scale canonical Authoring data for the complete provider corpus. The next implementation dependency becomes Serving publication/navigation and the whole-Bible reader, not another passage-specific architecture exercise.

### Validation

The first `Whole-Bible corpus foundation` run reached the real pinned OSHB source and correctly failed before database work because `wlc/VerseMap.xml` was initially classified as an unexpected book XML. Upstream inspection showed that this is an auxiliary verse-mapping file, not a biblical book. The validator now permits only that exact known auxiliary XML while retaining hard failure for any other unexpected XML. The corrected PR head must pass the existing contract/governance/database/web regressions plus the whole-Bible workflow from a blank PostgreSQL 17 database. No remote Supabase or Vercel target is modified.


## 2026-10-04 — Harden corpus cache provenance and empty-export failure semantics

### Push intent

Close two post-merge fail-closed gaps in the pinned Hebrew-corpus tooling before using its outputs as input to real relational ingestion.

### Why

The successful 1 Samuel 16:7 smoke proved the normal acquisition/export/crosswalk path, but independent adversarial review found two cases the workflow did not test. First, cache verification trusted whatever file list appeared in a local `source-manifest.json`; a truncated or incomplete manifest could therefore omit files from verification while retaining the correct source pin metadata. Second, `export_oshb_words.py` returned success and left an empty NDJSON file when a syntactically valid requested reference did not exist.

### What changed

- bind source manifests to registry schema version, acquisition method and exact configured acquisition paths;
- require a non-empty manifest file array;
- reject unsafe/traversal paths and duplicate manifest paths;
- validate manifest SHA-256 syntax, byte counts, on-disk byte size and content hash;
- require the manifest file set to equal the actual cached file set, rejecting both missing and untracked files;
- reject unsafe configured archive/raw-file paths before filesystem writes;
- make zero-record OSHB export a non-zero failure and remove the empty output artifact;
- add adversarial CI checks for truncated manifests, manifest traversal, untracked cache files, configured path traversal and a nonexistent OSHB reference.

### Intended effect

A locally cached corpus can no longer be accepted merely because a self-authored manifest carries the right commit SHA, and downstream jobs cannot mistake an empty OSHB export for a successful passage extraction. These controls strengthen provenance/integrity only; they do not promote candidate crosswalks or change corpus licensing.

### Validation

The new PR must pass Contract validation, Project governance and Corpus source smoke. The adversarial smoke cases are expected to fail against the previously merged tooling and pass only with these guards.

## 2026-10-04 — Close CitationLocator and passage-scoped MCP identity gaps

### Push intent

Repair two machine-contract defects found by post-merge adversarial review, and synchronize the living state with the fact that Database Spike 001 is now merged.

### Why

The CitationLocator schema required type-specific property names but several identity properties still accepted `null`, while printed-page labels could be empty. Separately, the Product MCP `get_rule_applications` input retained a pre-ReferenceSystem bare `reference` string even though the project now requires every human reference label to carry explicit ReferenceSystem identity. Existing fixtures did not exercise either failure mode.

### What changed

- made SOURCE_SPAN, PRINTED_PAGE, SOURCE_ASSET_PAGE, DOCUMENT_SECTION, LEXICON_ENTRY, BIBLICAL_REFERENCE, and CORPUS_RESULT locator identities non-null and made printed-page labels non-empty;
- changed RuleApplicationsRequestV1 to reuse PassageLocatorV1, accepting either canonical `referenceSpanId` or `referenceSystemCode` plus `referenceLabel`;
- added one positive rule-application request fixture and nine negative regression fixtures;
- updated Product MCP prose, active architecture, and the machine-contract inventory;
- corrected PROJECT_STATE implementation priorities and latest intent after PR #9 merged to protected `main`.
- limited secret scanning to repository-controlled source and configuration, excluding dependency, build, test-report, coverage, cache, and VCS directories so generated third-party files cannot create false positives.

### Intended effect

Public evidence cannot carry formally present but unusable locator identities, and passage-scoped rule-application reads can no longer resolve human labels outside an explicit reference system.

### Validation

- regression-first contract runs failed on the new rule-application fixture and eight nullable/empty CitationLocator cases before the schema repair;
- a combined web/contract validation run reproduced false secret alarms from `.next` and `node_modules` before the generated-directory exclusion;
- repaired local contract validation passes with 40 positive fixtures plus all negative, semantic, vocabulary, governance, and secret checks;
- Core and Research Pro OpenAPI validation remain required before push/merge;
- GitHub `contracts` and `state-and-changelog` checks remain the merge authority.

## 2026-10-04 — Connect pinned OSHB, BHSA 2021, and ETCBC bridging corpus sources

### Push intent

Turn the previously open OSHB/BHSA corpus-source decision into a reproducible first implementation for Database Spike 001 without vendoring large upstream corpora or collapsing incompatible annotation frameworks.

### Why

The project already had the correct framework-scoped ontology, CorpusQuery layer pinning, rights model, and an explicit Spike requirement to test OSHB against structurally different BHSA/MACULA-style data. What was missing was an executable acquisition/import boundary: exact upstream pins, local download rules, provider-scoped exporters, rights defaults, and a decision table telling future agents which source should answer which class of corpus question.

OSHB and BHSA are complementary rather than interchangeable. OSHB is well suited to the initial word/lemma/morpheme/morphology baseline. BHSA provides a rich independent phrase/clause/syntactic framework. ETCBC bridging provides Open Scriptures morphology comparison on BHSA word nodes, but does not prove a universal provider-word-ID identity.

### What changed

- added `contracts/v1.1/corpus-source-registry.json` with exact reviewed pins for:
  - OSHB/morphhb commit `3d15126fb1ef74867fc1434be1942e837932691f`;
  - BHSA frozen dataset `2021` from repo commit `4db00e2157915495e1a4d3d57e41223df24775da`;
  - ETCBC bridging `2021` commit `324598bb3f9cb3a36543e77ac61e4b0f77addf82`;
- added JSON Schema validation for the corpus source registry;
- added `architecture/corpus-source-integration.md` as active authority;
- added `scripts/corpora/fetch_sources.py` to download only configured pinned source material into `.local/corpora/`, generate SHA-256 source manifests, verify existing caches, and report upstream movement without ever auto-advancing pins;
- added `scripts/corpora/export_oshb_words.py` for provider-scoped OSHB OSIS NDJSON export with source Unicode preserved exactly;
- added `scripts/corpora/export_bhsa_features.py` for provider-scoped BHSA word/phrase/clause NDJSON export and optional pinned bridging features;
- added `scripts/corpora/build_candidate_crosswalk.py` to propose only fail-closed, non-canonical current-OSHB to BHSA word mappings when reference/order/consonantal signatures agree;
- pinned Text-Fabric `13.1.0` in `requirements-corpus.txt` for the BHSA adapter;
- added `.gitignore` rules so downloaded corpora and generated local exports do not enter Git;
- documented the usage policy:
  - OSHB for the first morphology/morpheme baseline;
  - BHSA for declared phrase/clause/syntax layers;
  - ETCBC bridging for derived comparison/mapping evidence;
  - project SemanticSetVersion for project semantic classes;
  - preserve disagreement rather than silently flattening it;
- documented the rights boundary:
  - OSHB licensed morphology/lemma data requires attribution;
  - BHSA data is treated as CC BY-NC with explicit RightsDecision required for public/commercial serving;
  - bridging-derived public serving defaults to deny until mixed upstream rights are reviewed;
- strengthened the Database Spike 001 specification so the next real-corpus relational round must import these pinned sources and require an explicit compatible cross-layer mapping; the currently merged PostgreSQL harness still uses controlled synthetic fixtures;
- extended contract validation to validate the registry, its semantic source ensemble/rights invariants, and corpus-adapter Python syntax;
- updated README, contracts README, architecture manifest, PROJECT_STATE and this CHANGELOG.

### Intended effect

A developer can now reproducibly fetch and inspect the exact upstream Hebrew data prepared for the next real-corpus database-spike round, export provider-scoped records, and know which annotation layer owns each claim. Upstream branch movement cannot silently change an existing ResearchRelease, and BHSA licensing cannot be bypassed by treating repository availability as public/commercial permission.

### Validation

#### First real smoke result and repair

The first `Corpus source smoke` run on PR #8 provided useful negative evidence rather than being bypassed:

- exact OSHB, BHSA 2021 and ETCBC bridging downloads all completed and verified;
- OSHB 1 Samuel 16:7 export succeeded with 25 provider-scoped word records;
- BHSA export failed during Text-Fabric initialization with `KeyError: 'g_cons'`;
- inspection of pinned BHSA `tf/2021/otext.tf` showed that its declared text/lexical formats reference both UTF-8 and transliterated/plain features, so the original curated subset was incomplete even though the exporter itself did not request `g_cons`.

Repair:

- add every pinned feature referenced by `otext.tf` format expressions plus section features to the BHSA acquisition set;
- make `fetch_sources.py` parse pinned `otext.tf` and fail early if any referenced local feature file is missing;
- make contract validation assert the minimum BHSA Text-Fabric dependency set;
- rerun the unchanged real-corpus smoke until export and candidate crosswalk complete successfully.

#### Second real smoke result and repair

Run `37192323018` advanced materially further:

- all exact pinned source downloads passed;
- OSHB export passed with 25 words for 1 Samuel 16:7;
- BHSA Text-Fabric initialization and export process itself passed, proving the dependency-closure repair;
- the requested BHSA filter still produced zero rows;
- crosswalk compilation then correctly emitted one unresolved reference rather than inventing mappings;
- final smoke verification failed because `bhsa.ndjson` was empty.

The zero-row result exposed a provider-label assumption, not a corpus absence. BHSA ships both Latin `book` labels such as `Samuel_I` and English `book@en` labels such as `1_Samuel`; Text-Fabric section presentation must not be assumed to equal the CLI's hard-coded spelling.

Repair:

- add shared `scripts/corpora/reference_aliases.py` covering OSHB, BHSA Latin, and BHSA English book labels;
- use alias normalization only to compare/filter references;
- preserve provider-native labels in exported records;
- make BHSA requested-reference zero-row output a hard error with diagnostics;
- make current-OSHB/BHSA crosswalk normalize both provider labels through the same shared function;
- use `1Sam.16.7` as the common smoke input and rerun the real workflow.

#### Third real smoke finding: segmentation is genuinely many-to-many

Run `37192627166` passed the complete existing smoke and produced the first reliable real-data comparison:

- OSHB 1 Samuel 16:7: 25 word records;
- BHSA 1 Samuel 16:7: 34 word records;
- all pinned downloads, Text-Fabric load, both exporters, crosswalk process, and output-format validation succeeded;
- the previous 1:1/count-equality crosswalk correctly refused to fabricate mappings and emitted one `UNRESOLVED_REFERENCE`.

This result is not treated as a nuisance to suppress. It proves the architecture's framework-scoped segmentation premise on the primary spike verse.

Repair/extension:

- replace count-equality/zip mapping with conservative contiguous many-to-many span alignment;
- require exact equality of the whole normalized verse consonantal stream before any automatic span proposal;
- form the smallest contiguous source/target groups whose Hebrew-letter signatures match;
- support 1:1, 1:n, n:1, and n:m candidates while preserving provider IDs and word orders;
- keep every generated mapping `CANDIDATE_AUTOMATED`, `canonical = false`;
- fail closed to `NEEDS_REVIEW` for textual stream mismatch, empty signatures, exhaustion, or non-prefix divergence;
- tighten the 1 Samuel 16:7 smoke so it must produce at least one actual many-to-many candidate and no unresolved reference.

#### Fourth smoke diagnostic hardening

The stricter many-to-many smoke still produced one unresolved reference and no candidate spans. The existing job output did not expose the unresolved reason, so changing the mapping algorithm again would be guesswork.

Added permanent fail-closed diagnostics to unresolved crosswalk records and CI output:

- machine reason code;
- OSHB/BHSA word counts;
- consonantal stream lengths;
- SHA-256 of each consonantal stream;
- first differing character index.

The diagnostic deliberately does not print the verse text. The next smoke run is used to classify the failure before any further mapping change.

#### Fifth smoke: isolate zero-letter provider tokens

Run `37193120184` classified the previous ambiguity:

- OSHB whole-verse consonantal length: 92;
- BHSA whole-verse consonantal length: 92;
- SHA-256 of both normalized consonantal streams: `886cfe4cab6d1c1d3d032b5ed3cd201d3c12a41f82655ba04be075155f494253`;
- first differing character: none;
- alignment nevertheless stopped with `EMPTY_CONSONANTAL_SIGNATURE`.

Therefore the failure is not a textual-version mismatch and not a whole-verse normalization mismatch. Before changing alignment semantics, the crosswalk now records only the order/provider identity and boolean source-field presence of zero-letter tokens. It still does not print source Hebrew text. The next real smoke must identify which provider records have empty Hebrew-letter signatures; only then may the alignment rule decide whether they are ignorable structural tokens, exporter defects, or separately reviewable mappings.

The next diagnostic run identified the zero-letter side precisely: OSHB has no empty-signature word records, while BHSA word-order positions 27 and 33 are nodes `150439` and `150445`; both have neither `g_cons_utf8` nor `g_word_utf8`. Because BHSA documentation describes those features as the normal word-occurrence representations, the integration does not yet classify the nodes as ignorable. A narrower metadata-only probe now records POS/PDP, language, presence of lexeme/qere/bridging morphology, and phrase/clause membership for those two nodes. Mapping behavior remains fail-closed until that probe classifies them.

#### Sixth smoke: classify BHSA annotation-only nodes

Run `37195737087` showed that both zero-letter BHSA slots are genuine annotation-bearing nodes rather than exporter omissions:

- node `150439`, verse order 27: lexeme present, `sp=art`, `pdp=art`, `languageISO=hbo`, phrase `737331`, clause `455846`, no qere, no bridging morphology, no orthographic/consonantal value;
- node `150445`, verse order 33: lexeme present, `sp=art`, `pdp=art`, `languageISO=hbo`, phrase `737335`, clause `455847`, no qere, no bridging morphology, no orthographic/consonantal value;
- OSHB still has no empty-signature records;
- the complete normalized OSHB/BHSA consonantal verse streams remain identical.

Resolution:

- preserve those BHSA nodes as `ANNOTATION_ONLY_TARGET_NODE` records;
- do not delete them from the BHSA annotation graph;
- do not fabricate an orthographic TextSegment or attach them automatically to a neighbouring OSHB token;
- exclude them only from the orthographic span alignment;
- allow only text-bearing BHSA nodes into the conservative consonantal crosswalk;
- keep any unclassified empty node fail-closed as `NEEDS_REVIEW`;
- make Database Spike 001 explicitly test that an AnalysisNode may have zero segment memberships while retaining framework features and graph relations.

Before creating the repository commit:

- current upstream repository heads and frozen BHSA/bridging 2021 directories were inspected;
- the registry draft passed Draft 2020-12 JSON Schema validation;
- all three corpus Python adapters passed Python syntax compilation;
- the OSHB exporter was exercised against a synthetic namespaced OSIS verse and preserved source Hebrew, lemma, morphology, provider ID and verse order;
- Text-Fabric `13.1.0` was verified as the current PyPI release and supports pinned/local Text-Fabric data workflows;
- independent review found that BHSA uses `Samuel_I`, not `1_Samuel`, as the section book label and corrected the adapter/docs;
- independent review also found that ETCBC bridging 2021 must not be treated as a direct mapping from this project's current OSHB commit to BHSA nodes because the bridge artifact does not embed that current immutable OSHB input pin;
- a dedicated `Corpus source smoke` workflow was therefore added to fetch all three pinned sources and execute the OSHB exporter, BHSA exporter, and conservative crosswalk on 1 Samuel 16:7.
- first real smoke run `37141481533` proved all three pinned-source downloads and cache hashes, and exported 25 OSHB words, but failed at BHSA Text-Fabric load with `KeyError: g_cons`;
- inspection of BHSA 2021 `otext.tf` showed that Text-Fabric format initialization references a closure of transliterated/UTF-8 word, consonantal, trailer, qere, and lexeme features even when the exporter requests only a narrower analysis subset;
- the BHSA acquisition subset is expanded to that exact format dependency closure, preserving the bounded-download design; the failed smoke is retained as validation evidence and the workflow must pass on the corrected PR head.

Corpus source smoke run `37196120231` PASS proved the pinned acquisition/export/crosswalk path on the pre-sync head. The synchronized PR head must rerun `contracts`, `state-and-changelog`, and `Corpus source smoke` against latest `main` before squash merge. The merged Database Spike 001 already proves the PostgreSQL integrity slice with controlled fixtures; real-corpus import into that schema remains pending and is the next integration gate.


## 2026-10-04 — Add P1 fixture-backed release-pinned Passage serving shell

### Push intent

Implement P1-VS-001A–F as the first executable Product Serving shell without binding the UI to physical database tables or freezing the rich PassageExperience DTO.

### Why

The Core contract gates permit implementation work, while DB-0 and real publication/storage evidence remain pending. Phase 1 explicitly permits fixture releases, requires public fixture responses to be release-pinned, and requires Study/Research to share the same ResearchRelease. A server-side adapter boundary lets the serving shell be exercised now without creating a second data contract or pre-empting database decisions.

### What changed

- added `apps/web` with Next.js App Router and strict TypeScript;
- added domain ports/services for release resolution, passage reads and experience capabilities;
- added server-only fixture adapters that read and runtime-validate the existing canonical v1.1 fixture chain;
- added current and pinned passage APIs plus the current-release endpoint and capability endpoint;
- added current passage navigation that resolves the current fixture release once and redirects to the pinned release route;
- added a minimal Study/Research switch that retains the same release/reference/reference-system identity;
- added visible fixture/non-production labelling, ResearchRelease and ReferenceSpan display, and explicit later-phase placeholders;
- added distinct invalid-reference, missing-reference-system, invalid-release, missing-release, invalid-mode, contract-violation and temporary-unavailability states;
- added boundary checks prohibiting app/feature imports from adapters, DB/ORM/auth/cloud SDK dependencies, and SQL statement text in the scoped web implementation;
- after the first branch-only lockfile generation, narrowed lint tooling to that deterministic boundary scanner rather than carrying an unnecessary framework lint preset and its transitive dependency surface;
- added unit, HTTP integration and Playwright E2E/visual-state tests;
- added a feature-branch-only validation workflow to generate the npm lockfile artifact and, once tracked, run full acceptance;
- did not add database migrations, Supabase/PostgreSQL integration, ORM, auth, cloud credentials, publication worker, CorpusQuery, translation workbench, annotation storage, rich PassageExperience DTO or A1–A4 semantic changes.

### Intended effect

Provide a verifiable release/reference-aware serving shell whose fixture adapter can later be replaced by a DB-0-backed Serving adapter without changing page/business logic or treating provider identifiers as canonical reference identity.

### Validation

Feature-branch workflow run `37180410353` succeeded and produced the initial npm lockfile artifact. Dependency review then found that the framework lint preset introduced unnecessary transitive tooling for this narrowly scoped shell. The preset was removed while strict TypeScript and the deterministic source/import/SQL/SDK boundary scanner were retained.

The subsequent full local run exposed two real blockers that the first unit test did not cover: Ajv schema compilation received an `unknown` TypeScript value, and PassageRequest compilation could not resolve its external PassageLocator `$ref`, causing the current-release endpoint to return 503 throughout the HTTP integration test. The repair:

- tracks the regenerated npm lockfile;
- types parsed contract JSON as an Ajv schema;
- pre-registers canonical `$id` schemas before validator lookup/compilation;
- adds a regression test for PassageRequest external-reference resolution;
- narrows dynamic contract file access to `contracts/v1.1`, removing the production-build whole-repository trace warning;
- synchronizes Next.js 16 generated TypeScript declarations/settings and disables unwanted agent-rule file generation;
- ignores generated web build, dependency, report and incremental-build paths;
- excludes dependency, build, test-report, coverage, cache and VCS trees from the repository secret scan after generated Next.js/dependency files caused false alarms in the combined validation run.

After repair, local contract validation, Core/Research Pro OpenAPI validation, deterministic lockfile regeneration, `npm ci`, typecheck, boundary lint, eight unit tests, HTTP integration, and production build pass. Playwright could not install Chromium locally because the permitted download path returned a zero-byte invalid archive; the branch workflow must therefore run Playwright E2E/visual capture and the complete suite before merge. Visual QA must then be inspected for ready, invalid-mode, missing-reference and missing-release states.
## 2026-10-04 — Close inactive Serving candidate visibility leak

### Push intent

Repair a post-merge Database Spike 001 publication-boundary defect discovered by adversarial review of the actual RLS policies rather than accepting the earlier green CI result as sufficient.

### Why

The architecture requires publication visibility to be atomic: a candidate ResearchRelease may be fully materialized in Serving while inactive, but public clients must observe only the complete old release or the complete new release. The merged migration enabled RLS yet used `USING (true)` on release-scoped Serving tables. Because anon/authenticated also had direct SELECT grants, a caller who knew a candidate release or payload identifier could read materialized unpublished rows even though the PRODUCTION pointer had not moved.

### What changed

- changed `serving.release_is_published()` and `serving.component_is_published()` into narrowly scoped SECURITY DEFINER predicates with a fixed `pg_catalog, serving` search path;
- granted anon/authenticated EXECUTE only on those boolean publication predicates;
- kept canonical reference spans and channel definitions publicly readable;
- gated public corpus projections and semantic-set members on participation in at least one published release;
- gated ResearchRelease rows, release components, channel pointers, passage analyses, evidence packets/items, assertions and assertion/evidence links on a committed `PUBLISHED` event;
- added adversarial anon tests proving that fully materialized release 2, its components, its candidate evidence packet and its release-pinned corpus query are invisible before publication;
- added positive regression tests proving those release-scoped rows become visible after the publication transaction succeeds.

### Intended effect

Inactive candidate materialization remains possible, but it is no longer equivalent to public visibility. The database now enforces the architecture's old-release/new-release atomic visibility boundary even for direct table/API access, not only for clients that voluntarily use `current_release`.

### Validation

This change must pass the blank PostgreSQL 17 Database Spike workflow, Contract validation, and Project governance on the new PR head. The negative pre-publication tests are expected to fail against the previously merged migration and pass only with the publication-gated RLS policies.


## 2026-10-04 — Database Spike 001 executable PostgreSQL vertical slice

### Push intent

Move the project from contract-only database design into a reproducible PostgreSQL implementation spike that rejects invalid scholarly states at relational, rights, RLS, publication, and release-serving trust boundaries.

### Why

CORE_SPIKE_V1_1 permits Database Spike 001, but earlier evidence was synthetic contract validation. The next gate requires real DDL, FK/check/trigger behavior, RLS/grants, deterministic corpus execution, publication failure injection, and independent review against the four-plane architecture.

No remote Supabase project is modified. The connected account exposes only one inactive generically named project, while the repository contains no project ref proving that it is this product's target.

### What changed

- added `database/migrations/001_database_spike_001.sql` and a clean PostgreSQL 17 CI harness;
- implemented Authoring, Serving, Workspace, and Publication Control schemas;
- enforced framework/layer and text-stream integrity, semantic-set/construction/rule/translation dependencies, ResearchIssue/ResearchPosition versioning, rights snapshots, public evidence, release/channel objects, and Workspace RLS;
- materialized Serving-owned research-object, reference, corpus, semantic-set, release, and evidence projections so public runtime does not depend on Authoring;
- added PostgreSQL catalog assertions rejecting any Serving FK/function dependency on Authoring;
- added exact rights-subject binding for public excerpts;
- added shared-PK subtype/object-type enforcement;
- added composite Workspace project-owner FKs so a user cannot attach owned child rows to another user's project;
- added typed CitationLocator validation compatible with the v1.1 locator contract;
- added release/component projection immutability after PUBLISHED;
- made first publication append the PUBLISHED event and move the channel pointer in the same transaction;
- changed corpus pagination to use a publication-projected canonical reference sort key rather than UUID order;
- added an Authoring-offline test that temporarily renames the Authoring schema and requires anonymous current-release/corpus-query reads to continue from Serving projections;
- kept public runtime AI/BYOK architecture untouched and introduced no model-provider credential.

### Executable findings and corrections

1. Run `37142212945`: migration PASS; seed exposed stable/current-version insertion ordering. Stable rows now insert with null current pointer, version rows follow, then the pointer is set.
2. Run `37142329963`: migration/seed PASS; test used unsupported `min(uuid)`. Assertion changed to deterministic ordered selection.
3. Run `37142397559`: suite reached RLS; disposable test helper lacked role permission. Only the temporary helper grant was added.
4. Run `37142489342`: disposable PL/pgSQL delimiter malformed. Named dollar delimiters adopted.
5. Run `37142607945`: first full harness PASS, but independent architecture review rejected the green result because Serving still depended on Authoring. This was treated as a failed architecture gate, not accepted because CI was green.
6. Run `37143183450`: first Serving-isolation migration exposed delimiter serialization in new Serving rights validators. Named delimiters fixed it.
7. Run `37143277018`: restricted SECURITY DEFINER search path could not resolve hashing; hashing moved to PostgreSQL 17 core SHA-256 without widening search_path.
8. Run `37143374434`: final Authoring-RLS anonymous block had the same delimiter defect. Independent review also found that public evidence could borrow an ALLOW snapshot for another subject; the trigger now requires exact subject identity.
9. Run `37143497384`: Serving-isolation migration and seed PASS; wrong-subject test block delimiter failed and was corrected.
10. Run `37143591152`: no-Serving-FK-to-Authoring catalog assertion PASS; function scan accidentally called `pg_get_functiondef()` on aggregate rows. The scan now targets ordinary functions only.
11. Run `37143685280`: pre-final-review Database Spike harness PASS, with required Contract validation `37143685279` and Project governance `37143685263` also PASS.
12. Run `37192756787`: later replacement-token editing corrupted SQL dollar/regex text. This was classified as serialization corruption rather than a domain-rule failure.
13. Run `37192890177`: migration failed because a duplicate/partial 26K SQL tail had been appended after a complete first `COMMIT;`. Structural comparison proved all 58 tail CREATE objects already existed before the commit; the tail was removed and CI now statically requires exactly one `COMMIT;` with no trailing SQL.
14. Run `37195521246`: migration/seed PASS; the cross-issue ResearchPositionVersion negative test was rejected by shared-PK registration before reaching the intended composite FK. The test now registers the synthetic version object inside the expected-failure subtransaction.
15. Run `37195662708`: migration/seed PASS; the editorial-emendation negative test was likewise rejected by missing shared-PK registration before reaching the intended adopted-reading CHECK. The test now registers the synthetic TranslationSourceBasis first so the basis-kind CHECK is the required rejecting boundary.
16. Run `37195807481`: migration/seed PASS; the CitationLocator negative case was rejected by the already-PUBLISHED release-1 evidence immutability guard before the locator CHECK. Review showed the same isolation risk in wrong-operation rights, wrong-subject rights, and immutable-hash cases. All four now use a candidate evidence packet on unpublished release 2 so each test must reach its intended invariant.
17. Run `37195991129`: full Database Spike 001 PASS from a blank PostgreSQL 17 database, including static transaction-boundary guard, migration, seed, adversarial relational/RLS/rights/publication suite, Authoring-offline anonymous Serving reads, and query-plan probe. Required Contract validation `37195991128` and Project governance `37195991176` also PASS on the same head.

### Independent critical review

A green SQL harness is not sufficient by itself. Independent review identified and corrected load-bearing gaps that ordinary happy-path execution did not prove:

- Workspace child ownership is tied relationally to project ownership;
- shared-PK subtype rows enforce expected research-object type;
- CitationLocator is locator-specific rather than generic JSON;
- PUBLISHED releases cannot accept late payload/projection inserts;
- initial PUBLISHED event and channel-pointer move are one publication transaction;
- pagination uses release-pinned canonical reference order;
- public Serving has no FK/function dependency on Authoring;
- anonymous serving reads are tested while Authoring is unavailable by schema name;
- CHANGELOG corruption/duplication from automated replacement-token editing is removed rather than retained as false history.

### Intended effect

A green final head means the PostgreSQL implementation rejects the tested invalid states and the public Serving/Workspace runtime can be separated from Authoring at the relational/function boundary. It still does not prove remote Supabase deployment, Data API exposure, production corpus scale, the full CorpusQuery compiler, real OSHB/MACULA/BHSA ingestion, or every CORE_FREEZE gate.

### Validation

The reviewed PR head passed all three workflows:

- `Database Spike 001 / postgres-spike`: run `37195991129` PASS;
- `Contract validation / contracts`: run `37195991128` PASS;
- `Project governance / state-and-changelog`: run `37195991176` PASS.

Because this evidence summary itself creates a newer head, the latest exact head must pass the same three workflows again before merge. The merge gate is the current GitHub check state, not a permanently hard-coded “final run” identifier.


## 2026-10-04 — Re-verify live repository protection and PR enforcement

### Push intent

Perform a fresh live audit of repository governance after branch protection was enabled and subsequent protected-main work was merged.

### Why

The repository already recorded `REPO-GOV-001/002/003` as PASS, but the canonical verification evidence still centred on earlier main commits. Because repository rulesets are external live state, their correctness should be periodically re-read rather than inferred from repository prose.

### What changed

- re-read the live `Protect main` ruleset and confirmed:
  - enforcement active on the default branch;
  - no bypass actors;
  - deletion blocked;
  - non-fast-forward/force-push blocked;
  - linear history required;
  - PR required;
  - required approvals = 0;
  - review conversation resolution required;
  - squash-only merge;
  - strict required checks `contracts` and `state-and-changelog`;
- re-read repository merge settings and confirmed squash enabled, merge-commit/rebase disabled, update-branch enabled, and merged branches auto-deleted;
- confirmed latest audited main `3d2dc4d8f07b67f3be44f9fedc69a60acb775405` is associated with PR #6;
- confirmed PR #6 head passed both required checks before merge and the post-merge main commit also passed both checks;
- audited recent protected-main history and confirmed PR provenance for PR #4, PR #5, and PR #6;
- refreshed the live-governance verification record, repository-governance contract, canonical freeze-gate evidence, README validation index, and living project state;
- retained repository visibility as public observed state without changing it.

### Intended effect

Keep the repository's canonical governance evidence synchronized with actual GitHub enforcement and prove that the ruleset is not merely configured but is being used by recent main-branch changes.

### Validation

This PR must itself pass:

- `contracts`;
- `state-and-changelog`;

against latest `main` before squash merge. Post-merge main checks will be re-read as the final verification.



## 2026-10-04 — Adopt production-verified Pastoral Studio scholarly retrieval/RAG method

### Push intent

Make the private Hebrew-Bible Research Compiler use the scholarly retrieval method actually observed in the deployed Pastoral Studio Academic Biblical Study workflow, while preserving this project's stronger research-grade database and publication controls.

### Why

Earlier architecture correctly preserved the Sacred Studies Text × Topic × Lens, Librarian, synthesis, and review ideas, but one state record still relied on a static-code conclusion that several provider helpers were not wired into runtime.

A production browser run against the deployed Pastoral Studio showed a real multi-source retrieval phase before model synthesis, including Sefaria, Scite, CORE, OpenAlex, Crossref, and Open Library / Internet Archive, with explicit degraded-mode fallback when CORE authentication failed.

### What changed

- added `architecture/pastoral-studio-runtime-scholarly-rag.md` as the active retrieval-orchestration reference;
- defined Pastoral Studio parity as behavioral/method parity, not code copying;
- formalized source-specialized parallel retrieval before Librarian synthesis;
- retained OpenAlex, Semantic Scholar, CORE, Crossref, and Scite as the required scholarly-provider ensemble;
- documented Sefaria and Open Library / Internet Archive as auxiliary source-specialized retrieval routes;
- formalized explicit degraded-mode fallback and prohibited model-memory substitution for failed providers;
- formalized normalization, Work/Edition deduplication, access/rights resolution, enrichment, Librarian dossier, candidate claims, counterevidence, review, LiteratureSnapshot, ResearchBuild, and ResearchRelease;
- updated the machine-readable scholarly research method, active architecture, living state, README, and contract validation.

### Intended effect

Future GPT/Codex/Gemini/Claude database builds should search academic material using the same practical retrieval pattern that proved operational in Pastoral Studio, but persist and govern the results as research-grade data instead of immediately turning provider output into an unversioned answer.

### Validation

- contract validation asserts the production-runtime reference, capability-routed fan-out, degraded-mode policy, Librarian-after-retrieval ordering, model-memory prohibition, and auxiliary source routes;
- existing provider-ensemble, model-neutrality, rights, schema, OpenAPI, and governance checks remain mandatory;
- GitHub PR checks are the merge authority.

## 2026-10-03 — Post-protection governance consistency audit

### Push intent

Independently re-check the live GitHub protection state and reconcile every current governance authority after the `Protect main` ruleset and governance-sync PR were already in place.

### Why

The live repository, freeze checklist, PROJECT_STATE, repository-governance contract, README, and closed issue #1 all reported governance as enforced. However, `architecture/reviews/2026-10-03-panel-contract-closure.md` is still registered as a current validation record and retained one sentence saying live branch protection was not enabled. That made the validation chain internally inconsistent even though the live GitHub configuration itself was correct.

Historical CHANGELOG entries that recorded the repository before protection was enabled are valid historical evidence and must not be rewritten as though protection had always existed.

### What changed

- re-read live `main` metadata and confirmed `protected = true`;
- re-read ruleset `Protect main` (ID `24409248`) and confirmed enforcement remains active on the default branch;
- re-confirmed PR-only updates, `0` required approvals, conversation resolution, squash-only merge, strict latest-main checks, no bypass actors, linear history, deletion protection, and force-push/non-fast-forward protection;
- re-confirmed required GitHub Actions checks are `contracts` and `state-and-changelog`;
- re-confirmed post-merge push runs for governance-sync commit `14cb67e9c70fa92c0dc629c0e8efcf6e4dc5659c`: Project governance `37102653272` PASS and Contract validation `37102653290` PASS;
- corrected the stale branch-protection sentence in the current panel review and pointed it to the later live-governance verification record;
- appended an independent post-sync re-audit section to the canonical live-governance verification;
- updated PROJECT_STATE revision and latest push intent;
- deliberately left older CHANGELOG PENDING/unprotected-state statements untouched because they describe historical state rather than current authority.

### Intended effect

All current governance authorities now agree with actual GitHub enforcement while the repository retains an honest history of the earlier unprotected period. Future agents should not misread an old panel-review sentence as the current branch-protection state.

### Validation

- live GitHub ruleset and branch metadata were read directly during this audit;
- canonical current-state files were checked individually rather than relying on GitHub search-index snippets;
- freeze checklist already had `REPO-GOV-001/002/003` PASS and required no change;
- issue #1 was already closed as completed and required no change;
- first PR-head Project governance run `37103129603`: PASS;
- first PR-head Contract validation run `37103129599`: PASS;
- independent diff review found one documentation-structure defect: the now-resolved governance item still sat under a “Remaining open items” heading;
- second reviewed PR-head Project governance run `37103197575`: PASS;
- second reviewed PR-head Contract validation run `37103197574`: PASS;
- the final merge gate is the latest GitHub-required `contracts` and `state-and-changelog` result against latest `main`; no CHANGELOG entry claims a permanently “final” run ID because editing this record itself creates a newer head.

## 2026-10-03 — Live repository protection enabled and verified

### Push intent

Synchronize repository governance documents with the live GitHub `Protect main` ruleset after repository-admin protection was enabled.

### Why

The repository previously documented branch protection as an unresolved operational gap:

- `main protected = false`;
- no repository ruleset;
- required CI existed but did not prevent direct updates.

Live GitHub state has now changed. Leaving `REPO-GOV-001/002`, PROJECT_STATE, issue #1, and repository-governance prose in PENDING state would make the repository's canonical governance record false.

### What changed

- verified live `main protected = true`;
- verified active repository ruleset `Protect main` (ID `24409248`);
- verified pull requests are mandatory with `0` required approvals;
- verified unresolved review conversations block merge;
- verified squash is the only allowed merge method;
- verified required GitHub Actions checks are `contracts` and `state-and-changelog`;
- verified strict required-status-check mode is enabled, requiring validation against latest `main`;
- verified branch deletion and non-fast-forward/force-push updates are blocked;
- verified linear history is required;
- verified there are no bypass actors;
- verified CODEOWNERS remains present;
- recorded current repository visibility as public without changing it;
- changed `REPO-GOV-001` and `REPO-GOV-002` from PENDING to PASS;
- retained `REPO-GOV-003` as PASS;
- replaced stale pending-state text in `architecture/repository-governance.md` and `PROJECT_STATE.md`;
- added `architecture/reviews/2026-10-03-live-repository-governance-verification.md` as the auditable live-state record;
- updated README/manifest to expose the verified governance state.

### Intended effect

The repository's canonical state now matches actual GitHub enforcement. Contributors can work independently without mandatory mutual approval, but ordinary changes cannot bypass pull requests, latest-main validation, required CI, conversation resolution, or squash-only protected-main history.

### Validation

- live GitHub ruleset API verified ruleset ID `24409248`, enforcement `active`, default-branch target, no bypass actors;
- live branch API verified `main protected = true`;
- latest `main` commit `7923a56e9bce4046363834071ba625c28db2980b` had successful `contracts` and `state-and-changelog` GitHub Actions checks before this governance-sync PR;
- this PR must itself pass the same required checks before merge;
- after merge, issue #1 should be closed as completed and main push checks re-verified.

## 2026-10-03 — Independent contract-closure panel

### Push intent

Critically evaluate three architecture critique sets with independent academic, database/API, rights/security, Research Pro, and engineering/governance review lenses; accept only changes that close real load-bearing gaps; then independently re-review the modified contracts before Database Spike 001.

### Why

The pre-spike v1.1 contract was already strong, so indiscriminately implementing every critique would have increased ontology and API surface without proving scholarly or engineering value. The panel therefore separated true contract holes from production hardening, deferred work, and over-design.

### What changed

- added explicit ReferenceSystem-aware PassageLocator and PassageRequest contracts;
- separated normalized CorpusQuery meaning from execution cursor/page state;
- made corpus page-count versus exact-total semantics explicit;
- added immutable TranslationSourceBasis and versioned TranslationPolicyVersion while reusing the existing RuleVersion engine;
- required TranslationDecision to pin exact source basis and policy version;
- removed the first-pass undefined TargetLanguageProfile dependency;
- kept PassageCore content extensible until the serving projection is actually frozen;
- kept passage-level TranslationSourceBasis out of top-level release-manifest enumeration to avoid whole-Bible manifest explosion;
- hardened RightsDecisionSnapshot so UNKNOWN_RESTRICTIVE resolves DENY, final snapshots cannot remain UNKNOWN, conditions/obligations are typed, and permissive public evidence requires the right snapshot/hash state;
- added typed CitationLocator with locator-specific required identity;
- tightened DiscoveryRecord persistence rights, ProductEntitlement provenance vocabulary, ResearchPositionVersion issue-version framing, and commentary assertion provenance;
- clarified publication visibility atomicity across separate Authoring and Serving stores;
- defined Database Spike 001 as an adversarial scholarly-integrity vertical slice rather than a table-creation demo;
- added CODEOWNERS/repository-governance documentation and pinned GitHub Actions used by panel-modified workflows to immutable SHAs;
- synchronized the concurrent multi-provider scholarly discovery and Sacred Studies research-method work from latest main rather than overwriting it;
- extended contract validation with new positive/negative fixtures, local-ref checks, vocabulary drift checks, provider/method checks, and second-pass adversarial invariants.

### Intended effect

Database Spike 001 can now test a smaller, more coherent contract surface in which the most important scholarly identities, rights outcomes, query semantics, translation dependencies, release boundaries, and governance assumptions are explicit without prematurely freezing every future API or bibliographic detail.

### Validation

- earlier clean PR Contract validation run 37099589859 passed after the first closure pass;
- later Project governance run 37099830333 correctly failed because the new mandatory PROJECT_STATE/CHANGELOG rule landed concurrently on main and the panel branch had not yet adopted it;
- the branch synchronized that governance baseline and updated both living governance documents;
- Contract validation runs 37100959518, 37101013187, and 37101156060 passed during successive review rounds;
- Project governance runs 37100959521, 37101013160, and 37101156012 passed during successive review rounds;
- the final independent adversarial review found no further load-bearing domain-model defect;
- `architecture/reviews/2026-10-03-panel-contract-closure.md` is the canonical panel adjudication record;
- live branch protection remains the only unresolved repository-governance item and is tracked in issue #1.

## 2026-10-03 — Sacred Studies method parity + mandatory push governance

### Push intent

Make the Hebrew-Bible research database use the full Sacred Studies scholarly-search/research method while correcting defects, and make project state/version history mandatory on every future push.

### Why

Two risks were identified:

1. `Sacred Studies-style` had been documented mainly as a provider-aggregation concept, without fully pinning the exact query/search/dossier/synthesis/review method.
2. Product intent and architecture were well documented, but there was no mechanically enforced rule requiring every push to update a living repository-state record and a human-readable reasoned change history.

### What changed

- added `architecture/sacred-studies-research-method.md`;
- added `contracts/v1.1/scholarly-research-method.json`;
- defined Text × Topic × Lens search matrix;
- preserved concise English academic-query generation, standard English book naming, and 3-6 term/phrase query design;
- preserved all-era + modern scholarship search policy, replacing stale 2015-2025 hard-coding with a rolling recent window;
- preserved academic-source prioritization and zero-hallucination bibliography rule;
- preserved Librarian dossier -> synthesis -> critical review/revision loop;
- preserved 88/100 review threshold and maximum three attempts;
- corrected Sacred Studies defects: invalid review output cannot auto-pass; provider failure cannot fall back to model-memory evidence;
- documented that current Sacred Studies provider helper wiring is incomplete and therefore is not copied literally;
- added `PROJECT_STATE.md` as mandatory living repository state;
- added `CHANGELOG.md` as mandatory reasoned push history;
- added `AGENTS.md` with read-before-change and update-before-push rules;
- added GitHub Actions governance check requiring every push/PR to modify both `PROJECT_STATE.md` and `CHANGELOG.md`;
- updated README, charter, manifest, discovery architecture, and contract validator to point to/enforce the new method/governance.

### Intended effect

Any future GPT/Codex/Gemini/developer build should be able to reconstruct both the product's current state and the exact scholarly search method without relying on chat history. No future push should silently change architecture without also updating project state and explaining why.

### Validation

- project-governance workflow introduced in this push;
- contract validator extended to verify Sacred Studies-derived method parameters;
- existing Core and Research Pro OpenAPI validation remains required;
- post-push GitHub Actions result is the authoritative execution record.


## 2026-10-03 — Panel contract closure + adversarial re-review

### Push intent

Close the remaining load-bearing architecture and machine-contract gaps before Database Spike 001 without expanding v1.1 into another speculative redesign.

### Why

Independent review of the active v1.1 architecture found several real pre-spike defects: ambiguous human-reference resolution, a corpus-query cursor response without an executable page-request contract, no explicit adopted source-text state for official translation decisions, no versioned project translation policy, permissive rights snapshot edge cases, under-specified citation locators, and several Research Pro/versioning/governance inconsistencies.

The same review also rejected lower-value proposals that would over-expand v1.1 before real PostgreSQL/corpus evidence, including a large bibliographic redesign, full TEI/OCR ontology work, another BYOK architecture layer, and exhaustive API error/pagination standardization.

### What changed

- added ReferenceSystem-aware PassageLocator/PassageRequest contracts while keeping canonical ReferenceSpan identity primary;
- added CorpusQueryExecutionRequest with cursor/page state separate from normalized query semantics;
- clarified page versus exact total match-count semantics;
- added immutable TranslationSourceBasis for the exact textual state translated;
- added versioned TranslationPolicy that reuses existing RuleVersion objects rather than creating a parallel rule engine;
- required TranslationDecision to pin exact source basis and policy version;
- made RightsDecisionSnapshot fail closed and typed conditions/obligations;
- rejected UNKNOWN as a final resolved rights outcome;
- typed CitationLocator and required locator-specific identity;
- required rights snapshot for published excerpts and content hash for immutable evidence;
- pinned ResearchPositionVersion to exact ResearchIssueVersion;
- tightened discovery persistence/rights coupling, entitlement vocabulary, commentary assertion provenance, and release component semantics;
- clarified publication visibility atomicity for separate Authoring/Serving databases;
- defined Database Spike 001 as an adversarial scholarly-integrity vertical slice with relational, RLS, publication, corpus, rights and textual-state attacks;
- added CODEOWNERS and repository-governance contract;
- pinned GitHub Actions dependencies used by contract/project governance to immutable commit SHAs;
- synchronized all changes with the newer multi-provider scholarly-discovery and Sacred Studies-derived research-method work already added to main;
- added/expanded positive and negative fixtures plus schema, vocabulary, local-ref and semantic validation.

### Intended effect

Database Spike 001 can now test a narrower, more explicit set of scholarly invariants instead of discovering preventable domain/API contradictions mid-migration. The project retains extension space where the serving DTO is not yet frozen and avoids inventing new ontologies before real implementation evidence.

### Validation

- six-role panel review used separate academic/method, relational-data, API/contract, rights/security, Research Pro/bibliography, and engineering/governance lenses;
- first clean PR Contract validation run 37099589859 passed before the second adversarial review;
- subsequent review corrected over-constraint in PassageCore, incomplete CitationLocator semantics, a dangling target-language-profile dependency, ambiguous source-basis evidence identity, UNKNOWN final rights decisions, and ambiguous non-exact totals;
- substantive closeout Contract validation run 37101013187 passed;
- substantive closeout Project governance run 37101013160 passed;
- CORE-SPIKE-012/013/014 are therefore marked PASS with explicit CI evidence;
- the panel adjudication record is stored at `architecture/reviews/2026-10-03-panel-contract-closure.md`;
- merge is allowed only when the latest PR Contract validation and Project governance runs are both successful; the PR checks are the authoritative final gate rather than a hard-coded “last run” ID in this changelog;
- live GitHub branch protection remains unresolved and is tracked in issue #1 rather than falsely marked complete.


## 2026-10-03 — Repository governance gate registry correction

### Push intent

Repair a post-merge source-of-truth inconsistency found by the final independent read-only review.

### Why

`architecture/repository-governance.md` explicitly required live branch-protection/ruleset state to be tracked as `REPO-GOV-001/002` in the canonical freeze checklist, but those gate rows were absent after PR #2 merged. The operational state itself was already documented correctly as pending, but the canonical gate registry did not contain the promised IDs.

### What changed

- restored `REPO-GOV-001` for PR + required Contract validation enforcement on `main`;
- restored `REPO-GOV-002` for force-push/deletion protection;
- recorded both as PENDING using live GitHub evidence: `main protected = false`, repository rulesets empty;
- recorded `REPO-GOV-003` as PASS because `.github/CODEOWNERS` exists;
- updated PROJECT_STATE to distinguish Database Spike readiness from repository production-governance readiness.

### Intended effect

The governance architecture, live repository state, and canonical freeze registry now say the same thing. Database Spike 001 remains unblocked, while branch protection is not falsely represented as complete.

### Validation

- PR #2 post-merge Contract validation push run `37101307953`: PASS;
- PR #2 post-merge Project governance push run `37101307963`: PASS;
- this follow-up PR must pass both latest PR checks before merge.


### Independent self-review correction

The first follow-up patch inserted the repository-governance gate table at an ambiguous Markdown anchor and accidentally displaced the `CORE_SPIKE_V1_1` profile heading. Independent PR diff review caught this before merge. The freeze checklist was rebuilt from current `main`, preserving the original Profiles taxonomy and adding a separate `## REPOSITORY_GOVERNANCE` gate section before the Core Spike gate table.
