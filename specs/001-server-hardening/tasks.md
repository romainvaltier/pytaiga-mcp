---

description: "Task list for MCP Server Hardening & Quality Improvements feature"

---

# Tasks: MCP Server Hardening & Quality Improvements

**Input**: Design documents from `/specs/001-server-hardening/`
**Prerequisites**: plan.md (✅ complete), spec.md (✅ complete with 5 user stories)
**Branch**: `001-server-hardening`
**Created**: 2026-01-12

**Tests**: Tests are included as separate tasks organized by user story (test-first discipline per constitution)

**Organization**: Tasks are grouped by user story (P1, P1, P2, P2, P3) to enable independent implementation and testing of each story.

## Format: `- [ ] [ID] [P?] [Story] Description with file path`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1, US2, US3, US4, US5)
- Include exact file paths in descriptions

## Path Conventions

- **Single project**: `src/`, `tests/` at repository root
- Tasks use existing directory structure from plan.md
- New modules: `src/validators.py`, `src/logging_utils.py`
- Test organization: By resource type (auth/, projects/, epics/, etc.) with new auth/, error_handling/, integration/ directories

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and structure verification

- [ ] T001 Verify existing project structure matches plan.md (src/server.py, src/taiga_client.py, tests/)
- [ ] T002 [P] Create new module files: src/validators.py (empty skeleton)
- [ ] T003 [P] Create new module files: src/logging_utils.py (empty skeleton)
- [ ] T004 [P] Create test directories: tests/auth/, tests/error_handling/, tests/integration/
- [ ] T005 Configure linting and type checking tools (black, isort, mypy, flake8) in pyproject.toml if needed
- [ ] T006 Setup pytest markers for test organization (unit, integration, slow) and resource types (auth, core, projects, epics, etc.)

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [ ] T007 [P] Create Session model/class in src/server.py with attributes: session_id (UUID), user_id, created_at, last_accessed, ttl_seconds (default 28800 = 8 hours), concurrent_limit (5)
- [ ] T008 [P] Create RateLimitInfo model/class in src/server.py with attributes: username, attempt_count, last_attempt_time, lockout_until, window_size (60 seconds), max_attempts (5)
- [ ] T009 [P] Create ValidationRule model/class in src/validators.py with attributes: field_name, field_type (int/str/etc), min_value, max_value, min_length, max_length, pattern, required
- [ ] T010 Implement session storage infrastructure in src/server.py: active_sessions dict (maps session_id → TaigaClientWrapper), rate_limit_data dict (maps username → RateLimitInfo)
- [ ] T011 Implement helper function _get_authenticated_client(session_id) in src/server.py to validate session and retrieve client (raises PermissionError if invalid/expired)
- [ ] T012 Implement session expiry validation logic in src/server.py: check TTL on each operation, reject expired sessions, store last_accessed timestamp
- [ ] T013 Create base validation framework in src/validators.py with function validate_input(data, rules) that checks all constraints
- [ ] T014 Setup logging infrastructure in src/logging_utils.py with functions: log_operation(operation, user, details, sensitive_fields=['password', 'token', 'session_id']) to sanitize logs
- [ ] T015 Create conftest.py fixtures for testing: session_setup (creates mock authenticated session), rate_limit_setup, validation_setup, error_context

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Comprehensive Input Validation & Security (Priority: P1) 🎯 MVP

**Goal**: Implement comprehensive input validation across all API operations to prevent invalid data from reaching Taiga API, ensuring secure and predictable behavior

**Independent Test**: Can be fully tested by:
1. Sending requests with invalid inputs (negative IDs, empty strings, oversized strings)
2. Verifying rejection at validation layer with descriptive errors
3. Ensuring valid inputs pass through to API
4. Confirming error messages guide users to correct values
5. Running validation test suite covering all resource types

### Tests for User Story 1 (Test-First Discipline)

