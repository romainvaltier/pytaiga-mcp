---

description: "Task list for MCP Server Hardening Sprint 4 - Final implementation phase"

---

# Tasks: MCP Server Hardening & Quality Improvements - Sprint 4 (Final Phase)

**Input**: Design documents from `/specs/001-server-hardening/`
**Prerequisites**: Sprints 1-3 complete (18 user stories merged to master), plan.md ✅, spec.md ✅
**Branch**: `001-server-hardening`
**Sprint**: Sprint 4 (Week 7-8)
**Target Completion**: End of Sprint 4 with all 5 user stories complete, >85% code coverage, production-ready

---

## 📊 Sprint 4 Scope Summary

**4 User Stories Remaining** (3 new, 1 discovered):

| Story | Title | Points | PR | Status |
|-------|-------|--------|----|----|
| **US-3.3** | Input Validation Test Suite | 8 | TBD | ✅ Complete (just generated) |
| **US-2.6** | Add Input Validation to Delete Operations | 3-5 | TBD | ⏳ TODO (discovered during planning) |
| **US-3.4** | Delete Operation Test Suite | 8 | TBD | ⏳ TODO |
| **US-3.5** | Edge Case & Boundary Testing | 8 | TBD | ⏳ TODO |
| **Total** | **4 stories** | **27-29** | - | **~2 weeks** |

**Feature Status**: 18/22 user stories complete (82%). Sprint 4 completion → Milestone 1 v0.2.0 (Security Hardened MVP)

---

## Format: `- [ ] [ID] [P?] [Story] Description with file path`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1-US5)
- Include exact file paths in descriptions
- All tasks reference EXISTING code from Sprints 1-3 (in src/ and tests/)

---

## Phase 1: Sprint 4 Setup & Verification (Blocking Prerequisites)

**Purpose**: Verify existing implementation state and prepare for Sprint 4 work

- [ ] T001 Verify all Sprint 1-3 implementations exist: src/validators.py, src/logging_utils.py, src/server.py with Session/RateLimitInfo classes
- [ ] T002 Verify test structure from Sprint 3: tests/auth/, tests/error_handling/, tests/integration/ directories exist
- [ ] T003 [P] Review merged PRs #1-12 and document any changes to core modules since plan.md creation
- [ ] T004 Verify Sprint 3 test count: 200+ tests passing, existing coverage metrics baseline
- [ ] T005 Setup Sprint 4 tracking: Create branch markers for US-3.3, US-2.6, US-3.4, US-3.5 completion

---

## Phase 2: US-3.3 - Input Validation Test Suite (8 points) ✅ COMPLETE

**Goal**: Generate comprehensive test suite for input validation across all 7 resource types (projects, epics, user stories, tasks, issues, sprints, milestones)

**Status**: COMPLETE - Tests generated during planning phase

**Independent Test Criteria**:
- Validation coverage across all resource types
- Success path: valid inputs pass validation
- Error path: invalid inputs rejected with descriptive messages
- Edge cases: boundary values, empty/oversized strings, negative IDs

### Tests for US-3.3 (Test-First Discipline)

- [ ] T006 [P] [US3.3] Unit test: validate negative project ID in tests/auth/test_input_validation.py - verify rejection with "project_id must be positive integer"
- [ ] T007 [P] [US3.3] Unit test: validate empty project name in tests/auth/test_input_validation.py - verify rejection with "project_name is required and cannot be empty"
- [ ] T008 [P] [US3.3] Unit test: validate oversized project name (>255 chars) in tests/auth/test_input_validation.py - verify rejection
- [ ] T009 [P] [US3.3] Unit test: validate valid project creation in tests/auth/test_input_validation.py - verify passes validation
- [ ] T010 [P] [US3.3] Integration test: CRUD operations with validation in tests/integration/test_validation_integration.py covering projects, epics, user_stories, tasks, issues, sprints, milestones
- [ ] T011 [P] [US3.3] Unit test: validate epic ID constraints in tests/projects/test_validation.py
- [ ] T012 [P] [US3.3] Unit test: validate user story field constraints in tests/user_stories/test_validation.py
- [ ] T013 [P] [US3.3] Unit test: validate task field constraints in tests/tasks/test_validation.py
- [ ] T014 [P] [US3.3] Unit test: validate issue field constraints in tests/issues/test_validation.py
- [ ] T015 [P] [US3.3] Unit test: validate sprint field constraints in tests/sprints/test_validation.py
- [ ] T016 [P] [US3.3] Unit test: validate milestone field constraints in tests/milestones/test_validation.py

