# Repository Working Protocol

These instructions apply to every human or AI agent changing this repository.

## Before any change

Read, in order:

1. `PROJECT_CHARTER.md`
2. `PROJECT_STATE.md`
3. `architecture/manifest.json`
4. latest entry in `CHANGELOG.md`
5. relevant active architecture/contracts

Do not implement from a superseded document.


## Product-scope guard

The canonical product baseline is the **whole Hebrew Bible**.

- 1 Samuel 16:7, Psalm/superscription cases, Ketiv/Qere cases and other named passages are acceptance/edge-case fixtures, never the product scope.
- Do not hard-code importer, API, navigation, release or UI scope to fixture passages.
- Prioritize whole-Bible base-product coverage before Research Pro depth.
- Research Pro is a progressive overlay and must not block base passage availability.
- Read `architecture/whole-bible-base-product.md` before corpus, serving, passage-UI or Research Pro implementation work.

## AI execution policy

GitHub Copilot is not an authorized project agent or reviewer for this repository.

- Do not request GitHub Copilot pull-request review.
- Do not use Copilot Coding Agent, Copilot Autofix, Copilot Chat/code generation, or any GitHub feature that consumes Copilot quota, premium requests, or equivalent Copilot AI credits for this project.
- Do not treat a Copilot comment, review, suggestion, or status as project acceptance evidence.
- AI-assisted implementation, analysis, repository orchestration and code review are performed through the project's ChatGPT workflow.
- Deterministic GitHub Actions, ordinary GitHub repository features, and human collaborators remain allowed; this restriction targets GitHub Copilot AI consumption.
- Any exception requires an explicit repository-owner policy change committed through the governed PR path.

Machine authority: `contracts/v1.1/github-ai-usage-policy.json`.

## During research/database work

For external scholarly discovery, follow:

- `architecture/sacred-studies-research-method.md`
- `architecture/scholarly-discovery-aggregation.md`
- `contracts/v1.1/scholarly-research-method.json`
- `contracts/v1.1/scholarly-provider-registry.json`

Do not replace provider evidence with model memory.

## Before every push or PR update

Mandatory:

1. update `PROJECT_STATE.md` so it describes the repository **after** the proposed change;
2. update `CHANGELOG.md` with what changed, why, intended effect, and validation;
3. if product mission/fixed requirements changed, also update `PROJECT_CHARTER.md`;
4. if architecture authority changed, update `architecture/manifest.json`;
5. run contract/governance validation.

Every pushed change must include both `PROJECT_STATE.md` and `CHANGELOG.md` in the same push/PR change set.

Prefer an atomic multi-file commit or a PR whose final diff includes both files. Do not make isolated direct-to-main content commits that bypass this rule.

## Version-control principle

`PROJECT_CHARTER.md` = stable constitution.

`PROJECT_STATE.md` = current living state, mandatory every push.

`CHANGELOG.md` = append-only rationale/history, mandatory every push.

Git commits/PRs = immutable technical history.

GitHub Actions = enforcement/evidence.
