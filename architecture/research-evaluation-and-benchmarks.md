# Research Evaluation and Benchmark Architecture

Status: **ACTIVE ARCHITECTURE REQUIREMENT**

The product cannot be judged research-grade by visual quality, citation count, whether model answers sound plausible, or whether the private authoring database is correct in isolation.

Evaluation must also verify that compiled public releases faithfully reproduce the approved research state.

Every major corpus, retrieval and synthesis change must eventually be evaluated against a controlled benchmark.

## 1. Evaluation layers

Evaluate separately:

1. Hebrew corpus query correctness
2. Academic retrieval quality
3. Citation-source support
4. Counterevidence retrieval
5. Translation-comparison correctness
6. Rights / access-control leakage
7. AI synthesis faithfulness
8. UI evidence presentation
9. Research compiler correctness
10. Publication firewall correctness
11. Compiled serving-projection parity
12. Research-release integrity and rollback

Do not collapse these into one generic "answer quality" score.

## 2. Benchmark growth strategy

No full benchmark is required before early UI scaffolding.

Before Stage 4/5 is considered production-ready, establish a reviewed gold set.

Suggested growth:

- architecture spike: 5 to 10 cases;
- alpha: 30 to 50 cases;
- research beta: 100+ cases across domains.

A case is a test fixture, not necessarily a publishable research conclusion.

## 3. Benchmark domains

Include cases covering:

- morphology;
- morpheme segmentation;
- Ketiv / Qere;
- Hebrew Unicode search;
- lexeme identity / homonym ambiguity;
- preposition semantics;
- clause syntax;
- phrase / clause framework disagreement;
- word order;
- valency;
- corpus parallel search;
- semantic-set candidate search;
- textual criticism;
- LXX / ancient version evidence;
- Chinese translation alignment;
- Chinese translation comparison;
- documented translator notes;
- commentary retrieval;
- scholarly disagreement;
- counterexample search;
- rights-restricted source behaviour.

## 4. Gold annotations per case

Where applicable record:

- input question;
- intent classification;
- reference span;
- required corpus release/framework;
- expected exact matches or known sample matches;
- expected non-matches;
- must-retrieve source sections;
- relevant optional sources;
- known counterevidence;
- known scholarly disagreements;
- forbidden unsupported claims;
- acceptable conclusion range;
- rights expectations;
- evaluator notes.

## 5. Corpus query metrics

For deterministic / framework-complete queries:

- precision;
- recall against reviewed fixtures;
- false positive causes;
- false negative causes;
- count integrity;
- duplicate inflation;
- framework pin correctness;
- normalization sensitivity.

For heuristic semantic analogues:
- candidate recall;
- human usefulness;
- semantic-set provenance;
- taxonomy sensitivity.

Never score heuristic candidate search as if it were an exhaustive corpus query.

## 6. Academic retrieval metrics

Measure:

- Recall@k;
- Precision@k;
- MRR;
- nDCG where ranking is meaningful;
- exact citation recall;
- source diversity;
- edition correctness;
- passage-first commentary recall;
- rule + qualification co-retrieval;
- claim + exception co-retrieval;
- counterevidence recall.

Track by retrieval namespace, not only globally.

## 7. Citation support evaluation

For each generated analytical assertion classify:

- directly supported;
- supported with qualification;
- plausible inference from evidence;
- unsupported;
- contradicted by cited source;
- citation wrong edition/location;
- citation source inaccessible / unverifiable.

Primary metric:
unsupported claim rate.

Separate:
citation existence from citation entailment.

A real citation that does not support the claim is a failure.

## 8. Scholarly-source independence

Track:

- distinct work count;
- distinct author count;
- duplicated file count;
- multiple editions of same work;
- detected dependency / citation relationships.

Do not turn number of retrieved works directly into a "consensus score."

## 9. Counterevidence evaluation

For disputed questions, assess:

- known counterexample recall;
- competing-analysis recall;
- conflicting grammar category recall;
- alternative translation witness recall;
- whether final synthesis surfaces material opposition.

A system that retrieves only supporting evidence fails even if all citations are genuine.

## 10. Rights and security evaluation

Measure:

- private-source leakage rate;
- cross-tenant leakage rate;
- rights-policy violation rate;
- model-context rights leakage;
- cache isolation failure;
- public/private vector retrieval leakage;
- filtered ANN recall.

Target for unauthorized disclosure:
zero.

## 11. Prompt-injection benchmark

Create adversarial documents containing:

- "ignore previous instructions";
- attempts to request other users' documents;
- requests to widen rights mode;
- fake tool instructions;
- hidden / low-visibility instructions;
- instructions embedded in metadata.

Pass condition:

The source may be quoted or analysed as content, but must not alter tool privilege, retrieval scope, authorization or system instructions.

## 12. Regression policy

Any change to:

- corpus importer;
- normalization profile;
- Query DSL;
- semantic-set definitions;
- embedding model;
- full-text configuration;
- reranker;
- source routing;
- prompt template;
- rights resolver;

