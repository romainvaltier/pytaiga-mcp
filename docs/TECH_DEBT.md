# Tech Debt & Code Quality Issues

## Tracking Code Quality Improvements

This document tracks identified issues, code quality gaps, and recommended improvements discovered during development.

---

## Issue #1: Missing Input Validation in Delete Operations

**Severity**: 🟠 MEDIUM
**Type**: Code Quality / Bug Fix
**Status**: 📋 Backlog
**Created**: 2026-01-11 (during US-3.4 planning)
**Related Story**: US-2.6
**Effort**: 3-5 story points

### Problem

3 of 6 delete operations lack input validation. They fail at the API layer instead of validation layer, providing poor error messages and inconsistent behavior.

### Current State

| Operation | Validation | Error Handling |
|-----------|-----------|-----------------|
| delete_project | ✅ YES | API layer fails |
| delete_task | ✅ YES | API layer fails |
| delete_epic | ✅ YES | API layer fails |
| delete_user_story | ❌ **NO** | API layer fails |
| delete_issue | ❌ **NO** | API layer fails |
| delete_milestone | ❌ **NO** | API layer fails |

### Root Cause

Operations delete_user_story, delete_issue, and delete_milestone in `src/server.py` do not call validation functions before API calls.

### Impact

- **User Experience**: Poor error messages when invalid IDs provided
- **Code Consistency**: 50% of delete operations have validation
- **Testing**: 18+ tests will need updates when fixed
- **Maintainability**: Inconsistent validation patterns

### Solution

1. **Add validation calls** (src/server.py):
   ```python
   # delete_user_story (line ~1210)
   user_story_id = validate_user_story_id(user_story_id)

   # delete_issue (line ~1574)
   issue_id = validate_issue_id(issue_id)

   # delete_milestone (line ~1982)
   milestone_id = validate_milestone_id(milestone_id)
   ```

2. **Standardize return types** (all 6 operations):
   - Change return type to: `-> DeleteResponse`
   - delete_project already uses this pattern
   - Others need to match

### Files to Modify

- `src/server.py` - Add 3 validation calls, fix return types (3 operations)
- `tests/test_delete_operations.py` - Update 18 tests (Phases 2, 6)

### Testing Impact

**Before Fix** (US-3.4):
```python
# Tests document NO validation - TypeError at API layer
with pytest.raises(TypeError):
    delete_user_story(session_id, user_story_id="invalid")
```

**After Fix** (US-2.6):
```python
# Tests expect ValidationError - consistent with project/task/epic
with pytest.raises(ValidationError, match="must be an integer"):
    delete_user_story(session_id, user_story_id="invalid")
```

### Recommended Timeline

- **Can Start**: Immediately (no blockers)
- **After**: US-3.4 completion (Sprint 4, week 7-8)
- **Sprint**: Sprint 5+ (week 9+)
- **Effort**: 1-2 hours implementation + testing

### Related Documentation

- **Plan**: `/docs/roadmap/US-3.4-PLAN.md` (Line 585+)
- **Backlog**: `/docs/roadmap/SPRINT_PLANNING.md` (Line 425+)
- **Tests**: `/tests/test_delete_operations.py` (Phases 2, 6)

---

## Issue #2: Return Type Inconsistency in Delete Operations

**Severity**: 🟡 LOW
**Type**: Code Consistency
**Status**: 📋 Backlog
**Created**: 2026-01-11 (during US-3.4 planning)
**Grouped With**: US-2.6
**Effort**: Included in US-2.6

### Problem

Delete operations return different types:
- `delete_project()` → `DeleteResponse` (TypedDict with "status" and "project_id")
- All others → `Dict[str, Any]`

### Impact

- **Type Safety**: Inconsistent type hints confuse developers
- **API Contract**: Different return structures for similar operations
- **Testing**: Must handle both patterns

### Solution

Standardize all 6 delete operations to return `DeleteResponse`:

```python
class DeleteResponse(TypedDict):
    status: str  # "deleted"
    {resource}_id: int  # resource-specific ID

# All operations return:
{"status": "deleted", "{resource}_id": value}
```

### Files to Modify

- `src/server.py` - Standardize all delete return types (6 operations)
- `src/types.py` - Ensure DeleteResponse is exported

---

## Issue #3: Wiki Page Delete Operation Doesn't Exist

**Severity**: 🟢 LOW (Documentation)
**Type**: Roadmap Clarification
**Status**: ✅ RESOLVED
**Created**: 2026-01-11 (during US-3.4 planning)
**Fix**: Updated ROADMAP.md

### Problem

ROADMAP.md (line 549) lists `test_delete_wiki_page()` as US-3.4 test case, but no `delete_wiki_page()` operation exists.

### Investigation

Wiki operations available:
- ✅ `list_wiki_pages()`
- ✅ `get_wiki_page()`
- ❌ `delete_wiki_page()` - **NOT IMPLEMENTED**

### Resolution

- ✅ Updated ROADMAP.md to remove non-existent test
- ✅ US-3.4-PLAN.md documents this finding
- ✅ Test suite skips this test

### Action Items

- Future: Consider implementing delete_wiki_page if needed
- Document that wiki operations are read-only for now

---

## Summary Table

| Issue | Severity | Type | Status | Story | Effort |
|-------|----------|------|--------|-------|--------|
| Missing validations | 🟠 MEDIUM | Bug Fix | Backlog | US-2.6 | 3-5 pts |
| Return type inconsistency | 🟡 LOW | Code Quality | Backlog | US-2.6 | Included |
| Wiki delete missing | 🟢 LOW | Documentation | Resolved | N/A | 0 |

---

## Recommendations

### Immediate (This Sprint - Sprint 4)

- ✅ **US-3.4**: Create test suite documenting current behavior (40 tests)
- 📋 **Backlog US-2.6**: Formally schedule for later

### Next Sprint (Sprint 5+)

- 🔄 **US-2.6**: Implement fixes (3-5 points)
  - Add missing validations
  - Standardize return types
  - Update 18 tests

### Future Work

- Consider implementing `delete_wiki_page()` if needed
- Consider version-based optimistic locking for delete operations (per CLAUDE.md)

---

## Testing Strategy

### Phase 1: Document Current Behavior (US-3.4)

```bash
pytest tests/test_delete_operations.py::TestDeleteInvalidInputs -v
# These pass by documenting NO validation exists
```

### Phase 2: Fix and Verify (US-2.6)

```bash
# Make code changes
# Then rerun tests:
pytest tests/test_delete_operations.py::TestDeleteInvalidInputs -v
# Now expect ValidationError instead of TypeError
```

### Full Suite Verification

```bash
pytest tests/ -v  # Target: 307+ tests passing
```

---

## Discovered During

- **Sprint**: Planning Phase (Sprint 4 - US-3.4)
- **Date**: 2026-01-11
- **Method**: Codebase exploration and analysis
- **Impact**: 0 (Testing only, no code changes required for US-3.4)

---

**Last Updated**: 2026-01-11
**Maintained By**: Development Team
**Review Cycle**: After each sprint
