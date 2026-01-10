# Contributing & Workflow Guide

**Document Purpose**: Define the way of working for implementing the development roadmap
**Last Updated**: 2026-01-10
**Status**: Ready for team adoption

---

## 🎯 Overview

This document defines how we organize development work, create branches, submit PRs, and track progress against the [Development Roadmap](roadmap/).

**Key Principles**:
- ✅ Clear traceability from roadmap to code
- ✅ Simple, predictable workflow (GitHub Flow)
- ✅ Regular integration to main branch
- ✅ Comprehensive PR reviews
- ✅ Automated testing and quality checks

---

## 🌳 Branching Strategy

We use **GitHub Flow** - a simple, effective branching strategy:

```
master (main branch - always deployable)
  ├─ feature/EPIC-1-input-validation ──→ PR → Merge
  ├─ feature/EPIC-1-session-hardening ──→ PR → Merge
  ├─ test/session-validation-tests ──→ PR → Merge
  └─ fix/update-project-parameter-bug ──→ PR → Merge
```

### Branch Types & Naming Conventions

| Type | Pattern | Example | When to Use |
|------|---------|---------|------------|
| **Feature** | `feature/EPIC-#-description` | `feature/EPIC-1-input-validation` | New feature from roadmap |
| **User Story** | `feature/US-#-description` | `feature/US-1.1-password-validation` | Subtask of epic |
| **Bug Fix** | `fix/ISSUE-#-description` | `fix/session-expiration-bug` | Bug fixes (roadmap or discovered) |
| **Testing** | `test/description` | `test/session-validation-tests` | New tests, test improvements |
| **Refactor** | `refactor/description` | `refactor/api-consistency` | Code cleanup (from EPIC-2) |
| **Documentation** | `docs/description` | `docs/roadmap-updates` | Docs changes |
| **Chore** | `chore/description` | `chore/update-dependencies` | Dependencies, config |

### Branch Naming Rules

- Use **lowercase** and **hyphens** (no spaces or underscores)
- Start with **type prefix** (feature, fix, test, refactor, docs, chore)
- Include **epic or issue number** when applicable
- Use **descriptive names** (40-50 chars max)
- Examples:
  - ✅ `feature/EPIC-1-input-validation`
  - ✅ `test/session-lifecycle-tests`
  - ✅ `fix/project-parameter-bug`
  - ❌ `feature/stuff` (too vague)
  - ❌ `EPIC-1-input-validation` (missing type)
  - ❌ `feature/Epic 1 Input Validation` (spaces, mixed case)

---

## 📋 Workflow Steps

### 1. Select Work from Roadmap

Choose from the roadmap in **priority order**:

**From**: `docs/roadmap/SPRINT_PLANNING.md`
- Select assigned sprint stories
- Use this sprint's user stories
- Follow the Definition of Done

**From**: `docs/roadmap/ROADMAP.md`
- Reference epic number and story number
- Review acceptance criteria
- Note subtasks and dependencies

### 2. Create Feature Branch

```bash
# Update main branch
git checkout master
git pull origin master

# Create feature branch
git checkout -b feature/EPIC-1-input-validation

# Verify you're on correct branch
git branch -v  # Should show: * feature/EPIC-1-input-validation
```

### 3. Implement the Feature

Follow these guidelines:

**Code Quality**:
```bash
# Format code before committing
black src/
isort src/

# Type checking
mypy src/

# Linting
flake8 src/

# Run tests
pytest tests/ -v
```

**Commits**:
- Make **atomic commits** (one logical change per commit)
- Write **clear commit messages** (see section below)
- Reference **epic/story number** in commit messages
- Example:
  ```
  feat(EPIC-1): add password validation helper

  Add validate_password() function to validators.py

  - Validate password length (min 8 chars)
  - Validate special characters
  - Add unit tests

  Closes: EPIC-1.1
  ```

### 4. Write/Update Tests

**Before pushing**:
- ✅ Write tests for new functionality
- ✅ Update tests for modified code
- ✅ Run full test suite: `pytest`
- ✅ Check coverage: `pytest --cov=src`
- ✅ Target: >80% coverage for changed code

```bash
# Run tests locally
pytest tests/ -v --cov=src

# Run specific test file
pytest tests/test_validators.py -v

# Run with coverage report
pytest --cov=src --cov-report=html
```

### 5. Create Pull Request

**Before creating PR**:
- ✅ Code is formatted (black, isort)
- ✅ All tests pass locally
- ✅ Coverage meets standards
- ✅ Type checking passes (mypy)
- ✅ Linting passes (flake8)
- ✅ Commit messages are clear
- ✅ Branch is up to date with master

