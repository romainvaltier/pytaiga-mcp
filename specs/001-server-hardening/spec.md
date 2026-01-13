# Feature Specification: MCP Server Hardening & Quality Improvements

**Feature Branch**: `001-server-hardening`
**Created**: 2026-01-12
**Status**: In Progress (Sprints 1-4, across multiple PRs)
**Input**: User description: "Hardening existing MCP server with security, testing, and quality improvements"
**Epic Scope**: Comprehensive security hardening, quality improvements, and testing infrastructure spanning Sprints 1-4 (22 user stories across 5 epic categories)
**Completion Target**: End of Sprint 4 (Week 8) with all 22 user stories complete (18 merged ✅, 4 in progress), >85% code coverage, production-ready

---

## 📋 Feature Status Summary

**Story Structure**: This specification documents 22 user stories organized across 5 Epic categories (User Stories 1-5). Within each epic are multiple discrete user stories (US-1.1, US-1.2, ..., US-3.5, etc.) tracked in the roadmap. Sprint 4 adds 4 new stories (US-2.6, US-3.3, US-3.4, US-3.5) to complete the feature.

| Sprint | Stories | Status | Completion |
|--------|---------|--------|------------|
| Sprint 1 | US-1.1, US-1.4, US-1.5, US-2.4, US-2.5 | ✅ Complete | 5 PRs merged |
| Sprint 2 | US-1.2, US-1.3, US-2.1 | ✅ Complete | 3 PRs merged |
| Sprint 3 | US-2.2, US-2.3, US-3.1, US-3.2 | ✅ Complete | 4 PRs merged |
| Sprint 4 | US-2.6, US-3.3, US-3.4, US-3.5 | ⏳ In Progress | 4 stories (1 complete, 3 remaining) |

**Total**: 19/22 user stories complete (86%), Sprint 4 targets 22/22 (100%)

---

## 🔍 Clarifications

### Session 2026-01-12

Conducted during `/speckit.clarify` workflow to align specification with SPRINT_PLANNING.md progress (Sprints 1-4 actual delivery).

- **Q1: Branch Purpose & Scope** → A: Option B - Full feature documentation with completion tracking (Sprints 1-4) and cross-links to merged PRs. Enables this branch to serve as master specification baseline for the entire hardening epic.

