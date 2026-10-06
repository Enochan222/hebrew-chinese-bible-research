# v1.1 Machine-Readable Contracts

Status: **ACTIVE CANDIDATE CONTRACTS**

These files are normative companions to the active architecture.

## Contract profiles

- Core: `contracts/v1.1/openapi.yaml` + Core schemas
- Research Pro extension: `contracts/v1.1/research-pro-openapi.yaml` + Research Pro schemas
- Optional public AI: strict BYOK policy, independent of deterministic scholarly serving

Profile metadata:

- `contracts/v1.1/profiles.json`
- `contracts/v1.1/freeze-checklist.md`

Research Pro is not a second product or truth state. The separate profile records engineering maturity only.

## Precedence

Within the applicable profile:

1. JSON Schema / that profile's OpenAPI / Product MCP contract;
2. `vocabulary.json`;
3. active architecture prose;
4. superseded architecture files are design history only.

Core OpenAPI does not override Research Pro extension endpoints merely because they live in a separate profile.

## Core machine contracts

- `json-schema/corpus-source-registry.schema.json`
- `corpus-source-registry.json`
- `json-schema/github-ai-usage-policy.schema.json`
- `github-ai-usage-policy.json`
- `json-schema/whole-bible-corpus-build-manifest.schema.json`
- `fixtures/whole-bible-corpus-build-manifest.json`
- `json-schema/hebrew-bible-canon-system.schema.json`
- `hebrew-bible-canon-system.json`
- `json-schema/corpus-query.schema.json`
- `json-schema/corpus-query-normalized.schema.json`
- `json-schema/corpus-query-result.schema.json`
- `json-schema/rights-condition.schema.json`
- `json-schema/citation-locator.schema.json`
- `json-schema/translation-policy-version.schema.json`
- `json-schema/translation-source-basis.schema.json`
- `json-schema/corpus-query-execution-request.schema.json`
- `json-schema/passage-core.schema.json`
- `json-schema/passage-request.schema.json`
- `json-schema/passage-locator.schema.json`
- `json-schema/release-pointer.schema.json`
- `json-schema/construction-instances-request.schema.json`
- `json-schema/rule-applications-request.schema.json`
- `json-schema/evidence-request.schema.json`
- `json-schema/semantic-sets-request.schema.json`
- `json-schema/query-execution-policy.schema.json`
- `json-schema/release-manifest.schema.json`
- `json-schema/rights-decision-snapshot.schema.json`
- `json-schema/published-passage-analysis.schema.json`
- `json-schema/published-evidence-item.schema.json`
- `json-schema/translation-decision.schema.json`
- `json-schema/annotation-layer.schema.json`
- `json-schema/provider-witness-binding.schema.json`
- `json-schema/release-event.schema.json`
- `json-schema/release-lifecycle-policy.schema.json`
- `release-lifecycle-policy.json`
- `json-schema/release-channel-pointer.schema.json`
- `json-schema/semantic-set-version.schema.json`
- `json-schema/construction-compilation-run.schema.json`
- `json-schema/construction-instance.schema.json`
- `json-schema/rule-application.schema.json`
- `query-semantics.md`
- `openapi.yaml`
- `product-mcp-tools.json`

## Research Pro extension machine contracts

- `json-schema/research-target.schema.json`
- `json-schema/research-issue-version.schema.json`
- `json-schema/research-position-version.schema.json`
- `json-schema/literature-snapshot.schema.json`
- `json-schema/commentary-entry.schema.json`
- `json-schema/discovery-record.schema.json`
- `json-schema/experience-capabilities.schema.json`
- `json-schema/product-entitlement.schema.json`
- `json-schema/research-model-run.schema.json`
- `json-schema/scholarly-provider-request.schema.json`
- `scholarly-provider-registry.json`
- `research-pro-openapi.yaml`

## Validation

- `scripts/validate_contracts.py`
- `.github/workflows/contract-validation.yml`
- positive fixtures: `contracts/v1.1/fixtures/`
- negative fixtures: `contracts/v1.1/negative-fixtures/`

Important invariants:

- Pinned corpus sources never auto-advance; provider/framework identities remain explicit.
- WB-CORPUS-001 coverage is measured against a selected ReferenceSystem inventory; provider book-division counts are provenance metadata, not a hard-coded whole-Bible gate.
- OSHB morphology/morpheme data and BHSA structural annotations remain separate AnnotationLayers.
- ETCBC bridging is mapping/comparison evidence, not universal canonical word identity.

- Pattern Builder, HTTP, MCP, and NL-to-DSL share CorpusQuery semantics.
- Query execution uses a release-pinned normalized query.
- Product MCP is read-only over published data in the initial contract.
- Release manifest hashing excludes its own hash and uses deterministic component ordering.
- RightsDecisionSnapshot represents explicit-rule and default-deny outcomes.
- Published scholarship uses assertion-level public evidence.
- JSON Schema validation is necessary but not sufficient; deterministic semantic validation is mandatory.

## Scholarly discovery build contracts

- The initial provider ensemble is OpenAlex, Semantic Scholar, CORE, Crossref, and Scite.
- Direct API and MCP are transport alternatives behind the same provider adapter boundary.
- Build-time query expansion and synthesis use a provider-neutral ResearchModelAdapter; Gemini is not required.
- Every DiscoveryRecord is traceable to a ScholarlyProviderRequest.
- Provider/model credentials are never contract payloads.


## Contract-closure invariants

- Human passage labels are resolved through an explicit ReferenceSystem before domain execution.
- Query meaning and pagination state are separate: CorpusQueryExecutionRequest wraps the normalized query plus cursor/page size.
- Official project TranslationDecision pins an immutable TranslationSourceBasis and exact TranslationPolicyVersion.
- Rights conditions and obligations are machine typed and UNKNOWN_RESTRICTIVE is fail-closed.
- Public excerpts require a rights decision snapshot; immutable evidence requires a content hash.
