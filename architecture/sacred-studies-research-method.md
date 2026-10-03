# Sacred Studies Derived Scholarly Research Method

Status: **CANONICAL RESEARCH-METHOD CONTRACT FOR SCHOLARLY DISCOVERY / DATABASE BUILD**
Date: 2026-10-03

## 1. Decision

The Hebrew-Chinese Bible Research database-building process must preserve the research method demonstrated by `AvodaConsulting/sacred-studies-2`, while correcting implementation defects and making the method reproducible, provider-complete, rights-aware, and model-neutral.

`Sacred Studies method parity` means functional/methodological parity, not literal source-code copying.

The following method is mandatory for relevant scholarly-discovery builds.

## 1.1 Production runtime authority

Static inspection of the reference repository is not the final authority for what the deployed lineage application actually executes.

A production Academic Biblical Study run verified a real retrieval fan-out involving Sefaria, Scite, CORE, OpenAlex, Crossref, and Open Library / Internet Archive before Librarian/Writer synthesis, including explicit degraded-mode fallback when one provider failed.

Accordingly, `architecture/pastoral-studio-runtime-scholarly-rag.md` defines the production-verified retrieval orchestration. This document continues to define the inherited research-question, query, Librarian, synthesis, and review method.


## 2. Sacred Studies method that must be preserved

### 2.1 Research question framing

Start from the intersection of:

1. **Text**: biblical passage / research target;
2. **Topic**: the specific exegetical, linguistic, textual-critical, translation, historical, literary, or theological question;
3. **Lens**: selected research approach, scholarly method, tradition, or user-provided research direction where explicitly requested.

This reproduces the Sacred Studies `SEARCH MATRIX (CROSS-REFERENCE)` principle.

Default Hebrew-Bible database builds use academically neutral critical-exegetical coverage unless the research task explicitly requests a confessional/traditional lens.

### 2.2 English academic query optimization

For Chinese/non-English or terminology-heavy input, the ResearchModelAdapter must convert the passage/topic into concise English academic database queries.

Preserved Sacred Studies rules:

- use standard English biblical book names;
- use appropriate academic terminology;
- generate concise search strings built from approximately 3-6 key terms/phrases;
- return search terms rather than prose;
- retain Hebrew/Greek/technical terms when they improve retrieval;
- do not translate the research question into vague general language.

One seed question may produce multiple query variants for different terminology eras, subissues, and counterpositions.

### 2.3 Search breadth

Preserve the Sacred Studies two-direction coverage rule:

- search across **all relevant academic eras**, including seminal/classic scholarship;
- give an explicit **modern scholarship emphasis**.

Sacred Studies hard-coded 2015-2025. This project preserves the method but fixes the date bug by using a rolling recent-scholarship window, defaulting to the previous 10 complete years plus the current year unless a ResearchIssue specifies another historical scope.

### 2.4 Academic source prioritization

Preserve the source-quality filter:

- prioritize peer-reviewed journal articles, critical monographs, major commentaries, academic edited volumes, dissertations/theses where relevant, and established university/academic presses;
- prioritize field-relevant journals rather than generic web popularity;
- exclude devotional blogs, sermons, wikis, generic SEO content, and unsourced summaries from the scholarly evidence pool;
- non-academic web material may be retained only when it is itself the research object, e.g. translator documentation or reception evidence.

### 2.5 Zero-hallucination bibliography rule

Preserve Sacred Studies' librarian rule:

- never invent bibliography items;
- every cited work must resolve to a real bibliographic identity;
- never invent page numbers, dates, DOIs, quotations, or source access;
- sparse search results are reported as sparse coverage rather than filled from model memory.

### 2.6 Multi-source librarian dossier

The librarian phase builds a structured research dossier containing at minimum:

- normalized bibliography / canonical Work identities;
- concise findings relevant to the ResearchIssue;
- raw provider/source links or locators where allowed;
- evidence access level;
- provider provenance;
- coverage limitations.

