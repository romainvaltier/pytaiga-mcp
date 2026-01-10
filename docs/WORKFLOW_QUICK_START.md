# Git Workflow Quick Start Guide

**For busy developers who want the essentials without reading everything**

---

## 🚀 30-Second Version

```bash
# 1. Update and create branch
git checkout master && git pull origin master
git checkout -b feature/EPIC-1-description

# 2. Work on the feature
# ... make changes, write tests, commit regularly ...
git add .
git commit -m "feat(EPIC-1): your changes"

# 3. Format and test before push
black src/ && isort src/ && pytest tests/ -v

# 4. Push and create PR
git push origin feature/EPIC-1-description
# Go to GitHub and create PR

# 5. After PR is approved, merge on GitHub
# Then pull latest
git checkout master && git pull origin master
```

---

## 🌳 Branch Naming Quick Reference

| Type | Pattern | Example |
|------|---------|---------|
| Feature | `feature/EPIC-#-description` | `feature/EPIC-1-input-validation` |
| User Story | `feature/US-#-description` | `feature/US-1.1-password-validation` |
| Bug Fix | `fix/description` | `fix/session-bug` |
| Test | `test/description` | `test/session-tests` |
| Refactor | `refactor/description` | `refactor/api-consistency` |
| Docs | `docs/description` | `docs/roadmap-updates` |

---

## 📝 Commit Message Template

```
feat(EPIC-1): short description (50 chars max)

Optional detailed explanation of what and why.
Keep to 72 characters per line.

Closes: #123
Epic: EPIC-1
```

**Types**: `feat`, `fix`, `test`, `refactor`, `docs`, `chore`, `style`

---

## ✅ Before Creating PR

```bash
# Format code
black src/
isort src/

# Type check
mypy src/

# Lint
flake8 src/

# Test (must pass!)
pytest tests/ -v --cov=src

# Verify branch is up to date
git fetch origin
git rebase origin/master
```

---

## 📋 PR Description Template

```markdown
## Description
[What does this PR do? Reference the roadmap story]

## Roadmap Reference
- Epic: EPIC-1
- Story: US-1.1 (Input Validation Framework)
- Link: [ROADMAP.md](docs/roadmap/ROADMAP.md)

## Type of Change
- [ ] New feature
- [ ] Bug fix
- [ ] Breaking change
- [ ] Documentation

## Acceptance Criteria
- [ ] Criterion 1
- [ ] Criterion 2
- [ ] Criterion 3

## Testing
- Tests added: [list files]
- Coverage: [percentage]

## Checklist
- [ ] Code formatted (black, isort)
- [ ] Tests passing
- [ ] Coverage >80%
- [ ] Type checking passes
- [ ] Documentation updated
```

---

## 🔄 Typical Workflow Example

**Scenario**: Implementing US-1.1 (Input Validation)

```bash
# Step 1: Start fresh
git checkout master
git pull origin master

# Step 2: Create feature branch
git checkout -b feature/EPIC-1-input-validation

# Step 3: Implement feature
# Edit src/validators.py
# Add validate_project_id(), validate_email(), etc.
# Create tests/test_validators.py with tests
# Update docstrings and comments

# Step 4: Format and check quality
black src/
isort src/
mypy src/
flake8 src/

# Step 5: Run tests
pytest tests/ -v --cov=src
# Should show: 95% coverage, all tests passing ✅

# Step 6: Commit your work
git add src/validators.py tests/test_validators.py
git commit -m "feat(EPIC-1): add input validation framework

Add validators.py with comprehensive input validation:
- validate_project_id() - positive integer check
- validate_email() - RFC compliant validation
- validate_subject() - length validation

Includes unit tests with 95% coverage.

Epic: EPIC-1
"

# Step 7: Push to GitHub
git push origin feature/EPIC-1-input-validation

# Step 8: Create PR on GitHub
# - Set title: "feat(EPIC-1): add input validation framework"
# - Use template above
# - Reference: Closes #XXX (if bug) or Epic: EPIC-1

# Step 9: Code review cycle
# - Reviewer comments
# - You respond and make changes
# - git add, git commit, git push (same branch)
# - Reviewer approves

# Step 10: Merge (on GitHub)
# - Click "Squash and merge" or "Rebase and merge"
# - Confirm

# Step 11: Cleanup
git checkout master
git pull origin master
git branch -d feature/EPIC-1-input-validation
```

