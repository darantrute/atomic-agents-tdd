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
import json
import os
import subprocess
import sys
from datetime import datetime
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
        self.background_tasks = []  # Track async tasks

        # State persistence
        self.state_file = project_dir / "specs" / ".pipeline-state.json"
        self.state = self._load_state()

        # Auto-discover valid agents
        self.valid_agents = self._discover_agents()

    def _discover_agents(self) -> set:
        """Discover available agents from agents/*.md files."""
        agents_dir = self.base_dir / "agents"
        agents = set()

        for agent_file in agents_dir.glob("*.md"):
            # Skip Zone.Identifier files (Windows artifacts)
            if ":Zone.Identifier" in agent_file.name:
                continue
            # Skip pipeline-orchestrator (it's not callable as a sub-agent)
            if agent_file.stem == "pipeline-orchestrator":
                continue
            agents.add(agent_file.stem)

        print(f"📦 Discovered {len(agents)} agents: {', '.join(sorted(agents))}")
        return agents

    def _load_state(self) -> dict:
        """Load state from disk if exists, else return default state."""
        if self.state_file.exists():
            try:
                state = json.loads(self.state_file.read_text())
                print(f"📂 Loaded existing state from {self.state_file}")
                return state
            except json.JSONDecodeError:
                print(f"⚠️  Corrupted state file, starting fresh")
                return {'issues_found': [], '_meta': {}}
        return {'issues_found': [], '_meta': {}}

    def _persist_state(self):
        """Write state to disk after every change."""
        self.state['_meta']['last_updated'] = datetime.now().isoformat()
        self.state['_meta']['pid'] = os.getpid()
        self.state_file.parent.mkdir(parents=True, exist_ok=True)
        self.state_file.write_text(json.dumps(self.state, indent=2))

    def _acquire_lock(self, lock_file: Path) -> bool:
        """Acquire lock with PID-based stale detection."""
        if lock_file.exists():
            try:
                content = lock_file.read_text().strip()
                if content:
                    old_pid = int(content)
                    # Check if process is still running
                    try:
                        os.kill(old_pid, 0)  # Signal 0 = check existence
                        # Process exists - lock is valid
                        return False
                    except OSError:
                        # Process dead - stale lock
                        print(f"🔓 Removing stale lock (PID {old_pid} is dead)")
                        lock_file.unlink()
            except (ValueError, FileNotFoundError):
                # Invalid lock file content, remove it
                try:
                    lock_file.unlink()
                except FileNotFoundError:
                    pass

        # Write our PID
        lock_file.write_text(str(os.getpid()))
        return True

    def _release_lock(self, lock_file: Path):
        """Release lock file."""
        try:
            lock_file.unlink(missing_ok=True)
        except Exception:
            pass

    def _validate_agent_path(self, agent_path: str) -> tuple[bool, str]:
        """
        Validate that agent path exists and follows correct naming.
        Returns: (is_valid, error_message)
        """
        # Check format
        if not agent_path.startswith("agents/") or not agent_path.endswith(".md"):
            return False, f"Agent path must be 'agents/<name>.md', got: {agent_path}"

        # Extract agent name
        agent_name = agent_path[7:-3]  # Remove "agents/" and ".md"

        # Check if agent is in valid list
        if agent_name not in self.valid_agents:
            available = ", ".join(sorted(self.valid_agents))
            return False, f"Unknown agent '{agent_name}'. Available agents: {available}"

        # Check if file exists
        agent_file = self.base_dir / agent_path
        if not agent_file.exists():
            return False, f"Agent file not found: {agent_file}"

        return True, ""

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

                # Validate agent path
                is_valid, error_msg = self._validate_agent_path(agent_path)
                if not is_valid:
                    print(f"❌ Invalid agent path: {error_msg}")
                    return {
                        "content": [{"type": "text", "text": f"❌ Invalid agent path: {error_msg}"}],
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

                # Validate agent path
                is_valid, error_msg = self._validate_agent_path(agent_path)
                if not is_valid:
                    print(f"❌ Invalid agent path: {error_msg}")
                    return {
                        "content": [{"type": "text", "text": f"❌ Invalid agent path: {error_msg}"}],
                        "is_error": True
                    }

                # Limit parallel execution to 10 agents max
                if len(inputs) > 10:
                    return {
                        "content": [{"type": "text", "text": f"❌ Error: Too many parallel agents ({len(inputs)}). Maximum is 10. Split into multiple batches."}],
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

        @tool(
            "update_progress",
            "Update pipeline progress tracking with phase information. REQUIRED: phase (e.g. 'phase-1'), status ('started'|'completed'|'failed'). OPTIONAL: details (dict with extra info).",
            {"phase": str, "status": str, "details": dict}
        )
        async def update_progress_tool(args: Dict[str, Any]) -> Dict[str, Any]:
            """Tool for updating structured progress"""
            try:
                phase = args.get("phase", "unknown")
                status = args.get("status", "unknown")
                details = args.get("details", {})

                # Update state with phase info
                if 'phases' not in self.state:
                    self.state['phases'] = []

                self.state['phases'].append({
                    "phase": phase,
                    "status": status,
                    "timestamp": datetime.now().isoformat(),
                    "details": details
                })
                self.state['current_phase'] = phase
                self.state['last_updated'] = datetime.now().isoformat()

                # Persist to disk
                self._persist_state()

                # Also write human-readable progress.txt
                self._write_progress_txt()

                print(f"\n📝 Progress: {phase} - {status}")

                return {
                    "content": [{"type": "text", "text": f"✅ Progress updated: {phase} - {status}"}]
                }

            except Exception as e:
                return {
                    "content": [{"type": "text", "text": f"❌ Error: {str(e)}"}],
                    "is_error": True
                }

        @tool(
            "rollback_pipeline",
            "Emergency rollback to base commit. USE WITH CAUTION - discards all pipeline changes. REQUIRED: confirm (must be 'yes' to proceed).",
            {"confirm": str}
        )
        async def rollback_tool(args: Dict[str, Any]) -> Dict[str, Any]:
            """Tool for emergency rollback"""
            try:
                if args.get("confirm") != "yes":
                    return {
                        "content": [{"type": "text", "text": "❌ Rollback requires confirm='yes' to proceed. This will discard ALL pipeline changes."}],
                        "is_error": True
                    }

                base_commit = self.state.get("base_commit")
                if not base_commit:
                    return {
                        "content": [{"type": "text", "text": "❌ No base_commit in state - cannot rollback. Run git log to find commit manually."}],
                        "is_error": True
                    }

                print(f"\n⚠️  ROLLING BACK to {base_commit[:8]}...")

                # Hard reset to base commit
                result = subprocess.run(
                    ["git", "reset", "--hard", base_commit],
                    cwd=self.project_dir,
                    capture_output=True,
                    text=True
                )

                if result.returncode != 0:
                    return {
                        "content": [{"type": "text", "text": f"❌ Rollback failed: {result.stderr}"}],
                        "is_error": True
                    }

                # Clear state except base_commit and task
                old_task = self.state.get('task', '')
                self.state = {
                    "base_commit": base_commit,
                    "task": old_task,
                    "issues_found": [],
                    "rolled_back_at": datetime.now().isoformat(),
                    "_meta": {}
                }
                self._persist_state()

                print(f"✅ Rolled back to {base_commit[:8]}")

                return {
                    "content": [{"type": "text", "text": f"✅ Rolled back to {base_commit[:8]}. Pipeline state cleared. You can restart the pipeline."}]
                }

            except Exception as e:
                return {
                    "content": [{"type": "text", "text": f"❌ Rollback error: {str(e)}"}],
                    "is_error": True
                }

        return [
            run_agent_tool,
            run_agents_parallel_tool,
            run_agent_background_tool,
            get_state_tool,
            report_progress_tool,
            update_progress_tool,
            rollback_tool,
        ]

    def _write_progress_txt(self):
        """Write human-readable progress.txt from state."""
        progress_txt = self.project_dir / "progress.txt"

        lines = [
            "Pipeline Progress",
            "=" * 50,
            f"Task: {self.state.get('task', 'N/A')}",
            f"Started: {self.state.get('started_at', 'N/A')}",
            f"Last Update: {self.state.get('last_updated', 'N/A')}",
            f"Current Phase: {self.state.get('current_phase', 'N/A')}",
            f"Branch: {self.state.get('branch', 'N/A')}",
            "",
            "State:",
        ]

        # Add key state values
        skip_keys = {'_meta', 'phases', 'issues_found', 'task', 'started_at', 'last_updated', 'current_phase'}
        for key, value in self.state.items():
            if key not in skip_keys:
                lines.append(f"  {key}: {value}")

        # Add phase history
        lines.append("")
        lines.append("Phase History (last 10):")
        for p in self.state.get("phases", [])[-10:]:
            lines.append(f"  - {p['phase']}: {p['status']} ({p['timestamp']})")

        progress_txt.write_text("\n".join(lines))

    def _extract_markers(self, output: str):
        """Extract and store output markers like TESTS_FILE:, PLAN_FILE:, etc."""
        markers = {
            'tests_file': r'TESTS_FILE:\s*(.+)',
            'plan_file': r'PLAN_FILE:\s*(.+)',
            'branch': r'BRANCH:\s*(.+)',
            'base_commit': r'BASE_COMMIT:\s*(.+)',  # Track pipeline base commit
            'metrics_file': r'REPORT_FILE:\s*(.+)',
            'architecture_map': r'ARCHITECTURE_MAP:\s*(.+)',
            'style_system': r'STYLE_SYSTEM:\s*(.+)',
            'tailwind_config': r'TAILWIND_CONFIG:\s*(.+)',
            # Bugfinder markers
            'bugfinder_report': r'BUGFINDER_REPORT:\s*(.+)',
            'critical_issues': r'CRITICAL_ISSUES:\s*(\d+)',
            'high_priority': r'HIGH_PRIORITY:\s*(\d+)',
            # Bugfixer markers
            'bugfixer_report': r'BUGFIXER_REPORT:\s*(.+)',
            'issues_fixed': r'ISSUES_FIXED:\s*(\d+)',
            'issues_skipped': r'ISSUES_SKIPPED:\s*(\d+)',
            'all_critical_fixed': r'ALL_CRITICAL_FIXED:\s*(yes|no)',
            # Quick bugcheck markers
            'security_issues': r'SECURITY_ISSUES:\s*(\d+)',
            'type_errors': r'TYPE_ERRORS:\s*(\d+)',
            'error_handling_issues': r'ERROR_HANDLING_ISSUES:\s*(\d+)',
            'lint_errors': r'LINT_ERRORS:\s*(\d+)',
            # Codebase Context Builder markers
            'codebase_context': r'CODEBASE_CONTEXT:\s*(.+)',
            # Documentation Generator markers
            'documentation_added': r'DOCUMENTATION_ADDED:\s*(.+)',
            'files_documented': r'FILES_DOCUMENTED:\s*(\d+)',
            # Environment Provisioner markers
            'infra_config': r'INFRA_CONFIG:\s*(.+)',
            # Compliance Enforcer markers
            'compliance_report': r'COMPLIANCE_REPORT:\s*(.+)',
            'compliance_validation': r'COMPLIANCE_VALIDATION:\s*(pass|fail)',
            # Code Structure Validator markers
            'structure_report': r'STRUCTURE_REPORT:\s*(.+)',
            'structure_validation': r'STRUCTURE_VALIDATION:\s*(pass|fail)',
        }

        markers_found = False
        for key, pattern in markers.items():
            value = extract_output_marker(output, pattern)
            if value:
                self.state[key] = value
                print(f"   📌 {key}: {value}")
                markers_found = True

        # Persist state after extracting markers
        if markers_found:
            self._persist_state()

    async def run(self, task: str):
        """
        Start conversation with orchestrator agent.
        The agent has tools to control execution.
        """
        # Check for concurrent execution lock (PID-based)
        lock_file = self.project_dir / ".pipeline.lock"

        if not self._acquire_lock(lock_file):
            print("\n" + "="*70)
            print("  ⚠️  ANOTHER PIPELINE IS RUNNING IN THIS DIRECTORY")
            print("="*70)
            print("\nTo run multiple pipelines in parallel, use git worktrees:")
            print("  ./run-isolated.sh \"Your feature description\"")
            print("\nOr create a worktree manually:")
            print("  git worktree add /tmp/my-worktree main")
            print("  cd /tmp/my-worktree")
            print(f"  python {Path(__file__).absolute()} \"Your feature\"")
            print("\n" + "="*70 + "\n")
            sys.exit(1)

        # Store task in state for recovery
        self.state['task'] = task
        self.state['started_at'] = datetime.now().isoformat()
        self._persist_state()

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

        # Build orchestrator system prompt from template (no phase injection - phases loaded on-demand)
        orchestrator_template = (self.base_dir / "agents" / "pipeline-orchestrator.md").read_text()

        # Add project context
        system_prompt = orchestrator_template + f"""

## Project Context

Project Directory: {self.project_dir}
Task: {task}

Begin by analyzing the task and deciding which phases to run.
"""

        # Create orchestrator with tools
        options = ClaudeAgentOptions(
            system_prompt=system_prompt,
            model="claude-sonnet-4-5-20250929",
            cwd=self.project_dir,
            mcp_servers={
                "pipeline": mcp_server,
                # Ref.tools HTTP MCP disabled - SDK CLI doesn't support it yet
                # "ref": {
                #     "transport": "http",
                #     "url": "https://api.ref.tools/mcp",
                #     "headers": {
                #         "x-ref-api-key": REF_API_KEY
                #     }
                # }
            },
            allowed_tools=[
                "mcp__pipeline__run_agent",
                "mcp__pipeline__run_agents_parallel",
                "mcp__pipeline__run_agent_background",
                "mcp__pipeline__get_state",
                "mcp__pipeline__report_progress",
                "mcp__pipeline__update_progress",
                "mcp__pipeline__rollback_pipeline",
                "Read",  # Let orchestrator read files if needed
                "Bash",  # Let orchestrator check things if needed
            ],
            permission_mode="acceptEdits",
        )

        try:
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

        finally:
            # Release lock
            self._release_lock(lock_file)

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

    async def run_continuation(self):
        """
        Resume interrupted pipeline using continuation agent.
        Reads progress.txt and tests.json to determine next steps.
        """
        # Check for concurrent execution lock (PID-based)
        lock_file = self.project_dir / ".pipeline.lock"

        if not self._acquire_lock(lock_file):
            print("\n" + "="*70)
            print("  ⚠️  ANOTHER PIPELINE IS RUNNING IN THIS DIRECTORY")
            print("="*70)
            sys.exit(1)

        print("\n" + "="*70)
        print("  ATOMIC AGENTS TDD - CONTINUATION MODE")
        print("="*70)
        print(f"\nProject: {self.project_dir}")
        print("\nResuming from progress.txt...")
        print()

        # Run continuation agent directly via orchestrator
        result = await self.orch.run_agent(
            agent_path="agents/continuation.md",
            task_input=str(self.project_dir),
            cwd=self.project_dir,
        )

        print("\n" + "="*70)
        print("  CONTINUATION COMPLETE")
        print("="*70)

        # Release lock
        self._release_lock(lock_file)

        print()
        return result


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
        nargs='?',
        default=None,
        help="Task description (not needed for --continue)",
    )

    parser.add_argument(
        "--project-dir",
        type=Path,
        default=Path.cwd(),
        help="Project directory (default: current directory)",
    )

    parser.add_argument(
        "--continue",
        dest='continue_mode',
        action="store_true",
        help="Resume interrupted pipeline from progress.txt",
    )

    args = parser.parse_args()

    try:
        pipeline = AgentFirstPipeline(Path(__file__).parent, args.project_dir)

        if args.continue_mode:
            # Validate state files exist
            if not (args.project_dir / "progress.txt").exists():
                print("❌ Error: No progress.txt found. Cannot resume.")
                print("   Run without --continue to start a new pipeline.")
                sys.exit(1)

            specs_dir = args.project_dir / "specs"
            if not specs_dir.exists() or not list(specs_dir.glob("chore-*-tests.json")):
                print("❌ Error: No test file found. Cannot resume.")
                sys.exit(1)

            print("🔄 Resuming pipeline from progress.txt...")
            asyncio.run(pipeline.run_continuation())
        else:
            if not args.task:
                parser.error("task is required unless using --continue")
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
