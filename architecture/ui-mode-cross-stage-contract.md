# Study / Research UI Mode Cross-Stage Contract

Status: **ACTIVE CANDIDATE CROSS-STAGE UI CONTRACT**

This document locks the product relationship between the two user-facing research experiences:

- STUDY
- RESEARCH

The modes are projections over the same product, same data model and same active ResearchRelease.

They are not separate applications, separate databases or separate scholarly truth systems.

This contract must be read with:

- `architecture/research-pro-scholarly-intelligence.md`
- `architecture/product-platform-and-publication-model.md`
- `architecture/database-api-cross-stage-contract-v1.1-candidate.md`
- `contracts/v1.1/vocabulary.json`

---

# 1. Experience modes

## 1.1 STUDY

Purpose:

Provide a professional, comparatively low-density passage and translation research experience.

Typical emphasis:

- Hebrew / LXX / Chinese witnesses;
- proposed/user translation;
- morphology and concise syntax;
- key corpus evidence;
- published translation note;
- reviewed commentary;
- key scholarship;
- major alternative interpretation;
- source/citation traceability.

Study is not an academically opaque "basic mode".

It must preserve enough evidence to audit any substantive published conclusion it displays.

## 1.2 RESEARCH

Purpose:

Expose the deeper scholarly environment.

Additional emphasis:

- Corpus Lab;
- construction browser;
- advanced query builder / DSL;
- full ResearchIssue graph;
- ResearchPosition graph;
- claim/evidence graph;
- full bibliography;
- literature snapshots;
- research history;
- citation/dependency graph;
- advanced textual criticism;
- literature review;
- recent/live scholarly discovery;
- saved research projects;
- export/citation workflow.

Research mode is more detailed.

It is not more authoritative than Study mode.

Both read the same published research objects.

---

# 2. Mode switching

The mode switch is a presentation/workflow control.

Recommended product-level labels:

- Study
- Research

Avoid labels such as:

- Basic
- Expert AI
- Smart Mode
- Advanced AI

The selected mode may be user preference/workspace state.

Switching mode must preserve:

- current passage;
- selected translation witnesses;
- active ResearchRelease;
- selected corpus release/framework where applicable;
- user translation draft;
- selected source object where meaningful.

Switching mode must not create a second research session with a different canonical scholarly state.

---

# 3. ResearchRelease invariant

Both modes must pin the same active ResearchRelease unless the user deliberately selects a historical release.

Example:

```text
Study:
1 Sam 16:7
ResearchRelease = 2027.01

Research:
1 Sam 16:7
ResearchRelease = 2027.01
```

Research mode may expose more objects from the release.

It must not silently use a newer unpublished authoring state.

---

# 4. Shared page identity

A passage route must have one stable passage/reference identity.

Mode must not be encoded into the canonical passage ID.

Acceptable UI state patterns may include:

- query parameter;
- user preference;
- client/server workspace state.

Example conceptual route:

```text
/1-samuel/16/7?mode=research
```

The exact route syntax is implementation-specific.

Deep links should be able to preserve mode when explicitly shared, while the underlying passage remains the same object.

---

# 5. Core shared data contract

Both modes receive a shared release-pinned core.

## `PassageExperienceCoreV1`

Required fields:

- `researchRelease`
- `referenceSpan`
- `referenceLabels`
- `navigation`
- `textualWitnesses`
- `selectedTranslationWitnesses`
- `userWorkspaceSummary nullable`
- `publishedTranslationDecision nullable`
- `publishedTranslationNote nullable`
- `publishedCommentarySummary nullable`
- `keyEvidenceSummary`
- `availability`
- `capabilities`

No mode-specific endpoint may redefine these fields with different scholarly meaning.

---

# 6. Study projection

## `StudyPassageProjectionV1`

Contains the shared core plus concise modules:

- `wordInspectionSummary`
- `syntaxSummary`
- `corpusSummary`
- `textualCriticismSummary`
- `keyScholarship`
- `majorAlternatives`
- `translationImplications`
- `commentarySummary`
- `minimumEvidenceLinks`

### Study density rule

The default rendering should prioritize:

1. text;
2. translation;
3. concise linguistic analysis;
4. published translation rationale;
5. key evidence.

Do not render the full research graph by default.

### Study transparency rule

For each substantive conclusion shown, expose:

- evidence label;
- key citation(s);
- ResearchRelease;
- material uncertainty or major alternative;
- source/bibliographic link where permitted.

