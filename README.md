# Atomic Agents with TDD - TRUE Agent-First Architecture

> Test-Driven Development meets Atomic Markdown Agents with Tools-Based Orchestration

A lightweight orchestration framework combining:
- **TRUE agent-first architecture** - Agents control execution via tools, Python is just a dumb executor
- **Atomic markdown agents** (Unix philosophy for AI)
- **Test-first approach** (acceptance criteria before implementation)
- **Fresh context sessions** (resilient to context window limits)
- **State via files** (not complex schemas)
- **Parallel execution** (asyncio.gather for concurrent agents)

## Quick Start

```bash
# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set API key
export ANTHROPIC_API_KEY='your-key-here'

# Run the full TDD pipeline (agent-driven!)
python run.py "Create a /api/health endpoint that returns system status"
```

### What Happens? (All Agent-Driven!)

The **pipeline-orchestrator** agent controls everything by calling tools:

1. **Git Setup** - Creates feature branch
2. **Generate Tests** - Creates `specs/chore-DDMMYY-HHMM-tests.json` with 5-15 acceptance criteria
3. **Create Plan** - Creates `specs/chore-DDMMYY-HHMM-plan.md` with implementation steps
4. **Analyze Dependencies** - Determines which tests can run in parallel
5. **Implement & Verify Loop** - For each test group:
   - Runs implementer agents (in parallel when possible!)
   - Runs verifier agents (in parallel when possible!)
6. **Bug Check** - Final analysis for issues
7. **Metrics** - Cost and performance summary

**The orchestrator decides everything** - Python just provides tools!

## Working with Large Specifications

### Scope Guidance

**Recommended:** 5-15 tests per run (30-45 minutes, optimal for focused tasks)
**Supported:** Up to 100 tests per run (2-4 hours, for large projects)

### Large Project Strategy

For specifications that generate 50+ tests:

1. **Option 1: Submit as Single Spec (Patient Approach)**
   ```bash
   python run.py "$(cat large-project-spec.txt)"
   # Pipeline runs for 2-4 hours, completes all tests
   # Context window: ~65% usage (plenty of headroom)
   ```

2. **Option 2: Split into Phases (Incremental Approach)**
   ```bash
   # Phase 1: Infrastructure (15 tests, 45 min)
   python run.py "$(cat phase-1-infrastructure.txt)"

   # Phase 2: Core Features (30 tests, 90 min)
   python run.py "$(cat phase-2-features.txt)"

   # Phase 3: Polish (10 tests, 30 min)
   python run.py "$(cat phase-3-polish.txt)"
   ```

### Fault Tolerance with Continuation Agent

If the pipeline is interrupted (error, timeout, or manual stop):

```bash
# Pipeline stopped at test 45/80?
# The continuation agent picks up where it left off

python run.py --continue  # (if supported)
# OR manually invoke continuation agent
# Continuation agent:
# - Reads progress.txt to see what's done
# - Counts passing vs failing tests
# - Implements remaining tests
# - Fully automated resume!
```

**How it works:**
- Progress tracked in `progress.txt`
- Test results stored in `specs/chore-*-tests.json` (`"passes": true/false`)
- Continuation agent identifies next failing test and resumes
- No manual state management needed!

### Why Large Specs Work Now

**Context is NOT a bottleneck:**
- Each agent (implementer, verifier) gets fresh context
- Orchestrator receives only 500 chars per agent output
- 80 tests = ~130k tokens (65% of 200k budget)
- No continuation sessions needed (unless error occurs)

**Trade-offs:**
- ✅ Single command for entire project
- ✅ Fault-tolerant (resume from failure)
- ⚠️  Long runtime (2-4 hours for 80 tests)
- ⚠️  Error at test 60 requires restart (continuation handles this)

## Architecture: TRUE Agent-First

### The Revolutionary Insight

**OLD WAY (run_v2.py):**
```python
# ❌ Python decides what to do - NOT agent-first!
for phase in PHASES:
    if phase == "git":
        run_agent("git-setup.md", task)
    elif phase == "tests":
        run_agent("test-generator.md", task)
    # ... hard-coded orchestration logic
```

