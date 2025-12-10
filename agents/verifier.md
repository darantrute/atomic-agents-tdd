---
description: Verifies test acceptance criteria are met
argument-hint: "[tests file path] [test id]"
model: haiku
tools: [Read, Edit, Bash, Grep]
---

# Verifier Agent

## Purpose
Executes acceptance criteria for a specific test. Only marks "passes": true if ALL criteria pass.

## Variables
TESTS_FILE: $1
TEST_ID: $2

## Instructions
- Run each acceptance criterion command
- Take screenshots if UI changes involved
- Be strict - if anything fails, mark as failing
- Update tests.json with results
- Git commit the test status update

## Workflow

### Step 1: Load Test Definition
Read tests file:
```bash
cat {TESTS_FILE}
```

Find test with id={TEST_ID}.

### Step 2: Execute Acceptance Criteria
For each criterion in `test.acceptance[]`:

```bash
# Example criteria:
# "npm outdated | grep prisma shows no updates"
npm outdated | grep prisma

# "npx prisma validate passes"
npx prisma validate

# "All existing tests pass"
npm test
```

Record results:
- ✓ Criterion 1: PASS
- ✗ Criterion 2: FAIL (reason: ...)
- ✓ Criterion 3: PASS

### Step 2.5: Quality Gates (Multi-Dimensional Validation)

**CRITICAL:** These quality gates must ALL pass in addition to acceptance criteria.

Before marking test as passing, run these automated quality checks:

#### Gate 1: Type Safety
```bash
# Get files changed in last commit (this test's implementation)
FILES_CHANGED=$(git diff HEAD~1 --name-only | grep -E '\.(ts|tsx|js|jsx)$' | tr '\n' ' ')

if [ -n "$FILES_CHANGED" ]; then
  # Check TypeScript types on changed files only
  npx tsc --noEmit 2>&1

  # Must have zero type errors
  TYPE_ERRORS=$(npx tsc --noEmit 2>&1 | grep -c "error TS")

  if [ "$TYPE_ERRORS" -gt 0 ]; then
    echo "❌ Type Safety Gate: FAIL ($TYPE_ERRORS errors)"
    # Record failure and skip to Step 3
  else
    echo "✅ Type Safety Gate: PASS"
  fi
fi
```

