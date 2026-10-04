#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path

from reference_aliases import parse_reference_label

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_FOUNDATION = ROOT / ".local/whole-bible-corpus"
DEFAULT_CANON = ROOT / "contracts/v1.1/hebrew-bible-canon-system.json"


def sha256_file(path: Path) -> str:
    h=hashlib.sha256()
    with path.open("rb") as fh:
        for block in iter(lambda:fh.read(1024*1024),b""):
            h.update(block)
    return h.hexdigest()


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def included_books(canon: dict) -> list[dict]:
    books=sorted((b for b in canon["books"] if b.get("included")),key=lambda b:b["bookOrder"])
    if [b["bookOrder"] for b in books] != list(range(1,len(books)+1)):
        raise RuntimeError("selected CanonSystem order is not contiguous")
    return books


def main() -> int:
    parser=argparse.ArgumentParser(description="Partition accepted WB-CORPUS-001 artifacts into bounded per-book WB-1 inputs.")
    parser.add_argument("--foundation-dir",type=Path,default=DEFAULT_FOUNDATION)
    parser.add_argument("--canon",type=Path,default=DEFAULT_CANON)
    parser.add_argument("--output-dir",type=Path,required=True)
    parser.add_argument("--report",type=Path,required=True)
    args=parser.parse_args()

    foundation=args.foundation_dir
    manifest=load(foundation/"coverage-manifest.json")
    inventory=load(foundation/"reference-inventory.json")
    canon=load(args.canon)
    books=included_books(canon)
    codes=[b["osisCode"] for b in books]
    code_set=set(codes)

    if manifest.get("buildType")!="WB-CORPUS-001" or manifest.get("gatePass") is not True:
        raise SystemExit("WB-1 requires an accepted WB-CORPUS-001 source foundation")
    if inventory.get("referenceSystemCode")!="OSHB_OSIS":
        raise SystemExit("WB-1 currently requires the accepted OSHB_OSIS source inventory")

    inventory_codes={row["providerBookCode"] for row in inventory.get("bookDivisions",[])}
    missing_from_source=sorted(code_set-inventory_codes)
    unconfigured_source=sorted(inventory_codes-code_set)
    if missing_from_source or unconfigured_source:
        raise SystemExit(
            f"selected CanonSystem/source-book reconciliation failed: "
            f"missing_from_source={missing_from_source} unconfigured_source={unconfigured_source}"
        )

    artifacts={
        "oshb":foundation/"oshb.ndjson",
        "bhsa":foundation/"bhsa.ndjson",
        "crosswalk":foundation/"crosswalk.ndjson",
    }
    manifest_artifacts=manifest["artifacts"]
    artifact_keys={"oshb":"oshbExport","bhsa":"bhsaExport","crosswalk":"crosswalk"}
    for key,path in artifacts.items():
        if not path.is_file():
            raise SystemExit(f"WB-CORPUS-001 artifact missing: {path}")
        actual=sha256_file(path)
        expected=manifest_artifacts[artifact_keys[key]]["sha256"]
        if actual!=expected:
            raise SystemExit(f"WB-CORPUS-001 artifact hash mismatch for {key}: {actual} != {expected}")

    for kind in artifacts:
        (args.output_dir/kind).mkdir(parents=True,exist_ok=True)

    handles: dict[tuple[str,str],object]={}
    counts={code:{
        "oshbRows":0,"bhsaRows":0,"crosswalkRows":0,
        "candidateMappings":0,"annotationOnlyNodes":0,"unresolvedReferences":0,
    } for code in codes}
    refs={code:{"oshb":set(),"bhsa":set(),"crosswalk":set()} for code in codes}
    type_counts=Counter()

    def get_handle(kind: str, code: str):
        key=(kind,code)
        if key not in handles:
            handles[key]=(args.output_dir/kind/f"{code}.ndjson").open("w",encoding="utf-8")
        return handles[key]

    try:
        for kind,path in artifacts.items():
            with path.open(encoding="utf-8") as fh:
                for line_number,line in enumerate(fh,start=1):
                    if not line.strip():
                        continue
                    row=json.loads(line)
                    if kind=="crosswalk":
                        ref_obj=row.get("reference")
                        if not isinstance(ref_obj,dict):
                            raise RuntimeError(f"{path}:{line_number} crosswalk record missing reference")
                        code=str(ref_obj.get("book"))
                        ref=f"{code}.{int(ref_obj['chapter'])}.{int(ref_obj['verse'])}"
                        record_type=row.get("recordType")
                        if record_type not in {"CANDIDATE_SPAN_MAPPING","ANNOTATION_ONLY_TARGET_NODE","UNRESOLVED_REFERENCE"}:
                            raise RuntimeError(f"{path}:{line_number} unknown recordType {record_type!r}")
                        type_counts[record_type]+=1
                        if record_type=="CANDIDATE_SPAN_MAPPING": counts[code]["candidateMappings"]+=1
                        elif record_type=="ANNOTATION_ONLY_TARGET_NODE": counts[code]["annotationOnlyNodes"]+=1
                        else: counts[code]["unresolvedReferences"]+=1
                        counts[code]["crosswalkRows"]+=1
                        refs[code]["crosswalk"].add(ref)
                    else:
                        code,chapter,verse=parse_reference_label(str(row["referenceLabel"]))
                        ref=f"{code}.{chapter}.{verse}"
                        expected_key="OSHB_MORPHHB" if kind=="oshb" else "BHSA_2021"
                        if row.get("sourceKey")!=expected_key:
                            raise RuntimeError(f"{path}:{line_number} sourceKey drift")
                        counts[code][f"{kind}Rows"]+=1
                        refs[code][kind].add(ref)
                    if code not in code_set:
                        raise RuntimeError(f"{path}:{line_number} record resolved outside selected CanonSystem: {code}")
                    get_handle(kind,code).write(line if line.endswith("\n") else line+"\n")
    finally:
        for handle in handles.values():
            handle.close()

    for kind in artifacts:
        for code in codes:
            path=args.output_dir/kind/f"{code}.ndjson"
            if not path.is_file() or path.stat().st_size==0:
                raise SystemExit(f"WB-1 partition missing/empty {kind} book file: {code}")

    manifest_books={row["bookCode"]:row for row in manifest["perBook"]}
    per_book=[]
    errors=[]
    for book in books:
        code=book["osisCode"]
        source=manifest_books.get(code)
        if source is None:
            errors.append({"book":code,"kind":"SOURCE_MANIFEST_BOOK_MISSING"})
            continue
        observed=counts[code]
        expected_pairs={
            "oshbRows":source["oshbWords"],
            "bhsaRows":source["bhsaWordNodes"],
            "candidateMappings":None,
            "unresolvedReferences":source["unresolvedReferences"],
        }
        for key,wanted in expected_pairs.items():
            if wanted is not None and observed[key]!=wanted:
                errors.append({"book":code,"kind":key,"expected":wanted,"actual":observed[key]})
        if len(refs[code]["oshb"])!=source["oshbReferences"]:
            errors.append({"book":code,"kind":"oshbReferences","expected":source["oshbReferences"],"actual":len(refs[code]["oshb"])})
        if len(refs[code]["bhsa"])!=source["bhsaReferences"]:
            errors.append({"book":code,"kind":"bhsaReferences","expected":source["bhsaReferences"],"actual":len(refs[code]["bhsa"])})
        if len(refs[code]["crosswalk"])!=source["crosswalkObservedReferences"]:
            errors.append({"book":code,"kind":"crosswalkObservedReferences","expected":source["crosswalkObservedReferences"],"actual":len(refs[code]["crosswalk"])})
        per_book.append({
            "book":code,"bookOrder":book["bookOrder"],
            **observed,
            "oshbReferences":len(refs[code]["oshb"]),
            "bhsaReferences":len(refs[code]["bhsa"]),
            "crosswalkObservedReferences":len(refs[code]["crosswalk"]),
            "hashes":{
                kind:sha256_file(args.output_dir/kind/f"{code}.ndjson")
                for kind in artifacts
            }
        })

    total_oshb=sum(row["oshbRows"] for row in per_book)
    total_bhsa=sum(row["bhsaRows"] for row in per_book)
    total_candidate=sum(row["candidateMappings"] for row in per_book)
    total_unresolved=sum(row["unresolvedReferences"] for row in per_book)
    if total_oshb!=manifest["coverage"]["oshb"]["wordRecords"]:
        errors.append({"kind":"TOTAL_OSHB","expected":manifest["coverage"]["oshb"]["wordRecords"],"actual":total_oshb})
    if total_bhsa!=manifest["coverage"]["bhsa"]["wordNodes"]:
        errors.append({"kind":"TOTAL_BHSA","expected":manifest["coverage"]["bhsa"]["wordNodes"],"actual":total_bhsa})
    if total_candidate!=manifest["coverage"]["crosswalk"]["candidateMappings"]:
        errors.append({"kind":"TOTAL_CANDIDATES","expected":manifest["coverage"]["crosswalk"]["candidateMappings"],"actual":total_candidate})
    if total_unresolved!=manifest["coverage"]["crosswalk"]["unresolvedReferenceSpans"]:
        errors.append({"kind":"TOTAL_UNRESOLVED","expected":manifest["coverage"]["crosswalk"]["unresolvedReferenceSpans"],"actual":total_unresolved})

    report={
        "schemaVersion":"1.0",
        "sourceBuildId":manifest["buildId"],
        "sourceCoverageManifestSha256":sha256_file(foundation/"coverage-manifest.json"),
        "sourceReferenceInventorySha256":sha256_file(foundation/"reference-inventory.json"),
        "selectedCanonSystem":canon["canonSystem"],
        "books":per_book,
        "totals":{
            "books":len(per_book),
            "oshbRows":total_oshb,
            "bhsaRows":total_bhsa,
            "candidateMappings":total_candidate,
            "annotationOnlyNodes":sum(row["annotationOnlyNodes"] for row in per_book),
            "unresolvedReferences":total_unresolved,
        },
        "crosswalkRecordTypes":dict(sorted(type_counts.items())),
        "reconciliationErrors":errors,
        "pass":not errors,
    }
    args.report.parent.mkdir(parents=True,exist_ok=True)
    args.report.write_text(json.dumps(report,ensure_ascii=False,sort_keys=True,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({"sourceBuildId":report["sourceBuildId"],"totals":report["totals"],"pass":report["pass"]},sort_keys=True))
    return 0 if not errors else 2


if __name__=="__main__":
    raise SystemExit(main())
