---

description: "Sprint 4 Implementation Tracking - Completing the Server Hardening Epic with Testing & Edge Cases"

---

# Tasks: MCP Server Hardening & Quality Improvements - Sprint 4 (Final Implementation Phase)

**Input**: Feature specification from `/specs/001-server-hardening/spec.md` and `/specs/001-server-hardening/plan.md`
**Prerequisites**: Sprints 1-3 complete (18 user stories merged to master PR #1-13), spec.md ✅, plan.md ✅
**Current Branch**: `001-server-hardening` (HEAD: 13981d1 - critical story structure resolved)
**Sprint**: Sprint 4 (Week 7-8)
**Target Completion**: End of Sprint 4 with all 4 user stories complete (US-2.6, US-3.3✅, US-3.4, US-3.5), >85% code coverage, production-ready for v0.2.0

---

## 📊 Sprint 4 Status Dashboard

**Overall Progress**:
- Sprints 1-3: ✅ 18/18 stories COMPLETE (merged to master)
- Sprint 4: ⏳ 2/4 stories COMPLETE (US-3.3 merged PR #13, US-2.6 complete T030 passing)

**4 User Stories for Sprint 4**:

| Story | Title | Points | Phase | Status | Merged PR |
|-------|-------|--------|-------|--------|-----------|
| **US-3.3** | Input Validation Test Suite | 8 | 2 | ✅ Complete | #13 |
| **US-2.6** | Add Input Validation to Delete Operations | 3-5 | 3 | ✅ Complete | Pending |
| **US-3.4** | Delete Operation Test Suite | 8 | 4 | ⏳ Ready | Pending |
| **US-3.5** | Edge Case & Boundary Testing | 8 | 5 | ⏳ Ready | Pending |
| **Total** | **4 stories** | **27-29** | - | **2/4** | - |

**Key Metrics**:
- Sprint 1-3: 18 stories ✅, 13 PRs merged, 269+ tests, 66% baseline coverage
- Sprint 4: 4 stories, 27-29 points, target >85% final coverage
- Total: 22/22 stories (100% target), Milestone v0.2.0

---

## Phase 1: Sprint 4 Setup & Verification (Complete - 2026-01-12)

**Purpose**: Verify Sprint 1-3 implementations exist and Sprint 4 can begin

**Status**: ✅ **COMPLETE**

**Deliverables**:
- ✅ All Sprint 1-3 implementations verified (validators.py, logging_utils.py, server.py, types.py, taiga_client.py)
- ✅ Test directory structure reorganized (auth/, error_handling/, integration/, resource type directories)
- ✅ 13 merged PRs (#1-13) documented with zero breaking changes
- ✅ Test baseline: 269+ tests passing, 66% coverage established
- ✅ Sprint 4 tracking setup: Spec, Plan, GitHub issues created

**Completed Tasks**:
- [x] T001 ✅ Verify all Sprint 1-3 implementations exist
- [x] T002 ✅ Verify test structure from Sprint 3
- [x] T003 [P] ✅ Review merged PRs #1-13
- [x] T004 ✅ Verify Sprint 3 test count: 269 tests passing
- [x] T005 ✅ Setup Sprint 4 tracking: Spec, Plan, GitHub issues

---

## Phase 2: US-3.3 - Input Validation Test Suite (Complete - PR #13)

**Goal**: Generate comprehensive test suite for input validation across all 7 resource types

**Status**: ✅ **COMPLETE - MERGED TO MASTER (PR #13)**

**GitHub Issues**: #31-#45 (Phase 2) - All completed

**Story Acceptance**: ACHIEVED
- ✅ Requests with invalid inputs rejected at validation layer with descriptive errors
- ✅ Validation tests for all 7 resource types (projects, epics, user_stories, tasks, issues, sprints, milestones)
- ✅ All edge cases (0, -1, empty string, 255-char, 256-char) correctly handled
- ✅ Valid inputs pass validation and reach API layer
- ✅ Integration tests for CRUD operations with validation pass end-to-end

**Completed Tasks**:
- [x] T006 [P] [US3.3] ✅ Unit test: validate negative project ID - tests/auth/test_input_validation.py
- [x] T007 [P] [US3.3] ✅ Unit test: validate empty project name - tests/auth/test_input_validation.py
- [x] T008 [P] [US3.3] ✅ Unit test: validate oversized project name - tests/auth/test_input_validation.py
- [x] T009 [P] [US3.3] ✅ Unit test: validate valid project creation - tests/auth/test_input_validation.py
- [x] T010 [P] [US3.3] ✅ Integration test: CRUD with validation - tests/integration/test_validation_integration.py
- [x] T011 [P] [US3.3] ✅ Unit test: epic ID constraints - tests/projects/test_validation.py
- [x] T012 [P] [US3.3] ✅ Unit test: user story field constraints - tests/user_stories/test_validation.py
- [x] T013 [P] [US3.3] ✅ Unit test: task field constraints - tests/tasks/test_validation.py
- [x] T014 [P] [US3.3] ✅ Unit test: issue field constraints - tests/issues/test_validation.py
- [x] T015 [P] [US3.3] ✅ Unit test: sprint field constraints - tests/sprints/test_validation.py
- [x] T016 [P] [US3.3] ✅ Unit test: milestone field constraints - tests/milestones/test_validation.py
- [x] T017 [US3.3] ✅ Verify validation rules for projects in src/validators.py
- [x] T018 [US3.3] ✅ Verify validation rules for all 7 resource types in src/validators.py
- [x] T019 [US3.3] ✅ Verify validation calls in src/server.py CRUD tools
- [x] T020 [US3.3] ✅ Run full test suite - all validation tests passing

**Checkpoint**: ✅ US-3.3 Complete - Input Validation Test Suite 100% covered, merged to master

---

## Phase 3: US-2.6 - Add Input Validation to Delete Operations (Complete)

**Goal**: Fix missing input validation in 3 delete operations discovered during planning

**Status**: ✅ **COMPLETE** (All 10 tasks complete, all 26 tests passing)

**GitHub Issues**: #46-#55 (Phase 3) - All completed

**Story Acceptance Criteria**:
- Invalid IDs rejected before API call
- Valid IDs reach API
- Error messages match pattern from other delete operations
- Return types consistent (DeleteResponse)

### Tests for US-2.6 (Test-First Discipline)

- [x] T021 [P] [US2.6] ✅ Unit test: validate negative user story ID before delete in tests/user_stories/test_validation.py
- [x] T022 [P] [US2.6] ✅ Unit test: validate negative issue ID before delete in tests/issues/test_validation.py
- [x] T023 [P] [US2.6] ✅ Unit test: validate negative milestone ID before delete in tests/milestones/test_validation.py
- [x] T024 [P] [US2.6] ✅ Unit test: valid delete operations pass validation in tests/test_delete_operations.py
- [x] T025 [US2.6] ✅ Integration test: delete operations validation in tests/integration/test_validation_integration.py

### Implementation for US-2.6

- [x] T026 [US2.6] ✅ Add validate_user_story_id() call to delete_user_story() in src/server.py before API call
- [x] T027 [US2.6] ✅ Add validate_issue_id() call to delete_issue() in src/server.py before API call
- [x] T028 [US2.6] ✅ Add validate_milestone_id() call to delete_milestone() in src/server.py before API call
- [x] T029 [US2.6] ✅ Standardize return type for all delete operations to DeleteResponse in src/server.py
- [x] T030 [US2.6] ✅ Run validation tests (T021-T025) and verify all passing before proceeding to US-3.4

**Blocking Note**: Phase 4 (US-3.4) CANNOT START until T030 completes. Tests in Phase 4 assume validation fixes are in place.

**Checkpoint**: US-2.6 Complete - Delete operations validation implemented and tested

---

## Phase 4: US-3.4 - Delete Operation Test Suite (Ready to Start - UNBLOCKED)

**Goal**: Comprehensive tests for all 6 delete operations with success and error paths

**Status**: ✅ **UNBLOCKED** (Phase 3 task T030 complete, all validation tests passing)

**GitHub Issues**: #56-#70 (Phase 4) - Ready to start

**Note**: US-2.6 validation fixes are now in place. Phase 4 can begin immediately.

**Story Acceptance Criteria**:
- All delete operations tested (success path)
- All error paths tested (invalid ID, 404, 403, 409)
- Return type consistency verified
- Cascade/version conflict handling tested

### Tests for US-3.4 (Test-First Discipline)

- [ ] T031 [P] [US3.4] Unit test: delete project success in tests/projects/test_delete_operations.py
- [ ] T032 [P] [US3.4] Unit test: delete epic success in tests/epics/test_delete_operations.py
- [ ] T033 [P] [US3.4] Unit test: delete user story success (with validation T026) in tests/user_stories/test_delete_operations.py
- [ ] T034 [P] [US3.4] Unit test: delete task success in tests/tasks/test_delete_operations.py
- [ ] T035 [P] [US3.4] Unit test: delete issue success (with validation T027) in tests/issues/test_delete_operations.py
- [ ] T036 [P] [US3.4] Unit test: delete sprint success in tests/sprints/test_delete_operations.py
- [ ] T037 [P] [US3.4] Unit test: delete milestone success (with validation T028) in tests/milestones/test_delete_operations.py
- [ ] T038 [P] [US3.4] Unit test: delete invalid ID errors (404, 403, 409) in tests/test_delete_operations.py
- [ ] T039 [P] [US3.4] Unit test: delete cascade/version conflict handling in tests/integration/test_delete_conflicts.py
- [ ] T040 [US3.4] Integration test: complete delete workflows in tests/integration/test_workflows.py

### Implementation for US-3.4

- [ ] T041 [US3.4] Verify all 6 delete operations in src/server.py exist and callable
- [ ] T042 [US3.4] Verify error handling for delete operations: catch 404, 403, 409 with user-friendly messages
- [ ] T043 [US3.4] Verify return type consistency: all delete operations return DeleteResponse
- [ ] T044 [US3.4] Run all delete operation tests (T031-T040) and verify passing
- [ ] T045 [US3.4] Verify delete operation coverage: ≥90% for all 6 operations via pytest --cov

**Checkpoint**: US-3.4 Complete - All delete operations tested with success and error paths

---

## Phase 5: US-3.5 - Edge Case & Boundary Testing (Ready to Start - Parallel with Phase 4)

**Goal**: Comprehensive edge case and boundary value testing across all code paths

**Status**: ✅ **READY TO START (Parallel with Phase 4)** (No dependencies between US-3.4 and US-3.5)

**GitHub Issues**: #71-#85 (Phase 5) - Created and ready

**Execution Note**: This phase can run in parallel with Phase 4 on a different team member. No dependencies between them. After Phase 3 completion, Phase 4 and Phase 5 can proceed simultaneously.

**Story Acceptance Criteria**:
- Edge cases identified from spec.md covered in tests
- Boundary values tested (empty lists, max values, concurrent operations)
- Timeout/network errors handled
- Resource conflicts (concurrent modifications) tested

### Tests for US-3.5 (Test-First Discipline)

- [ ] T046 [P] [US3.5] Unit test: empty list handling in tests/integration/test_edge_cases.py
- [ ] T047 [P] [US3.5] Unit test: boundary value testing (0, -1, max int) in tests/integration/test_edge_cases.py
- [ ] T048 [P] [US3.5] Unit test: concurrent operation handling in tests/integration/test_edge_cases.py
- [ ] T049 [P] [US3.5] Unit test: timeout/network error handling in tests/error_handling/test_network_errors.py
- [ ] T050 [P] [US3.5] Unit test: very large bulk operations (10k+ items) in tests/integration/test_bulk_operations.py
- [ ] T051 [P] [US3.5] Unit test: session expiry during operation in tests/auth/test_session_edge_cases.py
- [ ] T052 [P] [US3.5] Unit test: rate limit exceeded during operation in tests/auth/test_rate_limit_edge_cases.py
- [ ] T053 [P] [US3.5] Integration test: complete workflows with edge cases in tests/integration/test_workflows_edge_cases.py

### Implementation for US-3.5

- [ ] T054 [US3.5] Verify session expiry handling: operations fail with "session expired" if TTL exceeded
- [ ] T055 [US3.5] Verify rate limit handling: operations fail with "too many attempts" if rate limit exceeded
- [ ] T056 [US3.5] Verify timeout handling: operations fail with user-friendly message if request times out
- [ ] T057 [US3.5] Verify concurrent modification handling: 409 conflict error with version mismatch info
- [ ] T058 [US3.5] Run all edge case tests (T046-T053) and verify passing
- [ ] T059 [US3.5] Run coverage analysis: pytest --cov=src and verify >85% total coverage across all modules

**Checkpoint**: US-3.5 Complete - All edge cases and boundary conditions tested

---

## Phase 6: Sprint 4 Quality Gates & Validation (Pending Phases 2-5)

**Purpose**: Verify Sprint 4 deliverables meet success criteria and feature is production-ready

**Status**: ⏳ **PENDING** (Awaits Phases 2-5 completion)

**GitHub Issues**: #86-#95 (Phase 6) - Created with quality gate checklist

**Execution Note**: This phase gates release approval. All Phases 2-5 must complete with all tests passing before Phase 6 begins.

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

## Phase 7: Release & Deployment (Pending Phase 6)

**Purpose**: Prepare for v0.2.0 (Security Hardened MVP) release

**Status**: ⏳ **PENDING** (Awaits Phase 6 completion - Quality gates must PASS)

**GitHub Issues**: #96-#103 (Phase 7) - Created with release checklist

**Execution Note**: Final phase. Only starts after Phase 6 quality gates pass. Includes version bump, changelog, git tag v0.2.0, and GitHub release publication.

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

- **US-3.3** (Input Validation Tests): ✅ COMPLETE - No dependencies
- **US-2.6** (Delete Validation Fix): No dependencies on other stories → Can run in parallel with US-3.3 (already done)
- **US-3.4** (Delete Operation Tests): **Depends on US-2.6** (T030 must complete first) → Start after T030
- **US-3.5** (Edge Case Testing): No dependencies on other stories → Can run in parallel with US-3.4

### Parallel Opportunities

**Week 1 (Days 1-3)**:
- ✅ US-3.3 complete (merged PR #13)
- US-2.6 validation fix (T021-T030) runs immediately

**Week 1 (Days 4-5)**:
- US-3.4 delete tests (T031-T045) **starts immediately after** US-2.6 validation fix (T030) completes
- US-3.5 edge case tests (T046-T059) **can start in parallel** with US-3.4 on different team member

**Week 2**:
- Quality gates (T060-T069) run after all user story tests complete
- Release preparation (T070-T078) after quality gates pass

### Suggested Team Allocation (2 developers)

**Developer A**: US-2.6 (validation fix) → US-3.4 (delete tests)
- T021-T030 (US-2.6: write tests, then add validation)
- T031-T045 (US-3.4: delete operation tests after US-2.6 validation in place)

**Developer B**: US-3.5 (edge cases in parallel with Dev A's US-3.4)
- T046-T059 (US-3.5: edge case tests can start after T030)

**Both**: Quality gates and release
- T060-T078 (quality validation and release prep)

---

## Implementation Strategy

### Sprints 1-3: MVP Delivered (18 Stories - 100% Complete)

Sprints 1-3 delivered the core MVP:
- ✅ Input validation framework (US-1.1)
- ✅ Session management with TTL, rate limiting, concurrent limits (US-1.2, US-1.3)
- ✅ Secure logging and error handling (US-1.5, US-3.2)
- ✅ Code quality and type hints (US-2.4, US-2.5, US-2.2, US-2.3)
- ✅ Session validation test suite (US-3.1)
- ✅ Input validation test suite (US-3.3)
- ✅ All deployed and merged to master

### Sprint 4: Final Polish & Comprehensive Testing (4 Stories - In Progress)

Sprint 4 completes the epic with:
1. **US-2.6**: Close validation gaps in 3 delete operations (discovered gap, 3-5 points)
2. **US-3.3**: Prove validation works for all resource types (✅ COMPLETE, merged)
3. **US-3.4**: Comprehensive delete operation testing (blocked by US-2.6)
4. **US-3.5**: Edge case and boundary condition testing

**Result**: >85% code coverage, production-ready, Milestone 1 (v0.2.0) released

---

## Quality Gates (Must Pass Before Release)

✅ **Phase 6 Gate**: All quality metrics pass
- [ ] Code coverage >85% (measured via pytest-cov)
- [ ] All tests passing (300+ tests from Sprints 1-4)
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

**After US-3.3 (Phase 2)**: ✅ COMPLETE
- Input validation test suite complete - 11+ tests, validation layer proven, merged to master

**After US-2.6 (Phase 3)**: TODO
- Delete operations validation implemented - 3 operations fixed, 5 tests passing

**After US-3.4 (Phase 4)**: TODO
- Delete operations test suite complete - 10+ tests, all delete paths covered

**After US-3.5 (Phase 5)**: TODO
- Edge case testing complete - 8+ tests, boundary conditions covered, >85% coverage achieved

**After Phase 6**: TODO
- Quality gates pass - code ready for production

**After Phase 7**: TODO
- v0.2.0 released - Security Hardened MVP deployed

---

## Notes

- All 4 Sprint 4 stories build on Sprints 1-3 work (18 stories already merged, 269+ tests)
- US-3.3 already complete (Phase 2 ✅) - merged to master PR #13
- US-2.6 discovered during planning (validation gap), added to Sprint 4 scope
- Feature complete = end of Sprint 4 (all 22 stories done, >85% coverage)
- Milestone 1 (v0.2.0) releases Sprint 4 work
- Sprint 5+ (distributed sessions, monitoring, performance) are continuation phases
- Each task references existing code paths (no new modules needed beyond Sprints 1-3)
- Test-first discipline: write tests BEFORE fixes (T021-T023 before T026-T028)
- Commit after each user story completion (US-2.6, US-3.4, US-3.5)