**NEW WAY (run.py with tools):**
```python
# ✅ Agent decides what to do - Python just provides tools!
@tool("run_agent", "Run a single agent", {...})
async def run_agent_tool(args):
    return await orch.run_agent(args["agent_path"], args["agent_input"])

@tool("run_agents_parallel", "Run multiple agents in PARALLEL", {...})
async def run_agents_parallel_tool(args):
    tasks = [orch.run_agent(path, inp) for inp in args["inputs"]]
    return await asyncio.gather(*tasks)

# Orchestrator agent calls these tools to control execution!
```

### Available Tools for Orchestrator Agent

The orchestrator agent has access to these tools:

1. **run_agent** - Run a single agent (blocking)
2. **run_agents_parallel** - Run multiple agents in parallel (fast!)
3. **run_agent_background** - Run agent in background (non-blocking)
4. **get_state** - Get current pipeline state (tests_file, plan_file, branch, etc.)
5. **report_progress** - Report progress to user

**Python provides tools. Agent makes ALL decisions.**

### Core Files (21 Total)

**Execution Framework:**
- `run.py` - Main entrypoint (tools-based orchestration)
- `orchestrator.py` - Agent executor (wraps Claude SDK)
- `markdown_parser.py` - Parses agent markdown files

**Agent Files (18 total in agents/):**
- `pipeline-orchestrator.md` - **Master coordinator** (calls tools to control pipeline)
- `git-setup.md` - Creates feature branches
- `requirements-analyzer.md` - Converts text specs to architecture JSON
- `style-integrator.md` - Generates design system and Tailwind config
- `codebase-context-builder.md` - Discovers existing patterns (cached 7 days)
- `environment-provisioner.md` - **NEW!** Auto-generates docker-compose, .env files
- `test-generator.md` - Generates acceptance criteria
- `chore-planner.md` - Creates implementation plans
- `execution-planner.md` - Analyzes dependencies for parallel execution
- `implementer.md` - Implements tests from plan
- `verifier.md` - Verifies acceptance criteria with quality gates
- `quick-bugcheck.md` - Lightweight bug detection after each implementation group
- `bugfinder.md` - Comprehensive bug analysis
- `bugfixer.md` - Auto-fixes deterministic bugs
- `code-structure-validator.md` - **NEW!** Enforces frontend/backend boundaries
- `compliance-enforcer.md` - **NEW!** Validates GDPR patterns
- `documentation-generator.md` - Adds JSDoc, creates DECISIONS.md ADRs
- `metrics-reporter.md` - Generates cost/performance reports
- `continuation.md` - Resumes interrupted pipelines

**Supporting Files:**
- `requirements.txt` - Python dependencies
- `README.md` - This file

## Agent Format

Each agent is a markdown file with:

```markdown
---
description: What this agent does
argument-hint: "[param1] [param2]"
model: sonnet
tools: [Read, Write, Bash]
---

# Agent Name

## Purpose
High-level description

## Variables
INPUT: $1

## Instructions
- Rule 1
- Rule 2

## Workflow
1. Step 1
2. Step 2

## Report
Expected output format
```

## Pipeline Orchestrator (The Brain)

The `pipeline-orchestrator.md` agent controls the ENTIRE pipeline by calling tools:

### Phase 1: Git Setup
```
Tool: run_agent
Parameters:
  agent_path: "agents/git-setup.md"
  agent_input: "Create feature branch for: <task>"
```

### Phase 2: Test Generation
```
Tool: run_agent
Parameters:
  agent_path: "agents/test-generator.md"
  agent_input: "<task>"
```

### Phase 3: Planning
```
Tool: run_agent
Parameters:
  agent_path: "agents/chore-planner.md"
  agent_input: "<tests_file path from get_state>"
```

### Phase 4: Execution Planning
```
Tool: run_agent
Parameters:
  agent_path: "agents/execution-planner.md"
  agent_input: "<tests_file path>"
```

### Phase 5: Implementation (PARALLEL!)
```
Tool: run_agents_parallel
Parameters:
  agent_path: "agents/implementer.md"
  inputs: ["plan.md test-001", "plan.md test-002", "plan.md test-003"]
```

**The orchestrator decides when to run agents in parallel vs sequential!**

### Phase 6: Verification (PARALLEL!)
```
Tool: run_agents_parallel
Parameters:
  agent_path: "agents/verifier.md"
  inputs: ["tests.json test-001", "tests.json test-002", "tests.json test-003"]
```

### Phase 7: Bug Finding
```
Tool: run_agent
Parameters:
  agent_path: "agents/bugfinder.md"
  agent_input: "<branch name from get_state>"
```