- [ ] T016 [P] [US1] Unit test: validate negative project ID in tests/auth/test_input_validation.py - verify rejection with "project_id must be positive integer"
- [ ] T017 [P] [US1] Unit test: validate empty project name in tests/auth/test_input_validation.py - verify rejection with "project_name is required and cannot be empty"
- [ ] T018 [P] [US1] Unit test: validate oversized project name (>255 chars) in tests/auth/test_input_validation.py - verify rejection
- [ ] T019 [P] [US1] Unit test: validate valid project creation in tests/auth/test_input_validation.py - verify passes validation
- [ ] T020 [P] [US1] Integration test: CRUD operations with validation in tests/integration/test_validation_integration.py covering projects, epics, user_stories, tasks, issues, sprints, milestones
- [ ] T021 [P] [US1] Unit test: validate epic ID constraints in tests/projects/test_validation.py
- [ ] T022 [P] [US1] Unit test: validate user story field constraints in tests/user_stories/test_validation.py
- [ ] T023 [P] [US1] Unit test: validate task field constraints in tests/tasks/test_validation.py
- [ ] T024 [P] [US1] Unit test: validate issue field constraints in tests/issues/test_validation.py
- [ ] T025 [P] [US1] Unit test: validate sprint field constraints in tests/sprints/test_validation.py
- [ ] T026 [P] [US1] Unit test: validate milestone field constraints in tests/milestones/test_validation.py

### Implementation for User Story 1

- [ ] T027 [US1] Implement validation rules for projects in src/validators.py: project_id (positive int), project_name (required, 1-255 chars), description (0-2000 chars), key (1-50 chars)
- [ ] T028 [US1] Implement validation rules for epics in src/validators.py: epic_id (positive int), epic_name (required, 1-255 chars), project_id (positive int)
- [ ] T029 [US1] Implement validation rules for user stories in src/validators.py: story_id (positive int), title (required, 1-255 chars), project_id (positive int), estimated_effort (0-999)
- [ ] T030 [US1] Implement validation rules for tasks in src/validators.py: task_id (positive int), subject (required, 1-255 chars), project_id (positive int), status (valid enum)
- [ ] T031 [US1] Implement validation rules for issues in src/validators.py: issue_id (positive int), subject (required, 1-255 chars), project_id (positive int), priority (valid enum)
- [ ] T032 [US1] Implement validation rules for sprints in src/validators.py: sprint_id (positive int), name (required, 1-255 chars), project_id (positive int), start_date (valid ISO date), end_date (valid ISO date, > start_date)
- [ ] T033 [US1] Implement validation rules for milestones in src/validators.py: milestone_id (positive int), name (required, 1-255 chars), project_id (positive int), target_date (valid ISO date)
- [ ] T034 [P] [US1] Add validation calls to existing tools in src/server.py: create_project(), update_project(), delete_project() - validate inputs before API call (FR-001)
- [ ] T035 [P] [US1] Add validation calls to epic operations in src/server.py: create_epic(), update_epic(), delete_epic() - validate inputs before API call
- [ ] T036 [P] [US1] Add validation calls to user story operations in src/server.py: create_user_story(), update_user_story(), delete_user_story(), list_user_stories() - validate inputs
- [ ] T037 [P] [US1] Add validation calls to task operations in src/server.py: create_task(), update_task(), delete_task() - validate inputs before API call
- [ ] T038 [P] [US1] Add validation calls to issue operations in src/server.py: create_issue(), update_issue(), delete_issue() - validate inputs before API call
- [ ] T039 [P] [US1] Add validation calls to sprint operations in src/server.py: create_sprint(), update_sprint(), delete_sprint() - validate inputs before API call
- [ ] T040 [P] [US1] Add validation calls to milestone operations in src/server.py: create_milestone(), update_milestone(), delete_milestone() - validate inputs before API call
- [ ] T041 [US1] Create error formatter helper function in src/server.py to generate descriptive validation error messages with recovery guidance (FR-001)
- [ ] T042 [US1] Add logging for validation failures in src/logging_utils.py to track rejected inputs (log with sensitive data sanitization)

**Checkpoint**: At this point, User Story 1 (Input Validation) should be fully functional and testable independently with >85% coverage of validation layer

---

## Phase 4: User Story 2 - Session Management Hardening & Security (Priority: P1)

**Goal**: Implement robust session management with automatic timeout enforcement, concurrent session limits, and rate limiting to protect against account abuse and resource exhaustion

**Independent Test**: Can be fully tested by:
1. Creating authenticated sessions and verifying TTL enforcement
2. Attempting operations after session expiry (should be rejected)
3. Creating multiple concurrent sessions and enforcing limits
4. Making rapid login attempts and verifying rate limiting
5. Verifying automatic cleanup of expired sessions

### Tests for User Story 2 (Test-First Discipline)

