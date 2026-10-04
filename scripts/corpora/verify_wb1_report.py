#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    parser=argparse.ArgumentParser(description="Verify WB-1 whole-corpus coverage evidence.")
    parser.add_argument("--report",type=Path,required=True)
    parser.add_argument("--canon",type=Path,required=True)
    parser.add_argument("--oshb-export-report",type=Path,required=True)
    parser.add_argument("--bhsa-export-report",type=Path,required=True)
    parser.add_argument("--crosswalk-report",type=Path,required=True)
    args=parser.parse_args()

    report=load(args.report)
    canon=load(args.canon)
    oshb=load(args.oshb_export_report)
    bhsa=load(args.bhsa_export_report)
    crosswalk=load(args.crosswalk_report)
    errors=[]

    expected_books=[
        b["osisCode"] for b in sorted(
            (b for b in canon["books"] if b.get("included")),
            key=lambda b:b["bookOrder"]
        )
    ]
    if report.get("milestone")!="WB-1": errors.append("milestone must be WB-1")
    if report.get("canonSystem",{}).get("code")!=canon["canonSystem"]["code"]: errors.append("canon system code mismatch")
    if report.get("canonSystem",{}).get("includedBooks")!=expected_books: errors.append("report canon book sequence mismatch")
    if len(expected_books)!=39: errors.append(f"configured canon must contain 39 split OSIS books, got {len(expected_books)}")

    totals=report.get("totals",{})
    if totals.get("configuredBooks")!=39: errors.append("configuredBooks != 39")
    if totals.get("importedBooks")!=39: errors.append("importedBooks != 39")
    if totals.get("oshbWordRecords")!=oshb.get("wordRecords"): errors.append("OSHB export/import total mismatch")
    if totals.get("bhsaWordRecords")!=bhsa.get("wordRecords"): errors.append("BHSA export/import total mismatch")
    if totals.get("candidateMappingGroups")!=crosswalk.get("totals",{}).get("candidateMappingGroups"): errors.append("crosswalk candidate total mismatch")
    if totals.get("unresolvedCrossFrameworkReferences")!=crosswalk.get("totals",{}).get("unresolvedReferences"): errors.append("crosswalk unresolved total mismatch")
    if totals.get("oshbMissingSurfaceRecords")!=0: errors.append("OSHB missing source surface is not accepted")
    if totals.get("servingCorpusRows")!=0: errors.append("WB-1 must not write real corpus rows to Serving")

    coverage=report.get("coverage",{})
    for key in (
        "missingConfiguredBooks","perBookDuplicateProviderIds",
        "crossBookDuplicateOshbProviderIds","crossBookDuplicateBhsaProviderIds",
        "parityFailures","importerErrors"
    ):
        if coverage.get(key): errors.append(f"coverage failure {key}: {coverage.get(key)}")

    gate=report.get("gate",{})
    if gate.get("sourceIngestionIntegrity") is not True: errors.append("sourceIngestionIntegrity gate not true")
    if gate.get("rightsBoundaryServingRemainsEmpty") is not True: errors.append("rights boundary gate not true")
    if gate.get("coreFreezeWb002EvidenceReady") is not True: errors.append("CORE-FZ-WB-002 evidence gate not true")
    if report.get("servingProjectionWritten") is not False: errors.append("servingProjectionWritten must be false")

    rows=report.get("books",[])
    if [row.get("book") for row in rows]!=expected_books: errors.append("per-book report order/coverage mismatch")
    for row in rows:
        code=row.get("book")
        source=row.get("source",{})
        expected=row.get("expectedImport",{})
        if source.get("oshbWordRecords",0)<=0: errors.append(f"{code}: empty OSHB source")
        if source.get("bhsaWordRecords",0)<=0: errors.append(f"{code}: empty BHSA source")
        if source.get("duplicateOshbProviderIds"): errors.append(f"{code}: duplicate OSHB provider IDs")
        if source.get("duplicateBhsaProviderIds"): errors.append(f"{code}: duplicate BHSA provider IDs")
        if source.get("oshbMissingSurfaceProviderIds"): errors.append(f"{code}: OSHB missing surface records")
        if expected.get("oshbWordNodes")!=source.get("oshbWordRecords"): errors.append(f"{code}: OSHB expected import mismatch")
        if expected.get("bhsaWordNodes")!=source.get("bhsaWordRecords"): errors.append(f"{code}: BHSA expected import mismatch")
        for unresolved in row.get("crosswalk",{}).get("unresolved",[]):
            if not unresolved.get("reason"): errors.append(f"{code}: unresolved mapping missing reason")

    if errors:
        print("WB-1 COVERAGE VERIFICATION FAILED")
        for error in errors:
            print(f"- {error}")
        return 1

    print(
        "WB-1 coverage verified: "
        f"books={totals['importedBooks']} "
        f"OSHB={totals['oshbWordRecords']} "
        f"BHSA={totals['bhsaWordRecords']} "
        f"refs={totals['canonicalReferenceAtoms']} "
        f"mappingGroups={totals['candidateMappingGroups']} "
        f"unresolvedMappings={totals['unresolvedCrossFrameworkReferences']}"
    )
    return 0


if __name__=="__main__":
    raise SystemExit(main())
