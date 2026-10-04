#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path

from reference_aliases import parse_reference_label

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_REGISTRY = ROOT / "contracts/v1.1/corpus-source-registry.json"


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def normalized_label(row: dict) -> str:
    book, chapter, verse = parse_reference_label(row["referenceLabel"])
    return f"{book}.{chapter}.{verse}"


def normalized_crosswalk_reference(row: dict) -> str:
    ref = row["reference"]
    return f"{ref['book']}.{int(ref['chapter'])}.{int(ref['verse'])}"


def scan_provider(path: Path, source_key: str, id_key: str) -> dict:
    refs: Counter[str] = Counter()
    seen_ids: set[str] = set()
    rows = 0
    with path.open(encoding="utf-8") as fh:
        for line_number, line in enumerate(fh, start=1):
            if not line.strip():
                continue
            row = json.loads(line)
            if row.get("sourceKey") != source_key:
                raise RuntimeError(f"{path}:{line_number} unexpected sourceKey {row.get('sourceKey')!r}")
            provider_id = row.get(id_key)
            if provider_id is None or provider_id == "":
                raise RuntimeError(f"{path}:{line_number} missing {id_key}")
            provider_id_s = str(provider_id)
            if provider_id_s in seen_ids:
                raise RuntimeError(f"{path}:{line_number} duplicate {id_key} {provider_id_s}")
            seen_ids.add(provider_id_s)
            refs[normalized_label(row)] += 1
            rows += 1
    if rows == 0:
        raise RuntimeError(f"{path} contains no provider records")
    return {"rows": rows, "refs": refs}


def scan_crosswalk(path: Path) -> dict:
    observed_refs: set[str] = set()
    mapped_refs: set[str] = set()
    unresolved_refs: set[str] = set()
    unresolved_reasons: Counter[str] = Counter()
    record_types: Counter[str] = Counter()
    candidate_records = 0
    annotation_only_records = 0
    mapped_source_nodes = 0
    mapped_target_nodes = 0

    with path.open(encoding="utf-8") as fh:
        for line_number, line in enumerate(fh, start=1):
            if not line.strip():
                continue
            row = json.loads(line)
            record_type = row.get("recordType")
            if record_type not in {
                "CANDIDATE_SPAN_MAPPING",
                "ANNOTATION_ONLY_TARGET_NODE",
                "UNRESOLVED_REFERENCE",
            }:
                raise RuntimeError(f"{path}:{line_number} unknown recordType {record_type!r}")
            ref = normalized_crosswalk_reference(row)
            observed_refs.add(ref)
            record_types[record_type] += 1
            if record_type == "CANDIDATE_SPAN_MAPPING":
                mapped_refs.add(ref)
                candidate_records += 1
                mapped_source_nodes += int(row.get("sourceCount", 0))
                mapped_target_nodes += int(row.get("targetCount", 0))
            elif record_type == "ANNOTATION_ONLY_TARGET_NODE":
                annotation_only_records += 1
            else:
                unresolved_refs.add(ref)
                unresolved_reasons[str(row.get("reason") or "UNKNOWN")] += 1

    if not observed_refs:
        raise RuntimeError(f"{path} contains no crosswalk records")
    return {
        "observedRefs": observed_refs,
        "mappedRefs": mapped_refs,
        "unresolvedRefs": unresolved_refs,
        "unresolvedReasons": unresolved_reasons,
        "recordTypes": record_types,
        "candidateRecords": candidate_records,
        "annotationOnlyRecords": annotation_only_records,
        "mappedSourceNodes": mapped_source_nodes,
        "mappedTargetNodes": mapped_target_nodes,
    }


def source_pins(registry_path: Path) -> dict:
    registry = json.loads(registry_path.read_text(encoding="utf-8"))
    result = {}
    for source in registry["sources"]:
        pin = source["pin"]
        result[source["sourceKey"]] = {
            "commitSha": pin.get("commitSha"),
            "datasetVersion": pin.get("datasetVersion"),
        }
    required = {"OSHB_MORPHHB", "BHSA_2021", "ETCBC_BRIDGING_2021"}
    missing = required - set(result)
    if missing:
        raise RuntimeError(f"corpus source registry missing required sources: {sorted(missing)}")
    return result


def artifact(path: Path) -> dict:
    return {"fileName": path.name, "bytes": path.stat().st_size, "sha256": sha256_file(path)}


