# Implementation Plan: US-3.4 Delete Operation Test Suite

## Story Overview

**US-3.4**: Delete Operation Test Suite (8 story points)
**Epic**: EPIC-3 Comprehensive Testing
**Sprint**: Sprint 4 (Weeks 7-8)
**Priority**: 🟠 HIGH
**Status**: Ready to implement (Sprint 1-3 ✅ Complete, US-3.3 ✅ Complete)

## Objective

Create comprehensive test suite for all delete operations to prevent data loss and ensure production-ready delete functionality. Target: 40+ tests covering success paths, error scenarios, cascade behavior, and edge cases. Achieve >70% coverage of delete operation code paths.

## Current State Analysis

### Existing Delete Operations

**6 total delete operations implemented:**

| Function | Parameters | Validation | Error Handling | Current Tests |
|----------|-----------|-----------|----------------|---------------|
| delete_project | session_id, project_id | ✅ validate_project_id | ✅ Consistent | 1 error test |
| delete_user_story | session_id, user_story_id | ❌ None | ✅ Consistent | 1 error test |
| delete_task | session_id, task_id | ✅ validate_task_id | ✅ Consistent | 0 tests |
| delete_issue | session_id, issue_id | ❌ None | ✅ Consistent | 1 error test |
| delete_epic | session_id, epic_id | ✅ validate_epic_id | ✅ Consistent | 1 error test |
| delete_milestone | session_id, milestone_id | ❌ None | ✅ Consistent | 1 error test |

**Note**: Wiki pages have only list/get operations. NO delete_wiki_page() exists. ROADMAP.md test case will be skipped.

### File Structure

- `src/server.py` - Delete tool definitions (6 functions)
- `tests/test_error_handling.py` - Existing error handling tests (5 delete tests)
- `tests/test_server.py` - Existing unit tests (0 delete tests)
- **NEW**: `tests/test_delete_operations.py` - Comprehensive delete test suite (~40 tests)

### Critical Gaps

1. **Success Path Tests**: 0 (no tests verify successful deletion)
2. **Input Validation Tests**: 0 (only 3/6 operations have validation)
3. **Return Format Tests**: 0 (inconsistency not documented)
4. **Session Validation Tests**: 0 (only basic PermissionError tests exist)
5. **Cascade Tests**: 2/6+ scenarios (only project and user_story cascades documented)
6. **Logging Tests**: 0 (no verification of log output)
7. **Multiple Delete Tests**: 0 (concurrent/sequential scenarios untested)

## Implementation Strategy

### Test Organization

Create `/workspaces/pytaiga-mcp/tests/test_delete_operations.py` with **8 test classes, ~40 tests total**:

```
TestDeleteOperationsSetup
├── TestDeleteSuccessPaths (6 tests)
├── TestDeleteInvalidInputs (6 tests)
├── TestDeleteNotFound (6 tests)
├── TestDeleteCascadeBehavior (6 tests)
├── TestDeleteSessionValidation (3 tests)
├── TestDeleteReturnFormats (6 tests)
├── TestDeleteMultipleOperations (3 tests)
└── TestDeleteLogging (4 tests)

Total: 40 tests
```

### Phase 1: Setup & Success Path Tests (2 hours)

**Create TestDeleteOperationsSetup fixture class:**
- Setup authenticated session with mock TaigaClientWrapper
- Create reusable fixtures for all test classes
- Import necessary dependencies (TaigaException, ValidationError, SessionInfo)

**Implement TestDeleteSuccessPaths (6 tests):**

Test successful deletion for each resource:

```python
def test_delete_project_success(self, authenticated_session):
    """Test successful project deletion"""
    session_id, mock_client = authenticated_session
    mock_client.api.projects.delete.return_value = None

    result = src.server.delete_project(session_id=session_id, project_id=1)

    mock_client.api.projects.delete.assert_called_once_with(id=1)
    assert result["status"] == "deleted"
    assert result["project_id"] == 1

def test_delete_user_story_success(self, authenticated_session):
    """Test successful user story deletion"""
    # Similar pattern

def test_delete_task_success(self, authenticated_session):
    """Test successful task deletion"""
    # Similar pattern

def test_delete_issue_success(self, authenticated_session):
    """Test successful issue deletion"""
    # Similar pattern

def test_delete_epic_success(self, authenticated_session):
    """Test successful epic deletion"""
    # Similar pattern

def test_delete_milestone_success(self, authenticated_session):
    """Test successful milestone deletion"""
    # Similar pattern
```