Research entitlement is not required to see this minimum verification layer.

---

# 7. Research projection

## `ResearchPassageProjectionV1`

Contains the same shared core plus research-depth modules:

- `fullTokenAndMorphemeAnalysis`
- `corpusQueryContext`
- `constructionInstances`
- `semanticSetMemberships`
- `researchIssues`
- `researchPositions`
- `positionClaimGraph`
- `fullTextualCriticism`
- `literatureSnapshot`
- `literatureReview`
- `fullBibliography`
- `scholarlyDependencyGraph`
- `commentarySectionsWithEvidence`
- `translationDecisionEvidence`
- `recentDiscoverySummary`
- `researchExportCapabilities`

The Research projection may be composed from multiple lazy-loaded domain APIs.

It does not need to be one giant payload.

---

# 8. Module visibility contract

Recommended default visibility:

| Module | Study | Research |
|---|---|---|
| Hebrew / LXX / Chinese witnesses | FULL | FULL |
| User translation draft | FULL | FULL |
| Basic morphology | FULL | FULL |
| Full morpheme/framework detail | SUMMARY | FULL |
| Syntax | SUMMARY | FULL |
| Key corpus parallels | SUMMARY | FULL |
| Advanced CorpusQuery | HIDDEN/LIMITED | FULL |
| Construction instances | SUMMARY/LINK | FULL |
| Translation note | FULL | FULL |
| Reviewed commentary | FULL | FULL |
| Key scholarship | FULL | FULL |
| Full bibliography | LIMITED | FULL |
| ResearchIssue | SUMMARY | FULL |
| ResearchPosition graph | LIMITED | FULL |
| Claim/evidence graph | HIDDEN | FULL |
| Citation/dependency graph | HIDDEN | FULL |
| Literature review | SUMMARY | FULL |
| Search methodology | HIDDEN | FULL |
| Live scholarly discovery | HIDDEN | FULL |
| Textual criticism | SUMMARY | FULL |
| Export/citation tools | BASIC | FULL |

These are UX defaults.

Actual feature availability is resolved through ProductEntitlement.

---

# 9. Capability contract

The client must not infer entitlement from plan names or UI mode alone.

## `ExperienceCapabilitiesV1`

Fields:

- `experienceModesAllowed`
- `featureDecisions`
- `reasonCodes`
- `validUntil nullable`
- `sourceReferences nullable`

Example:

```json
{
  "experienceModesAllowed": ["STUDY", "RESEARCH"],
  "featureDecisions": {
    "PASSAGE_STUDY": "ALLOW",
    "KEY_SCHOLARSHIP": "ALLOW",
    "SCHOLARLY_DEBATE_GRAPH": "ALLOW",
    "LIVE_LITERATURE_DISCOVERY": "DENY"
  }
}
```

The server resolves capability.

The browser does not decide entitlement from local flags.

---

# 10. Rights-before-entitlement rule

Every content response passes two independent checks:

```text
1. Source Rights
2. Product Entitlement
```

Order matters.

A feature entitlement never overrides rights.

Example:

```text
User entitlement:
ADVANCED_TEXTUAL_CRITICISM = ALLOW

Source rights:
DISPLAY_FULLTEXT = DENY
DISPLAY_EXCERPT = ALLOW

Result:
advanced interface may be visible,
but only the permitted excerpt/metadata is returned.
```

No UI mode may convert restricted private library content into public/customer content.

---

# 11. API composition contract

Prefer domain APIs plus view-model composition over duplicated Study/Research business logic.

Shared domain endpoints may include:

- passage;
- witnesses;
- translations;
- published analysis;
- evidence;
- issues;
- positions;
- literature snapshots;
- commentary;
- constructions;
- corpus query;
- entitlements.

Optional server-side aggregation endpoints may return Study/Research view models.

If aggregation exists, it must call the same domain services.

Do not implement:

```text
Study database logic
+
separate Research database logic
```

---

# 12. Cross-stage ownership

## Phase 1

Lock:

- experience-mode enum;
- ProductEntitlement boundary;
- shared `PassageExperienceCoreV1`;
- capability resolver interface;
- ResearchRelease pinning;
- stable mode-switch state.

UI may use fixtures.

## Phase 2

Implement Study mode passage experience:

- witnesses;
- translations;
- user draft;
- translation note;
- commentary summary;
- key evidence.

Research mode may initially expose the same core with placeholders for deeper modules.

## Phase 3

Research mode gains:

