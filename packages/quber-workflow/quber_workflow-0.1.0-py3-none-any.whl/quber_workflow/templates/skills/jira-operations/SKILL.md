---
name: jira-operations
description: Jira issue management for QUE project using Jira REST API. Use when searching issues, creating issues, updating issues, adding comments, transitioning issue status, or getting issue details. Automatically uses QUE project key.
allowed-tools: Bash, Read
---

# Jira Operations Skill

This Skill provides Jira issue management capabilities using the Jira REST API.

## Prerequisites

- Environment variables must be set:
  - `ATLASSIAN_SITE_NAME` - Jira site URL (e.g., https://mandeng.atlassian.net)
  - `ATLASSIAN_USER_EMAIL` - Your Jira email
  - `ATLASSIAN_API_TOKEN` - Your Jira API token
  - `JIRA_PROJECT_PREFIX` - Project key (e.g., QUE)
  - `JIRA_PROJECT_LABEL` - Project label automatically applied to all created issues (e.g., quber-excel)
- `curl` and `jq` must be installed
- Default project: `QUE`

## Available Operations

### 1. Search Issues

**Script**: `scripts/search-issues.sh`

**Usage**:
```bash
bash .claude/skills/jira-operations/scripts/search-issues.sh \
  "JQL query" \
  [fields] \
  [limit]
```

**Arguments**:
- `jql`: JQL query string
- `fields`: Optional comma-separated field list (default: summary,status,issuetype,created,priority)
- `limit`: Optional max results (default: 50)

**Examples**:
```bash
# Search recent QUE issues
bash .claude/skills/jira-operations/scripts/search-issues.sh \
  "project = QUE ORDER BY created DESC" \
  "summary,status,assignee" \
  10

# Search by status
bash .claude/skills/jira-operations/scripts/search-issues.sh \
  "project = QUE AND status = 'In Progress'"
```

### 2. Get Issue Details

**Script**: `scripts/get-issue.sh`

**Usage**:
```bash
bash .claude/skills/jira-operations/scripts/get-issue.sh <issue-key>
```

**Arguments**:
- `issue-key`: Jira issue key (e.g., QUE-122)

**Example**:
```bash
bash .claude/skills/jira-operations/scripts/get-issue.sh QUE-122
```

### 3. Create Issue

**Script**: `scripts/create-issue.sh`

**Usage**:
```bash
bash .claude/skills/jira-operations/scripts/create-issue.sh \
  "summary" \
  "description" \
  [issue-type] \
  [priority] \
  [project-key] \
  [parent-key] \
  [labels]
```

**Arguments**:
- `summary`: Issue title
- `description`: Issue description (markdown supported)
- `issue-type`: Optional (default: Task) - Task, Bug, Story, Epic, Subtask
- `priority`: Optional (default: Medium) - Highest, High, Medium, Low, Lowest
- `project-key`: Optional (default: QUE)
- `parent-key`: Optional - Parent issue key for subtasks or epic linking
- `labels`: Optional (default: $JIRA_PROJECT_LABEL) - Comma-separated labels (e.g., "quber-excel,urgent")

**Examples**:
```bash
# Create standalone task
bash .claude/skills/jira-operations/scripts/create-issue.sh \
  "Add unit tests for spatial grid" \
  "## Description
Need comprehensive unit tests for the spatial grid module.

## Acceptance Criteria
- Test empty grid handling
- Test merged cell scenarios" \
  "Task" \
  "High"

# Create subtask under QUE-122
bash .claude/skills/jira-operations/scripts/create-issue.sh \
  "Test spatial grid edge cases" \
  "Verify edge case handling" \
  "Subtask" \
  "Medium" \
  "QUE" \
  "QUE-122"

# Create task linked to epic QUE-89
bash .claude/skills/jira-operations/scripts/create-issue.sh \
  "Implement feature X" \
  "Feature X implementation" \
  "Task" \
  "High" \
  "QUE" \
  "QUE-89"
```

### 4. Update Issue

**Script**: `scripts/update-issue.sh`

**Usage**:
```bash
bash .claude/skills/jira-operations/scripts/update-issue.sh \
  <issue-key> \
  <field> \
  <value>
```

**Arguments**:
- `issue-key`: Jira issue key
- `field`: Field to update (summary, description, priority, parent)
- `value`: New value

**Examples**:
```bash
# Update summary
bash .claude/skills/jira-operations/scripts/update-issue.sh \
  QUE-122 \
  summary \
  "Updated task summary"

# Link to epic QUE-89
bash .claude/skills/jira-operations/scripts/update-issue.sh \
  QUE-122 \
  parent \
  QUE-89

# Link subtask to parent task
bash .claude/skills/jira-operations/scripts/update-issue.sh \
  QUE-125 \
  parent \
  QUE-122
```

### 5. Add Comment

**Script**: `scripts/add-comment.sh`

**Usage**:
```bash
bash .claude/skills/jira-operations/scripts/add-comment.sh \
  <issue-key> \
  "comment text"
```

**Arguments**:
- `issue-key`: Jira issue key
- `comment`: Comment text (markdown supported)

**Example**:
```bash
bash .claude/skills/jira-operations/scripts/add-comment.sh \
  QUE-122 \
  "Implementation completed in PR #45"
```

### 6. Transition Issue

**Script**: `scripts/transition-issue.sh`

**Usage**:
```bash
bash .claude/skills/jira-operations/scripts/transition-issue.sh \
  <issue-key> \
  <transition-id>
```

**Arguments**:
- `issue-key`: Jira issue key
- `transition-id`: Transition ID (get from get-transitions.sh)

**Example**:
```bash
# First get available transitions
bash .claude/skills/jira-operations/scripts/get-transitions.sh QUE-122

# Then transition
bash .claude/skills/jira-operations/scripts/transition-issue.sh QUE-122 31
```

### 7. Get Available Transitions

**Script**: `scripts/get-transitions.sh`

**Usage**:
```bash
bash .claude/skills/jira-operations/scripts/get-transitions.sh <issue-key>
```

**Arguments**:
- `issue-key`: Jira issue key

**Example**:
```bash
bash .claude/skills/jira-operations/scripts/get-transitions.sh QUE-122
```

### 8. Delete Issue

**Script**: `scripts/delete-issue.sh`

**Usage**:
```bash
bash .claude/skills/jira-operations/scripts/delete-issue.sh <issue-key>
```

**Arguments**:
- `issue-key`: Jira issue key

**Example**:
```bash
bash .claude/skills/jira-operations/scripts/delete-issue.sh QUE-123
```

**Warning**: This permanently deletes the issue. Use with caution.

### 9. Get Issue Types

**Script**: `scripts/get-issue-types.sh`

**Usage**:
```bash
bash .claude/skills/jira-operations/scripts/get-issue-types.sh [project-key]
```

**Arguments**:
- `project-key`: Optional (default: QUE)

**Example**:
```bash
bash .claude/skills/jira-operations/scripts/get-issue-types.sh QUE
```

**Output**: Returns available issue types with their IDs, names, subtask flag, and hierarchy levels:
```json
[
  {"id": "10004", "name": "Epic", "subtask": false, "hierarchyLevel": 1},
  {"id": "10001", "name": "Task", "subtask": false, "hierarchyLevel": 0},
  {"id": "10002", "name": "Bug", "subtask": false, "hierarchyLevel": 0},
  {"id": "10003", "name": "Story", "subtask": false, "hierarchyLevel": 0},
  {"id": "10005", "name": "Subtask", "subtask": true, "hierarchyLevel": -1}
]
```

## JQL Query Examples

**Recent issues**:
```
project = QUE ORDER BY created DESC
```

**By status**:
```
project = QUE AND status = 'In Progress'
```

**By assignee**:
```
project = QUE AND assignee = currentUser()
```

**Recently updated**:
```
project = QUE AND updated >= -7d
```

**By type**:
```
project = QUE AND issuetype = Task
```

**By priority**:
```
project = QUE AND priority = High
```

## Error Handling

All scripts return:
- **Exit code 0**: Success (JSON output)
- **Exit code 1**: Error (stderr contains error message)

## Integration with Agents

This Skill is designed for use by the `jira-workflow` agent. When the agent needs to perform Jira operations:

1. Agent determines operation needed
2. Agent calls appropriate script via Bash tool
3. Script executes Jira REST API call via curl
4. Results returned as JSON to agent
5. Agent formats response for user

## Project Configuration

**Default Project**: QUE (Quberai)
**Site**: https://mandeng.atlassian.net

All scripts automatically use the QUE project key unless otherwise specified.