**Create PR on GitHub**:
```bash
git push origin feature/EPIC-1-input-validation
```

Then go to GitHub and create PR with:

```markdown
## Description
Implementing input validation framework (EPIC-1.1)

Adds comprehensive input validation for all tool parameters:
- Integer validation for IDs
- Email validation for invitations
- String length validation
- Custom field whitelisting

## Related Roadmap
- Epic: EPIC-1 (Security Hardening)
- Story: US-1.1 (Input Validation Framework)
- Story Points: 8
- Link: [ROADMAP.md](docs/roadmap/ROADMAP.md#us-11-input-validation-framework)

## Type of Change
- [x] New feature
- [ ] Bug fix
- [ ] Breaking change
- [ ] Documentation update

## Acceptance Criteria Met
- [x] All integer IDs validated (positive integers only)
- [x] Email validated with regex
- [x] String parameters validated for length
- [x] Kwargs parameters whitelisted
- [x] Clear error messages
- [x] Unit tests for validators
- [x] Tests passing (100%)

## Testing
- Unit tests added: `tests/test_validators.py`
- Coverage: 95% for validators.py
- Integration tests: Included in test_server.py

## Checklist
- [x] Code follows style guidelines
- [x] Tests written and passing
- [x] Documentation updated
- [x] No new warnings/errors
- [x] Ready for review
```

### 6. Code Review

**For Reviewers**:
- ✅ Verify against acceptance criteria
- ✅ Check code quality and style
- ✅ Review test coverage
- ✅ Check for security issues
- ✅ Ask clarifying questions
- ✅ Approve or request changes

**For Authors**:
- ✅ Address all review comments
- ✅ Explain reasoning when needed
- ✅ Mark conversations as resolved
- ✅ Request re-review after changes

### 7. Merge & Deploy

**Merge Process**:
```bash
# GitHub will show merge button when:
# - PR is approved
# - All checks pass
# - No conflicts

# Click "Squash and merge" or "Rebase and merge"
# (Avoid "Create a merge commit" to keep history clean)
```

**After Merge**:
- ✅ PR is automatically closed
- ✅ Branch is automatically deleted
- ✅ Update roadmap progress
- ✅ Close related issues
- ✅ Move card in project board (if using)

---

## 📝 Commit Message Format

Follow **Conventional Commits** format:

```
<type>(<scope>): <subject>

<body>

<footer>
```

### Format Details

**Type**: One of:
- `feat` - New feature
- `fix` - Bug fix
- `test` - Test changes
- `refactor` - Code refactoring
- `docs` - Documentation
- `chore` - Config, dependencies
- `style` - Code style (formatting)

**Scope** (optional):
- `EPIC-1` - Security hardening
- `EPIC-2` - Code quality
- `core` - Core functionality
- `api` - API changes
- `tests` - Testing

**Subject**:
- Imperative mood ("add", not "added")
- No period at end
- Max 50 characters
- Lowercase

**Body** (optional):
- Explain what and why (not how)
- Wrap at 72 characters
- Separate from subject with blank line

**Footer** (optional):
- Reference issues: `Closes: #123`
- Reference epics: `Epic: EPIC-1`
- Breaking changes: `BREAKING CHANGE: description`

### Examples

```
feat(EPIC-1): add input validation framework

Add validators.py with comprehensive input validation:
- validate_project_id() - positive integer check
- validate_email() - RFC compliant validation
- validate_subject() - length and content check
- validate_kwargs() - field whitelisting

Includes unit tests with 95% coverage.
Closes: #234
Epic: EPIC-1
```

```
fix(core): handle session expiration correctly

Check session expiry before API calls instead of
only on login. Prevents stale session errors.

Closes: #567
```

```
test(EPIC-3): add session validation test suite

Add comprehensive tests for session management:
- test_invalid_session_id()
- test_expired_session()
- test_concurrent_sessions()
- test_session_cleanup()

Achieves 95% coverage for session code.
Epic: EPIC-3
```

---

## 🔄 Development Workflow by Epic Type

### Feature Work (EPIC-4: Features)

```
1. Create branch: feature/EPIC-4-comment-management
2. Implement feature:
   - Add tools to server.py
   - Add wrapper methods to taiga_client.py
   - Write tests
   - Update docstrings
3. Create PR with reference to EPIC-4
4. Code review (focus on API design, error handling)
5. Merge when approved
6. Update roadmap: Mark US-4.1 complete
```

### Test Work (EPIC-3: Testing)

