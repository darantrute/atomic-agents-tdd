---
description: Complete TDD workflow for chore tasks (test-first approach)
argument-hint: [task description]
model: sonnet
tools: [Task, Read]
---

# Chore TDD Pipeline

## Purpose
Orchestrates the complete test-driven chore workflow:
1. Generate test acceptance criteria
2. Create implementation plan
3. Implement + verify each test
4. Final bug check

## Variables
TASK: $1

## Workflow

### Phase 1: Generate Tests (Test-First!)
Run `agents/test-generator.md` with {TASK}
- Creates: `specs/chore-DDMMYY-HHMM-tests.json`
- Extract: `TESTS_FILE: (.+)` → store as `tests_path`
- Expected: 5-15 tests with acceptance criteria

### Phase 2: Create Implementation Plan
Run `agents/chore-planner.md` with {tests_path}
- Reads: tests.json
- Creates: `specs/chore-DDMMYY-HHMM-plan.md`
- Extract: `PLAN_FILE: (.+)` → store as `plan_path`
- Expected: Detailed steps for each test

### Phase 3: Implementation Loop
For each test in tests.json with "passes": false:

**3.1 Implement Test**
- Run `agents/implementer.md` with {plan_path} and {test_id}
- Expected: Code changes committed
- On failure: abort pipeline

**3.2 Verify Test**
- Run `agents/verifier.md` with {tests_path} and {test_id}
- Expected: Test marked as passing or failing
- On failure: retry implementation once

**3.3 Check Progress**
- Read {tests_path}
- Count: passing vs total tests
- If all passing: proceed to Phase 4
- If failures remain: continue loop

### Phase 4: Final Validation
Run `agents/bugfinder.md` with "last-commit"
- Analyzes: All code changes
- Creates: Bug report
- Extract: `CRITICAL_ISSUES: (\d+)`

If critical issues found:
- Stop pipeline
- Report issues to user
- Require manual intervention

If no critical issues:
- Pipeline complete
- Report success metrics

## Error Handling

**Test generation fails:**
- Abort: Cannot proceed without tests

**Planning fails:**
- Retry with more context
- If still fails: abort

**Implementation fails:**
- Mark test as failing
- Continue to next test
- Report at end

**Verification fails:**
- Keep test marked as failing
- Document reason
- Continue to next test

**Bug finder finds critical issues:**
- Abort pipeline
- Require fix before continuing

## State Files Created

```
specs/
├── chore-DDMMYY-HHMM-tests.json      # Test definitions
├── chore-DDMMYY-HHMM-plan.md         # Implementation plan
└── bugfinder-DDMMYY-HHMM-report.md   # Final validation

progress.txt                           # Session notes
```

## Git Commits

- After test generation: "Generate tests for: {TASK}"
- After planning: "Create implementation plan"
- After each test: "Implement test-{id}: {description}"
- After verification: "Verify test-{id}: {PASS/FAIL}"
- After bug check: "Final validation: {status}"

## Success Criteria

✅ All tests generated
✅ Implementation plan created
✅ All tests implemented
✅ All tests verified and passing
✅ No critical bugs found
✅ All changes committed

## Report Format

```
PIPELINE: Chore TDD
TASK: {task_description}
DURATION: {start} → {end}

Phase 1: Tests Generated
- File: {tests_path}
- Count: {n} tests

Phase 2: Plan Created
- File: {plan_path}
- Tests covered: {n}/{total}

Phase 3: Implementation
- Implemented: {n} tests
- Verified: {passing}/{n} passing
- Failures: {list_of_failed_tests}

Phase 4: Bug Check
- Critical: {count}
- High: {count}
- Status: {PASS/FAIL}

FINAL STATUS: {SUCCESS | PARTIAL | FAILED}
TESTS PASSING: {passing}/{total}
COMMITS: {count}

{If failures, list them with reasons}
```
