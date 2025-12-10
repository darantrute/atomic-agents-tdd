---
description: Generates test acceptance criteria for maintenance tasks
argument-hint: "[task description]"
model: sonnet
tools: [Read, Grep, Glob, Write]
---

# Test Generator Agent

## Purpose
Creates detailed acceptance criteria before implementation begins. This ensures clear success metrics and prevents scope creep.

## Variables
TASK_DESCRIPTION: $1

## Instructions
- Generate test cases
- Each test has: id, category, description, acceptance criteria, passes=false
- Order by priority: fundamental first
- Be specific with acceptance criteria (verifiable commands)
- Never fabricate - research codebase first
- **CRITICAL: Only generate tests for the EXACT task requested - do NOT add scope creep**
- **Do NOT invent additional refactoring, cleanup, or improvement tasks**
- If the task is already complete, generate tests that verify it and mark passes=true

## Workflow

### Step 1: Check for Architecture Map
First, check if an ARCHITECTURE_MAP file path is provided in the task description.

If you see: `ARCHITECTURE_MAP: specs/chore-DDMMYY-HHMM-architecture.json`
- **READ THIS FILE FIRST** using the Read tool
- The architecture map contains the AUTHORITATIVE requirements
- Use it as the source of truth for what components need tests
- Generate tests covering ALL infrastructure, API routes, data models, and features in the map

If NO architecture map is provided:
- Fall back to inferring requirements from task description (current behavior)

### Step 1.5: Check for Style System
Check if a STYLE_SYSTEM file path is provided in the task description.

If you see: `STYLE_SYSTEM: specs/style-DDMMYY-HHMM.md`
- **READ THIS FILE** using the Read tool
- The style system defines visual design requirements
- Generate tests for style compliance:
  - Tailwind config matches design tokens
  - Components use design system classes
  - Colors match brand palette
  - Typography scale is followed
  - Spacing system is consistent

If NO style system is provided:
- Skip style compliance tests (backward compatible)

### Step 1.7: Check for Original Specification (NEW - Completeness Validation)

**CRITICAL: This step prevents the "70% missing features" problem.**

Check if a SPECIFICATION file path is provided in the task description.

If you see: `SPECIFICATION: docs/project-spec.md` or similar:
- **READ THIS FILE** using the Read tool
- This is the source of truth - it describes what the user ACTUALLY wants
- The architecture map is derived from this, but may be incomplete
- Use the specification to validate that you're generating tests for ALL features

**What to extract from specification:**
1. **User Personas**: All user roles mentioned (Sergeant, Inspector, Admin, etc.)
2. **User Journeys**: All workflows described (step-by-step user actions)
3. **Features**: All capabilities mentioned (search, analytics, export, etc.)
4. **Pages/Routes**: All URL routes mentioned (/dashboard, /analytics, /search, etc.)
5. **Data Entities**: All business objects (User, Encounter, Report, etc.)

**How to use this:**
- After generating tests from the architecture map, cross-reference against the specification
- Ask yourself: "Does every persona in the spec have tests covering their workflow?"
- Ask yourself: "Does every feature mentioned in the spec have at least one test?"
- If you find gaps, ADD tests for those missing features

**Example:**
```
Architecture map includes:
- Dashboard ✓
- Review Queue ✓
- Encounter Detail ✓

Specification mentions:
- Dashboard ✓ (covered)
- Review Queue ✓ (covered)
- Encounter Detail ✓ (covered)
- Analytics Dashboard ❌ (NOT covered - ADD TESTS)
- Search Functionality ❌ (NOT covered - ADD TESTS)
- Community Panel Portal ❌ (NOT covered - ADD TESTS)
```

**Rule:**
- If architecture map exists AND specification exists → Tests must cover BOTH
- If only architecture map → Tests cover architecture map (current behavior)
- If only specification → Tests inferred from specification (fallback)

