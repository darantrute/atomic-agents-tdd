# Phase 1.5: Completeness Validation

**CRITICAL QUALITY GATE: Prevents the "70% missing features" problem**

## Purpose

Validate that generated tests comprehensively cover the original specification BEFORE planning and implementation begin. This phase catches gaps early when they're cheap to fix.

## When to Run This Phase

**ALWAYS run if:**
- Original specification document exists (user provided detailed requirements)
- Project has ≥3 user personas (multi-portal architecture)
- Specification mentions ≥10 features or pages
- This is a greenfield project (building from scratch)

**SKIP if:**
- Simple bug fix or small enhancement (<5 components)
- No specification document (requirements inferred from task description)
- Adding to existing well-tested codebase

## Prerequisites

- ✅ Phase 1 completed (tests generated)
- ✅ Tests file exists: `specs/chore-*.json`
- ✅ Architecture map exists: `specs/chore-*-architecture.json`
- ✅ **Original specification document available** (critical)

## Workflow

### Step 1: Get State

Use `get_state()` to retrieve:
- `tests_file` (from Phase 1)
- `architecture_map` (from Phase 0.5)

### Step 2: Identify Specification Document

The specification document should be provided by the user at the start of the pipeline. Common locations:
- `docs/specification.md`
- `docs/requirements.md`
- `docs/project-spec.md`
- `README.md` (for smaller projects)
- User-provided path

**If you don't have the spec path:**
1. Check if user provided it in the initial task description
2. Check common locations using Read tool
3. If not found, ASK user for specification path
4. If user confirms no spec exists, SKIP this phase

### Step 3: Run Completeness Validator

Call run_agent with completeness-validator:
- Use get_state() to get tests_file and architecture_map paths
- Pass specification path, architecture map path, and tests file path
- Format: `{spec_path} {architecture_map_path} {tests_file_path}`

Example:
```
Tool: run_agent
agent_path: "agents/completeness-validator.md"
agent_input: "docs/project-spec.md specs/chore-051225-1535-architecture.json specs/chore-051225-1536-tests.json"
```

### Step 4: Check Validation Results

The completeness-validator will output markers:
```
COMPLETENESS_REPORT: specs/completeness-report-DDMMYY-HHMM.md
VALIDATION_STATUS: {pass|fail}
COVERAGE_PERCENTAGE: {percentage}
RECOMMENDATION: {block|warn|proceed}
MISSING_FEATURES_COUNT: {count}
MISSING_ROUTES_COUNT: {count}
MISSING_PERSONAS_COUNT: {count}
```

Python will automatically extract these markers into state.

### Step 5: Decision Point

Based on `VALIDATION_STATUS` and `RECOMMENDATION`:

**If RECOMMENDATION = "block" (coverage <80%):**
1. Report failure to user using report_progress:
   ```
   Tool: report_progress
   message: "⚠️  BLOCKED: Test coverage only {percentage}% - {missing_features_count} missing features. See {completeness_report} for details."
   ```

2. Options:
   - **Option A (Recommended):** Stop pipeline, regenerate tests
     ```
     Tool: report_progress
     message: "Pipeline stopped. Please review completeness report and either: (1) Regenerate tests with Phase 1, or (2) Adjust specification scope."
     ```
     STOP HERE. Pipeline should not continue.

   - **Option B (Not Recommended):** Continue with partial scope
     ```
     Tool: report_progress
     message: "⚠️  WARNING: Continuing with {percentage}% coverage. {missing_features_count} features will NOT be implemented."
     ```
     Proceed to Phase 2, but user is warned.

**If RECOMMENDATION = "warn" (coverage 80-90%):**
1. Report to user:
   ```
   Tool: report_progress
   message: "Test coverage: {percentage}% - Good coverage with minor gaps. See {completeness_report} for details."
   ```

2. Continue to Phase 2 (proceed with caution)

**If RECOMMENDATION = "proceed" (coverage ≥90%):**
1. Report success:
   ```
   Tool: report_progress
   message: "✅ Test coverage validated: {percentage}% - Excellent coverage. Proceeding to planning phase."
   ```

2. Continue to Phase 2 confidently

### Step 6: Report Progress

Always report the outcome:
```
Tool: report_progress
message: "Phase 1.5 complete - Completeness validation: {status}"
```

## Example: Full Phase 1.5 Execution

```
# Step 1: Get state
Tool: get_state
Returns:
  tests_file: specs/chore-051225-1536-tests.json
  architecture_map: specs/chore-051225-1535-architecture.json

# Step 2: Run validator
Tool: run_agent
agent_path: "agents/completeness-validator.md"
agent_input: "docs/police-review-spec.md specs/chore-051225-1535-architecture.json specs/chore-051225-1536-tests.json"

# Step 3: Check results (extracted automatically)
State markers:
  VALIDATION_STATUS: fail
  COVERAGE_PERCENTAGE: 19.2
  RECOMMENDATION: block
  MISSING_FEATURES_COUNT: 24
  MISSING_PERSONAS_COUNT: 4

# Step 4: Block pipeline
Tool: report_progress
message: "⚠️  BLOCKED: Test coverage only 19.2% - 24 missing features, 4 missing personas. Pipeline stopped. Review specs/completeness-report-051225-1545.md"

# STOP - Do not proceed to Phase 2
```

