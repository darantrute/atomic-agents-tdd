# Phase 0.7: Codebase Context Discovery

Call run_agent with codebase-context-builder to discover existing patterns:
- agent_path: "agents/codebase-context-builder.md"
- agent_input: "." (project root)
- Python will automatically extract CODEBASE_CONTEXT marker
- Use get_state() to retrieve codebase_context path

**One-time execution:**
The agent checks if context file already exists:
- If exists and < 7 days old: Reuses existing context (saves $1)
- If exists and > 7 days old: Regenerates (patterns may have changed)
- If not exists: Performs full analysis

This creates: `specs/codebase-context-DDMMYY-HHMM.json`

Call report_progress:
- message: "Discovered existing codebase patterns for consistency"

Example:
```
Tool: run_agent
agent_path: "agents/codebase-context-builder.md"
agent_input: "."
```

**Why this matters:**
- Implementer will use this context to generate code matching existing patterns
- Ensures consistency (if codebase uses Zustand, new code uses Zustand)
- Prevents style mismatches (if codebase uses Tailwind, new code uses Tailwind)
- One-time cost ($1), reused for all features