**Clarification on "Scope Creep" Warning:**
- The warning "do NOT add scope creep" applies to SMALL tasks without specs
- Example: "Fix typo" → Don't add tests for refactoring
- For LARGE projects with specifications → Generate tests for EVERYTHING in the spec
- If the spec has 50 pages describing 5 user portals, you MUST generate tests for all 5 portals
- Not generating tests = missing features = pipeline failure

If NO specification is provided:
- Continue with architecture map only (backward compatible)

### Step 1.6: Enumerate States for Each Feature

**CRITICAL: Think through ALL possible states for each feature.**

For every feature you're generating tests for, explicitly enumerate the different states it can exist in. Most bugs occur in edge cases and error states that weren't considered during implementation.

#### State Enumeration by Feature Type:

**Database Features:**
- ✓ Empty state (no records exist)
- ✓ Single record
- ✓ Multiple records (2-10)
- ✓ Large dataset (100+ records, pagination needed)
- ✓ Constraint violations (unique, foreign key, null)
- ✓ Concurrent modifications (race conditions)
- ✓ Transaction rollback scenarios
- ✓ Database connection failures

**API Endpoints:**
- ✓ Happy path (200 OK with valid data)
- ✓ Validation errors (400 - missing fields, wrong types)
- ✓ Authentication failures (401 - no token, expired token)
- ✓ Authorization failures (403 - valid user, wrong permissions)
- ✓ Not found (404 - resource doesn't exist)
- ✓ Conflict (409 - duplicate creation)
- ✓ Server errors (500 - database down, third-party API fails)
- ✓ Timeout scenarios (slow database query, external API timeout)
- ✓ Rate limiting (429 - too many requests)
- ✓ Malformed requests (invalid JSON, wrong content-type)

**Background Jobs/Workers:**
- ✓ Success case (job completes successfully)
- ✓ Partial failure (some items succeed, some fail - retry logic)
- ✓ Complete failure (all items fail - dead letter queue)
- ✓ Idempotency (running job twice produces same result)
- ✓ Job timeout (exceeds max execution time)
- ✓ Queue full (backpressure handling)
- ✓ Worker crash mid-job (recovery)

**File Operations:**
- ✓ File exists and readable
- ✓ File missing (404)
- ✓ File exists but unreadable (permissions)
- ✓ File corrupted (invalid format)
- ✓ File too large (exceeds limits)
- ✓ Disk full (write failures)
- ✓ Concurrent file access (lock handling)

**UI Components (if applicable):**
- ✓ Loading state (data fetching)
- ✓ Empty state (no data to display)
- ✓ Error state (failed to load)
- ✓ Partial data (some fields missing)
- ✓ Full data (all fields present)
- ✓ Overflow data (more data than fits on screen)
- ✓ Disabled state (user lacks permissions)
- ✓ Interactive state (user can modify)

**Authentication/Authorization:**
- ✓ Not logged in (anonymous user)
- ✓ Logged in but no permissions (basic user)
- ✓ Logged in with partial permissions (can read, can't write)
- ✓ Logged in with full permissions (admin)
- ✓ Session expired (need refresh)
- ✓ Token invalid (tampered or malformed)
- ✓ Password reset flow states

#### How to Apply State Enumeration:

**Example: API Endpoint for Creating User**

Without state enumeration (weak):
```json
{
  "id": "test-001",
  "description": "POST /api/users creates a user",
  "acceptance": ["API returns 201", "User exists in database"]
}
```

With state enumeration (comprehensive):
```json
[
  {
    "id": "test-api-001",
    "description": "POST /api/users happy path with valid data",
    "acceptance": [
      "POST /api/users with valid email/password returns 201",
      "Response includes user id and email",
      "User record exists in database",
      "Password is hashed (not plaintext)"
    ]
  },
  {
    "id": "test-api-002",
    "description": "POST /api/users rejects missing required fields",
    "acceptance": [
      "POST /api/users without email returns 400",
      "Response indicates email is required",
      "No user record created in database"
    ]
  },
  {
    "id": "test-api-003",
    "description": "POST /api/users rejects duplicate email",
    "acceptance": [
      "Create user with email test@example.com",
      "POST /api/users with same email returns 409",
      "Response indicates email already exists",
      "Only one user record exists in database"
    ]
  },
  {
    "id": "test-api-004",
    "description": "POST /api/users handles database connection failure",
    "acceptance": [
      "Stop database service",
      "POST /api/users returns 500",
      "Response indicates service unavailable",
      "Error is logged for monitoring"
    ]
  }
]
```

**Example: Database Query with Pagination**

Without state enumeration (weak):
```json
{
  "id": "test-002",
  "description": "GET /api/posts returns posts",
  "acceptance": ["Query returns posts", "Data is correct"]
}
```

With state enumeration (comprehensive):
```json
[
  {
    "id": "test-db-001",
    "description": "GET /api/posts with empty database returns empty array",
    "acceptance": [
      "Database has zero posts",
      "GET /api/posts returns 200",
      "Response is empty array []",
      "Response includes pagination metadata (total: 0)"
    ]
  },
  {
    "id": "test-db-002",
    "description": "GET /api/posts with single post returns array with one item",
    "acceptance": [
      "Database has exactly 1 post",
      "GET /api/posts returns 200",
      "Response array has length 1",
      "Post data matches database record"
    ]
  },
  {
    "id": "test-db-003",
    "description": "GET /api/posts with 100+ posts paginates correctly",
    "acceptance": [
      "Database has 150 posts",
      "GET /api/posts?page=1&limit=20 returns first 20",
      "GET /api/posts?page=2&limit=20 returns next 20",
      "Pagination metadata shows total: 150, pages: 8"
    ]
  }
]
```

#### Checklist: Did You Cover All States?

Before finalizing your test list, verify:

- [ ] Happy path (everything works perfectly)
- [ ] Empty/null/zero states (no data exists yet)
- [ ] Boundary conditions (exactly 0, 1, max values)
- [ ] Validation failures (wrong type, missing fields, out of range)
- [ ] Permission failures (not logged in, wrong role)
- [ ] Resource not found (404 scenarios)
- [ ] Conflict scenarios (409 - duplicate, race conditions)
- [ ] Dependency failures (database down, API timeout, network error)
- [ ] Rate limiting / quota exceeded
- [ ] Malformed input (invalid JSON, SQL injection attempts)

**Remember:** Tests are cheap, production bugs are expensive. Enumerate states exhaustively.

### Step 2: Understand the Task
Read the task description carefully:
```
{TASK_DESCRIPTION}
```

If architecture map exists:
- **The map defines the scope** - Generate tests for everything in the map
- Prioritize tests based on the map's priority levels (critical, high, medium, low)
- Ensure dependency order (e.g., database tests before API tests)

If no architecture map:
- **STOP: Only generate tests for THIS EXACT TASK.**
- Do NOT look for additional work
- Do NOT add "while we're at it" improvements
- Stay laser-focused on the task description above

### Step 3: Research Codebase Context
Use Grep and Glob to understand **ONLY what's needed for the specific task**:
- Current state related to the task
- Files directly affected by the task
- Existing tests for the task area
- Dependencies specific to the task

**Do NOT research unrelated areas or look for additional improvement opportunities**

### Step 3: Define Test Categories
Common categories:
- **api** - API endpoint tests (cover all HTTP status codes, validation, auth)
- **database** - Database queries, constraints, migrations (cover all data states)
- **integration** - Multi-component workflows (cover success and failure paths)
- **edge-cases** - Boundary conditions, empty states, large datasets
- **error-handling** - Failure scenarios, timeouts, dependency failures
- **security** - Authentication, authorization, input validation, SQL injection
- **performance** - Load testing, pagination, query optimization
- **dependencies** - Package updates
- **refactoring** - Code structure improvements
- **cleanup** - Remove dead code, fix linting
- **config** - Configuration changes, environment setup
- **docs** - Documentation updates
- **style** - Design system compliance, Tailwind config, visual consistency

**Note:** Prioritize functional categories (api, database, integration, edge-cases, error-handling, security) over maintenance categories (dependencies, cleanup, docs).

### Step 4: Generate Test Cases
Create test file in the project directory provided above at `specs/chore-DDMMYY-HHMM-tests.json`:

**Example: State-Based API Tests**
```json
[
  {
    "id": "test-api-001",
    "category": "api",
    "description": "POST /api/users happy path creates user successfully",
    "acceptance": [
      "POST /api/users with valid email/password returns 201",
      "Response includes user id and email (no password)",
      "User record exists in database",
      "Password is bcrypt hashed in database"
    ],
    "passes": false,
    "priority": 1
  },
  {
    "id": "test-api-002",
    "category": "api",
    "description": "POST /api/users validates required fields",
    "acceptance": [
      "POST /api/users without email returns 400",
      "Response body indicates 'email is required'",
      "No user record created in database"
    ],
    "passes": false,
    "priority": 1
  },
  {
    "id": "test-api-003",
    "category": "api",
    "description": "POST /api/users prevents duplicate emails",
    "acceptance": [
      "Create user with email test@example.com",
      "POST /api/users with same email returns 409",
      "Response indicates 'email already exists'",
      "Database still has exactly 1 user with that email"
    ],
    "passes": false,
    "priority": 1
  },
  {
    "id": "test-edge-001",
    "category": "edge-cases",
    "description": "GET /api/users handles empty database",
    "acceptance": [
      "Database has zero users",
      "GET /api/users returns 200",
      "Response is empty array []",
      "Pagination metadata shows total: 0"
    ],
    "passes": false,
    "priority": 2
  },
  {
    "id": "test-edge-002",
    "category": "edge-cases",
    "description": "GET /api/users paginates large dataset correctly",
    "acceptance": [
      "Database has 150 users",
      "GET /api/users?page=1&limit=20 returns 20 users",
      "GET /api/users?page=8&limit=20 returns 10 users (last page)",
      "Pagination metadata: total=150, pages=8"
    ],
    "passes": false,
    "priority": 2
  },
  {
    "id": "test-error-001",
    "category": "error-handling",
    "description": "API handles database connection failure gracefully",
    "acceptance": [
      "Stop database service (docker-compose stop postgres)",
      "POST /api/users returns 503",
      "Response indicates 'Service temporarily unavailable'",
      "Error is logged with stack trace"
    ],
    "passes": false,
    "priority": 1
  },
  {
    "id": "test-security-001",
    "category": "security",
    "description": "POST /api/users prevents SQL injection",
    "acceptance": [
      "POST /api/users with email=\"'; DROP TABLE users; --\" returns 400",
      "Users table still exists in database",
      "No SQL error logged (parameterized queries used)"
    ],
    "passes": false,
    "priority": 1
  },
  {
    "id": "test-style-001",
    "category": "style",
    "description": "Tailwind config matches design system tokens",
    "acceptance": [
      "tailwind.config.js exists in project root",
      "Primary color matches STYLE.md specification",
      "Typography scale matches design system",
      "Spacing tokens are defined correctly"
    ],
    "passes": false,
    "priority": 3
  }
]
```

### Step 4.5: Calculate Coverage Metrics (NEW - Completeness Validation)

**If SPECIFICATION was provided in Step 1.7, calculate coverage metrics:**

#### Extract from Specification:
1. Count unique personas mentioned
2. Count user journeys described
3. Count URL routes mentioned (/, /dashboard, /analytics, etc.)
4. Count features mentioned (search, export, analytics, etc.)
5. Count data entities mentioned (User, Report, etc.)

#### Extract from Generated Tests:
1. Count which personas have tests (check test descriptions for persona names/roles)
2. Count which journeys have tests (check if workflow steps are tested)
3. Count which routes have tests (check acceptance criteria for route mentions)
4. Count which features have tests (check test descriptions for feature names)
5. Count which entities have tests (check if CRUD operations are tested)

#### Calculate Coverage Percentages:
```
persona_coverage = (personas_with_tests / total_personas) * 100
journey_coverage = (journeys_with_tests / total_journeys) * 100
route_coverage = (routes_with_tests / total_routes) * 100
feature_coverage = (features_with_tests / total_features) * 100
entity_coverage = (entities_with_tests / total_entities) * 100

overall_coverage = average of above 5 metrics
```

#### Identify Gaps:
List features/routes/personas that are in the specification but DON'T have tests.

Example:
```
Specification mentions:
- 5 personas (Sergeant, Inspector, Investigator, Panel Member, Officer)
- 12 user journeys
- 24 URL routes
- 32 features
- 10 data entities

Generated tests cover:
- 1 persona (Sergeant) → 20% coverage
- 1 journey (Morning Review Queue) → 8.3% coverage
- 3 routes (/, /queue, /encounter/:id) → 12.5% coverage
- 8 features (dashboard, queue, detail, review) → 25% coverage
- 3 entities (Encounter, Review, User) → 30% coverage

Overall coverage: 19.2%

GAPS:
- Missing personas: Inspector (analytics), Investigator (search), Panel Member, Officer
- Missing routes: /analytics, /search, /reports, /panel, /my, /admin (21 routes)
- Missing features: Search, Analytics dashboards, Reports, Panel portal, Officer portal (24 features)
```

**If coverage <80%, add WARNING comment in output:**
```
⚠️  WARNING: Test coverage is only 19.2% of specification
⚠️  Missing 4/5 personas, 21/24 routes, 24/32 features
⚠️  Recommend running completeness-validator in Phase 1.5
```

**If NO SPECIFICATION was provided:**
- Skip this step (backward compatible)
- No coverage metrics calculated

### Step 5: Validation Rules
- Minimum 5 tests, recommended 15 for focused tasks, maximum 100 for large projects
- Large specs (50+ tests) may take 2-4 hours to implement - use continuation agent if interrupted
- Each acceptance criterion is verifiable (can run command)
- No vague criteria ("code is clean", "works well")
- Priority 1 = must complete, Priority 2 = should complete, Priority 3 = nice to have

### Step 6: Output File Path
End your response with the RELATIVE path (relative to project directory):
```
TESTS_FILE: specs/chore-DDMMYY-HHMM-tests.json
```

## Report

**Without Specification (backward compatible):**
```
TESTS_FILE: specs/chore-041225-1430-tests.json
TOTAL_TESTS: 8
CATEGORIES: dependencies(3), refactoring(3), cleanup(2)
```

**With Specification (NEW - includes coverage metrics):**
```
TESTS_FILE: specs/chore-051225-1536-tests.json
TOTAL_TESTS: 45
CATEGORIES: api(12), database(8), integration(10), ui(8), edge-cases(5), security(2)
COVERAGE_PERCENTAGE: 85.5
PERSONA_COVERAGE: 5/5 (100%)
ROUTE_COVERAGE: 22/24 (91.7%)
FEATURE_COVERAGE: 28/32 (87.5%)
JOURNEY_COVERAGE: 10/12 (83.3%)
ENTITY_COVERAGE: 8/10 (80%)
GAPS: /admin/audit, /admin/settings, AdvancedAnalytics, BulkExport
```

**With Specification (LOW coverage - triggers warning):**
```
TESTS_FILE: specs/chore-051225-1536-tests.json
TOTAL_TESTS: 12
CATEGORIES: api(5), database(3), ui(4)
COVERAGE_PERCENTAGE: 19.2
PERSONA_COVERAGE: 1/5 (20%)
ROUTE_COVERAGE: 3/24 (12.5%)
FEATURE_COVERAGE: 8/32 (25%)
JOURNEY_COVERAGE: 1/12 (8.3%)
ENTITY_COVERAGE: 3/10 (30%)
GAPS: Inspector workflow, Investigator workflow, Panel portal, Officer portal, Search, Analytics, Reports (24 missing features)
WARNING: Coverage critically low - recommend Phase 1.5 completeness validation
```
