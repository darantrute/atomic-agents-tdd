# Phase 8: Push and Create Draft PR (REQUIRED)

**IMPORTANT:** This phase is REQUIRED for full automation. Only proceed if all tests passed and no critical bugs remain.

Use get_state() to get:
- branch (feature branch name)
- tests_file
- bugfinder_report (if available)

Push branch to remote:
```bash
git push -u origin {branch}
```

Create draft PR using GitHub CLI:
```bash
gh pr create --draft \
  --title "feat: {task_summary}" \
  --body "$(cat <<'EOF'
## Summary
Auto-generated implementation via TDD pipeline.

## Tests
- {test_count} tests implemented and passing ✓
- All quality gates passed ✓

## Changes
{brief_summary_of_changes}

## Review Checklist
- [ ] Code review completed
- [ ] Integration tested locally
- [ ] Ready to merge

---
🤖 Generated with [Claude Code](https://claude.com/claude-code)

**Status:** Draft - requires human review before merge
EOF
)"
```

**Why draft PR?**
- Visible to team immediately
- Cannot be merged accidentally
- CI/CD runs automatically
- You mark as "Ready for review" after local testing

**Execution Steps:**

1. Check prerequisites:
```bash
# Verify gh CLI is available
gh auth status
# If fails: ERROR and provide manual instructions
```

2. Push branch:
```bash
git push -u origin {branch}
# If fails: ERROR - cannot proceed without push
```

3. Create draft PR:
```bash
gh pr create --draft --title "feat: {task_summary}" --body "..."
# Capture PR URL from output
```

4. Report completion:
```
Tool: report_progress
message: "✅ PIPELINE COMPLETE - Draft PR created: {pr_url}"
```

**If Phase 8 Fails:**
- Report error with manual instructions
- Pipeline is still considered successful (code is committed locally)
- User must push and create PR manually

**Fallback instructions:**
```
Phase 8 failed - manual steps required:
  cd {worktree_path}
  git push -u origin {branch}
  gh pr create --draft --title "feat: {task}" --web
```

Call report_progress with final status:
- Success: "Draft PR created: {pr_url} - Review on GitHub and mark ready when satisfied"
- Failure: "Push/PR creation failed - see manual instructions above"

The pipeline completes when all phases are done. No special "DONE" signal needed - just stop calling tools.
