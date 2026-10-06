# Repository Change Log

Every push/PR must update this file together with `PROJECT_STATE.md`.

Entries record **what changed, why, intended effect, and validation**. The Git commit itself supplies the immutable SHA/timestamp linkage.

## 2026-10-06 — Implement WB-2 rights-safe Serving candidate

### Push intent

Compile the accepted WB-1 whole-corpus Authoring result into the first real release-pinned public Serving projection while keeping unresolved public-rights sources fail-closed.

### Why

WB-1 proves complete relational ingestion, but it intentionally leaves real corpus rows out of Serving. The current Serving schema also lacks public text-segment projection, node-to-segment membership and a Serving-owned passage reference index. In addition, the PostgreSQL rights-obligation validator still expected an obsolete `type` key while the canonical RightsDecisionSnapshot v1.1 contract uses `obligationType`; leaving that drift in place would make an attribution-bound OSHB publication internally inconsistent.

### What changed

- added migration `002_wb2_serving_projection.sql` with Serving-owned text segments, node/segment membership, passage reference index, corpus attribution and operation-specific rights bindings;
- aligned PostgreSQL rights-obligation validation with the canonical v1.1 `obligationType` schema;
- require both storage and public-display RightsDecisionSnapshots before a public text segment can be materialized;
- require any ATTRIBUTION display obligation to match a materialized Serving attribution;
- keep the initial public projection OSHB-only under the pinned registry's `ALLOW_WITH_ATTRIBUTION` state;
- keep BHSA 2021 and ETCBC bridging out of Serving while their registry states require/deny public rights review;
- keep automatic cross-framework candidates Authoring-only;
- added `serving.get_passage_core(...)` as a release-pinned database passage read over Serving-owned data;
- added `publish_wb2_serving.py`, a strict WB-2 report schema and a two-phase verifier for inactive/public isolation and published behavior;
- added a clean-PostgreSQL WB-2 GitHub Actions workflow that reconstructs WB-CORPUS-001 and WB-1 from exact pins before compilation.

### Intended effect

WB-2 should prove that whole-Bible OSHB text can cross the publication firewall into an immutable ResearchRelease without granting public access to Authoring or accidentally publishing BHSA/bridging-derived data. The application reader remains fixture-backed until WB-3.

### Validation

Pending exact-head CI. Acceptance requires: migration success; accepted WB-1 parity; 39 configured books and 23,213 selected references in the Serving passage index; 306,785 rights-approved OSHB nodes/text segments and node-segment memberships; zero BHSA nodes, bridging features or non-OSHB text segments in Serving; invisibility before publication; atomic PRODUCTION publication; representative Genesis, 1 Samuel and 2 Chronicles reads; Authoring isolation; and post-publication projection immutability.


## 2026-10-05 — Implement WB-1 relational whole-corpus candidate

### Push intent

Consume the accepted WB-CORPUS-001 whole-source foundation in PostgreSQL Authoring and produce the relational coverage evidence required for `CORE-FZ-WB-002`.

### Why

WB-CORPUS-001 already proves complete pinned source export/reconciliation with 23,213 selected references, 306,785 OSHB words, 426,590 BHSA word nodes, 287,216 candidate mappings, 1,138 explicit unresolved references and zero silent reference loss. WB-1 therefore must not create a second competing source denominator. Its task is to prove that the relational model can preserve that accepted source foundation at whole-corpus scale.

Whole-corpus relational execution also invalidates the WB-0-only assumption that every AnalysisNode and member TextSegment have exactly the same ReferenceSpan: real phrase/clause structures can cover multiple reference atoms.

### What changed

- added a machine-validated selected `TANAKH_OSIS_39` CanonSystem for relational/navigation order while retaining WB-CORPUS-001 ReferenceSystem inventory as source-coverage authority;
- implemented `authoring.canon_systems` and `authoring.canon_books`;
- generalized AnalysisNode/TextSegment integrity to same-expression, same-book span containment;
- added an adversarial SQL regression for valid multi-atom containment and invalid out-of-span membership;
- added a streaming partitioner that hash-verifies the accepted WB-CORPUS-001 artifacts and reconciles exact provider-book codes before producing bounded per-book inputs;
- added a per-book transactional PostgreSQL COPY importer bound to the WB-CORPUS-001 build ID, source pins, reference-set hash and partition hashes;
- require all OSHB/BHSA provider word records to remain provider-scoped AnalysisNodes;
- preserve BHSA phrase/clause nodes, features, range spans, text-bearing memberships and graph edges;
- keep reviewed annotation-only and other empty-source BHSA states explicit rather than inventing orthographic text;
- keep grouped automatic cross-framework mappings non-canonical and preserve unresolved mappings as explicit research exceptions;
- reconcile PostgreSQL word-node, text-segment, phrase/clause, mapping and ReferenceAtom counts to source evidence by book;
- fail on missing configured source divisions, duplicate provider identities, OSHB source-surface loss, importer errors or source/database parity drift;
- keep real BHSA/bridging rows out of Serving;
- added a dedicated 60-minute WB-1 relational CI gate and machine-auditable artifact upload.

