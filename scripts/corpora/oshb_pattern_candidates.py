#!/usr/bin/env python3
"""Read-only OSHB lexical proximity candidate spike; NOT CorpusQuery production serving."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def check(pattern: dict) -> dict:
    fields = {"schemaVersion", "sourceKey", "scope", "actionLemmaRaw", "bodyLemmaRaw",
              "targetPrefixLemmaRaw", "direction", "minInterveningWords", "maxInterveningWords"}
    if set(pattern) != fields or pattern["schemaVersion"] != "0.1" or pattern["sourceKey"] != "OSHB_MORPHHB":
        raise ValueError("invalid pattern schema/source identity")
    if pattern["scope"] != "SAME_VERSE":
        raise ValueError("same-clause requires a reviewed framework-scoped clause layer")
    for key in ("actionLemmaRaw", "bodyLemmaRaw"):
        vals = pattern[key]
        if not isinstance(vals, list) or not vals or len(vals) != len(set(vals)) or any(
            not isinstance(s, str) or not s.strip() or "/" in s for s in vals
        ):
            raise ValueError(f"{key} needs distinct source-exact terminal OSHB lemma codes")
    if pattern["targetPrefixLemmaRaw"] != "l":
        raise ValueError("only source lamed lemma prefix component is supported")
    if pattern["direction"] not in ("ACTION_BEFORE_TARGET", "TARGET_BEFORE_ACTION", "EITHER"):
        raise ValueError("invalid direction")
    a, b = pattern["minInterveningWords"], pattern["maxInterveningWords"]
    if type(a) is not int or type(b) is not int or not 0 <= a <= b <= 100:
        raise ValueError("invalid word-distance bounds")
    return pattern


def verb(morph: str) -> bool:
    # OSHB morphRaw: HVqp3ms; HC/Vqw3ms; HR/Vqc. Do not confuse morphemes/words.
    return any(piece.startswith("HV") or piece.startswith("V") for piece in morph.split("/"))


def verified_word(w: dict) -> dict:
    required = ("sourceKey", "referenceSystemCode", "referenceLabel",
                "wordOrderInVerse", "surfaceSourceExact", "lemmaRaw", "morphRaw")
    if any(k not in w for k in required) or w["sourceKey"] != "OSHB_MORPHHB" or w["referenceSystemCode"] != "OSHB_OSIS":
        raise ValueError("incompatible OSHB word source/reference")
    if type(w["wordOrderInVerse"]) is not int or w["wordOrderInVerse"] < 1:
        raise ValueError("invalid word order")
    if any(not isinstance(w[k], str) or not w[k] for k in ("referenceLabel", "surfaceSourceExact", "lemmaRaw", "morphRaw")):
        raise ValueError("missing OSHB literal word features")
    return w


def matches_in_verse(words: list[dict], p: dict):
    actions, targets = [], []
    for w in words:
        parts = [x.strip() for x in w["lemmaRaw"].split("/")]
        if parts[-1] in p["actionLemmaRaw"] and verb(w["morphRaw"]):
            actions.append(w)
        if len(parts) > 1 and "l" in parts[:-1] and parts[-1] in p["bodyLemmaRaw"]:
            targets.append(w)
    for a in actions:
        for b in targets:
            delta = b["wordOrderInVerse"] - a["wordOrderInVerse"]
            if not delta:
                continue
            direction = "ACTION_BEFORE_TARGET" if delta > 0 else "TARGET_BEFORE_ACTION"
            gap = abs(delta) - 1
            if p["direction"] not in ("EITHER", direction) or not p["minInterveningWords"] <= gap <= p["maxInterveningWords"]:
                continue
            yield {
                "referenceSystemCode": "OSHB_OSIS", "referenceLabel": a["referenceLabel"],
                "actionWordOrder": a["wordOrderInVerse"], "targetWordOrder": b["wordOrderInVerse"],
                "interveningWords": gap, "direction": direction,
                "action": {k: a.get(v) for k, v in (("surface", "surfaceSourceExact"), ("lemmaRaw", "lemmaRaw"),
                                                      ("morphRaw", "morphRaw"), ("providerScopedWordId", "providerScopedWordId"))},
                "target": {k: b.get(v) for k, v in (("surface", "surfaceSourceExact"), ("lemmaRaw", "lemmaRaw"),
                                                     ("morphRaw", "morphRaw"), ("providerScopedWordId", "providerScopedWordId"))},
                "classification": "MORPHOLOGICAL_PROXIMITY_CANDIDATE",
                "limitations": ["SAME_VERSE_NOT_SAME_CLAUSE", "PREFIX_NOT_SYNTACTIC_GOVERNMENT",
                                "OSHB_WORDS_NOT_CROSS_FRAMEWORK_EQUIVALENCES"]
            }


def search(source: Path, pattern: dict) -> dict:
    p = check(pattern)
    seen, current, current_ref, matches = set(), [], None, []
    word_count = 0
    def flush():
        matches.extend(matches_in_verse(current, p))
    with source.open(encoding="utf-8") as stream:
        for number, line in enumerate(stream, 1):
            if not line.strip():
                continue
            try:
                w = verified_word(json.loads(line))
            except (ValueError, TypeError, json.JSONDecodeError) as exc:
                raise ValueError(f"OSHB input line {number}: {exc}") from exc
            ref = w["referenceLabel"]
            if ref != current_ref:
                flush()
                if ref in seen:
                    raise ValueError(f"noncontiguous repeat of reference {ref}")
                seen.add(ref)
                current, current_ref = [], ref
            if w["wordOrderInVerse"] != len(current) + 1:
                raise ValueError(f"duplicate/nonconsecutive word order in {ref}")
            current.append(w)
            word_count += 1
    flush()
    return {
        "toolVersion": "oshb-proximity-candidate-0.1",
        "sourceKey": "OSHB_MORPHHB",
        "sourceSha256": digest(source),
        "patternSha256": hashlib.sha256(json.dumps(p, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()).hexdigest(),
        "referenceSystemCode": "OSHB_OSIS",
        "scope": "SAME_VERSE",
        "epistemicStatus": "MORPHOLOGICAL_PROXIMITY_CANDIDATES_ONLY",
        "sourceCompleteness": "UNVERIFIED_INPUT_SCOPE",
        "inputReferences": len(seen),
        "inputWords": word_count,
        "totalCandidateMatchesExactWithinInput": len(matches),
        "matches": matches,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--oshb", required=True, type=Path)
    parser.add_argument("--pattern", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    result = search(args.oshb, json.loads(args.pattern.read_text(encoding="utf-8")))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, ensure_ascii=False, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    print(f"{result['totalCandidateMatchesExactWithinInput']} candidates; scope not independently verified")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
