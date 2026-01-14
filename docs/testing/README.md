# Testing Documentation - pytaiga-mcp v0.2.0

This directory contains comprehensive testing guides and utilities for the pytaiga-mcp v0.2.0 Security Hardened MVP.

## Quick Navigation

### 📖 For Complete Testing Details
**Start here**: [`E2E_TESTING_GUIDE.md`](./E2E_TESTING_GUIDE.md)

Comprehensive guide covering:
- Prerequisites and setup instructions
- Three testing setup options (Docker, Claude Desktop, Cursor IDE)
- Manual E2E test scenarios with curl examples
- Automated test verification commands
- Python E2E test script template
- Complete verification checklist
- Common issues and solutions
- Security and performance testing
- Monitoring and logging

### 🚀 Quick Start Script
**Use this**: [`quick_e2e_test.sh`](./quick_e2e_test.sh)

```bash
bash docs/testing/quick_e2e_test.sh
```

Automated script that verifies:
- Python 3.10+ availability
- All dependencies installed
- Unit tests passing (smoke test)
- Code quality checks (black, isort, mypy, flake8)
- MCP server startup
- Edge case tests
- Auto-generates summary and next steps

## 🎯 Testing Quick Reference

### Four Quick-Start Options

| Option | Time | Approach | Best For |
|--------|------|----------|----------|
| **Option 1: Script** | 30s | Run `quick_e2e_test.sh` | Quick verification |
| **Option 2: Docker** | 5m | Docker + local testing | Local development |
| **Option 3: Claude Desktop** | 10m | Configure MCP integration | AI-powered testing |
| **Option 4: Manual Curl** | 15m | Test via HTTP directly | Understanding flow |

### Five Testing Strategies

1. **Automated (Default)**: `pytest tests/ -v`
   - Best for: CI/CD pipelines, regression testing
   - Coverage: All 417+ tests

2. **Manual Workflow**: Follow curl scenarios in E2E guide
   - Best for: Understanding API behavior
   - Coverage: Login → CRUD → Logout

3. **Performance Testing**: `time pytest tests/ -q`
   - Best for: Performance verification
   - Target: <2 seconds for full suite

4. **Security Testing**: See E2E guide security section
   - Best for: Validating security controls
   - Coverage: HTTPS, rate limiting, input validation

5. **Integration Testing**: `pytest tests/integration/ -v`
   - Best for: End-to-end workflows
   - Coverage: Full workflows with real Taiga API

## 📋 Complete Verification Checklist

**Server & Setup**
- [ ] Server starts without errors
- [ ] MCP tools are discoverable by client

**Authentication**
- [ ] Login works with valid credentials
- [ ] Login fails with invalid credentials
- [ ] Session is created and stored
- [ ] Session expires after configured time

**Security Controls**
- [ ] Rate limiting prevents brute force (5 attempts/15 min)
- [ ] HTTPS enforcement blocks HTTP logins
- [ ] Input validation rejects invalid inputs

**CRUD Operations**
- [ ] Create operations work for all resources
- [ ] Read operations return correct data
- [ ] Update operations persist changes
- [ ] Delete operations remove resources

**Quality & Performance**
- [ ] All 417+ tests pass
- [ ] Zero test flakiness (run 3x)
- [ ] Code quality checks pass (black, isort, mypy, flake8)
- [ ] Test performance <2 seconds
- [ ] Error handling returns appropriate messages

**Advanced Features**
- [ ] Type hints are correct
- [ ] Logging captures operations
- [ ] Validation test coverage verified

## 🗂️ Test Coverage by Area

The project has 417+ tests organized by functional area:

| Area | Tests | Coverage |
|------|-------|----------|
| Authentication (login, logout, session) | 45+ | 95%+ |
| Input Validation | 80+ | 90%+ |
| Project CRUD | 60+ | 85%+ |
| Epic CRUD | 50+ | 85%+ |
| User Story CRUD | 50+ | 85%+ |
| Task CRUD | 50+ | 85%+ |
| Issue CRUD | 40+ | 80%+ |
| Milestone/Sprint CRUD | 35+ | 80%+ |
| Error Handling | 40+ | 90%+ |
| Rate Limiting | 25+ | 95%+ |
| Edge Cases & Boundaries | 19+ | 80%+ |
| Session Management | 30+ | 90%+ |
| **TOTAL** | **417+** | **~70%** |

## 🔧 Running Specific Tests

```bash
# All tests
pytest

# Only authentication tests
pytest tests/auth/ -v

# Only validation tests
pytest -m validation -v

# Only integration tests
pytest tests/integration/ -v -m integration

# With coverage report
pytest --cov=src --cov-report=html

# Specific test file
pytest tests/test_server.py -v

# Specific test class
pytest tests/test_server.py::TestTaigaTools::test_login -v
```

## 🐛 Troubleshooting

### "Cannot connect to Taiga"
```bash
# Check Taiga is running
curl http://localhost:9000

# Enable debug logging
export LOG_LEVEL=DEBUG
```

### "HTTPS required" error
```bash
# For local development, disable HTTPS requirement
export ALLOW_HTTP_TAIGA=true
```

### "Rate limit exceeded" during testing
```bash
# Modify rate limit lockout duration
export RATE_LIMIT_LOCKOUT_SECONDS=60
```

### "Session expired" mid-test
```bash
# Increase session TTL for testing
export SESSION_EXPIRY=86400  # 24 hours
```

### Tests not finding MCP tools
```bash
# Ensure server is running
# Check MCP client configuration
# Verify tool definitions in src/server.py
```

## 📊 Expected Results

When everything is configured correctly:

**Quick E2E Test**: ~30-60 seconds ✅
```
✅ Python 3.10+ found
✅ uv found
✅ Unit tests passed
✅ Code quality checks passed
✅ MCP server started successfully
✅ Edge case tests passed
```

**Full Test Suite**: <2 seconds for 417+ tests ✅
```
417 passed in 1.19s
```

**Code Quality**: All tools passing ✅
```
✅ Black formatting OK
✅ isort imports OK
✅ mypy type checking OK
✅ flake8 linting OK
```

## 🎯 Next Steps

1. **Choose a testing approach** from the quick-start options above
2. **Run the quick verification** using `docs/testing/quick_e2e_test.sh`
3. **Follow the complete guide** in `E2E_TESTING_GUIDE.md` for detailed scenarios
4. **Verify all items** in the verification checklist
5. **Test with Claude Desktop** or other MCP client for real-world usage

## 📚 Related Documentation

- **[E2E_TESTING_GUIDE.md](./E2E_TESTING_GUIDE.md)** - Complete testing guide
- **[../CLAUDE.md](../CLAUDE.md)** - Development patterns and architecture
- **[../roadmap/SPRINT_PLANNING.md](../roadmap/SPRINT_PLANNING.md)** - Project progress
- **[../../README.md](../../README.md)** - Main project documentation
- **[../../CHANGELOG.md](../../CHANGELOG.md)** - Release notes for v0.2.0

---

**Last Updated**: 2026-01-13
**Version**: v0.2.0 (Security Hardened MVP)
**Status**: ✅ Ready for Testing & Deployment
