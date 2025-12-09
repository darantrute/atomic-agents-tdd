# Phase 0.8: Infrastructure Provisioning

Call run_agent with environment-provisioner to auto-generate infrastructure configs:
- agent_path: "agents/environment-provisioner.md"
- agent_input: "{architecture_map_path} development"
- Python will automatically extract INFRA_CONFIG marker
- Use get_state() to retrieve infra_config path

**What it generates:**
- docker-compose.yml (with custom ports, volumes, networks)
- .env.development, .env.staging, .env.production
- specs/infra-config-DDMMYY-HHMM.json (metadata)

Example:
```
Tool: run_agent
agent_path: "agents/environment-provisioner.md"
agent_input: "specs/chore-051225-1535-architecture.json development"
```

Call report_progress:
- message: "Generated infrastructure configurations (docker-compose, .env files)"

**Why this matters:**
- Zero manual docker-compose editing
- Custom ports (e.g., 5434 for PostgreSQL on Windows)
- Environment-specific configs (dev/staging/prod)
- Secrets as placeholders (never hardcoded)

**IMPORTANT:** This phase only runs if architecture map specifies infrastructure requirements.
If no infrastructure section in architecture map, skip this phase.
