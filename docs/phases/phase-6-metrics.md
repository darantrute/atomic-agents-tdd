# Phase 6: Generate Metrics

Use get_state() to get tests_file and plan_file

Call run_agent with metrics-reporter:
- agent_path: "agents/metrics-reporter.md"
- agent_input: "{tests_file} {plan_file}"

Python will extract REPORT_FILE marker automatically
