"""
Atomic Markdown Orchestrator
=============================

Executes atomic markdown agents and TDD pipelines.
"""

import asyncio
import json
import random
import re
from functools import wraps
from pathlib import Path
from typing import Dict, Any, List, Optional

from claude_agent_sdk import ClaudeSDKClient, ClaudeAgentOptions

from markdown_parser import (
    parse_agent_file,
    extract_output_marker,
    interpolate_variables,
)


def with_retry(max_attempts: int = 3, base_delay: float = 2.0, max_delay: float = 30.0):
    """
    Retry decorator with exponential backoff and jitter.
    
    Args:
        max_attempts: Maximum number of retry attempts
        base_delay: Initial delay in seconds
        max_delay: Maximum delay cap in seconds
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            last_exception = None
            for attempt in range(max_attempts):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    error_str = str(e).lower()
                    
                    # Don't retry on certain errors
                    non_retryable = ['invalid', 'not found', 'permission', 'authentication']
                    if any(nr in error_str for nr in non_retryable):
                        print(f"❌ Non-retryable error: {e}")
                        raise
                    
                    if attempt < max_attempts - 1:
                        # Exponential backoff with jitter
                        delay = min(base_delay * (2 ** attempt) + random.uniform(0, 1), max_delay)
                        print(f"\n⚠️  Attempt {attempt + 1}/{max_attempts} failed: {e}")
                        print(f"    Retrying in {delay:.1f}s...")
                        await asyncio.sleep(delay)
                    else:
                        print(f"\n❌ All {max_attempts} attempts failed. Last error: {e}")
            raise last_exception
        return wrapper
    return decorator


class MarkdownOrchestrator:
    """
    Executes atomic markdown agents and orchestrates pipelines.

    Key features:
    - Fresh context per agent (no state carried between agents)
    - State passing via output markers and files
    - Support for sequential and parallel execution
    """

    def __init__(self, base_dir: Path, project_dir: Path):
        """
        Args:
            base_dir: Directory containing agents/ and orchestrations/
            project_dir: Working directory for agent execution
        """
        self.base_dir = base_dir
        self.project_dir = project_dir
        self.state: Dict[str, Any] = {}  # Stores extracted values

    @with_retry(max_attempts=3, base_delay=2.0, max_delay=30.0)
    async def run_agent(
        self,
        agent_path: str,
        task_input: str,
        cwd: Optional[Path] = None,
    ) -> str:
        """
        Execute a single atomic agent with fresh context.
        
        Includes automatic retry with exponential backoff for transient failures.

        Args:
            agent_path: Relative path like "agents/test-generator.md"
            task_input: The input/prompt for the agent
            cwd: Working directory (defaults to self.project_dir)

        Returns:
            Agent's text response

        Example:
            result = await orchestrator.run_agent(
                "agents/test-generator.md",
                "Update Prisma dependencies",
                cwd=Path("/home/user/project")
            )
        """
        if cwd is None:
            cwd = self.project_dir

        # Parse agent markdown
        agent_file = self.base_dir / agent_path
        config = parse_agent_file(agent_file)

        print(f"\n{'='*70}")
        print(f"  Running Agent: {config.name}")
        print(f"  Model: {config.model}")
        print(f"  Tools: {', '.join(config.tools)}")
        print(f"  Working Directory: {cwd.resolve()}")

        # Verify git repo if agent has Bash tool
        if 'Bash' in config.tools:
            git_dir = cwd / '.git'
            if git_dir.exists():
                print(f"  Git Operations: ✓ Will run in project directory")
            else:
                print(f"  Git Operations: ⚠ No .git found (git commands may fail)")

        print(f"{'='*70}\n")

        # Build system prompt from agent config
        system_prompt = self._build_system_prompt(config)

        # Build user prompt: purpose + workflow + project directory + task input
        user_prompt = f"{config.purpose}\n\n{config.workflow}\n\n## Project Directory\nWrite all output files to: {cwd.resolve()}\n\n## Task Input\n{task_input}"

        # Create Claude SDK client (fresh context)
        client = ClaudeSDKClient(
            options=ClaudeAgentOptions(
                model=self._resolve_model(config.model),
                system_prompt=system_prompt,
                allowed_tools=config.tools,
                cwd=str(cwd.resolve()),
                max_turns=200,
            )
        )

        # Execute agent
        print(f"Sending prompt to {config.name}...\n")

        response_text = ""
        async with client:
            await client.query(user_prompt)

            # Collect response
            async for msg in client.receive_response():
                msg_type = type(msg).__name__

                if msg_type == "AssistantMessage" and hasattr(msg, "content"):
                    for block in msg.content:
                        block_type = type(block).__name__

                        if block_type == "TextBlock" and hasattr(block, "text"):
                            response_text += block.text
                            print(block.text, end="", flush=True)
                        elif block_type == "ToolUseBlock" and hasattr(block, "name"):
                            print(f"\n[Tool: {block.name}]", flush=True)

        print(f"\n\n{'='*70}")
        print(f"  Agent Complete: {config.name}")
        print(f"{'='*70}\n")

        return response_text

    def _build_system_prompt(self, config) -> str:
        """Build system prompt from agent config."""
        parts = [
            f"# {config.name}",
            "",
            config.purpose,
            "",
            "## Instructions",
        ]

        for instruction in config.instructions:
            parts.append(f"- {instruction}")

        return "\n".join(parts)

    def _resolve_model(self, model: str) -> str:
        """Resolve model aliases to full model names."""
        model_map = {
            'sonnet': 'claude-sonnet-4-5-20250929',
            'opus': 'claude-opus-4-20250514',
            'haiku': 'claude-3-5-haiku-20241022',
        }

        return model_map.get(model.lower(), model)

    async def execute_pipeline(
        self,
        pipeline_path: str,
        task: str,
        cwd: Optional[Path] = None,
    ) -> Dict[str, Any]:
        """
        Execute a pipeline that orchestrates multiple agents.

        Args:
            pipeline_path: Path like "orchestrations/chore-tdd-pipeline.md"
            task: The task description
            cwd: Working directory

        Returns:
            Dict with results from each step

        Note:
            This is a simplified implementation. Full implementation would
            parse the pipeline workflow and execute steps dynamically.
        """
        if cwd is None:
            cwd = self.project_dir

        print(f"\n{'#'*70}")
        print(f"  PIPELINE: {pipeline_path}")
        print(f"  Task: {task}")
        print(f"{'#'*70}\n")

        # Parse pipeline markdown
        pipeline_file = self.base_dir / pipeline_path
        config = parse_agent_file(pipeline_file)

        # For now, just print the pipeline workflow
        # Full implementation would parse and execute each step
        print("Pipeline Workflow:")
        print(config.workflow)
        print("\nNote: Full pipeline execution not yet implemented.")
        print("This would parse the workflow and execute each agent in sequence.\n")

        return {
            'status': 'pending_implementation',
            'pipeline': pipeline_path,
            'task': task,
        }


async def main():
    """Test the orchestrator."""
    base_dir = Path(__file__).parent
    project_dir = Path.cwd()

    orchestrator = MarkdownOrchestrator(base_dir, project_dir)

    # Example: Run test generator agent
    print("Testing single agent execution...")

    result = await orchestrator.run_agent(
        agent_path="agents/test-generator.md",
        task_input="Update Prisma to latest version and ensure all migrations work",
        cwd=project_dir,
    )

    # Extract output marker
    tests_file = extract_output_marker(result, r"TESTS_FILE: (.+)")
    if tests_file:
        print(f"\n✓ Tests generated: {tests_file}")
    else:
        print("\n✗ No TESTS_FILE marker found in output")


if __name__ == '__main__':
    asyncio.run(main())