### Phase 2: Invalid Input Tests (1.5 hours)

**Implement TestDeleteInvalidInputs (6 tests):**

Test input validation (or document lack thereof):

```python
def test_delete_project_invalid_id_string(self, authenticated_session):
    """Test project delete with string ID raises ValidationError"""
    session_id, _ = authenticated_session
    with pytest.raises(ValidationError, match="must be an integer"):
        src.server.delete_project(session_id=session_id, project_id="invalid")

def test_delete_project_negative_id(self, authenticated_session):
    """Test project delete with negative ID raises ValidationError"""
    session_id, _ = authenticated_session
    with pytest.raises(ValidationError, match="must be a positive integer"):
        src.server.delete_project(session_id=session_id, project_id=-1)

def test_delete_project_zero_id(self, authenticated_session):
    """Test project delete with zero ID raises ValidationError"""
    session_id, _ = authenticated_session
    with pytest.raises(ValidationError, match="must be a positive integer"):
        src.server.delete_project(session_id=session_id, project_id=0)

def test_delete_user_story_invalid_id(self, authenticated_session):
    """Test user_story delete with string ID (documents NO validation)"""
    session_id, _ = authenticated_session
    # user_story has NO validation - documents current behavior
    mock_client = MagicMock()
    mock_client.api.user_stories.delete.side_effect = TypeError()

    with pytest.raises(TypeError):  # Fails at API layer, not validation
        src.server.delete_user_story(session_id=session_id, user_story_id="invalid")

def test_delete_issue_invalid_id(self, authenticated_session):
    """Test issue delete with string ID (documents NO validation)"""
    # Similar to user_story - NO validation

def test_delete_milestone_invalid_id(self, authenticated_session):
    """Test milestone delete with string ID (documents NO validation)"""
    # Similar to user_story - NO validation
```

### Phase 3: Not Found Tests (1.5 hours)

**Implement TestDeleteNotFound (6 tests):**

Test 404 errors for non-existent resources:

```python
def test_delete_project_not_found(self, authenticated_session):
    """Test deleting non-existent project returns 404"""
    session_id, mock_client = authenticated_session
    mock_client.api.projects.delete.side_effect = TaigaException(
        {"detail": "Not found."}, 404
    )

    with pytest.raises(TaigaException) as exc_info:
        src.server.delete_project(session_id=session_id, project_id=99999)

    assert exc_info.value.status == 404

def test_delete_user_story_not_found(self, authenticated_session):
    """Test deleting non-existent user story returns 404"""
    # Similar pattern

def test_delete_task_not_found(self, authenticated_session):
    """Test deleting non-existent task returns 404"""
    # Similar pattern

def test_delete_issue_not_found(self, authenticated_session):
    """Test deleting non-existent issue returns 404"""
    # Similar pattern

def test_delete_epic_not_found(self, authenticated_session):
    """Test deleting non-existent epic returns 404"""
    # Similar pattern

def test_delete_milestone_not_found(self, authenticated_session):
    """Test deleting non-existent milestone returns 404"""
    # Similar pattern
```

### Phase 4: Cascade Behavior Tests (1.5 hours)

**Implement TestDeleteCascadeBehavior (6 tests):**

Test cascade/dependency constraints:

```python
def test_delete_project_with_user_stories(self, authenticated_session):
    """Test deleting project with user stories returns 409 Conflict"""
    session_id, mock_client = authenticated_session
    mock_client.api.projects.delete.side_effect = TaigaException(
        {"detail": "Cannot delete project with active user stories"}, 409
    )

    with pytest.raises(TaigaException) as exc_info:
        src.server.delete_project(session_id=session_id, project_id=1)

    assert exc_info.value.status == 409

def test_delete_user_story_with_tasks(self, authenticated_session):
    """Test deleting user story with tasks returns 409 Conflict"""
    session_id, mock_client = authenticated_session
    mock_client.api.user_stories.delete.side_effect = TaigaException(
        {"detail": "Cannot delete story with linked tasks"}, 409
    )

    with pytest.raises(TaigaException) as exc_info:
        src.server.delete_user_story(session_id=session_id, user_story_id=1)

    assert exc_info.value.status == 409

def test_delete_epic_with_user_stories(self, authenticated_session):
    """Test deleting epic with linked user stories returns 409"""
    # Similar cascade test for epic

def test_delete_milestone_with_assignments(self, authenticated_session):
    """Test deleting milestone with assigned items returns 409"""
    # Similar cascade test for milestone

def test_delete_task_success_no_dependencies(self, authenticated_session):
    """Test task deletion succeeds (no cascade constraints)"""
    session_id, mock_client = authenticated_session
    mock_client.api.tasks.delete.return_value = None

    result = src.server.delete_task(session_id=session_id, task_id=1)
    assert result["status"] == "deleted"

def test_delete_issue_success_no_dependencies(self, authenticated_session):
    """Test issue deletion succeeds (no cascade constraints)"""
    session_id, mock_client = authenticated_session
    mock_client.api.issues.delete.return_value = None

    result = src.server.delete_issue(session_id=session_id, issue_id=1)
    assert result["status"] == "deleted"
```