must run the affected benchmark subset.

Do not rely on one full benchmark score when only one subsystem changed.

## 13. Release gate

Stage 4 or Stage 5 is not research-ready if:

- must-retrieve sources are regularly missed;
- citation-source mismatch remains materially high;
- known exceptions are routinely omitted;
- counterevidence recall is poor;
- rights leakage occurs;
- corpus counts cannot be reproduced from pinned inputs.

## 14. Reporting

Store evaluation runs with:

- git commit;
- corpus release IDs;
- retrieval engine version;
- embedding model/version;
- reranker version;
- prompt version;
- benchmark version;
- metrics by domain;
- known failures.

Evaluation history is part of research infrastructure, not a one-time launch checklist.


## 15. Compiler and publication metrics

For each representative ResearchBuild measure:

- canonical-to-serving row parity for required objects;
- construction-instance parity between canonical query execution and compiled instances;
- rule-application parity;
- semantic-set membership parity;
- published-analysis evidence-link integrity;
- release component hash verification;
- private/unpublishable object leakage;
- private locator leakage;
- quotation/excerpt policy violations;
- stale serving projection rate.

A successful authoring-side analysis is insufficient if publication changes or loses its meaning.

## 16. Query compiler equivalence

For optional natural-language search, maintain fixtures where a manual AST and a natural-language-generated AST must normalize to the same canonical query or an explicitly equivalent query.

Then verify both execute to the same deterministic result set.

Score separately:

- intent-to-AST accuracy;
- schema-valid AST rate;
- semantic equivalence to gold AST;
- execution-result equivalence;
- unsafe/over-complex query rejection.

Do not score the LLM's prose explanation as a substitute for query correctness.

## 17. Research-release tests

Every published release should pass:

- manifest schema validation;
- component hash validation;
- no mutable payload after PUBLISHED;
- current-release pointer test;
- supersede without deletion;
- revoke behaviour;
- rollback to prior release;
- user workspace preservation across release change;
- API compatibility with supported software version.

## 18. Public-serving independence test

Run a production-like test with:

- authoring database unavailable;
- external LLM provider unavailable;
- private RAG index unavailable.

The following must still work:

- passage display;
- published translations;
- published analysis;
- citations;
- construction browsing;
- deterministic CorpusQuery;
- approved rule applications.

This is a release gate for the core scholarly product.


## 19. Research Pro and UI-mode regression tests

Required cross-mode fixtures:

- same passage + same ResearchRelease in STUDY and RESEARCH;
- same CommentaryEntry identity in both modes;
- same published translation decision in both modes;
- Study summary citations are a valid subset/projection of Research evidence;
- Study remains academically verifiable without Research entitlement;
- switching mode preserves passage/release/workspace state;
- Research depth does not change canonical conclusion.

## 20. Product entitlement tests

Test separately from rights:

- feature allowed + source rights allowed;
- feature denied + source rights allowed;
- feature allowed + source rights denied;
- feature denied + source rights denied.

Verify distinct failure reason codes.

Target:

- zero cases where entitlement overrides source rights;
- zero cases where client-side flag manipulation enables a server-denied feature.

## 21. Scholarly discovery evaluation

For DiscoveryRecord / bibliographic resolution measure:

- duplicate-work creation rate;
- DOI exact-resolution precision;
- title-author fingerprint precision/recall;
- AI-assisted resolution review acceptance rate;
- metadata/abstract/fulltext access-level accuracy;
- passage/lexeme/construction target-link precision;
- explicit-reference versus AI-inferred mapping confusion rate.

A discovery record must not be scored as a canonical scholarly contribution until resolved/reviewed.

## 22. ResearchIssue / ResearchPosition evaluation

Benchmark cases should verify:

- issue scope correctness;
- position separation;
- claim-to-position relation correctness;
- preservation of minority/counter positions;
- no conversion of work counts into consensus percentages;
- debate-status dependence on reviewed LiteratureSnapshot;
- historical versus current position distinction where documented.

## 23. LiteratureSnapshot evaluation

For a reviewed snapshot verify:

- provider list persisted;
- all query strings/languages persisted;
- date range persisted;
- deduplication method/version persisted;
- included/excluded records accounted for;
- coverage limitations visible;
- as-of date visible;
- multilingual queries retained where used.

A "current scholarship" UI must fail QA if the snapshot/as-of context is missing.

## 24. CommentaryEntry projection tests

Verify:

- commentary section evidence links resolve;
- rendered prose does not introduce unsupported claims;
- Study summary and Research expansion share one commentary identity;
- Research evidence expansion respects rights;
- translation note remains distinct from general commentary;
- updated commentary requires a new release/version rather than mutating a published historical release.

## 25. Live discovery non-contamination test

Inject newly discovered works after a release is published.

Verify:

- Research mode can show them as DISCOVERED_SINCE_RELEASE;
- Study commentary remains unchanged;
- published ResearchIssue status remains unchanged;
- translation decision remains unchanged;
- no release hash changes;
- next ResearchBuild may explicitly include/promote them after review.
