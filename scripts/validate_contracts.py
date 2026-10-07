#!/usr/bin/env python3
from __future__ import annotations
import json, re, sys
from pathlib import Path
from typing import Any
import yaml
from jsonschema import Draft202012Validator, FormatChecker
from referencing import Registry, Resource

ROOT = Path(__file__).resolve().parents[1]
ERRORS: list[str] = []

def fail(msg: str) -> None:
    ERRORS.append(msg)

def load(path: str) -> Any:
    return json.loads((ROOT / path).read_text(encoding="utf-8"))

def build_schema_registry() -> Registry:
    registry = Registry()
    for path in (ROOT / "contracts/v1.1/json-schema").glob("*.json"):
        schema = json.loads(path.read_text(encoding="utf-8"))
        Draft202012Validator.check_schema(schema)
        schema_id = schema.get("$id")
        if schema_id:
            registry = registry.with_resource(schema_id, Resource.from_contents(schema))
    return registry

SCHEMA_REGISTRY = build_schema_registry()

def schema_errors(schema_path: str, fixture_path: str) -> list[str]:
    schema, fixture = load(schema_path), load(fixture_path)
    return [f"{fixture_path}: {e.message}" for e in Draft202012Validator(schema, registry=SCHEMA_REGISTRY, format_checker=FormatChecker()).iter_errors(fixture)]

POSITIVE = [
 ("contracts/v1.1/json-schema/corpus-source-registry.schema.json","contracts/v1.1/corpus-source-registry.json"),
 ("contracts/v1.1/json-schema/github-ai-usage-policy.schema.json","contracts/v1.1/github-ai-usage-policy.json"),
 ("contracts/v1.1/json-schema/whole-bible-corpus-build-manifest.schema.json","contracts/v1.1/fixtures/whole-bible-corpus-build-manifest.json"),
 ("contracts/v1.1/json-schema/hebrew-bible-canon-system.schema.json","contracts/v1.1/hebrew-bible-canon-system.json"),
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
 ("contracts/v1.1/json-schema/translation-witness-list.schema.json","contracts/v1.1/fixtures/translation-witness-list.json"),
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
 ("contracts/v1.1/json-schema/scholarly-provider-request.schema.json","contracts/v1.1/fixtures/scholarly-provider-request.json"), ("contracts/v1.1/json-schema/passage-locator.schema.json","contracts/v1.1/fixtures/passage-locator-label.json"),
 ("contracts/v1.1/json-schema/passage-request.schema.json","contracts/v1.1/fixtures/passage-request.json"),
 ("contracts/v1.1/json-schema/passage-core.schema.json","contracts/v1.1/fixtures/passage-core.json"),
 ("contracts/v1.1/json-schema/corpus-query-execution-request.schema.json","contracts/v1.1/fixtures/corpus-query-execution-request.json"),
 ("contracts/v1.1/json-schema/corpus-query-result.schema.json","contracts/v1.1/fixtures/corpus-query-result.json"),
 ("contracts/v1.1/json-schema/translation-source-basis.schema.json","contracts/v1.1/fixtures/translation-source-basis.json"),
 ("contracts/v1.1/json-schema/translation-policy-version.schema.json","contracts/v1.1/fixtures/translation-policy-version.json"),
 ("contracts/v1.1/json-schema/rights-decision-snapshot.schema.json","contracts/v1.1/fixtures/rights-decision-conditional.json"),
 ("contracts/v1.1/json-schema/rule-applications-request.schema.json","contracts/v1.1/fixtures/rule-applications-request.json"),

]

