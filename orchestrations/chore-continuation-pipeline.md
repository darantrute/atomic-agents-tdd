---
description: Resume chore workflow from previous session (fresh context)
argument-hint: [project directory]
model: sonnet
tools: [Task, Read, Bash]
---

# Chore Continuation Pipeline

## Purpose
Resumes work from a previous session. Assumes:
- tests.json already exists
- plan.md already exists
- Some tests may be passing
- Fresh context window (no memory)

## Variables
PROJECT_DIR: $1

## Workflow

### Phase 1: Get Bearings (Fresh Context)
**You have NO memory of previous sessions.**

Run these commands to orient yourself:
```bash
cd {PROJECT_DIR}
pwd
ls -la
ls -la specs/
cat progress.txt
git log --oneline -10
```

Expected state files:
- `specs/chore-*-tests.json` (test definitions)
- `specs/chore-*-plan.md` (implementation plan)
- `progress.txt` (session notes)
- Git history with commits

### Phase 2: Verify No Regressions (CRITICAL!)
Before continuing with new tests, verify existing passing tests still work.

Run `agents/continuation.md` with {PROJECT_DIR}
- This agent:
  - Reads tests.json
  - Finds tests marked "passes": true
  - Re-runs their acceptance criteria
  - If any fail: marks as failing, fixes immediately

Expected: All existing passing tests still pass

### Phase 3: Identify Next Test
Read `specs/chore-*-tests.json`:
- Count: passing vs failing tests
- Find: highest priority test with "passes": false
- Store: test_id

If all tests passing:
- Skip to Phase 5 (final validation)

### Phase 4: Implement + Verify Loop
For the identified test:

**4.1 Implement**
- Run `agents/implementer.md` with plan_path and test_id
- Expected: Code changes committed

**4.2 Verify**
- Run `agents/verifier.md` with tests_path and test_id
- Expected: Test marked as passing or failing

**4.3 Check Context Window**
If context usage > 70%:
- Update progress.txt with current state
- Git commit all work
- End session
- Report: "Session ended cleanly, ready to resume"
- Exit pipeline

If context usage < 70%:
- Continue to Phase 2 (verify regressions, implement next test)

### Phase 5: Final Validation
Run `agents/bugfinder.md` with "all"
- Analyzes: Entire codebase
- Creates: Bug report
- Expected: No critical issues

### Phase 6: Update Progress
Update `progress.txt`:
```
Session: Continuation {n}
Date: {timestamp}

Resumed From:
- Previous: {n} tests passing
- Started: {test_id}

Work Completed:
- Implemented: {list_of_test_ids}
- Verified: {n} tests
- All passing: {yes/no}

Final Status:
- Tests: {passing}/{total} passing ({percentage}%)
- Commits: {count}
- Critical issues: {count}

Next Session:
- {Continue with test-{id} | All tests complete}
```

## State Management

**Read at start:**
- `progress.txt` - What was done last
- `specs/chore-*-tests.json` - Test status
- `specs/chore-*-plan.md` - Implementation guide
- `git log` - Recent changes

**Update during:**
- `specs/chore-*-tests.json` - Mark tests as passing
- `progress.txt` - Session notes
- Git commits - Each implementation

**Write at end:**
- `progress.txt` - Final session summary
- `specs/bugfinder-*-report.md` - Validation results

## Session Boundaries

**Start session:**
1. Get bearings (fresh context)
2. Verify regressions
3. Continue work

**End session:**
1. Commit all work
2. Update progress.txt
3. Leave in clean state

**Resume next session:**
1. Run this pipeline again
2. Fresh context, reads state files
3. Continues where left off

## Success Criteria

✅ Previous passing tests still pass
✅ At least one new test implemented + verified
✅ Progress documented
✅ All work committed
✅ Left in clean state (ready to resume)

## Report Format

```
PIPELINE: Chore Continuation
SESSION: {n}
PROJECT: {PROJECT_DIR}

Phase 1: Oriented
- Found: {n} tests ({passing} passing)
- Last work: {test_id}

Phase 2: Regression Check
- Verified: {n} passing tests
- Status: {all_pass | some_failed}

Phase 3-4: Implementation
- Implemented: {list_of_test_ids}
- Verified: {results}

Phase 5: Final Validation
- Critical issues: {count}
- Status: {PASS/FAIL}

PROGRESS: {passing}/{total} tests passing ({percentage}%)
COMMITS: {count}
CONTEXT_USAGE: {percentage}%

STATUS: {CONTINUING | ENDED_CLEANLY | ALL_COMPLETE}
NEXT: {what_to_do_next}
```
