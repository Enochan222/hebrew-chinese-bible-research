# Corpus source tools

These tools connect the project to version-pinned OSHB/morphhb, BHSA 2021 and ETCBC bridging inputs.

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
  --reference 1_Samuel.16.7 \
  --output .local/exports/bhsa-1sam16-7.ndjson
```

The BHSA exporter loads ETCBC bridging features when the pinned bridging cache exists. Those fields are attached to BHSA word nodes as comparison evidence and are not represented as OSHB provider word IDs.

## Updating upstream data

```bash
python scripts/corpora/fetch_sources.py --check-upstream
```

If the upstream head differs from the pin, open a reviewed PR to change `contracts/v1.1/corpus-source-registry.json`. Never make the fetcher auto-advance the pin.

See `architecture/corpus-source-integration.md`.