- [ ] T043 [P] [US2] Unit test: session TTL expiration in tests/auth/test_session_validation.py - verify rejection after 8 hours with "session expired" error (FR-002)
- [ ] T044 [P] [US2] Unit test: rate limiting on login attempts in tests/auth/test_rate_limiting.py - verify 6th login in 60 seconds rejected with "too many login attempts" (FR-003)
- [ ] T045 [P] [US2] Unit test: concurrent session limits in tests/auth/test_concurrent_limits.py - verify 6th session rejected with "maximum concurrent sessions exceeded" (FR-004)
- [ ] T046 [P] [US2] Unit test: automatic cleanup of expired sessions in tests/auth/test_session_validation.py - verify cleanup after TTL expires (FR-012)
- [ ] T047 [P] [US2] Unit test: rate limit lockout duration in tests/auth/test_rate_limiting.py - verify 15-minute lockout after max attempts (FR-003)
- [ ] T048 [P] [US2] Unit test: session last_accessed updates on operation in tests/auth/test_session_validation.py
- [ ] T049 [US2] Integration test: complete session lifecycle in tests/integration/test_session_lifecycle.py - login, operations, expiry, cleanup
- [ ] T050 [P] [US2] Unit test: rate limit window sliding behavior in tests/auth/test_rate_limiting.py

### Implementation for User Story 2

- [ ] T051 [US2] Implement TTL enforcement in src/server.py: check (current_time - session.last_accessed) > ttl_seconds on every operation, raise PermissionError("session expired") (FR-002)
- [ ] T052 [US2] Implement session cleanup task in src/server.py: background cleanup function to remove expired sessions from active_sessions dict, preventing memory leaks (FR-012)
- [ ] T053 [US2] Implement rate limiting on login in src/server.py: track login attempts per username, reject 6th attempt in 60-second window with "too many login attempts, please try again in 15 minutes" (FR-003)
- [ ] T054 [US2] Implement rate limit lockout logic in src/server.py: set lockout_until timestamp on violation, reject further login attempts until lockout expires (15 minutes) (FR-003)
- [ ] T055 [US2] Implement concurrent session limits in src/server.py: count active sessions per user, reject login if count >= 5 with clear error message including current count (FR-004)
- [ ] T056 [US2] Implement automatic session cleanup task in src/server.py: background function to remove RateLimitInfo entries after 15-minute lockout expires (FR-012)
- [ ] T057 [US2] Update login tool in src/server.py to return session_id and metadata (session created time, TTL) for client awareness
- [ ] T058 [US2] Update logout tool in src/server.py to properly remove session from active_sessions and related rate limit data
- [ ] T059 [US2] Add session validation to ALL existing tools in src/server.py: call _get_authenticated_client(session_id) at start of each tool (FR-002)
- [ ] T060 [US2] Add logging for session lifecycle events in src/logging_utils.py: login success/failure, session expiry, concurrent limit violations, rate limit violations (FR-006)

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently - input validation + session security complete

---

## Phase 5: User Story 3 - Comprehensive Error Handling & Logging (Priority: P2)

**Goal**: Implement production-ready error handling with clear messages and secure logging that captures operation history without exposing sensitive data

**Independent Test**: Can be fully tested by:
1. Testing each error condition (404, 403, 409, timeout, etc.)
2. Verifying error messages are user-friendly and actionable
3. Checking logs for comprehensive operation capture
4. Confirming passwords/tokens never appear in logs
5. Validating error recovery guidance

### Tests for User Story 3 (Test-First Discipline)

- [ ] T061 [P] [US3] Unit test: 404 error handling in tests/error_handling/test_error_handling.py - verify user-friendly message "resource not found (ID: 123)" (FR-005)
- [ ] T062 [P] [US3] Unit test: 403 permission error in tests/error_handling/test_error_handling.py - verify message "insufficient permissions for this operation"
- [ ] T063 [P] [US3] Unit test: login logging without password in tests/error_handling/test_logging.py - verify logs contain "User login: username=john, result=success" without password (FR-006)
- [ ] T064 [P] [US3] Unit test: failed login logging in tests/error_handling/test_logging.py - verify logs contain reason and no session_id (FR-006)
- [ ] T065 [P] [US3] Unit test: timeout error handling in tests/error_handling/test_error_handling.py - verify recovery guidance "please try again"
- [ ] T066 [P] [US3] Unit test: 409 conflict error in tests/error_handling/test_error_handling.py - verify user-friendly conflict message
- [ ] T067 [P] [US3] Unit test: sensitive data sanitization in logs in tests/error_handling/test_logging.py - verify password, token, session_id never logged (FR-006)
- [ ] T068 [US3] Integration test: error handling across all resource types in tests/integration/test_error_handling_integration.py