### Phase 8: Metrics
```
Tool: run_agent
Parameters:
  agent_path: "agents/metrics-reporter.md"
  agent_input: "."
```

## TDD Pattern (Inspired by Anthropic's Autonomous Coding)

### 1. Test-First JSON
Generate acceptance criteria BEFORE implementing:

```json
[
  {
    "id": "test-001",
    "category": "functionality",
    "description": "Health endpoint returns 200 OK",
    "acceptance": [
      "File exists at src/app/api/health/route.ts",
      "File exports GET handler",
      "TypeScript compilation passes"
    ],
    "passes": false,
    "priority": 1
  }
]
```

### 2. Progress Tracking
Agents update `progress.txt` with implementation notes.

### 3. State Management via Markers
Agents communicate results via output markers:

```markdown
## Report
BRANCH: feature/create-api-health-endpoint
TESTS_FILE: specs/chore-041225-1030-tests.json
PLAN_FILE: specs/chore-041225-1031-plan.md
```

Python extracts these markers and stores in `self.state`:

```python
def _extract_markers(self, result: str):
    """Extract BRANCH:, TESTS_FILE:, etc. from agent output"""
    if match := re.search(r"BRANCH:\s*(.+)", result):
        self.state["branch"] = match.group(1).strip()
    if match := re.search(r"TESTS_FILE:\s*(.+)", result):
        self.state["tests_file"] = match.group(1).strip()
    # ...
```

Orchestrator retrieves state via `get_state()` tool!

## State Files

```
specs/
├── chore-DDMMYY-HHMM-tests.json    # Test definitions
├── chore-DDMMYY-HHMM-plan.md       # Implementation plan
└── bugfinder-DDMMYY-HHMM-report.md # Bug analysis

progress.txt                         # Session notes
```

## Example: Health Endpoint Task

```bash
python run.py "Create a /api/health endpoint that returns system status"
```

**What happens (all agent-driven):**

1. Orchestrator calls `run_agent(git-setup.md)` → Creates `feature/create-api-health-endpoint`
2. Orchestrator calls `run_agent(test-generator.md)` → Creates 12 tests in `specs/chore-041225-1030-tests.json`
3. Orchestrator calls `run_agent(chore-planner.md)` → Creates detailed plan in `specs/chore-041225-1031-plan.md`
4. Orchestrator calls `run_agent(execution-planner.md)` → Analyzes dependencies, identifies 6 execution groups
5. Orchestrator calls `run_agent(implementer.md, test-001)` → Implements route.ts (268 lines)
6. Orchestrator calls `run_agent(verifier.md, test-001)` → Verifies all acceptance criteria pass
7. Orchestrator calls `run_agents_parallel(implementer.md, [test-002, test-008])` → **PARALLEL EXECUTION!**
8. Orchestrator calls `run_agents_parallel(verifier.md, [test-002, test-008])` → **PARALLEL VERIFICATION!**
9. ... continues through all groups ...
10. Orchestrator calls `run_agent(bugfinder.md)` → Analyzes for bugs
11. Orchestrator calls `run_agent(metrics-reporter.md)` → Generates cost/performance summary

**Zero hard-coded logic in Python. All decisions made by orchestrator agent via tool calls!**

## Key Technical Decisions

### 1. MCP Server Pattern for Tools
```python
from claude_agent_sdk import create_sdk_mcp_server

# Register tools via MCP server
mcp_server = create_sdk_mcp_server(
    name="pipeline",
    version="1.0.0",
    tools=[run_agent_tool, run_agents_parallel_tool, ...]
)

options = ClaudeAgentOptions(
    system_prompt=system_prompt,
    mcp_servers={"pipeline": mcp_server},
    allowed_tools=[
        "mcp__pipeline__run_agent",
        "mcp__pipeline__run_agents_parallel",
        "mcp__pipeline__get_state",
        "Read",
        "Bash",
    ]
)
```

### 2. Tool Names Must Use MCP Format
```python
# ✅ Correct
allowed_tools=["mcp__pipeline__run_agent"]

# ❌ Wrong
allowed_tools=["run_agent"]
```

### 3. Async Parallel Execution
```python
@tool("run_agents_parallel", "Run multiple agents in PARALLEL", {...})
async def run_agents_parallel_tool(args):
    tasks = [orch.run_agent(path, inp) for inp in args["inputs"]]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    return results
```

