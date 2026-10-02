# Security, Publication Firewall, and Trust Boundaries

Status: **ACTIVE ARCHITECTURE REQUIREMENT**

This project processes:
- public corpora;
- provider-restricted Bible translations;
- copyrighted academic books;
- user-supplied private research material;
- generated embeddings;
- model-generated analysis;
- external API content.

Security must therefore be designed around both conventional data access control and AI/RAG-specific threats.

## 1. Trust-boundary map

Treat these as separate trust zones:

1. Browser client
2. Next.js / application server
3. Supabase Data API
4. PostgreSQL
5. Supabase Storage / object storage
6. Ingestion worker
7. AI model provider
8. Google Drive source library
9. FHL / external Bible provider
10. Open corpus providers such as OSHB / MACULA / BHSA
11. User-uploaded documents
12. Admin-only operations

No source outside the application database is inherently trusted merely because it is academic, stored in Drive, or comes from a known URL.

## 2. Retrieved source text is data, never instruction

Non-negotiable rule:

> Retrieved academic text, PDF text, OCR text, metadata, notes, webpages and corpus content are untrusted DATA.

They must never be allowed to:
- override system or developer instructions;
- change research permissions;
- change rights mode;
- request credentials;
- select a more privileged tool;
- initiate admin ingestion;
- access another user's project;
- widen retrieval scope by instruction;
- change model safety settings;
- alter source ranking solely because a document tells the model to do so.

The research orchestrator must treat commands found inside retrieved sources as quoted/source content, not tool instructions.

## 3. Indirect prompt injection and RAG poisoning

Threats include:
- visible malicious instructions in a source;
- hidden text layers;
- white-on-white text;
- document metadata instructions;
- OCR-invisible / human-invisible text;
- poisoned user notes;
- adversarial HTML;
- malicious content designed to manipulate reranking or generation.

Mitigations:

### Ingestion
- preserve original hash and source origin;
- record uploader / provider;
- record extraction method;
- detect extreme hidden-text / metadata anomalies where feasible;
- preserve raw and extracted representations separately;
- flag suspicious content;
- allow human quarantine / review.

### Retrieval
- enforce rights and tenant filters before retrieval output;
- do not permit source text to select new tools or namespaces;
- cap source contribution;
- preserve source identities;
- log retrieved object IDs.

### Model context
- wrap source content in explicit data delimiters;
- identify source text as untrusted reference material;
- keep tool instructions outside source text;
- never interpolate source text into privileged instruction fields.

### Tools
- tool permissions are fixed by application policy;
- no retrieved document can add a tool;
- no retrieved text can elevate the user or switch to admin mode.

## 4. Supabase / PostgreSQL access control

RLS is necessary but insufficient.

Every exposed table/view must be reviewed for both:
- SQL grants;
- RLS policies.

### Browser
- uses anon/public credentials only;
- may use authenticated JWT after sign-in;
- never receives service-role / secret key.

### Service role / secret
- server-side only;
- limited to workflows that genuinely require bypass;
- never logged into user-visible output;
- never passed to the model.

### Views
Views created by privileged owners may bypass underlying RLS unless safe invoker behaviour is explicitly used.

Policy:
- use security-invoker views where exposed and supported;
- otherwise keep privileged views in unexposed schemas;
- test effective rows as anon and authenticated roles.

### Functions / RPC
Database functions require separate review.

For every exposed RPC:
- review EXECUTE grants;
- review search_path;
- avoid SECURITY DEFINER unless required;
- when SECURITY DEFINER is required, document why;
- constrain parameters;
- test cross-tenant access;
- avoid dynamic SQL unless strictly necessary.

## 5. Private/public separation

At minimum distinguish:

### Public
- open corpus data;
- public bibliographic metadata;
- verified public-domain sources;
- licensed public excerpts;
- non-sensitive project documentation.

### Restricted provider content
- translation text whose provider permits display but not redistribution;
- provider-controlled notes;
- API-derived content subject to provider terms.

### Private research
- copyrighted academic source text;
- private extracted text;
- private embeddings where legally permitted;
- private user notes;
- user translation drafts;
- unpublished research.