### Intended effect

A successful exact-head run will demonstrate that the accepted whole-source corpus survives relational ingestion without silent provider-record loss and without weakening framework identity or rights boundaries. Only then can `CORE-FZ-WB-002` be treated as satisfied.

### Validation

The first complete exact-head execution on PR #20 passed the whole-corpus relational workflow and all independent repository regressions. It observed 39/39 configured books, 23,213 selected/reference atoms, 306,785 OSHB word nodes, 426,590 BHSA word nodes, 253,203 BHSA phrase nodes, 88,131 BHSA clause nodes, 1,106,383 BHSA graph-membership edges, 469,484 bridging feature values, 287,216 grouped candidate mappings of which 103,987 are non-1:1, 6,409 reviewed annotation-only BHSA nodes, 79 explicit unclassified empty-source BHSA nodes, 1,138 unresolved cross-framework references, zero provider-ID duplicates, zero importer/parity failures, zero OSHB missing-surface records, and zero real-corpus Serving rows.

Independent review recomputed the 39-book totals and source/database arithmetic, confirmed the 1,138 unresolved references match WB-CORPUS-001 and remain mapping exceptions rather than silently dropped provider records, and confirmed WB-0 UUID identity compatibility. The synchronized hardening head `6ec515067f05a901667e4d1f783329f0ee46a53a` then reran every required gate successfully: WB-1 Relational Whole Corpus `37230153202`, Whole-Bible corpus foundation `37230153211`, Database Spike 001 `37230153245`, Corpus source smoke `37230153207`, P1 fixture shell validation `37230153208`, Contract validation `37230153210` and Project governance `37230153217`.

On that evidence, `CORE-FZ-WB-002` is accepted as PASS. This does not claim public whole-Bible Serving or reader completion: `CORE-FZ-WB-001` still requires navigation verification and `CORE-FZ-WB-003` remains WB-2/WB-3 work. The closeout documentation head must still pass latest-head CI before merge.


## 2026-10-05 — Prohibit GitHub Copilot consumption for project AI work

### Push intent

Make the repository-owner requirement explicit: this project must not intentionally consume GitHub Copilot quota, premium requests or equivalent Copilot AI credits. AI-assisted implementation, analysis, orchestration and code review are assigned to the project's ChatGPT workflow.

### Why

Recent WB-1 pull requests received automatic comments from `copilot-pull-request-reviewer`, including quota-limit notices. Live repository ruleset inspection showed no repository rule requiring Copilot review, while draft pull requests did not receive the automatic review. The owner has now disabled account-level Automatic Copilot code review and requires a repository-level policy so future project agents do not request or depend on Copilot.

The GitHub connector cannot independently read the user's account-level Copilot toggle, so the disabled account setting is recorded as owner-reported, not as verified repository metadata.

### What changed

- added `contracts/v1.1/github-ai-usage-policy.json` and its JSON Schema;
- set GitHub Copilot `authorized=false` and automatic code review `false`;
- prohibit Copilot PR review, Coding Agent, Autofix, Chat/code generation and any project operation consuming Copilot quota/premium requests;
- designate ChatGPT as the authorized project AI execution/review channel;
- preserve deterministic GitHub Actions, ordinary non-AI GitHub features and human collaboration;
- added the policy to `AGENTS.md` and `architecture/repository-governance.md`;
- extended contract validation to enforce the machine policy, required governance wording and absence of Copilot dependencies in `.github/workflows`.

### Intended effect

Opening or updating repository work must not deliberately trigger or rely on GitHub Copilot. Copilot output cannot become acceptance evidence. Existing GitHub Actions CI continues unchanged because it is deterministic infrastructure rather than Copilot AI usage.

### Validation

