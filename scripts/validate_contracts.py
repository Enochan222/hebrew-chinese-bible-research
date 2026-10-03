#!/usr/bin/env python3
from __future__ import annotations
import json, re, sys
from pathlib import Path
from typing import Any
from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
ERRORS: list[str] = []

def fail(msg: str) -> None:
    ERRORS.append(msg)

def load(path: str) -> Any:
    return json.loads((ROOT / path).read_text(encoding="utf-8"))

def schema_errors(schema_path: str, fixture_path: str) -> list[str]:
    schema, fixture = load(schema_path), load(fixture_path)
    return [f"{fixture_path}: {e.message}" for e in Draft202012Validator(schema, format_checker=FormatChecker()).iter_errors(fixture)]

POSITIVE = [
 ("contracts/v1.1/json-schema/corpus-query.schema.json","contracts/v1.1/fixtures/corpus-query-1sam16-7.json"),
 ("contracts/v1.1/json-schema/corpus-query-normalized.schema.json","contracts/v1.1/fixtures/corpus-query-1sam16-7.json"),
 ("contracts/v1.1/json-schema/release-manifest.schema.json","contracts/v1.1/fixtures/release-manifest.json"),
 ("contracts/v1.1/json-schema/rights-decision-snapshot.schema.json","contracts/v1.1/fixtures/rights-decision-deny-persist.json"),
 ("contracts/v1.1/json-schema/rights-decision-snapshot.schema.json","contracts/v1.1/fixtures/rights-decision-allow-persist.json"),
 ("contracts/v1.1/json-schema/rights-decision-snapshot.schema.json","contracts/v1.1/fixtures/rights-decision-default-deny.json"),
 ("contracts/v1.1/json-schema/published-passage-analysis.schema.json","contracts/v1.1/fixtures/published-passage-analysis.json"),
 ("contracts/v1.1/json-schema/translation-decision.schema.json","contracts/v1.1/fixtures/translation-decision.json"),
 ("contracts/v1.1/json-schema/annotation-layer.schema.json","contracts/v1.1/fixtures/annotation-layer-morpheme.json"),
 ("contracts/v1.1/json-schema/annotation-layer.schema.json","contracts/v1.1/fixtures/annotation-layer-morphology.json"),
 ("contracts/v1.1/json-schema/annotation-layer.schema.json","contracts/v1.1/fixtures/annotation-layer-clause.json"),
 ("contracts/v1.1/json-schema/provider-witness-binding.schema.json","contracts/v1.1/fixtures/provider-witness-snapshot.json"),
 ("contracts/v1.1/json-schema/provider-witness-binding.schema.json","contracts/v1.1/fixtures/provider-witness-live.json"),
 ("contracts/v1.1/json-schema/release-event.schema.json","contracts/v1.1/fixtures/release-event-published.json"),
 ("contracts/v1.1/json-schema/release-channel-pointer.schema.json","contracts/v1.1/fixtures/release-channel-production.json"),
 ("contracts/v1.1/json-schema/semantic-set-version.schema.json","contracts/v1.1/fixtures/semantic-set-body-part.json"),
 ("contracts/v1.1/json-schema/construction-compilation-run.schema.json","contracts/v1.1/fixtures/construction-compilation-run.json"),
 ("contracts/v1.1/json-schema/construction-instance.schema.json","contracts/v1.1/fixtures/construction-instance-1sam16-7.json"),
 ("contracts/v1.1/json-schema/rule-application.schema.json","contracts/v1.1/fixtures/rule-application-1sam16-7.json"),
 ("contracts/v1.1/json-schema/published-evidence-item.schema.json","contracts/v1.1/fixtures/published-evidence-item.json"),
 ("contracts/v1.1/json-schema/query-execution-policy.schema.json","contracts/v1.1/fixtures/query-execution-policy.json"),
 ("contracts/v1.1/json-schema/research-target.schema.json","contracts/v1.1/fixtures/research-target-1sam16-7.json"),
 ("contracts/v1.1/json-schema/research-issue-version.schema.json","contracts/v1.1/fixtures/research-issue-version.json"),
 ("contracts/v1.1/json-schema/research-position-version.schema.json","contracts/v1.1/fixtures/research-position-version.json"),
 ("contracts/v1.1/json-schema/literature-snapshot.schema.json","contracts/v1.1/fixtures/literature-snapshot.json"),
 ("contracts/v1.1/json-schema/commentary-entry.schema.json","contracts/v1.1/fixtures/commentary-entry.json"),
 ("contracts/v1.1/json-schema/discovery-record.schema.json","contracts/v1.1/fixtures/discovery-record.json"),
 ("contracts/v1.1/json-schema/experience-capabilities.schema.json","contracts/v1.1/fixtures/experience-capabilities.json"),
 ("contracts/v1.1/json-schema/product-entitlement.schema.json","contracts/v1.1/fixtures/product-entitlement.json"),
 ("contracts/v1.1/json-schema/research-model-run.schema.json","contracts/v1.1/fixtures/research-model-run.json"),
 ("contracts/v1.1/json-schema/scholarly-provider-request.schema.json","contracts/v1.1/fixtures/scholarly-provider-request.json"),
]

