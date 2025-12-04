#!/usr/bin/env python3
"""
Atomic Agents TDD - TRUE Agent-First Architecture (Tools-Based)
================================================================

The orchestrator agent uses TOOLS to control execution.
Python provides tools. Agent calls them. THAT'S IT.

Inspired by: github.com/disler/multi-agent-orchestration
"""

import argparse
import asyncio
import sys
from pathlib import Path
from typing import Optional, Dict, Any, List

from claude_agent_sdk import ClaudeSDKClient, ClaudeAgentOptions, tool
from orchestrator import MarkdownOrchestrator
from config import REF_API_KEY
from markdown_parser import extract_output_marker


class AgentFirstPipeline:
    """
    Tools-based orchestration. The agent calls tools. We execute them.
    """

    def __init__(self, base_dir: Path, project_dir: Path):
        self.base_dir = base_dir
        self.project_dir = project_dir
        self.orch = MarkdownOrchestrator(base_dir, project_dir)
        self.state = {}  # Track state for extraction markers
        self.background_tasks = []  # Track async tasks

    def create_orchestration_tools(self):
        """
        Create tools that the orchestrator agent can call.
        These are the ONLY ways the agent can control execution.
        """

        @tool(
            "run_agent",
            "Run a single agent with input. Returns agent output. REQUIRED: agent_path (e.g. 'agents/git-setup.md'), agent_input (the full input string for the agent).",
            {"agent_path": str, "agent_input": str}
        )
        async def run_agent_tool(args: Dict[str, Any]) -> Dict[str, Any]:
            """Tool for running a single agent"""
            try:
                agent_path = args.get("agent_path")
                agent_input = args.get("agent_input")

                if not agent_path or not agent_input:
                    return {
                        "content": [{"type": "text", "text": "❌ Error: 'agent_path' and 'agent_input' are required"}],
                        "is_error": True
                    }

                print(f"\n▶️  Running: {agent_path}")
                print(f"   Input: {agent_input[:80]}...")

                # Run the agent synchronously
                result = await self.orch.run_agent(
                    agent_path=agent_path,
                    task_input=agent_input,
                    cwd=self.project_dir,
                )

                # Extract markers from result
                self._extract_markers(result)

                print(f"✓ {agent_path} complete")

                # Return result to orchestrator
                return {
                    "content": [{"type": "text", "text": f"✅ Agent completed successfully.\n\nOutput:\n{result[:500]}"}]
                }

            except Exception as e:
                print(f"❌ Error running agent: {e}")
                return {
                    "content": [{"type": "text", "text": f"❌ Error: {str(e)}"}],
                    "is_error": True
                }

        @tool(
            "run_agents_parallel",
            "Run multiple agents in PARALLEL with different inputs. Much faster than sequential! REQUIRED: agent_path (same agent for all), inputs (list of input strings, one per agent instance).",
            {"agent_path": str, "inputs": list}
        )
        async def run_agents_parallel_tool(args: Dict[str, Any]) -> Dict[str, Any]:
            """Tool for running multiple agents in parallel"""
            try:
                agent_path = args.get("agent_path")
                inputs = args.get("inputs", [])

                if not agent_path or not inputs:
                    return {
                        "content": [{"type": "text", "text": "❌ Error: 'agent_path' and 'inputs' are required"}],
                        "is_error": True
                    }

                print(f"\n⚡ Running {len(inputs)} agents in PARALLEL:")
                print(f"   {agent_path}")

                # Create tasks for parallel execution
                tasks = []
                for agent_input in inputs:
                    tasks.append(self.orch.run_agent(
                        agent_path=agent_path,
                        task_input=agent_input,
                        cwd=self.project_dir,
                    ))

                # Run all in parallel!
                results = await asyncio.gather(*tasks, return_exceptions=True)

                # Extract markers from all results
                for result in results:
                    if not isinstance(result, Exception):
                        self._extract_markers(result)

                # Count successes
                successes = sum(1 for r in results if not isinstance(r, Exception))
                failures = len(results) - successes

                print(f"✓ Parallel execution complete: {successes}/{len(inputs)} succeeded")

                return {
                    "content": [{
                        "type": "text",
                        "text": f"✅ Parallel execution complete!\n\n"
                                f"Total agents: {len(inputs)}\n"
                                f"Succeeded: {successes}\n"
                                f"Failed: {failures}\n\n"
                                f"All agents have completed their work."
                    }]
                }

            except Exception as e:
                print(f"❌ Error in parallel execution: {e}")
                return {
                    "content": [{"type": "text", "text": f"❌ Error: {str(e)}"}],
                    "is_error": True
                }

        @tool(
            "run_agent_background",
            "Run an agent in the BACKGROUND (non-blocking). Returns immediately. Use for long-running tasks. REQUIRED: agent_path, agent_input.",
            {"agent_path": str, "agent_input": str}
        )
        async def run_agent_background_tool(args: Dict[str, Any]) -> Dict[str, Any]:
            """Tool for running agent in background"""
            try:
                agent_path = args.get("agent_path")
                agent_input = args.get("agent_input")

                if not agent_path or not agent_input:
                    return {
                        "content": [{"type": "text", "text": "❌ Error: 'agent_path' and 'agent_input' are required"}],
                        "is_error": True
                    }

                print(f"\n🔄 Starting background agent: {agent_path}")

                # Create background task
                task = asyncio.create_task(
                    self.orch.run_agent(
                        agent_path=agent_path,
                        task_input=agent_input,
                        cwd=self.project_dir,
                    )
                )

                # Track it
                self.background_tasks.append(task)

                return {
                    "content": [{
                        "type": "text",
                        "text": f"✅ Agent started in background!\n\n"
                                f"Agent: {agent_path}\n"
                                f"Input: {agent_input[:100]}...\n\n"
                                f"The agent is running asynchronously. You can continue with other work."
                    }]
                }

            except Exception as e:
                print(f"❌ Error starting background agent: {e}")
                return {
                    "content": [{"type": "text", "text": f"❌ Error: {str(e)}"}],
                    "is_error": True
                }

        @tool(
            "get_state",
            "Get current pipeline state (tests_file, plan_file, branch, etc). Use this to get paths you need for other agents.",
            {}
        )
        async def get_state_tool(args: Dict[str, Any]) -> Dict[str, Any]:
            """Tool for getting current state"""
            try:
                if not self.state:
                    return {
                        "content": [{"type": "text", "text": "📋 State is empty (no agents have run yet)"}]
                    }

                state_lines = ["📋 Current Pipeline State:\n"]
                for key, value in self.state.items():
                    state_lines.append(f"• {key}: {value}\n")

                return {
                    "content": [{"type": "text", "text": "".join(state_lines)}]
                }

            except Exception as e:
                return {
                    "content": [{"type": "text", "text": f"❌ Error: {str(e)}"}],
                    "is_error": True
                }

        @tool(
            "report_progress",
            "Report progress to the user. Use this to keep user informed. REQUIRED: message.",
            {"message": str}
        )
        async def report_progress_tool(args: Dict[str, Any]) -> Dict[str, Any]:
            """Tool for reporting progress"""
            try:
                message = args.get("message", "")
                print(f"\n📊 {message}")

                return {
                    "content": [{"type": "text", "text": "✅ Progress reported to user"}]
                }

            except Exception as e:
                return {
                    "content": [{"type": "text", "text": f"❌ Error: {str(e)}"}],
                    "is_error": True
                }

        return [
            run_agent_tool,
            run_agents_parallel_tool,
            run_agent_background_tool,
            get_state_tool,
            report_progress_tool,
        ]

    def _extract_markers(self, output: str):
        """Extract and store output markers like TESTS_FILE:, PLAN_FILE:, etc."""
        markers = {
            'tests_file': r'TESTS_FILE:\s*(.+)',
            'plan_file': r'PLAN_FILE:\s*(.+)',
            'branch': r'BRANCH:\s*(.+)',
            'metrics_file': r'REPORT_FILE:\s*(.+)',
        }

        for key, pattern in markers.items():
            value = extract_output_marker(output, pattern)
            if value:
                self.state[key] = value
                print(f"   📌 {key}: {value}")

    async def run(self, task: str):
        """
        Start conversation with orchestrator agent.
        The agent has tools to control execution.
        """
        print("\n" + "="*70)
        print("  ATOMIC AGENTS TDD - TRUE AGENT-FIRST (TOOLS-BASED)")
        print("="*70)
        print(f"\nTask: {task}")
        print(f"Project: {self.project_dir}")
        print("\nStarting orchestrator agent with execution tools...")
        print("(The agent controls everything via tool calls)\n")

        # Create tools
        tools = self.create_orchestration_tools()

        # Register tools via MCP server
        from claude_agent_sdk import create_sdk_mcp_server

        mcp_server = create_sdk_mcp_server(
            name="pipeline",
            version="1.0.0",
            tools=tools
        )

        # Build orchestrator system prompt
        system_prompt = f"""You are the TDD pipeline orchestrator.

Your job: Coordinate the entire Test-Driven Development pipeline by calling tools.

## Available Tools

You have these tools to control execution:

1. **run_agent** - Run a single agent (blocking)
2. **run_agents_parallel** - Run multiple agents in parallel (faster!)
3. **run_agent_background** - Run agent in background (non-blocking)
4. **get_state** - Get current state (tests_file, plan_file, etc)
5. **report_progress** - Report progress to user

## Pipeline Phases

Follow this workflow:

### Phase 1: Git Setup
Call: run_agent(agent_path="agents/git-setup.md", agent_input="{task}")
This creates a feature branch.

### Phase 2: Generate Tests
Call: run_agent(agent_path="agents/test-generator.md", agent_input="{task}")
Call: get_state() to see tests_file path

### Phase 3: Create Plan
Call: run_agent(agent_path="agents/chore-planner.md", agent_input="{{tests_file}}")
Call: get_state() to see plan_file path

### Phase 4: Execution Planning
Call: run_agent(agent_path="agents/execution-planner.md", agent_input="{{tests_file}}")
This tells you which tests can run in parallel.

### Phase 5: Implementation & Verification
For each execution group:
- If PARALLEL: Call run_agents_parallel with list of inputs like ["{{plan_file}} test-001", "{{plan_file}} test-002"]
- If SEQUENTIAL: Call run_agent for each test individually

Then verify:
- Call run_agents_parallel for verifiers: ["{{tests_file}} test-001", "{{tests_file}} test-002"]

Report progress after each group!

### Phase 6: Bug Check
Call: run_agent(agent_path="agents/bugfinder.md", agent_input="all")

### Phase 7: Metrics
Call: run_agent(agent_path="agents/metrics-reporter.md", agent_input="{{tests_file}} {{plan_file}}")

### Phase 8: Final Summary
Report final results with report_progress tool.

## Important Notes

- Use get_state() to retrieve file paths you need
- Use run_agents_parallel whenever possible for speed
- Use report_progress to keep user informed
- Track all state yourself - Python doesn't help you
- Construct full inputs for agents (include plan_file path, test IDs, etc)

## Project Context

Project Directory: {self.project_dir}
Task: {task}

Begin by running git-setup, then follow the phases above.
"""

        # Create orchestrator with tools
        options = ClaudeAgentOptions(
            system_prompt=system_prompt,
            model="claude-sonnet-4-5-20250929",
            cwd=self.project_dir,
            mcp_servers={
                "pipeline": mcp_server,
                "ref": {
                    "transport": "http",
                    "url": "https://api.ref.tools/mcp",
                    "headers": {
                        "x-ref-api-key": REF_API_KEY
                    }
                }
            },
            allowed_tools=[
                "mcp__pipeline__run_agent",
                "mcp__pipeline__run_agents_parallel",
                "mcp__pipeline__run_agent_background",
                "mcp__pipeline__get_state",
                "mcp__pipeline__report_progress",
                "mcp__ref__ref_search_documentation",  # Search tech docs
                "mcp__ref__ref_read_url",              # Read web pages
                "mcp__ref__ref_search_web",            # Fallback web search
                "Read",  # Let orchestrator read files if needed
                "Bash",  # Let orchestrator check things if needed
            ],
            permission_mode="acceptEdits",
        )

        # Run orchestrator
        async with ClaudeSDKClient(options=options) as client:
            await client.query(f"Begin the TDD pipeline for this task: {task}")

            # Process all responses
            async for message in client.receive_response():
                # The agent will call tools
                # Tools execute
                # Agent gets results
                # Agent makes decisions
                pass

        # Wait for any background tasks
        if self.background_tasks:
            print("\n⏳ Waiting for background tasks to complete...")
            await asyncio.gather(*self.background_tasks, return_exceptions=True)

        # Final summary
        print("\n" + "="*70)
        print("  PIPELINE COMPLETE")
        print("="*70)

        if self.state:
            print("\n📋 Final State:")
            for key, value in self.state.items():
                print(f"  • {key}: {value}")

        if self.state.get('branch'):
            print(f"\n🔀 Git Branch: {self.state['branch']}")
            print(f"\nTo push changes:")
            print(f"  cd {self.project_dir}")
            print(f"  git push -u origin {self.state['branch']}")

        print()


def main():
    parser = argparse.ArgumentParser(
        description="Run atomic agents TDD pipeline (Tools-Based Agent-First)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
TRUE Agent-First Architecture (Tools-Based):
  - Orchestrator agent calls tools
  - Python provides tools
  - Agent makes ALL decisions
  - Zero string parsing
  - Clean, extensible design

Examples:
  python run.py "Create a /api/health endpoint"
  python run.py "Add UK postcode validation utility"
        """,
    )

    parser.add_argument(
        "task",
        type=str,
        help="Task description",
    )

    parser.add_argument(
        "--project-dir",
        type=Path,
        default=Path.cwd(),
        help="Project directory (default: current directory)",
    )

    args = parser.parse_args()

    try:
        pipeline = AgentFirstPipeline(Path(__file__).parent, args.project_dir)
        asyncio.run(pipeline.run(args.task))
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user")
        sys.exit(130)
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