Contract validation must pass with the new policy fixture and semantic checks. Project governance/state-and-changelog must pass. After the owner disabled Automatic Copilot code review, the governance PR is opened normally and its review list is checked to confirm no new `copilot-pull-request-reviewer` review appears; absence on that PR is operational evidence, not a general API-level proof of the user setting.

## 2026-10-05 — Add WB-CORPUS-001 whole-Bible source foundation

### Push intent

Separate complete-source coverage/reconciliation from WB-1 relational ingestion so the next database change starts from a deterministic, machine-auditable whole-corpus input rather than another passage fixture or a provider book-count convention.

### Why

WB-0 now proves that the existing ontology and PostgreSQL schema can ingest the difficult 1 Samuel 16:7 OSHB/BHSA canary without inventing universal token identity. The remaining risk is scale: the repository still lacked one explicit full-provider build that establishes the expected reference set independently of exporter success, reconciles OSHB and BHSA across the complete pinned sources, and distinguishes explicit provider/mapping exceptions from silent reference loss.

Using successful exporter output as its own denominator would be circular validation. Likewise, treating a fixed 39-book or 24-book provider division count as a canonical coverage gate would collapse CanonSystem/ReferenceSystem distinctions the architecture already preserves.

### What changed

- added WB-CORPUS-001 as the source/build milestone between the accepted WB-0 canary and WB-1 relational whole-corpus ingestion;
- made OSHB/BHSA export scope explicit through mutually exclusive `--reference` and `--all` modes;
- kept the existing canary output shape intact so WB-0 pinned export/hash regression evidence remains valid;
- added an independent source-derived `OSHB_OSIS` reference inventory generated directly from the exact pinned OSHB XML/source manifest;
- labelled that inventory as a bootstrap ReferenceSystem snapshot rather than final project CanonSystem adjudication;
- added a one-command whole-corpus build that exports both providers, runs the conservative candidate crosswalk and creates a deterministic coverage manifest;
- made recognized annotation-only BHSA rows survive even when another empty node makes the same reference unresolved;
- added quiet whole-corpus unresolved logging without suppressing unresolved records;
- added a JSON Schema and positive contract fixture for the WB-CORPUS-001 manifest;
- added unit regressions for explicit whole-source export, dynamic provider division counts, silent-reference-loss failure and annotation-only preservation;
- added a dedicated full-source GitHub Actions workflow that fetches exact pins, builds the whole corpus, validates the manifest and rechecks the 1 Samuel 16:7 canary;
- documented that provider book-division counts are provenance metadata only and cannot substitute for selected ReferenceSystem coverage;
- kept PostgreSQL import, Serving projection and ResearchRelease publication out of this change.

### Intended effect

WB-1 can now generalize the already-proven WB-0 importer against one explicit source foundation. A provider/reference mismatch can remain a reviewable exception, but a reference cannot disappear silently between the selected reference inventory, provider exports and crosswalk while still being reported as complete.

The existing ReferenceSpan/TextSegment/AnalysisNode/AnnotationLayer ontology, grouped candidate mapping model, rights boundary and ResearchRelease publication model remain unchanged.

### Validation

- corpus unit tests cover explicit export scope, whole-source OSHB export, source-derived inventory, dynamic provider division counts, annotation-only preservation and silent-reference-loss rejection;
- the WB-CORPUS-001 manifest schema is registered in normal contract validation;
- the first exact-head full-source run completed the corpus build and generated `wb-corpus-8d40ce30066d83c2922a03b7`: 23,213 expected reference spans, 306,785 OSHB words, 426,590 BHSA nodes, 287,216 candidate mappings, 1,138 explicit unresolved references, zero silent reference loss, `gatePass=true`, status `COMPLETE_WITH_EXPLICIT_EXCEPTIONS`;
- that first run then exposed a CI dependency defect rather than a corpus defect: the generated-manifest validation step imported `jsonschema` although the workflow had installed only `requirements-corpus.txt`;
- the workflow now installs the repository-pinned contract validators through `requirements-contracts.txt` as well as corpus tooling, and it also runs on relevant pushes to `main` so the same full-source gate is repeated post-merge;
- WB-0's existing database workflow remains a regression gate and must continue to pass with the unchanged canary export shape;
- Project governance and Contract validation remain protected-merge requirements.

## 2026-10-05 — Implement WB-0 real OSHB/BHSA relational canary

### Push intent

Move from separate corpus-source smoke and synthetic PostgreSQL evidence to the first real-corpus relational ingestion canary, while preserving the whole-Bible roadmap and fail-closed publication/rights boundaries.

