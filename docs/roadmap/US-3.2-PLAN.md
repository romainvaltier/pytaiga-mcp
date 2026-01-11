# Implementation Plan: US-3.2 Error Handling Test Suite

## Story Overview

**US-3.2**: Error Handling Test Suite (13 story points)
**Epic**: EPIC-3 Comprehensive Testing
**Sprint**: Sprint 3 (Weeks 5-6)
**Priority**: 🔴 CRITICAL
**Status**: Ready to implement (Sprint 1-2 ✅ Complete, US-3.1 ✅ Complete)

## Objective

Create comprehensive error handling tests for all resource operations to achieve minimum 90% coverage for error paths and ensure user-friendly error messages.

## Current State Analysis

### ❌ Critical Coverage Gap Identified

**Exploration Findings:**
- **52 MCP tools total** in the codebase
- **41 CRUD operations** with TaigaException error handling
- **0% TaigaException test coverage** ⚠️ CRITICAL GAP
- **0% network error test coverage** ⚠️ HIGH PRIORITY GAP
- **Only 1/41 (2.4%) CRUD operations** have error tests

### ✅ Existing Error Test Coverage (Good)

**Already Well-Tested:**
- `ValidationError`: 44 comprehensive tests in test_validators.py ✅
- `PermissionError`: 5 tests in test_session_management.py ✅
- Rate limiting: 28 tests in test_rate_limiting.py ✅
- HTTPS enforcement: ValueError tests in test_https_enforcement.py ✅

### 🎯 Error Handling Pattern Analysis

**All resource operations follow this consistent pattern:**

```python
# Pattern for operations WITH validation (create, update, delete)
try:
    # 1. Input validation layer
    field = validate_field(field)
    kwargs = validate_kwargs(kwargs, allowed_fields)
except ValidationError as e:
    logger.warning(f"Input validation failed: {e}")
    raise ValueError(str(e))

# 2. API operation layer
try:
    result = taiga_client_wrapper.api.resource.operation(...)
except TaigaException as e:
    logger.error(f"Taiga API error: {e}", exc_info=False)
    raise e
except Exception as e:
    logger.error(f"Unexpected error: {e}", exc_info=True)
    raise RuntimeError(f"Server error: {e}")
```

**Key Observations:**
- 100% consistent TaigaException handling across all resources
- ValidationError → ValueError conversion pattern
- Comprehensive logging on all errors
- Catch-all Exception → RuntimeError wrapper

## US-3.2 Acceptance Criteria Mapping

| Acceptance Criteria | Current Status | Plan |
|---------------------|----------------|------|
| TaigaException handling tested for all resource types | ⚠️ 0% | **CREATE TESTS** |
| 404 Not Found errors properly handled | ⚠️ 0% | **CREATE TESTS** |
| 403 Forbidden errors properly handled | ⚠️ 0% | **CREATE TESTS** |
| Invalid field errors caught and reported | ✅ Complete | Already tested (44 tests) |
| Network timeout errors handled | ⚠️ 0% | **CREATE TESTS** |
| Malformed API responses handled | ⚠️ 0% | **CREATE TESTS** |
| Minimum 90% coverage for error paths | ⚠️ ~30% | **ACHIEVE 90%+** |
| Error messages are user-friendly | ⚠️ Untested | **VERIFY** |

## Implementation Strategy

### Resource Types to Test (7 total)

1. **Projects** (7 operations: create, get, update, delete, list, get_by_slug, list_all)
2. **User Stories** (6 operations: create, get, update, delete, list, get_statuses)
3. **Tasks** (5 operations: create, get, update, delete, list)
4. **Issues** (9 operations: create, get, update, delete, list, get priorities/severities/statuses/types)
5. **Epics** (5 operations: create, get, update, delete, list)
6. **Milestones** (5 operations: create, get, update, delete, list)
7. **Wiki** (2 operations: list, get)

### Test Coverage Approach (Realistic for 13 Story Points)

Given 13 story points (~13 hours), testing ALL 41 CRUD operations would be impractical. Instead, use a **representative sampling strategy**:

**Core Operations per Resource (4 tests each × 7 resources = 28 tests):**
1. **GET not found** (404): Test `get_{resource}()` with non-existent ID
2. **GET forbidden** (403): Test `get_{resource}()` with permission denied
3. **CREATE validation error**: Test `create_{resource}()` with invalid data
4. **UPDATE version conflict**: Test `update_{resource}()` with stale version

**Additional Cross-Cutting Tests (10 tests):**
1. **DELETE cascade error** (2 tests): Projects, User Stories
2. **Network timeout** (3 tests): Connection timeout, read timeout, request timeout
3. **Malformed response** (2 tests): Invalid JSON, missing required fields
4. **Unexpected exception** (3 tests): Generic error handling, RuntimeError wrapping

**Total: 38 tests in new test_error_handling.py file**

## Implementation Phases

### Phase 1: Create test_error_handling.py Structure (30 min)

Create new file `/workspaces/pytaiga-mcp/tests/test_error_handling.py` with fixture and test class shells.

### Phase 2: Implement Resource Error Tests (4.5 hours)