### Phase 5: Session Validation Tests (1 hour)

**Implement TestDeleteSessionValidation (3 tests):**

Test authentication/authorization before delete:

```python
def test_delete_project_invalid_session(self):
    """Test delete with invalid session ID raises PermissionError"""
    with pytest.raises(PermissionError):
        src.server.delete_project(session_id="invalid-session", project_id=1)

def test_delete_project_expired_session(self):
    """Test delete with expired session raises PermissionError"""
    session_id = str(uuid.uuid4())
    mock_client = MagicMock()
    mock_client.is_authenticated = True

    session_info = SessionInfo(
        session_id=session_id, client=mock_client, username="test"
    )
    session_info.expires_at = datetime.utcnow() - timedelta(hours=1)
    src.server.active_sessions[session_id] = session_info

    try:
        with pytest.raises(PermissionError):
            src.server.delete_project(session_id=session_id, project_id=1)
    finally:
        if session_id in src.server.active_sessions:
            del src.server.active_sessions[session_id]

def test_delete_project_unauthenticated_client(self):
    """Test delete with unauthenticated client raises PermissionError"""
    session_id = str(uuid.uuid4())
    mock_client = MagicMock()
    mock_client.is_authenticated = False

    src.server.active_sessions[session_id] = SessionInfo(
        session_id=session_id, client=mock_client, username="test"
    )

    try:
        with pytest.raises(PermissionError):
            src.server.delete_project(session_id=session_id, project_id=1)
    finally:
        if session_id in src.server.active_sessions:
            del src.server.active_sessions[session_id]
```

### Phase 6: Return Format Tests (1 hour)

**Implement TestDeleteReturnFormats (6 tests):**

Verify consistent return structure for all resources:

```python
def test_delete_project_return_format(self, authenticated_session):
    """Verify project delete returns correct format"""
    session_id, mock_client = authenticated_session
    mock_client.api.projects.delete.return_value = None

    result = src.server.delete_project(session_id=session_id, project_id=1)

    assert isinstance(result, dict)
    assert "status" in result and result["status"] == "deleted"
    assert "project_id" in result and result["project_id"] == 1

def test_delete_user_story_return_format(self, authenticated_session):
    """Verify user_story delete returns correct format"""
    # Similar verification - documents inconsistency if any

def test_delete_task_return_format(self, authenticated_session):
    """Verify task delete returns correct format"""
    # Similar verification

def test_delete_issue_return_format(self, authenticated_session):
    """Verify issue delete returns correct format"""
    # Similar verification

def test_delete_epic_return_format(self, authenticated_session):
    """Verify epic delete returns correct format"""
    # Similar verification

def test_delete_milestone_return_format(self, authenticated_session):
    """Verify milestone delete returns correct format"""
    # Similar verification
```

### Phase 7: Multiple Delete Tests (1 hour)

**Implement TestDeleteMultipleOperations (3 tests):**

Test concurrent and sequential delete scenarios:

