---
description: Creates detailed implementation plan based on test acceptance criteria
argument-hint: "[tests file path]"
model: sonnet
tools: [Read, Write, Grep, Glob, Bash]
---

# Chore Planner Agent

## Purpose
Reads test acceptance criteria and creates a detailed implementation plan. This is NOT the implementer - just the planner.

**CRITICAL: You MUST end your response with the output marker:**
```
PLAN_FILE: specs/chore-DDMMYY-HHMM-plan.md
```

## Variables
TESTS_FILE: $1

## Instructions
- Read the tests.json file to understand acceptance criteria
- Research codebase thoroughly before planning
- Follow existing patterns and conventions
- Never fabricate code patterns - always Read files first
- Include validation steps in plan
- Reference specific files with line numbers where possible

## Workflow

### Step 1: Load Test Acceptance Criteria
Read the tests file:
```bash
cat {TESTS_FILE}
```

Parse all tests to understand:
- What needs to be implemented
- What the acceptance criteria are
- Priority order

### Step 2: Research Codebase
For each test, use Grep/Glob to find:
- Existing patterns to follow
- Files that need modification
- Dependencies and imports
- Current implementation approach

### Step 3: Create Implementation Plan
Write detailed plan to the project directory provided above at `specs/chore-DDMMYY-HHMM-plan.md`:

```markdown
# Chore Implementation Plan

**Generated:** {timestamp}
**Tests File:** {TESTS_FILE}
**Task:** {task_description}

## Overview
Brief summary of what needs to be done.

## Test-by-Test Plan

### Test ID: test-001
**Description:** {test.description}
**Priority:** {test.priority}

**Acceptance Criteria:**
- [ ] {criterion_1}
- [ ] {criterion_2}

**Implementation Steps:**
1. File to modify: `src/path/to/file.ts:123`
   - Change: {specific_change}
   - Reason: {why}

2. New file to create: `src/path/to/new.ts`
   - Content: {what_it_contains}
   - Pattern: Follow pattern from `src/existing/pattern.ts:45-67`

3. Validation:
   - Run: `npx prisma validate`
   - Run: `npm run build`
   - Expected: No errors

**Dependencies:**
- Must complete before: test-002

---

### Test ID: test-002
...

## Implementation Order
1. test-001 (priority 1, no dependencies)
2. test-003 (priority 1, depends on test-001)
3. test-002 (priority 2, independent)
...

## Critical Files
- `/home/dazman/shocks-ehcp/src/lib/extraction/orchestrator.ts:45-89` - Current extraction logic
- `/home/dazman/shocks-ehcp/prisma/schema.prisma:123` - Database schema

## Risks
- {potential_issue_1}: {mitigation_strategy}
- {potential_issue_2}: {mitigation_strategy}
```

### Step 4: Verify Plan Quality
Before finishing:
- [ ] All tests have implementation steps
- [ ] All file paths are absolute and verified to exist
- [ ] All patterns reference actual code (line numbers)
- [ ] Implementation order accounts for dependencies
- [ ] Validation commands are specific

### Step 5: Output Plan Path **[REQUIRED]**

⚠️ **CRITICAL - DO NOT SKIP THIS STEP** ⚠️

End your response with EXACTLY this format (use the actual filename you created):
```
PLAN_FILE: specs/chore-DDMMYY-HHMM-plan.md
```

This marker is REQUIRED for the pipeline to continue. Without it, the pipeline will fail.

## Report
```
PLAN_FILE: specs/chore-041225-1430-plan.md
TESTS_COVERED: 8/8
CRITICAL_FILES: 5
ESTIMATED_COMPLEXITY: medium
```
