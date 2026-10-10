# Experimental OSHB lexical proximity candidate search

This read-only script runs against the pinned OSHB export NDJSON. It is **not** the production CorpusQuery v1.1 executor, public reader or an AI natural-language interpreter.

Usage: `python scripts/corpora/oshb_pattern_candidates.py --oshb .local/whole-bible-corpus/oshb.ndjson --pattern PATTERN.json --output .local/candidates.json`.

Pattern JSON fields: `schemaVersion=0.1`, `sourceKey=OSHB_MORPHHB`, `scope=SAME_VERSE`, `actionLemmaRaw=["7200"]`, `bodyLemmaRaw=["5869 a"]`, `targetPrefixLemmaRaw=l`, `direction=ACTION_BEFORE_TARGET`, `minInterveningWords=0`, `maxInterveningWords=3`.

The example uses **source-exact OSHB terminal lemma codes**, not Hebrew orthographic spellings or BHSA/cross-framework lexical identities. The example lexical set is NOT reviewed or exhaustive. OSHB encodes a noun with attached lamed prefix as part of one word, e.g. `l/5869 a`; its prefix is not necessarily an independent word or proof of a syntactic relationship.

Search counts intervening OSHB orthographic word tokens inside a single verse. `0` means adjacent distinct words, not zero morphemes. A same-verse hit is **not** a same-clause hit; BHSA clause membership requires a separately reviewed, rights-cleared framework-specific layer. Source/pattern SHA-256 and source-exact evidence are preserved. Completeness is explicitly `UNVERIFIED_INPUT_SCOPE` until independent full-source coverage validation.

Before interpreting a Chinese request such as '人體器官 + 動作 ל，中間相隔 N 個詞', the eventual AI interpreter must distinguish (1) specified action lexeme versus any verb, (2) ל prefixed to the anatomical noun versus a verb or a different grammatical relation, (3) either word order versus a specified order, (4) orthographic words versus morphemes, (5) same verse versus same clause, and (6) reviewed BODY_PART semantic-set membership versus an AI suggestion.

**Only one production DSL.** Pattern Builder and optional AI interpreters must both compile into the existing validated release-pinned `CorpusQuery v1.1` (see `contracts/v1.1/query-semantics.md`). This test-only JSON must not become another product DSL. AI may propose candidate sets and query plans, but cannot manufacture corpus rows, change rights, silently broaden constraints, or upgrade lexical proximity into syntactic evidence.