- Corpus Lab;
- advanced CorpusQuery;
- construction browser;
- semantic sets;
- full linguistic/corpus evidence.

Study mode receives concise compiled summaries from the same objects.

## Phase 4

Research mode gains:

- ResearchIssue;
- ResearchPosition;
- scholarly target links;
- full bibliography;
- literature snapshot;
- source access routes;
- private/editorial scholarly-intelligence workflows.

Public Study mode remains release-pinned and does not gain live private discovery.

## Phase 5

Research mode gains:

- literature review;
- claim/evidence graph;
- scholarly dependency graph;
- live recent-discovery surface;
- advanced textual criticism;
- research export.

Study mode receives final polished:

- commentary;
- translation note;
- key scholarship;
- major alternatives.

---

# 13. Reviewed versus live research state

Both modes may show reviewed content.

Only Research mode should normally expose live discovery.

## Reviewed

Label:

- REVIEWED SCHOLARSHIP
- CURATED IN RESEARCH RELEASE

Properties:

- release-pinned;
- reviewed;
- citable;
- may support published conclusions.

## Live

Label:

- RECENTLY DISCOVERED
- NOT YET INCORPORATED INTO REVIEWED SYNTHESIS

Properties:

- provider-dependent;
- access level varies;
- may be metadata-only;
- cannot update published analysis;
- excluded from Study mode by default.

---

# 14. ResearchIssue rendering

## Study

Show at most a concise summary such as:

- "Two major analyses are represented in the reviewed literature."
- major alternative labels;
- link: "Open in Research".

Avoid dumping full claim graphs.

## Research

Show:

- issue question;
- scope;
- debate status;
- positions;
- linked scholarly claims;
- evidence/counterevidence;
- historical development;
- literature snapshot date;
- coverage limitations;
- source lineage where available.

---

# 15. Commentary rendering

## Study

Default:

- readable scholarly prose;
- concise section structure;
- footnoted/key citations;
- clear translation implications.

## Research

Allow:

- commentary section decomposition;
- underlying issue links;
- claim-level evidence;
- source spans where rights permit;
- counterarguments;
- literature snapshot;
- translation-decision links.

Both modes point to the same `commentary_entry_id`.

Research is an expanded inspection of the same commentary artifact, not a separately generated commentary.

---

# 16. Product entitlement UX

Do not fill Study mode with lock icons.

Preferred pattern:

- Study remains coherent by itself.
- Where deeper functionality exists, show a natural "Open in Research" affordance.
- If the user's entitlement allows it, switch directly.
- If not, the product shell may present plan/entitlement UI outside the scholarly content itself.

Entitlement messaging must never imply that hidden academic evidence does not exist.

---

# 17. Failure and unavailable states

The UI must distinguish:

- FEATURE_NOT_ENTITLED
- SOURCE_RIGHTS_RESTRICTED
- NOT_IN_RESEARCH_RELEASE
- NOT_YET_REVIEWED
- DISCOVERY_PROVIDER_UNAVAILABLE
- COVERAGE_NOT_AVAILABLE
- DATA_TEMPORARILY_UNAVAILABLE

Do not collapse them into "Pro required".

This distinction is academically and operationally important.

---

# 18. Performance contract

Study should load the core passage view without requiring Research-depth graph queries.

Research modules may lazy-load.

Recommended sequence:

```text
PassageExperienceCore
        ↓
Study visible immediately
        ↓
Research modules requested as opened
```

The mode switch must not force re-fetching immutable shared core data unnecessarily.

---

# 19. Analytics/privacy boundary

If product analytics are later added:

- analytics event names must not become scholarly evidence;
- private research queries should not be reused for official issue/claim creation without explicit workflow;
- product entitlement telemetry must not enter the ResearchRelease;
- user reading behaviour must not influence scholarly ranking as if it represented academic authority.

---

# 20. Cross-stage invariants

1. Study and Research share the same ResearchRelease.
2. Study and Research share the same canonical entity IDs.
3. Research exposes more depth, not a different truth.
4. Study preserves minimum evidence transparency.
5. Rights and entitlements are separate.
6. Live discovery is non-canonical until publication.
7. Commentary has one published identity across both modes.
8. ResearchIssue/Position are shared domain objects, not Research-only duplicates.
9. Switching mode preserves passage/workspace state.
10. Entitlement failure and rights restriction have distinct error states.
11. Public runtime never reaches private authoring source full text merely because Research mode is enabled.
12. A hidden Research module cannot make Study's published claim academically unverifiable.
