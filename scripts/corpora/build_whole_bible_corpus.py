#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUTPUT_DIR = ROOT / ".local/whole-bible-corpus"


def run(*parts: object) -> None:
    command = [str(part) for part in parts]
    print("+", " ".join(command), flush=True)
    subprocess.run(command, cwd=ROOT, check=True)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Build WB-CORPUS-001 from the exact pinned OSHB/BHSA/bridging source cache."
    )
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--oshb-input", type=Path, default=ROOT / ".local/corpora/oshb-morphhb/wlc")
    parser.add_argument("--oshb-source-manifest", type=Path, default=ROOT / ".local/corpora/oshb-morphhb/source-manifest.json")
    parser.add_argument("--bhsa-dir", type=Path, default=ROOT / ".local/corpora/bhsa-2021/tf/2021")
    parser.add_argument("--bridging-dir", type=Path, default=ROOT / ".local/corpora/etcbc-bridging-2021/tf/2021")
    parser.add_argument("--registry", type=Path, default=ROOT / "contracts/v1.1/corpus-source-registry.json")
    args = parser.parse_args()

    out = args.output_dir
    out.mkdir(parents=True, exist_ok=True)
    inventory = out / "reference-inventory.json"
    oshb = out / "oshb.ndjson"
    bhsa = out / "bhsa.ndjson"
    crosswalk = out / "crosswalk.ndjson"
    manifest = out / "coverage-manifest.json"

    run(
        sys.executable, "scripts/corpora/build_reference_inventory.py",
        "--input", args.oshb_input,
        "--source-manifest", args.oshb_source_manifest,
        "--registry", args.registry,
        "--output", inventory,
    )
    run(sys.executable, "scripts/corpora/export_oshb_words.py", "--input", args.oshb_input, "--all", "--output", oshb)
    run(
        sys.executable, "scripts/corpora/export_bhsa_features.py",
        "--bhsa-dir", args.bhsa_dir,
        "--bridging-dir", args.bridging_dir,
        "--all", "--output", bhsa,
    )
    run(
        sys.executable, "scripts/corpora/build_candidate_crosswalk.py",
        "--oshb", oshb, "--bhsa", bhsa, "--output", crosswalk, "--quiet-unresolved",
    )
    run(
        sys.executable, "scripts/corpora/build_whole_bible_manifest.py",
        "--reference-inventory", inventory,
        "--oshb", oshb,
        "--bhsa", bhsa,
        "--crosswalk", crosswalk,
        "--registry", args.registry,
        "--output", manifest,
    )

    built = json.loads(manifest.read_text(encoding="utf-8"))
    if not built.get("gatePass"):
        raise SystemExit("WB-CORPUS-001 coverage gate failed")
    print(f"WB-CORPUS-001 complete: {manifest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
