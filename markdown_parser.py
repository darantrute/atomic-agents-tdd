"""
Markdown Parser for Atomic Agents
===================================

Parses markdown files with YAML frontmatter and ##### section headers.
"""

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional

try:
    import frontmatter
except ImportError:
    print("Error: python-frontmatter not installed")
    print("Install with: pip install python-frontmatter")
    raise


@dataclass
class AgentConfig:
    """Parsed markdown agent configuration."""
    name: str
    description: str
    argument_hint: str
    model: str
    tools: List[str]
    purpose: str
    variables: Dict[str, str]
    instructions: List[str]
    workflow: str
    report_format: Optional[str]
    raw_content: str  # Full markdown content


def parse_agent_file(filepath: Path) -> AgentConfig:
    """
    Parse markdown file with YAML frontmatter and ## section headers.

    Args:
        filepath: Path to .md file

    Returns:
        AgentConfig with all sections parsed

    Example file structure:
        ---
        description: Agent purpose
        argument-hint: [param1] [param2]
        model: sonnet
        tools: [Read, Write, Bash]
        ---

        # Agent Name

        ## Purpose
        What this agent does...

        ## Variables
        INPUT: $1

        ## Instructions
        - Rule 1
        - Rule 2

        ## Workflow
        1. Step 1
        2. Step 2

        ## Report
        Output format...
    """
    if not filepath.exists():
        raise FileNotFoundError(f"Agent file not found: {filepath}")

    # Parse frontmatter + content
    with open(filepath, 'r', encoding='utf-8') as f:
        post = frontmatter.load(f)

    metadata = post.metadata
    content = post.content

    # Extract agent name from filename
    name = filepath.stem

    # Parse sections using ## headers
    sections = _parse_sections(content)

    # Parse variables section
    variables = _parse_variables(sections.get('Variables', ''))

    # Parse instructions section
    instructions = _parse_instructions(sections.get('Instructions', ''))

    return AgentConfig(
        name=name,
        description=metadata.get('description', ''),
        argument_hint=metadata.get('argument-hint', ''),
        model=metadata.get('model', 'sonnet'),
        tools=metadata.get('tools', []),
        purpose=sections.get('Purpose', ''),
        variables=variables,
        instructions=instructions,
        workflow=sections.get('Workflow', ''),
        report_format=sections.get('Report'),
        raw_content=content,
    )


def _parse_sections(content: str) -> Dict[str, str]:
    """
    Parse content into sections based on ## headers.

    Returns dict like:
        {
            'Purpose': 'This agent does...',
            'Variables': 'INPUT: $1\nOUTPUT: $2',
            'Workflow': '1. Step 1\n2. Step 2',
        }
    """
    sections = {}
    current_section = None
    current_content = []

    for line in content.split('\n'):
        # Check for ## header (but not # or ###)
        if line.startswith('## ') and not line.startswith('### '):
            # Save previous section
            if current_section:
                sections[current_section] = '\n'.join(current_content).strip()

            # Start new section
            current_section = line[3:].strip()
            current_content = []
        else:
            # Add line to current section
            if current_section:
                current_content.append(line)

    # Save last section
    if current_section:
        sections[current_section] = '\n'.join(current_content).strip()

    return sections


def _parse_variables(variables_section: str) -> Dict[str, str]:
    """
    Parse variables section into dict.

    Input:
        INPUT: $1
        OUTPUT: $2
        STATIC: "hardcoded value"

    Returns:
        {'INPUT': '$1', 'OUTPUT': '$2', 'STATIC': '"hardcoded value"'}
    """
    variables = {}

    for line in variables_section.split('\n'):
        line = line.strip()
        if ':' in line:
            key, value = line.split(':', 1)
            variables[key.strip()] = value.strip()

    return variables


def _parse_instructions(instructions_section: str) -> List[str]:
    """
    Parse instructions section into list of rules.

    Input:
        - Rule 1
        - Rule 2
        - Rule 3

    Returns:
        ['Rule 1', 'Rule 2', 'Rule 3']
    """
    instructions = []

    for line in instructions_section.split('\n'):
        line = line.strip()
        if line.startswith('- '):
            instructions.append(line[2:].strip())

    return instructions


def extract_output_marker(text: str, pattern: str) -> Optional[str]:
    """
    Extract output marker from agent response.

    Args:
        text: Agent response text
        pattern: Regex pattern (e.g., "PLAN_FILE: (.+)")

    Returns:
        Extracted value or None

    Example:
        text = "Here's the plan...\nPLAN_FILE: specs/chore-123.md"
        pattern = "PLAN_FILE: (.+)"
        returns: "specs/chore-123.md"
    """
    match = re.search(pattern, text, re.MULTILINE)
    if match:
        return match.group(1).strip()
    return None


def interpolate_variables(template: str, state: Dict[str, str]) -> str:
    """
    Replace {variables} in template with values from state.

    Args:
        template: String with {variable} placeholders
        state: Dict of variable values

    Returns:
        Template with variables replaced

    Example:
        template = "Run agent with {input_file}"
        state = {'input_file': 'test.json'}
        returns: "Run agent with test.json"
    """
    result = template

    for key, value in state.items():
        placeholder = f'{{{key}}}'
        result = result.replace(placeholder, str(value))

    return result


if __name__ == '__main__':
    # Test parser
    test_file = Path(__file__).parent / 'agents' / 'test-generator.md'

    if test_file.exists():
        print(f"Testing parser with: {test_file}\n")

        config = parse_agent_file(test_file)

        print(f"Name: {config.name}")
        print(f"Description: {config.description}")
        print(f"Model: {config.model}")
        print(f"Tools: {config.tools}")
        print(f"\nVariables:")
        for key, value in config.variables.items():
            print(f"  {key}: {value}")
        print(f"\nInstructions: {len(config.instructions)} rules")
        print(f"Workflow length: {len(config.workflow)} chars")

        # Test output extraction
        test_output = "Here's the result...\nTESTS_FILE: specs/chore-041225-tests.json"
        extracted = extract_output_marker(test_output, r"TESTS_FILE: (.+)")
        print(f"\nTest extraction: {extracted}")
    else:
        print(f"Test file not found: {test_file}")
