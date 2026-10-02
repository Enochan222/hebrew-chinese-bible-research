# BYOK Credential Handling Policy

Status: **NON-NEGOTIABLE SECURITY CONTRACT**

## 1. Product invariant

The public product contains no platform-owned model-provider secret.

Every optional runtime model request is authenticated with a credential supplied by the current user.

Gemini is the first supported provider.

## 2. Terminology

Use:

- BYOK credential
- provider credential
- user-supplied credential

Do not use application-secret names as product-domain fields.

The user credential is opaque. Do not assume a fixed Gemini key syntax.

## 3. Allowed lifecycle

~~~text
USER INPUT
  -> browser volatile memory
  -> one AI request
  -> ephemeral server relay memory
  -> provider
  -> response
~~~

The credential must not become persistent application state.

## 4. Browser rules

Allowed:

- password-type input;
- temporary React/runtime state;
- explicit Forget key action;
- provider validity test initiated by the user.

Forbidden:

- hardcoded credential;
- build-time injected provider key;
- localStorage;
- IndexedDB;
- cookie;
- URL query parameter;
- route parameter;
- DOM text/debug rendering;
- persisted client state store;
- service-worker cache;
- browser analytics property;
- error-report metadata.

## 5. Relay rules

The optional BYOK relay is credential-blind except during the live request.

Requirements:

- HTTPS only;
- request body/header logging disabled or redacted;
- no request replay;
- no background retry that persists credential material;
- no queue payload containing the credential;
- no cache key derived from the raw credential;
- no database insert/update containing the credential;
- no telemetry/span attribute containing the credential;
- no error string that echoes provider authentication headers;
- bounded timeout;
- provider allowlist;
- outbound destination fixed by provider adapter, never user supplied.

## 6. Credential forwarding

The server constructs provider authentication at runtime.

The credential must not appear in URL, query string, logs, response, model prompt, evidence packet, or audit record.

## 7. API contract

Normal passage, corpus, evidence, bibliography, release, and workspace endpoints must not accept or require provider credentials.

Only AI-specific endpoints may receive a BYOK credential.

Use a dedicated BYOK transport field/header that is explicitly redacted. Do not reuse the application's own user-auth Authorization header.

## 8. Data model prohibition

There is deliberately no table for raw provider credentials.

Provider preferences may persist only non-secret metadata such as provider, preferred model, AI feature enabled, and last validation time.

## 9. Environment prohibition

Public runtime environments must not define shared model-provider secrets such as GEMINI_API_KEY, GOOGLE_API_KEY, OPENAI_API_KEY, or ANTHROPIC_API_KEY.

Infrastructure credentials required for database/deployment operation are a separate category and remain server-side secrets.

## 10. Mandatory tests

1. valid BYOK request leaves no raw key in application logs;
2. invalid BYOK request leaves no raw key in exception logs;
3. provider error does not echo the key;
4. telemetry contains no key;
5. server access logs contain no key;
6. client analytics contain no key;
7. browser storage inspection contains no key;
8. refresh removes in-memory key;
9. sign-out removes in-memory key;
10. Forget key removes it immediately.

## 11. Source-control scanning

CI must scan for provider secret variable names, realistic secret patterns, accidental .env files, and secrets in fixtures/test snapshots.

The scan blocks merge on likely model-provider secret leakage.

## 12. Behaviour without BYOK

Without a provider credential, Passage Study, Corpus Lab, published commentary, published evidence, deterministic search, ResearchRelease browsing, and deterministic rules/constructions continue to work.

Only optional AI features become unavailable.

## 13. Gemini-specific requirement

Gemini is the first supported provider, but the application treats the credential as opaque.

Do not code fixed-prefix, fixed-length, or standard-key/auth-key string assumptions.

Provider validation determines acceptance.

## 14. Absolute prohibition

A developer, code generator, Site Builder, agent, or deployment script must not temporarily add a shared model API key for convenience.

Doing so is an architecture violation, not a development shortcut.