### Why

The repository could already fetch and export pinned OSHB/BHSA/bridging data and could independently prove relational constraints with synthetic fixtures, but it had not connected those two evidence paths. Real 1 Samuel 16:7 data also exposes a schema fact that the synthetic pairwise mapping fixture did not: an orthographic cross-framework claim may be 1:n, n:1 or n:m and cannot safely be flattened into pairwise node equivalence.

### What changed

- aligned the pairwise Authoring mapping table with the active `cross_annotation_mappings` contract;
- added grouped cross-annotation mapping tables with ordered source/target members, layer/span integrity, review state and canonicality;
- prohibited `CANDIDATE_AUTOMATED` grouped mappings from becoming canonical;
- added `scripts/corpora/load_wb0_postgres.py` to validate exact source pins/manifests/counts and load the pinned real canary;
- store separate OSHB and BHSA DigitalExpression, TextStream, CorpusRelease, AnnotationFramework and AnnotationLayer identities;
- preserve exact provider reference labels and provider-scoped node/word IDs;
- import 25 OSHB words and 34 BHSA words, with BHSA phrase/clause graph nodes and membership edges;
- preserve BHSA nodes 150439 and 150445 as annotation-only AnalysisNodes with zero TextSegment memberships;
- retain ETCBC bridging values as BHSA-node comparison features;
- retain project BODY_PART semantic membership as project authority rather than provider taxonomy;
- store 25 orthographic span candidates as grouped, non-canonical Authoring research data rather than false pairwise equivalence;
- add real relational assertions for counts, graph membership, candidate state, many-to-many behavior, invalid layer membership, accidental promotion and a mixed OSHB/BHSA semantic/clause query;
- add a second clean PostgreSQL CI job that fetches the exact pinned sources and runs the WB-0 canary independently of the existing synthetic spike;
- keep real BHSA/bridging data out of Serving because public/commercial rights remain unresolved;
- update the active corpus/database contract and implementation documentation to distinguish pairwise reviewed mapping from grouped n:m candidate evidence.

### Intended effect

WB-0 becomes executable evidence that the existing provider-scoped ontology can represent the real 1 Samuel 16:7 source data without inventing universal token identity or orthographic content. It also establishes the importer shape that WB-1 must generalize across the whole configured Hebrew Bible.

### Validation

The first PR execution reached the real PostgreSQL loader successfully and produced the pinned evidence: 25 OSHB words, 34 BHSA words, 32 text-bearing BHSA words, 2 annotation-only nodes, 22 phrases, 7 clauses, 90 graph-membership edges, 35 bridging feature values, 25 mapping groups, 7 non-1:1 groups, one BODY_PART target and zero unresolved references. Its SQL assertion run then exposed a test-boundary defect: the deliberately invalid wrong-layer member was correctly rejected by the mapping span/layer trigger before the expected composite FK fired. The test was narrowed to accept only those two intended rejection boundaries, and the exact real export hashes/counts were promoted into CI regression evidence.

A subsequent reviewed head passed the original synthetic PostgreSQL spike and the full WB-0 real-corpus job, including real source fetch/export, candidate crosswalk, PostgreSQL load, all relational assertions and the pinned evidence-report checks. Contract validation, Project governance, Corpus source smoke and P1 fixture-shell validation also passed on that reviewed head. The closeout documentation edit itself creates a new head, so protected merge still requires the same latest-head gates rather than treating those earlier run IDs as permanently final.

Merge is allowed only when Project governance, Contract validation, Corpus source smoke, the original synthetic Database Spike job, and the new `wb0-real-corpus-canary` PostgreSQL job all pass on the exact final PR head. WB-0 success does not satisfy the whole-Bible CORE-FZ-WB-002 gate.

## 2026-10-05 — Harden whole-Bible reference and corpus-adapter boundaries

### Push intent

Repair post-merge integration defects that the compact 1 Samuel 16:7 fixture did not expose, without presenting the existing source adapters or fixture web shell as a completed whole-Bible database product.

### Why

PassageLocatorV1 deliberately treats `referenceSystemCode` and `referenceLabel` as explicit but system-owned strings. The web shell nevertheless imposed an OSIS-like ASCII regex, rejecting valid labels such as `1 Samuel 16:7` before the declared ReferenceSystem could resolve them. The corpus crosswalk also treated any empty BHSA node with generic lexical/graph metadata as a known annotation-only node, although the real evidence only established a narrower Hebrew article shape. Separately, the Core OpenAPI did not document the implemented passage-route error surface. A repository-local Python virtual environment also reproduced another secret-scan false positive. The zero-word OSHB export defect was independently repaired on current `main` by PR #13 before this change was rebased.