NEG_SCHEMA = [
 ("contracts/v1.1/json-schema/corpus-query.schema.json","contracts/v1.1/negative-fixtures/corpus-query-empty-bind.json"),
 ("contracts/v1.1/json-schema/rights-decision-snapshot.schema.json","contracts/v1.1/negative-fixtures/rights-default-deny-with-winner.json"),
]

UUID = re.compile(r"^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[1-5][0-9a-fA-F]{3}-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}$")

def walk(x: Any):
    if not isinstance(x, dict): return
    yield x
    for y in x.get("children", []): yield from walk(y)
    if "child" in x: yield from walk(x["child"])

def query_semantic(q: dict) -> list[str]:
    out=[]
    nodes={n["id"] for n in q.get("nodes",[])}
    layers={x["annotationLayerId"] for x in q.get("analysisContext",{}).get("layers",[])}
    for x in walk(q.get("expression")):
        if x.get("predicateType")=="NODE_CONSTRAINT":
            if x.get("nodeId") not in nodes: out.append("unknown node")
            if x.get("annotationLayerId") and x["annotationLayerId"] not in layers: out.append("undeclared layer")
            field,op,val=x.get("field"),x.get("operator"),x.get("value")
            if field=="FEATURE" and not x.get("featureKey"): out.append("FEATURE needs featureKey")
            if field in {"LEXEME_ID","SEMANTIC_SET_VERSION_ID","REFERENCE_SPAN_ID"}:
                vals=val if isinstance(val,list) else [val]
                if not vals or any(not isinstance(v,str) or not UUID.match(v) for v in vals): out.append("ID field needs UUID")
            if op in {"IN","NOT_IN"} and (not isinstance(val,list) or not val): out.append("IN needs array")
            if op in {"EQ","NEQ","GT","GTE","LT","LTE"} and isinstance(val,list): out.append("scalar op got array")
            if op in {"GT","GTE","LT","LTE"} and isinstance(val,bool): out.append("ordered comparison on boolean")
        elif x.get("predicateType")=="RELATION":
            if x.get("from") not in nodes or x.get("to") not in nodes: out.append("unknown relation node")
            if x.get("annotationLayerId") and x["annotationLayerId"] not in layers: out.append("relation undeclared layer")
            if x.get("relationType")=="WITHIN_N_SEGMENTS" and "maxDistance" not in x: out.append("distance missing")
        if x.get("operator") in {"EXISTS","NOT_EXISTS","MIN_COUNT","MAX_COUNT","EXACT_COUNT"}:
            if not x.get("bind"): out.append("empty quantifier bind")
            if any(b not in nodes for b in x.get("bind",[])): out.append("unknown quantifier bind")
    return out

def translation_semantic(d: dict) -> list[str]:
    out=[]
    ids=[x["candidateId"] for x in d.get("candidateRenderings",[])]
    if len(ids)!=len(set(ids)): out.append("duplicate candidateId")
    selected=[x for x in d.get("candidateRenderings",[]) if x.get("status")=="SELECTED"]
    sr=d.get("selectedRendering")
    if sr is None and selected: out.append("selected candidate with null selectedRendering")
    if sr is not None:
        if len(selected)!=1: out.append("resolved decision needs exactly one SELECTED")
        elif selected[0].get("rendering")!=sr: out.append("selected rendering mismatch")
    return out

def manifest_semantic(d: dict) -> list[str]:
    orders=[x.get("componentOrder") for x in d.get("components",[])]
    if any(x is None for x in orders): return ["missing componentOrder"]
    if len(orders)!=len(set(orders)): return ["duplicate componentOrder"]
    if sorted(orders)!=list(range(len(orders))): return ["componentOrder not contiguous"]
    return []

def rights_semantic(d: dict) -> list[str]:
    if d.get("decisionBasis")=="RULE" and not d.get("winningRuleIds"): return ["RULE without winner"]
    if d.get("decisionBasis")=="DEFAULT_DENY" and (d.get("winningRuleIds") or d.get("decision")!="DENY"): return ["bad DEFAULT_DENY"]
    return []

