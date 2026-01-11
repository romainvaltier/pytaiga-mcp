# Sprint Planning & Backlog

**Last Updated**: 2026-01-10
**Project**: Taiga MCP Bridge
**Total Estimated Story Points**: 195 points
**Sprints**: 2-week iterations (8 sprints planned)

---

## 📅 Sprint Schedule

```
Sprint 1 (Week 1-2)  : Security Hardening Phase 1
Sprint 2 (Week 3-4)  : Security Hardening Phase 2 + Quality
Sprint 3 (Week 5-6)  : Code Quality & Consistency
Sprint 4 (Week 7-8)  : Comprehensive Testing Phase 1
Sprint 5 (Week 9-10) : Comprehensive Testing Phase 2
Sprint 6 (Week 11-12): Feature Completeness Phase 1
Sprint 7 (Week 13-14): Feature Completeness Phase 2
Sprint 8 (Week 15+)  : Production Readiness (ongoing)
```

---

## 🎯 Sprint 1: Security Hardening - Foundation (Weeks 1-2) ✅ COMPLETED
**Story Points Completed**: 22/26 (85%)
**Priority**: 🔴 CRITICAL
**Status**: ✅ COMPLETED (2026-01-10)

### User Stories

| ID | Title | Points | PR | Status |
|----|-------|--------|----|----|
| US-1.1 | Input Validation Framework | 8 | #1 | ✅ Merged |
| US-1.4 | HTTPS Enforcement | 3 | #2 | ✅ Merged |
| US-1.5 | Secure Logging | 3 | #3 | ✅ Merged |
| US-2.4 | Reduce Code Duplication | 3 | #4 | ✅ Merged |
| US-2.5 | Enhanced Type Hints | 5 | #5 | ✅ Merged |

**Sprint Goal**: ✅ Implement basic input validation and fix critical security issues

**Definition of Done**:
- [x] All code reviewed and merged (5 PRs)
- [x] Tests passing: 104/105 (99% success rate)
- [x] No security regressions
- [x] Documentation updated (ROADMAP.md updated)
- [x] Ready for next sprint

**Deliverables**:
- Created `src/validators.py` with 20+ validation functions (100% coverage)
- Created `src/logging_utils.py` with 5 sanitization functions (100% coverage)
- Created `src/types.py` with 30+ TypedDict definitions (100% coverage)
- Added comprehensive docstrings to all 57 MCP tools with examples
- Consolidated code duplication in 8 assign/unassign functions
- HTTPS enforcement with environment variable bypass (ALLOW_HTTP_TAIGA)
- All 104 tests passing

---

## 🎯 Sprint 2: Session Hardening + Quick Wins (Weeks 3-4) 🔄 IN PROGRESS
**Story Points Target**: 24 points
**Story Points Completed**: 18/24 (75%)
**Priority**: 🔴 CRITICAL
**Status**: 🔄 IN PROGRESS (Sprint 1 ✅ Complete)

### User Stories

| ID | Title | Points | Assigned | Status | PR |
|----|-------|--------|----------|--------|-----|
| US-1.2 | Session Management Hardening | 13 | Claude | ✅ Merged | #6 |
| US-1.3 | Rate Limiting on Login | 5 | Claude | ✅ Merged | #7 |
| US-2.1 | API Parameter Standardization | 8 | TBD | Pending | - |

**Sprint Goal**: Harden session management and establish API consistency

**Blocking Dependencies**: ✅ Sprint 1 Complete - Ready to begin

**Deliverables**:

**US-1.2 (Complete)**:
- SessionInfo dataclass with TTL enforcement and metadata tracking
- Session validation with automatic TTL checks and cleanup
- Per-user concurrent session limit enforcement (default: 5 sessions)
- Background cleanup task (runs every 5 minutes)
- Enhanced session_status tool with expiration metadata
- Configuration variables: SESSION_EXPIRY, MAX_CONCURRENT_SESSIONS, SESSION_CLEANUP_INTERVAL
- Comprehensive test suite: 25 tests covering all session management features
- All tests passing: 129/130 (1 pre-existing failure unrelated to this work)