### 4. State Extraction from Agent Output
```python
def _extract_markers(self, result: str):
    """Extract markers like TESTS_FILE:, PLAN_FILE:, BRANCH:"""
    # Regex patterns to find markers in agent output
    # Store in self.state dictionary
    # Orchestrator retrieves via get_state() tool
```

## Advantages Over Hard-Coded Orchestration

| Hard-Coded Python | Tools-Based Agent-First |
|-------------------|-------------------------|
| Python decides execution order | Agent decides execution order |
| Python hard-codes phases | Agent adapts phases dynamically |
| Python decides parallel vs sequential | Agent analyzes dependencies |
| Python error handling logic | Agent handles errors contextually |
| Brittle to changes | Flexible and adaptable |
| NOT truly agent-first | TRUE agent-first ALL THE WAY |

**Agent-First Score:** 10/10 (Python is just a dumb tool executor)

## Philosophy

> **TRUE Agent-First Architecture**
>
> Agents make ALL decisions.
> Python provides tools, nothing more.
> Orchestrator controls execution via tool calls.
> Parallel execution when agents decide it's safe.
> State persists via files, not memory.
> Fresh context = read state from files.

## Patterns from Anthropic & Multi-Agent-Orchestration

### ✅ Adopted (Essential)
- **Test-first JSON** - Acceptance criteria before implementation
- **Tools-based orchestration** - Agent calls tools to control execution
- **MCP server registration** - `create_sdk_mcp_server` pattern
- **Parallel execution** - `asyncio.gather` for concurrent agents
- **Background execution** - `asyncio.create_task` for non-blocking
- **State via markers** - Agents communicate via TESTS_FILE:, PLAN_FILE:, etc.
- **Fresh context pattern** - Read state from files, no memory
- **Git as persistence** - State via commits

### ❌ Skipped (Over-Engineering)
- **200 test cases upfront** - Too much (we use 5-15 dynamic tests)
- **Puppeteer MCP** - Browser automation (not needed)
- **Security hooks** - Bash command allowlists (unnecessary)
- **String command parsing** - We use tools, not string commands!

## Why This Architecture is Revolutionary

### The Problem with Most "Agent" Systems:
Most systems claim to be "agent-first" but are actually:
```python
# Python decides everything
if condition:
    run_agent("foo")
else:
    run_agent("bar")
```

### This is TRUE Agent-First:
```python
# Agent decides everything via tools
@tool("run_agent")
def run_agent_tool(args):
    return orch.run_agent(args["agent_path"], args["agent_input"])

# Orchestrator agent calls this tool when IT decides to
```

**The agent is in control. Python just executes commands.**

## NEW: Production-Ready Agents (Dec 2025)

Three new agents were added to enable full automation for enterprise projects:

### 1. Environment Provisioner (`environment-provisioner.md`)

**Purpose:** Auto-generate docker-compose.yml, .env files, and infrastructure configs

**When it runs:** Phase 0.8 (after codebase context, before test generation)

**What it generates:**
- `docker-compose.yml` with custom ports, volumes, networks
- `.env.development`, `.env.staging`, `.env.production`
- `specs/infra-config-DDMMYY-HHMM.json` (metadata)

**Example output:**
```yaml
# docker-compose.yml
services:
  postgres:
    image: postgis/postgis:15-3.4
    ports:
      - "5434:5432"  # Custom port to avoid conflicts
    volumes:
      - postgres-data:/var/lib/postgresql/data
    networks:
      - myapp_network
```

**Why it matters:**
- ✅ Zero manual docker-compose editing
- ✅ Handles custom ports (Windows conflicts)
- ✅ Environment-specific configs
- ✅ Secrets as placeholders (never hardcoded)

**Marker:** `INFRA_CONFIG: specs/infra-config-*.json`

---

### 2. Compliance Enforcer (`compliance-enforcer.md`)

**Purpose:** Validate GDPR patterns and **BLOCK** deployment on violations

**When it runs:** Phase 5.7 (after bugfixing, before deployment)

**What it validates:**
- ❌ **CRITICAL:** Consent collection before data submission
- ❌ **CRITICAL:** Right to deletion (soft deletes)
- ❌ **CRITICAL:** Audit logging on PII access
- ⚠️ **WARNING:** Data minimization
- ⚠️ **WARNING:** Encryption at rest
- ⚠️ **WARNING:** Third-party data sharing