---

## 🐛 Quick Bug Fix

```bash
# Create issue on GitHub
# Then fix it

git checkout master && git pull
git checkout -b fix/session-bug

# ... fix the bug, write test ...

black src/ && isort src/ && mypy src/ && pytest tests/

git add .
git commit -m "fix(core): handle session expiration correctly

Check session expiry before API calls instead of only on login.

Closes: #567
"

git push origin fix/session-bug
# Create PR on GitHub, reference the issue
```

---

## 🆘 Oops, I Messed Up

### "I committed to wrong branch"
```bash
git branch feature/correct-name
git reset --hard origin/master
git checkout feature/correct-name
git push -u origin feature/correct-name
```

### "I need to update my branch"
```bash
git fetch origin
git rebase origin/master
# If conflicts: resolve → git rebase --continue
```

### "I need to undo my last commit"
```bash
# Keep changes, undo commit
git reset --soft HEAD~1

# Or: discard commit entirely
git reset --hard HEAD~1
```

---

## ✨ Daily Workflow Checklist

**Start of Day**:
```bash
git checkout master
git pull origin master
git checkout -b feature/EPIC-X-description
```

**During Day**:
```bash
git add .
git commit -m "feat: your changes"
# Repeat as you make progress
```

**End of Day**:
```bash
git push origin feature/EPIC-X-description
# (If not already pushed)
```

**Before PR**:
```bash
black src/ && isort src/ && mypy src/ && flake8 src/
pytest tests/ -v --cov=src
git fetch origin && git rebase origin/master
```

---

## 📊 Status Check Commands

```bash
# See current branch
git branch -v

# See unpushed commits
git log origin/master..HEAD

# See local vs remote
git status

# See what's changed
git diff

# See commits
git log --oneline -10

# See current changes staged
git diff --cached
```

---

## 🎯 Integration with Roadmap

**When starting work**:
1. Choose story from: `docs/roadmap/SPRINT_PLANNING.md`
2. Read requirements from: `docs/roadmap/ROADMAP.md`
3. Create branch: `feature/EPIC-X-Y-description`
4. Reference in PR: "Epic: EPIC-X" or "Closes: #XXX"

**When completing work**:
1. PR merged to master
2. Update `docs/roadmap/SPRINT_PLANNING.md` - Mark story as complete
3. Continue to next story

---

## 🚀 Merging & Releasing

**After PR Approved**:
- Click "Merge" on GitHub (Squash recommended)
- Branch auto-deletes
- You: `git checkout master && git pull origin master`

**Release Process**:
1. All stories for epic complete ✅
2. Create PR: `docs/release-vX.Y.Z`
3. Update `CHANGELOG.md`
4. Get approval
5. Merge PR
6. Tag: `git tag -a vX.Y.Z -m "Release notes"`
7. Push: `git push origin vX.Y.Z`

---

## 💡 Pro Tips

1. **Commit often** - Small, focused commits are easier to review
2. **Push daily** - Don't keep code only local
3. **Rebase, don't merge** - Keeps history clean: `git rebase origin/master`
4. **Write good messages** - Future you will thank you
5. **Test before push** - CI will catch issues, but test first
6. **Keep PRs focused** - One feature per PR, not 5 features
7. **Review code carefully** - Code review catches bugs early
8. **Ask questions** - If something is unclear, ask!

---

## 📞 Help & Issues

**"I'm stuck on something"**
- Check this document again
- Ask on team Slack/Discord
- Ask tech lead

**"I have a question about a story"**
- Check `docs/roadmap/ROADMAP.md` for acceptance criteria
- Ask in PR review if unclear

**"My branch is messy"**
- Don't panic! Create a new clean branch
- Reference the messy one if needed later

**"I need to change something after merge"**
- Create a new PR with the fix
- Reference the original PR

---

## 🎓 Learn More

- **Full details**: [`CONTRIBUTING_WORKFLOW.md`](CONTRIBUTING_WORKFLOW.md)
- **Roadmap**: [`roadmap/ROADMAP.md`](roadmap/ROADMAP.md)
- **Sprint planning**: [`roadmap/SPRINT_PLANNING.md`](roadmap/SPRINT_PLANNING.md)

---

**Version**: 1.0
**Last Updated**: 2026-01-10
**Ready to use**: Yes ✅