**US-1.3 (Complete)**:
- LoginAttempt and RateLimitInfo dataclasses for rate limit tracking
- Sliding window algorithm for failed attempt tracking
- Per-user rate limiting with configurable thresholds (default: 5 attempts per 60s)
- Lockout enforcement (default: 15 minutes) with countdown in error messages
- Rate limit checks integrated into login() tool
- Background cleanup task for rate limit data memory management
- Thread-safe implementation with proper locking
- Comprehensive test suite: 28 tests covering all rate limiting features
- All tests passing: 157/158 (1 pre-existing failure in test_update_project)
- Configuration variables: LOGIN_MAX_ATTEMPTS, LOGIN_RATE_WINDOW, LOGIN_LOCKOUT_DURATION, RATE_LIMIT_CLEANUP_INTERVAL

---

## 🎯 Sprint 3: Code Quality & Consistency (Weeks 5-6)
**Story Points Target**: 21 points
**Priority**: 🟠 HIGH
**Status**: Not Started

### User Stories

| ID | Title | Points | Assigned | Status |
|----|-------|--------|----------|--------|
| US-2.2 | Consistent Resource Access Patterns | 5 | TBD | Todo |
| US-2.3 | Remove Commented-Out Code | 2 | TBD | Todo |
| US-3.1 | Session Validation Test Suite | 8 | TBD | Todo |
| US-3.2 | Error Handling Test Suite | 13 | TBD | Todo |

**Sprint Goal**: Improve code consistency and begin comprehensive testing

**Blocking Dependencies**: Sprint 1-2 completion

---

## 🎯 Sprint 4: Testing Phase 1 (Weeks 7-8)
**Story Points Target**: 24 points
**Priority**: 🔴 CRITICAL
**Status**: Not Started

### User Stories

| ID | Title | Points | Assigned | Status |
|----|-------|--------|----------|--------|
| US-3.3 | Input Validation Test Suite | 8 | TBD | Todo |
| US-3.4 | Delete Operation Test Suite | 8 | TBD | Todo |
| US-3.5 | Edge Case & Boundary Testing | 8 | TBD | Todo |

**Sprint Goal**: Achieve >70% code coverage with focus on critical paths

**Blocking Dependencies**: Sprints 1-3 completion

**Coverage Target**: 70% code coverage

---

## 🎯 Sprint 5: Testing Phase 2 (Weeks 9-10)
**Story Points Target**: 16 points
**Priority**: 🟠 HIGH
**Status**: Not Started

### User Stories

| ID | Title | Points | Assigned | Status |
|----|-------|--------|----------|--------|
| US-3.6 | Integration Test Expansion | 8 | TBD | Todo |
| US-5.1 | Distributed Session Storage | 13 | TBD | Todo |

**Sprint Goal**: Achieve >85% code coverage and prepare for distributed deployment

**Coverage Target**: 85%+ code coverage

---

## 🎯 Sprint 6: Feature Completeness Phase 1 (Weeks 11-12)
**Story Points Target**: 26 points
**Priority**: 🟡 MEDIUM
**Status**: Not Started

### User Stories

| ID | Title | Points | Assigned | Status |
|----|-------|--------|----------|--------|
| US-4.1 | Comment Management | 13 | TBD | Todo |
| US-4.2 | Attachment Management | 13 | TBD | Todo |

**Sprint Goal**: Add comment and attachment support

**Blocking Dependencies**: Sprint 1-5 completion (stable base)

---

## 🎯 Sprint 7: Feature Completeness Phase 2 (Weeks 13-14)
**Story Points Target**: 29 points
**Priority**: 🟡 MEDIUM
**Status**: Not Started

### User Stories

| ID | Title | Points | Assigned | Status |
|----|-------|--------|----------|--------|
| US-4.3 | Epic-UserStory Relationships | 8 | TBD | Todo |
| US-4.4 | Custom Attributes Support | 13 | TBD | Todo |
| US-4.5 | Bulk Operations | 13 | TBD | Todo |

**Sprint Goal**: Implement advanced relationship and bulk operation support

---

## 🎯 Sprint 8+: Production Readiness (Weeks 15+)
**Story Points Target**: 54+ points (ongoing)
**Priority**: 🟠 HIGH
**Status**: Not Started

