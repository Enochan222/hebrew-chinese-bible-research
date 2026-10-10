# Repository Change Log

Every push/PR must update this file together with `PROJECT_STATE.md`.

Entries record **what changed, why, intended effect, and validation**. The Git commit itself supplies the immutable SHA/timestamp linkage.

## 2026-10-10 — Bound deterministic Hebrew proximity-search feasibility

### Push intent
Respond to whole-Bible Corpus Lab product review by proving an actual executable lexical/morphological proximity candidate search while preventing an experimental matcher from being advertised as the canonical CorpusQuery engine.

### What changed
- Added a read-only OSHB NDJSON candidate evaluator for action lemmas, lamed-prefixed target lemmas, word-distance bounds, and word order within the same verse.
- Preserved source/pattern SHA-256 hashes, raw morphology, exact scoped counts and explicit candidate-only epistemic labels.
- Added regression tests covering gap boundaries, reverse order, attached prefix, verse boundaries, required verb morphology, duplicate/noncontiguous references, unsupported clauses and invalid distance.
- Added a dedicated no-AI GitHub Actions validation job and documented how this limited feasibility spike must eventually be replaced by the validated canonical CorpusQuery v1.1 pipeline.
- Explicitly distinguished lexical proximity, curated semantic-set membership and BHSA clause/dependency relationships; no current-case language model is permitted to decide corpus matches.

### Validation
Locally exercised the read-only algorithm on a synthetic OSHB-shaped word stream and ten edge-case tests; GitHub exact-head workflow acceptance remains required. Real pinned whole-Bible search and public Serving integration are not claimed.

## 2026-10-10 — WB-4 DB-1 post-merge integrity repair

### Push intent

Restore the complete reviewed PR #35 security fixes onto main after PR #34's squash merge (`2f50699ae9b5c9b927c51585af0c1d78ff8905c1`) deleted the former dependency branch and left the original companion PR conflicted. The replacement PR starts from the merged base and changes only the six relevant files.

### What changed and why

- enforce canonical `TRANSLATION` release component kind instead of noncanonical `TRANSLATION_WITNESS`;
- permanently guard bound display/storage RightsDecisionSnapshots from mutation even before publication;
- reject OLD-release to NEW-release update relocation of published translation witnesses and segments;
- prevent metadata-only/restricted parent downgrade while text children survive, independently hide child text via RLS and return empty child arrays via translation RPC;
- define the versioned `WB4_SEGMENT_BUNDLE_V1` byte serialization and independently computed SHA-256 of the exact ordered UTF-8 text, segment/stream IDs, ReferenceSpan and DigitalExpression;
- recompute segment and bundle hashes in candidate materialization and again at the first PUBLISHED lifecycle event;
- independently revalidate the rights snapshots' exact subject, operation, scope, audience, verdict and obligations at PUBLISHED, blocking staged rights-pointer swaps;
- add targeted adversarial PostgreSQL regressions for forged matching hashes, staged text/content hash tampering, wrong rights snapshots, metadata-only text leakage and published release relocation;
- preserve real OSHB whole-Bible base reader and exclude any real copyrighted translation dataset.

### Validation and limits

The earlier companion head passed the Database Spike PostgreSQL adversarial path; the replacement branch requires its own exact-head complete suite before protected merge. This proves only the synthetic single-passage DB-1 path, not a multi-passage aggregate component hash, real translation permission or whole-Bible Hebrew-Chinese alignment. `CORE-FZ-TRANS-002` remains PENDING.



## 2026-10-10 — Require exact release-component membership for translation Serving

### Push intent

Close a publication identity gap found during independent review of PR #34 despite a green prior exact-head CI suite.

### Why

Exact ProviderDistribution and RightsDecisionSnapshot checks alone do not authorize inserting a translation witness into an unrelated ResearchRelease. Its CORPUS passage must resolve in that release, its TRANSLATION_WITNESS component must pin the exact DigitalExpression, and a DISPLAYABLE persisted witness must use the same snapshot hash as its release component.

### What changed

