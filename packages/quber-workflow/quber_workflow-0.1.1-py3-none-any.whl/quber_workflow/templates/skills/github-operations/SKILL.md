---
name: github-operations
description: GitHub pull request and repository operations using gh CLI for the quber_excel repository (xmandeng/quber_excel). Use when creating PRs, listing PRs, getting PR status, viewing PR files, or performing git operations. Automatically detects repository from git remote.
allowed-tools: Bash, Read, Grep, Glob
---

# GitHub Operations Skill

This Skill provides GitHub pull request and repository management capabilities using the GitHub CLI (`gh`) tool.

## Prerequisites

- GitHub CLI (`gh`) must be installed and authenticated
- Repository: `xmandeng/quber_excel` (auto-detected from git remote)
- Environment: `GITHUB_PERSONAL_ACCESS_TOKEN` must be set

## Available Operations

### 1. Create Pull Request

**Script**: `scripts/create-pr.sh`

**Usage**:
```bash
bash .claude/skills/github-operations/scripts/create-pr.sh \
  "title" \
  "PR body content" \
  "base-branch"
```

**Arguments**:
- `title`: PR title (follows QUE-XXX: format)
- `body`: PR description (markdown format)
- `base`: Target branch (optional, defaults to "main")

**Note**: Head branch is auto-detected from current git branch by gh pr create.

**Example**:
```bash
bash .claude/skills/github-operations/scripts/create-pr.sh \
  "QUE-123: Add CLI markdown converter" \
  "## Summary
Add CLI for markdown conversion

## Changes Made
- Implement convert command
- Add tests" \
  "main"
```

### 2. List Pull Requests

**Script**: `scripts/list-prs.sh`

**Usage**:
```bash
bash .claude/skills/github-operations/scripts/list-prs.sh [state] [base]
```

**Arguments**:
- `state`: PR state (open, closed, merged, all) - default: open
- `base`: Base branch filter - default: all branches

**Example**:
```bash
# List open PRs
bash .claude/skills/github-operations/scripts/list-prs.sh open main

# List all PRs
bash .claude/skills/github-operations/scripts/list-prs.sh all
```

### 3. Get Pull Request Details

**Script**: `scripts/get-pr.sh`

**Usage**:
```bash
bash .claude/skills/github-operations/scripts/get-pr.sh <pr-number>
```

**Arguments**:
- `pr-number`: Pull request number

**Example**:
```bash
bash .claude/skills/github-operations/scripts/get-pr.sh 45
```

### 4. Get Pull Request Files

**Script**: `scripts/get-pr-files.sh`

**Usage**:
```bash
bash .claude/skills/github-operations/scripts/get-pr-files.sh <pr-number>
```

**Arguments**:
- `pr-number`: Pull request number

**Example**:
```bash
bash .claude/skills/github-operations/scripts/get-pr-files.sh 45
```

## PR Conventions for quber_excel

**IMPORTANT**: All PR standards are defined in `docs/GITHUB_WORKFLOW_SPEC.md`. This Skill follows those specifications.

### Quick Reference

**Title Format**: `QUE-XXX: Brief description of changes`
- Example: `QUE-149: Refactor github-workflow agent to reference GITHUB_WORKFLOW_SPEC.md`

**Branch Naming**: `<type>/QUE-XXX-brief-description`
- Example: `feature/QUE-149-refactor-github-agent-specs`
- Example: `bugfix/QUE-131-fix-jira-exit-error`

**PR Body**: Must include Summary, Related Jira Issue, Acceptance Criteria with Functional Evidence, Test Evidence, Changes Made

See `docs/GITHUB_WORKFLOW_SPEC.md` for complete PR standards, functional evidence requirements, and quality gates.

## Error Handling

All scripts return:
- **Exit code 0**: Success
- **Exit code 1**: Error (check stderr for details)

## Integration with Agents

This Skill is designed for use by the `github-workflow` agent. When the agent needs to perform GitHub operations:

1. Agent determines operation needed
2. Agent calls appropriate script via Bash tool
3. Script executes using `gh` CLI
4. Results returned to agent
5. Agent formats response for user

## Repository Auto-Detection

The GitHub CLI (`gh`) automatically detects the repository from `git config --get remote.origin.url`. Scripts do not need to specify `owner` and `repo` parameters.

To verify repository:
```bash
git remote -v
```

Should show: `origin  git@github.com:xmandeng/quber_excel.git`