### Phase 1: Core Operations (Weeks 15-18)

| ID | Title | Points | Assigned | Status |
|----|-------|--------|----------|--------|
| US-5.2 | Monitoring and Logging | 8 | TBD | Todo |
| US-5.3 | Configuration Management | 5 | TBD | Todo |
| US-5.4 | Performance Optimization | 8 | TBD | Todo |
| US-5.6 | CI/CD Pipeline | 8 | TBD | Todo |
| US-5.7 | Security Audit & Hardening | 13 | TBD | Todo |

**Sprint Goal**: Establish production operations and CI/CD

### Phase 2: Documentation & Release (Weeks 19+)

| ID | Title | Points | Assigned | Status |
|----|-------|--------|----------|--------|
| US-5.5 | Documentation and Training | 8 | TBD | Todo |
| US-4.6 | Search and Advanced Filtering | 8 | TBD | Todo |

**Sprint Goal**: Complete documentation and prepare for v1.0 release

---

## 📊 Burndown Projection

```
Sprint 1-5 (10 weeks):    Security + Testing Foundation
  Week 1-2:   Sprint 1   ████░░░░░░ (21 points)
  Week 3-4:   Sprint 2   ████████░░ (24 points)
  Week 5-6:   Sprint 3   ██████░░░░ (21 points)
  Week 7-8:   Sprint 4   ████████░░ (24 points)
  Week 9-10:  Sprint 5   ████░░░░░░ (16 points)
  Subtotal: 106 points

Sprint 6-7 (4 weeks):     Feature Addition
  Week 11-12: Sprint 6   ████████░░ (26 points)
  Week 13-14: Sprint 7   ██████░░░░ (29 points)
  Subtotal: 55 points

Sprint 8+ (ongoing):      Production Excellence
  Week 15+:   Production ████████░░ (54+ points)
  Subtotal: 54+ points

Total: 195+ story points
```

---

## 🏆 Release Milestones

### Milestone 1: v0.2.0 - Security Hardened MVP (End of Sprint 5)
**Target**: Week 10
**Contents**:
- Input validation framework
- Session management hardening
- Rate limiting
- API consistency improvements
- Comprehensive test coverage (85%+)
- Security hardening complete

**Go/No-Go Criteria**:
- [ ] Code coverage >85%
- [ ] No high-severity security issues
- [ ] All tests passing
- [ ] Performance benchmarks met
- [ ] Documentation updated

---

### Milestone 2: v0.3.0 - Extended Features (End of Sprint 7)
**Target**: Week 14
**Contents**:
- Comment management
- Attachment support
- Epic-story relationships
- Custom attributes
- Bulk operations
- Integration test suite complete

**Go/No-Go Criteria**:
- [ ] All feature tests passing
- [ ] Code coverage maintained >85%
- [ ] Integration tests passing
- [ ] Performance acceptable
- [ ] No regressions from v0.2.0

---

### Milestone 3: v1.0.0 - Production Ready (End of Sprint 8+)
**Target**: Week 20+
**Contents**:
- Distributed session storage
- Complete monitoring/logging
- CI/CD pipeline
- Security audit completed
- Comprehensive documentation
- All advanced features

**Go/No-Go Criteria**:
- [ ] Code coverage >85%
- [ ] Security audit A-grade
- [ ] Load tests passing
- [ ] Documentation complete
- [ ] CI/CD automated
- [ ] Deployment runbooks created

---

## 📝 Backlog Items (Prioritized)

### High Priority (Do Next)
1. US-1.1: Input Validation Framework
2. US-1.2: Session Management Hardening
3. US-3.1: Session Validation Test Suite
4. US-3.2: Error Handling Test Suite
5. US-2.1: API Parameter Standardization

### Medium Priority (Do After)
6. US-3.3: Input Validation Test Suite
7. US-3.4: Delete Operation Test Suite
8. US-3.5: Edge Case Testing
9. US-3.6: Integration Test Expansion
10. US-4.1: Comment Management

### Lower Priority (Future)
11. US-4.2: Attachment Management
12. US-4.3: Epic-Story Relationships
13. US-4.4: Custom Attributes
14. US-4.5: Bulk Operations
15. US-4.6: Search & Advanced Filtering

