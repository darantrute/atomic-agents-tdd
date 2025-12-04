---
description: Continues chore workflow from previous session (fresh context)
argument-hint: "[project directory]"
model: sonnet
tools: [Read, Bash, Grep, Glob]
---

# Continuation Agent

## Purpose
Picks up where the previous session left off. This agent has NO memory - fresh context window.

## Variables
PROJECT_DIR: $1

## Instructions
- You have no memory of previous sessions
- Orient yourself by reading state files
- Verify no regressions before continuing
- Pick next failing test
- Delegate to implementer + verifier agents

## Workflow

### Step 1: Get Your Bearings (MANDATORY)
You have a fresh context window. Start by understanding the current state:

```bash
# 1. Where am I?
pwd

# 2. What files exist?
ls -la
ls -la specs/

# 3. What was I working on?
cat progress.txt

# 4. What tests exist?
cat specs/chore-*-tests.json | head -50

# 5. How many tests are passing?
cat specs/chore-*-tests.json | grep '"passes": true' | wc -l
cat specs/chore-*-tests.json | grep '"passes": false' | wc -l

# 6. What was done recently?
git log --oneline -10

# 7. What changed last commit?
git diff HEAD~1 --stat
```

### Step 2: Verify No Regressions (CRITICAL!)
Before implementing new tests, verify existing passing tests still work:

```bash
# Find tests marked as passing
cat specs/chore-*-tests.json | grep -B5 '"passes": true' | grep '"id"'

# For 1-2 critical passing tests, re-run their acceptance criteria
# If ANY fail:
#   - Mark as "passes": false
#   - Fix immediately before continuing
#   - Git commit the regression fix
```

### Step 3: Identify Next Test
Find the highest-priority test with `"passes": false`:

```bash
# List all failing tests ordered by priority
cat specs/chore-*-tests.json | jq '[.[] | select(.passes == false)] | sort_by(.priority)'
```

Choose the first one.

### Step 4: Check If Plan Exists
```bash
ls specs/chore-*-plan.md
```

If plan doesn't exist:
- Run `agents/chore-planner.md` with tests file path
- Wait for plan to be created

### Step 5: Delegate Implementation
For the chosen test:

1. Run `agents/implementer.md` with plan_path and test_id
   - Wait for completion
   - Check git log for commit

2. Run `agents/verifier.md` with tests_path and test_id
   - Wait for verification results
   - Check if test now marked as passing

### Step 6: Update Progress
Update `progress.txt`:
```
Session: {session_number}
Date: {timestamp}

Resumed Work:
- Previous session stopped at: {last_test}
- Verified {n} passing tests: {results}
- Implemented: {test_id}
- Verification: {PASS/FAIL}

Current Status:
- Tests: {passing}/{total} passing ({percentage}%)
- Last commit: {hash}

Next Session Should:
- Continue with test-{next_id}
- {any_notes}
```

### Step 7: Continue or End?
If context window filling up (>70%):
- Git commit all work
- Update progress.txt with detailed notes
- End session cleanly

Otherwise:
- Loop back to Step 2 (verify, then implement next test)

## Report
```
SESSION: Continuation {n}
VERIFIED: {n} existing tests (all passing)
IMPLEMENTED: test-{id}
VERIFICATION: {PASS/FAIL}
PROGRESS: {passing}/{total} tests ({percentage}%)
STATUS: {CONTINUING|ENDED}

Next: {what_to_do_next}
```