### Implementation for US-3.3 (Already Complete from Sprints 1-3)

- [ ] T017 [US3.3] Verify validation rules for projects in src/validators.py: project_id, project_name, description, key
- [ ] T018 [US3.3] Verify validation rules for epics, user stories, tasks, issues, sprints, milestones in src/validators.py
- [ ] T019 [US3.3] Verify validation calls in src/server.py: all CRUD tools call validate_input() before API
- [ ] T020 [US3.3] Run full test suite and verify validation test coverage (all 11 tests passing)

**Checkpoint**: US-3.3 Complete - Input Validation Test Suite 100% covered

---

## Phase 3: US-2.6 - Add Input Validation to Delete Operations (3-5 points) ⏳ NEW

**Goal**: Fix missing input validation in 3 delete operations (delete_user_story, delete_issue, delete_milestone) discovered during planning

**Status**: NEW - Discovered during planning, added to Sprint 4 scope per clarifications

**Independent Test Criteria**:
- Invalid IDs rejected before API call
- Valid IDs reach API
- Error messages match pattern from other delete operations
- Return types consistent (DeleteResponse)

### Tests for US-2.6 (Test-First Discipline)

- [ ] T021 [P] [US2.6] Unit test: validate negative user story ID before delete in tests/user_stories/test_validation.py
- [ ] T022 [P] [US2.6] Unit test: validate negative issue ID before delete in tests/issues/test_validation.py
- [ ] T023 [P] [US2.6] Unit test: validate negative milestone ID before delete in tests/milestones/test_validation.py
- [ ] T024 [P] [US2.6] Unit test: valid delete operations pass validation in tests/test_delete_operations.py
- [ ] T025 [US2.6] Integration test: delete operations validation in tests/integration/test_validation_integration.py

### Implementation for US-2.6

- [ ] T026 [US2.6] Add validate_user_story_id() call to delete_user_story() in src/server.py before API call
- [ ] T027 [US2.6] Add validate_issue_id() call to delete_issue() in src/server.py before API call
- [ ] T028 [US2.6] Add validate_milestone_id() call to delete_milestone() in src/server.py before API call
- [ ] T029 [US2.6] Standardize return type for all delete operations to DeleteResponse in src/server.py (consistency)
- [ ] T030 [US2.6] Run validation tests (T021-T025) and verify all passing

**Checkpoint**: US-2.6 Complete - Delete operations validation implemented and tested

---

## Phase 4: US-3.4 - Delete Operation Test Suite (8 points) ⏳ TODO

**Goal**: Comprehensive tests for all 6 delete operations (projects, epics, user stories, tasks, issues, sprints, milestones) covering success and error paths

**Status**: TODO - Starts after US-2.6 validation fix

**Independent Test Criteria**:
- All delete operations tested (success path)
- All error paths tested (invalid ID, 404, 403, 409)
- Return type consistency verified
- Cascade/version conflict handling tested

### Tests for US-3.4 (Test-First Discipline)

- [ ] T031 [P] [US3.4] Unit test: delete project success in tests/projects/test_delete_operations.py - verify DeleteResponse returned
- [ ] T032 [P] [US3.4] Unit test: delete epic success in tests/epics/test_delete_operations.py
- [ ] T033 [P] [US3.4] Unit test: delete user story success in tests/user_stories/test_delete_operations.py (now with validation T026)
- [ ] T034 [P] [US3.4] Unit test: delete task success in tests/tasks/test_delete_operations.py
- [ ] T035 [P] [US3.4] Unit test: delete issue success in tests/issues/test_delete_operations.py (now with validation T027)
- [ ] T036 [P] [US3.4] Unit test: delete sprint success in tests/sprints/test_delete_operations.py
- [ ] T037 [P] [US3.4] Unit test: delete milestone success in tests/milestones/test_delete_operations.py (now with validation T028)
- [ ] T038 [P] [US3.4] Unit test: delete invalid ID errors in tests/test_delete_operations.py - 404, 403, 409 error handling
- [ ] T039 [P] [US3.4] Unit test: delete cascade/version conflict handling in tests/integration/test_delete_conflicts.py
- [ ] T040 [US3.4] Integration test: complete delete workflows in tests/integration/test_workflows.py (delete after create)

### Implementation for US-3.4

- [ ] T041 [US3.4] Verify all 6 delete operations in src/server.py exist and callable (delete_project through delete_milestone)
- [ ] T042 [US3.4] Verify error handling for delete operations: catch 404, 403, 409 with user-friendly messages
- [ ] T043 [US3.4] Verify return type consistency: all delete operations return DeleteResponse
- [ ] T044 [US3.4] Run all delete operation tests (T031-T040) and verify passing
- [ ] T045 [US3.4] Verify delete operation coverage: ≥90% for all 6 operations via pytest --cov