```python
def test_delete_same_resource_twice(self, authenticated_session):
    """Test deleting same resource twice returns 404 on second attempt"""
    session_id, mock_client = authenticated_session

    # First delete succeeds
    mock_client.api.projects.delete.return_value = None
    result1 = src.server.delete_project(session_id=session_id, project_id=1)
    assert result1["status"] == "deleted"

    # Second delete returns 404
    mock_client.api.projects.delete.side_effect = TaigaException(
        {"detail": "Not found."}, 404
    )
    with pytest.raises(TaigaException) as exc_info:
        src.server.delete_project(session_id=session_id, project_id=1)
    assert exc_info.value.status == 404

def test_delete_multiple_resources_success(self, authenticated_session):
    """Test deleting multiple different resources in sequence"""
    session_id, mock_client = authenticated_session

    # Mock all delete operations
    mock_client.api.projects.delete.return_value = None
    mock_client.api.user_stories.delete.return_value = None
    mock_client.api.tasks.delete.return_value = None

    # Delete multiple resources
    r1 = src.server.delete_project(session_id=session_id, project_id=1)
    r2 = src.server.delete_user_story(session_id=session_id, user_story_id=2)
    r3 = src.server.delete_task(session_id=session_id, task_id=3)

    assert all(r["status"] == "deleted" for r in [r1, r2, r3])

def test_delete_cascade_order(self, authenticated_session):
    """Test proper cascade delete order (dependencies before parent)"""
    session_id, mock_client = authenticated_session

    # Project delete fails with 409 (has user stories)
    mock_client.api.projects.delete.side_effect = TaigaException(
        {"detail": "Cannot delete project with active user stories"}, 409
    )

    with pytest.raises(TaigaException):
        src.server.delete_project(session_id=session_id, project_id=1)

    # Delete user story first
    mock_client.api.user_stories.delete.return_value = None
    result = src.server.delete_user_story(session_id=session_id, user_story_id=1)
    assert result["status"] == "deleted"

    # Now project delete succeeds
    mock_client.api.projects.delete.side_effect = None
    mock_client.api.projects.delete.return_value = None
    result = src.server.delete_project(session_id=session_id, project_id=1)
    assert result["status"] == "deleted"
```

### Phase 8: Logging Tests (1 hour)

**Implement TestDeleteLogging (4 tests):**

Verify logging for all delete scenarios:

```python
def test_delete_project_logs_success(self, authenticated_session, caplog):
    """Verify success logging for delete operation"""
    import logging
    caplog.set_level(logging.INFO)

    session_id, mock_client = authenticated_session
    mock_client.api.projects.delete.return_value = None

    src.server.delete_project(session_id=session_id, project_id=1)

    assert "Project 1 deleted successfully" in caplog.text

def test_delete_project_logs_taiga_error(self, authenticated_session, caplog):
    """Verify error logging for TaigaException"""
    import logging
    caplog.set_level(logging.ERROR)

    session_id, mock_client = authenticated_session
    mock_client.api.projects.delete.side_effect = TaigaException(
        {"detail": "Not found."}, 404
    )

    with pytest.raises(TaigaException):
        src.server.delete_project(session_id=session_id, project_id=99999)

    assert "Taiga API error deleting project 99999" in caplog.text

def test_delete_project_logs_unexpected_error(self, authenticated_session, caplog):
    """Verify error logging for unexpected exceptions"""
    import logging
    caplog.set_level(logging.ERROR)

    session_id, mock_client = authenticated_session
    mock_client.api.projects.delete.side_effect = Exception("Unexpected error")

    with pytest.raises(RuntimeError):
        src.server.delete_project(session_id=session_id, project_id=1)

    assert "Unexpected error deleting project 1" in caplog.text

def test_delete_multiple_operations_logs(self, authenticated_session, caplog):
    """Verify logging for multiple delete operations"""
    import logging
    caplog.set_level(logging.INFO)

    session_id, mock_client = authenticated_session
    mock_client.api.projects.delete.return_value = None
    mock_client.api.epics.delete.return_value = None

    src.server.delete_project(session_id=session_id, project_id=1)
    src.server.delete_epic(session_id=session_id, epic_id=2)

    assert "Project 1 deleted successfully" in caplog.text
    assert "Epic 2 deleted successfully" in caplog.text
```

## Critical Files

1. **NEW**: `/workspaces/pytaiga-mcp/tests/test_delete_operations.py` - ~40 tests (new file)
2. **READ**: `/workspaces/pytaiga-mcp/src/server.py` - delete functions at lines 943, 1203, 1407, 1567, 1826, 1975
3. **READ**: `/workspaces/pytaiga-mcp/tests/test_error_handling.py` - existing error patterns
4. **UPDATE**: `/workspaces/pytaiga-mcp/docs/roadmap/SPRINT_PLANNING.md` - mark US-3.4 complete

## Implementation Phases

### Phase 1: Setup & Success Tests (2 hours)
- Create test_delete_operations.py with fixtures
- Implement TestDeleteOperationsSetup class
- Implement TestDeleteSuccessPaths (6 tests)
- Run tests and verify all pass

### Phase 2: Input Validation Tests (1.5 hours)
- Implement TestDeleteInvalidInputs (6 tests)
- Document validation gaps (user_story, issue, milestone)
- Verify tests pass