### Implementation for User Story 3

- [ ] T069 [US3] Create error handler middleware/decorator in src/server.py to catch TaigaException and convert to user-friendly messages (FR-005)
- [ ] T070 [US3] Implement 404 error handler: catch "not found" errors, return "resource not found (ID: {id})" with clear message (FR-005)
- [ ] T071 [US3] Implement 403 error handler: catch permission errors, return "insufficient permissions for this operation" with recovery guidance (FR-005)
- [ ] T072 [US3] Implement 409 error handler: catch conflict errors, return "resource conflict - it may have been modified, please refresh and try again" (FR-005)
- [ ] T073 [US3] Implement timeout error handler: catch timeout errors, return "request timeout - server may be busy, please try again" (FR-005)
- [ ] T074 [US3] Implement generic error handler: catch all unhandled exceptions, return "operation failed - please try again" without exposing stack trace (FR-005)
- [ ] T075 [US3] Update src/logging_utils.py to implement log_operation() function with sensitive field sanitization (FR-006)
- [ ] T076 [US3] Add logging to login/logout operations in src/server.py: log username, result, timestamp - NEVER log password or session_id (FR-006)
- [ ] T077 [US3] Add logging to all CRUD operations in src/server.py: log operation type, resource type, user, timestamp, success/failure status (FR-006)
- [ ] T078 [US3] Add logging to error conditions in src/server.py: log error type, message, affected resource/user, recovery guidance (FR-006)
- [ ] T079 [US3] Update all tools in src/server.py to include error recovery guidance in error messages: "please try again", "check permissions", "contact support", etc. (FR-005, SC-012)

**Checkpoint**: At this point, User Stories 1, 2, and 3 should be working - validation, security, and error handling complete

---

## Phase 6: User Story 4 - Code Quality & Consistency (Priority: P2)

**Goal**: Implement consistent code patterns, reduce duplication, and add complete type hints for maintainability and reduced bugs

**Independent Test**: Can be fully tested by:
1. Running automated tools (type checker, linter, formatter) and verifying zero violations
2. Checking for duplicate code patterns and verifying consolidation
3. Reviewing type hints coverage across modules
4. Validating all code follows established patterns
5. Confirming code is readable and documented

### Tests for User Story 4 (Quality Validation)

- [ ] T080 [P] [US4] Type checking: run mypy on src/ and verify zero type errors (FR-008, SC-007)
- [ ] T081 [P] [US4] Linting: run flake8 on src/ and verify zero lint violations (FR-011, SC-010)
- [ ] T082 [P] [US4] Formatting: run black on src/ and verify all code properly formatted (FR-011, SC-009)
- [ ] T083 [P] [US4] Import sorting: run isort on src/ and verify imports organized (FR-011, SC-009)
- [ ] T084 [US4] Code coverage check: run pytest --cov=src and verify coverage is maintained through all changes (FR-010)

### Implementation for User Story 4

- [ ] T085 [US4] Add complete type hints to src/validators.py: all functions, parameters, return types (FR-008)
- [ ] T086 [US4] Add complete type hints to src/logging_utils.py: all functions, parameters, return types (FR-008)
- [ ] T087 [US4] Add complete type hints to src/server.py: all tool functions, helper functions, parameters, return types (FR-008)
- [ ] T088 [US4] Add docstrings to validators.py functions with parameter descriptions and return type documentation (FR-008)
- [ ] T089 [US4] Add docstrings to logging_utils.py functions with parameter descriptions and return type documentation (FR-008)
- [ ] T090 [US4] Review src/server.py for duplicate code patterns: identify assign/unassign operations, similar validation code, similar error handling (FR-007)
- [ ] T091 [US4] Consolidate duplicate validation patterns in src/server.py: create shared validation helper functions to eliminate duplication (FR-007, SC-006)
- [ ] T092 [US4] Consolidate duplicate error handling patterns in src/server.py: create shared error handling wrappers (FR-007, SC-006)
- [ ] T093 [US4] Consolidate duplicate logging patterns in src/server.py: use logging_utils.log_operation() consistently (FR-007, SC-006)
- [ ] T094 [US4] Format all source files: run black src/ and isort src/ to enforce consistent formatting (FR-011, SC-009)
- [ ] T095 [US4] Run linting: flake8 src/ and fix any violations (FR-011, SC-010)
- [ ] T096 [US4] Run type checking: mypy src/ and fix any type errors (FR-008, SC-007)
- [ ] T097 [US4] Document code quality standards in docs/CODE_QUALITY.md: type hints, linting rules, formatting rules, duplication limits

