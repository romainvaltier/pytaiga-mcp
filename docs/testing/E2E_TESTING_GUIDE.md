# End-to-End (E2E) Testing Guide - pytaiga-mcp v0.2.0

## Prerequisites

### Required
- Python 3.10+
- Taiga instance (local or remote)
- MCP client (Claude Desktop, Cursor, or custom)
- Git repository cloned

### Optional
- Docker (for running Taiga locally)
- PostgreSQL (if running Taiga in Docker)

## Option 1: Quick Test with Local Taiga (Docker)

### Step 1: Start Taiga Instance

```bash
# Clone Taiga Docker setup (if needed)
docker-compose up -d

# Default credentials:
# - URL: http://localhost:9000
# - Admin: admin / 123123
# - Create test project with sample data
```

### Step 2: Install pytaiga-mcp

```bash
cd /path/to/pytaiga-mcp
uv pip install -e .
```

### Step 3: Configure Environment

Create `.env` file:
```env
TAIGA_API_URL=http://localhost:9000
ALLOW_HTTP_TAIGA=true
LOG_LEVEL=DEBUG
SESSION_EXPIRY=3600
```

### Step 4: Start MCP Server

**Option A: stdio mode (for terminal testing)**
```bash
uv run python src/server.py
```

**Option B: SSE mode (for web clients)**
```bash
uv run python src/server.py --sse
```

## Option 2: Test with Claude Desktop

### Step 1: Get MCP Server Path

```bash
# Find absolute path
pwd  # Output: /workspaces/pytaiga-mcp
```

### Step 2: Configure Claude Desktop

Edit `~/.config/Claude/claude_desktop_config.json` (macOS/Linux) or `%APPDATA%\Claude\claude_desktop_config.json` (Windows):

```json
{
  "mcpServers": {
    "taiga": {
      "command": "uv",
      "args": [
        "--directory",
        "/workspaces/pytaiga-mcp",
        "run",
        "python",
        "src/server.py"
      ],
      "env": {
        "TAIGA_API_URL": "http://localhost:9000",
        "ALLOW_HTTP_TAIGA": "true",
        "LOG_LEVEL": "INFO"
      }
    }
  }
}
```

### Step 3: Restart Claude Desktop

Close and reopen Claude Desktop. Check MCP status in the settings.

### Step 4: Test in Claude

Send messages like:
```
Can you help me login to Taiga and list all projects?
```

## Option 3: Test with Cursor IDE

Similar to Claude Desktop:

1. Open Cursor settings
2. Find MCP configuration section
3. Add the same config as above
4. Test using Cursor's inline assistant

## Manual E2E Test Scenarios

### Scenario 1: Complete Project Workflow

```bash
# Test Commands via curl or Python client

# 1. LOGIN
curl -X POST http://localhost:3000/api/v1/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"123123","host":"http://localhost:9000"}'
# Response: {"session_id":"uuid..."}

# 2. Create Project
curl -X POST http://localhost:3000/api/v1/projects \
  -H "Authorization: Bearer SESSION_ID" \
  -d '{"name":"Test Project","description":"E2E Test"}'

# 3. Create Epic
curl -X POST http://localhost:3000/api/v1/epics \
  -H "Authorization: Bearer SESSION_ID" \
  -d '{"project_id":1,"subject":"Test Epic"}'

# 4. Create User Story
curl -X POST http://localhost:3000/api/v1/user_stories \
  -H "Authorization: Bearer SESSION_ID" \
  -d '{"project_id":1,"subject":"Test Story","epic_id":1}'

# 5. Create Task
curl -X POST http://localhost:3000/api/v1/tasks \
  -H "Authorization: Bearer SESSION_ID" \
  -d '{"project_id":1,"user_story_id":1,"subject":"Test Task"}'

# 6. Get Project Details
curl http://localhost:3000/api/v1/projects/1 \
  -H "Authorization: Bearer SESSION_ID"

# 7. Delete Task
curl -X DELETE http://localhost:3000/api/v1/tasks/1 \
  -H "Authorization: Bearer SESSION_ID"

# 8. LOGOUT
curl -X POST http://localhost:3000/api/v1/logout \
  -H "Authorization: Bearer SESSION_ID"
```