For each resource type (projects, user_stories, tasks, issues, epics, milestones, wiki), implement 4 core tests:
1. `test_get_{resource}_not_found()` - 404 error
2. `test_get_{resource}_forbidden()` - 403 error
3. `test_create_{resource}_validation_error()` - Invalid data
4. `test_update_{resource}_version_conflict()` - Stale version

Use pytest.raises() pattern to verify exception handling.

**Time Estimate:**
- Projects: 40 min (first one, establish pattern)
- User Stories: 30 min
- Tasks: 30 min
- Issues: 30 min
- Epics: 30 min
- Milestones: 30 min
- Wiki: 20 min
- **Total: ~4 hours**

### Phase 3: Implement Cross-Cutting Error Tests (1.5 hours)

#### Network Error Tests (30 min)
- test_connection_timeout()
- test_read_timeout()
- test_connection_error()

#### Malformed Response Tests (30 min)
- test_invalid_json_response()
- test_missing_required_fields()

#### Delete Cascade Error Tests (30 min)
- test_delete_project_with_dependencies()
- test_delete_user_story_cascade_error()

### Phase 4: Run Tests and Verify Coverage (1.5 hours)

1. Run all 38 error handling tests
2. Generate coverage report (target: 90%+ for error paths)
3. Verify error messages are user-friendly
4. Run full test suite (212 tests) for regression check

### Phase 5: Format and Quality Checks (30 min)

- black tests/test_error_handling.py
- isort tests/test_error_handling.py
- mypy tests/test_error_handling.py (optional)

### Phase 6: Documentation (30 min)

Update SPRINT_PLANNING.md with US-3.2 deliverables and mark complete.

## Critical Files

1. **`/workspaces/pytaiga-mcp/tests/test_error_handling.py`** - NEW FILE (create with 38 tests)
2. **`/workspaces/pytaiga-mcp/docs/roadmap/SPRINT_PLANNING.md`** - Mark US-3.2 complete
3. **`/workspaces/pytaiga-mcp/src/server.py`** - Read-only (verify error handling patterns)

## Verification Checklist

- [ ] All 38 tests passing
- [ ] Error path coverage ≥90% verified in coverage report
- [ ] TaigaException handling tested for all 7 resource types (28 tests)
- [ ] Network error handling tested (3 tests)
- [ ] Malformed response handling tested (2 tests)
- [ ] Delete cascade errors tested (2 tests)
- [ ] Error messages verified as user-friendly
- [ ] No regressions in existing 174 tests
- [ ] Code formatted with black and isort
- [ ] SPRINT_PLANNING.md updated

## Workflow (Following "Way of Working")

1. Create branch: `feature/US-3.2-error-handling-tests`
2. Create tests/test_error_handling.py with structure (Phase 1)
3. Implement 28 resource error tests (Phase 2)
4. Implement 10 cross-cutting error tests (Phase 3)
5. Run tests and verify all 38 pass (Phase 4)
6. Generate coverage report and verify ≥90% (Phase 4)
7. Format code with black and isort (Phase 5)
8. Run full test suite (212 tests) - ensure no regressions
9. Create PR with title: "feat(EPIC-3): Error Handling Test Suite (US-3.2)"
10. Squash and merge
11. Update SPRINT_PLANNING.md
12. Commit and push documentation update

## Estimated Effort

Total: **~8-9 hours** (matches 13 story points at ~40 min per point)

- Phase 1 (Structure): 30 min
- Phase 2 (Resource tests): 4 hours
- Phase 3 (Cross-cutting tests): 1.5 hours
- Phase 4 (Coverage verification): 1.5 hours
- Phase 5 (Format & quality): 30 min
- Phase 6 (Documentation): 30 min

## Risk Assessment

**Low Risk:**
- Only adding tests, not modifying production code
- Tests follow established mocking patterns
- Existing 174 tests provide regression safety net
- Representative sampling ensures good coverage without exhaustive testing
- Error handling patterns are already consistent across codebase

## Success Criteria

✅ All US-3.2 acceptance criteria met:
- TaigaException handling tested for all resource types: **28 tests (4 per resource × 7)** ✅
- 404 Not Found errors properly handled: **7 tests (1 per resource)** ✅
- 403 Forbidden errors properly handled: **7 tests (1 per resource)** ✅
- Invalid field errors caught and reported: **Already tested (44 tests in test_validators.py)** ✅
- Network timeout errors handled: **3 tests** ✅
- Malformed API responses handled: **2 tests** ✅
- Minimum 90% coverage for error paths: **Verified via coverage report** ✅
- Error messages are user-friendly: **Verified in tests** ✅

## Notes

- **Representative Sampling Strategy**: Testing 4 core operations per resource type (28 tests) instead of all 41 CRUD operations provides excellent coverage while remaining feasible for 13 story points
- **Existing Tests Leverage**: ValidationError (44 tests) and PermissionError (5 tests) already comprehensively tested - no duplication needed
- **Pattern-Based Testing**: Since all resource operations follow the same error handling pattern, representative tests provide high confidence across all operations
- **Focus on Critical Paths**: GET not found, CREATE validation, UPDATE version conflict, and DELETE cascade cover the most common real-world error scenarios
- **Cross-Cutting Tests**: Network and malformed response tests validate the catch-all exception handling that wraps all operations
- After US-3.2, error handling will have **comprehensive test coverage** ensuring production-ready error paths
