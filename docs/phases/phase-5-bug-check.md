# Phase 5: Bug Check

Use get_state() to retrieve base_commit (from Phase 0)

Call run_agent with bugfinder to analyze only pipeline changes:
- agent_path: "agents/bugfinder.md"
- agent_input: "since-branch-start {base_commit}"

This analyzes ONLY the code changes made during this pipeline run (from base commit to current HEAD), not the entire codebase.

**Why this matters:**
- Focuses on NEW issues introduced by pipeline
- Avoids false positives from pre-existing code
- Makes bug reports actionable and relevant
- Faster analysis than scanning entire codebase

**Fallback:** If base_commit is not available in state, use "all" scope instead.

Example:
```
Tool: get_state
Returns: {"base_commit": "abc1234567890abcdef1234567890abcdef12", ...}

Tool: run_agent
agent_path: "agents/bugfinder.md"
agent_input: "since-branch-start abc1234567890abcdef1234567890abcdef12"
```

Python will extract BUGFINDER_REPORT marker automatically.
