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

A requested OSHB passage with zero words is likewise an error. The unfiltered whole-source mode may still be used to export every available source record.

The BHSA exporter loads ETCBC bridging features when the pinned bridging cache exists. Those fields are attached to BHSA word nodes as 2021 comparison evidence and are not represented as current OSHB provider word IDs.

Build a conservative current-OSHB to BHSA candidate crosswalk:

```bash
python scripts/corpora/build_candidate_crosswalk.py \
  --oshb .local/exports/oshb-1sam16-7.ndjson \
  --bhsa .local/exports/bhsa-1sam16-7.ndjson \
  --output .local/exports/crosswalk-1sam16-7.ndjson
```

The crosswalk supports conservative contiguous many-to-many token spans. Equal token counts are not required. It first requires equal whole-verse consonantal streams, then emits the smallest prefix-compatible contiguous span groups. Any textual/prefix divergence becomes `NEEDS_REVIEW`; generated mappings are `CANDIDATE_AUTOMATED` and never canonical by themselves.

Automatic `ANNOTATION_ONLY_TARGET_NODE` classification is intentionally narrow: it currently recognizes only the evidenced unbridged Biblical Hebrew article-node shape with lexeme, article POS/PDP and phrase/clause context. Other empty target nodes remain unresolved until their source semantics are reviewed.

## Updating upstream data

```bash
python scripts/corpora/fetch_sources.py --check-upstream
```

If the upstream head differs from the pin, open a reviewed PR to change `contracts/v1.1/corpus-source-registry.json`. Never make the fetcher auto-advance the pin.

See `architecture/corpus-source-integration.md`.