**Checkpoint**: At this point, User Stories 1, 2, 3, and 4 should be complete - validation, security, error handling, and code quality all in place

---

## Phase 7: User Story 5 - Comprehensive Testing Coverage (Priority: P3)

**Goal**: Achieve >85% code coverage with comprehensive test organization and edge case coverage for production readiness

**Independent Test**: Can be fully tested by:
1. Running full test suite and verifying >85% code coverage
2. Testing all CRUD operations (create, read, update, delete)
3. Testing all error scenarios and edge cases
4. Running integration tests for complete workflows
5. Verifying tests are maintainable and well-organized

### Tests for User Story 5 (Test Organization & Coverage)

- [ ] T098 [P] [US5] Comprehensive test suite for projects: create, read, update, delete with success and error paths in tests/projects/test_projects.py
- [ ] T099 [P] [US5] Comprehensive test suite for epics: create, read, update, delete with success and error paths in tests/epics/test_epics.py
- [ ] T100 [P] [US5] Comprehensive test suite for user stories: create, read, update, delete with success and error paths in tests/user_stories/test_user_stories.py
- [ ] T101 [P] [US5] Comprehensive test suite for tasks: create, read, update, delete with success and error paths in tests/tasks/test_tasks.py
- [ ] T102 [P] [US5] Comprehensive test suite for issues: create, read, update, delete with success and error paths in tests/issues/test_issues.py
- [ ] T103 [P] [US5] Comprehensive test suite for sprints: create, read, update, delete with success and error paths in tests/sprints/test_sprints.py
- [ ] T104 [P] [US5] Comprehensive test suite for milestones: create, read, update, delete with success and error paths in tests/milestones/test_milestones.py
- [ ] T105 [P] [US5] Edge case tests: empty lists, boundary values, concurrent operations in tests/integration/test_edge_cases.py
- [ ] T106 [P] [US5] Integration tests: complete workflows (login → create project → create epic → create story → create task) in tests/integration/test_workflows.py
- [ ] T107 [US5] Run coverage analysis: pytest --cov=src --cov-report=html and verify >85% coverage (FR-010, SC-008)
- [ ] T108 [US5] Identify coverage gaps and add tests for uncovered code paths to reach >85% target (FR-010, SC-008)
- [ ] T109 [US5] Verify test suite performance: pytest and confirm all tests complete in <10 seconds with zero flaky tests (SC-011)
- [ ] T110 [US5] Organize tests with markers: @pytest.mark.unit, @pytest.mark.integration, @pytest.mark.slow for organization (FR-009)
- [ ] T111 [US5] Organize tests by resource type: separate directories for auth/, projects/, epics/, user_stories/, tasks/, issues/, sprints/, milestones/, error_handling/, integration/ (FR-009)

### Implementation for User Story 5

- [ ] T112 [US5] Create comprehensive unit test suite in tests/auth/ covering all session/validation/rate limit scenarios (T043-T050, T061-T068 should already exist)
- [ ] T113 [US5] Create comprehensive resource test suites in tests/[resource_type]/ covering all CRUD operations with success and error paths
- [ ] T114 [US5] Create comprehensive integration test suite in tests/integration/ covering complete user workflows
- [ ] T115 [US5] Create edge case test suite in tests/integration/test_edge_cases.py covering boundary conditions and concurrent scenarios
- [ ] T116 [US5] Configure pytest markers in pyproject.toml: unit, integration, slow, and resource types (auth, projects, epics, user_stories, tasks, issues, sprints, milestones) (FR-009)
- [ ] T117 [US5] Verify test organization: run pytest --co (collect only) and confirm tests are organized by resource type (FR-009)
- [ ] T118 [US5] Verify test performance: run full test suite and confirm completion in <10 seconds (SC-011)

**Checkpoint**: At this point, all User Stories 1-5 should be complete - validation, security, error handling, code quality, and comprehensive testing all in place with >85% coverage

