# Requirements Analyzer Agent - Implementation Guide

## What Was Added

A new agent that runs BEFORE test generation to analyze project requirements and create a comprehensive technical architecture map.

## Files Created/Modified

### 1. New Agent: `agents/requirements-analyzer.md`
**Purpose:** Analyzes project specs and maps to concrete technical architecture

**What it does:**
- Identifies project type (analytics platform, e-commerce, CMS, etc.)
- Maps abstract features to concrete components
- Specifies infrastructure needs (database, cache, APIs, etc.)
- Defines API contracts with request/response shapes
- Identifies data models and schemas
- Creates dependency graph
- Assigns priority levels
- Outputs structured JSON architecture map

**Output:** `specs/chore-DDMMYY-HHMM-architecture.json`

**Example architecture map:**
```json
{
  "project_type": "data_analytics_platform",
  "infrastructure": [...],
  "api_routes": [...],
  "data_models": [...],
  "features": [...],
  "test_priorities": {...},
  "dependency_graph": {...}
}
```

### 2. Updated: `agents/pipeline-orchestrator.md`
**Added Phase 0.5:** Requirements Analysis

Now the orchestrator runs:
```
Phase 0: Git Setup
Phase 0.5: Requirements Analysis ← NEW!
Phase 0.6: Style Integration ← NEW!
Phase 1: Generate Tests (enhanced to use architecture map + style system)
Phase 2: Create Plan
Phase 3: Execution Planning
Phase 4: Implementation
...
```

### 3. Updated: `agents/test-generator.md`
**Enhanced with architecture map support**

New Step 1: Check for ARCHITECTURE_MAP in task description
- If present: Read architecture JSON and generate comprehensive tests
- If absent: Fall back to current behavior (infer from task description)

### 4. New Agent: `agents/style-integrator.md`
**Purpose:** Applies design system templates based on architecture

**What it does:**
- Reads architecture.json to determine project type
- Selects appropriate style template (analytics, saas, base)
- Generates STYLE.md with design tokens
- Creates tailwind.config.js with theme configuration
- Outputs STYLE_SYSTEM and TAILWIND_CONFIG markers

**Output:**
- `specs/style-DDMMYY-HHMM.md`
- `specs/tailwind-config-DDMMYY-HHMM.js`

### 5. Updated: `run.py`
**Added enhancements:**

1. New marker extraction: `architecture_map`, `style_system`, `tailwind_config`
2. Added `requirements-analyzer` and `style-integrator` to valid agents list

## How It Works

### Before (Current Behavior):
```
User Spec → test-generator (pattern matching) → minimal tests → code
```

### After (With Requirements Analyzer + Style Integration):
```
User Spec → requirements-analyzer (architecture reasoning)
          → architecture.json
          → style-integrator (design template selection)
          → STYLE.md + tailwind.config.js
          → test-generator (reads architecture + style)
          → comprehensive tests (functionality + design)
          → code with professional styling
```

## Usage Example

```bash
python3 run.py --project-dir ~/my-project "Create a data analytics platform..."
```

**Old flow:**
1. Git setup
2. Test-generator creates 8-10 basic UI tests
3. Implementer creates minimal code

**New flow:**
1. Git setup
2. **Requirements-analyzer creates architecture map** ← NEW!
3. **Style-integrator applies design system** ← NEW!
4. Test-generator reads map + style and creates 25-35 comprehensive tests covering:
   - Database schema
   - API endpoints
   - Data models
   - UI components
   - Integration tests
   - Style compliance ← NEW!
5. Implementer creates full implementation with professional styling

## What This Fixes

**Problem:** User gave comprehensive spec for analytics platform, but framework only created:
- Navigation component
- Empty homepage
- Map page skeleton
- Settings page

**Why:** Test-generator couldn't infer from vague requirements

**Solution:** Requirements-analyzer provides structured architecture map that includes:
- Database schema (PostgreSQL + Prisma)
- API routes (/api/ingest, /api/stats, /api/records)
- Data models (StopSearchRecord with all fields)
- Dashboard components (KPI cards, charts, filters)
- Map components (markers, clusters, popups)
- ETL pipeline components

Test-generator now has concrete requirements to test!

## Agent Communication Flow

```
orchestrator
  ↓ calls run_agent("requirements-analyzer.md", spec)
  ↓
requirements-analyzer
  ↓ outputs ARCHITECTURE_MAP: specs/architecture.json
  ↓
orchestrator extracts marker, stores in state
  ↓ calls run_agent("test-generator.md", spec + architecture_map)
  ↓
test-generator
  ↓ reads architecture.json
  ↓ generates comprehensive tests
  ↓ outputs TESTS_FILE: specs/tests.json
  ↓
orchestrator continues with rest of pipeline...
```

## State Management

`get_state()` now returns:
```python
{
  "branch": "feature/...",
  "architecture_map": "specs/chore-051225-1535-architecture.json",  # NEW!
  "tests_file": "specs/chore-051225-1535-tests.json",
  "plan_file": "specs/chore-051225-1535-plan.md"
}
```

## Key Design Principles

1. **Agents all the way down** - No code changes to orchestration logic
2. **File-based communication** - Architecture map is a JSON file
3. **Marker-based state** - Python automatically extracts ARCHITECTURE_MAP
4. **Backward compatible** - If no architecture map, test-generator works as before
5. **Single responsibility** - Requirements-analyzer only analyzes, doesn't test

## Testing The New Agent

Try it with a complex spec:

```bash
python3 run.py --project-dir ~/test-project "Create a data analytics platform with PostgreSQL database, ETL pipeline for UK Police API data, interactive dashboard with KPIs (total stops, arrest rate), map visualization with Mapbox, filtering by date/region/ethnicity, and CSV export functionality."
```

Expected output:
1. Git branch created
2. **Architecture map created** with ~15-20 components identified
3. Tests generated covering all components (~25-35 tests)
4. Full implementation of database, APIs, dashboard, map, filters

## Future Enhancements

Potential improvements to requirements-analyzer:

1. **Domain knowledge base** - Pre-defined patterns for common project types
2. **Coverage validation** - Warn if spec mentions features not in architecture map
3. **Cost estimation** - Predict implementation complexity based on architecture
4. **Conflict detection** - Identify incompatible requirements (e.g., "serverless" + "WebSockets")

## Rollback

If the requirements-analyzer causes issues, you can disable it by:

1. Comment out Phase 0.5 in `pipeline-orchestrator.md`
2. Remove `requirements-analyzer` from `valid_agents` in `run.py`
3. Revert `test-generator.md` to skip architecture map check

The system will work as before.