### Admin-only
- source ingestion;
- rights adjudication;
- service credentials;
- raw provider diagnostics;
- cross-user maintenance.

## 6. Rights enforcement before model context

The rights resolver must run before source content is:
- persisted;
- cached;
- embedded;
- displayed;
- quoted;
- sent to an AI model.

A source can therefore have combinations such as:
- display allowed;
- cache denied;
- embedding denied;
- external-model context denied.

Do not treat "user can read it in Drive" as "application may send full text to an external model API."

## 7. Retrieval audit log

Research-grade retrieval should be auditable.

Log where permitted:
- request ID;
- user / tenant;
- research run;
- requested namespaces;
- rights mode;
- resolved source IDs;
- filtered-out reason categories;
- retrieval algorithm / version;
- reranker version;
- returned object IDs;
- timestamp.

Do not log restricted full text unnecessarily.

## 8. Vector-search isolation

Approximate vector search can lose recall under selective filters.

Testing must include:
- tenant filter;
- rights mode filter;
- namespace filter;
- edition/review-status filter.

Measure:
- filtered recall@k;
- under-return rate;
- cross-tenant leakage rate.

Mitigation options:
- exact search for narrow partitions;
- iterative HNSW scans;
- partial indexes;
- partitioned public/private indexes;
- tenant partitioning where scale justifies it.

Do not describe ANN candidate retrieval as exhaustive literature search.

## 9. Cross-tenant tests

Mandatory negative tests:

- User A cannot retrieve User B private source spans.
- User A cannot retrieve User B embeddings.
- Public mode cannot retrieve private source excerpts.
- A public view cannot bypass underlying RLS.
- RPC cannot enumerate inaccessible IDs.
- analysis-run evidence cannot reference a private object that the requesting user is not entitled to see.
- cached results do not cross tenant / rights mode.

## 10. Provider isolation

External provider failures or hostile payloads must not compromise other lanes.

FHL or another provider response must be:
- schema validated;
- bounded in size;
- treated as untrusted data;
- cached only when allowed;
- associated with provider/version provenance.

One provider outage must not make the entire Passage Study fail.

## 11. Ingestion-worker isolation

Ingestion is privileged and must not run with browser-equivalent trust.

Required:
- bounded file type handling;
- malware / archive-bomb awareness where relevant;
- resource limits;
- deterministic file hashes;
- no model-generated path names trusted blindly;
- source state remains FAILED/PARTIAL when extraction is incomplete.

## 12. Security review gates by stage

### Stage 1
- auth boundary;
- secret handling;
- exposed schema inventory;
- public/private data classes.

### Stage 2
- provider rights;
- API cache isolation;
- translation text display permissions.

### Stage 3
- corpus write protection;
- query resource limits;
- denial-of-service controls for pathological grammar queries.

### Stage 4
- RLS integration tests;
- view/RPC review;
- RAG prompt injection tests;
- private embedding isolation;
- retrieval audit logging.

### Stage 5
- tool firewall;
- evidence-object authorization;
- source-as-data prompt construction;
- assertion/evidence leakage tests;
- model provider data-handling review.

## 13. Security acceptance rule

A result is not safe merely because the model does not display restricted text.

Restricted content must not reach an unauthorized retrieval result or model context in the first place.


## 14. Publication firewall

The strongest control is data minimization.

The public serving database should not contain restricted academic source full text merely because the private authoring system can access it.

Required one-way path:

```text
AUTHORING_RESEARCH
  -> publication validator
  -> PUBLIC_SERVING
```

The publication validator must reject:

- private Drive URLs;
- private source locators not intended for display;
- source text exceeding permitted excerpt/quotation rules;
- objects whose rights policy denies public use;
- unresolved private object references;
- unreviewed mandatory claims;
- failed citation entailment requirements;
- release components with invalid hashes.

Public runtime credentials must not provide a route back into the authoring database.

## 15. User workspace isolation

User workspace is separate from official published research.

A user's:

- translation draft;
- saved query;
- annotation;
- semantic-set draft;
- rule draft;

must not alter the current ResearchRelease.

Promotion into official research requires an explicit authoring/review/publication workflow.

For MVP deployment, workspace and serving data may share a Supabase project only if schema, RLS, grants, RPCs and caches preserve the separation.