- **Q2: Mapping Completed Work to Spec** → A: Option C - Status badges with PR footnotes (e.g., "✅ COMPLETED (Sprint 2)" with PR #6, #7 references). Keeps context visible while reading, enables quick navigation to PRs.

- **Q3: Sprint 4 Scope** → A: Option A - Include US-2.6 (Add Input Validation to Delete Operations) in Sprint 4 alongside US-3.4/US-3.5. Keeps related validation work together with logical dependencies (validate before test). Adds 3-5 points, manageable within 2-week sprint.

- **Q4: Feature Completion Criteria** → A: Option A - End of Sprint 4 marks feature complete. All 5 user stories (Validation, Session, Error Handling, Quality, Testing) complete, >85% code coverage, production-ready. Milestone 1 (v0.2.0) and distributed sessions (Sprint 5) are next phase continuation.

- **Q5: Spec Documentation Level** → A: Option B - Requirements + Actual Implementation sections. Add "Implementation" subsections under each completed story (Sprints 1-3) showing actual file paths, class names, methods, PR links. For Sprint 4 work (incomplete), mark sections as "TODO". Makes spec comprehensive reference (both what was needed + what was delivered).

---

## User Scenarios & Testing *(mandatory)*

<!--
  IMPORTANT: User stories should be PRIORITIZED as user journeys ordered by importance.
  Each user story/journey must be INDEPENDENTLY TESTABLE - meaning if you implement just ONE of them,
  you should still have a viable MVP (Minimum Viable Product) that delivers value.
  
  Assign priorities (P1, P2, P3, etc.) to each story, where P1 is the most critical.
  Think of each story as a standalone slice of functionality that can be:
  - Developed independently
  - Tested independently
  - Deployed independently
  - Demonstrated to users independently
-->

### User Story 1 - Comprehensive Input Validation & Security (Priority: P1) ✅ COMPLETED (Sprint 1, 3-4)

**Status**: Complete - US-1.1 merged (Sprint 1 PR #1), US-3.3 merged (Sprint 3-4 PR #13)

Development teams need robust input validation across all API operations to prevent invalid data from reaching the Taiga API, ensuring secure and predictable behavior.

**Why this priority**: Input validation is the first line of defense against malformed requests, security vulnerabilities, and API errors. Without proper validation, the system fails at the Taiga API layer with poor error messages instead of rejecting bad input early with clear guidance.

**Independent Test**: Can be fully tested by:
1. Sending requests with invalid inputs (negative IDs, empty strings, oversized strings)
2. Verifying rejection at validation layer with descriptive errors
3. Ensuring valid inputs pass through to API
4. Confirming error messages guide users to correct values

Delivers comprehensive input validation coverage across all resource types (projects, epics, user stories, tasks, issues, sprints, milestones).

**Acceptance Scenarios**:

1. **Given** an API request with a negative project ID, **When** the validation layer processes it, **Then** it is rejected with error message "project_id must be positive integer" before API call

2. **Given** an API request with an empty project name, **When** the validation layer processes it, **Then** it is rejected with "project_name is required and cannot be empty"

3. **Given** an API request with a project name exceeding 255 characters, **When** the validation layer processes it, **Then** it is rejected with "project_name cannot exceed 255 characters"

4. **Given** a valid project creation request, **When** the validation layer processes it, **Then** it passes validation and reaches the API layer

5. **Given** multiple CRUD operations with invalid data, **When** running a comprehensive test suite, **Then** all invalid inputs are caught by validation layer, not API layer

**Implementation** (Sprint 1 - PR #1, completed):
- Created `src/validators.py` with 20+ validation functions for all resource types (projects, epics, user stories, tasks, issues, sprints, milestones)
- Implemented core validation rules: IDs as positive integers, strings with length limits (1-255 chars), enums for status/priority fields
- Integrated validation calls into all CRUD tools in `src/server.py` (create_project, update_project, delete_project, etc.)
- Added error formatter helper to generate descriptive validation error messages with recovery guidance
- 100% validation layer test coverage via `tests/auth/test_input_validation.py`
- Status: ✅ MERGED - All input validation for CRUD operations complete

**Sprint 4 Remaining** (US-2.6, US-3.4, US-3.5):
- US-2.6: Add input validation to 3 delete operations (delete_user_story, delete_issue, delete_milestone)
- US-3.4: Comprehensive delete operation test suite with success and error paths
- US-3.5: Edge case and boundary condition testing across all code paths
- Status: ⏳ READY TO START - US-3.3 complete, US-2.6/US-3.5 have no dependencies, US-3.4 blocked by US-2.6

---

### User Story 2 - Session Management Hardening & Security (Priority: P1) ✅ COMPLETED (Sprint 2)

**Status**: Complete - US-1.2 (Session Hardening) PR #6 merged, US-1.3 (Rate Limiting) PR #7 merged

Operations teams need robust session management with automatic timeout enforcement, concurrent session limits, and rate limiting to protect against account abuse and resource exhaustion.

**Why this priority**: Session security is critical for protecting user accounts and preventing unauthorized access. Hardened session management prevents brute force attacks, session hijacking, and resource exhaustion attacks.

**Independent Test**: Can be fully tested by:
1. Creating authenticated sessions and verifying TTL enforcement
2. Attempting operations after session expiry (should be rejected)
3. Creating multiple concurrent sessions and enforcing limits
4. Making rapid login attempts and verifying rate limiting
5. Verifying automatic cleanup of expired sessions

Delivers complete session lifecycle security and resource protection.

**Acceptance Scenarios**:

1. **Given** an authenticated session, **When** the session TTL expires, **Then** subsequent API calls are rejected with "session expired" error

2. **Given** a user attempting 6 logins within 60 seconds, **When** the 6th attempt is made, **Then** it is rejected with "too many login attempts, please try again in 15 minutes"

3. **Given** a user with 5 active concurrent sessions, **When** a 6th login attempt is made, **Then** it is rejected with "maximum concurrent sessions exceeded (5 active)"

4. **Given** a user with 3 concurrent sessions, **When** each session is inactive for 8 hours, **Then** all 3 sessions are automatically removed from active sessions

5. **Given** a session management test suite, **When** running tests, **Then** all edge cases pass (TTL enforcement, rate limiting, concurrent limits, cleanup)

**Implementation** (Sprint 2 - PR #6, #7, completed):
- Created `SessionInfo` dataclass (src/server.py) with TTL enforcement (default 8 hours), last_accessed tracking, concurrent session limits (max 5 per user)
- Created `RateLimitInfo` and `LoginAttempt` dataclasses for rate limit tracking with sliding window algorithm
- Implemented session validation with automatic TTL checks and rejection of expired sessions
- Implemented per-user concurrent session limit enforcement (default: 5 active sessions)
- Implemented rate limiting on login attempts (max 5 attempts per 60 seconds with 15-minute lockout)
- Background cleanup tasks (every 5 minutes) for expired sessions and rate limit data
- Thread-safe implementation with proper locking mechanisms
- Configuration variables: SESSION_EXPIRY, MAX_CONCURRENT_SESSIONS, SESSION_CLEANUP_INTERVAL, LOGIN_MAX_ATTEMPTS, LOGIN_RATE_WINDOW, LOGIN_LOCKOUT_DURATION
- Comprehensive test coverage: 28 session tests (TestSessionInfo, TestSessionValidation, TestConcurrentSessionLimits, TestSessionCleanup, TestSessionStatus) + 28 rate limiting tests (TestLoginAttempt, TestRateLimitInfo, TestSlidingWindow, TestLockoutEnforcement)
- Status: ✅ MERGED - All session management and rate limiting complete

---

### User Story 3 - Comprehensive Error Handling & Logging (Priority: P2) ✅ COMPLETED (Sprint 1, 3)

**Status**: Complete - US-1.5 (Secure Logging) PR #3 merged, US-3.2 (Error Handling Tests) PR #12 merged

Support and operations teams need comprehensive error handling with clear messages and secure logging that captures operation history without exposing sensitive data.

**Why this priority**: Good error handling improves debugging speed and user experience. Secure logging provides audit trails for compliance and troubleshooting without security risks from exposed credentials.

**Independent Test**: Can be fully tested by:
1. Testing each error condition (404, 403, 409, timeout, etc.)
2. Verifying error messages are user-friendly and actionable
3. Checking logs for comprehensive operation capture
4. Confirming passwords/tokens never appear in logs
5. Validating error recovery guidance

Delivers production-ready error handling and audit-compliant logging.

**Acceptance Scenarios**:

1. **Given** a request to a non-existent resource, **When** the API returns 404, **Then** error is caught and user receives "resource not found (ID: 123)" message

2. **Given** a request for a resource without permission, **When** API returns 403, **Then** user receives "insufficient permissions for this operation" message

3. **Given** a login operation, **When** the operation completes, **Then** logs contain "User login: username=john, result=success" without password

4. **Given** a failed login operation, **When** the operation fails, **Then** logs contain "User login failed: username=john, reason=invalid_credentials" and session_id is never logged

5. **Given** a request that times out, **When** the timeout occurs, **Then** user receives "request timeout - server may be busy, please try again" with retry guidance

**Implementation** (Sprint 1 & 3 - PR #3, #12, completed):
- Created `src/logging_utils.py` with secure logging infrastructure: `log_operation()` function with sensitive field sanitization (password, token, session_id never logged)
- Implemented error handler middleware in src/server.py to catch TaigaException and HTTP errors
- Created error handlers for specific status codes: 404 (Not Found), 403 (Forbidden), 409 (Conflict), timeout/connection errors
- All error messages converted to user-friendly format with recovery guidance ("please try again", "check permissions", "contact support")
- Added logging to authentication, CRUD, and error operations: login/logout events, operation type, resource, user, timestamp, success/failure status
- Secure logging verified: passwords/tokens/session_ids never appear in logs, all sensitive fields sanitized
- Comprehensive error handling test suite: 38 tests covering 7 error categories (validation, auth, 404, 403, 409, timeouts, unexpected exceptions)
- Error path coverage: 90%+ verified across critical paths
- Status: ✅ MERGED - All error handling and secure logging complete

---

### User Story 4 - Code Quality & Consistency (Priority: P2) ✅ COMPLETED (Sprint 1, 3)

**Status**: Complete - US-2.4, US-2.5 (Duplication, Type Hints) PR #4, #5 merged; US-2.2, US-2.3 (Resource Patterns, Cleanup) PR #9, #10 merged

Development teams need consistent code patterns, reduced duplication, and clear type hints for maintainability and reduced bugs.

**Why this priority**: Code quality reduces bugs, improves maintainability, and accelerates development. Consistency patterns and reduced duplication make code easier to reason about and modify.

**Independent Test**: Can be fully tested by:
1. Running automated tools (type checker, linter, formatter) and verifying zero violations
2. Checking for duplicate code patterns and verifying consolidation
3. Reviewing type hints coverage across modules
4. Validating all code follows established patterns
5. Confirming code is readable and documented

Delivers clean, maintainable codebase following established standards.

**Acceptance Scenarios**:

1. **Given** source code, **When** running type checker, **Then** zero type errors are found

2. **Given** source code, **When** running linter, **Then** zero lint violations are found

3. **Given** source code, **When** running formatter, **Then** all code is properly formatted (consistent spacing, imports organized)

4. **Given** multiple similar code patterns in different locations, **When** reviewing the code, **Then** duplication is identified and consolidated

5. **Given** all modules, **When** checking type hints, **Then** 100% of function parameters and returns have type annotations

**Implementation** (Sprint 1 & 3 - PR #4, #5, #9, #10, completed):
- Consolidated duplicate code patterns: 8 assign/unassign operations reduced to shared implementations (PR #4)
- Added comprehensive type hints to all modules: `src/server.py`, `src/taiga_client.py`, `src/validators.py`, `src/logging_utils.py` with full parameter and return type annotations (PR #5)
- Created unified resource access pattern via `get_resource()` method in TaigaClientWrapper (PR #9) - centralizes pytaigaclient API quirks for all 7 resource types
- Replaced 19 direct API get() calls with consistent get_resource() wrapper (PR #9)
- Removed 9 disabled tool definitions (45 lines from server.py) and 26 commented-out code sections (PR #10)
- Code reduction: server.py 2302 → 2218 lines (84 lines removed)
- Created RESOURCE_MAPPING constant documenting parameter patterns (named vs positional) for each resource type
- Updated CLAUDE.md with comprehensive "Resource Access Patterns" and "API Parameter Standardization" documentation
- All code formatted with black and isort (consistent spacing, imports organized)
- Type checking (mypy): Zero type errors
- Linting (flake8): Zero lint violations
- Code coverage maintained with duplication reduction and cleanup
- Status: ✅ MERGED - Code quality, consistency, and duplication reduction complete

---

### User Story 5 - Comprehensive Testing Coverage (Priority: P3) ⏳ IN PROGRESS (Sprint 3-4)

**Status**: Partially complete - US-3.1 (Session Tests) PR #11 merged, US-3.4, US-3.5 in progress (Sprint 4)

QA and development teams need comprehensive test coverage across all code paths and error scenarios to ensure production readiness.

**Why this priority**: Comprehensive testing catches edge cases, prevents regressions, and provides confidence in deployments. High code coverage ensures critical paths are tested.

**Independent Test**: Can be fully tested by:
1. Running full test suite and verifying >85% code coverage
2. Testing all CRUD operations (create, read, update, delete)
3. Testing all error scenarios and edge cases
4. Running integration tests for complete workflows
5. Verifying tests are maintainable and well-organized

Delivers production-grade test coverage with clear test organization.

**Acceptance Scenarios**:

1. **Given** the entire codebase, **When** running coverage analysis, **Then** code coverage is >85%

2. **Given** all CRUD operations, **When** testing each operation, **Then** all tests pass including success paths and error paths

3. **Given** edge cases (empty lists, boundary values, concurrent operations), **When** running test suite, **Then** all edge cases are covered

4. **Given** multiple resource types (projects, epics, stories, tasks), **When** running integration tests, **Then** all workflows pass end-to-end

5. **Given** test suite, **When** running tests, **Then** all tests complete in <10 seconds with zero flakes

**Implementation** (Sprint 3 - PR #11, completed; Sprint 4 - in progress):

**Completed (Sprint 3 - PR #11)**:
- Comprehensive session validation test suite: 28 tests covering SessionInfo, session validation, concurrent limits, cleanup, status checks
- Session code coverage: ≥95% verified
- Test classes: TestSessionInfo (7 tests), TestSessionValidation (5 tests), TestConcurrentSessionLimits (3 tests), TestBackgroundCleanup (3 tests), TestSessionStatus (6 tests)
- All 28 session tests passing (100% pass rate)
- Full test suite: 174 unit tests passing with zero regressions

**In Progress (Sprint 4)**:
- The remaining testing work is split into 4 discrete user stories (US-2.6, US-3.3, US-3.4, US-3.5) documented below
- Target: >85% code coverage across all modules, <10 second test suite execution, zero flaky tests
- Status: ⏳ TODO - Complete remaining test suites and achieve >85% coverage

---

### User Story US-2.6 - Add Input Validation to Delete Operations (Priority: P1) ⏳ READY TO START (Sprint 4)

**Status**: Ready to start - Discovered during planning, added to Sprint 4 scope (no blocking dependencies)

**Story Points**: 3-5

Development teams need to close a validation gap in 3 delete operations that were missing input validation checks, discovered during Sprint 4 planning.

**Why this priority**: Input validation is the first line of defense. Three delete operations (delete_user_story, delete_issue, delete_milestone) were discovered without validation checks during code review, creating a security/stability gap that must be fixed before comprehensive delete testing.

**Independent Test**: Can be fully tested by:
1. Testing each delete operation with negative/invalid IDs and verifying rejection
2. Testing with valid IDs and verifying they reach the API
3. Verifying error messages match the pattern from other delete operations
4. Confirming return types are consistent (DeleteResponse)

**Acceptance Scenarios**:

1. **Given** delete_user_story() is called with a negative user story ID, **When** validation layer processes it, **Then** it is rejected with "user_story_id must be positive integer" before API call

2. **Given** delete_issue() is called with a negative issue ID, **When** validation layer processes it, **Then** it is rejected with "issue_id must be positive integer" before API call

3. **Given** delete_milestone() is called with a negative milestone ID, **When** validation layer processes it, **Then** it is rejected with "milestone_id must be positive integer" before API call

4. **Given** valid delete operations with correct IDs, **When** validation layer processes them, **Then** they pass validation and reach the API layer

5. **Given** all 3 delete operations after validation is added, **When** running the validation test suite, **Then** all invalid inputs are caught and all valid inputs pass

**Implementation** (Sprint 4):
- Add validate_user_story_id() call to delete_user_story() in src/server.py before API call
- Add validate_issue_id() call to delete_issue() in src/server.py before API call
- Add validate_milestone_id() call to delete_milestone() in src/server.py before API call
- Standardize return type for all delete operations to DeleteResponse (consistency check)
- Verify all validation tests pass before proceeding to US-3.4 (delete operation test suite)
- Status: ⏳ TODO - Implement validation fixes and verify tests passing

---

### User Story US-3.3 - Input Validation Test Suite (Priority: P1) ✅ COMPLETE (Sprint 3-4)

**Status**: Complete - Merged to master as PR #13 with comprehensive validation tests

**Story Points**: 8

QA and development teams need comprehensive test coverage for input validation across all 7 resource types to ensure the validation layer is production-ready.

**Why this priority**: Validation is critical; we need proof that validation rules work for all resource types and edge cases. Comprehensive tests give confidence in the validation layer before it's deployed.

**Independent Test**: Can be fully tested by:
1. Testing invalid inputs (negative IDs, empty strings, oversized strings) for all 7 resource types
2. Testing valid inputs to ensure they pass validation
3. Testing edge cases (boundary values, special characters, max-length strings)
4. Verifying all error messages are descriptive and actionable

**Acceptance Scenarios**:

1. **Given** requests with invalid inputs (negative IDs, empty strings, oversized values), **When** running validation test suite, **Then** all invalid inputs are rejected at validation layer with descriptive error messages

2. **Given** validation tests for all 7 resource types (projects, epics, user stories, tasks, issues, sprints, milestones), **When** running the test suite, **Then** all 15+ validation tests pass (11 unit tests + integration tests + verification tasks)

3. **Given** edge case inputs (0, -1, empty string, 255-char string, 256-char string), **When** running edge case tests, **Then** all boundary conditions are correctly handled

4. **Given** valid project creation requests, **When** validation layer processes them, **Then** they pass validation and reach the API layer

5. **Given** integration tests for CRUD operations with validation, **When** running the integration test suite, **Then** all workflows pass end-to-end

**Implementation** (Sprint 3-4 - PR #13, completed):
- ✅ Created comprehensive unit tests for validation across all 7 resource types in tests/auth/test_input_validation.py and resource-specific test files (T006-T016)
- ✅ Created integration tests for CRUD operations with validation in tests/integration/test_validation_integration.py (T010)
- ✅ Verified validation rules for all resource types are implemented in src/validators.py (T017-T018)
- ✅ Verified all validation calls are present in src/server.py CRUD tools (T019)
- ✅ Ran full test suite and verified validation test coverage >85% for validators module (T020)
- ✅ Status: MERGED to master as PR #13 with 15 validation tests passing

---

### User Story US-3.4 - Delete Operation Test Suite (Priority: P2) ⏳ BLOCKED (Sprint 4)

**Status**: Blocked - Cannot start until US-2.6 validation fixes are complete (T030 must complete)

**Story Points**: 8

**Blocking Trigger**: Unblock when US-2.6 task T030 (delete validation tests passing) is complete. This ensures we test the correct (validated) implementation, not the buggy code.

QA and development teams need comprehensive test coverage for all delete operations to ensure they work correctly, handle errors gracefully, and maintain consistent return types.

**Why this priority**: Delete operations are critical and must be thoroughly tested. We have 6 delete operations (projects, epics, user stories, tasks, issues, sprints, milestones) each with multiple error paths (404, 403, 409). High coverage ensures data integrity.

**Independent Test**: Can be fully tested by:
1. Testing each delete operation with valid IDs (success path)
2. Testing each delete operation with invalid/non-existent IDs (error paths)
3. Testing version conflicts and cascade issues
4. Testing that return types are consistent across all operations
5. Running complete delete workflows in integration tests

**Acceptance Scenarios**:

1. **Given** delete operations for all 6 resource types with valid IDs, **When** running success path tests, **Then** all operations succeed and return DeleteResponse

2. **Given** delete operations with invalid IDs (404, 403, 409 errors), **When** error path tests run, **Then** all error conditions are caught and return user-friendly messages

3. **Given** delete operations on resources with version conflicts, **When** attempting to delete, **Then** 409 conflict errors are caught and include version mismatch information

4. **Given** return types from all delete operations, **When** checking consistency, **Then** all return DeleteResponse with identical structure

5. **Given** complete delete workflows (create → read → delete), **When** running integration tests, **Then** all workflows pass end-to-end

**Implementation** (Sprint 4 - After US-2.6 complete):
- Create unit tests for all 6 delete operations covering success paths in tests/projects/test_delete_operations.py, tests/epics/test_delete_operations.py, etc.
- Create unit tests for delete error paths (404, 403, 409) in tests/test_delete_operations.py
- Create integration tests for complete delete workflows in tests/integration/test_workflows.py
- Verify error handling for delete operations in src/server.py: catch 404, 403, 409 with user-friendly messages
- Verify return type consistency: all delete operations return DeleteResponse
- Run all delete operation tests and achieve delete operation coverage ≥90%
- Status: ⏳ TODO - Complete delete operation test suite after US-2.6

---

### User Story US-3.5 - Edge Case & Boundary Testing (Priority: P2) ⏳ READY TO START (Sprint 4)

**Status**: Ready to start - Can run in parallel with US-3.4 on a separate team member (no blocking dependencies)

**Story Points**: 8

QA and development teams need comprehensive edge case and boundary value testing to ensure the system handles unusual inputs, concurrent operations, and resource limits gracefully.

**Why this priority**: Edge cases are where production systems fail. Boundary testing (empty lists, max values, concurrent operations) ensures robustness and prevents customer-impacting bugs.

**Independent Test**: Can be fully tested by:
1. Testing edge cases (empty lists, boundary values like 0, -1, max integers)
2. Testing concurrent operations and resource conflicts
3. Testing timeout and network error scenarios
4. Testing very large bulk operations (10k+ items)
5. Testing session expiry and rate limit edge cases
6. Running complete workflows with all edge case combinations

**Acceptance Scenarios**:

1. **Given** operations with empty list results, boundary values (0, -1, max int), **When** running edge case tests, **Then** all conditions are handled correctly with appropriate responses (empty results vs errors)

2. **Given** concurrent operations modifying the same resource, **When** attempting concurrent modifications, **Then** version conflicts are detected and returned with clear error messages

3. **Given** operations with timeout or network errors, **When** errors occur, **Then** user receives "request timeout - server may be busy, please try again" with retry guidance

4. **Given** very large bulk operations with 10k+ items, **When** processing, **Then** operations complete in <2 seconds with <100MB memory per session

5. **Given** session expiry or rate limit exceeded during operations, **When** conditions occur, **Then** operations fail with appropriate error messages and no data corruption

**Implementation** (Sprint 4 - Parallel with US-3.4):
- Create unit tests for empty list handling in tests/integration/test_edge_cases.py
- Create boundary value tests (0, -1, max int) in tests/integration/test_edge_cases.py
- Create concurrent operation tests for resource conflicts in tests/integration/test_edge_cases.py
- Create timeout/network error tests in tests/error_handling/test_network_errors.py
- Create large bulk operation tests (10k+ items) in tests/integration/test_bulk_operations.py
- Create session expiry and rate limit edge case tests in tests/auth/test_session_edge_cases.py, tests/auth/test_rate_limit_edge_cases.py
- Create complete workflow edge case tests in tests/integration/test_workflows_edge_cases.py
- Verify session expiry handling, rate limit handling, timeout handling, and concurrent modification handling in src/server.py
- Run all edge case tests and achieve >85% total code coverage via pytest --cov
- Status: ⏳ TODO - Complete edge case test suite

---

### Edge Cases

Edge cases are explicitly tested in **User Story US-3.5** (Edge Case & Boundary Testing):

- **Session Expiry**: What happens when a user attempts to perform an operation after their session expires? (Covered by US-3.5 Acceptance Scenario 5)
- **Rate Limiting**: How does the system handle rapid-fire requests that exceed rate limits? (Covered by US-3.5 implementation task: rate limit edge case tests)
- **API Unavailability**: What happens when the Taiga API is temporarily unavailable during an operation? (Covered by US-3.5 Acceptance Scenario 3 - timeout/network error handling)
- **Concurrent Modifications**: How does the system handle concurrent requests modifying the same resource (conflict/version issues)? (Covered by US-3.5 Acceptance Scenario 2)
- **Validation Conflicts**: What happens when input validation rules conflict with Taiga API constraints? (Covered by US-3.3 edge case tests for boundary values)
- **Bulk Operations**: How does the system handle very large bulk operations (lists with 10k+ items)? (Covered by US-3.5 Acceptance Scenario 4 - <2 seconds, <100MB memory constraint)

## Requirements *(mandatory)*

<!--
  ACTION REQUIRED: The content in this section represents placeholders.
  Fill them out with the right functional requirements.
-->

### Functional Requirements

- **FR-001**: System MUST validate all input parameters (IDs as positive integers, strings with length limits) before sending to Taiga API

- **FR-002**: System MUST implement session management with automatic expiry (8 hours default) and prevent use of expired sessions

- **FR-003**: System MUST enforce rate limiting on login attempts (max 5 attempts per 60 seconds with 15-minute lockout)

- **FR-004**: System MUST enforce concurrent session limits (max 5 active sessions per user) with clear error messages

- **FR-005**: System MUST catch TaigaException and HTTP errors and convert to user-friendly error messages with recovery guidance

- **FR-006**: System MUST log all operations (authentication, CRUD, errors) without exposing passwords or session tokens in logs

- **FR-007**: System MUST consolidate duplicate code patterns (e.g., assign/unassign operations) to single implementations

- **FR-008**: System MUST provide complete type hints for all functions, parameters, and return values

- **FR-009**: System MUST organize test suite by resource type (auth, projects, epics, user_stories, tasks, issues, sprints) with markers for unit/integration/slow tests

- **FR-010**: System MUST maintain >85% code coverage across all modules with comprehensive edge case testing

- **FR-011**: System MUST support automated formatting (black, isort) and type checking (mypy) with zero violations in CI/CD

- **FR-012**: System MUST implement automatic cleanup of expired sessions and rate limit data to prevent memory leaks

### Key Entities

- **Session**: Represents authenticated user connection with TTL, concurrent limit tracking, and metadata
- **RateLimitInfo**: Tracks login attempts, lockout status, and sliding window for rate limiting
- **ValidationRule**: Encapsulates input validation constraints (type, min/max, pattern) for each operation

## Success Criteria *(mandatory)*

<!--
  ACTION REQUIRED: Define measurable success criteria.
  These must be technology-agnostic and measurable.
-->

### Measurable Outcomes

- **SC-001**: Input validation rejects 100% of invalid inputs (negative IDs, empty strings, oversized values) with clear error messages

- **SC-002**: Sessions automatically expire after 8 hours with subsequent operations rejected with "session expired" error

- **SC-003**: Login rate limiting prevents >5 attempts per 60 seconds with automatic 15-minute lockout on violation

- **SC-004**: Concurrent session limits enforced: maximum 5 active sessions per user with clear error on 6th attempt

- **SC-005**: All operations logged with zero exposure of passwords or session tokens in logs

- **SC-006**: Code duplication reduced by ≥50% through consolidation of similar patterns

- **SC-007**: 100% of functions have complete type hints verified by mypy with zero errors

- **SC-008**: Code coverage >85% measured by pytest-cov across all modules

- **SC-009**: Automated formatting (black, isort) produces zero violations on all source files

- **SC-010**: Linting (flake8) produces zero violations on all source files

- **SC-011**: Full test suite executes in <10 seconds with zero flaky tests

- **SC-012**: Error messages consistently formatted and include recovery guidance for users

### Assumptions

- Session timeout of 8 hours is reasonable default; configurable via environment variable if needed
- Rate limiting (5 attempts per 60 seconds, 15-minute lockout) follows industry best practices
- Concurrent session limit of 5 is appropriate for typical user workloads
- Taiga API errors can be classified into standard categories (404, 403, 409, timeout)
- Type hints are aspirational for production code quality; existing code will be incrementally updated
- Code coverage >85% balances pragmatism with production readiness (100% unrealistic)
- Existing test infrastructure (pytest, conftest fixtures) is adequate for test organization
- **Story Structure**: This specification documents 22 user stories organized into 5 Epic categories (User Stories 1-5). Each epic contains multiple discrete user stories (US-1.1, US-1.2, ..., US-3.5). All 22 stories are part of the hardening feature spanning Sprints 1-4.
- **Feature scope**: This specification encompasses the complete hardening epic (Sprints 1-4), not just new work. Sprints 1-3 are already merged to master; Sprint 4 adds 4 new discrete user stories (US-2.6, US-3.3, US-3.4, US-3.5) to complete the feature.
- **Sprint 4 Stories**:
  - **US-2.6** (Add Input Validation to Delete Operations): 3-5 points, discovered during planning, closes a validation gap in 3 delete operations
  - **US-3.3** (Input Validation Test Suite): 8 points, comprehensive tests for validation layer across all 7 resource types, can run in parallel with US-2.6
  - **US-3.4** (Delete Operation Test Suite): 8 points, blocked by US-2.6 (must implement fixes before testing them)
  - **US-3.5** (Edge Case & Boundary Testing): 8 points, can run in parallel with US-3.4 on a separate team member
  - **Total Sprint 4**: 27-29 points, 4 discrete stories with explicit dependencies and parallel opportunities
- **Feature completion**: Feature is complete at end of Sprint 4 (all 22 user stories done: 18 merged ✅ + 4 new ⏳, >85% coverage). Milestone 1 (v0.2.0) releases this feature; Sprint 5+ are continuation phases
