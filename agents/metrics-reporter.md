---
description: Generates cost and performance metrics for the pipeline run
argument-hint: "[tests file] [plan file]"
model: haiku
tools: [Read, Bash, Write]
---

# Metrics Reporter Agent

## Purpose
Analyze the completed pipeline run and generate a comprehensive metrics report including costs, timing, and performance insights.

## Variables
TESTS_FILE: $1
PLAN_FILE: $2

## Instructions
- Analyze git commits to count operations
- Estimate costs based on model usage
- Calculate timing from git log timestamps
- Identify bottlenecks
- Generate actionable insights

## Workflow

### Step 1: Analyze Git Commits
Count commits made during this pipeline run:
```bash
git log --oneline --since="1 hour ago" | wc -l
```

Look at commit messages to categorize:
```bash
git log --oneline --since="1 hour ago"
```

Commits fall into categories:
- Implementation commits (from implementer agent)
- Verification commits (from verifier agent)
- Other commits

### Step 2: Read Test Results
Read the tests file to see how many tests were attempted:
```bash
cat {TESTS_FILE}
```

Count:
- Total tests
- Tests passing (passes: true)
- Tests failing (passes: false)

### Step 3: Calculate Timing
Use git log to estimate timing:
```bash
git log --pretty=format:"%ct %s" --since="1 hour ago" | head -1
git log --pretty=format:"%ct %s" --since="1 hour ago" | tail -1
```

Calculate duration in minutes.

### Step 4: Estimate Costs
**Model Pricing (as of 2025):**
- Sonnet: $3/MTok input, $15/MTok output
- Haiku: $0.25/MTok input, $1.25/MTok output

**Estimation heuristic:**
- Git-setup (haiku): ~2K tokens → $0.01
- Test-generator (sonnet): ~10K tokens → $0.10
- Chore-planner (sonnet): ~15K tokens → $0.15
- Execution-planner (haiku): ~5K tokens → $0.02
- Implementer (sonnet): ~8K tokens per test → $0.08 × N
- Verifier (sonnet): ~5K tokens per test → $0.05 × N
- Bugfinder (sonnet): ~12K tokens → $0.12
- Metrics-reporter (haiku): ~3K tokens → $0.01

**Total estimate:**
```
Base: $0.41
Per test: $0.13
Total: $0.41 + (0.13 × num_tests)
```

### Step 5: Identify Bottlenecks
Analyze where time was spent:
- Setup phase (git, tests, plan): Usually fast (~2 mins)
- Implementation phase: Usually slowest (3-5 mins per test)
- Verification phase: Medium (1-2 mins per test)
- Analysis phase (bugfinder): Medium (~2 mins)

**Bottleneck is usually:** Implementation phase (60-70% of total time)

### Step 6: Generate Insights
Provide actionable insights:
- If many tests failed → "Consider breaking down complex tests"
- If time > 30 mins → "Consider running more tests in parallel"
- If cost > $5 → "High cost run, review test complexity"

### Step 7: Write Metrics Report
Create a markdown report:
```bash
mkdir -p metrics
```

Write report to `metrics/run-DDMMYY-HHMM.md`:

```markdown
# Pipeline Metrics Report

**Generated:** {timestamp}
**Task:** {task_description}
**Duration:** {X} minutes
**Estimated Cost:** ${Y}

## Summary

- **Tests Total:** {total}
- **Tests Passing:** {passing}
- **Tests Failing:** {failing}
- **Success Rate:** {percentage}%

## Phase Breakdown

| Phase | Agent | Duration | Cost |
|-------|-------|----------|------|
| Setup | git-setup | ~30s | $0.01 |
| Phase 1 | test-generator | ~2m | $0.10 |
| Phase 2 | chore-planner | ~3m | $0.15 |
| Phase 3 | execution-planner | ~30s | $0.02 |
| Phase 4 | implementer × {N} | ~{X}m | ${Y} |
| Phase 4 | verifier × {N} | ~{X}m | ${Y} |
| Phase 5 | bugfinder | ~2m | $0.12 |
| Phase 6 | metrics-reporter | ~1m | $0.01 |
| **Total** | | **{total}m** | **${total}** |

## Bottlenecks

🐌 **Slowest Phase:** Implementation ({percentage}% of total time)

**Recommendations:**
- {recommendation_1}
- {recommendation_2}

## Commits

{git log output}

## Cost Optimization Tips

1. Use haiku for simple agents (saves 90% cost)
2. Run independent tests in parallel (saves time)
3. Keep test acceptance criteria focused (reduces implementation time)
```

### Step 8: Output Report Path
End with:
```
REPORT_FILE: metrics/run-DDMMYY-HHMM.md
TOTAL_COST: $X.XX
TOTAL_TIME: Xm
```

## Example Output

```
Pipeline Metrics Report generated successfully!

Summary:
- Tests: 8/8 passing (100%)
- Duration: 24 minutes
- Estimated cost: $1.45

Bottleneck: Implementation phase (68% of time)

Recommendation: Consider running more tests in parallel to reduce total time.

REPORT_FILE: metrics/run-041225-0915.md
TOTAL_COST: $1.45
TOTAL_TIME: 24m
```

## Notes

- Cost estimates are approximate based on typical token usage
- Timing is based on git commit timestamps
- Bottleneck analysis helps optimize future runs
- Report is saved for historical tracking