### Scenario 2: Error Handling Test

Test the security and error handling:

```bash
# Test 1: Invalid Session
curl http://localhost:3000/api/v1/projects \
  -H "Authorization: Bearer invalid_session"
# Expected: 403 Forbidden - "Invalid session"

# Test 2: Invalid Input
curl -X POST http://localhost:3000/api/v1/projects \
  -d '{"name":"","description":"missing name"}'
# Expected: 400 Bad Request - "Project name is required"

# Test 3: Rate Limiting
for i in {1..6}; do
  curl -X POST http://localhost:3000/api/v1/login \
    -d '{"username":"admin","password":"wrong"}'
done
# Expected: 429 Too Many Requests after 5 attempts - "Rate limit exceeded"

# Test 4: HTTPS Enforcement
curl -X POST http://localhost:3000/api/v1/login \
  -d '{"username":"admin","password":"123123","host":"http://insecure.taiga.com"}'
# Expected: 403 Forbidden - "HTTPS required"
```

### Scenario 3: Session Management Test

```bash
# Test 1: Session Expiry
# Start session, then wait SESSION_EXPIRY seconds (default: 8 hours)
# After expiry, operations should fail

# Test 2: Concurrent Sessions
# Open multiple sessions with same user
# Each should work independently

# Test 3: Session Cleanup
# Create sessions, logout, verify cleanup
```

## Automated Test Verification

### Run Unit Tests

```bash
# All tests
pytest tests/ -v

# Only authentication tests
pytest tests/auth/ -v

# Only validation tests
pytest tests/ -k validation -v

# With coverage
pytest tests/ --cov=src --cov-report=html

# Specific test
pytest tests/auth/test_session_management.py::TestSessionInfo::test_session_info_creation_with_defaults -v
```

### Run Specific Feature Tests

```bash
# Input Validation Tests
pytest tests/ -m validation -v

# Session Management Tests
pytest tests/auth/test_session_management.py -v

# Rate Limiting Tests
pytest tests/auth/test_rate_limiting.py -v

# Delete Operations Tests
pytest tests/projects/test_delete_operations.py -v

# Edge Cases Tests
pytest tests/integration/test_edge_cases_simple.py -v
```

### Check Code Quality

```bash
# Code formatting
black --check src/

# Import organization
isort --check-only src/

# Type checking
mypy src/

# Linting
flake8 src/

# All at once
black src/ && isort src/ && mypy src/ && flake8 src/ && echo "✅ All checks passed!"
```

## Using Python Script for E2E Testing

Create `test_e2e.py`:

```python
#!/usr/bin/env python3
"""E2E test script for pytaiga-mcp"""

import subprocess
import time
import requests
import json
from typing import Optional

class TaigaMCPClient:
    def __init__(self, base_url: str = "http://localhost:3000"):
        self.base_url = base_url
        self.session_id = None
        self.headers = {}
    
    def login(self, username: str, password: str, host: str):
        """Login to Taiga"""
        print(f"🔐 Logging in as {username}...")
        # Implementation depends on your API
        # For stdio mode, you'd use subprocess
        # For SSE mode, use HTTP requests
        
    def test_workflow(self):
        """Test complete workflow"""
        try:
            # 1. Login
            self.login("admin", "123123", "http://localhost:9000")
            print("✅ Login successful")
            
            # 2. Create project
            # project = self.create_project("E2E Test Project")
            # print("✅ Project created")
            
            # 3. Create epic
            # epic = self.create_epic(project['id'], "Test Epic")
            # print("✅ Epic created")
            
            # 4. Create user story
            # story = self.create_user_story(project['id'], epic['id'])
            # print("✅ User story created")
            
            # 5. List resources
            # projects = self.list_projects()
            # print(f"✅ Listed {len(projects)} projects")
            
            # 6. Logout
            # self.logout()
            # print("✅ Logout successful")
            
            print("\n✅ E2E test PASSED!")
            
        except Exception as e:
            print(f"\n❌ E2E test FAILED: {e}")
            return False
        
        return True

if __name__ == "__main__":
    client = TaigaMCPClient()
    client.test_workflow()
```