- fail compiler materialization if the target release does not list the exact translation DigitalExpression as a TRANSLATION_WITNESS component;
- fail if the requested reference span cannot resolve through the release's pinned CORPUS component;
- fail DISPLAYABLE materialization when the release translation component content hash differs from the provider observation's pinned snapshot hash;
- add adversarial candidate releases for each mismatch and assert exact rejection reasons;
- recompute SHA-256 from exact persisted UTF-8 translation surface before projection; a 64-character hex string alone is not acceptable;
- add a forgery regression proving mismatched text/hash is rejected and the valid fixture still materializes;
- repair a generated SQL string-replacement truncation that caused PostgreSQL's unterminated-string failure; add a static pre-migration guard for the complete SHA-256 block;
- remove a duplicated 6 KB suffix after the first migration COMMIT, found by the next exact-head PostgreSQL run, and extend CI to enforce a single terminal COMMIT;
- reject any page render where schema-valid Serving translation witnesses resolve to a different canonical ReferenceSpanId than the release-pinned Hebrew passage; add a hostile cross-span integration regression;
- preserve synthetic-only/right-safe publication, current WB-3 reader and RL-1 immutability boundaries.

### Validation

Pending exact-head validation following this patch. Previous PR #34 head `a216f45fca1c9c11bfaf4f993454260e65a9f631` passed Project governance, Contract validation, Whole-Bible corpus foundation, P1 fixture shell validation, Database Spike, WB-1 and WB-2/WB-3; those runs are not evidence for the new head. `CORE-FZ-TRANS-002` remains PENDING until fresh regression and merge safety checks.

## 2026-10-08 — Implement WB-4 DB-1 rights-gated translation Serving candidate

### Push intent

Implement Issue #32 as the first PostgreSQL translation-witness publication slice after the strict PR #29 contract, using synthetic/right-safe witness data only.

### Why

The canonical witness API now distinguishes TextualWork/TextualEdition/DigitalExpression identity, provider delivery, passage coverage and display rights, but PostgreSQL had no normalized ProviderDistribution identity and no release-compiled translation witness projection. Implementing the reader directly from provider JSON would collapse those boundaries and could expose text without the exact storage/display rights facts required by the contract.

### What changed

- add Authoring Provider and ProviderDistribution identity, with ProviderDistribution -> exact DigitalExpression FK;
- add independent coverage and provider-observation/binding tables;
- enforce snapshot/live storage invariants and provider-observation DigitalExpression compatibility;
- add release-scoped Serving translation witness metadata and segment projections;
- add a privileged publication compiler that validates exact display and storage RightsDecisionSnapshots before copying persisted text;
- require DISPLAYABLE witnesses to be COVERED, READY, SNAPSHOT_PINNED, PERSISTED_CONTENT and segment-bearing;
- expose release-pinned and current-channel translation witness RPCs that resolve through the release's corpus ReferenceSystem/ReferenceSpan;
- preserve zero segments for non-displayable states;
- attach release immutability guards and lifecycle-aware RLS;
- extend the synthetic Database Spike with wrong-expression/wrong-storage-rights attacks, inactive/public visibility checks, exact text/hash parity, OSHB-only empty-list compatibility, revoke behavior, post-publication immutability and Authoring isolation;
- keep real copyrighted translations out of the repository and Serving fixture;
- close overlapping Issue #31 as duplicate of the more complete Issue #32 implementation authority.

### Intended effect

WB-4 gains a real publication boundary without yet selecting a production Chinese translation. Provider availability cannot imply passage coverage, storage permission or public-display permission. A future real witness can only be published by satisfying the same exact identity/right/lifecycle constraints proven with synthetic data.

### Validation

Pending exact-head CI. `CORE-FZ-TRANS-002` remains PENDING until Database Spike 001, WB-1, WB-2/WB-3, whole-Bible source foundation, Contract validation, Project governance and relevant web regressions pass on one synchronized PR head.

## 2026-10-08 — Reconcile RL-1 hardening with merged WB-4 contract

### Push intent

Resolve PR #30 against current `main` after PR #29 merged, without losing either the WB-4 translation-witness contract or the RL-1 permanent Serving-projection fix.

### What changed

- merge current `main` ancestry into PR #30;
- preserve all PR #29 segment-level witness, rights/provider-state and synthetic-fixture contract work;
- carry forward the PR #30 permanent guards for every current `corpus_release_id` Serving projection;
- preserve the catalog-level future-table guard assertion and real whole-Bible revoke/reactivate workflow;
- synchronize PROJECT_STATE and freeze evidence so WB-4 remains the next implementation frontier after RL-1 merge verification.

### Validation