def main() -> int:
    parser = argparse.ArgumentParser(description="Build the deterministic WB-CORPUS-001 coverage manifest.")
    parser.add_argument("--reference-inventory", type=Path, required=True)
    parser.add_argument("--oshb", type=Path, required=True)
    parser.add_argument("--bhsa", type=Path, required=True)
    parser.add_argument("--crosswalk", type=Path, required=True)
    parser.add_argument("--registry", type=Path, default=DEFAULT_REGISTRY)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    inventory = json.loads(args.reference_inventory.read_text(encoding="utf-8"))
    if inventory.get("referenceSystemCode") != "OSHB_OSIS":
        raise SystemExit("WB-CORPUS-001 currently requires the OSHB_OSIS bootstrap reference inventory")
    expected_list = inventory.get("references")
    if not isinstance(expected_list, list) or not expected_list:
        raise SystemExit("reference inventory has no expected references")
    expected = set(expected_list)
    if len(expected) != len(expected_list):
        raise SystemExit("reference inventory contains duplicate references")

    oshb = scan_provider(args.oshb, "OSHB_MORPHHB", "providerScopedWordId")
    bhsa = scan_provider(args.bhsa, "BHSA_2021", "providerScopedNodeId")
    crosswalk = scan_crosswalk(args.crosswalk)

    oshb_refs = set(oshb["refs"])
    bhsa_refs = set(bhsa["refs"])
    crosswalk_refs = crosswalk["observedRefs"]

    oshb_missing = sorted(expected - oshb_refs)
    oshb_provider_only = sorted(oshb_refs - expected)
    bhsa_missing = sorted(expected - bhsa_refs)
    bhsa_provider_only = sorted(bhsa_refs - expected)
    crosswalk_missing = sorted((oshb_refs | bhsa_refs) - crosswalk_refs)
    crosswalk_provider_only = sorted(crosswalk_refs - (oshb_refs | bhsa_refs))
    silent_reference_loss = sorted(expected - crosswalk_refs)
    unresolved = sorted(crosswalk["unresolvedRefs"])

    by_book: dict[str, dict] = defaultdict(lambda: {
        "expectedReferences": 0,
        "oshbReferences": 0,
        "oshbWords": 0,
        "bhsaReferences": 0,
        "bhsaWordNodes": 0,
        "crosswalkObservedReferences": 0,
        "unresolvedReferences": 0,
    })
    for ref in expected:
        by_book[ref.rsplit(".", 2)[0]]["expectedReferences"] += 1
    for ref, count in oshb["refs"].items():
        book = ref.rsplit(".", 2)[0]
        by_book[book]["oshbReferences"] += 1
        by_book[book]["oshbWords"] += count
    for ref, count in bhsa["refs"].items():
        book = ref.rsplit(".", 2)[0]
        by_book[book]["bhsaReferences"] += 1
        by_book[book]["bhsaWordNodes"] += count
    for ref in crosswalk_refs:
        by_book[ref.rsplit(".", 2)[0]]["crosswalkObservedReferences"] += 1
    for ref in crosswalk["unresolvedRefs"]:
        by_book[ref.rsplit(".", 2)[0]]["unresolvedReferences"] += 1

    gate_pass = not (
        oshb_missing
        or oshb_provider_only
        or crosswalk_missing
        or crosswalk_provider_only
        or silent_reference_loss
    )
    explicit_exceptions = bool(bhsa_missing or bhsa_provider_only or unresolved)
    status = (
        "INVALID_SILENT_REFERENCE_LOSS"
        if not gate_pass
        else "COMPLETE_WITH_EXPLICIT_EXCEPTIONS"
        if explicit_exceptions
        else "COMPLETE"
    )

    pins = source_pins(args.registry)
    artifacts = {
        "referenceInventory": artifact(args.reference_inventory),
        "oshbExport": artifact(args.oshb),
        "bhsaExport": artifact(args.bhsa),
        "crosswalk": artifact(args.crosswalk),
    }
    build_seed = json.dumps(
        {"referenceSetSha256": inventory["referenceSetSha256"], "sourcePins": pins, "artifacts": artifacts},
        sort_keys=True,
        separators=(",", ":"),
    )
    build_id = "wb-corpus-" + hashlib.sha256(build_seed.encode("utf-8")).hexdigest()[:24]

    manifest = {
        "schemaVersion": "1.0",
        "buildType": "WB-CORPUS-001",
        "buildId": build_id,
        "status": status,
        "gatePass": gate_pass,
        "referenceSystem": {
            "code": inventory["referenceSystemCode"],
            "authorityStatus": inventory["authorityStatus"],
            "derivation": inventory["derivation"],
            "referenceSetSha256": inventory["referenceSetSha256"],
            "expectedReferenceSpans": len(expected),
            "providerBookDivisionCount": inventory["providerBookDivisionCount"],
            "note": "Provider book-division count is provenance metadata only; coverage is gated by the selected ReferenceSystem inventory, not by a hard-coded 39/24-book count.",
        },
        "sourcePins": pins,
        "coverage": {
            "oshb": {"wordRecords": oshb["rows"], "referenceSpans": len(oshb_refs)},
            "bhsa": {"wordNodes": bhsa["rows"], "referenceSpans": len(bhsa_refs)},
            "crosswalk": {
                "observedReferenceSpans": len(crosswalk_refs),
                "candidateMappings": crosswalk["candidateRecords"],
                "annotationOnlyNodes": crosswalk["annotationOnlyRecords"],
                "mappedSourceNodes": crosswalk["mappedSourceNodes"],
                "mappedTargetNodes": crosswalk["mappedTargetNodes"],
                "unresolvedReferenceSpans": len(crosswalk["unresolvedRefs"]),
                "unresolvedReasons": dict(sorted(crosswalk["unresolvedReasons"].items())),
                "recordTypes": dict(sorted(crosswalk["recordTypes"].items())),
            },
            "silentReferenceLoss": len(silent_reference_loss),
        },
        "exceptions": {
            "oshbMissingExpectedReferences": oshb_missing,
            "oshbProviderOnlyReferences": oshb_provider_only,
            "bhsaMissingExpectedReferences": bhsa_missing,
            "bhsaProviderOnlyReferences": bhsa_provider_only,
            "crosswalkMissingProviderReferences": crosswalk_missing,
            "crosswalkProviderOnlyReferences": crosswalk_provider_only,
            "silentReferenceLossReferences": silent_reference_loss,
            "unresolvedCrosswalkReferences": unresolved,
        },
        "perBook": [{"bookCode": book, **stats} for book, stats in sorted(by_book.items())],
        "artifacts": artifacts,
    }

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "buildId": build_id,
        "status": status,
        "gatePass": gate_pass,
        "expectedReferenceSpans": len(expected),
        "silentReferenceLoss": len(silent_reference_loss),
        "unresolvedReferenceSpans": len(crosswalk["unresolvedRefs"]),
    }, sort_keys=True))
    return 0 if gate_pass else 2


if __name__ == "__main__":
    raise SystemExit(main())