def validate_fixtures():
    for s,f in POSITIVE:
        errs=schema_errors(s,f)
        ERRORS.extend(errs)
        if errs: continue
        d=load(f)
        if "corpus-query-1sam16-7" in f: ERRORS.extend(f"{f}: {e}" for e in query_semantic(d))
        if f.endswith("translation-decision.json"): ERRORS.extend(f"{f}: {e}" for e in translation_semantic(d))
        if f.endswith("release-manifest.json"): ERRORS.extend(f"{f}: {e}" for e in manifest_semantic(d))
        if "rights-decision-" in f: ERRORS.extend(f"{f}: {e}" for e in rights_semantic(d))
    for s,f in NEG_SCHEMA:
        if not schema_errors(s,f): fail(f"{f}: expected schema rejection")
    semantic_neg=[
      ("contracts/v1.1/negative-fixtures/corpus-query-invalid-id-value.json",query_semantic),
      ("contracts/v1.1/negative-fixtures/translation-decision-two-selected.json",translation_semantic),
      ("contracts/v1.1/negative-fixtures/translation-decision-selected-mismatch.json",translation_semantic),
      ("contracts/v1.1/negative-fixtures/release-manifest-duplicate-order.json",manifest_semantic),
    ]
    for f,fn in semantic_neg:
        if not fn(load(f)): fail(f"{f}: expected semantic rejection")

def governance():
    m=load("architecture/manifest.json")
    for group in ("active","superseded","historical","currentValidation"):
        for p in m.get(group,[]):
            if not (ROOT/p).exists(): fail(f"manifest missing {p}")
    ids={}
    for p in (ROOT/"architecture/adr").glob("*.md"):
        hit=re.search(r"^# ADR-(\d+):",p.read_text(encoding="utf-8"),re.M)
        if hit: ids.setdefault(hit.group(1),[]).append(str(p.relative_to(ROOT)))
    for n,paths in ids.items():
        if len(paths)>1: fail(f"duplicate ADR-{n}: {paths}")
    text=(ROOT/"contracts/v1.1/freeze-checklist.md").read_text(encoding="utf-8")
    gates=re.findall(r"\|\s*([A-Z]+(?:-[A-Z]+)*-\d{3})\s*\|",text)
    for g in set(gates):
        if gates.count(g)>1: fail(f"duplicate freeze gate {g}")
    if not (ROOT/"PROJECT_STATE.md").exists(): fail("PROJECT_STATE.md missing")
    if not (ROOT/"CHANGELOG.md").exists(): fail("CHANGELOG.md missing")
    if "PROJECT_STATE.md" not in m.get("active",[]): fail("PROJECT_STATE.md must be active living authority")
    if "PROJECT_CHARTER.md" not in m.get("active",[]): fail("PROJECT_CHARTER.md must be active architecture authority")
    charter=(ROOT/"PROJECT_CHARTER.md").read_text(encoding="utf-8")
    for required in ("# 1. Product mission","# 13. Explicit non-goals","# 15. Fixed requirements versus open decisions"):
        if required not in charter: fail(f"project charter missing canonical section {required}")
    readme=(ROOT/"README.md").read_text(encoding="utf-8")
    if "PROJECT_CHARTER.md" not in readme: fail("README must point to project charter")
    active=(ROOT/"architecture/database-api-cross-stage-contract-v1.1.md").read_text(encoding="utf-8")
    if "Expand " + chr(96) + "works.work_type" + chr(96) in active: fail("stale mixed work_type section")
    tax=(ROOT/"docs/academic-source-taxonomy.md").read_text(encoding="utf-8")
    for stale in ("VERIFIED_OPEN","LICENSED_FOR_INDEXING","LICENSED_PRIVATE_ONLY","USER_SUPPLIED_RESEARCH_ONLY"):
        if stale in tax: fail(f"stale source status {stale}")