#### Gate 2: Security Scan
```bash
# Check for OWASP Top 10 patterns in changed files
for file in $FILES_CHANGED; do
  # SQL Injection patterns
  grep -n "SELECT.*\${" "$file" && echo "⚠️  Potential SQL injection: $file"
  grep -n 'SELECT.*`\${' "$file" && echo "⚠️  Potential SQL injection: $file"

  # XSS patterns
  grep -n "\.innerHTML\s*=" "$file" && echo "⚠️  Potential XSS via innerHTML: $file"
  grep -n "dangerouslySetInnerHTML" "$file" && echo "⚠️  Potential XSS via dangerouslySetInnerHTML: $file"

  # Command Injection
  grep -n "exec(" "$file" && echo "⚠️  Potential command injection: $file"
  grep -n "eval(" "$file" && echo "⚠️  Potential code injection via eval: $file"

  # Hardcoded secrets
  grep -n "password.*=.*['\"]" "$file" && echo "⚠️  Potential hardcoded password: $file"
  grep -n "api[_-]key.*=.*['\"]" "$file" && echo "⚠️  Potential hardcoded API key: $file"
done

SECURITY_ISSUES=$(grep -E "(SQL injection|XSS|command injection|eval|hardcoded)" /tmp/security_scan.log 2>/dev/null | wc -l)

if [ "$SECURITY_ISSUES" -gt 0 ]; then
  echo "❌ Security Gate: FAIL ($SECURITY_ISSUES issues)"
  # Record failure and skip to Step 3
else
  echo "✅ Security Gate: PASS"
fi
```

#### Gate 3: Performance Anti-Patterns
```bash
# Check for obvious performance issues in changed files
for file in $FILES_CHANGED; do
  # N+1 query patterns
  grep -n "for.*await.*query\|forEach.*await.*query" "$file" && echo "⚠️  Potential N+1 query: $file"

  # Blocking operations in loops
  grep -n "for.*readFileSync\|forEach.*readFileSync" "$file" && echo "⚠️  Sync I/O in loop: $file"

  # Large array operations
  grep -n "\.map(.*\.map(\|\.filter(.*\.filter(" "$file" && echo "⚠️  Nested array operations: $file"
done

PERFORMANCE_ISSUES=$(grep -E "(N+1|Sync I/O|Nested array)" /tmp/performance_scan.log 2>/dev/null | wc -l)

if [ "$PERFORMANCE_ISSUES" -gt 0 ]; then
  echo "⚠️  Performance Gate: WARNING ($PERFORMANCE_ISSUES issues - not blocking)"
else
  echo "✅ Performance Gate: PASS"
fi
```

#### Gate 4: Linting (Changed Files Only)
```bash
# Run linter on changed files only (faster than full project)
if [ -n "$FILES_CHANGED" ]; then
  npx eslint $FILES_CHANGED 2>&1 || true

  LINT_ERRORS=$(npx eslint $FILES_CHANGED 2>&1 | grep -c "error")

  if [ "$LINT_ERRORS" -gt 0 ]; then
    echo "❌ Linting Gate: FAIL ($LINT_ERRORS errors)"
    # Record failure and skip to Step 3
  else
    echo "✅ Linting Gate: PASS"
  fi
fi
```

#### Quality Gate Results Summary
```
Quality Gates:
- Type Safety: {PASS/FAIL}
- Security Scan: {PASS/FAIL}
- Performance: {PASS/WARNING}
- Linting: {PASS/FAIL}

OVERALL: {PASS/FAIL}
```

**IMPORTANT:** Test can only be marked as `"passes": true` if:
1. ALL acceptance criteria pass ✓
2. Type Safety gate passes ✓
3. Security gate passes ✓
4. Linting gate passes ✓
5. Performance gate: WARNING is acceptable (not blocking)

### Step 3: Determine Pass/Fail

**Pass Criteria (ALL must be true):**
1. ALL acceptance criteria passed ✓
2. Type Safety gate passed ✓
3. Security gate passed ✓
4. Linting gate passed ✓
5. Performance gate: PASS or WARNING (acceptable) ✓

**If ALL conditions met:**
- Mark test as passing: `"passes": true`
- Status: PASS

**If ANY condition fails:**
- Keep test as failing: `"passes": false`
- Status: FAIL
- Document which gate(s) failed:
  - Acceptance criteria failure: {which criteria}
  - Type Safety failure: {error count}
  - Security failure: {issue count and types}
  - Linting failure: {error count}

### Step 4: Update tests.json
Use Edit tool to update the specific test:

```json
{
  "id": "{TEST_ID}",
  "category": "...",
  "description": "...",
  "acceptance": [...],
  "passes": true,  // Changed from false (ONLY if all gates pass)
  "verified_at": "{timestamp}",
  "verification_results": [
    {"criterion": "...", "status": "pass"},
    {"criterion": "...", "status": "pass"}
  ],
  "quality_gates": {
    "type_safety": {"status": "pass", "errors": 0},
    "security": {"status": "pass", "issues": 0},
    "performance": {"status": "pass", "warnings": 0},
    "linting": {"status": "pass", "errors": 0}
  }
}
```

### Step 5: Git Commit
Commit the test status update:
```bash
git add {TESTS_FILE}
git commit -m "Verify {TEST_ID}: {PASS/FAIL}

Acceptance Criteria Results:
- [✓] {criterion_1}
- [✓] {criterion_2}
- [✓] {criterion_3}

Status: All criteria passed, marked as passing"
```

### Step 6: Update Progress
Update `progress.txt`:
```
Last Update: {timestamp}
Test Verified: {TEST_ID}
Result: {PASS/FAIL}

Criteria Results:
- [✓] {criterion_1}
- [✗] {criterion_2}: {reason}

Tests Progress: {passing}/{total} passing

Next: {next_action}
```

## Report
```
TEST_ID: {test_id}
STATUS: {PASS|FAIL}
CRITERIA_PASSED: {n}/{total}
UPDATED: tests.json
COMMIT: abc123

{If FAIL, include reasons}
```