### Phase 3: Not Found Tests (1.5 hours)
- Implement TestDeleteNotFound (6 tests)
- Verify 404 error handling across all resources
- Run tests

### Phase 4: Cascade Tests (1.5 hours)
- Implement TestDeleteCascadeBehavior (6 tests)
- Test cascade constraints and dependencies
- Verify error codes (409 Conflict)

### Phase 5: Session Validation Tests (1 hour)
- Implement TestDeleteSessionValidation (3 tests)
- Test invalid/expired/unauthenticated sessions
- Verify PermissionError raised

### Phase 6: Return Format Tests (1 hour)
- Implement TestDeleteReturnFormats (6 tests)
- Document any inconsistencies
- Verify standard format

### Phase 7: Multiple Delete Tests (1 hour)
- Implement TestDeleteMultipleOperations (3 tests)
- Test concurrent and cascade scenarios
- Verify proper ordering

### Phase 8: Logging Tests (1 hour)
- Implement TestDeleteLogging (4 tests)
- Verify success and error logging
- Run with caplog fixture

### Phase 9: Quality & Verification (1 hour)
- Format code: `black tests/test_delete_operations.py && isort tests/test_delete_operations.py`
- Run full test suite: `pytest tests/ -v`
- Generate coverage report
- Verify no regressions

## Success Criteria

✅ All US-3.4 acceptance criteria met:
- [x] Delete operations tested with valid IDs (6 success tests)
- [x] Delete with invalid IDs returns proper error (6 validation tests)
- [x] Delete with non-existent IDs returns proper error (6 not found tests)
- [x] Cascade delete behavior tested (6 cascade tests)
- [x] Multiple deletes don't cause issues (3 multiple delete tests)
- [x] Session validation verified before delete (3 session tests)
- [x] Delete return values correct format (6 return format tests)
- [x] Logging verified for delete operations (4 logging tests)

**Total: 40 new delete operation tests**

## Verification Checklist

- [ ] All 40 new tests passing
- [ ] Total test suite: 307+ tests passing (267 existing + 40 new)
- [ ] No regressions in existing tests
- [ ] Code formatted with black and isort
- [ ] All 6 delete operations tested
- [ ] All 8 acceptance criteria covered
- [ ] SPRINT_PLANNING.md updated
- [ ] PR created and merged

## Known Issues & Notes

**Validation Gaps**: 3 operations (user_story, issue, milestone) currently have NO input validation. Tests will document this behavior, and it's recommended for future enhancement.

**Return Type Inconsistency**: delete_project returns DeleteResponse, others return Dict[str, Any]. Tests will document this for consistency tracking.

**Wiki Page**: ROADMAP.md mentions test_delete_wiki_page() but the operation doesn't exist in codebase. This test will be skipped.

**Version Parameter**: Delete operations don't use version parameter for optimistic locking (documented in CLAUDE.md). Current implementation uses id-only deletion.

## Estimated Effort

Total: **~9-10 hours** (matches 8 story points at ~1.25 hours per point with overhead)

- Phase 1 (Setup & Success): 2 hours
- Phase 2 (Input Validation): 1.5 hours
- Phase 3 (Not Found): 1.5 hours
- Phase 4 (Cascade): 1.5 hours
- Phase 5 (Session): 1 hour
- Phase 6 (Return Format): 1 hour
- Phase 7 (Multiple Delete): 1 hour
- Phase 8 (Logging): 1 hour
- Phase 9 (Quality & Verification): 1 hour

## Risk Assessment

**Low Risk:**
- Only adding tests, not modifying server.py delete functions
- Tests follow established patterns from test_error_handling.py
- Existing 5 delete error tests provide regression safety
- Comprehensive coverage ensures all code paths tested

**Medium Risk:**
- Validation gaps in 3 operations may cause test complications (document behavior instead of enforcing)
- Cascade behavior may vary by Taiga version (mock all scenarios)

## Workflow

1. Create feature branch: `feature/US-3.4-delete-operation-tests`
2. Create test_delete_operations.py with ~40 tests (8 phases)
3. Run tests and verify all pass
4. Format code: `black tests/test_delete_operations.py && isort tests/test_delete_operations.py`
5. Run full test suite: `pytest tests/ -v` (target: 307+ passing)
6. Create PR with title: "feat(EPIC-3): Delete Operation Test Suite (US-3.4)"
7. Squash and merge
8. Update SPRINT_PLANNING.md to mark US-3.4 complete
9. Commit and push documentation
10. Cleanup feature branch
