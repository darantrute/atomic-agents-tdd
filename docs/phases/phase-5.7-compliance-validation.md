# Phase 5.7: Compliance Validation

Use get_state() to get base_commit, architecture_map, and changed files:

Call run_agent with compliance-enforcer to validate GDPR:
- agent_path: "agents/compliance-enforcer.md"
- agent_input: "{changed_files} {architecture_map_path}"

**What it validates:**
- Consent collection before data submission (CRITICAL)
- Right to deletion (soft deletes) (CRITICAL)
- Audit logging on PII access (CRITICAL)
- Data minimization (WARNING)
- Encryption at rest (WARNING)
- Third-party data sharing (WARNING)

Python will extract markers:
- COMPLIANCE_REPORT: {report_path}
- COMPLIANCE_VALIDATION: {pass|fail}

Example:
```
Tool: run_agent
agent_path: "agents/compliance-enforcer.md"
agent_input: "frontend/src/pages/RegistrationPage.tsx backend/src/routes/officers.ts specs/chore-051225-1535-architecture.json"
```

**If COMPLIANCE_VALIDATION: fail:**
- BLOCK deployment
- Display COMPLIANCE_REPORT path
- Instruct user to fix critical violations
- EXIT pipeline with error

**If COMPLIANCE_VALIDATION: pass:**
- Proceed to Phase 6

Call report_progress:
- message: "GDPR compliance validated - all checks passed"
