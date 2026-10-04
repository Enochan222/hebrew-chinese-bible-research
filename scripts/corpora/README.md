# Corpus source tools

These tools connect the project to version-pinned OSHB/morphhb, BHSA 2021 and ETCBC bridging inputs. The fetcher also validates that every Text-Fabric feature referenced by BHSA `otext.tf` is present locally, so an apparently valid partial cache cannot fail later during Text-Fabric initialization.

## Rules

- Do not commit downloaded corpora.
- Do not follow upstream branch heads automatically.
- Do not normalize source Hebrew in place.
- Do not flatten OSHB and BHSA into one canonical analysis layer.
- Do not publish BHSA/bridging-derived data until RightsPolicy permits the intended operation.

## Bootstrap

```bash
python scripts/corpora/fetch_sources.py --list
python scripts/corpora/fetch_sources.py
```

BHSA export needs Text-Fabric:

```bash
python -m pip install -r requirements-corpus.txt
```

OSHB example:

```bash
python scripts/corpora/export_oshb_words.py \
  --reference 1Sam.16.7 \
  --output .local/exports/oshb-1sam16-7.ndjson
```

BHSA example:

```bash
python scripts/corpora/export_bhsa_features.py \
  --reference 1Sam.16.7 \
  --output .local/exports/bhsa-1sam16-7.ndjson
```

Passage CLI filters share `reference_aliases.py`, which equates known OSHB/BHSA Latin/BHSA English book labels only for filtering and candidate comparison. Exported provider labels remain unchanged. A requested BHSA passage with zero words is an error, not a successful empty export.

A requested OSHB passage with zero words is likewise an error. Export scope is explicit: use `--reference` for a canary/debug passage or `--all` for a complete pinned-provider export. Omitting both is an error.

The BHSA exporter loads ETCBC bridging features when the pinned bridging cache exists. Those fields are attached to BHSA word nodes as 2021 comparison evidence and are not represented as current OSHB provider word IDs.

Build a conservative current-OSHB to BHSA candidate crosswalk:

```bash
python scripts/corpora/build_candidate_crosswalk.py \
  --oshb .local/exports/oshb-1sam16-7.ndjson \
  --bhsa .local/exports/bhsa-1sam16-7.ndjson \
  --output .local/exports/crosswalk-1sam16-7.ndjson
```

The crosswalk supports conservative contiguous many-to-many token spans. Equal token counts are not required. It first requires equal whole-verse consonantal streams, then emits the smallest prefix-compatible contiguous span groups. Any textual/prefix divergence becomes `NEEDS_REVIEW`; generated mappings are `CANDIDATE_AUTOMATED` and never canonical by themselves.

## WB-CORPUS-001 whole-Bible source foundation

After fetching the exact pins, build the complete source foundation in one command:

```bash
python scripts/corpora/build_whole_bible_corpus.py
```

The build performs:

```text
pinned OSHB source XML
  -> independent OSHB_OSIS reference inventory
  -> explicit OSHB --all export

pinned BHSA + bridging
  -> explicit BHSA --all export

provider exports
  -> conservative whole-corpus candidate crosswalk
  -> deterministic coverage-manifest.json
```

The expected reference inventory is generated directly from the exact pinned OSHB source XML and source manifest, independently of exporter output. An exporter omission therefore cannot silently shrink its own denominator. At this stage `OSHB_OSIS` is explicitly a source-derived bootstrap ReferenceSystem snapshot, not final project CanonSystem adjudication.

Provider book-division counts are retained as provenance metadata only. The WB-CORPUS-001 gate compares reference sets and records missing/provider-only references, unresolved mappings, annotation-only nodes and silent reference loss explicitly. It does not load PostgreSQL and does not by itself satisfy WB-1.

## WB-0 relational canary loader

After the pinned exports and candidate crosswalk exist, load the real 1 Samuel 16:7 canary into a clean Database Spike schema:

```bash
python scripts/corpora/load_wb0_postgres.py \
  --oshb .local/exports/oshb-1sam16-7.ndjson \
  --bhsa .local/exports/bhsa-1sam16-7.ndjson \
  --crosswalk .local/exports/crosswalk-1sam16-7.ndjson \
  --report .local/exports/wb0-relational-report.json
```

The loader is intentionally narrow:

- it refuses source-pin/count drift for the immutable WB-0 canary;
- it preserves provider-native reference labels and IDs;
- it creates separate OSHB and BHSA DigitalExpression/CorpusRelease identities;
- it keeps BHSA phrase/clause graph membership framework-scoped;
- BHSA nodes `150439` and `150445` remain real AnalysisNodes with zero TextSegment memberships;
- many-to-many crosswalk candidates are stored as grouped Authoring research data rather than false pairwise equivalence;
- every automatic candidate remains `canonical=false`, `CANDIDATE_AUTOMATED`;
- bridging values are retained as BHSA-node comparison features, not current OSHB provider-ID equivalence;
- the loader writes no Serving corpus projection.

WB-0 is a relational canary. After it passes, WB-1 must generalize the importer and produce a whole-corpus coverage/error audit rather than extending the product passage by passage.

## WB-1 relational whole-corpus load

WB-1 consumes the already accepted WB-CORPUS-001 artifacts. It does not build another independent whole-source denominator.

```bash
python scripts/corpora/partition_wb_corpus_for_relational.py \
  --foundation-dir .local/whole-bible-corpus \
  --output-dir .local/wb1/partitions \
  --report .local/wb1/reports/partition.json

python scripts/corpora/load_wb1_postgres.py \
  --oshb-dir .local/wb1/partitions/oshb \
  --bhsa-dir .local/wb1/partitions/bhsa \
  --crosswalk-dir .local/wb1/partitions/crosswalk \
  --source-foundation-manifest .local/whole-bible-corpus/coverage-manifest.json \
  --reference-inventory .local/whole-bible-corpus/reference-inventory.json \
  --partition-report .local/wb1/reports/partition.json \
  --report .local/wb1/reports/wb1-relational-coverage.json
```

The selected CanonSystem is `TANAKH_OSIS_39`, but source completeness is still measured against the independently derived WB-CORPUS-001 ReferenceSystem inventory. Exact provider-book code reconciliation is checked before partitioning; a book count by itself is not accepted as coverage evidence.

The relational gate requires all source word records to remain represented as provider-scoped AnalysisNodes, reconciles per-book PostgreSQL counts to the accepted source artifacts, records annotation-only/unclassified empty BHSA states separately, and keeps unresolved OSHB/BHSA mappings non-canonical. No real BHSA/bridging projection is written to Serving in WB-1.

Automatic `ANNOTATION_ONLY_TARGET_NODE` classification is intentionally narrow: it currently recognizes only the evidenced unbridged Biblical Hebrew article-node shape with lexeme, article POS/PDP and phrase/clause context. Other empty target nodes remain unresolved until their source semantics are reviewed.

## Updating upstream data

```bash
python scripts/corpora/fetch_sources.py --check-upstream
```

If the upstream head differs from the pin, open a reviewed PR to change `contracts/v1.1/corpus-source-registry.json`. Never make the fetcher auto-advance the pin.

See `architecture/corpus-source-integration.md`.