---

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: Final improvements, documentation, and validation

- [ ] T119 [P] Documentation: Update README.md with new session management requirements and validation constraints
- [ ] T120 [P] Documentation: Create HARDENING.md documenting security improvements: TTL enforcement, rate limiting, validation, error handling, logging
- [ ] T121 [P] Documentation: Update CLAUDE.md with validation patterns, error handling patterns, logging patterns for future developers
- [ ] T122 Documentation: Update pyproject.toml with any new dependencies (pydantic if validation framework uses it)
- [ ] T123 [P] Run final code formatting: black src/ && isort src/
- [ ] T124 [P] Run final type checking: mypy src/
- [ ] T125 [P] Run final linting: flake8 src/
- [ ] T126 [P] Run final coverage: pytest --cov=src --cov-report=term-missing and document final coverage percentage
- [ ] T127 Run full test suite: pytest -v and verify all tests pass with <10 seconds execution time
- [ ] T128 Final verification: Run quickstart.md scenarios (login, create project, create epic, create story, etc.) to ensure end-to-end functionality
- [ ] T129 Performance validation: Verify input validation <5ms per request, session lookup O(1), full test suite <10 seconds
- [ ] T130 Update SPRINT_PLANNING.md to mark all user stories in this feature as complete

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - **BLOCKS all user stories**
- **User Story 1 (Phase 3)**: Depends on Foundational completion - Input Validation (P1)
- **User Story 2 (Phase 4)**: Depends on Foundational completion - Session Security (P1)
- **User Story 3 (Phase 5)**: Depends on Foundational completion - Error Handling (P2)
- **User Story 4 (Phase 6)**: Depends on completion of US1, US2, US3 - Code Quality (P2)
- **User Story 5 (Phase 7)**: Depends on completion of US1, US2, US3, US4 - Testing Coverage (P3)
- **Polish (Phase 8)**: Depends on all user stories being complete

### User Story Parallelization

After Foundational phase (Phase 2) completes:
- **User Stories 1 & 2** (both P1): Can run in parallel - input validation and session security are independent
- **User Story 3** (P2): Can start after US1 & US2 - error handling depends on both existing
- **User Story 4** (P2): Can run in parallel with US3 - code quality is independent
- **User Story 5** (P3): Must come after US1, US2, US3, US4 - depends on features being complete for testing

### Within Each User Story

- **Tests must be written FIRST** (test-first discipline per constitution)
- Tests MUST FAIL before implementation
- **Models/validators before services/middleware**
- **Services before tools/endpoints**
- **Core implementation before integration**
- Story complete before moving to next priority

### Parallel Opportunities

**Phase 1 Setup**: All tasks marked [P] can run in parallel

**Phase 2 Foundational**: Tasks T007-T009 marked [P] can run in parallel (models), then T010-T015 run sequentially

**Phase 3 User Story 1**:
- Tests T016-T026 marked [P] can run in parallel
- Validation implementations T027-T033 marked [P] can run in parallel
- Tool integrations T034-T040 marked [P] can run in parallel

**Phase 4 User Story 2**:
- Tests T043-T048 marked [P] can run in parallel
- Implementations T051-T060 run sequentially (dependencies)

**Phase 5 User Story 3**:
- Tests T061-T067 marked [P] can run in parallel
- Implementations T069-T079 run sequentially (dependencies)

**Phase 6 User Story 4**:
- Quality validation T080-T084 marked [P] can run in parallel
- Type hints, consolidation, formatting T085-T096 run sequentially

**Phase 7 User Story 5**:
- Test suites T098-T105 marked [P] can run in parallel
- Coverage verification T107-T118 run sequentially

---

## Parallel Example: User Story 1 (Input Validation)

```bash
# After Foundational phase, launch all validation tests in parallel:
pytest tests/auth/test_input_validation.py tests/projects/test_validation.py tests/user_stories/test_validation.py tests/tasks/test_validation.py tests/issues/test_validation.py tests/sprints/test_validation.py tests/milestones/test_validation.py -v

# Launch all validation rule implementations in parallel:
# Developer A: T027 (projects) and T028 (epics)
# Developer B: T029 (user stories) and T030 (tasks)
# Developer C: T031 (issues), T032 (sprints), T033 (milestones)

# Launch all tool integrations in parallel:
# Developer A: T034-T035 (projects, epics)
# Developer B: T036-T037 (user stories, tasks)
# Developer C: T038-T040 (issues, sprints, milestones)
```

