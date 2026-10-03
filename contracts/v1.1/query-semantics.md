# CorpusQuery v1.1 Binding and Execution Semantics

Status: **NORMATIVE CANDIDATE SEMANTICS**

Companion schema:

- `contracts/v1.1/json-schema/corpus-query.schema.json`

This document closes semantic ambiguity that JSON Schema alone cannot express.

## 1. Node declarations

`nodes[]` declares query variables.

A node declaration does not itself assert that a matching corpus object exists.

Existence is established by predicates in `expression`.

`bind: true` means the node may appear in returned match bindings when it is in the outer query scope.

`bind: false` means it is not returned even if matched.

All node IDs are unique within one query.

## 2. Atomic node constraints

Fields have distinct semantics:

- `LEXEME_ID`: internal reviewed lexeme identity;
- `LEMMA_TEXT`: layer/source lemma text after the pinned normalization/morphology rules;
- `SURFACE`: text-segment surface according to the pinned text context;
- `POS`: part-of-speech feature according to the declared annotation layer;
- `FEATURE`: framework feature; `featureKey` is required;
- `SEMANTIC_SET_VERSION_ID`: membership in exactly one pinned semantic-set version;
- `REFERENCE_SPAN_ID`: reference-span identity.

The validator must reject a `FEATURE` constraint without `featureKey`.

## 3. Relation predicates

Text-stream relations:

- IMMEDIATELY_PRECEDES
- PRECEDES
- FOLLOWS
- WITHIN_N_SEGMENTS
- SAME_REFERENCE_SPAN

Framework/layer-scoped relations:

- SAME_PHRASE
- SAME_CLAUSE
- SAME_SENTENCE
- ATTACHED_TO
- GOVERNS
- DEPENDENT_OF
- SEMANTIC_ROLE
- MORPHEME_OF
- HAS_MORPHEME
- PREFIX_MORPHEME_OF
- SUFFIX_MORPHEME_OF

A framework/layer-scoped relation must provide a compatible `annotationLayerId`.

`WITHIN_N_SEGMENTS` requires `maxDistance`.

The query planner must reject a relation that is not supported by the declared layer kind/ontology.

## 4. ALL_OF

`ALL_OF` is conjunction over one binding environment.

All child expressions must be true for the same outer bindings.

It must not be implemented as independent result sets later joined only by reference span unless that is exactly equivalent to the declared variable bindings.

## 5. ANY_OF

`ANY_OF` is disjunction.

All branches operate against the same outer binding scope.

For deterministic result shape, every branch must preserve the same outer returned binding set.

Branch-local variables belong inside EXISTS/NOT_EXISTS/count scopes rather than appearing only in some ANY_OF branches.

A semantic validator must reject ambiguous branch result shapes.

## 6. NOT

`NOT` negates a predicate/expression against the **current outer binding**.

NOT must not introduce a new unbound node.

Example:

~~~text
N is already bound
NOT (N LEMMA_TEXT = עין)
~~~

means the current N binding is not עין.

To express:

> no עין node exists in the same clause

use `NOT_EXISTS`, not NOT.

## 7. EXISTS

`EXISTS.bind` explicitly declares locally scoped nodes.

Semantics:

1. keep the current outer binding;
2. search for at least one assignment of the locally bound nodes making `child` true;
3. return only the outer binding;
4. do not expose local bindings in the result.

The bind list is mandatory.

## 8. NOT_EXISTS

Same scope rules as EXISTS.

The expression is true only when no assignment of the locally scoped nodes makes `child` true for the current outer binding.

This is the correct operator for absence of another corpus object.

## 9. COUNT quantifiers

`MIN_COUNT`, `MAX_COUNT`, and `EXACT_COUNT` count **distinct tuples of the explicitly listed local `bind` nodes**, after semantic deduplication.

They do not count raw SQL rows.

This prevents join multiplication from changing scholarly counts.

Example:

~~~text
EXACT_COUNT 2 bind=[X]
~~~

means exactly two distinct X bindings satisfy the child expression for the current outer binding.

## 10. Semantic-set membership

`SEMANTIC_SET_VERSION_ID` always pins an immutable semantic-set version.

Runtime AI classification is not permitted to add/remove members during execution.