**Checkpoint**: US-3.4 Complete - All delete operations tested with success and error paths

---

## Phase 5: US-3.5 - Edge Case & Boundary Testing (8 points) ⏳ TODO

**Goal**: Comprehensive edge case and boundary value testing across all code paths (validation, session, error handling, CRUD)

**Status**: TODO - Starts after US-3.4

**Independent Test Criteria**:
- Edge cases identified from spec.md covered in tests
- Boundary values tested (empty lists, max values, concurrent operations)
- Timeout/network errors handled
- Resource conflicts (concurrent modifications) tested

### Tests for US-3.5 (Test-First Discipline)

- [ ] T046 [P] [US3.5] Unit test: empty list handling in tests/integration/test_edge_cases.py - verify empty results vs API errors
- [ ] T047 [P] [US3.5] Unit test: boundary value testing (0, -1, max int) in tests/integration/test_edge_cases.py
- [ ] T048 [P] [US3.5] Unit test: concurrent operation handling in tests/integration/test_edge_cases.py - concurrent modifications, version conflicts
- [ ] T049 [P] [US3.5] Unit test: timeout/network error handling in tests/error_handling/test_network_errors.py
- [ ] T050 [P] [US3.5] Unit test: very large bulk operations (10k+ items) in tests/integration/test_bulk_operations.py - memory/performance
- [ ] T051 [P] [US3.5] Unit test: session expiry during operation in tests/auth/test_session_edge_cases.py
- [ ] T052 [P] [US3.5] Unit test: rate limit exceeded during operation in tests/auth/test_rate_limit_edge_cases.py
- [ ] T053 [P] [US3.5] Integration test: complete workflows with edge cases in tests/integration/test_workflows_edge_cases.py

### Implementation for US-3.5

- [ ] T054 [US3.5] Verify session expiry handling: operations fail with "session expired" if TTL exceeded
- [ ] T054 [US3.5] Verify rate limit handling: operations fail with "too many attempts" if rate limit exceeded
- [ ] T056 [US3.5] Verify timeout handling: operations fail with user-friendly message if request times out
- [ ] T057 [US3.5] Verify concurrent modification handling: 409 conflict error with version mismatch info
- [ ] T058 [US3.5] Run all edge case tests (T046-T053) and verify passing
- [ ] T059 [US3.5] Run coverage analysis: pytest --cov=src and verify >85% total coverage across all modules

**Checkpoint**: US-3.5 Complete - All edge cases and boundary conditions tested

---

## Phase 6: Sprint 4 Quality Gates & Validation

**Purpose**: Verify Sprint 4 deliverables meet success criteria and feature is production-ready

- [ ] T060 [P] Code quality: Run black src/ and verify all code formatted
- [ ] T061 [P] Code quality: Run isort src/ and verify imports organized
- [ ] T062 [P] Code quality: Run mypy src/ and verify zero type errors
- [ ] T063 [P] Code quality: Run flake8 src/ and verify zero lint violations
- [ ] T064 Test coverage: Run pytest --cov=src --cov-report=html and verify >85% coverage (all modules)
- [ ] T065 Test performance: Run pytest and verify all tests complete in <10 seconds
- [ ] T066 Test flakiness: Run full test suite 3 times and verify zero flaky tests
- [ ] T067 Documentation: Update CLAUDE.md with Sprint 4 changes (if any new patterns added)
- [ ] T068 Regression: Run full test suite (200+ tests) and verify zero regressions from Sprints 1-3
- [ ] T069 Manual testing: Verify Sprint 4 features work end-to-end (login → create → validate → delete → error handling)

---

## Phase 7: Release & Deployment

**Purpose**: Prepare for v0.2.0 (Security Hardened MVP) release

- [ ] T070 Version bump: Update pyproject.toml version to 0.2.0
- [ ] T071 Changelog: Create CHANGELOG.md entry for v0.2.0 with all features (Sprints 1-4 summary)
- [ ] T072 Git tag: Create git tag v0.2.0 with annotated message
- [ ] T073 PR creation: Create final PR for Sprint 4 with all changes
- [ ] T074 PR review: Team review and approval of Sprint 4 PR
- [ ] T075 Merge: Merge Sprint 4 PR to master
- [ ] T076 GitHub release: Publish v0.2.0 release on GitHub with release notes
- [ ] T077 Documentation: Update README.md with v0.2.0 features and improvements
- [ ] T078 Post-release: Update SPRINT_PLANNING.md to mark feature complete, plan Sprint 5

