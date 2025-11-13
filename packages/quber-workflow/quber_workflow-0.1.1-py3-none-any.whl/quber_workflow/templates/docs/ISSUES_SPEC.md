# Jira Issues Specification

This document defines the complete specification for Jira issue types, templates, workflows, and quality standards for the Financial Document Analyzer project.

**Purpose**: This is a pure specification document that defines WHAT issues should contain and HOW they should be structured. Implementation details (HOW to create issues) are handled by the jira-workflow agent.

## Table of Contents

- [Overview](#overview)
- [Project Context](#project-context)
- [Issue Types](#issue-types)
- [Type Selection Logic](#type-selection-logic)
- [Issue Templates](#issue-templates)
- [Title Conventions](#title-conventions)
- [Test Evidence Requirements](#test-evidence-requirements)
- [Epic Governance](#epic-governance)
- [Sub-task Guidance](#sub-task-guidance)
- [Status Workflow](#status-workflow)
- [Validation Rules](#validation-rules)
- [Response Formats](#response-formats)
- [Priority and Defaults](#priority-and-defaults)

---

## Overview

All Jira issue operations follow these core principles:

1. **Type Intelligence**: Automatically select appropriate issue type based on request analysis
2. **Quality Enforcement**: Every ticket embeds mandatory Test Evidence Requirements
3. **Epic Governance**: Epics are team-managed strategic tools (agents link but don't create)
4. **Evidence First**: Production data verification is mandatory for all PRs
5. **Sub-tasks are Optional**: Use only when warranted (3+ pieces, parallelizable work)

---

## Project Context

- **Project Key**: `QUE` (Quberai)
- **Jira Instance**: https://mandeng.atlassian.net
- **Repository**: quber-excel
- **Main Branch**: main
- **Issue Types**: Epic (team-only), Story, Task, Bug, Sub-task

---

## Issue Types

### Epic (Team-Managed Only)

**Purpose**: Large business initiative spanning multiple Stories/Tasks

**Creation**: ❌ **Agents CANNOT create Epics**
- Epics are strategic planning tools managed by the team
- Requires manual creation via Jira UI
- Agents can link issues to existing Epics

**Known Epics**:
- **QUE-89**: Core Infrastructure - Models, Protocols, Config
- **QUE-1**: Document Processing - PDF to Tables
- **QUE-2**: Metrics Search - Matching Strategies
- **QUE-91**: Extraction & Validation - PydanticAI Agent
- **QUE-92**: Pipeline & Web UI - FastAPI + HTMX

### Story

**Purpose**: User-facing feature or capability that delivers direct value

**When to use**:
- End-user features
- New capabilities
- User workflows
- UI/UX improvements

**Keywords**: "feature", "as a user", "capability", "upload", "process", "view", "enable"

**Examples**:
- "Upload and Process PDF Documents"
- "Add CLI for markdown conversion"
- "Enable merged cell detection"

### Task

**Purpose**: Technical work, infrastructure, refactoring, internal improvements

**When to use**:
- Technical upgrades
- Refactoring
- Infrastructure setup
- Internal optimizations
- Test improvements

**Keywords**: "implement", "refactor", "upgrade", "migrate", "add tests", "setup", "optimize"

**Examples**:
- "Upgrade Python to 3.13"
- "Refactor table matching logic"
- "Optimize cell extraction performance"
- "Setup Logfire instrumentation"

### Bug

**Purpose**: Defect, error, unexpected behavior, broken functionality

**When to use**:
- Something broken
- Incorrect behavior
- Errors/exceptions
- Regression issues

**Keywords**: "fix", "error", "broken", "fails", "incorrect", "bug", "regression"

**Examples**:
- "PDF extraction fails on rotated pages"
- "Fix merged cell coordinate calculation"
- "Handle empty worksheets without errors"

### Sub-task

**Purpose**: Implementation piece under parent Story/Task/Bug

**When to use** (situational, optional):
- ✅ Parent has 3+ distinct implementation pieces
- ✅ Work can be parallelized across multiple PRs
- ✅ Complex bug requiring multiple separate fixes
- ✅ Clear breakdown of independent steps

**When NOT to use**:
- ❌ Single cohesive change (use checklist in parent instead)
- ❌ Only 1-2 simple steps
- ❌ Steps must be done together in one PR

**Examples**:
- "Create upload API endpoint" (under "Upload and Process PDF Documents" Story)
- "Add storage layer" (under parent Story)
- "Build upload UI component" (under parent Story)

---

## Type Selection Logic

When creating an issue, analyze the request and automatically select the appropriate type:

### Decision Tree

```
Is this a large strategic initiative spanning multiple Stories?
├─ YES → ❌ CANNOT CREATE (Epic - team-managed)
└─ NO → Continue...

Does this deliver direct value to end users?
├─ YES → ✅ Story
└─ NO → Continue...

Is this fixing broken/incorrect functionality?
├─ YES → ✅ Bug
└─ NO → Continue...

Is this technical work without user-visible changes?
├─ YES → ✅ Task
└─ NO → Continue...

Is this an implementation piece under an existing parent?
├─ YES → ✅ Sub-task (if warranted - 3+ pieces)
└─ NO → Ask for clarification
```

### Ambiguous Cases

If type cannot be determined:
1. Ask for clarification
2. Present options with reasoning
3. Wait for response before creating

**Example**:
```
ℹ️ Type clarification needed

"Refactor table matching logic" could be:
- Task: Internal technical refactoring (no user-visible changes)
- Story: If this changes user experience or adds new capabilities

Which is more appropriate for this work?
```

---

## Issue Templates

All templates below use **Jira markup format** (not markdown).

### Story Template

```
h2. User Story

*As a* [financial analyst / developer / user]
*I want* [feature/capability]
*So that* [benefit/value delivered]

h2. Acceptance Criteria

*CRITICAL*: Each criterion MUST specify how to verify with PRODUCTION DATA

h3. AC1: [Feature capability]

* *Verify by:* [How to verify - use realistic data, real workflows, actual scenarios]
* *Expected:* [Concrete, measurable outcome with numbers/specifics]
* *Show:* [What to demonstrate - file names, sizes, results]

h3. AC2: [Next capability]

* *Verify by:* [How to verify this works]
* *Expected:* [Concrete, measurable outcome]
* *Show:* [What to demonstrate]

h3. AC3: [Additional capability if needed]

* *Verify by:* [How to verify this works]
* *Expected:* [Concrete, measurable outcome]
* *Show:* [What to demonstrate]

h2. Story Points

*Points*: [1, 2, 3, 5, 8, 13]

h2. Priority

*Priority*: [High/Medium/Low - default to Medium]

h2. Technical Notes

*Implementation considerations:*
* Uses PydanticAI for structured LLM outputs
* Logfire tracing required for key operations
* Must pass pyright --strict type checking
* Follow protocol-based design patterns
* Use frozen Pydantic models where appropriate

h2. Test Evidence Requirements

*CRITICAL - CANNOT BE SKIPPED*

When implementing, the PR MUST include *functional evidence* for EACH acceptance criterion:

✅ *Real Production/Realistic Data*
* Use actual production data or realistic files (NOT test fixtures from {{tests/fixtures/}})
* For file processing: show file names, sizes, and processing results
* For API/service: show realistic requests/responses
* For UI: show actual user workflows with real data

✅ *Actual Usage Workflows*
* Demonstrate the feature working as specified in acceptance criteria
* Show integration with existing systems works
* Prove end-to-end workflows function correctly

✅ *Concrete, Measurable Results*
* Specific file names, sizes, or identifiers
* Quantifiable outcomes (counts, durations, sizes)
* Sample output data relevant to the feature

✅ *End-to-End Verification*
* Show feature works in application context
* Verify dependencies actually work (import and use them)
* Demonstrate configuration settings function

*Reference*: See [docs/PR_EVIDENCE_GUIDELINES.md|https://github.com/xmandeng/quber-analyst/blob/main/docs/PR_EVIDENCE_GUIDELINES.md] for comprehensive standards and examples (PR #59, PR #60).

*Evidence Checklist:*
* [ ] Tested with realistic data appropriate to the feature
* [ ] Documented concrete, measurable results (file sizes, counts, etc.)
* [ ] Showed feature working as specified in ACs
* [ ] Demonstrated end-to-end in realistic context
* [ ] Included specific examples with verifiable details

*Test Data Available:*
* Production JSON files: {{inputs/}} directory
* For other features: use realistic data appropriate to what you're building

h2. Definition of Done

* [ ] Code implemented and tested
* [ ] *Functional evidence provided for EACH acceptance criterion*
* [ ] Unit tests passing (80%+ coverage target)
* [ ] Type checking clean (pyright --strict)
* [ ] Linting clean (ruff check)
* [ ] Logfire instrumentation added for key operations
* [ ] Documentation updated
* [ ] Code reviewed and approved
* [ ] Merged to main branch

h2. Dependencies

[Other stories or tasks that must be completed first]
* None

h2. Related Epic

Epic: [QUE-XXX or leave blank if unclear]

h2. Workstream

Workstream: [WS1, WS2, WS3, WS4, or WS5 - if applicable]

h2. Additional Context

[Screenshots, examples, diagrams, or other helpful information]
```

---

### Task Template

```
h2. Task Description

[Clear description of what technical work needs to be done]

h2. Parent Story

[Link to the user story this task belongs to, if applicable]
Story: [QUE-XXX or None]

h2. Implementation Details

[Technical approach or specific requirements - use checklist for steps]

* [ ] Step 1
* [ ] Step 2
* [ ] Step 3

h2. Estimated Time

*Estimate*: [hours/days - rough estimate]

h2. Priority

*Priority*: [High/Medium/Low - default to Medium]

h2. Test Evidence Requirements

*CRITICAL - CANNOT BE SKIPPED*

When creating PR, you MUST provide *functional evidence* for each requirement:

✅ *For EACH step in Implementation Details:*
# Use REAL production/realistic data (NOT test fixtures from {{tests/}})
# Show concrete, measurable results
# Demonstrate feature working as specified
# Prove it works in realistic application context

*Evidence Checklist:*
* [ ] Tested with realistic data appropriate to the feature
* [ ] Documented concrete, measurable results
* [ ] Showed feature working as specified
* [ ] Demonstrated end-to-end in realistic context
* [ ] Included specific examples with verifiable details

*Reference*: See [docs/PR_EVIDENCE_GUIDELINES.md|https://github.com/xmandeng/quber-analyst/blob/main/docs/PR_EVIDENCE_GUIDELINES.md]

Examples: PR #59 (JSON loader), PR #60 (Python 3.13 upgrade)

h2. Definition of Done

* [ ] Implementation complete
* [ ] *Functional evidence provided for each requirement*
* [ ] Tests added/updated
* [ ] Code follows project standards
* [ ] No linting errors (ruff check)
* [ ] Type checking passes (pyright --strict)
* [ ] Logfire spans added for key operations
* [ ] PR created and linked

h2. Dependencies

[Other tasks that must be completed first]
* None

h2. Technical Notes

*Follow project patterns:*
* Use protocol-based design (if implementing interface)
* Use PydanticAI for LLM interactions
* Add Logfire instrumentation
* Ensure frozen Pydantic models (immutable where appropriate)
* Strict type hints on all functions

h2. Resources

* [ARCHITECTURE.md|https://github.com/xmandeng/quber-analyst/blob/main/docs/ARCHITECTURE.md]
* [WORKSTREAMS.md|https://github.com/xmandeng/quber-analyst/blob/main/docs/WORKSTREAMS.md]
* [DECISIONS.md|https://github.com/xmandeng/quber-analyst/blob/main/docs/DECISIONS.md]

h2. Related Epic

Epic: [QUE-XXX or leave blank if unclear]

h2. Workstream

Workstream: [WS1, WS2, WS3, WS4, or WS5 - if applicable]
```

---

### Bug Template

```
h2. Bug Description

[Clear description of what is broken or behaving incorrectly]

h2. Steps to Reproduce

# [First step]
# [Second step]
# [Third step]

h2. Expected Behavior

[What should happen]

h2. Actual Behavior

[What actually happens - the bug]

h2. Environment

* *Python Version*: [e.g., 3.13]
* *OS*: [e.g., Ubuntu 22.04, macOS 14]
* *Relevant Dependencies*: [e.g., pydantic 2.10, docling 2.17]

h2. Error Messages / Logs

{code}
[Paste any error messages or relevant log output]
{code}

h2. Severity

*Severity*: [Critical/High/Medium/Low]
* *Critical*: System down, data loss, security issue
* *High*: Major functionality broken, no workaround
* *Medium*: Functionality impaired, workaround exists
* *Low*: Minor issue, cosmetic problem

h2. Acceptance Criteria for Fix

h3. AC1: Bug no longer occurs

* *Verify by:* [Reproduce original steps - should now work]
* *Expected:* [Correct behavior observed]
* *Show:* [Concrete evidence it's fixed]

h3. AC2: No regressions introduced

* *Verify by:* [Run existing workflows/tests]
* *Expected:* [All existing functionality still works]
* *Show:* [Evidence of regression testing]

h2. Test Evidence Requirements

*CRITICAL - CANNOT BE SKIPPED*

When creating PR with fix, you MUST provide *functional evidence*:

✅ *Reproduction*
* Show you can reproduce the original bug (before fix)
* Document the error/incorrect behavior

✅ *Fix Verification*
* Show the bug no longer occurs (after fix)
* Use realistic data/scenarios that triggered the bug
* Demonstrate correct behavior with concrete examples

✅ *Regression Testing*
* Prove existing workflows still function
* Show related features unaffected
* Demonstrate end-to-end scenarios work

*Evidence Checklist:*
* [ ] Reproduced original bug (before fix)
* [ ] Verified bug fixed (after fix) with realistic scenario
* [ ] Tested for regressions in related functionality
* [ ] Documented concrete results showing correct behavior
* [ ] Included specific examples with verifiable details

*Reference*: See [docs/PR_EVIDENCE_GUIDELINES.md|https://github.com/xmandeng/quber-analyst/blob/main/docs/PR_EVIDENCE_GUIDELINES.md]

h2. Definition of Done

* [ ] Bug fixed and verified
* [ ] *Functional evidence provided* (reproduced bug + verified fix)
* [ ] Tests added to prevent regression
* [ ] Existing tests still pass
* [ ] Type checking clean (pyright --strict)
* [ ] Linting clean (ruff check)
* [ ] PR created and linked

h2. Root Cause Analysis

[Optional: What caused the bug? Understanding helps prevent similar issues]

h2. Dependencies

[Any blockers or related issues]
* None

h2. Related Epic

Epic: [QUE-XXX or leave blank if unclear]

h2. Workstream

Workstream: [WS1, WS2, WS3, WS4, or WS5 - if applicable]
```

---

### Sub-task Template

**NOTE**: Use only when warranted (3+ implementation pieces, parallelizable work)

```
h2. Sub-task Description

[Clear description of this specific implementation piece]

*Parent*: [QUE-XXX - REQUIRED, must specify parent]

h2. What This Accomplishes

[How this sub-task contributes to the parent ticket goal]

h2. Implementation Steps

* [ ] Step 1
* [ ] Step 2
* [ ] Step 3

h2. Acceptance Criteria

[Simplified - focus on this piece only, not entire parent goal]

* *Verify by:* [How to verify this piece works]
* *Expected:* [Specific outcome for this sub-task]
* *Show:* [What to demonstrate]

h2. Priority

*Priority*: [Inherits from parent - typically same as parent]

h2. Test Evidence Requirements

*CRITICAL - CANNOT BE SKIPPED*

Even for Sub-tasks, PR MUST include *functional evidence*:

✅ *Demonstrate this piece works* with realistic data
✅ *Show concrete results* specific to this sub-task
✅ *Prove integration* with parent ticket context

*Evidence Checklist:*
* [ ] Tested with realistic data
* [ ] Documented concrete results
* [ ] Showed sub-task working as specified
* [ ] Verified integration with parent context

*Reference*: See [docs/PR_EVIDENCE_GUIDELINES.md|https://github.com/xmandeng/quber-analyst/blob/main/docs/PR_EVIDENCE_GUIDELINES.md]

h2. Definition of Done

* [ ] Implementation complete for this piece
* [ ] *Functional evidence provided*
* [ ] Tests added/updated for this piece
* [ ] Type checking clean (pyright --strict)
* [ ] Linting clean (ruff check)
* [ ] Logfire spans added if needed
* [ ] PR created and linked
* [ ] Parent ticket updated (if all sub-tasks done)

h2. Technical Notes

[Any specific technical considerations for this piece]
* Follow same standards as parent ticket
* Use PydanticAI, Logfire, protocols as appropriate

h2. Related Epic

[Inherited from parent - usually same as parent's Epic]
Epic: [QUE-XXX or leave blank]
```

---

### Epic Template (Reference Only - Team Creates)

**NOTE**: Agents cannot create Epics. This template shows expected structure for team-created Epics.

```
h2. Epic Overview

[Clear description of what this epic will deliver]

h2. Business Value

[Why this epic is important and what value it brings]

h2. Success Metrics

* [ ] Metric 1
* [ ] Metric 2
* [ ] Metric 3

h2. User Stories

[List the user stories that make up this epic]
* [ ] Story 1: As a..., I want..., so that...
* [ ] Story 2: As a..., I want..., so that...

h2. Dependencies

* None

h2. Target Completion

Sprint/Milestone: [target]

h2. Technical Considerations

* PydanticAI required for all LLM interactions
* Logfire integration for observability
* Strict type checking (pyright --strict)
* Protocol-based design patterns
* Frozen Pydantic models (immutable)

h2. Related Workstream

Workstream: [WS1-5]
```

---

## Title Conventions

**Format**: Clear and descriptive - **NO redundant prefixes**

Issue type is already shown in Jira - don't duplicate it in the title.

### ✅ Good Titles

- **Epic**: `Core Infrastructure - Models, Protocols, Config`
- **Story**: `Upload and Process PDF Documents`
- **Task**: `Upgrade Python to 3.13`
- **Bug**: `PDF extraction fails on rotated pages`
- **Sub-task**: `Create upload API endpoint`

### ❌ Bad Titles

- `[EPIC] Core Infrastructure`
- `[STORY] Upload and Process...`
- `As a user, I want to upload PDFs` (user story format in description, not title)
- `TASK: Upgrade Python...`
- `[BUG] PDF extraction...`
- `[SUBTASK] Create...`

---

## Test Evidence Requirements

**MANDATORY FOR ALL ISSUE TYPES**

Every PR must include functional evidence demonstrating the feature/fix works with production data.

### Core Requirements

#### 1. Real Production/Realistic Data

**Use**:
- Actual production data from `inputs/` directory
- Realistic files/scenarios relevant to the feature
- Real API requests/responses
- Actual user workflows

**DON'T Use**:
- Test fixtures from `tests/fixtures/` (unit tests only)
- Minimal test data
- Synthetic examples that don't reflect real usage

#### 2. Actual Usage Workflows

**Show**:
- Feature working as specified in acceptance criteria
- Integration with existing systems
- End-to-end workflows functioning correctly
- Real-world use cases

#### 3. Concrete, Measurable Results

**Provide**:
- Specific file names and sizes
- Quantifiable outcomes (counts, durations, percentages)
- Sample output data
- Performance metrics where relevant

#### 4. End-to-End Verification

**Demonstrate**:
- Feature works in full application context
- Dependencies function correctly
- Configuration settings work
- No regressions in existing functionality

### Evidence Checklist

Every PR must complete:

- [ ] Tested with realistic data appropriate to the feature
- [ ] Documented concrete, measurable results (file sizes, counts, etc.)
- [ ] Showed feature working as specified in acceptance criteria
- [ ] Demonstrated end-to-end in realistic context
- [ ] Included specific examples with verifiable details

### Reference Documents

- **[PR_EVIDENCE_GUIDELINES.md](PR_EVIDENCE_GUIDELINES.md)** - Comprehensive standards
- **PR #59** - Example: JSON loader with production data
- **PR #60** - Example: Python 3.13 upgrade with real workload

### Type-Specific Evidence

**Story**:
- Demonstrate each AC met with real user workflows
- Show feature delivering promised value
- Provide concrete usage examples

**Task**:
- Demonstrate each implementation step works
- Show technical improvement with measurable results
- Prove changes integrate correctly

**Bug**:
- Reproduce original bug (before fix)
- Verify bug fixed (after fix) with realistic scenario
- Demonstrate no regressions in related functionality

**Sub-task**:
- Demonstrate this piece works with realistic data
- Show concrete results specific to this sub-task
- Prove integration with parent ticket context

---

## Epic Governance

### Cannot Create Epics

**Epics are strategic planning tools** created by the team, not agents.

**When Epic creation is requested**:

```
❌ I cannot create Epics

Epics are strategic business initiatives managed by the team for roadmap planning.

Please create the Epic manually in Jira:
https://mandeng.atlassian.net/secure/CreateIssue.jspa

Once created, I can help link Stories, Tasks, and Bugs to it.
```

### Can Link to Existing Epics

**Decision logic**:

1. **Epic explicitly specified** → Link to it
   - "Link to Epic QUE-89"
   - "This is for the Core Infrastructure epic"

2. **Epic obvious from context** → Link automatically
   - Core/models/protocols → QUE-89 (Core Infrastructure)
   - PDF/docling/tables → QUE-1 (Document Processing)
   - Matching/heuristic/LLM → QUE-2 (Metrics Search)
   - Extraction/PydanticAI/values → QUE-91 (Extraction & Validation)
   - Pipeline/FastAPI/UI → QUE-92 (Pipeline & Web UI)

3. **Epic unclear** → Leave blank
   - Add note: "Epic assignment pending - team to assign during planning"

### Known Epics

- **QUE-89**: Core Infrastructure - Models, Protocols, Config
- **QUE-1**: Document Processing - PDF to Tables
- **QUE-2**: Metrics Search - Matching Strategies
- **QUE-91**: Extraction & Validation - PydanticAI Agent
- **QUE-92**: Pipeline & Web UI - FastAPI + HTMX

---

## Sub-task Guidance

**Sub-tasks are OPTIONAL, situational tools** - not required for every ticket.

### When to Use Sub-tasks

**Consider sub-tasks when**:
- ✅ Story/Task has **3+ distinct implementation pieces**
- ✅ Work can be **parallelized** across multiple PRs
- ✅ Complex Bug requiring **multiple separate fixes**
- ✅ Clear **breakdown** of independent steps

### When NOT to Use Sub-tasks

**Don't use sub-tasks when**:
- ❌ Single, cohesive change (use checklist in description instead)
- ❌ Only 1-2 simple steps
- ❌ Steps must be done together in one PR

### Sub-task Structure

**Can be created under**:
- Story (implementation pieces)
- Task (technical breakdown)
- Bug (complex fix steps)

**Each Sub-task**:
- Has its own status (To Do → In Progress → In Review → Done)
- Can be assigned independently
- Can be automated independently
- Inherits context from parent
- Requires functional evidence (same standards as parent types)

### Example

```
Story: QUE-50 - Upload and Process PDF Documents
├─ Sub-task: QUE-51 - Create upload API endpoint
├─ Sub-task: QUE-52 - Implement file validation
├─ Sub-task: QUE-53 - Add storage layer
└─ Sub-task: QUE-54 - Build upload UI component
```

---

## Status Workflow

### Standard Workflow

**Automated via GitHub workflows** (not manual):

```
To Do → In Progress → In Review → Done
```

### Status Meanings

- **To Do**: Refined, clear ACs, ready to start
- **In Progress**: Currently being worked on
- **In Review**: PR created, awaiting review
- **Done**: Complete and merged

### Status Transitions

**Automated via `.github/workflows/jira-transition.yml`**:

- Branch created → Jira moves to "In Progress"
- PR opened → Jira moves to "In Review"
- PR merged → Jira moves to "Done"

**Agent Role**: Read-only status awareness. Do NOT manually transition tickets.

### Workflow Example

1. Agent creates Jira ticket QUE-50 (Story)
2. Developer creates branch `feature/QUE-50-upload-pdfs`
3. GitHub workflow → QUE-50 moves to "In Progress"
4. Developer implements feature, creates PR
5. GitHub workflow → QUE-50 moves to "In Review"
6. PR merged to main
7. GitHub workflow → QUE-50 moves to "Done"

---

## Validation Rules

### Before Creating Any Ticket

**Must validate**:
- ✓ Type determined (Story/Task/Bug/Sub-task - NOT Epic)
- ✓ Title is clear and descriptive
- ✓ Title has NO redundant prefix ([STORY], [TASK], etc.)
- ✓ Template selected matches type
- ✓ Required fields for that type present
- ✓ Parent specified (if Sub-task)
- ✓ Epic link determined or explicitly left blank
- ✓ Project key is "QUE"

**If validation fails**:
```
❌ Cannot create issue
Reason: [specific problem]
Need: [what's missing or wrong]
```

### Type-Specific Validation

**Story**:
- ✓ Has user story format (As a.../I want.../So that...)
- ✓ Has acceptance criteria with Verify/Expected/Show
- ✓ Has Test Evidence Requirements section
- ✓ Has Definition of Done

**Task**:
- ✓ Has clear task description
- ✓ Has implementation details/steps
- ✓ Has Test Evidence Requirements
- ✓ Has Definition of Done

**Bug**:
- ✓ Has bug description
- ✓ Has steps to reproduce
- ✓ Has expected vs actual behavior
- ✓ Has severity
- ✓ Has Test Evidence Requirements (fix verification)

**Sub-task**:
- ✓ Has parent ticket specified
- ✓ Has clear description of piece
- ✓ Has simplified acceptance criteria
- ✓ Has Test Evidence Requirements

---

## Response Formats

### Success: Issue Created

```
✅ Created [Type] QUE-XXX
Title: [title]
Type: [Story/Task/Bug/Sub-task]
Priority: [priority]
Status: To Do
Parent Epic: [QUE-YYY or None]
Parent Issue: [QUE-ZZZ - if Sub-task]
URL: https://mandeng.atlassian.net/browse/QUE-XXX
```

### Error: Cannot Create

```
❌ Cannot create issue
Reason: [specific problem]
Need: [what's required]
Suggestion: [how to fix]
```

### Error: Epic Creation Requested

```
❌ Cannot create Epic

Epics are strategic planning tools managed by the team.
Please create Epic manually in Jira, then I can link issues to it.
```

### Info: Clarification Needed

```
ℹ️ Type clarification needed

"[request]" could be:
- [Option 1]: [reasoning]
- [Option 2]: [reasoning]

Which is more appropriate?
```

---

## Priority and Defaults

### Priority Defaults

If priority not specified:
- **Epic**: High (strategic)
- **Story**: Medium
- **Task**: Medium
- **Bug**: Based on severity
  - Critical → High
  - High → High
  - Medium → Medium
  - Low → Low
- **Sub-task**: Inherit from parent

### Smart Defaults

**Status**:
- All new issues: To Do

**Assignee**:
- Unassigned (team assigns during planning)

**Epic Linking**:
- If context clearly indicates Epic → Link automatically
- If unclear → Leave blank, note "Epic assignment pending"

---

## Integration Patterns

### GitHub Workflow Integration

**Issue Management Agent Responsibilities**:
- Create Jira tickets with quality standards
- Link tickets to Epics
- Manage ticket metadata
- Enforce Test Evidence Requirements

**GitHub Automation Responsibilities** (automated workflows):
- Listen to GitHub events (branch create, PR open, PR merge)
- Automatically transition Jira tickets based on events
- No manual status management needed

**Pull Request Agent Responsibilities**:
- Create PRs with functional evidence
- Link PRs to Jira tickets
- Manage PR reviews and merging

### Dispatcher Integration

The dispatcher automation system:
- Queries Jira for tickets with `automate:safe` label in "To Do" status
- Type-agnostic: processes Story, Task, Bug, Sub-task all the same way
- Delegates ALL Jira operations to the issue management agent
- Must provide functional evidence in all PRs

---

## Technical Standards

All tickets reference these project standards:

### Code Quality
- **Type Checking**: pyright --strict (zero errors)
- **Linting**: ruff check (zero errors)
- **Testing**: pytest (80%+ coverage target)

### Architecture
- **Protocols**: Protocol-based design for abstractions
- **Pydantic**: Frozen models where appropriate (immutable)
- **PydanticAI**: For all LLM interactions
- **Logfire**: Instrumentation for key operations

### Development
- **Python Version**: 3.13+
- **Async**: async/await for I/O operations
- **Configuration**: AppConfig (Pydantic Settings)
- **Environment Variables**: Override defaults, never hardcode secrets

---

## Reference Documents

- **[CLAUDE.md](../CLAUDE.md)** - Main project instructions
- **[PR_EVIDENCE_GUIDELINES.md](PR_EVIDENCE_GUIDELINES.md)** - Comprehensive evidence standards
- **[ARCHITECTURE.md](ARCHITECTURE.md)** - System architecture
- **[WORKSTREAMS.md](WORKSTREAMS.md)** - Workstream breakdown
- **[DECISIONS.md](DECISIONS.md)** - Key technical decisions
- **[WORKSTREAM_COMPLETION.md](WORKSTREAM_COMPLETION.md)** - Completion standards

---

## Example PRs

**Excellent Examples**:
- **[PR #59](https://github.com/xmandeng/quber-analyst/pull/59)** - JSON loader with production data evidence
- **[PR #60](https://github.com/xmandeng/quber-analyst/pull/60)** - Python 3.13 upgrade with real workload evidence

Study these PRs to understand the expected evidence quality.

---

## Summary

This specification defines:

1. **5 Issue Types**: Epic (team-only), Story, Task, Bug, Sub-task
2. **Intelligent Type Selection**: Automatic analysis-based type determination
3. **Comprehensive Templates**: All issue types with embedded quality standards
4. **Mandatory Evidence Requirements**: Production data verification for all PRs
5. **Epic Governance**: Team creates, agents link
6. **Sub-task Guidance**: Optional, situational use (3+ pieces, parallelizable)
7. **Automated Workflows**: GitHub-driven status transitions
8. **Clear Validation Rules**: Ensure quality before creation
9. **Standard Response Formats**: Consistent success/error messaging
10. **Integration Patterns**: Clear separation of responsibilities

**Implementation Note**: This is a specification document. The jira-workflow agent determines the implementation mechanism (Skills, MCP tools, or other approaches) appropriate for the project.

All agents and developers must follow these specifications when creating or managing Jira issues.
