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
    parser.add_argument("--source-foundation-manifest",type=Path,required=True)
    parser.add_argument("--partition-report",type=Path,required=True)
    args=parser.parse_args()

    report=load(args.report)
    canon=load(args.canon)
    foundation=load(args.source_foundation_manifest)
    partition=load(args.partition_report)
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
    if report.get("sourceFoundation",{}).get("buildId")!=foundation.get("buildId"): errors.append("source foundation buildId mismatch")
    if foundation.get("gatePass") is not True: errors.append("source foundation gatePass is not true")
    if foundation.get("coverage",{}).get("silentReferenceLoss")!=0: errors.append("source foundation has silent reference loss")
    if partition.get("pass") is not True or partition.get("sourceBuildId")!=foundation.get("buildId"): errors.append("partition evidence mismatch")

    totals=report.get("totals",{})
    configured=len(expected_books)
    if totals.get("configuredBooks")!=configured: errors.append("configuredBooks mismatch selected CanonSystem")
    if totals.get("importedBooks")!=configured: errors.append("importedBooks mismatch selected CanonSystem")
    if totals.get("oshbWordRecords")!=foundation["coverage"]["oshb"]["wordRecords"]: errors.append("OSHB foundation/import total mismatch")
    if totals.get("bhsaWordRecords")!=foundation["coverage"]["bhsa"]["wordNodes"]: errors.append("BHSA foundation/import total mismatch")
    if totals.get("candidateMappingGroups")!=foundation["coverage"]["crosswalk"]["candidateMappings"]: errors.append("crosswalk candidate total mismatch")
    if totals.get("unresolvedCrossFrameworkReferences")!=foundation["coverage"]["crosswalk"]["unresolvedReferenceSpans"]: errors.append("crosswalk unresolved total mismatch")
    if totals.get("selectedReferenceAtoms")!=foundation["referenceSystem"]["expectedReferenceSpans"]: errors.append("selected ReferenceAtom total mismatch source inventory")
    expected_provider_only=len(foundation.get("exceptions",{}).get("bhsaProviderOnlyReferences",[]))
    if totals.get("providerOnlyReferenceAtoms")!=expected_provider_only: errors.append("providerOnlyReferenceAtoms mismatch source exceptions")
    if totals.get("relationalReferenceAtoms") != totals.get("selectedReferenceAtoms",0) + totals.get("providerOnlyReferenceAtoms",0):
        errors.append("relationalReferenceAtoms must equal selected + provider-only atoms")
    if totals.get("reviewedAnnotationOnlyBhsaNodes")!=foundation["coverage"]["crosswalk"]["annotationOnlyNodes"]:
        errors.append("reviewed annotation-only BHSA node total mismatch source foundation")
    if totals.get("unresolvedCrossFrameworkReferences")!=len(foundation.get("exceptions",{}).get("unresolvedCrosswalkReferences",[])):
        errors.append("unresolved reference count mismatch exception inventory")
    for exception_key in (
        "oshbMissingExpectedReferences","oshbProviderOnlyReferences",
        "bhsaMissingExpectedReferences","crosswalkMissingProviderReferences",
        "crosswalkProviderOnlyReferences","silentReferenceLossReferences",
    ):
        if foundation.get("exceptions",{}).get(exception_key):
            errors.append(f"source foundation contains non-empty {exception_key}: {foundation['exceptions'][exception_key]}")
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
        if expected.get("oshbTextSegments") != source.get("oshbWordRecords",0) - len(source.get("oshbMissingSurfaceProviderIds",[])):
            errors.append(f"{code}: OSHB segment/source arithmetic mismatch")
        expected_bhsa_segments = (
            source.get("bhsaWordRecords",0)
            - len(source.get("reviewedAnnotationOnlyBhsaProviderIds",[]))
            - len(source.get("unclassifiedEmptyBhsaProviderIds",[]))
        )
        if expected.get("bhsaTextSegments") != expected_bhsa_segments:
            errors.append(f"{code}: BHSA segment/source arithmetic mismatch")
        if row.get("crosswalk",{}).get("annotationOnlyRecordsEmitted") != len(source.get("reviewedAnnotationOnlyBhsaProviderIds",[])):
            errors.append(f"{code}: annotation-only crosswalk/source classification mismatch")
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
        f"selected_refs={totals['selectedReferenceAtoms']} "
        f"mappingGroups={totals['candidateMappingGroups']} "
        f"unresolvedMappings={totals['unresolvedCrossFrameworkReferences']}"
    )
    return 0


if __name__=="__main__":
    raise SystemExit(main())