**Example violation:**
```typescript
// ❌ BLOCKED: No consent check
const handleSubmit = async (data) => {
  await fetch('/api/register', {
    method: 'POST',
    body: JSON.stringify(data)  // VIOLATION!
  });
};
```

**Example fix:**
```typescript
// ✅ PASSED: Consent check added
const handleSubmit = async (data) => {
  if (!hasConsent('data_collection')) {
    showConsentModal();
    return;
  }
  await fetch('/api/register', {
    method: 'POST',
    body: JSON.stringify(data)
  });
};
```

**Why it matters:**
- ✅ Prevents GDPR violations from reaching production
- ✅ UK ICO fines can reach £17M - this catches issues immediately
- ✅ Auto-generates actionable fix recommendations
- ✅ Blocks deployment on CRITICAL violations

**Markers:**
- `COMPLIANCE_REPORT: specs/compliance-*.md`
- `COMPLIANCE_VALIDATION: pass|fail`

---

### 3. Code Structure Validator (`code-structure-validator.md`)

**Purpose:** Enforce frontend/backend boundaries and **BLOCK** contamination

**When it runs:** Phase 5.6 (before compliance check)

**What it validates:**
- ❌ **CRITICAL:** Frontend cannot import backend
- ❌ **CRITICAL:** Backend cannot import React
- ❌ **CRITICAL:** Shared directory must be type-only
- ⚠️ **WARNING:** Folder structure matches architecture
- ⚠️ **WARNING:** No circular dependencies

**Example violation:**
```typescript
// ❌ BLOCKED: Frontend importing backend
// frontend/src/components/Dashboard.tsx
import { getStats } from '../../backend/src/services/statsService';
```

**Example fix:**
```typescript
// ✅ PASSED: Use API client
// frontend/src/api/statsClient.ts
export const getStats = async () => {
  const res = await fetch('/api/stats');  // HTTP only
  return res.json();
};
```

**Why it matters:**
- ✅ Prevents architectural erosion
- ✅ Enables independent deployment (frontend/backend)
- ✅ Catches violations before code review
- ✅ Blocks deployment on boundary violations

**Markers:**
- `STRUCTURE_REPORT: specs/structure-*.md`
- `STRUCTURE_VALIDATION: pass|fail`

---

### Integration Example

When you run:
```bash
./run-isolated.sh "Build analytics platform with PostgreSQL"
```

**The pipeline now includes:**
```
Phase 0.8: Infrastructure Provisioning
├─ Generates docker-compose.yml (port 5434)
├─ Generates .env files
└─ Outputs: INFRA_CONFIG ✓

Phase 5.6: Code Structure Validation
├─ Checks frontend/backend boundaries
├─ All imports valid ✓
└─ Outputs: STRUCTURE_VALIDATION: pass ✓

Phase 5.7: Compliance Validation
├─ Checks GDPR patterns
├─ Consent modal found ✓
├─ Audit logging present ✓
└─ Outputs: COMPLIANCE_VALIDATION: pass ✓
```

**If validation fails:**
```
❌ COMPLIANCE_VALIDATION: fail

BLOCKING DEPLOYMENT:
- 2 CRITICAL violations found
- See specs/compliance-081225-1430.md for details

Fix violations and re-run pipeline.
```

---

### Success Metrics

| Metric | Before | After (With New Agents) |
|--------|--------|-------------------------|
| Infrastructure setup | 2-4 hours | Fully automated |
| GDPR compliance | Manual review | Auto-validated, blocks on violations |
| Code structure violations | Caught in review | Caught immediately |
| Pipeline time | 5-10 min | 7-12 min (+2-3 min validation) |
| Manual intervention | 3-5 per feature | 0 (full automation) |

**Cost:** +$0.25 per run (validation agents use Haiku model)

## Future Enhancements

- [ ] Cost tracking per agent (Claude API usage)
- [ ] Event logging (JSON logs for debugging)
- [ ] Retry mechanisms (with exponential backoff)
- [ ] Conditional tool execution (if/else in agent logic)
- [ ] State snapshots (save/restore pipeline state)
- [ ] Multi-project support (orchestrate across repos)

## Credits

Inspired by:
- [Anthropic's Autonomous Coding Demo](https://github.com/anthropics/claude-quickstarts/tree/main/autonomous-coding)
- [Multi-Agent Orchestration](https://github.com/disler/multi-agent-orchestration) - Tools-based patterns
- [Agentic Prompt Engineering](https://github.com/disler/agentic-prompt-engineering)

## License

MIT