---

## Dependencies & Execution Order

### Story Dependencies

- **US-3.3** (Input Validation Tests): No dependencies → Can start immediately
- **US-2.6** (Delete Validation Fix): No dependencies on other stories → Can run in parallel with US-3.3
- **US-3.4** (Delete Operation Tests): Depends on US-2.6 validation fix (test after fix) → Start after T030
- **US-3.5** (Edge Case Testing): No dependencies on other stories → Can run in parallel with US-3.4

### Parallel Opportunities

**Week 1 (Day 1-3)**:
- US-3.3 tests (T006-T016) run in parallel
- US-2.6 validation fix (T026-T028) runs in parallel with US-3.3

**Week 1 (Day 4-5)**:
- US-3.4 delete tests (T031-T040) after US-2.6 validation complete (T030)
- US-3.5 edge case tests (T046-T053) can start in parallel with US-3.4 on different team member

**Week 2**:
- Quality gates (T060-T069) run after all user story tests complete
- Release preparation (T070-T078) after quality gates pass

### Suggested Team Allocation (2 developers)

**Developer A**: US-3.3 + US-3.4 (tests first, then validation fix, then delete tests)
- T006-T020 (US-3.3 tests + verification)
- T026-T030 (US-2.6 validation fix)
- T031-T045 (US-3.4 delete tests)

**Developer B**: US-2.6 (fix) + US-3.5 (edge cases in parallel)
- T021-T025 (US-2.6 tests)
- T046-T059 (US-3.5 edge case tests in parallel with Dev A's US-3.4)

**Both**: Quality gates and release
- T060-T078 (quality validation and release prep)

---

## Implementation Strategy

### MVP Scope (Sprints 1-3 Already Complete)

Sprints 1-3 delivered the MVP:
- Input validation framework
- Session management with TTL, rate limiting, concurrent limits
- Secure logging and error handling
- Code quality and type hints
- All deployed to production

### Sprint 4: Final Polish & Comprehensive Testing

Sprint 4 completes the epic with:
1. **Input Validation Test Suite** (US-3.3): Prove all validation rules work
2. **Delete Operation Validation Fix** (US-2.6): Close discovered gap in delete operations
3. **Delete Operation Test Suite** (US-3.4): Comprehensive tests for all delete paths
4. **Edge Case Testing** (US-3.5): Boundary conditions and concurrent scenarios

**Result**: >85% code coverage, production-ready, Milestone 1 (v0.2.0) released

---

## Quality Gates (Must Pass Before Release)

✅ **Phase 6 Gate**: All quality metrics pass
- [ ] Code coverage >85% (measured via pytest-cov)
- [ ] All tests passing (200+ tests from Sprints 1-4)
- [ ] Zero type errors (mypy clean)
- [ ] Zero lint violations (flake8 clean)
- [ ] All code formatted (black/isort compliant)
- [ ] Test suite <10 seconds (performance)
- [ ] Zero flaky tests (reliable)
- [ ] Manual testing passed (end-to-end workflows)

✅ **Release Gate**: v0.2.0 ready
- [ ] Version bumped (0.2.0)
- [ ] Changelog updated
- [ ] PR reviewed and approved
- [ ] All tests passing on master
- [ ] Documentation updated
- [ ] Git tagged (v0.2.0)

---

## Checkpoints

**After US-3.3**: Input validation test suite complete - 11 tests, validation layer proven
**After US-2.6**: Delete operations validation implemented - 3 operations fixed
**After US-3.4**: Delete operations test suite complete - 10 tests, all delete paths covered
**After US-3.5**: Edge case testing complete - 8 tests, boundary conditions covered, >85% coverage achieved
**After Phase 6**: Quality gates pass - code ready for production
**After Phase 7**: v0.2.0 released - Security Hardened MVP deployed

---

## Notes

- All tasks build on Sprints 1-3 work (18 stories already merged)
- Sprint 4 = final 4 stories (US-3.3✅, US-2.6, US-3.4, US-3.5)
- US-2.6 discovered during planning, added to Sprint 4 scope
- Feature complete = end of Sprint 4 (all 5 spec user stories done, >85% coverage)
- Milestone 1 (v0.2.0) releases Sprint 4 work
- Sprint 5+ (distributed sessions, monitoring) are continuation phases
- Each task references existing code paths (no new modules needed)
- Test-first discipline: write tests BEFORE fixes (T021-T023 before T026-T028)
- Commit after each user story completion (US-3.3, US-2.6, US-3.4, US-3.5)
