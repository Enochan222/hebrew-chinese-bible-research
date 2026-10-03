# Repository Governance Contract

Status: **REQUIRED OPERATIONAL GOVERNANCE**

The repository's product charter, architecture, machine contracts and validation workflow are source-of-truth assets. Contract CI existing after a direct push is not equivalent to enforced merge governance.

## Required main-branch rules

The `main` branch should enforce:

1. changes enter through pull requests;
2. the `Contract validation` workflow is a required status check;
3. force pushes are blocked;
4. branch deletion is blocked;
5. stale/out-of-date branches are handled according to the repository's chosen merge policy;
6. CODEOWNERS applies to Charter, architecture, contracts, contract validator and workflows.

For a single-maintainer phase, mandatory second-person review may remain disabled. Required CI is still mandatory.

## Current verified state

At the start of the 2026-10-03 panel closure review:

- `main protected = false`;
- repository rulesets were empty;
- Contract validation ran after pushes but did not prevent an invalid direct push from entering `main`.

The current ChatGPT GitHub connector exposes ruleset/protection reads but not repository-admin writes. Therefore this repository setting cannot be truthfully marked complete by a file commit alone.

Track the live configuration under `REPO-GOV-001` and `REPO-GOV-002` in `contracts/v1.1/freeze-checklist.md`.

## Development practice until live enforcement exists

Even before the GitHub ruleset is enabled, architecture/contract changes should use a branch + pull request + successful Contract validation before merge.

A validator change and the contract change it permits should receive explicit review as one trust-boundary change, because a PR must not make an unsafe contract pass merely by weakening the validator.