## Example: Successful Validation

```
# Step 1: Get state
Tool: get_state
Returns:
  tests_file: specs/chore-051225-1536-tests.json
  architecture_map: specs/chore-051225-1535-architecture.json

# Step 2: Run validator
Tool: run_agent
agent_path: "agents/completeness-validator.md"
agent_input: "docs/ecommerce-spec.md specs/chore-051225-1535-architecture.json specs/chore-051225-1536-tests.json"

# Step 3: Check results
State markers:
  VALIDATION_STATUS: pass
  COVERAGE_PERCENTAGE: 92.5
  RECOMMENDATION: proceed
  MISSING_FEATURES_COUNT: 3

# Step 4: Proceed
Tool: report_progress
message: "✅ Test coverage validated: 92.5% - Excellent coverage. Proceeding to planning phase."

# Continue to Phase 2
```

## What Completeness Validator Checks

The validator compares specification to generated tests across 5 dimensions:

1. **User Persona Coverage**
   - All user roles mentioned in spec
   - Each persona should have tests covering their workflows
   - Example: Sergeant, Inspector, Admin, Panel Member, Officer

2. **User Journey Coverage**
   - All workflows/scenarios described in spec
   - Each journey = sequence of user actions
   - Example: "Morning Review Queue," "Pattern Investigation"

3. **URL Route Coverage**
   - All pages/routes mentioned in spec
   - Example: /, /analytics, /search, /reports, /admin

4. **Feature Coverage**
   - All capabilities mentioned in spec
   - Example: Search, Export, Analytics, Notifications

5. **Data Entity Coverage**
   - All business objects mentioned in spec
   - Example: User, Encounter, Report, Review, Pattern

## Coverage Thresholds

| Coverage | Status | Action |
|----------|--------|--------|
| ≥90% | ✅ PASS | Proceed confidently to Phase 2 |
| 80-89% | ⚠️ WARN | Proceed with caution, minor gaps acceptable |
| <80% | 🔴 BLOCK | Stop pipeline, regenerate tests or adjust scope |

**Special cases:**
- Missing CRITICAL features (auth, core workflow) → Block regardless of percentage
- Missing >50% of personas → Block (multi-portal architecture incomplete)
- Missing security/compliance features → Block (regulatory risk)

## Common Gap Patterns

### Pattern 1: Multi-Portal Architecture Missed
**Symptom:** Tests cover 1 persona, spec describes 5 personas
**Root cause:** Requirements analyzer treated as single portal
**Fix:** Re-run Phase 0.5 with emphasis on multi-portal detection

### Pattern 2: Analytics Infrastructure Missed
**Symptom:** Tests cover CRUD, spec describes dashboards/charts/trends
**Root cause:** Requirements analyzer missed analytics keywords
**Fix:** Re-run Phase 0.5 with analytics detection enabled

### Pattern 3: Search Functionality Missed
**Symptom:** Tests cover display, spec mentions search 12 times
**Root cause:** Search treated as optional, not core feature
**Fix:** Re-run Phase 0.5 with search detection enabled

### Pattern 4: Reporting/Export Missed
**Symptom:** Tests cover UI, spec describes PDF export, evidence packs
**Root cause:** Export treated as enhancement, not core requirement
**Fix:** Re-run Phase 0.5 with reporting detection enabled

## Integration with Pipeline

**Pipeline Flow:**
```
Phase 0: Git Setup
  ↓
Phase 0.5: Requirements Analysis → architecture.json
  ↓
Phase 1: Test Generation → tests.json
  ↓
Phase 1.5: Completeness Validation (NEW) → validation report
  ↓
  If BLOCK → STOP (regenerate tests)
  If WARN → Continue with notice
  If PASS → Continue confidently
  ↓
Phase 2: Planning
  ↓
Phase 3: Execution Strategy
  ↓
Phase 4+: Implementation
```

## Success Criteria

- ✅ Completeness validator ran successfully
- ✅ Validation report generated
- ✅ Coverage metrics calculated for all 5 dimensions
- ✅ Gaps identified and listed
- ✅ Decision made: block/warn/proceed
- ✅ User informed of validation results

## Failure Modes to Avoid

- ❌ Skipping this phase for large projects (leads to 70% missing features)
- ❌ Ignoring BLOCK recommendation (implementing incomplete spec)
- ❌ Not providing specification path (validator can't run)
- ❌ Proceeding with <80% coverage without user consent
- ❌ Not reading the completeness report (missing context on gaps)

## Benefits of This Phase

1. **Catches gaps early** - Before planning and implementation (cheap to fix)
2. **Prevents wasted effort** - Don't implement wrong thing
3. **Builds confidence** - High coverage = comprehensive implementation
4. **Documents scope** - Clear record of what WILL and WON'T be built
5. **Enables informed decisions** - User can adjust scope before committing

## Cost-Benefit Analysis

**Cost:** +2 minutes, +$0.05
**Benefit:** Prevents 70% missing features (saves hours of rework)
**ROI:** 100-1000x (catching one major gap justifies the phase)

---

**Remember:** This phase is your insurance against incomplete implementations. Better to spend 2 minutes validating than 4 hours implementing 30% of the requirements.