If a semantic set is incomplete, the result epistemic class must reflect that limitation.

## 11. Annotation-layer dependencies

Every query execution derives a dependency manifest from the authoritative AST.

The manifest records:

- corpus release;
- digital expression/text stream;
- annotation layer IDs and versions;
- normalization profile;
- semantic-set version IDs;
- relation ontologies used;
- query schema/version;
- planner/compiler version.

A separate manually entered framework-requirements field is not authoritative.

## 12. Query completeness labels

Results must carry one of:

- CORPUS_COMPLETE
- FRAMEWORK_COMPLETE
- CURATED_SET_COMPLETE
- HEURISTIC_CANDIDATE
- INCOMPLETE_COVERAGE

The label describes completeness only relative to the pinned data/query semantics.

It must not be paraphrased as linguistic exhaustiveness beyond those boundaries.

## 13. Result counting

The system must distinguish at least:

- page match count;
- exact total match count where the engine has actually computed an exact total;
- construction-instance count;
- clause count;
- verse/reference-label count;
- reference-span count.

`pageMatchCount` is always the number of rows in the current `matches` page.

`totalMatchCount` is populated only when `totalCountExact = true`. If the server has not computed a defensible exact total, `totalCountExact = false` and `totalMatchCount = null`.

UI and API must state which count is being shown and must not present a page count or estimate as an exact corpus total.

## 14. HTTP, MCP, and UI equivalence

These four entry paths compile to the same normalized CorpusQuery:

- Pattern Builder;
- direct HTTP API query;
- Product MCP `run_corpus_query`;
- optional natural-language query interpreter.

No path is permitted to have different hidden query semantics.

## 15. LLM boundary

An LLM may propose a candidate AST.

It may not:

- execute SQL;
- change annotation-layer scope after validation;
- change rights scope;
- decide which corpus rows match;
- silently relax an exact query into a semantic analogue.

The deterministic query engine decides result membership.

## 16. Release resolution and validate/run race prevention

An incoming draft CorpusQuery may omit `researchReleaseId` only at the validation boundary.

Validation must:

1. resolve the current requested release channel exactly once;
2. write the resolved `researchReleaseId` into the normalized query;
3. validate all corpus/layer/semantic-set dependencies against that release;
4. return a query conforming to `corpus-query-normalized.schema.json`.

`POST /corpus/query/run` and Product MCP `run_corpus_query` execute only a normalized release-pinned query.

They must not re-resolve the current release pointer.

This prevents validation against Release A followed by execution against Release B after a channel-pointer change.

## 17. Field/operator semantic validation

JSON Schema shape validation is followed by a deterministic semantic validator.

At minimum it enforces:

- `FEATURE` requires `featureKey`;
- `LEXEME_ID`, `SEMANTIC_SET_VERSION_ID`, and `REFERENCE_SPAN_ID` values are UUID identities;
- `IN` and `NOT_IN` require a non-empty array;
- scalar comparison operators do not accept boolean values;
- every node reference is declared;
- local quantifier bindings are declared and not leaked into outer result shape;
- annotation-layer relation compatibility;
- relation-specific required fields such as `maxDistance`;
- server query-complexity policy.

## 18. Query resource policy

Semantic validity does not imply safe execution.

The server owns a versioned `QueryExecutionPolicyV1` containing:

- maximum declared nodes;
- maximum AST depth;
- maximum relation count;
- maximum quantifier nesting;
- maximum segment distance;
- default page size;
- maximum page size;
- hard result cap;
- execution timeout.

Limits may be tuned by benchmark without changing query meaning, but every execution records the policy version used.

A query rejected for cost/resource reasons is not described as linguistically invalid.

## 19. Stable result ordering and pagination

Large corpus results use deterministic pagination.

Canonical order is based on release-pinned textual/reference order plus deterministic binding/result identifiers.

A cursor must pin:

- researchReleaseId;
- normalized query hash;
- query execution policy version;
- last stable sort key.

A cursor must not be reusable after the release/query hash changes.

Execution is requested through `CorpusQueryExecutionRequestV1`, which wraps the immutable normalized query plus retrieval state (`cursor`, `pageSize`). Cursor/page state must never mutate query meaning.

Counts must continue to distinguish match, construction, clause, verse/reference-label, and reference-span counts.
