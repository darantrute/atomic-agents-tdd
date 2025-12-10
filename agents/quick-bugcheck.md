---
description: Lightweight bug check after each implementation group
argument-hint: '[group number]'
model: haiku
tools: [Bash, Grep, Read]
---

# Quick Bugcheck Agent

## Purpose
Fast, lightweight quality check after each implementation group. Catches obvious issues while context is fresh. Runs in ~10 seconds.

## Variables
GROUP_NUMBER: $1

## Philosophy
- SPEED is critical (use haiku model, simple checks)
- Catch LOW-HANGING FRUIT only
- Don't duplicate full bugfinder (that runs at end)
- Focus on changed files in this group only
- Surface issues to next implementer group

## Instructions
- Get files changed in last N commits (this group)
- Run fast static checks
- Look for obvious red flags
- Store issues in state for next group
- Don't block pipeline (warning only)

## Workflow

### Step 1: Identify Changed Files in This Group

```bash
# Get commit count for this group (typically 1-3 commits)
# Assuming each group makes 1-3 commits
GROUP_COMMITS=3

# Get files changed in last N commits
git diff HEAD~$GROUP_COMMITS --name-only | grep -E '\.(ts|tsx|js|jsx)$'
```

Store in FILES_CHANGED variable.

### Step 2: Fast Type Check

```bash
# TypeScript check on changed files only
if command -v npx &> /dev/null; then
  echo "Running TypeScript check..."
  npx tsc --noEmit 2>&1 | head -20

  TYPE_ERRORS=$(npx tsc --noEmit 2>&1 | grep -c "error TS" || echo "0")

  if [ "$TYPE_ERRORS" -gt 0 ]; then
    echo "⚠️  Found $TYPE_ERRORS TypeScript errors"
  else
    echo "✅ No TypeScript errors"
  fi
else
  echo "⏭️  TypeScript not available, skipping"
  TYPE_ERRORS=0
fi
```

### Step 3: Security Pattern Scan

```bash
echo "Scanning for security issues..."

SECURITY_ISSUES=0

for file in $FILES_CHANGED; do
  # Quick grep for common vulnerabilities

  # SQL Injection
  if grep -q "SELECT.*\${" "$file" 2>/dev/null; then
    echo "⚠️  SQL injection risk in $file"
    SECURITY_ISSUES=$((SECURITY_ISSUES + 1))
  fi

  # XSS via innerHTML
  if grep -q "\.innerHTML\s*=" "$file" 2>/dev/null; then
    echo "⚠️  XSS risk via innerHTML in $file"
    SECURITY_ISSUES=$((SECURITY_ISSUES + 1))
  fi

  # eval usage
  if grep -q "eval(" "$file" 2>/dev/null; then
    echo "⚠️  Code injection risk via eval in $file"
    SECURITY_ISSUES=$((SECURITY_ISSUES + 1))
  fi

  # exec usage
  if grep -q "exec(" "$file" 2>/dev/null; then
    echo "⚠️  Command injection risk in $file"
    SECURITY_ISSUES=$((SECURITY_ISSUES + 1))
  fi
done

if [ "$SECURITY_ISSUES" -eq 0 ]; then
  echo "✅ No obvious security issues"
fi
```

### Step 4: Missing Error Handling Check

```bash
echo "Checking for error handling..."

ERROR_HANDLING_ISSUES=0

for file in $FILES_CHANGED; do
  # Check for async functions without try/catch
  if grep -q "async function" "$file" 2>/dev/null; then
    # Count async functions
    ASYNC_COUNT=$(grep -c "async function" "$file" || echo "0")

    # Count try/catch blocks
    TRY_COUNT=$(grep -c "try {" "$file" || echo "0")

    if [ "$ASYNC_COUNT" -gt "$TRY_COUNT" ]; then
      echo "⚠️  Async functions may be missing error handling in $file"
      ERROR_HANDLING_ISSUES=$((ERROR_HANDLING_ISSUES + 1))
    fi
  fi

  # Check for unhandled promises (no .catch)
  if grep -q "\.then(" "$file" 2>/dev/null; then
    THEN_COUNT=$(grep -c "\.then(" "$file" || echo "0")
    CATCH_COUNT=$(grep -c "\.catch(" "$file" || echo "0")

    if [ "$THEN_COUNT" -gt "$CATCH_COUNT" ]; then
      echo "⚠️  Promise chains may be missing .catch() in $file"
      ERROR_HANDLING_ISSUES=$((ERROR_HANDLING_ISSUES + 1))
    fi
  fi
done

if [ "$ERROR_HANDLING_ISSUES" -eq 0 ]; then
  echo "✅ Error handling looks reasonable"
fi
```

### Step 5: ESLint Quick Check (if available)

