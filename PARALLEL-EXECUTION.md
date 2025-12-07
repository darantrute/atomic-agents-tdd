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

## FAQ

**Q: Can I run 10 pipelines at once?**
A: Yes! Each gets its own worktree. Limited only by system resources.

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