### What changed

- made web passage labels and ReferenceSystem codes opaque after non-empty presence validation, leaving system-specific syntax to deterministic reference resolution;
- changed unknown human labels from synthetic 400-format failures to normal 404 lookup misses;
- narrowed automatic BHSA annotation-only classification to the evidenced unbridged Hebrew article shape with lexeme plus phrase/clause context;
- kept every other empty BHSA node fail-closed for review;
- retained PR #13's stronger zero-record OSHB behavior, including removal of an empty output artifact;
- added synthetic corpus adapter unit tests and made the corpus workflow run them before downloading sources;
- documented all implemented Core passage error statuses and codes in OpenAPI and made contract validation reject future drift;
- bound each implemented passage route to its exact status set and each status to its exact allowed error-code schema after independent review found that a shared union still permitted invalid status/code combinations;
- preserved the separate generic `NOT_FOUND` response used by non-passage analysis/evidence endpoints;
- excluded repository-local virtual-environment directories from secret scanning and Git tracking.

### Intended effect

Adding new biblical books, versification systems, or human label conventions no longer requires weakening an OSIS-specific web regex. Whole-corpus adapter runs cannot silently promote unfamiliar empty BHSA nodes as reviewed annotation-only structures. API clients can rely on the same error surface that the fixture implementation actually returns.

### Validation

- regression-first web unit test failed on the previous ReferenceSystem regex;
- regression-first corpus tests failed on generic empty-node classification and zero-word OSHB success;
- the strengthened contract validator failed on all eight over-broad passage status/code mappings before route-specific response schemas were introduced;
- the repaired focused web and corpus tests pass;
- full contract, OpenAPI, web, corpus-smoke and GitHub validation remain required on the exact PR head before merge.


## 2026-10-05 — Make whole-Bible base coverage the explicit execution baseline

### Push intent

Realign the repository's implementation ordering with the product's existing canonical whole-Hebrew-Bible scope: build a complete database-backed Bible research base first, then layer progressively deeper academic/Research Pro intelligence onto the same canonical targets.

### Why

The Charter already stated that the long-term scope is the whole Hebrew Bible, but the active staging/state documents could still be read as moving from a passage fixture shell directly into translation and then scholarly-provider work. Repeated 1 Samuel 16:7 validation also created a practical risk that future agents would mistake an acceptance canary for the product/content scope.

The intended product is a whole-Bible Hebrew/translation research edition as the base, with scholarly issues, literature review, commentary and recent discovery as top-up modules. A passage lacking a compiled academic dossier must still be a valid base-product passage.

### What changed

- added `architecture/whole-bible-base-product.md` as an active product-execution authority;
- made passage-specific fixtures explicit acceptance vectors rather than product scope;
- clarified in the Charter that the base whole-Bible product precedes and survives without Research Pro coverage;
- added a repository-agent scope guard to `AGENTS.md`;
- inserted Phase 2A for real whole-Bible corpus ingestion, coverage QA, release-pinned passage serving and database-backed reader before the existing translation workbench, now Phase 2B;
- aligned Study/Research and Research Pro phase ownership with Phase 2A/2B;
- added CORE-FZ-WB-001/002/003 whole-Bible coverage/import/serving gates;
- added validator checks requiring the new authority and whole-Bible gates;
- reordered PROJECT_STATE implementation priorities so whole-corpus database/reader work precedes scholarly-provider implementation;
- updated README/manifest so future contributors discover the same execution model.

### Intended effect

The existing v1.1 ontology, rights model, release model, Database Spike and Research Pro design remain intact, but implementation now has one unambiguous dependency path:

`real corpus -> whole-Bible database -> passage API/reader -> translation/comparison -> deterministic corpus analysis -> academic overlay`.

This prevents passage-fixture depth or Research Pro architecture from displacing whole-Bible base-product coverage.

### Validation

This PR must pass Contract validation and Project governance. The validator now fails if the Whole-Bible Base Product authority is removed from the active manifest or if any of CORE-FZ-WB-001/002/003 disappears. No runtime/database migration is introduced, so existing Database Spike, corpus-source and P1 fixture-shell workflows are regression evidence rather than new semantic acceptance gates.


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