PR #30 implementation head `cedeaa20baa90284fa9f063ef3f1ced943ca7061` and synchronized head `6573807a7cd199847f70ea42d54f584809f84601` both passed the full affected workflow set. This merge-resolved head must rerun Contract validation, Project governance, Database Spike, WB-1, WB-2/WB-3, Whole-Bible corpus foundation and P1 before merge.

## 2026-10-08 — Reopen RL-1 and harden Serving projection immutability

### Push intent

Correct an acceptance defect discovered after PR #28 merged. Keep WB-4 publication blocked until every release-keyed CORPUS Serving projection remains permanently immutable after first publication, including while REVOKED.

### Why

PR #28 correctly separated ever-published immutability from current public servability and passed its exact-head workflows. Follow-up adversarial review found that the permanent component mutation guard covered `corpus_nodes`, features, edges and mappings but omitted three tables that also belong to the published CORPUS payload:

- `serving.reference_labels`;
- `serving.corpus_text_segments`;
- `serving.corpus_node_segments`.

That meant a revoked historical release could still have its published reference addressing, Hebrew surface text or node-to-text membership rewritten. The generic Database Spike test attacked only `corpus_node_features`, and the accepted real WB-2/WB-3 workflow did not exercise revoke/reactivate, so both gates missed the defect.

### What changed

- reopen Issue #25 and keep `CORE-FZ-RELEASE-002` pending re-acceptance;
- attach `guard_component_projection('corpus_release_id')` to every current Serving table keyed by `corpus_release_id`;
- add a catalog-level regression that fails if any future `corpus_release_id` Serving table lacks that permanent guard;
- add post-REVOKED mutation attacks for reference labels, corpus text segments and corpus node/segment memberships;
- extend the real whole-Bible WB-2/WB-3 workflow with revoke -> public-hidden -> immutable-projection -> reactivate -> explicit channel restore -> public-readable assertions;
- align the active database/API contract with canonical event-sequence ordering and explicitly enumerate immutable CORPUS Serving projection surfaces;
- synchronize PROJECT_STATE to the reopened RL-1 hardening frontier.

### Intended effect

REVOKED changes availability only. It cannot reopen any part of an ever-published corpus payload for mutation. Future release-keyed corpus tables cannot silently bypass that invariant.

### Validation

PR #30 implementation head `cedeaa20baa90284fa9f063ef3f1ced943ca7061` passed every triggered implementation gate:

- Database Spike 001 `37669525047`, including the catalog-level permanent-projection-guard assertion and post-REVOKED mutation attacks;
- WB-2 WB-3 Serving Reader `37669525095`, including the real whole-Bible OSHB PUBLISHED -> REVOKED -> REACTIVATED lifecycle regression and restored Gen.1.1 serving;
- WB-1 Relational Whole Corpus `37669524878`;
- Whole-Bible corpus foundation `37669524970`;
- P1 fixture shell validation `37669524947`;
- Contract validation `37669525237`;
- Project governance `37669524996`.

On that evidence, `CORE-FZ-RELEASE-002` is accepted as PASS. This synchronized acceptance/state commit must still pass its own triggered exact-head checks before PR #30 is merged and Issue #25 is closed.



## 2026-10-08 — Prevent live witnesses from claiming snapshot identity

### Push intent

Complete the snapshot/live mutual-exclusion rule in ProviderWitnessBinding before accepting PR #29.

### Why

A `LIVE_EXTERNAL` binding may carry an observed hash for the provider response, but it must not carry a non-null `snapshotContentHash`. Doing so would falsely imply that live external text is an immutable persisted release snapshot.

### What changed

- constrain `LIVE_EXTERNAL.snapshotContentHash` to null when the field is present;
- add an adversarial live-binding fixture that supplies a fake snapshot hash;
- require contract validation to reject that fixture;
- keep READY live-provider delivery possible without claiming snapshot immutability.

### Validation

The change is contract-only and synthetic-only. Exact-head validation must pass again before merge.


## 2026-10-08 — Fail closed on null snapshot witness hash

### Push intent

Close the last clear ProviderWitnessBinding inconsistency found in adversarial review of PR #29 before accepting the WB-4 contract boundary.

### Why

A `SNAPSHOT_PINNED` witness means provider text has been persisted into a release-bound immutable snapshot. The schema required the `snapshotContentHash` field but still permitted its value to be null, which would make that snapshot unverifiable and contradict the release-pinning model.

### What changed

