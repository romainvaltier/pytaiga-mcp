# Implementation Plan: US-2.1 API Parameter Standardization

**Epic**: EPIC-2 Code Quality & Consistency
**Story**: US-2.1 (8 story points)
**Branch**: `feature/US-2.1-api-parameter-standardization`

## Overview

Standardize API parameter naming across all pytaigaclient library calls to improve consistency and maintainability. Focus on LIST, GET, and UPDATE operations where inconsistencies exist.

**Approach**: Standardize within library constraints, minimal code churn, explicit documentation of exceptions

## Critical Inconsistencies Found

### LIST Operations (Priority 1)
- User stories & tasks: `list(project=project_id)` ← Lines 1016, 1296
- All others: `list(project_id=project_id)` ← Lines 1469, 1745, 1916, etc.

### GET Operations (Priority 2)
- Projects: `get(project_id)` positional ← Line 730
- Should be: `get(project_id=project_id)` named (library requirement)

### UPDATE Operations (Priority 3)
- Already consistent, just needs documentation
- Projects: `update(project_id=, version=, project_data=)`
- Others: `edit(resource_id=, version=, **kwargs)`

## Standardization Decisions

### Decision 1: LIST Operations → Use `project_id=` (Named Parameter)

**Rationale:**
- Taiga API query parameter is `project_id` (not `project`)
- Named parameters are explicit and self-documenting
- Only 2 resources need changes vs. 8+ if going the other way
- Aligns with other filter parameters

**Exception:** `milestones.list(project=project_id)` - library enforces `project=`

### Decision 2: GET Operations → Positional (Except Projects)

**Rationale:**
- Projects library uses named `project_id=` - keep as-is
- All others use positional - already correct
- Minimal changes needed

### Decision 3: UPDATE Operations → Document Split Pattern

**Rationale:**
- Library enforces different methods: `update()` vs `edit()`
- This is a library constraint, not our inconsistency
- Already consistent - just add documentation

## Implementation Phases

### Phase 1: Add Documentation Comments (30 min)

Add module-level docstring explaining conventions:

```python
# PARAMETER NAMING CONVENTIONS (enforced by pytaigaclient library):
# - LIST: Use project_id= for filtering (except milestones: project=)
# - GET: Positional for resources (except projects.get(project_id=))
# - UPDATE: Projects uses update(project_id=, version=, project_data=)
#           Others use edit(resource_id=, version=, **kwargs)
# - CREATE: All use project= (already consistent)
# - DELETE: All use id= (already consistent)
```

### Phase 2: Standardize LIST Operations (1 hour)

**Changes Required:**

| Line | Current | New | Resource |
|------|---------|-----|----------|
| 1016 | `user_stories.list(project=project_id, **filters)` | `user_stories.list(project_id=project_id, **filters)` | User Stories |
| 1296 | `tasks.list(project=project_id, **filters)` | `tasks.list(project_id=project_id, **filters)` | Tasks |

**Verification:**
```bash
grep -n "\.list(project=" src/server.py | grep -v "project_id="
# Should only show milestones.list(project=
```

### Phase 3: Standardize GET Operations (30 min)

**Changes Required:**

| Line | Current | New | Resource |
|------|---------|-----|----------|
| 730 | `projects.get(project_id)` | `projects.get(project_id=project_id)` | Projects |

Lines 893, 896 already correct (in update_project function).

### Phase 4: Update Test Suite (2 hours)

**Add Parameter Verification Tests:**

