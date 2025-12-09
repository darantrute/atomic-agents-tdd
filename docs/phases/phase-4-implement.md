# Phase 4: Implement Tests

**CRITICAL: You must construct FULLY FORMED inputs!**

Use get_state() to retrieve:
- tests_file (from Phase 1)
- plan_file (from Phase 2)

For each execution group from Phase 3:

**If group is PARALLEL** (multiple test IDs):
Call run_agents_parallel:
- agent_path: "agents/implementer.md"
- inputs: ["{plan_file} test-001", "{plan_file} test-002", "{plan_file} test-003"]

Example:
- inputs: ["specs/chore-041225-1031-plan.md test-001", "specs/chore-041225-1031-plan.md test-002"]

**If group is SEQUENTIAL** (single test ID):
Call run_agent for each test:
- agent_path: "agents/implementer.md"
- agent_input: "{plan_file} test-001"

After each group, verify with run_agents_parallel:
- agent_path: "agents/verifier.md"
- inputs: ["{tests_file} test-001", "{tests_file} test-002"]

**NEW: Quick Bug Check After Each Group**
After verification completes, run lightweight bug check:
- Call run_agent: "agents/quick-bugcheck.md"
- agent_input: "{group_number}"

This runs fast (~10 seconds) quality checks:
- TypeScript errors in new code
- ESLint on changed files
- Obvious security patterns (eval, innerHTML, SQL injection, XSS)
- Missing error handling

Extract markers (automatic):
- CRITICAL_ISSUES: {count} (security vulnerabilities)
- HIGH_PRIORITY: {count} (type errors, missing error handling)
- WARNING_ISSUES: {count} (linting, minor issues)
- SECURITY_ISSUES: {count}
- TYPE_ERRORS: {count}
- ERROR_HANDLING_ISSUES: {count}

**CRITICAL: Immediate Fix for Critical Issues**

If CRITICAL_ISSUES > 0:
1. STOP pipeline immediately
2. Call run_agent with bugfixer in immediate mode:
   - agent_path: "agents/bugfixer.md"
   - agent_input: "immediate group-{group_number}"
3. Bugfixer will:
   - Fix security vulnerabilities immediately
   - Git commit fixes with message: "fix(security): Auto-fix critical issues in group {N}"
   - Max 1 iteration (no retry loop in immediate mode)
4. Re-run verifier for this group:
   - Call run_agent: "agents/verifier.md"
   - agent_input: "{tests_file} {test_ids_for_this_group}"
   - Ensure fixes didn't break tests
5. If verifier passes, continue to next group
6. If verifier fails after fixes, BLOCK pipeline with error message

Example workflow when CRITICAL issues found:
```
# Group 1 completes, quick-bugcheck runs
CRITICAL_ISSUES: 2 (SQL injection in users.ts, XSS in dashboard.tsx)

# Immediate bugfixer intervention
Tool: run_agent
agent_path: "agents/bugfixer.md"
agent_input: "immediate group-1"

# Bugfixer outputs: ISSUES_FIXED: 2

# Re-verify group 1
Tool: run_agent
agent_path: "agents/verifier.md"
agent_input: "specs/tests.json test-001 test-002"

# If pass, continue to Group 2
# If fail, BLOCK with: "Critical bug fixes broke tests - manual intervention required"
```

If HIGH_PRIORITY > 0 OR WARNING_ISSUES > 0 (but CRITICAL_ISSUES == 0):
- Add to state['issues_found'] for next group
- Next implementer will be warned about patterns to avoid
- Continue pipeline (don't block)

Call report_progress after each group:
- message: "Group 1 complete (2/10 tests implemented and verified)"
- If CRITICAL issues fixed: "⚠️  Fixed 2 critical security issues immediately"
- If HIGH/WARNING issues: "⚠️  Found 3 non-critical issues (will fix in Phase 5.5)"
