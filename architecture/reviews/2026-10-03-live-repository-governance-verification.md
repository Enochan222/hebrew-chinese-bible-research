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
