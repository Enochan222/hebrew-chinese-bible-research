# Repository Governance Contract

Status: **LIVE ENFORCEMENT VERIFIED**

The repository's product charter, architecture, machine contracts and validation workflow are source-of-truth assets. Contract CI existing after a direct push is not equivalent to enforced merge governance.

## Required main-branch rules

The `main` branch must enforce:

1. changes enter through pull requests;
2. required status checks pass before merge;
3. protected-branch changes are tested against the latest `main`;
4. force pushes are blocked;
5. branch deletion is blocked;
6. linear history is maintained;
7. unresolved review conversations block merge;
8. canonical truth files have declared CODEOWNERS.

For the current collaboration model, mandatory second-person approval is intentionally disabled. Required machine checks remain mandatory.

## Current verified live state

Verified on 2026-10-03 from live GitHub repository metadata.

Repository ruleset:

- name: `Protect main`;
- ruleset ID: `24409248`;
- target: default branch;
- enforcement: `active`;
- bypass actors: none;
- current user bypass: never.

Live branch metadata reports:

- `main protected = true`.

### Enforced branch rules

- deletion blocked;
- non-fast-forward / force push blocked;
- linear history required.

### Pull-request rule

- pull request required;
- approving reviews required: `0`;
- stale approvals are not relevant because approval count is zero;
- team review not required;
- Code Owner approval not required;
- most-recent-push approval not required;
- review conversation resolution required;
- allowed merge method: squash only.

This supports multiple collaborators without requiring mutual approval while still preventing direct ordinary updates to `main`.

### Required status checks

Required checks:

- `contracts`;
- `state-and-changelog`.

Both checks are bound to GitHub Actions.

Strict status-check mode is enabled:

- `strict_required_status_checks_policy = true`.

Therefore a pull request must be validated against the latest protected-branch state before merge.

### Repository merge settings

Live repository metadata also verifies:

- merge commit disabled;
- rebase merge disabled;
- squash merge enabled;
- update branch enabled;
- auto merge enabled.

## Project AI execution policy

The repository owner has selected **ChatGPT as the authorized AI execution/review channel for this project**.

GitHub Copilot is not authorized for project work. The project must not intentionally consume Copilot quota, premium requests or equivalent Copilot AI credits for:

- pull-request code review;
- coding-agent execution;
- Autofix;
- Copilot Chat or code generation;
- repository orchestration;
- any other Copilot-backed AI operation.

A Copilot review/comment is not acceptance evidence and must never be required for merge.

This restriction does not prohibit deterministic GitHub Actions, ordinary non-AI GitHub features, or human contributors.

Canonical machine policy:

- `contracts/v1.1/github-ai-usage-policy.json`.

Repository CI validates the machine policy and rejects Copilot references in GitHub Actions workflow files. User/account-level GitHub Copilot settings are outside repository-file enforcement; the repository owner reported on 2026-10-05 that automatic Copilot code review was disabled at account level. That account-level state is recorded as owner-reported, not independently verified by repository metadata.

## Required contribution path

The enforced normal contribution path is:

```text
feature branch
  -> pull request
  -> synchronize with latest main when required
  -> contracts PASS
  -> state-and-changelog PASS
  -> resolve review conversations
  -> squash merge
  -> protected main
```

A validator change and the contract change it permits should receive explicit review as one trust-boundary change, because a PR must not make an unsafe contract pass merely by weakening the validator.

## Governance evidence

Canonical live-verification record:

- `architecture/reviews/2026-10-03-live-repository-governance-verification.md`.

Canonical gate status:

- `contracts/v1.1/freeze-checklist.md`.

`REPO-GOV-001`, `REPO-GOV-002`, and `REPO-GOV-003` are PASS.

## Repository visibility

Live repository metadata currently reports the repository as **public**.

This document records that fact but does not change repository visibility. Visibility changes require a separate deliberate repository-administration decision.

## Current re-verification

Re-verified on 2026-10-04 against live GitHub metadata after further protected-main work.

The ruleset remains active with the same load-bearing rules, required checks, strict latest-main policy, no bypass actors, and squash-only merge path.

Current audited `main` commit `3d2dc4d8f07b67f3be44f9fedc69a60acb775405` is a squash merge from PR #6 rather than a direct push. Its PR head passed both required checks before merge, and the post-merge main commit also passed both workflows.

Recent protected-main commits inspected after ruleset activation were traceable to PR #4, PR #5, and PR #6. No bypass evidence was found.

The legacy branch-protection API's own `enabled: false` field is not the controlling signal for this repository because the active repository ruleset provides protection; branch metadata correctly reports `protected: true`.

See the canonical live record:

- `architecture/reviews/2026-10-03-live-repository-governance-verification.md`.
