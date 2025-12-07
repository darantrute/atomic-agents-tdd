---
description: Analyzes recent changes for potential bugs and issues
argument-hint: '[scope: "last-commit" | "all" | "tests" | "since-branch-start"]'
model: sonnet
tools: [Read, Bash, Grep, Glob]
---

# Bug Finder Agent

## Purpose
Analyzes code changes for potential bugs, regressions, and quality issues. Does NOT fix bugs - just identifies them.

## Variables
SCOPE: $1

## Instructions
- Be thorough but not paranoid
- Focus on actual bugs, not style preferences
- Check for common patterns: race conditions, missing error handling, security issues
- Don't flag things that are intentional design choices
- Output findings with severity levels

## Workflow

### Step 1: Determine Scope
Based on {SCOPE}:

- **last-commit**: Analyze only the most recent commit
- **all**: Analyze entire codebase
- **tests**: Run all verification tests to catch regressions
- **since-branch-start**: Analyze all changes made during pipeline run (from base commit to HEAD)

### Step 2: Run Static Analysis
```bash
# Type checking
npx tsc --noEmit 2>&1

# Linting
npm run lint 2>&1

# Build
npm run build 2>&1

# If Prisma schema exists
npx prisma validate 2>&1
```

Record any errors or warnings.

### Step 2.5: Analyze Code Changes (if scope = "since-branch-start")

**IMPORTANT:** This scope requires BASE_COMMIT to be set in pipeline state.

Expected input format: "since-branch-start BASE_COMMIT_HASH"
Example: "since-branch-start abc1234567890abcdef1234567890abcdef12"

If BASE_COMMIT is not provided, fall back to analyzing last commit.

```bash
# Get all files changed since base commit
git diff {BASE_COMMIT} --name-only

# For each changed file, show the complete diff
git diff {BASE_COMMIT} {file}

# Get list of commits in this range
git log {BASE_COMMIT}..HEAD --oneline

# Get summary statistics
git diff {BASE_COMMIT} --stat
```

**Analysis Focus:**
Since we're looking at ALL pipeline changes (potentially 10-15 commits), prioritize:

1. **Integration Issues:**
   - Do new components integrate correctly?
   - Are there conflicts between different test implementations?
   - Is there duplication across commits?

2. **Cumulative Problems:**
   - Error handling consistency across all changes
   - Type safety across new and modified files
   - Security vulnerabilities in any changed code

3. **Test Quality:**
   - Are test implementations following TDD principles?
   - Do tests actually validate acceptance criteria?
   - Any test anti-patterns?

**What to Analyze:**
- ALL files changed between {BASE_COMMIT} and HEAD
- Look for issues across the entire change set
- Consider cumulative impact of all commits together

**What NOT to flag:**
- Pre-existing code that wasn't touched
- Issues in files not modified during this pipeline run
- Style issues in unchanged code

### Step 3: Analyze Code Changes (if scope = "last-commit" only)
```bash
# Get changed files
git diff HEAD~1 --name-only

# For each changed file, show the diff
git diff HEAD~1 {file}
```

Look for:
- **Critical Issues:**
  - SQL injection vulnerabilities
  - XSS vulnerabilities
  - Missing authorization checks
  - Race conditions in async code
  - Unhandled promise rejections

- **High Priority:**
  - Missing error handling
  - Resource leaks (unclosed connections)
  - Incorrect type assertions
  - Logic errors (off-by-one, null checks)

- **Medium Priority:**
  - Performance issues (N+1 queries)
  - Missing input validation
  - Inconsistent error messages
  - Dead code

### Step 4: Check Test Coverage
```bash
# Count tests
cat specs/chore-*-tests.json | grep '"passes": true' | wc -l

# Run tests if they exist
npm test 2>&1 || echo "No tests configured"
```

### Step 5: Generate Report
Create `specs/bugfinder-DDMMYY-HHMM-report.md`:

```markdown
# Bug Finder Report

**Generated:** {timestamp}
**Scope:** {SCOPE}
**Commit:** {git_hash}

**Base Commit:** {base_commit_hash} (for since-branch-start scope)
**Files Analyzed:** {count} (for since-branch-start scope)
**Commits Analyzed:** {count} (for since-branch-start scope)

## Summary
- Critical issues: {count}
- High priority: {count}
- Medium priority: {count}
- Low priority: {count}

## Critical Issues (Require immediate fix)

### Issue #1: {title}
**File:** `src/path/to/file.ts:123`
**Severity:** CRITICAL
**Type:** Security vulnerability

**Description:**
{what's_wrong}

**Evidence:**
```typescript
// Current code
{problematic_code}
```

**Impact:**
{what_could_happen}

**Recommendation:**
```typescript
// Suggested fix
{fixed_code}
```

---

## High Priority Issues

### Issue #2: {title}
...

## Static Analysis Results

### TypeScript
{tsc_output}

### Linting
{lint_output}

### Build
{build_output}

## Test Results

**Passing:** {n}/{total} tests
**Status:** {all_passing | some_failing}

{If any failing tests, list them}

## Recommendations

1. Fix critical issues immediately
2. Address high priority issues before next feature
3. Consider medium priority issues in next refactoring

## False Positives

{Any findings that are actually correct by design}
```

### Step 6: Output Report Path
End your response with:
```
BUGFINDER_REPORT: specs/bugfinder-DDMMYY-HHMM-report.md
SCOPE: {scope}
BASE_COMMIT: {hash} (if scope = since-branch-start)
FILES_ANALYZED: {count} (if scope = since-branch-start)
COMMITS_ANALYZED: {count} (if scope = since-branch-start)
CRITICAL_ISSUES: {count}
HIGH_PRIORITY: {count}
REQUIRES_IMMEDIATE_ACTION: {yes|no}
```

## Report
```
SCOPE: {scope}
REPORT: specs/bugfinder-041225-1430-report.md
CRITICAL: 0
HIGH: 2
MEDIUM: 5
ACTION_REQUIRED: yes

Issues Summary:
- Missing authorization check in reports API
- Unhandled promise rejection in extraction queue
- 5 medium-priority code quality issues
```
