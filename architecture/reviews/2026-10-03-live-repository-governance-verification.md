# Live Repository Governance Verification

Date: 2026-10-03  
Status: **VERIFIED LIVE GITHUB STATE**

## Purpose

This record verifies repository governance from live GitHub repository metadata after the `Protect main` repository ruleset was enabled.

It distinguishes actual GitHub enforcement from governance intent documented only in repository files.

## Verified repository state

Repository:

- `Enochan222/hebrew-chinese-bible-research`
- default branch: `main`
- repository visibility: **public**
- merge commit: disabled
- rebase merge: disabled
- squash merge: enabled
- update branch: enabled
- auto merge: enabled

The repository visibility is recorded here as observed state only. This verification does not change repository visibility.

## Verified main-branch protection

Live branch metadata reports:

- `main protected = true`.

Protection is provided by a repository ruleset rather than the legacy branch-protection rule API.

Therefore the legacy branch-protection payload may still report its own older protection fields as disabled while `main` is protected by the active ruleset.

## Active ruleset

Ruleset:

- name: `Protect main`
- ruleset ID: `24409248`
- target: branch
- target condition: default branch
- enforcement: `active`
- bypass actors: none
- current user bypass: never

## Enforced rules

### Deletion

Enabled.

Matching refs cannot be deleted through ordinary write access.

### Non-fast-forward / force push

Enabled.

Force-push / history-rewrite updates to `main` are blocked.

### Linear history

Enabled.

Merge commits cannot be pushed to the protected branch.

The repository itself also has:

- merge commits disabled;
- rebase merge disabled;
- squash merge enabled.

Therefore the intended normal merge path is squash merge.

### Pull request requirement

Enabled.

Parameters verified live:

- required approving reviews: `0`;
- dismiss stale approvals on push: `false`;
- required team reviewers: none;
- Code Owner approval: not required;
- last-push approval: not required;
- review conversation resolution: required;
- allowed merge methods: squash only.

This intentionally supports two or more collaborators without requiring mutual approval while still forcing all ordinary branch updates through pull requests.

### Required status checks

Enabled.

Required checks:

- `contracts`
- `state-and-changelog`

Both checks are bound to GitHub Actions integration ID `15368`.

Strict required-status-check policy is enabled:

- `strict_required_status_checks_policy = true`.

Therefore a pull request must be tested against the latest protected-branch state before merge.

`do_not_enforce_on_create = false`.

## Latest main validation evidence

At verification time, latest `main` was:

- `7923a56e9bce4046363834071ba625c28db2980b`.

Its live GitHub check runs were:

- `contracts`: completed / success;
- `state-and-changelog`: completed / success.

Both were produced by GitHub Actions.

## Copilot extra-approval parameter

The live ruleset currently reports:

- `require_extra_approval_for_unattributed_changes = true`.

Because required approving reviews are `0`, this does not currently create a general second-person approval requirement.

This setting is not treated as a load-bearing repository gate.

## Governance conclusion

The previously open repository-governance conditions are now satisfied:

- `REPO-GOV-001`: PASS;
- `REPO-GOV-002`: PASS;
- `REPO-GOV-003`: PASS.

The repository can now be described as live PR/CI-governed rather than merely governance-documented.

Normal contribution path:

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

This verification does not imply that the full product or v1.1 architecture is frozen. It verifies only repository-governance enforcement.


## Independent post-sync re-audit

After governance synchronization PR #4 was squash-merged, live GitHub state was re-read independently rather than inferred from repository prose.

Re-audit baseline:

- current `main`: `14cb67e9c70fa92c0dc629c0e8efcf6e4dc5659c`;
- `main protected = true`;
- ruleset `Protect main` ID `24409248`, enforcement `active`;
- target condition remains the default branch;
- bypass actors remain empty and current-user bypass remains `never`;
- pull requests remain required with `0` approving reviews;
- review conversation resolution remains required;
- allowed merge method remains squash only;
- required checks remain `contracts` and `state-and-changelog`, both bound to GitHub Actions;
- strict latest-main status-check mode remains enabled;
- deletion, non-fast-forward/force-push updates, and non-linear protected-branch history remain blocked.

Post-merge push validation for `14cb67e...`:

- Project governance run `37102653272`: PASS;
- Contract validation run `37102653290`: PASS.

A cross-document consistency audit then checked `PROJECT_STATE.md`, the canonical freeze checklist, repository-governance contract, README, closed issue #1, this verification record, and the panel review. The live/current sources were consistent except for one historical-looking sentence in the still-current panel review that continued to describe branch protection as unresolved. That sentence is corrected by the governance-consistency follow-up PR.

Older CHANGELOG entries that record the repository before protection was enabled are intentionally retained as historical records; they are not current-state authority.

## 2026-10-04 current-state re-verification

A fresh live audit was performed after subsequent governed changes.

Current `main` at audit time:

- `3d2dc4d8f07b67f3be44f9fedc69a60acb775405`;
- commit is associated with merged PR #6, `Adopt Pastoral Studio runtime scholarly RAG method`;
- PR #6 head `c70d6e66215fd3cda5633397c0276dc9d2fc977d` passed both required GitHub Actions checks before merge:
  - `contracts`: success;
  - `state-and-changelog`: success;
- the post-merge `main` commit also passed both checks.

The active ruleset was re-read live and remains unchanged in all load-bearing respects:

- ruleset `Protect main`, ID `24409248`;
- enforcement `active`;
- target `~DEFAULT_BRANCH`;
- bypass actors: none;
- current-user bypass: never;
- deletion blocked;
- non-fast-forward / force push blocked;
- linear history required;
- pull request required;
- required approvals: `0`;
- review conversation resolution required;
- squash is the only permitted merge method;
- required checks:
  - `contracts` from GitHub Actions integration `15368`;
  - `state-and-changelog` from GitHub Actions integration `15368`;
- strict latest-main status-check mode enabled;
- status checks are enforced on the protected branch rather than waived on creation.

Repository merge settings were also re-read live:

- `allow_squash_merge = true`;
- `allow_merge_commit = false`;
- `allow_rebase_merge = false`;
- `allow_update_branch = true`;
- `delete_branch_on_merge = true`.

A recent-history audit of protected-main changes found that the post-protection governance/application updates inspected were all traceable to pull requests:

- PR #4 -> `14cb67e9c70fa92c0dc629c0e8efcf6e4dc5659c`;
- PR #5 -> `589cb83d022542d84f7e7f708a64f4d3bfc779dc`;
- PR #6 -> `3d2dc4d8f07b67f3be44f9fedc69a60acb775405`.

No evidence of a ruleset bypass was found in this audit.

### Legacy branch-protection API note

The legacy branch-protection sub-payload may still report its own older protection fields as disabled even while the branch-level metadata reports `protected = true`.

That is expected here because enforcement is supplied by the repository Ruleset API, not by a legacy branch-protection rule. The ruleset state is the controlling live evidence.

### Re-verification conclusion

The current live repository state continues to satisfy:

- `REPO-GOV-001`: PASS;
- `REPO-GOV-002`: PASS;
- `REPO-GOV-003`: PASS.

This re-verification updates evidence freshness only. It does not change product architecture, repository visibility, review-count policy, or merge semantics.
