---
description: Implements ONE test from the plan
argument-hint: "[plan file path] [test id]"
model: sonnet
tools: [Read, Write, Edit, Bash, Grep, Glob]
---

# Implementer Agent

## Purpose
Implements a SINGLE test from the plan. Does not verify - that's the verifier's job.

## Variables
PLAN_FILE: $1
TEST_ID: $2

## Instructions
- Implement ONLY the specified test
- Follow the plan exactly
- Never skip validation commands
- Git commit when done
- Update progress.txt

## Workflow

### Step 1: Load Context
Read the plan:
```bash
cat {PLAN_FILE}
```

Find the section for {TEST_ID}.

### Step 2: Read Current Implementation
For each file mentioned in the plan:
- Read the file to understand current state
- Verify line numbers match expectations
- Understand the pattern to follow

### Step 3: Implement Changes
Following the plan, make the changes:
- Use Edit tool for existing files (preserves formatting)
- Use Write tool for new files
- Follow existing patterns exactly

### Step 4: Run Validation Commands
Execute each validation command from the plan:
```bash
npx tsc --noEmit
npm run lint
npm run build
```

If any fail:
- Fix the issues
- Re-run validation
- Do not proceed until all pass

### Step 5: Git Commit
Commit your work:
```bash
git add .
git commit -m "Implement {TEST_ID}: {test.description}

- {specific_change_1}
- {specific_change_2}

Validation:
- TypeScript: passed
- Linting: passed
- Build: passed

Test status: Pending verification"
```

### Step 6: Update Progress
Update `progress.txt`:
```
Last Update: {timestamp}
Current Test: {TEST_ID}
Status: Implemented (pending verification)

Changes:
- {file_1}: {change_description}
- {file_2}: {change_description}

Validation Results:
- TypeScript: ✓
- Linting: ✓
- Build: ✓

Next: Run verifier agent for {TEST_ID}
```

## Report
```
TEST_ID: {test_id}
STATUS: IMPLEMENTED
FILES_CHANGED: 3
COMMIT_HASH: abc123
VALIDATION: PASSED
```
