# Phase 0.5: Requirements Analysis

Call run_agent with requirements-analyzer:
- Pass the task description as agent_input
- Python will automatically extract ARCHITECTURE_MAP marker
- Use get_state() to retrieve architecture_map path

Call report_progress:
- message: "Analyzed requirements and mapped technical architecture"

Example:
```
Tool: run_agent
agent_path: "agents/requirements-analyzer.md"
agent_input: "Create analytics platform..."
```

This creates: `specs/chore-DDMMYY-HHMM-architecture.json`
