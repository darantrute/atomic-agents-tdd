# Phase 4.5: Document Implementation

**CRITICAL: Run documentation-generator AFTER implementer, BEFORE verifier**

For each test that was just implemented:

Call run_agent with documentation-generator:
- agent_path: "agents/documentation-generator.md"
- agent_input: "{test_id}"
- Python will automatically extract DOCUMENTATION_ADDED marker

Example:
```
# Implementation flow for each test:
1. Implementer runs (writes code)
2. Documentation Generator runs (adds JSDoc, DECISIONS.md, README) ← NEW!
3. Verifier runs (validates acceptance criteria + quality gates)

Tool: run_agent
agent_path: "agents/implementer.md"
agent_input: "specs/plan.md test-001"

Tool: run_agent
agent_path: "agents/documentation-generator.md"
agent_input: "test-001"

Tool: run_agent
agent_path: "agents/verifier.md"
agent_input: "specs/tests.json test-001"
```

**What documentation-generator does:**
- Adds comprehensive JSDoc to all new functions/components
- Explains design decisions ("Why X approach")
- Documents alternatives considered and trade-offs
- Lists edge cases handled
- Updates or creates DECISIONS.md with ADR entry
- Updates README.md if user-facing feature added
- Separate git commit for documentation

**Why this phase matters:**
- Context is fresh (just wrote the code, remember why)
- Future developers understand "why" not just "what"
- Maintenance becomes possible (not mysterious code)
- Separate commit keeps git history clean

Call report_progress after documenting each test:
- message: "Documented test-{id} with design decisions and trade-offs"