- require `SNAPSHOT_PINNED.snapshotContentHash` to be a non-null SHA-256 value;
- add an adversarial null-hash provider-binding fixture;
- register that fixture as a mandatory schema rejection;
- leave `LIVE_EXTERNAL` locator/ephemeral semantics unchanged.

### Validation

This changes no real translation data and adds no provider content. Exact-head Contract validation plus the full affected repository regression suite must pass again before PR #29 may merge.


## 2026-10-08 — Close WB-4 segment-level witness contract

### Push intent

Make the translation-witness API stable enough for the next PostgreSQL/alignment implementation without publishing any real copyrighted translation.

### What changed

- replace free-form passage echo with ResearchRelease-pinned canonical ReferenceSpan plus resolved ReferenceSystem identity;
- carry TextualWork, nullable TextualEdition and exact DigitalExpression identity per witness;
- add ordered content-hashed TranslationWitnessSegment objects with stable TextStream/TextSegment IDs;
- separate coverage, provider delivery and display-rights state instead of collapsing them into availability;
- require displayable witnesses to be covered, delivery-ready and segment-bearing;
- force rights-restricted, metadata-only, stale, provider-error, not-retrieved and uncovered/unknown states to expose zero translation text;
- require RightsDecisionSnapshot and provenance identity per witness;
- strengthen ProviderWitnessBinding with required observed hash/time and explicit providerVersion presence;
- add schema and semantic adversarial fixtures for missing display segments, uncovered/restricted text leakage and duplicate DigitalExpression identity;
- add `CORE-FZ-TRANS-002` as a PENDING implementation gate.

### Validation

All translation text in fixtures remains synthetic. Contract validation must reject the new adversarial vectors and the full repository regression suite must pass on the exact PR head before merge. Real witness selection, licensing, ingestion and Serving remain outside this contract-only PR.

## 2026-10-08 — Start WB-4 with a strict translation-witness contract

### Push intent

Begin the translation-witness base without prematurely publishing real translation content or allowing provider-specific payloads to define the product contract.

### Why

Core OpenAPI exposed TranslationWitnessList through a permissive inline witness object with additional properties allowed. That left DigitalExpression identity, passage coverage and provider binding underspecified at the API boundary and risked conflating provider availability with publication permission.

### What changed

- add canonical strict TranslationWitness and TranslationWitnessList JSON Schemas;
- bind every witness to an exact DigitalExpression and language tag;
- make passage coverage explicit instead of inferring it from provider availability;
- embed the existing ProviderWitnessBinding as delivery/storage mechanics rather than rights authority;
- replace the permissive inline OpenAPI witness object with the canonical list schema;
- add positive and adversarial fixtures and validator checks;
- document that provider binding, passage coverage and public-display rights are separate facts;
- record merged PR #28 / closed Issue #25 as the accepted RL-1 lifecycle baseline;
- keep all real translation text out of this contract-only frontier.

### Intended effect

WB-4 database publication and reader work can now target one machine-readable witness contract while remaining fail-closed on rights. Synthetic fixtures cannot be mistaken for selected or licensed product translations.

### Validation

Contract validation passed on PR #29 head before the governance synchronization commit. Exact-head validation and whole-Bible regressions must pass again before merge.

## 2026-10-06 — Implement RL-1 release lifecycle split candidate

### Push intent

Close the load-bearing lifecycle ambiguity discovered during WB-2/WB-3 review before translation-witness publication expands the Serving surface.

### Why

The database used the existence of a PUBLISHED event both to make release payloads immutable and to decide whether a release was currently public. That made REVOKED ineffective for public withdrawal, while redefining the same predicate would have made revoked historical releases mutable. The release event contract also lacked deterministic ordering for equal timestamps.

### What changed

- add required per-release `eventSequence` to the canonical ReleaseEvent contract and PostgreSQL event table;
- enforce gapless event order, non-decreasing effective time and valid PUBLISHED/SUPERSEDED/REVOKED/REACTIVATED transitions;
- split ever-published immutability from lifecycle-aware public servability;
- keep SUPERSEDED historical releases pinned-readable and permanently immutable;
- make REVOKED remove public RLS/API visibility and atomically detach channel pointers without mutating payloads;
- require an explicit REACTIVATED transition before a revoked release can be assigned to a channel again;
- make reactivation restore eligibility only, never deployment selection;
- reject channel pointers to non-servable releases;
- add Database Spike adversarial coverage for revoke, reactivation, equal-time ordering, immutable revoked payloads, invalid transitions, sequence gaps, time reversal, channel safety and unauthorized transition attempts;
- add `CORE-FZ-RELEASE-002` so Core freeze cannot ignore lifecycle semantics.