---

## Implementation Strategy

### MVP First (Input Validation + Session Security)

1. Complete Phase 1: Setup (1 day)
2. Complete Phase 2: Foundational (2 days) - **CRITICAL GATE**
3. Complete Phase 3: User Story 1 - Input Validation (3 days) - Tests first, then implementation
4. Complete Phase 4: User Story 2 - Session Security (3 days) - Tests first, then implementation
5. **STOP and VALIDATE**: Run full test suite, verify >75% coverage, validate independently
6. Deploy/demo if ready (input validation + session security = MVP)

### Incremental Delivery (Full Feature)

1. **MVP (Days 1-9)**: Setup + Foundational + US1 + US2 ✅ Deploy first increment
2. **Sprint 2 (Days 10-13)**: US3 Error Handling + Logging ✅ Deploy second increment
3. **Sprint 3 (Days 14-15)**: US4 Code Quality + Consolidation ✅ Deploy third increment
4. **Sprint 4 (Days 16-20)**: US5 Comprehensive Testing + Coverage ✅ Deploy final increment
5. **Polish (Days 21-22)**: Documentation, final QA, roadmap updates

### Parallel Team Strategy (4 Developers)

**Phase 1-2 (Setup + Foundational)**: All 4 developers together
- T001-T006: Setup tasks
- T007-T015: Foundational infrastructure

**Phase 3-4 (After Foundational)**: Teams separate

**Developer A**: User Story 1 (Input Validation)
- T016-T026: Write validation tests
- T027-T033: Implement validation rules
- T034-T035: Integrate with projects/epics

**Developer B**: User Story 2 (Session Security)
- T043-T048: Write session tests
- T051-T060: Implement session management

**Developer C**: User Story 1 Parallel Track
- T036-T040: Integrate validation with remaining resources

**Developer D**: Start User Story 3 (Error Handling)
- T061-T068: Write error handling tests
- T069-T079: Implement error handling

**Then merge results, validate, deploy MVP**

---

## Quality Gates

### Phase 2 Gate (Must Pass Before User Stories)
- [ ] Session model and storage implemented
- [ ] RateLimitInfo model and storage implemented
- [ ] ValidationRule model defined
- [ ] _get_authenticated_client() works correctly
- [ ] conftest.py fixtures ready for testing

### Phase 3 Gate (Input Validation Complete)
- [ ] All validation tests passing
- [ ] All resource types have validation rules
- [ ] All tools call validation before API
- [ ] Error messages are user-friendly
- [ ] No validation test failures

### Phase 4 Gate (Session Security Complete)
- [ ] All session tests passing
- [ ] TTL enforcement working
- [ ] Rate limiting working
- [ ] Concurrent session limits working
- [ ] Cleanup tasks running
- [ ] No session test failures

### Phase 5 Gate (Error Handling Complete)
- [ ] All error handling tests passing
- [ ] Sensitive data never logged
- [ ] All error messages include recovery guidance
- [ ] Error handling covers all edge cases
- [ ] No error handling test failures

### Phase 6 Gate (Code Quality Complete)
- [ ] mypy: 0 type errors
- [ ] flake8: 0 lint violations
- [ ] black: all files formatted
- [ ] isort: all imports organized
- [ ] Code duplication reduced ≥50%

### Phase 7 Gate (Testing Complete)
- [ ] Code coverage ≥85%
- [ ] All CRUD operations tested
- [ ] All error paths tested
- [ ] All edge cases tested
- [ ] Test suite completes in <10 seconds
- [ ] Zero flaky tests

### Final Gate (Polish Complete)
- [ ] All documentation updated
- [ ] Performance targets met (<5ms validation, O(1) session lookup, <10s tests)
- [ ] All quality gates passing
- [ ] Ready for production deployment

---

## Notes

- **[P] tasks** = different files or independent operations, no dependencies
- **[Story] label** maps task to specific user story for traceability
- Each user story should be independently completable and testable
- **Test-first discipline**: Write tests FIRST, ensure they FAIL before implementing (per constitution)
- Tests must cover success paths AND error paths
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Avoid: vague tasks, same file conflicts without clear ordering, cross-story dependencies that break independence
- Success criteria from spec.md must be met before marking story complete
- Performance targets from plan.md must be validated before deployment
