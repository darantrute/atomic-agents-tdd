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

### Core Files (15 Total)

**Execution Framework:**
- `run.py` - Main entrypoint (tools-based orchestration)
- `orchestrator.py` - Agent executor (wraps Claude SDK)
- `markdown_parser.py` - Parses agent markdown files

**Agent Files (10 total in agents/):**
- `pipeline-orchestrator.md` - **Master coordinator** (calls tools to control pipeline)
- `git-setup.md` - Creates feature branches
- `test-generator.md` - Generates acceptance criteria
- `chore-planner.md` - Creates implementation plans
- `execution-planner.md` - Analyzes dependencies for parallel execution
- `implementer.md` - Implements tests from plan
- `verifier.md` - Verifies acceptance criteria
- `bugfinder.md` - Finds and reports bugs
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
