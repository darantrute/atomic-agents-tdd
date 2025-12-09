# Phase 0.6: Style Integration

Call run_agent with style-integrator:
- Use get_state() to retrieve architecture_map path (from Phase 0.5)
- Pass architecture_map path as agent_input
- Python will automatically extract STYLE_SYSTEM and TAILWIND_CONFIG markers
- Use get_state() to retrieve style_system and tailwind_config paths

Call report_progress:
- message: "Applied design system based on project architecture"

Example:
```
Tool: run_agent
agent_path: "agents/style-integrator.md"
agent_input: "specs/chore-051225-1535-architecture.json"
```

This creates:
- `specs/style-DDMMYY-HHMM.md`
- `specs/tailwind-config-DDMMYY-HHMM.js`
