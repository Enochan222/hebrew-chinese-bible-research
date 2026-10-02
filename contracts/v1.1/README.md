# v1.1 Machine-Readable Contracts

Status: **ACTIVE CANDIDATE CONTRACTS**

These files are normative companions to:

- `architecture/database-api-cross-stage-contract-v1.1.md`

Precedence for machine names and wire formats:

1. JSON Schema / OpenAPI / Product MCP contract in this directory;
2. `vocabulary.json`;
3. active architecture prose;
4. superseded architecture files are design history only.

Current files:

- `vocabulary.json`
- `json-schema/corpus-query.schema.json`
- `json-schema/release-manifest.schema.json`
- `json-schema/rights-decision-snapshot.schema.json`
- `json-schema/published-passage-analysis.schema.json`
- `json-schema/translation-decision.schema.json`
- `json-schema/annotation-layer.schema.json`
- `json-schema/provider-witness-binding.schema.json`
- `json-schema/release-event.schema.json`
- `json-schema/release-channel-pointer.schema.json`
- `json-schema/semantic-set-version.schema.json`
- `json-schema/construction-compilation-run.schema.json`
- `json-schema/construction-instance.schema.json`
- `json-schema/rule-application.schema.json`
- `json-schema/published-evidence-item.schema.json`
- `query-semantics.md`
- `openapi.yaml`
- `product-mcp-tools.json`
- `fixtures/`

Important invariants:

- HTTP, MCP, Pattern Builder, and NL-to-DSL use the same CorpusQuery schema.
- Product MCP is read-only over published data in the initial contract.
- Release manifest hashes are computed over the manifest payload, not a payload containing its own hash.
- RightsDecisionSnapshot is an immutable evaluation output.
- Published analysis uses assertion-level public evidence.
- JSON Schema validation is necessary but not sufficient: semantic validation must also check node references, layer compatibility, release availability, rights, and query complexity.