### Validation

This commit is an implementation candidate. Exact-head Contract validation, Project governance, Database Spike 001 and affected whole-Bible/Serving regressions must pass before RL-1 is accepted or Issue #25 is closed.


## 2026-10-06 — Accept WB-2/WB-3 whole-Bible reader gates

### Push intent

Synchronize repository authority with the exact-head evidence after the complete WB-2/WB-3 candidate passed.

### What changed

- promote `CORE-FZ-WB-001` from PENDING to PASS;
- promote `CORE-FZ-WB-003` from PENDING to PASS;
- record the exact commit and GitHub Actions runs supporting the two gates;
- move the implementation frontier from WB-2/WB-3 to WB-4/WB-5 while preserving the accepted reader regression suite;
- document the separate release-lifecycle semantic gap discovered during adversarial review without conflating it with whole-Bible acceptance.

### Validation

Exact head `21a2cedafb394b84d51e244de6ff37bbac4d6a82` passed:

- WB-2 WB-3 Serving Reader `37424398827`;
- WB-1 Relational Whole Corpus `37424398811`;
- Whole-Bible corpus foundation `37424398932`;
- Database Spike 001 `37424398816`;
- Contract validation `37424398834`;
- Project governance `37424398970`;
- P1 fixture shell validation `37424398799`, including unit/integration tests, fixture and Serving visual E2E, and production build.

The WB-2/WB-3 run proved rights-safe OSHB-only publication, anon RLS reads, 39-book data-driven navigation, Genesis chapter/passage indexes, Gen.50.26 -> Exod.1.1 traversal and arbitrary non-fixture passage retrieval. No Research Pro/BYOK dependency is required for the base reader.


## 2026-10-06 — Remove non-canonical Serving capability keys

### Push intent

Fix the remaining P1 integration failure after runtime capability validation was enabled.

### Why

The Serving capability adapter emitted PASSAGE_RESEARCH, HEBREW_TEXT and TRANSLATION_WITNESSES, but none of those names exists in the canonical ExperienceCapabilities v1.1 feature vocabulary. The passage API did not read capabilities, so it passed; full page rendering did and correctly failed closed with CONTRACT_VIOLATION.

### What changed

- remove the three ad hoc feature-decision keys from ServingCapabilityReader;
- keep PASSAGE_STUDY as the canonical base-reader capability;
- keep STUDY and RESEARCH experience modes in experienceModesAllowed;
- leave translation and Research Pro capability expansion to an explicit future contract revision rather than silently widening the schema.

### Validation

P1 integration, Serving E2E/visual capture and production build must rerun on the new exact head. Previously green database, corpus, rights and contract gates must remain green.


## 2026-10-06 — Enforce full RightsDecisionSnapshot table parity

### Push intent

Close the remaining machine-contract drift at the persisted WB-2 publication-rights boundary.

### Why

The nested RightsCondition and obligation validators had been aligned with v1.1, but the SQL table still accepted snapshot states the canonical JSON Schema rejects: unknown subject/operation/scope values, duplicate rule IDs, empty resolver versions, malformed decision hashes, and restrictive default-deny snapshots carrying residual conditions or obligations.

### What changed

- constrain subject type, operation, purpose scope, audience scope and commercial context to the canonical v1.1 enum domains;
- add deterministic UUID-array uniqueness validation, including rejection of duplicate/null members;
- require a non-empty resolver version and a 64-hex-character decision hash;
- require DEFAULT_DENY and UNKNOWN_RESTRICTIVE snapshots to be DENY with no winning rules, conditions or obligations;
- add adversarial SQL inserts covering invalid enum values, duplicate rule IDs, restrictive snapshots with residual restrictions metadata, empty resolver versions and malformed hashes.

### Validation

Database Spike and all exact-head whole-Bible/web/contract regressions must pass before WB-2/WB-3 is accepted.


## 2026-10-06 — Complete strict AJV typing for SERVING PassageCore conditional

### Push intent

Repair the second schema-compilation regression exposed by the P1 fixture-shell gate.

### Why

The prior correction made conditional required fields visible to AJV strictRequired, but strictTypes independently requires keywords such as `minLength`, `minItems` and nested object properties to declare their applicable type in the same conditional scope. The semantic rule was correct; its strict-schema representation was incomplete.