NEG_SCHEMA = [
 ("contracts/v1.1/json-schema/corpus-query.schema.json","contracts/v1.1/negative-fixtures/corpus-query-empty-bind.json"),
 ("contracts/v1.1/json-schema/rights-decision-snapshot.schema.json","contracts/v1.1/negative-fixtures/rights-default-deny-with-winner.json"), ("contracts/v1.1/json-schema/rights-decision-snapshot.schema.json","contracts/v1.1/negative-fixtures/rights-unknown-restrictive-allow.json"),
 ("contracts/v1.1/json-schema/rights-decision-snapshot.schema.json","contracts/v1.1/negative-fixtures/rights-conditional-empty.json"),
 ("contracts/v1.1/json-schema/rights-decision-snapshot.schema.json","contracts/v1.1/negative-fixtures/rights-max-excerpt-missing-unit.json"),
 ("contracts/v1.1/json-schema/rights-decision-snapshot.schema.json","contracts/v1.1/negative-fixtures/rights-unregistered-condition.json"),
 ("contracts/v1.1/json-schema/published-evidence-item.schema.json","contracts/v1.1/negative-fixtures/published-evidence-excerpt-without-rights.json"),
 ("contracts/v1.1/json-schema/published-evidence-item.schema.json","contracts/v1.1/negative-fixtures/published-evidence-immutable-without-hash.json"),
 ("contracts/v1.1/json-schema/discovery-record.schema.json","contracts/v1.1/negative-fixtures/discovery-persisted-without-rights.json"),
 ("contracts/v1.1/json-schema/translation-source-basis.schema.json","contracts/v1.1/negative-fixtures/translation-source-basis-emendation-without-reading.json"),
 ("contracts/v1.1/json-schema/provider-witness-binding.schema.json","contracts/v1.1/negative-fixtures/provider-witness-snapshot-null-hash.json"),
 ("contracts/v1.1/json-schema/translation-witness-list.schema.json","contracts/v1.1/negative-fixtures/translation-witness-list-extra-field.json"),
 ("contracts/v1.1/json-schema/translation-witness-list.schema.json","contracts/v1.1/negative-fixtures/translation-witness-displayable-without-segments.json"),
 ("contracts/v1.1/json-schema/translation-witness-list.schema.json","contracts/v1.1/negative-fixtures/translation-witness-not-covered-with-segments.json"),
 ("contracts/v1.1/json-schema/translation-witness-list.schema.json","contracts/v1.1/negative-fixtures/translation-witness-rights-restricted-with-segments.json"),
 ("contracts/v1.1/json-schema/citation-locator.schema.json","contracts/v1.1/negative-fixtures/citation-locator-source-span-missing-id.json"),
 ("contracts/v1.1/json-schema/rights-decision-snapshot.schema.json","contracts/v1.1/negative-fixtures/rights-snapshot-unknown-final-decision.json"),
 ("contracts/v1.1/json-schema/corpus-query-result.schema.json","contracts/v1.1/negative-fixtures/corpus-query-result-nonexact-with-total.json"),
 ("contracts/v1.1/json-schema/translation-source-basis.schema.json","contracts/v1.1/negative-fixtures/translation-source-basis-stream-with-apparatus.json"),
 ("contracts/v1.1/json-schema/published-evidence-item.schema.json","contracts/v1.1/negative-fixtures/published-evidence-excerpt-without-citation.json"),
 ("contracts/v1.1/json-schema/citation-locator.schema.json","contracts/v1.1/negative-fixtures/citation-locator-source-span-null-id.json"),
 ("contracts/v1.1/json-schema/citation-locator.schema.json","contracts/v1.1/negative-fixtures/citation-locator-printed-page-null-edition.json"),
 ("contracts/v1.1/json-schema/citation-locator.schema.json","contracts/v1.1/negative-fixtures/citation-locator-printed-page-empty-label.json"),
 ("contracts/v1.1/json-schema/citation-locator.schema.json","contracts/v1.1/negative-fixtures/citation-locator-source-asset-page-null-id.json"),
 ("contracts/v1.1/json-schema/citation-locator.schema.json","contracts/v1.1/negative-fixtures/citation-locator-biblical-reference-null-id.json"),
 ("contracts/v1.1/json-schema/citation-locator.schema.json","contracts/v1.1/negative-fixtures/citation-locator-corpus-result-null-id.json"),
 ("contracts/v1.1/json-schema/citation-locator.schema.json","contracts/v1.1/negative-fixtures/citation-locator-document-section-null-edition.json"),
 ("contracts/v1.1/json-schema/citation-locator.schema.json","contracts/v1.1/negative-fixtures/citation-locator-lexicon-entry-null-edition.json"),
 ("contracts/v1.1/json-schema/rule-applications-request.schema.json","contracts/v1.1/negative-fixtures/rule-applications-label-without-reference-system.json"),

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

def translation_witness_semantic(d: dict) -> list[str]:
    out=[]
    witnesses=d.get("witnesses",[])
    expression_ids=[w.get("digitalExpressionId") for w in witnesses]
    if len(expression_ids)!=len(set(expression_ids)): out.append("duplicate DigitalExpression witness")
    for witness in witnesses:
        segments=witness.get("segments",[])
        orders=[segment.get("segmentOrder") for segment in segments]
        if orders!=list(range(len(segments))): out.append("translation segmentOrder must be contiguous from 0")
        segment_ids=[segment.get("textSegmentId") for segment in segments]
        if len(segment_ids)!=len(set(segment_ids)): out.append("duplicate translation TextSegment")
    return out

def hebrew_bible_canon_semantic(d: dict) -> list[str]:
    out=[]
    books=d.get("books",[])
    included=[b for b in books if b.get("included")]
    codes=[b.get("osisCode") for b in included]
    orders=[b.get("bookOrder") for b in included]
    if len(codes)!=len(set(codes)): out.append("duplicate included canon osisCode")
    if len(orders)!=len(set(orders)): out.append("duplicate included canon bookOrder")
    if sorted(orders)!=list(range(1,len(included)+1)): out.append("included canon bookOrder must be contiguous from 1")
    expected=[
        "Gen","Exod","Lev","Num","Deut","Josh","Judg","1Sam","2Sam","1Kgs","2Kgs",
        "Isa","Jer","Ezek","Hos","Joel","Amos","Obad","Jonah","Mic","Nah","Hab","Zeph","Hag","Zech","Mal",
        "Ps","Job","Prov","Ruth","Song","Eccl","Lam","Esth","Dan","Ezra","Neh","1Chr","2Chr"
    ]
    if codes!=expected: out.append("selected TANAKH_OSIS_39 order drift")
    if d.get("canonSystem",{}).get("code")!="TANAKH_OSIS_39": out.append("selected CanonSystem code drift")
    return out

def github_ai_usage_policy_semantic(d: dict) -> list[str]:
    out=[]
    copilot=d.get("githubCopilot",{})
    if copilot.get("authorized") is not False: out.append("GitHub Copilot must remain unauthorized")
    if copilot.get("automaticCodeReview") is not False: out.append("automatic Copilot code review must remain disabled")
    prohibited=set(copilot.get("prohibitedOperations",[]))
    required={
        "PULL_REQUEST_CODE_REVIEW","CODING_AGENT","AUTOFIX","CHAT_OR_CODE_GENERATION",
        "ANY_OPERATION_CONSUMING_COPILOT_QUOTA_OR_PREMIUM_REQUESTS"
    }
    if not required.issubset(prohibited): out.append("Copilot prohibited-operation set drift")
    ai=d.get("aiExecution",{})
    if ai.get("authorizedProjectAI")!="CHATGPT": out.append("project AI execution authority must remain ChatGPT")
    if ai.get("exceptions")!="REPOSITORY_OWNER_EXPLICIT_POLICY_CHANGE_REQUIRED": out.append("AI policy exception boundary drift")
    infra=d.get("nonAIInfrastructure",{})
    if infra.get("githubActionsAllowed") is not True or infra.get("deterministicCIAllowed") is not True:
        out.append("non-AI deterministic GitHub CI must remain allowed")
    return out

def corpus_source_registry_semantic(d: dict) -> list[str]:
    out=[]
    sources=d.get("sources",[])
    keys=[s.get("sourceKey") for s in sources]
    if len(keys)!=len(set(keys)): out.append("duplicate corpus sourceKey")
    by_key={s.get("sourceKey"):s for s in sources}
    if set(by_key)!={"OSHB_MORPHHB","BHSA_2021","ETCBC_BRIDGING_2021"}: out.append("required corpus source ensemble drift")
    if by_key.get("OSHB_MORPHHB",{}).get("licensing",{}).get("publicServingDefault")!="ALLOW_WITH_ATTRIBUTION": out.append("OSHB serving-right default drift")
    if by_key.get("BHSA_2021",{}).get("pin",{}).get("datasetVersion")!="2021": out.append("BHSA dataset pin drift")
    if by_key.get("BHSA_2021",{}).get("licensing",{}).get("publicServingDefault")!="CONDITIONAL_RIGHTS_REVIEW": out.append("BHSA rights boundary drift")
    bhsa_paths=set(by_key.get("BHSA_2021",{}).get("acquisition",{}).get("paths",[]))
    required_bhsa_tf={
        "tf/2021/otext.tf","tf/2021/otype.tf","tf/2021/oslots.tf",
        "tf/2021/book.tf","tf/2021/chapter.tf","tf/2021/verse.tf",
        "tf/2021/g_cons.tf","tf/2021/g_cons_utf8.tf","tf/2021/g_word.tf","tf/2021/g_word_utf8.tf",
        "tf/2021/qere.tf","tf/2021/qere_utf8.tf","tf/2021/qere_trailer.tf","tf/2021/qere_trailer_utf8.tf",
        "tf/2021/trailer.tf","tf/2021/trailer_utf8.tf",
        "tf/2021/g_lex.tf","tf/2021/g_lex_utf8.tf","tf/2021/lex.tf","tf/2021/lex_utf8.tf","tf/2021/voc_lex_utf8.tf"
    }
    if not required_bhsa_tf.issubset(bhsa_paths): out.append("BHSA otext dependency set drift")
    if by_key.get("ETCBC_BRIDGING_2021",{}).get("integration",{}).get("canonicality")!="DERIVED_MAPPING_EVIDENCE": out.append("bridging canonicality drift")
    if by_key.get("ETCBC_BRIDGING_2021",{}).get("licensing",{}).get("publicServingDefault")!="DENY_UNTIL_RIGHTS_REVIEW": out.append("bridging rights boundary drift")
    if d.get("usagePolicy",{}).get("upstreamUpdatePolicy")!="NEVER_AUTO_ADVANCE": out.append("corpus pins may not auto-advance")
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

def translation_policy_semantic(d: dict) -> list[str]:
    policy=set(d.get("policyRuleVersionIds",[]))
    editorial=set(d.get("editorialConventionRuleVersionIds",[]))
    if policy & editorial: return ["same RuleVersion appears in policy and editorial-convention membership"]
    return []

def manifest_semantic(d: dict) -> list[str]:
    orders=[x.get("componentOrder") for x in d.get("components",[])]
    if any(x is None for x in orders): return ["missing componentOrder"]
    if len(orders)!=len(set(orders)): return ["duplicate componentOrder"]
    if sorted(orders)!=list(range(len(orders))): return ["componentOrder not contiguous"]
    logical=[(x.get("componentKind"),x.get("researchObjectId")) for x in d.get("components",[])]
    if len(logical)!=len(set(logical)): return ["duplicate logical release component"]
    return []

def query_policy_semantic(d: dict) -> list[str]:
    out=[]
    if d.get("defaultPageSize",0)>d.get("maxPageSize",0): out.append("defaultPageSize exceeds maxPageSize")
    if d.get("maxPageSize",0)>d.get("hardResultCap",0): out.append("maxPageSize exceeds hardResultCap")
    return out

def query_result_semantic(d: dict) -> list[str]:
    out=[]
    if d.get("pageMatchCount")!=len(d.get("matches",[])): out.append("pageMatchCount does not equal matches length")
    total=d.get("totalMatchCount")
    if d.get("totalCountExact") and total is None: out.append("exact total requires totalMatchCount")
    if not d.get("totalCountExact") and total is not None: out.append("non-exact total must be null")
    if total is not None and total<d.get("pageMatchCount",0): out.append("totalMatchCount smaller than pageMatchCount")
    return out

def experience_semantic(d: dict) -> list[str]:
    out=[]
    decisions=d.get("featureDecisions",{})
    reasons=d.get("reasonCodes",{})
    if not set(reasons).issubset(set(decisions)): out.append("reasonCodes contains unknown feature decision")
    for key in reasons:
        if decisions.get(key)!="DENY": out.append("reasonCode may only accompany DENY")
    return out

def rights_semantic(d: dict) -> list[str]:
    out=[]
    if d.get("decisionBasis")=="RULE" and not d.get("winningRuleIds"): out.append("RULE without winner")
    if d.get("decisionBasis")=="DEFAULT_DENY" and (d.get("winningRuleIds") or d.get("decision")!="DENY"): out.append("bad DEFAULT_DENY")
    if d.get("decisionBasis")=="UNKNOWN_RESTRICTIVE" and (d.get("winningRuleIds") or d.get("decision")!="DENY"): out.append("bad UNKNOWN_RESTRICTIVE")
    if d.get("decision")=="CONDITIONAL" and not (d.get("conditions") or d.get("obligations")): out.append("empty CONDITIONAL")
    applicable=set(d.get("applicableRuleIds") or [])
    winning=set(d.get("winningRuleIds") or [])
    if not winning.issubset(applicable): out.append("winning rule not in applicable rules")
    return out

def validate_schema_documents():
    for path in (ROOT/"contracts/v1.1/json-schema").glob("*.json"):
        schema=json.loads(path.read_text(encoding="utf-8"))
        try:
            Draft202012Validator.check_schema(schema)
        except Exception as exc:
            fail(f"{path.relative_to(ROOT)} invalid JSON Schema: {exc}")
        def scan(node):
            if isinstance(node,dict):
                ref=node.get("$ref")
                if isinstance(ref,str) and ref.startswith("./"):
                    target=(path.parent/ref).resolve()
                    if not target.exists(): fail(f"{path.relative_to(ROOT)} missing local ref {ref}")
                for value in node.values(): scan(value)
            elif isinstance(node,list):
                for value in node: scan(value)
        scan(schema)

def validate_fixtures():
    for s,f in POSITIVE:
        errs=schema_errors(s,f)
        ERRORS.extend(errs)
        if errs: continue
        d=load(f)
        if f.endswith("corpus-source-registry.json"): ERRORS.extend(f"{f}: {e}" for e in corpus_source_registry_semantic(d))
        if f.endswith("github-ai-usage-policy.json"): ERRORS.extend(f"{f}: {e}" for e in github_ai_usage_policy_semantic(d))
        if f.endswith("hebrew-bible-canon-system.json"): ERRORS.extend(f"{f}: {e}" for e in hebrew_bible_canon_semantic(d))
        if "corpus-query-1sam16-7" in f: ERRORS.extend(f"{f}: {e}" for e in query_semantic(d))
        if f.endswith("translation-decision.json"): ERRORS.extend(f"{f}: {e}" for e in translation_semantic(d))
        if f.endswith("translation-policy-version.json"): ERRORS.extend(f"{f}: {e}" for e in translation_policy_semantic(d))
        if f.endswith("release-manifest.json"): ERRORS.extend(f"{f}: {e}" for e in manifest_semantic(d))
        if "rights-decision-" in f: ERRORS.extend(f"{f}: {e}" for e in rights_semantic(d))
        if f.endswith("query-execution-policy.json"): ERRORS.extend(f"{f}: {e}" for e in query_policy_semantic(d))
        if f.endswith("corpus-query-result.json"): ERRORS.extend(f"{f}: {e}" for e in query_result_semantic(d))
        if f.endswith("experience-capabilities.json"): ERRORS.extend(f"{f}: {e}" for e in experience_semantic(d))
        if f.endswith("translation-witness-list.json"): ERRORS.extend(f"{f}: {e}" for e in translation_witness_semantic(d))
    for s,f in NEG_SCHEMA:
        if not schema_errors(s,f): fail(f"{f}: expected schema rejection")
    semantic_neg=[
      ("contracts/v1.1/negative-fixtures/corpus-query-invalid-id-value.json",query_semantic),
      ("contracts/v1.1/negative-fixtures/translation-decision-two-selected.json",translation_semantic),
      ("contracts/v1.1/negative-fixtures/translation-decision-selected-mismatch.json",translation_semantic),
      ("contracts/v1.1/negative-fixtures/release-manifest-duplicate-order.json",manifest_semantic),
      ("contracts/v1.1/negative-fixtures/release-manifest-duplicate-logical-component.json",manifest_semantic),
      ("contracts/v1.1/negative-fixtures/release-manifest-same-object-different-version.json",manifest_semantic),
      ("contracts/v1.1/negative-fixtures/rights-winner-not-applicable.json",rights_semantic),
      ("contracts/v1.1/negative-fixtures/query-execution-policy-invalid-bounds.json",query_policy_semantic),
      ("contracts/v1.1/negative-fixtures/translation-policy-overlapping-rule-membership.json",translation_policy_semantic),
      ("contracts/v1.1/negative-fixtures/translation-witness-duplicate-expression.json",translation_witness_semantic),
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
    required_scope_gates={"CORE-FZ-WB-001","CORE-FZ-WB-002","CORE-FZ-WB-003"}
    missing_scope_gates=sorted(required_scope_gates-set(gates))
    if missing_scope_gates: fail(f"whole-Bible core freeze gates missing: {missing_scope_gates}")
    if "architecture/whole-bible-base-product.md" not in m.get("active",[]):
        fail("whole-Bible base-product authority must be active")
    whole_bible=(ROOT/"architecture/whole-bible-base-product.md").read_text(encoding="utf-8")
    for required in ("Whole-Bible coverage is the baseline product scope.","acceptance vectors","Research Pro is an academic overlay"):
        if required not in whole_bible:
            fail(f"whole-Bible base-product authority missing invariant: {required}")
    if not (ROOT/"PROJECT_STATE.md").exists(): fail("PROJECT_STATE.md missing")
    if not (ROOT/"CHANGELOG.md").exists(): fail("CHANGELOG.md missing")
    if "PROJECT_STATE.md" not in m.get("active",[]): fail("PROJECT_STATE.md must be active living authority")
    if "PROJECT_CHARTER.md" not in m.get("active",[]): fail("PROJECT_CHARTER.md must be active architecture authority")
    ai_policy=load("contracts/v1.1/github-ai-usage-policy.json")
    ERRORS.extend(f"github-ai-usage-policy.json: {e}" for e in github_ai_usage_policy_semantic(ai_policy))
    agent_protocol=(ROOT/"AGENTS.md").read_text(encoding="utf-8")
    governance_contract=(ROOT/"architecture/repository-governance.md").read_text(encoding="utf-8")
    for required in (
        "GitHub Copilot is not an authorized project agent or reviewer",
        "AI-assisted implementation, analysis, repository orchestration and code review are performed through the project's ChatGPT workflow",
    ):
        if required not in agent_protocol:
            fail(f"AGENTS.md missing AI execution invariant: {required}")
    for required in (
        "GitHub Copilot is not authorized for project work",
        "ChatGPT as the authorized AI execution/review channel",
    ):
        if required not in governance_contract:
            fail(f"repository governance missing AI execution invariant: {required}")
    for workflow in (ROOT/".github/workflows").glob("*"):
        if workflow.is_file() and workflow.suffix in {".yml",".yaml"}:
            workflow_text=workflow.read_text(encoding="utf-8").lower()
            if "copilot" in workflow_text:
                fail(f"GitHub Actions workflow may not invoke or depend on Copilot: {workflow.relative_to(ROOT)}")
    charter=(ROOT/"PROJECT_CHARTER.md").read_text(encoding="utf-8")
    for required in ("# 1. Product mission","# 13. Explicit non-goals","# 15. Fixed requirements versus open decisions"):
        if required not in charter: fail(f"project charter missing canonical section {required}")
    readme=(ROOT/"README.md").read_text(encoding="utf-8")
    if "PROJECT_CHARTER.md" not in readme: fail("README must point to project charter")
    active=(ROOT/"architecture/database-api-cross-stage-contract-v1.1.md").read_text(encoding="utf-8")
    if "Expand " + chr(96) + "works.work_type" + chr(96) in active: fail("stale mixed work_type section")
    for adapter in (ROOT/"scripts/corpora").glob("*.py"):
        try: compile(adapter.read_text(encoding="utf-8"),str(adapter),"exec")
        except SyntaxError as exc: fail(f"corpus adapter syntax error {adapter.relative_to(ROOT)}: {exc}")
    tax=(ROOT/"docs/academic-source-taxonomy.md").read_text(encoding="utf-8")
    for stale in ("VERIFIED_OPEN","LICENSED_FOR_INDEXING","LICENSED_PRIVATE_ONLY","USER_SUPPLIED_RESEARCH_ONLY"):
        if stale in tax: fail(f"stale source status {stale}")

    core_api=yaml.safe_load((ROOT/"contracts/v1.1/openapi.yaml").read_text(encoding="utf-8"))
    required_passage_statuses={"200","400","404","500","503"}
    for route in ("/api/v1/passages/{reference}", "/api/v1/releases/{releaseId}/passages/{reference}"):
        actual=set(core_api["paths"][route]["get"]["responses"])
        if actual != required_passage_statuses:
            fail(f"Core OpenAPI passage route status drift {sorted(actual)} != {sorted(required_passage_statuses)}: {route}")
    def response_error_codes(route: str, status: str) -> set[str]:
        response=core_api["paths"][route]["get"]["responses"][status]
        response_name=response["$ref"].rsplit("/",1)[-1]
        response_schema=core_api["components"]["responses"][response_name]["content"]["application/json"]["schema"]
        schema_name=response_schema["$ref"].rsplit("/",1)[-1]
        code_schema=core_api["components"]["schemas"][schema_name]["properties"]["code"]
        if "const" in code_schema: return {code_schema["const"]}
        return set(code_schema.get("enum",[]))

    expected_route_errors={
        "/api/v1/passages/{reference}": {
            "400": {"REFERENCE_SYSTEM_REQUIRED", "INVALID_REFERENCE"},
            "404": {"REFERENCE_NOT_FOUND"},
            "500": {"CONTRACT_VIOLATION"},
            "503": {"DATA_TEMPORARILY_UNAVAILABLE"},
        },
        "/api/v1/releases/{releaseId}/passages/{reference}": {
            "400": {"REFERENCE_SYSTEM_REQUIRED", "INVALID_REFERENCE", "INVALID_RELEASE_ID"},
            "404": {"REFERENCE_NOT_FOUND", "RELEASE_NOT_FOUND"},
            "500": {"CONTRACT_VIOLATION"},
            "503": {"DATA_TEMPORARILY_UNAVAILABLE"},
        },
    }
    for route,statuses in expected_route_errors.items():
        for status,expected_codes in statuses.items():
            actual_codes=response_error_codes(route,status)
            if actual_codes!=expected_codes:
                fail(f"Core OpenAPI error-code drift for {route} {status}: {sorted(actual_codes)} != {sorted(expected_codes)}")
    translation_schema_ref=core_api["components"]["schemas"]["TranslationWitnessList"].get("$ref")
    if translation_schema_ref != "./json-schema/translation-witness-list.schema.json":
        fail(f"Core OpenAPI TranslationWitnessList must use canonical schema, got {translation_schema_ref!r}")
    witness_schema=load("contracts/v1.1/json-schema/translation-witness.schema.json")
    required_witness_fields={"textualWorkId","textualEditionId","digitalExpressionId","coverageStatus","deliveryStatus","displayStatus","binding","rightsDecisionSnapshotId","provenanceId","segments"}
    if not required_witness_fields.issubset(set(witness_schema.get("required",[]))):
        fail("TranslationWitness missing load-bearing identity/rights/segment fields")
    provider_binding=load("contracts/v1.1/json-schema/provider-witness-binding.schema.json")
    for required_field in ("providerVersion","observedHash","observedAt"):
        if required_field not in provider_binding.get("required",[]):
            fail(f"ProviderWitnessBinding must require {required_field}")
    for route in ("/api/v1/passages/{reference}/translations", "/api/v1/releases/{releaseId}/passages/{reference}/translations"):
        response_schema=core_api["paths"][route]["get"]["responses"]["200"]["content"]["application/json"]["schema"].get("$ref")
        if response_schema != "#/components/schemas/TranslationWitnessList":
            fail(f"translation route schema drift: {route} -> {response_schema!r}")
    generic_not_found=(core_api["components"]["responses"]["NotFound"]["content"]
                       ["application/json"]["schema"]["properties"]["code"].get("const"))
    if generic_not_found != "NOT_FOUND":
        fail(f"Core OpenAPI generic NotFound code drift: {generic_not_found!r} != 'NOT_FOUND'")

def vocab_drift():
    v=load("contracts/v1.1/vocabulary.json")
    q=load("contracts/v1.1/json-schema/corpus-query.schema.json")
    if set(v["queryNodeType"])!=set(q["properties"]["nodes"]["items"]["properties"]["nodeType"]["enum"]): fail("queryNodeType drift")
    if set(v["queryConstraintOperator"])!=set(q["$defs"]["nodeConstraint"]["properties"]["operator"]["enum"]): fail("queryConstraintOperator drift")
    r=load("contracts/v1.1/json-schema/rights-decision-snapshot.schema.json")
    for key,prop in [("rightsOperation","operation"),("rightsPurposeScope","purposeScope"),("rightsAudienceScope","audienceScope"),("rightsCommercialContext","commercialContext"),("rightsDecisionBasis","decisionBasis")]:
        if set(v[key])!=set(r["properties"][prop]["enum"]): fail(f"{key} drift")
    if set(v["rightsResolvedDecision"])!=set(r["properties"]["decision"]["enum"]): fail("rightsResolvedDecision drift")
    if set(v["rightsSubjectType"])!=set(r["properties"]["subjectType"]["enum"]): fail("rightsSubjectType drift")
    rm=load("contracts/v1.1/json-schema/release-manifest.schema.json")
    if set(v["releaseComponentKind"])!=set(rm["properties"]["components"]["items"]["properties"]["componentKind"]["enum"]): fail("releaseComponentKind drift")
    ri=load("contracts/v1.1/json-schema/research-issue-version.schema.json")
    if set(v["researchDebateStatus"])!=set(ri["properties"]["debateStatus"]["enum"]): fail("researchDebateStatus drift")
    ts=load("contracts/v1.1/json-schema/translation-source-basis.schema.json")
    if set(v["translationSourceBasisKind"])!=set(ts["properties"]["basisKind"]["enum"]): fail("translationSourceBasisKind drift")
    pe=load("contracts/v1.1/json-schema/product-entitlement.schema.json")
    if set(v["productEntitlementSourceType"])!=set(pe["properties"]["sourceType"]["enum"]): fail("productEntitlementSourceType drift")
    rc=load("contracts/v1.1/json-schema/rights-condition.schema.json")
    condition_ids=set()
    for branch in rc.get("oneOf",[]):
        value=branch.get("properties",{}).get("conditionSchemaId",{}).get("const")
        if value: condition_ids.add(value)
    if set(v["rightsConditionSchemaId"])!=condition_ids: fail("rightsConditionSchemaId drift")
    ce=load("contracts/v1.1/json-schema/commentary-entry.schema.json")
    if set(v["commentaryKind"])!=set(ce["properties"]["commentaryKind"]["enum"]): fail("commentaryKind drift")
    if set(v["commentarySectionType"])!=set(ce["properties"]["sections"]["items"]["properties"]["sectionType"]["enum"]): fail("commentarySectionType drift")
    dr=load("contracts/v1.1/json-schema/discovery-record.schema.json")
    if set(v["discoveryAccessLevel"])!=set(dr["properties"]["accessLevel"]["enum"]): fail("discoveryAccessLevel drift")
    if set(v["discoveryRecordStatus"])!=set(dr["properties"]["recordStatus"]["enum"]): fail("discoveryRecordStatus drift")
    if set(v["discoveryPayloadStorageMode"])!=set(dr["properties"]["payloadStorageMode"]["enum"]): fail("discoveryPayloadStorageMode drift")
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
    runtime_ref=method.get("runtimeReference",{})
    if runtime_ref.get("system")!="PASTORAL_STUDIO_PRODUCTION_RUNTIME": fail("Pastoral Studio runtime reference drift")
    if runtime_ref.get("parityPolicy")!="BEHAVIORAL_RETRIEVAL_ORCHESTRATION_NOT_CODE_COPY": fail("Pastoral Studio parity policy drift")
    orch=method.get("retrievalOrchestration",{})
    if orch.get("parallelCapabilityRoutedFanOut") is not True: fail("scholarly retrieval must preserve capability-routed fan-out")
    if orch.get("providerFailurePolicy")!="DEGRADED_CONTINUE_WITH_EXPLICIT_STATUS": fail("provider degraded-mode policy drift")
    if orch.get("modelMemoryMayReplaceMissingProviderResults") is not False: fail("model memory may not replace failed provider results")
    if orch.get("normalizeBeforeSynthesis") is not True: fail("provider results must normalize before synthesis")
    if orch.get("rightsBeforeModelContext") is not True: fail("rights must be resolved before model context")
    if orch.get("librarianRunsAfterRetrieval") is not True: fail("Librarian must run after evidence retrieval")
    if orch.get("counterevidencePassRequired") is not True: fail("counterevidence pass must remain required")
    if set(orch.get("auxiliarySourceRoutes",[]))!={"CURATED_PRIVATE_LIBRARY","SEFARIA","OPEN_LIBRARY_INTERNET_ARCHIVE"}: fail("auxiliary source-route drift")

    reg=load("contracts/v1.1/scholarly-provider-registry.json")
    required={"OPENALEX","SEMANTIC_SCHOLAR","CORE","CROSSREF","SCITE"}
    registered={p["providerKey"] for p in reg.get("providers",[]) if p.get("requiredInFirstImplementation")}
    if registered!=required: fail(f"initial scholarly provider ensemble drift: {registered}")
    allowed_caps=set(v["scholarlyDiscoveryCapability"])
    allowed_transports=set(v["scholarlyDiscoveryTransportMode"])
    for provider in reg.get("providers",[]):
        if not set(provider.get("expectedCapabilities",[])).issubset(allowed_caps): fail(f"provider registry unknown capabilities: {provider.get('providerKey')}")
        if not set(provider.get("transportModes",[])).issubset(allowed_transports): fail(f"provider registry unknown transport mode: {provider.get('providerKey')}")
    if "GEMINI" in rm["properties"]["modelProvider"].get("enum",[]): fail("research model provider must not be Gemini-locked")

def secret_scan():
    assignment=re.compile(r"(?i)\b(GEMINI_API_KEY|GOOGLE_API_KEY|OPENAI_API_KEY|ANTHROPIC_API_KEY|SCITE_API_KEY|CORE_API_KEY|SEMANTIC_SCHOLAR_API_KEY|OPENALEX_API_KEY)\s*=\s*[\"']?([A-Za-z0-9_\-]{8,})")
    literals=[re.compile(r"AIza[0-9A-Za-z_\-]{30,}"),re.compile(r"sk-[A-Za-z0-9_\-]{20,}"),re.compile(r"scite_[A-Za-z0-9_\-]{20,}")]
    excluded_dirs={".git", ".next", "node_modules", "playwright-report", "test-results", "dist", "build", "coverage", "__pycache__"}
    for p in ROOT.rglob("*"):
        rel=p.relative_to(ROOT)
        if (
            not p.is_file()
            or excluded_dirs.intersection(rel.parts)
            or any(part == "venv" or part.startswith(".venv") for part in rel.parts)
        ):
            continue
        if rel.name in {".env",".env.local",".env.production",".env.development"}: fail(f"forbidden env file {rel}")
        if p.suffix.lower() not in {".md",".json",".yaml",".yml",".py",".ts",".tsx",".js",".jsx",".toml",".txt"}: continue
        try: t=p.read_text(encoding="utf-8")
        except UnicodeDecodeError: continue
        if assignment.search(t): fail(f"possible model-secret assignment {rel}")
        for pat in literals:
            if pat.search(t): fail(f"possible model-secret literal {rel}")

def main() -> int:
    validate_schema_documents(); validate_fixtures(); governance(); vocab_drift(); secret_scan()
    if ERRORS:
        print("CONTRACT VALIDATION FAILED")
        for e in ERRORS: print(" -",e)
        return 1
    print(f"CONTRACT VALIDATION PASSED: {len(POSITIVE)} positive fixtures + negative/semantic/governance checks")
    return 0

if __name__=="__main__":
    sys.exit(main())