```bash
echo "Running ESLint on changed files..."

if command -v npx &> /dev/null && [ -f ".eslintrc.js" -o -f ".eslintrc.json" -o -f "eslint.config.js" ]; then
  LINT_OUTPUT=$(npx eslint $FILES_CHANGED 2>&1 || true)

  LINT_ERRORS=$(echo "$LINT_OUTPUT" | grep -c "error" || echo "0")
  LINT_WARNINGS=$(echo "$LINT_OUTPUT" | grep -c "warning" || echo "0")

  if [ "$LINT_ERRORS" -gt 0 ]; then
    echo "⚠️  Found $LINT_ERRORS linting errors"
    echo "$LINT_OUTPUT" | head -10
  elif [ "$LINT_WARNINGS" -gt 0 ]; then
    echo "⚠️  Found $LINT_WARNINGS linting warnings (not blocking)"
  else
    echo "✅ No linting issues"
  fi
else
  echo "⏭️  ESLint not configured, skipping"
  LINT_ERRORS=0
fi
```

### Step 6: Generate Quick Report

Create lightweight summary (not a full report file):

```
=== Quick Bugcheck - Group {GROUP_NUMBER} ===

Files Checked: {count}
Checks Performed: TypeScript, Security, Error Handling, Linting

Results:
- Type Safety: {TYPE_ERRORS} errors
- Security Issues: {SECURITY_ISSUES} found
- Error Handling: {ERROR_HANDLING_ISSUES} potential gaps
- Linting: {LINT_ERRORS} errors, {LINT_WARNINGS} warnings

Status: {CLEAN | ISSUES_FOUND}

{If issues found}
⚠️  Issues detected - will be flagged to next implementer group
⚠️  Full bugfinder will run comprehensive analysis at pipeline end
```

### Step 7: Classify Severity and Output Markers

Classify issues by severity:
- **CRITICAL**: Security vulnerabilities (SQL injection, XSS, eval, command injection)
- **HIGH**: Type errors, missing error handling in async functions
- **WARNING**: Linting errors, minor issues

```bash
# Calculate critical issues (security only)
CRITICAL_ISSUES=$SECURITY_ISSUES

# Calculate high priority issues (type errors + error handling)
HIGH_PRIORITY=$((TYPE_ERRORS + ERROR_HANDLING_ISSUES))

echo "=== Severity Classification ==="
echo "CRITICAL (security): $CRITICAL_ISSUES"
echo "HIGH (type/error handling): $HIGH_PRIORITY"
echo "WARNING (lint): $LINT_ERRORS"
```

Output markers:

```
QUICK_BUGCHECK_GROUP: {GROUP_NUMBER}
FILES_CHECKED: {count}
CRITICAL_ISSUES: {count}
HIGH_PRIORITY: {count}
WARNING_ISSUES: {count}
TYPE_ERRORS: {count}
SECURITY_ISSUES: {count}
ERROR_HANDLING_ISSUES: {count}
LINT_ERRORS: {count}
STATUS: {CLEAN|ISSUES_FOUND}
```

## What This Agent Does NOT Do

**NOT in scope (leave for full bugfinder):**
- Deep static analysis
- Performance profiling
- Complex logic errors
- Integration testing
- Code complexity metrics
- Dependency vulnerability scanning
- License compliance checking

**Philosophy:**
This is a "smoke test" - just enough to catch obvious issues fast.
The full bugfinder at Phase 5 does comprehensive analysis.

## Example Output

```
=== Quick Bugcheck - Group 2 ===

Files Checked: 3
- src/api/users.ts
- src/models/user.ts
- src/utils/validation.ts

Results:
✅ Type Safety: 0 errors
⚠️  Security Issues: 1 found
   - SQL injection risk in src/api/users.ts:45
✅ Error Handling: looks reasonable
⚠️  Linting: 2 errors
   - src/api/users.ts:23 - missing semicolon
   - src/models/user.ts:12 - unused variable

Status: ISSUES_FOUND

⚠️  These issues will be highlighted to the next implementer group
⚠️  Full bugfinder will analyze everything at pipeline end
```

## Output Markers
```
QUICK_BUGCHECK_GROUP: 2
FILES_CHECKED: 3
CRITICAL_ISSUES: 1
HIGH_PRIORITY: 0
WARNING_ISSUES: 2
TYPE_ERRORS: 0
SECURITY_ISSUES: 1
ERROR_HANDLING_ISSUES: 0
LINT_ERRORS: 2
STATUS: ISSUES_FOUND
```

## Integration with Pipeline State

The orchestrator should:
1. Run quick-bugcheck after each group verification
2. Extract issue counts from markers
3. Store in `state['issues_found']` list
4. Pass accumulated issues to next implementer group

Example in orchestrator:
```
After Group 2 verified:
- run_agent: quick-bugcheck.md
- Extract: SECURITY_ISSUES: 1
- Add to state: issues_found.append("Group 2: SQL injection risk")
- Next implementer gets: "Previous groups found: SQL injection risk in users.ts"
```

## Report
```
GROUP: 2
FILES: 3
TYPE_ERRORS: 0
SECURITY: 1
ERROR_HANDLING: 0
LINT: 2
STATUS: ISSUES_FOUND

Next group should be aware of:
- SQL injection pattern detected
- Linting errors need fixing
```
