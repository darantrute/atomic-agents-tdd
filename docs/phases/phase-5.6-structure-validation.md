# Phase 5.6: Code Structure Validation

Use get_state() to get base_commit and retrieve changed files:

Call run_agent with code-structure-validator to enforce boundaries:
- agent_path: "agents/code-structure-validator.md"
- agent_input: "{changed_files}"

**What it validates:**
- Frontend cannot import backend (CRITICAL)
- Backend cannot import React (CRITICAL)
- Shared directory must be type-only (CRITICAL)
- Folder structure matches architecture map (WARNING)
- No circular dependencies (WARNING)

Python will extract markers:
- STRUCTURE_REPORT: {report_path}
- STRUCTURE_VALIDATION: {pass|fail}

Example:
```
Tool: run_agent
agent_path: "agents/code-structure-validator.md"
agent_input: "frontend/src/components/Dashboard.tsx backend/src/routes/users.ts shared/types/Officer.ts"
```

**If STRUCTURE_VALIDATION: fail:**
- BLOCK deployment
- Display STRUCTURE_REPORT path
- Instruct user to fix violations
- EXIT pipeline with error

**If STRUCTURE_VALIDATION: pass:**
- Proceed to Phase 5.7

Call report_progress:
- message: "Code structure validated - all boundaries respected"
