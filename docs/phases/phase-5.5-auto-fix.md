# Phase 5.5: Auto-Fix Bugs

Use get_state() to check bugfinder results:
- CRITICAL_ISSUES: {count}
- HIGH_PRIORITY: {count}

**If CRITICAL_ISSUES > 0 OR HIGH_PRIORITY > 0:**

Call run_agent with bugfixer to auto-fix issues:
- agent_path: "agents/bugfixer.md"
- agent_input: "{bugfinder_report_path}"

Bugfixer will:
1. Read bugfinder report
2. Auto-fix deterministic issues (null checks, missing error handling, etc.)
3. Git commit each fix separately
4. Skip ambiguous issues (leave for manual review)

Python will extract markers:
- ISSUES_FIXED: {count}
- ISSUES_SKIPPED: {count}
- ALL_CRITICAL_FIXED: {yes|no}

**Re-validate after fixes:**
If ISSUES_FIXED > 0, re-run bugfinder to verify fixes:
- Call run_agent: "agents/bugfinder.md"
- agent_input: "since-branch-start {base_commit}"
- This validates fixes didn't introduce new issues

**Loop control:**
Maximum 2 bugfixer iterations to prevent infinite loops:
- Iteration 1: Fix issues from initial bugfinder
- Iteration 2: Fix issues from validation run (if any)
- After iteration 2: Stop, flag remaining issues for manual review

Example workflow:
```
Tool: get_state
Returns: {
  "bugfinder_report": "specs/bugfinder-051225-1430-report.md",
  "critical_issues": 2,
  "high_priority": 3
}

If critical_issues > 0 or high_priority > 0:

  # Iteration 1: Fix issues
  Tool: run_agent
  agent_path: "agents/bugfixer.md"
  agent_input: "specs/bugfinder-051225-1430-report.md"

  # Validate fixes
  Tool: run_agent
  agent_path: "agents/bugfinder.md"
  agent_input: "since-branch-start abc123..."

  # If new issues found and iteration < 2:
  Tool: run_agent
  agent_path: "agents/bugfixer.md"
  agent_input: "{new_bugfinder_report}"

  # Final validation
  Tool: run_agent
  agent_path: "agents/bugfinder.md"
  agent_input: "since-branch-start abc123..."
```

Call report_progress:
- message: "Auto-fixed {count} issues, {count} require manual review"

**If NO HIGH/CRITICAL issues:**
Skip Phase 5.5 entirely, proceed to Phase 5.6.