```
1. Create branch: test/session-validation-tests
2. Write tests:
   - Test valid sessions
   - Test invalid sessions
   - Test expired sessions
   - Test concurrent sessions
3. Create PR with reference to EPIC-3
4. Code review (focus on test coverage, edge cases)
5. Merge when approved
6. Update roadmap: Track coverage improvement
```

### Bug Fix Work (Discovered Issues)

```
1. Create GitHub issue (if not from roadmap)
2. Create branch: fix/session-expiration-bug
3. Fix bug:
   - Identify root cause
   - Write failing test first
   - Fix implementation
   - Verify test passes
4. Create PR with reference to issue
5. Code review
6. Merge when approved
7. Close issue
```

### Refactoring Work (EPIC-2: Quality)

```
1. Create branch: refactor/api-parameter-consistency
2. Refactor code:
   - Update API parameter names
   - Update tests
   - Update documentation
   - No behavior changes
3. Create PR with reference to EPIC-2
4. Code review (focus on consistency, no regressions)
5. Merge when approved
6. Update roadmap: Mark US-2.1 complete
```

---

## 📊 Tracking Progress

### Update Roadmap When:

- ✅ User story PR is merged → Mark as "In Progress" → "Completed"
- ✅ Sprint completes → Update sprint status
- ✅ Epic completes → Mark as "Completed"
- ✅ Release milestone reached → Close and tag release

### GitHub Project Board (Recommended)

Create a project with columns:

```
| Backlog | Sprint Planning | In Progress | Review | Done |
|---------|-----------------|-------------|--------|------|
```

- Backlog: All roadmap items not yet started
- Sprint Planning: Items assigned to current sprint
- In Progress: Branch created, actively developing
- Review: PR opened, awaiting review
- Done: PR merged, task complete

### Link PR to Project

In PR description, add:
```
Relates to: docs/roadmap/ROADMAP.md#us-11-input-validation-framework
```

---

## 🚀 Release Process

### Before Release Tag

1. **Update version** in `pyproject.toml`
2. **Update CHANGELOG.md** with release notes
3. **Create release PR**: `docs/release-vX.Y.Z`
   - List all merged PRs
   - Reference completed epics
   - Note breaking changes
4. **Get approval** from tech lead
5. **Merge release PR**

### Create Release Tag

```bash
git checkout master
git pull origin master

# Create annotated tag
git tag -a v0.2.0 -m "Security Hardened MVP - Roadmap v0.2.0"

# Push tag
git push origin v0.2.0

# GitHub will create release from tag
```

### Release Checklist

- [ ] All epic user stories merged
- [ ] Test coverage meets target (85%+)
- [ ] Security checklist passed
- [ ] Documentation updated
- [ ] CHANGELOG updated
- [ ] Version bumped
- [ ] Release notes written
- [ ] Tag created
- [ ] GitHub release published
- [ ] Team notified

---

## 📋 Definition of Done (DoD) Checklist

Every PR must meet these criteria before merging:

### Code
- [ ] Feature fully implemented
- [ ] No hardcoded values or test data
- [ ] Follows project code style
- [ ] Type hints present
- [ ] Docstrings updated

### Testing
- [ ] Unit tests written (>80% coverage)
- [ ] Integration tests passing (if applicable)
- [ ] Edge cases tested
- [ ] Error paths tested
- [ ] All tests passing locally: `pytest`

### Review
- [ ] Code reviewed by at least 1 person
- [ ] All review comments addressed
- [ ] No blocking comments
- [ ] Security review passed (for security work)

### Documentation
- [ ] Code comments added (where needed)
- [ ] Docstrings/README updated
- [ ] Acceptance criteria verified
- [ ] Related issues/epics referenced

### Quality
- [ ] Code formatted: `black src/` ✅
- [ ] Imports sorted: `isort src/` ✅
- [ ] Type checking: `mypy src/` ✅
- [ ] Linting: `flake8 src/` ✅
- [ ] No new warnings or errors
- [ ] Performance acceptable (no regressions)

### Integration
- [ ] Branch is up to date with master
- [ ] No merge conflicts
- [ ] All CI/CD checks passing
- [ ] Ready for production

---

## 🔒 Code Review Guidelines

### For Reviewers

**What to Check**:
1. ✅ Does it implement the requirement?
2. ✅ Is the code quality good?
3. ✅ Are there security issues?
4. ✅ Is error handling adequate?
5. ✅ Are tests sufficient?
6. ✅ Is documentation clear?
7. ✅ Could it be simpler/clearer?