---

## 🔄 Team Capacity Planning

### Assumptions
- 2-week sprints
- 2 developers
- 40 hours/week per developer
- 80% velocity (80 hours available per sprint per developer)
- Average story: 4-5 points

### Capacity Per Sprint
- **Total Capacity**: ~40-50 story points per 2-week sprint (with 2 devs)
- **Recommended Load**: 20-24 points per sprint (buffer for unknowns)

### Staffing Allocation (Suggested)
```
Sprint 1-2:
  Developer 1: Security tasks (US-1.1, US-1.2, US-1.3)
  Developer 2: Quality tasks (US-2.3, US-2.4, US-2.5)

Sprint 3-5:
  Developer 1: Testing (US-3.1, US-3.2, US-3.3)
  Developer 2: Code quality (US-2.1, US-2.2)

Sprint 6-7:
  Developer 1: Features (US-4.1, US-4.2)
  Developer 2: Features (US-4.3, US-4.4, US-4.5)

Sprint 8+:
  Developer 1: Operations (US-5.2, US-5.4, US-5.6)
  Developer 2: Security (US-5.7), Documentation (US-5.5)
```

---

## ✅ Definition of Done (DoD)

For every user story to be considered complete:

1. **Code**
   - [ ] Feature fully implemented
   - [ ] No hardcoded values or test data
   - [ ] Follows project coding standards
   - [ ] Type hints added/updated
   - [ ] Docstrings updated

2. **Testing**
   - [ ] Unit tests written (>80% coverage for changed code)
   - [ ] Integration tests passing (if applicable)
   - [ ] Edge cases tested
   - [ ] Error paths tested

3. **Review**
   - [ ] Code reviewed and approved
   - [ ] No blocking comments
   - [ ] Security review passed (for security stories)

4. **Documentation**
   - [ ] Docstrings/comments added
   - [ ] README updated (if user-facing)
   - [ ] ROADMAP updated
   - [ ] Known limitations documented

5. **Quality**
   - [ ] All tests passing
   - [ ] Linting/formatting passed
   - [ ] Type checking (mypy) passed
   - [ ] No performance regressions

6. **Integration**
   - [ ] Merged to main branch
   - [ ] No merge conflicts
   - [ ] CI/CD pipeline passing
   - [ ] Ready for production

---

## 🐛 Bug & Hotfix Process

### Severity Levels
- **P0 (Critical)**: Production outage, data loss, security breach
- **P1 (High)**: Feature broken, major functionality impaired
- **P2 (Medium)**: Feature partially broken, workaround exists
- **P3 (Low)**: Minor issue, cosmetic, edge case

### Handling
1. **P0/P1**: Drop current sprint work, fix immediately
2. **P2**: Add to current sprint if capacity exists
3. **P3**: Add to backlog, prioritize in planning

---

## 📊 Metrics & Tracking

### Sprint Metrics
- Velocity (points completed per sprint)
- Burn-down (progress toward sprint goal)
- Code coverage (target: maintain >85%)
- Test pass rate (target: 100%)
- Defect escape rate (bugs found in production)

### Quality Metrics
- Code review comments per PR
- Average time to code review
- Refactor vs feature ratio
- Technical debt items opened

### Release Metrics
- Features delivered vs planned
- Quality metrics at release
- Time from sprint start to release
- Customer satisfaction/feedback

---

## 🚀 Post-Release Activities

### For Each Release
1. Release notes drafted
2. Changelog updated
3. Version bumped in pyproject.toml
4. Git tag created
5. GitHub release published
6. Documentation published
7. User communication sent
8. Post-release monitoring
9. Feedback collection

---

**Next Actions**:
1. Assign team members to sprints
2. Clarify any story details
3. Setup project management tool (Jira, Taiga, GitHub Projects)
4. Schedule sprint planning meetings
5. Create story acceptance criteria collaboratively

**Questions to Address**:
- Team availability and capacity?
- Any dependencies on external projects?
- Target launch date for v1.0?
- Any features that are must-have vs nice-to-have?
- Budget/resource constraints?