The dossier is assembled from the required scholarly provider ensemble and the curated private library, not from model memory alone.

### 2.7 Multi-provider search

The intended Sacred Studies provider-aggregation idea is completed here as an actual required execution path:

- OpenAlex;
- Semantic Scholar;
- CORE;
- Crossref;
- Scite.

Provider roles and adapter semantics are defined in `architecture/scholarly-discovery-aggregation.md`.

The deployed Pastoral Studio production workflow has been verified to execute multi-source retrieval before Librarian/Writer synthesis. The Hebrew-Chinese Bible project therefore preserves that production-proven orchestration while implementing provider adapters behind its own normalized DiscoveryRecord / Work / LiteratureSnapshot contracts.

### 2.8 Synthesis from retrieved evidence

Preserve Sacred Studies' writer-stage principle:

- synthesize from the research dossier and retrieved evidence;
- interact directly with the primary biblical text rather than letting commentaries replace textual analysis;
- integrate relevant scholarship where the source actually supports the point;
- never create bibliography/page references during prose generation;
- distinguish source evidence, corpus observation, system inference, and synthesis.

For this project, synthesis produces candidate scholarly objects and drafts. It does not directly publish canonical commentary.

### 2.9 Critical review and revision loop

Preserve Sacred Studies' loop-engineering pattern:

- independent critical evaluation after synthesis;
- score against explicit criteria;
- threshold: **88/100**;
- maximum: **3 review/revision attempts**;
- below threshold: revise according to critique, then re-evaluate.

The Hebrew-Bible research criteria are:

1. substantive academic quality;
2. Hebrew textual/exegetical accuracy;
3. logical and argumentative coherence;
4. focus on the ResearchIssue;
5. adherence to explicit research scope/direction;
6. citation authenticity and source entailment;
7. original-language fidelity;
8. honesty about metadata/abstract/full-text access;
9. counterevidence and competing-position coverage;
10. provenance, rights, and epistemic-label correctness.

### 2.10 Review-loop defect corrections

Method parity does **not** preserve implementation bugs.

In particular:

- malformed reviewer JSON must never default to an artificial passing score;
- reviewer failure results in `REVIEW_INCOMPLETE`, not automatic PASS;
- provider failure does not authorize model-memory substitution;
- a model cannot review its own output into `VERIFIED` scholarly status;
- the 88/100 model-quality gate is an authoring QA signal, not human scholarly approval.

## 3. Model neutrality

Sacred Studies used Gemini heavily. This project preserves the tasks, not the vendor.

All model-assisted steps use `ResearchModelAdapter` and may run through:

- GPT / ChatGPT / Codex;
- Gemini;
- Claude;
- a local model;
- another approved future model.

The same prompt/method contract, input evidence requirements, provenance recording, and review rules apply regardless of model vendor.

## 4. Search sequence for a Hebrew-Bible ResearchIssue

Default sequence:

```text
ResearchTarget + ResearchIssue
 -> Text × Topic × Lens search matrix
 -> English academic query optimization
 -> query variants (exact / broader / terminology variants / counterposition)
 -> curated Drive-library retrieval
 -> OpenAlex + Semantic Scholar broad discovery
 -> Crossref bibliographic/DOI resolution
 -> CORE OA/full-text enrichment
 -> Scite citation-context / support-contrast / integrity enrichment
 -> dedup to canonical Work
 -> access + RightsPolicy
 -> librarian dossier
 -> candidate claim extraction
 -> counterevidence pass
 -> synthesis draft
 -> critical review threshold 88, max 3 attempts
 -> human/review gates
 -> ResearchIssue / ResearchPosition / LiteratureSnapshot
 -> candidate ResearchBuild
 -> ResearchRelease only after publication validation
```

## 5. Machine-readable authority

The machine-readable parameters for this method are maintained in:

- `contracts/v1.1/scholarly-research-method.json`

Changes to core method parameters require an ADR and synchronized updates to `PROJECT_STATE.md` and `CHANGELOG.md`.