**How to Comment**:
- Be **respectful** and **constructive**
- Explain **why** (not just what's wrong)
- Suggest **improvements** (not demands)
- Praise **good** code/tests
- Use emoji for quick feedback:
  - 👍 Looks good
  - 💭 Could be improved
  - ⚠️ Potential issue
  - ❌ Blocking issue

**When to Approve**:
- Definition of Done is met
- All blocking issues resolved
- Coverage meets standard
- Code quality is acceptable
- You understand the change

### For Authors

**Respond to Reviews**:
- [ ] Read all comments carefully
- [ ] Ask for clarification if needed
- [ ] Implement requested changes
- [ ] Leave explanatory comments when needed
- [ ] Mark conversations as resolved
- [ ] Request re-review after changes

**Handling Disagreement**:
- Discuss calmly and respectfully
- Ask tech lead if needed
- Remember: goal is better code

---

## 🐛 Handling Bug Fixes

### Bug Found During Development

```
1. Create GitHub issue:
   Title: "Bug: [description]"
   Description: Steps to reproduce, expected vs actual

2. Create fix branch:
   git checkout -b fix/bug-description

3. Fix process:
   - Write failing test first
   - Fix implementation
   - Verify test passes
   - Run full test suite

4. Create PR:
   Link to issue: "Closes: #XXX"
   Reference epic if from roadmap

5. Code review & merge
```

### Critical Bugs (P0)

```
1. If blocker for sprint:
   - Pull it into current sprint
   - Highest priority
   - Skip other work if needed

2. Follow normal PR process
   - But expedited review
   - Tech lead approves

3. Hot-fix if needed:
   - Merge to master immediately
   - Create patch release
   - Document what happened
```

---

## 🔐 Security Guidelines

### Before Committing

- [ ] No hardcoded passwords/tokens
- [ ] No sensitive data in logs
- [ ] No SQL injection vulnerabilities
- [ ] No XSS vulnerabilities
- [ ] Input properly validated
- [ ] Error messages don't expose internals

### In Code Review

- [ ] Check for security issues
- [ ] Verify input validation
- [ ] Check authentication/authorization
- [ ] Review error handling
- [ ] Check for data leaks

---

## 📚 Resources

- **Roadmap**: [docs/roadmap/ROADMAP.md](roadmap/ROADMAP.md)
- **Sprint Planning**: [docs/roadmap/SPRINT_PLANNING.md](roadmap/SPRINT_PLANNING.md)
- **Definition of Done**: [docs/roadmap/SPRINT_PLANNING.md](roadmap/SPRINT_PLANNING.md) - "Definition of Done (DoD)" section
- **Git Workflow**: This document
- **Code Style**: `black` (configured in `pyproject.toml`)
- **Type Hints**: `mypy` (configured in `pyproject.toml`)

---

## 🆘 Common Issues

### "I created a branch but made a mistake"

```bash
# If not pushed yet, just delete and recreate
git branch -D feature/wrong-name
git checkout -b feature/correct-name

# If already pushed, delete remote and local
git push origin --delete feature/wrong-name
git branch -D feature/wrong-name
```

### "I need to update my branch with latest master"

```bash
git fetch origin
git rebase origin/master

# If conflicts, resolve them and:
git rebase --continue
```

### "I committed something to wrong branch"

```bash
# Create new branch with your commits
git branch feature/correct-name

# Reset current branch
git reset --hard origin/master

# Switch to new branch
git checkout feature/correct-name
```

### "How do I preview my changes?"

```bash
# See what changed
git diff

# See changes ready to commit
git diff --cached

# See commits not yet pushed
git log origin/master..HEAD
```

---

## 🎯 Quick Reference

```bash
# Start new feature
git checkout master
git pull origin master
git checkout -b feature/EPIC-1-description

# Before committing
black src/
isort src/
mypy src/
flake8 src/
pytest tests/

# Commit
git add <files>
git commit -m "feat(EPIC-1): description"

# Push and create PR
git push origin feature/EPIC-1-description
# Then create PR on GitHub

# After PR approved
# Merge on GitHub, then locally:
git checkout master
git pull origin master
git branch -d feature/EPIC-1-description
```

---

## 📞 Questions?

- **About branching**: Ask tech lead
- **About testing**: Check test examples in `tests/`
- **About PR process**: See this document
- **About code style**: Run `black src/` and `mypy src/`
- **About roadmap**: See `docs/roadmap/`

---

**Last Updated**: 2026-01-10
**Version**: 1.0
**Status**: Ready for team adoption
**Next Review**: After Sprint 1 completion