def vocab_drift():
    v=load("contracts/v1.1/vocabulary.json")
    q=load("contracts/v1.1/json-schema/corpus-query.schema.json")
    if set(v["queryNodeType"])!=set(q["properties"]["nodes"]["items"]["properties"]["nodeType"]["enum"]): fail("queryNodeType drift")
    if set(v["queryConstraintOperator"])!=set(q["$defs"]["nodeConstraint"]["properties"]["operator"]["enum"]): fail("queryConstraintOperator drift")
    r=load("contracts/v1.1/json-schema/rights-decision-snapshot.schema.json")
    for key,prop in [("rightsOperation","operation"),("rightsPurposeScope","purposeScope"),("rightsAudienceScope","audienceScope"),("rightsCommercialContext","commercialContext"),("rightsDecisionBasis","decisionBasis")]:
        if set(v[key])!=set(r["properties"][prop]["enum"]): fail(f"{key} drift")
    rm=load("contracts/v1.1/json-schema/release-manifest.schema.json")
    if set(v["releaseComponentKind"])!=set(rm["properties"]["components"]["items"]["properties"]["componentKind"]["enum"]): fail("releaseComponentKind drift")
    ri=load("contracts/v1.1/json-schema/research-issue-version.schema.json")
    if set(v["researchDebateStatus"])!=set(ri["properties"]["debateStatus"]["enum"]): fail("researchDebateStatus drift")
    rm=load("contracts/v1.1/json-schema/research-model-run.schema.json")
    if set(v["researchModelTaskType"])!=set(rm["properties"]["taskType"]["enum"]): fail("researchModelTaskType drift")
    if set(v["researchModelRunStatus"])!=set(rm["properties"]["status"]["enum"]): fail("researchModelRunStatus drift")
    spr=load("contracts/v1.1/json-schema/scholarly-provider-request.schema.json")
    if set(v["scholarlyDiscoveryProviderKey"])!=set(spr["properties"]["providerKey"]["enum"]): fail("scholarlyDiscoveryProviderKey drift")
    if set(v["scholarlyDiscoveryTransportMode"])!=set(spr["properties"]["transportMode"]["enum"]): fail("scholarlyDiscoveryTransportMode drift")
    if set(v["scholarlyProviderRequestStatus"])!=set(spr["properties"]["status"]["enum"]): fail("scholarlyProviderRequestStatus drift")
    method=load("contracts/v1.1/scholarly-research-method.json")
    if method.get("searchMatrix")!=["TEXT","TOPIC","LENS"]: fail("Sacred Studies search matrix drift")
    qo=method.get("queryOptimization",{})
    if qo.get("keyTermsOrPhrasesMin")!=3 or qo.get("keyTermsOrPhrasesMax")!=6: fail("Sacred Studies query term-count drift")
    cr=method.get("criticalReview",{})
    if cr.get("passThreshold")!=88 or cr.get("maxAttempts")!=3: fail("Sacred Studies review-loop drift")
    if cr.get("malformedReviewerOutput")!="REVIEW_INCOMPLETE": fail("reviewer parse failure must not auto-pass")
    if method.get("modelBoundary",{}).get("vendorLocked") is not False: fail("research build model must remain vendor-neutral")
    reg=load("contracts/v1.1/scholarly-provider-registry.json")
    required={"OPENALEX","SEMANTIC_SCHOLAR","CORE","CROSSREF","SCITE"}
    registered={p["providerKey"] for p in reg.get("providers",[]) if p.get("requiredInFirstImplementation")}
    if registered!=required: fail(f"initial scholarly provider ensemble drift: {registered}")
    if "GEMINI" in rm["properties"]["modelProvider"].get("enum",[]): fail("research model provider must not be Gemini-locked")

def secret_scan():
    assignment=re.compile(r"(?i)\b(GEMINI_API_KEY|GOOGLE_API_KEY|OPENAI_API_KEY|ANTHROPIC_API_KEY|SCITE_API_KEY|CORE_API_KEY|SEMANTIC_SCHOLAR_API_KEY|OPENALEX_API_KEY)\s*=\s*[\"']?([A-Za-z0-9_\-]{8,})")
    literals=[re.compile(r"AIza[0-9A-Za-z_\-]{30,}"),re.compile(r"sk-[A-Za-z0-9_\-]{20,}"),re.compile(r"scite_[A-Za-z0-9_\-]{20,}")]
    for p in ROOT.rglob("*"):
        if not p.is_file() or ".git" in p.parts: continue
        rel=p.relative_to(ROOT)
        if rel.name in {".env",".env.local",".env.production",".env.development"}: fail(f"forbidden env file {rel}")
        if p.suffix.lower() not in {".md",".json",".yaml",".yml",".py",".ts",".tsx",".js",".jsx",".toml",".txt"}: continue
        try: t=p.read_text(encoding="utf-8")
        except UnicodeDecodeError: continue
        if assignment.search(t): fail(f"possible model-secret assignment {rel}")
        for pat in literals:
            if pat.search(t): fail(f"possible model-secret literal {rel}")

def main() -> int:
    validate_fixtures(); governance(); vocab_drift(); secret_scan()
    if ERRORS:
        print("CONTRACT VALIDATION FAILED")
        for e in ERRORS: print(" -",e)
        return 1
    print(f"CONTRACT VALIDATION PASSED: {len(POSITIVE)} positive fixtures + negative/semantic/governance checks")
    return 0

if __name__=="__main__":
    sys.exit(main())