```python
def test_list_user_stories_uses_project_id_parameter(session_setup):
    """Verify list_user_stories uses project_id= (not project=)"""
    session_id, mock_client = session_setup
    mock_client.api.user_stories.list.return_value = []

    src.server.list_user_stories(session_id, 123)

    # Verify called with project_id parameter
    mock_client.api.user_stories.list.assert_called_once_with(project_id=123)

def test_list_tasks_uses_project_id_parameter(session_setup):
    """Verify list_tasks uses project_id= (not project=)"""
    session_id, mock_client = session_setup
    mock_client.api.tasks.list.return_value = []

    src.server.list_tasks(session_id, 123)

    mock_client.api.tasks.list.assert_called_once_with(project_id=123)

def test_get_project_uses_named_parameter(session_setup):
    """Verify projects.get uses named project_id= parameter"""
    session_id, mock_client = session_setup
    mock_project = MagicMock()
    mock_project.id = 123
    mock_client.api.projects.get.return_value = mock_project

    src.server.get_project(session_id, 123)

    # Verify called with named parameter
    mock_client.api.projects.get.assert_called_once_with(project_id=123)
```

**Update Existing Tests:**
- Review existing list/get tests in test_server.py
- Update mock assertions to match new parameter patterns
- Ensure no tests rely on old parameter names

### Phase 5: Update Documentation (1 hour)

**CLAUDE.md - Add Section:**

```markdown
## API Parameter Standardization

The codebase follows these conventions when calling pytaigaclient:

### LIST Operations
- **Standard**: Use `project_id=project_id` for filtering
- **Exception**: `milestones.list(project=project_id)` - library requires `project=`
- **Example**: `user_stories.list(project_id=123, status=1)`

### GET Operations
- **Standard**: Use positional parameters for resource IDs
- **Exception**: `projects.get(project_id=project_id)` - library requires named
- **Example**: `user_stories.get(456)`, `projects.get(project_id=123)`

### UPDATE Operations
- **Projects**: `projects.update(project_id=id, version=v, project_data=dict)`
- **All Others**: `resource.edit(resource_id=id, version=v, **kwargs)`
- **Reason**: Library enforces different method signatures
```

## Critical Files

1. **src/server.py** (lines 1016, 1296, 730) - Main implementation changes
2. **tests/test_server.py** - Add parameter verification tests
3. **CLAUDE.md** - Add parameter standardization section
4. **docs/roadmap/SPRINT_PLANNING.md** - Mark US-2.1 complete

## Verification

### Automated Checks

```bash
# LIST operations - verify project_id= usage
grep -n "\.list(" src/server.py | grep -E "(user_stories|tasks)" | grep -v "project_id="
# Should return 0 results

# Projects GET - verify named parameter
grep -n "projects\.get(" src/server.py | grep -v "project_id=" | grep -v "slug="
# Should return 0 results

# Run all tests
pytest tests/test_server.py -v --cov=src --cov-report=term-missing
```

### Manual Checklist

- [ ] LIST operations use `project_id=` (except milestones)
- [ ] Projects GET uses named `project_id=`
- [ ] UPDATE operations documented (split pattern)
- [ ] New parameter verification tests added
- [ ] All existing tests passing
- [ ] CLAUDE.md updated with conventions
- [ ] Code comments explain library constraints
- [ ] No backward compatibility issues

## Acceptance Criteria

✅ All list operations use consistent parameter pattern
✅ Resource ID parameters follow `{resource}_id` convention
✅ Documentation updated with clear conventions
✅ All tests updated and passing
✅ Backward compatibility maintained (internal changes only)

## Estimated Effort

- Phase 1 (Comments): 30 min
- Phase 2 (LIST): 1 hour
- Phase 3 (GET): 30 min
- Phase 4 (Tests): 2 hours
- Phase 5 (Docs): 1 hour
- **Total**: 5 hours (matches 8 story points)

## Risk Assessment

**Low Risk:**
- Only 3 lines of code change in src/server.py
- Library accepts both parameter forms
- All changes are internal (no MCP tool interface changes)
- Incremental testing after each phase

**Mitigation:**
- Git commit after each phase for easy rollback
- Run full test suite after each change
- Verify with grep patterns before moving forward

## Next Steps

1. Implement Phase 1-3 (core code changes)
2. Add parameter verification tests (Phase 4)
3. Update documentation (Phase 5)
4. Run full test suite
5. Format code (black, isort)
6. Create PR
7. Update SPRINT_PLANNING.md
8. Sprint 2 complete! (24/24 points)