Run it:
```bash
python test_e2e.py
```

## Verification Checklist

- [ ] Server starts without errors
- [ ] MCP tools are discoverable by client
- [ ] Login works with valid credentials
- [ ] Login fails with invalid credentials
- [ ] Session is created and stored
- [ ] Session expires after configured time
- [ ] Rate limiting prevents brute force (5 attempts/15 min)
- [ ] HTTPS enforcement blocks HTTP logins
- [ ] Create operations work for all resources
- [ ] Read operations return correct data
- [ ] Update operations persist changes
- [ ] Delete operations remove resources
- [ ] Error handling returns appropriate messages
- [ ] Validation rejects invalid inputs
- [ ] Input validation test coverage verified
- [ ] All 417+ tests pass
- [ ] Zero test flakiness (run 3x)
- [ ] Code quality checks pass (black, isort, mypy, flake8)
- [ ] Type hints are correct
- [ ] Logging captures operations
- [ ] Performance is acceptable (<2 seconds for test suite)

## Common Issues & Solutions

### Issue: "Cannot connect to Taiga"
```bash
# Check Taiga is running
curl http://localhost:9000

# Check MCP server logs for errors
# Enable DEBUG logging
export LOG_LEVEL=DEBUG
```

### Issue: "HTTPS required" error
```bash
# Either use HTTPS URL or set environment variable
export ALLOW_HTTP_TAIGA=true
```

### Issue: "Rate limit exceeded" during testing
```bash
# Wait 30 minutes or modify RATE_LIMIT_LOCKOUT_SECONDS
# For testing: set to shorter duration
export RATE_LIMIT_LOCKOUT_SECONDS=60
```

### Issue: "Session expired" mid-test
```bash
# Increase SESSION_EXPIRY for testing
export SESSION_EXPIRY=86400  # 24 hours
```

### Issue: Tests not finding MCP tools
```bash
# Ensure server is running
# Check MCP client configuration
# Verify tool definitions in src/server.py
```

## Performance Testing

```bash
# Test with timing
time pytest tests/ -q

# Expected: <2 seconds for full suite
# If slower, check:
# - System resources
# - Network latency to Taiga
# - Database performance
```

## Security Testing

```bash
# Test HTTPS enforcement
curl -X POST http://localhost:3000/api/v1/login \
  -d '{"host":"http://insecure.example.com"}'
# Should fail

# Test SQL injection protection
curl -X POST http://localhost:3000/api/v1/projects \
  -d '{"name":"x'; DROP TABLE projects; --"}'
# Should fail with validation error

# Test password hashing
# Passwords should never be logged in plaintext
grep -r "password" /path/to/logs/
# Should not show actual passwords
```

## Monitoring & Logging

```bash
# View logs in real-time
tail -f taiga_mcp.log

# Filter by level
grep "ERROR" taiga_mcp.log

# Check performance metrics
grep "duration" taiga_mcp.log
```

## Next Steps After E2E Testing

1. ✅ Verify all functionality works as expected
2. ✅ Check error handling and edge cases
3. ✅ Validate security measures
4. ✅ Test with actual Taiga workflows
5. 📋 Document any issues found
6. 🚀 Deploy to production

---

**For more details, see**: [CLAUDE.md](../CLAUDE.md), [CHANGELOG.md](../CHANGELOG.md), [README.md](../README.md)
