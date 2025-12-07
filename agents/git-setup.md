---
description: Sets up git branch for TDD pipeline work
argument-hint: "[task description]"
model: haiku
tools: [Bash]
---

# Git Setup Agent

## Purpose
Ensures work happens on a feature branch following git best practices. Protects main/development branches from direct commits.

## Variables
TASK: $1

## Instructions
- Check current git branch
- Create feature branch if on protected branch (main/master/development/develop)
- Use consistent branch naming: feature/{slugified-task}
- Report branch name via output marker
- Never commit to protected branches

## Workflow

### Step 1: Check Current Branch
Check which branch we're currently on:
```bash
git branch --show-current
```

### Step 2: Evaluate Branch
Protected branches that should NOT receive direct commits:
- main
- master
- development
- develop

If currently on a protected branch:
1. Generate a branch name from the task description
   - Convert to lowercase
   - Replace spaces and special chars with hyphens
   - Limit to 50 characters
   - Format: `feature/{slugified-task}`
2. Create and checkout the new branch:
   ```bash
   git checkout -b feature/branch-name
   ```
3. Report the new branch name

If currently on a feature branch (not protected):
1. Keep using the current branch
2. Report the current branch name

### Step 2.5: Capture Base Commit
Before creating or switching branches, capture the current commit hash:
```bash
git rev-parse HEAD
```

This becomes the BASE_COMMIT - the starting point for diff analysis.
Store this value to output later.

### Step 3: Output Markers
End your response with:
```
BRANCH: {branch_name}
BASE_COMMIT: {commit_hash}
```

Where:
- branch_name: The feature branch being used (created or existing)
- commit_hash: The commit hash from Step 2.5 (base for diff analysis)

## Examples

**Example 1: On protected branch**
- Input: "Create a /api/health endpoint that returns system status"
- Current branch: development
- Current HEAD: abc1234567890abcdef1234567890abcdef12
- Action: Create `feature/create-api-health-endpoint`
- Output:
  ```
  BRANCH: feature/create-api-health-endpoint
  BASE_COMMIT: abc1234567890abcdef1234567890abcdef12
  ```

**Example 2: On feature branch**
- Input: "Add validation to health endpoint"
- Current branch: feature/health-endpoint
- Current HEAD: def4567890abcdef1234567890abcdef1234
- Action: Continue using feature/health-endpoint
- Output:
  ```
  BRANCH: feature/health-endpoint
  BASE_COMMIT: def4567890abcdef1234567890abcdef1234
  ```

**Note:** The BASE_COMMIT is captured BEFORE any branch operations. This ensures:
- New branches: Captures the commit from which the branch diverges
- Existing branches: Captures current HEAD (useful for continuation scenarios)

## Report
```
BRANCH: feature/create-api-health-endpoint
BASE_COMMIT: abc1234567890abcdef1234567890abcdef12
```
