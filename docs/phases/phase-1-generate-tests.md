# Phase 1: Generate Tests

Call run_agent with test-generator:
- Use get_state() to retrieve architecture_map path (from Phase 0.5)
- Use get_state() to retrieve style_system path (from Phase 0.6)
- Pass task description, architecture map, AND style system paths as agent_input
- Format: "{task}\n\nARCHITECTURE_MAP: {architecture_map_path}\n\nSTYLE_SYSTEM: {style_system_path}"
- Python will automatically extract TESTS_FILE marker
- Use get_state() to retrieve tests_file path

Example:
```
Tool: run_agent
agent_path: "agents/test-generator.md"
agent_input: "Create analytics platform\n\nARCHITECTURE_MAP: specs/chore-051225-1535-architecture.json\n\nSTYLE_SYSTEM: specs/style-051225-1536.md"
```

Call report_progress to update user:
- message: "Generated comprehensive test acceptance criteria from architecture map and style system"
