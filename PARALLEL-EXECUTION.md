# Running Multiple Pipelines in Parallel

The TDD pipeline supports safe parallel execution using **git worktrees**.

## Quick Start

### Option 1: Use the Helper Script (Recommended)

```bash
# Terminal 1
./run-isolated.sh "Add user authentication"

# Terminal 2 (at the same time!)
./run-isolated.sh "Add payment processing"

# Terminal 3 (why not?)
./run-isolated.sh "Add email notifications"
```

Each pipeline runs in complete isolation with **zero conflicts**.

---

## How It Works

The `run-isolated.sh` script:

1. Creates a unique git worktree in `/tmp/tdd-worktrees/`
2. Runs the pipeline in that isolated directory
3. Creates a separate feature branch
4. Leaves the worktree available for you to review/push

**Example:**
```bash
./run-isolated.sh "Add authentication"

# Output:
Creating isolated worktree: /tmp/tdd-worktrees/tdd-20251207-143045-12345
Running pipeline in isolated worktree...
Task: Add authentication

[... pipeline runs ...]

✅ Pipeline completed successfully
Branch: feature/add-authentication

Next steps:
  cd /tmp/tdd-worktrees/tdd-20251207-143045-12345
  git push origin feature/add-authentication

To cleanup this worktree later:
  cd /home/dazman/atomic-agents-tdd
  git worktree remove /tmp/tdd-worktrees/tdd-20251207-143045-12345
```

---

## Manual Worktree Usage

If you prefer manual control:

```bash
# Create worktree
git worktree add /tmp/my-auth-worktree main

# Change to worktree
cd /tmp/my-auth-worktree

# Run pipeline
python /home/dazman/atomic-agents-tdd/run.py "Add authentication"

# Review, commit, push
git push origin feature/add-authentication

# Cleanup (from main repo)
cd /home/dazman/atomic-agents-tdd
git worktree remove /tmp/my-auth-worktree
```

---

## Concurrent Execution Protection

The pipeline automatically detects if another instance is running in the **same directory**:

```bash
# Terminal 1
python run.py "Feature A"

# Terminal 2 (same directory)
python run.py "Feature B"

# Output:
======================================================================
  ⚠️  ANOTHER PIPELINE IS RUNNING IN THIS DIRECTORY
======================================================================

To run multiple pipelines in parallel, use git worktrees:
  ./run-isolated.sh "Your feature description"

Or create a worktree manually:
  git worktree add /tmp/my-worktree main
  cd /tmp/my-worktree
  python /home/dazman/atomic-agents-tdd/run.py "Your feature"

======================================================================
```

This **prevents data corruption** and **git conflicts**.

---

## Why Worktrees?

Running two pipelines in the same directory causes:

- ❌ **File conflicts** - Both modify the same files simultaneously
- ❌ **Git corruption** - Concurrent commits to working directory
- ❌ **Package.json corruption** - npm install race conditions
- ❌ **Test failures** - Tests run while files are half-written
- ❌ **Port conflicts** - Both try to use port 3000

**Git worktrees solve ALL of these:**

- ✅ **Complete isolation** - Separate working directories
- ✅ **Shared .git database** - Efficient storage (no duplication)
- ✅ **Native git feature** - Well-tested, stable
- ✅ **Easy cleanup** - `git worktree remove`
- ✅ **Branch protection** - Can't checkout same branch twice
- ✅ **Independent installs** - Separate node_modules/
- ✅ **No conflicts** - Ever

---

## Managing Worktrees

### List all worktrees
```bash
git worktree list
```

### Remove a worktree
```bash
git worktree remove /tmp/tdd-worktrees/tdd-20251207-143045-12345
```

### Remove all temp worktrees
```bash
git worktree list | grep "/tmp/tdd-worktrees" | awk '{print $1}' | xargs -I {} git worktree remove {}
```

### Prune stale worktrees
```bash
git worktree prune
```

---

## Environment Variables

### `WORKTREE_BASE`
Change where worktrees are created:

```bash
WORKTREE_BASE=/path/to/worktrees ./run-isolated.sh "Add feature"
```

Default: `/tmp/tdd-worktrees`

---

---

## Pull Request Workflow

### What Happens After Pipeline Completes

The pipeline **creates a draft PR automatically** (Phase 8):

```bash
./run-isolated.sh "Add authentication"

# Pipeline runs...
# At the end:
✅ All tests passing
✅ Code pushed to origin
✅ Draft PR created: https://github.com/user/repo/pull/123

Next steps:
1. Review the PR on GitHub
2. Test locally in the worktree
3. Mark as "Ready for review" when satisfied
```

**Draft PR means:**
- ✅ Team can see it immediately
- ✅ CI/CD runs automatically
- ❌ Cannot be merged accidentally (protected)
- ✅ You control when it's ready

---

### Handling Overlapping Changes

**Scenario:** Two PRs modify the same file

