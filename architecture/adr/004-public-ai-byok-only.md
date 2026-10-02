# ADR-004: Public Runtime AI Is Strict BYOK

Status: **ACCEPTED**
Date: 2026-10-03

## Context

The public product may offer optional AI-assisted features such as natural-language-to-CorpusQuery interpretation, explanation of deterministic corpus results, comparison of a user's private proposed translation against published evidence, and other clearly non-canonical assistance.

The product owner requires public users to supply their own model credential, with Gemini as the first supported provider.

## Decision

1. Public runtime AI is BYOK only.
2. The product ships with no shared Gemini/OpenAI/Anthropic/other model credential.
3. No model-provider credential value may appear in source code, committed config, fixtures, tests, examples, screenshots, documentation samples, client bundles, Docker images, Vercel environment variables, Supabase secrets, GitHub Actions secrets, or database seed data.
4. Public runtime code must not read shared model-secret environment variables such as GEMINI_API_KEY, GOOGLE_API_KEY, OPENAI_API_KEY, or equivalent.
5. A user-provided model credential is an opaque BYOK credential, not application configuration.
6. User BYOK credentials are non-persistent by default.
7. User BYOK credentials must not be stored in PostgreSQL/Supabase, object storage, cookies, localStorage, IndexedDB, telemetry, analytics, error-report payloads, request/response logs, audit logs, or crash dumps.
8. Default credential lifetime is in-memory session only. Page reload may require re-entry.
9. Gemini is the first supported provider, but the domain contract remains provider-neutral.
10. Canonical published scholarship and deterministic corpus search never require a BYOK credential.
11. If no BYOK credential is present, only optional AI-assisted features are unavailable.
12. Any future persistent credential vault requires a separate architecture/security decision.

## Runtime transport

Preferred public-web pattern:

~~~text
User
 -> enters BYOK credential
 -> browser memory only
 -> optional AI request
 -> ephemeral BYOK relay / provider adapter
 -> Gemini
~~~

The relay receives the credential only for the duration of the request, never persists it, never logs it, never returns it, never puts it in URLs/query strings, and sends it only to the selected provider.

A direct-browser provider integration may be evaluated later, but it is not the default architecture because browser-side secrets are exposed to XSS/extensions and provider security constraints.

## No platform fallback

The system must never silently fall back from missing/invalid BYOK to a platform credential.

Valid states are:

- BYOK_AVAILABLE
- BYOK_MISSING
- BYOK_INVALID
- PROVIDER_UNAVAILABLE
- FEATURE_DISABLED

## Research integrity

BYOK AI output is non-canonical unless later incorporated through the private authoring/review/publication workflow.

A user's BYOK credential cannot mutate ResearchRelease, publish scholarship, modify official semantic sets, execute arbitrary SQL, read the private Authoring database, bypass RightsPolicy, or bypass ProductEntitlement.

## Consequences

Positive:

- no platform model-secret leakage risk;
- no platform model-usage bill for public AI;
- users control their provider credential;
- optional AI remains replaceable;
- core scholarly product remains deterministic and independent.

Costs:

- users must obtain and enter a provider credential;
- reloads may require re-entry;
- relay logging/redaction requires explicit testing;
- some users may not be able to use optional AI features.