## 16. Research-release integrity

Security includes scholarly integrity.

Public canonical responses should pin:

- research_release_id;
- component versions;
- relevant hashes where needed.

Switching the active release is a privileged operation.

A rollback changes the active release pointer; it does not mutate historical published releases.


## 17. Product entitlement security boundary

ProductEntitlement and RightsPolicy are separate authorization dimensions.

Server-side response authorization must resolve:

1. source/content rights;
2. tenant/user access;
3. product feature entitlement;
4. experience-mode projection.

A ProductEntitlement ALLOW must never override a RightsPolicy DENY.

A Research-mode client must not receive restricted/private source data merely because the account has a professional subscription.

Entitlement enforcement must not exist only in client-side rendering logic.

Negative tests must include:

- Research entitlement cannot expose PRIVATE_LIBRARY_COPY;
- Research entitlement cannot expose full text when only excerpt display is allowed;
- Study and Research receive the same release-pinned scholarly conclusion;
- entitlement denial is distinguishable from rights restriction;
- direct API access cannot bypass a hidden/disabled Research feature.

## 18. Live scholarly discovery isolation

Live DiscoveryRecords are untrusted external data.

They must be:

- schema validated;
- tagged with provider and retrieval time;
- assigned source access level;
- kept outside canonical ResearchRelease payload until reviewed;
- unable to mutate ResearchIssue debate status;
- unable to mutate published commentary;
- unable to mutate translation decisions;
- unable to promote themselves into canonical Works without bibliographic resolution.

A hostile or malformed discovery-provider payload is treated as source data, not instruction.

## 19. Cross-mode scholarly integrity

Mode switching is not a privilege escalation path.

STUDY and RESEARCH must share:

- ResearchRelease;
- canonical entity IDs;
- commentary identity;
- translation decisions.

Research mode may fetch additional approved depth.

It must not silently switch to private authoring state or unreleased scholarly objects.


## 20. Public runtime model credentials are BYOK-only

Non-negotiable invariant:

> The public product owns no shared model-provider credential.

Gemini is the first supported runtime AI provider, but every public-user model call uses a credential supplied by that user.

The product must not contain or retrieve a shared model credential from:

- source code;
- Vercel environment variables;
- Supabase secrets;
- GitHub Actions secrets;
- database rows;
- config files;
- client bundles;
- test fixtures.

The public runtime must not define a hidden fallback path using a platform-owned model credential.

User BYOK credentials are transient secrets.

They must not be persisted in:

- PostgreSQL/Supabase;
- object storage;
- cookies;
- localStorage;
- IndexedDB;
- analytics;
- telemetry;
- logs;
- audit records;
- evidence packets.

Default client storage is volatile in-memory state only.

The optional AI relay may hold a user credential only during the live HTTPS request and must forward it only to the selected allowlisted provider.

The relay must redact the credential from:

- access logs;
- application logs;
- error reporting;
- telemetry spans;
- provider-error serialization.

Signing out, refreshing, or explicitly choosing Forget key removes the in-memory credential.

See:

- `architecture/byok-credential-handling.md`
- `architecture/adr/005-public-ai-byok-only.md`

## 21. BYOK threat model

Threats include:

- accidental source-control commit;
- accidental build-time injection;
- client persistence;
- XSS credential theft;
- malicious browser extension;
- server request logging;
- telemetry capture;
- error-object echo;
- provider redirect/SSRF;
- model credential accidentally entering prompts.

Mitigations:

- masked credential input;
- strict CSP and XSS controls;
- volatile memory only;
- fixed provider adapter destinations;
- no user-controlled provider URL;
- explicit log/telemetry redaction;
- no background job/queue containing credentials;
- no credential in prompt/evidence/research objects;
- CI secret scanning;
- negative tests for browser storage and logs.

## 22. BYOK availability is not scholarly availability

A missing or invalid BYOK credential affects only optional runtime AI.

It must not affect:

- passage rendering;
- published translation witnesses;
- CorpusQuery;
- semantic-set search;
- constructions;
- rule applications;
- published commentary;
- evidence/citations;
- ResearchRelease access.

The UI must not imply that AI access is required to use the research product.