```bash
# Terminal 1
./run-isolated.sh "Add authentication"
# → PR #1: Modifies src/models/user.ts (adds authToken)

# Terminal 2 (parallel)
./run-isolated.sh "Add payments"
# → PR #2: Modifies src/models/user.ts (adds paymentId)
```

**What happens:**

1. **Both PRs created as drafts** ✓
2. **Both reviewed independently** ✓
3. **PR #1 merged first** ✓
4. **PR #2 now has conflicts** ⚠️

**GitHub shows:**
```
⚠️  This branch has conflicts that must be resolved
```

**How to fix:**

```bash
# Update PR #2 with latest main
cd /tmp/tdd-worktrees/tdd-payments-xxx
git fetch origin
git merge origin/main

# Git shows conflict:
CONFLICT in src/models/user.ts

# Fix manually:
# Edit src/models/user.ts to include BOTH changes
git add src/models/user.ts
git commit -m "fix: Resolve merge conflict with authentication PR"
git push

# PR #2 now updated and ready to merge ✓
```

**Key point:** Git **never silently loses code**. It always detects conflicts and makes you resolve them manually.

---

### Best Practice Merge Order

**Strategy 1: Sequential Merge (Safest)**
```
1. PR #1: Review → Approve → Merge ✓
2. PR #2: Update with main → Resolve conflicts → Merge ✓
3. PR #3: Update with main → Resolve conflicts → Merge ✓
```

**Strategy 2: Parallel Review, Sequential Merge**
```
1. Create all PRs in parallel (draft mode) ✓
2. Team reviews all simultaneously ✓
3. Merge one at a time, updating others as needed ✓
```

**Strategy 3: Feature Flags (Advanced)**
```
1. All PRs include feature flags (disabled by default) ✓
2. Merge all PRs to main (features disabled) ✓
3. Enable features one by one in production ✓
```

---

### When Conflicts Are Expected

If you **know** multiple features will modify the same files:

**Option 1: Run sequentially**
```bash
./run-isolated.sh "Add authentication"
# Wait for PR to merge
./run-isolated.sh "Add payments"  # Now starts from updated main
```

**Option 2: Create dependency**
```bash
./run-isolated.sh "Add authentication"
# Let it complete and merge

# Then base payments on auth branch:
git worktree add /tmp/payments feature/add-authentication
cd /tmp/payments
python /path/to/run.py "Add payments"
# This branch is based on auth, not main
```

---

## FAQ

**Q: Can I run 10 pipelines at once?**
A: Yes! Each gets its own worktree. Limited only by system resources.

**Q: What if two PRs conflict?**
A: Git detects this! Merge the first PR, then update the second with `git merge main`, resolve conflicts, and merge.

**Q: Can conflicts cause data loss?**
A: No! Git always shows conflicts and requires manual resolution. It never silently loses code.

**Q: Do worktrees duplicate the entire repo?**
A: No! They share the `.git` database. Only working files are duplicated.

**Q: What happens to the worktree after pipeline completes?**
A: It stays available for you to review, test, and push. Clean up manually when done.

**Q: Can I use this in CI/CD?**
A: Absolutely! Each CI job can use its own worktree for complete isolation.

**Q: What if I forget to clean up worktrees?**
A: They're in `/tmp`, so they'll be cleared on system reboot. Or use `git worktree prune`.

**Q: Does this work on Windows?**
A: Yes, but the lock file protection uses `fcntl` (Unix-only). Windows users should use worktrees for parallel execution.

---

## Performance

Typical overhead:
- **Worktree creation:** ~1 second
- **Disk space per worktree:** ~100-500MB (depends on node_modules)
- **Cleanup:** ~0.5 seconds

**Worth it for:**
- Zero conflicts ✅
- Complete safety ✅
- True parallelism ✅

---

## Real-World Example

```bash
# Product owner creates 3 tickets
# You want to implement all in parallel

# Terminal 1
./run-isolated.sh "Add JWT authentication with refresh tokens"

# Terminal 2
./run-isolated.sh "Add Stripe payment processing"

# Terminal 3
./run-isolated.sh "Add email notification system with SendGrid"

# All three pipelines run simultaneously
# 30 minutes later, you have 3 feature branches ready to merge
# Zero conflicts, zero manual intervention
```

---

## Troubleshooting

### "Permission denied" on run-isolated.sh
```bash
chmod +x run-isolated.sh
```

### "git worktree add failed"
Check if you have uncommitted changes in main repo:
```bash
git status
```

Commit or stash them first.

### Worktree still exists but pipeline failed
Navigate to the worktree, investigate, then remove:
```bash
cd /tmp/tdd-worktrees/tdd-xxx
# Debug, fix, re-run
cd /home/dazman/atomic-agents-tdd
git worktree remove /tmp/tdd-worktrees/tdd-xxx
```

---

## Summary

**To run multiple pipelines in parallel:**

1. Use `./run-isolated.sh "Feature description"` in separate terminals
2. Each gets its own isolated workspace
3. Zero conflicts guaranteed
4. Review and push when done
5. Clean up worktrees as needed

**Simple. Safe. Powerful.**