### What changed

- redeclare string/object/array/integer types inside the SERVING conditional for every local constraint;
- retain the same mandatory resolved reference, non-empty Hebrew/token payload, complete Book/Chapter/Passage navigation index, attribution and reconstruction status.

### Validation

All exact-head workflows must rerun. No freeze gate is promoted by this schema-encoding correction.


## 2026-10-06 — Repair strict AJV compilation of SERVING PassageCore conditional

### Push intent

Fix the first regression found by exact-head validation of the WB-2/WB-3 trust-boundary hardening.

### Why

AJV strict mode requires every field named by a conditional `then.required` to be declared in the same conditional `then.properties` scope. The new SERVING PassageCore rule correctly identified the required runtime fields but relied on their top-level property declarations, causing schema compilation to fail before fixture or Serving validation ran.

### What changed

- declare attribution and reconstruction-status fields inside the SERVING conditional property scope;
- declare previous/next reference fields inside the conditional navigation property scope;
- preserve the same semantic requirements for complete SERVING Hebrew, token, navigation and attribution data.

### Validation

P1 fixture shell, Contract validation, WB-2/WB-3, Database Spike, WB-1 and whole-Bible corpus workflows must rerun on the new exact head. No gate status changes in this correction.


## 2026-10-06 — Harden WB-2/WB-3 rights and Serving trust boundaries

### Push intent

Review the updated whole-Bible Serving/reader branch against the canonical machine contracts before accepting WB-2/WB-3.

### Why

The branch had progressed beyond its original RED rights test, but independent review found two trust-boundary gaps. PostgreSQL used the canonical `obligationType` key while still implementing only part of the v1.1 rights language. Separately, PostgREST adapters trusted external JSON through TypeScript casts and bypassed the AJV runtime validation already used by fixture contracts. Concurrent WB-3 work also introduced the data-driven whole-Bible navigator, so its real database coverage now needs explicit acceptance evidence rather than UI existence alone.

### What changed

- aligned authoring and Serving SQL rights validators with all five canonical RightsCondition variants and all six canonical obligation variants;
- enforce exact schema version, required/exclusive keys, enum domains, nested uniqueness and additional-property rejection;
- added positive and adversarial PostgreSQL rights regressions;
- validate external PostgREST PassageCore and ReleasePointer responses against canonical AJV contracts;
- validate Serving capability projections;
- require complete Hebrew, token, attribution and Book/Chapter/Passage navigation payload for `dataSource=SERVING`;
- added a malformed Serving response regression that must return `CONTRACT_VIOLATION`;
- strengthened real PostgreSQL WB-3 acceptance to prove 39-book navigation, Genesis 50 chapters, Genesis 1 passage index, Gen.50.26 -> Exod.1.1 transition and non-fixture Isa.6.1 retrieval;
- removed stale fixture-only wording from runtime errors;
- synchronized PROJECT_STATE to the actual WB-2/WB-3 implementation frontier.

### Intended effect

WB-2 cannot claim rights-safe publication with a database rights language narrower than the canonical contract, malformed Serving payloads fail closed at the external-data boundary, and WB-3 whole-Bible navigation can be accepted only on machine evidence over the real published corpus.

### Validation

Exact-head CI is required after this commit. This entry does not itself promote `CORE-FZ-WB-001` or `CORE-FZ-WB-003`.

## 2026-10-05 — Start WB-2/WB-3 with rights obligation contract regression

### Push intent

Begin the database-backed whole-Bible Serving/reader milestone by proving the current PostgreSQL rights validator is out of sync with the canonical machine contract before changing production logic.

### Why

The canonical RightsDecisionSnapshot schema uses `obligationType`, including `ATTRIBUTION`, but `authoring.valid_rights_obligations` / `serving.valid_rights_obligations` still inspect the legacy key `type`. OSHB public serving requires attribution, so WB-2 must not publish a release while this contract/database mismatch exists.

### What changed

- added a RED Database Spike regression that inserts a CONDITIONAL corpus DISPLAY_FULLTEXT rights snapshot using canonical `obligationType: ATTRIBUTION`;
- deliberately made no Serving projection or reader implementation in this commit;
- recorded WB-2/WB-3 as started but not accepted.

### Validation

Expected RED: Database Spike 001 must reject the canonical obligation payload until the validator is corrected. Other independent gates should remain unaffected.


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
