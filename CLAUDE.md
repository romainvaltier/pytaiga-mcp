# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**Taiga MCP Bridge** is a Model Context Protocol (MCP) server that integrates the Taiga project management platform with AI tools. It provides comprehensive CRUD operations for Taiga resources (projects, epics, user stories, tasks, issues, sprints) through MCP tools.

The project uses a session-based authentication model where clients authenticate via `login` tool and receive a `session_id` that must be included in all subsequent tool calls.

## Core Architecture

### Session-Based Authentication Model
- **Login Flow**: Clients call the `login` tool with username, password, and host URL
- **Session Storage**: Valid authenticated sessions are stored in `active_sessions` dict in `server.py` (maps session_id → TaigaClientWrapper)
- **Session Validation**: Helper function `_get_authenticated_client()` validates session_id and retrieves the corresponding client
- **Key Requirement**: All subsequent tools must include `session_id` parameter and validate it through `_get_authenticated_client()`

### Main Components
1. **server.py** (66KB): FastMCP server with all MCP tool definitions. Contains login/logout, resource listing, and CRUD operations for projects, epics, user stories, tasks, issues, and sprints
2. **taiga_client.py**: `TaigaClientWrapper` class wrapping the pytaigaclient library. Handles Taiga API communication and maintains authentication state
3. **Dependencies**: Uses `mcp[cli]`, `fastapi`, `pytaigaclient` (custom fork), and other support libraries

### Transport Modes
- **stdio (default)**: For CLI/terminal clients, used by `run.sh`
- **SSE (Server-Sent Events)**: For web-based clients, enabled with `--sse` flag

## Development Commands

### Basic Setup
```bash
# Install dependencies (production only)
./install.sh

# Install with development tools
./install.sh --dev

# Manual installation with uv
uv pip install -e .
uv pip install -e ".[dev]"
```

### Running the Server
```bash
# Start with stdio transport (default)
./run.sh
# Or: uv run python src/server.py

# Start with SSE transport
./run.sh --sse
# Or: uv run python src/server.py --sse
```

### Testing
```bash
# Run all tests
pytest

# Run only unit tests
pytest tests/unit/ -v

# Run only integration tests
pytest tests/integration/ -v -m integration

# Run tests with specific markers
pytest -m "auth"  # Authentication tests
pytest -m "core"  # Core functionality tests

# Run with coverage
pytest --cov=src

# Run a single test file
pytest tests/test_server.py -v

# Run a specific test class or function
pytest tests/test_server.py::TestTaigaTools::test_login -v
```

### Debugging
```bash
# Inspect tool with stdio transport
./inspect.sh

# Inspect with SSE transport
./inspect.sh --sse

# Inspect in development mode
./inspect.sh --dev
```

### Code Quality
```bash
# Format code (black, isort)
black src/
isort src/

# Type checking
mypy src/

# Linting
flake8 src/

# Combined format check
black --check src/
isort --check-only src/
```

## Key Development Patterns

### Adding New Tools
1. Define tool in `server.py` using `@mcp.tool()` decorator
2. Validate `session_id` using `_get_authenticated_client()` helper
3. Call appropriate methods on the returned TaigaClientWrapper instance
4. Handle TaigaException and other errors gracefully
5. Return structured response (dict for success, raise exception for errors)

### Session Management
- Session objects stored in `active_sessions: Dict[str, TaigaClientWrapper]` in server.py
- Session IDs are UUIDs generated on successful login
- Use `_get_authenticated_client(session_id)` to safely retrieve authenticated clients
- Expired sessions are not auto-cleaned; logout tool removes them

### Error Handling
- FastMCP automatically converts raised exceptions to error responses
- TaigaException from pytaigaclient should be caught and re-raised or handled
- PermissionError is raised for invalid/expired session IDs

### API Parameter Standardization

The codebase follows strict conventions when calling pytaigaclient methods. These patterns are enforced by the pytaigaclient library and must be followed consistently.

#### LIST Operations
- **Standard**: Use `project_id=project_id` for filtering
- **Exception**: `milestones.list(project=project_id)` - library enforces `project=`
- **Example**: `user_stories.list(project_id=123, status=1)`
- **Rationale**: Named parameters are explicit and self-documenting; aligns with Taiga API query parameter naming

#### GET Operations
- **Standard (positional)**: `user_stories.get(resource_id)` - most resources accept positional IDs
- **Exception (named)**: `projects.get(project_id=project_id)` - library requires named parameter
- **Rationale**: Projects library enforces named parameter; others accept positional for brevity

#### UPDATE Operations
- **Projects**: `projects.update(project_id=id, version=v, project_data=dict)`
- **All Others**: `resource.edit(resource_id=id, version=v, **kwargs)`
- **Rationale**: Library enforces different method signatures (`update()` vs `edit()`)

#### CREATE Operations
- **Standard**: `resource.create(project=project_id, **kwargs)`
- **Rationale**: Library convention (all resources use this pattern)

#### DELETE Operations
- **Standard**: `resource.delete(id=resource_id, version=version)`
- **Rationale**: Consistent across all resources

**Important**: When adding new operations or resources, verify the expected parameter format with pytaigaclient documentation to ensure consistency with these patterns.

### Resource Access Patterns (US-2.2)

All resource retrieval (GET operations) in the codebase uses a unified accessor pattern via `TaigaClientWrapper.get_resource()`. This provides a consistent interface across all resource types while abstracting away pytaigaclient library variations (named vs positional parameters).

**Usage Pattern**:
```python
# In server.py MCP tools
taiga_client = _get_authenticated_client(session_id)

# Retrieve any resource type using the same pattern
project = taiga_client.get_resource("project", 123)
user_story = taiga_client.get_resource("user_story", 456)
task = taiga_client.get_resource("task", 789)
issue = taiga_client.get_resource("issue", 101)
epic = taiga_client.get_resource("epic", 202)
milestone = taiga_client.get_resource("milestone", 303)
wiki_page = taiga_client.get_resource("wiki_page", 404)
```

**Supported Resource Types**:
- `"project"` - Taiga projects (uses named parameter internally)
- `"user_story"` - User stories (uses positional parameter internally)
- `"task"` - Tasks (uses positional parameter internally)
- `"issue"` - Issues (uses positional parameter internally)
- `"epic"` - Epics (uses positional parameter internally)
- `"milestone"` - Milestones (uses positional parameter internally)
- `"wiki_page"` - Wiki pages (uses positional parameter internally)

**Implementation Details**:
- Located in `src/taiga_client.py`: `TaigaClientWrapper.get_resource(resource_type, resource_id)`
- Uses `RESOURCE_MAPPING` dictionary to centralize parameter format knowledge
- Automatically handles named vs positional parameter variations based on pytaigaclient requirements
- Includes comprehensive logging for debugging API calls
- Validates resource types and raises ValueError for unknown types
- Enforces authentication requirement via `_ensure_authenticated()`

**Do NOT**:
- Call `taiga_client.api.{resource}.get()` directly - always use `get_resource()`
- Hardcode parameter patterns - they may change based on library updates
- Mix direct API calls with `get_resource()` calls for the same resource type

**Why This Pattern?**:
- Centralizes pytaigaclient API quirks and variations in one place
- Makes the codebase easier to maintain and update
- Provides clear, consistent interface for developers
- Simplifies testing and mocking (test one method vs seven)
- Enables future extensibility (can add similar wrappers for create, update, delete)

## Configuration

Environment variables (can be set in `.env` file):
- `TAIGA_API_URL`: Base URL for Taiga API (default: http://localhost:9000)
- `SESSION_EXPIRY`: Session timeout in seconds (default: 28800 / 8 hours)
- `TAIGA_TRANSPORT`: Transport mode - "stdio" or "sse" (default: stdio)
- `REQUEST_TIMEOUT`: API request timeout in seconds (default: 30)
- `LOG_LEVEL`: Logging level (default: INFO)

## Development Roadmap

A comprehensive development roadmap is available in **`docs/roadmap/`** that outlines the complete path from MVP to production-ready software:

- **5 Epics** organized by priority: Security Hardening, Code Quality, Testing, Features, Production Readiness
- **23 User Stories** with acceptance criteria and story points (239 total points)
- **8+ Sprints** scheduled over 16-20 weeks with team assignments
- **3 Release Milestones**: v0.2.0 (MVP), v0.3.0 (Features), v1.0.0 (Production)

**Start here**: [`docs/roadmap/README.md`](docs/roadmap/README.md) - provides role-based navigation for PMs, developers, tech leads, and executives.

See [`docs/roadmap/`](docs/roadmap/) folder for:
- `ROADMAP.md` - Complete technical specifications
- `ROADMAP_VISUAL.md` - Visual timeline and diagrams
- `SPRINT_PLANNING.md` - Sprint-by-sprint execution guide
- `ROADMAP_INDEX.md` - Navigation and quick start
- `ROADMAP_QUICK_REFERENCE.md` - One-page printable summary

## Git Workflow & Development Process

The project uses **GitHub Flow** with a structured approach to ensure quality and traceability. All development must follow the defined workflow and integrate with the roadmap.

### Quick Start
- **For busy developers** (5-10 min read): See [`docs/WORKFLOW_QUICK_START.md`](docs/WORKFLOW_QUICK_START.md)
- **For comprehensive details** (20-30 min read): See [`docs/CONTRIBUTING_WORKFLOW.md`](docs/CONTRIBUTING_WORKFLOW.md)

### Branching Strategy

The project uses **GitHub Flow** with type-prefixed branches:

| Type | Pattern | Purpose | Example |
|------|---------|---------|---------|
| Feature | `feature/EPIC-#-description` | New feature for an epic | `feature/EPIC-1-input-validation` |
| User Story | `feature/US-#-description` | Implementation of user story | `feature/US-1.1-password-validation` |
| Bug Fix | `fix/description` | Fix for identified issue | `fix/session-bug` |
| Test | `test/description` | Test additions or improvements | `test/session-tests` |
| Refactor | `refactor/description` | Code refactoring | `refactor/api-consistency` |
| Docs | `docs/description` | Documentation updates | `docs/roadmap-updates` |
| Chore | `chore/description` | Build, config, deps | `chore/update-dependencies` |

### Development Workflow

All work follows this 8-step workflow:

1. **Plan**: Choose a story from the current sprint (see `docs/roadmap/SPRINT_PLANNING.md`)
2. **Create Branch**: `git checkout -b feature/EPIC-#-description`
3. **Implement**: Write code following patterns in "Key Development Patterns" section below
4. **Quality**: Run format, type check, lint, and tests before pushing
5. **Create PR**: Push branch and create pull request on GitHub
6. **Code Review**: Address reviewer comments and request approval
7. **Merge**: Use "Squash and merge" to keep history clean
8. **Update Roadmap**: Mark story as complete in `docs/roadmap/SPRINT_PLANNING.md`

### Commit Message Format

Use Conventional Commits format to link code to roadmap items:

```
feat(EPIC-1): short description (50 chars max)

Optional detailed explanation of what and why.
Keep to 72 characters per line.

Closes: #123
Epic: EPIC-1
```

**Types**: `feat`, `fix`, `test`, `refactor`, `docs`, `chore`, `style`

### Definition of Done

Every PR must satisfy the complete Definition of Done checklist:

**Code Quality**:
- [ ] Code formatted with `black` and `isort`
- [ ] No type errors (`mypy` passes)
- [ ] No lint errors (`flake8` passes)
- [ ] Code follows existing patterns in `Key Development Patterns` section

**Testing**:
- [ ] Tests written for new functionality
- [ ] All tests passing (`pytest`)
- [ ] Code coverage >80% (check with `pytest --cov=src`)
- [ ] Integration tests added for feature areas

**Review & Documentation**:
- [ ] PR reviewed and approved by at least one other developer
- [ ] Documentation updated if applicable
- [ ] Roadmap story marked as complete

**Release Integration**:
- [ ] PR links to roadmap epic/story
- [ ] Commit message includes epic reference
- [ ] No breaking changes without discussion

### Quality Checklist Before Creating PR

```bash
# 1. Format code
black src/
isort src/

# 2. Type check
mypy src/

# 3. Lint
flake8 src/

# 4. Test
pytest tests/ -v --cov=src

# 5. Update branch
git fetch origin
git rebase origin/master

# 6. Verify no conflicts
git status
```

## Project Structure
```
src/
  ├── server.py          # FastMCP server with all tools (main file)
  ├── taiga_client.py    # TaigaClientWrapper for API communication
  └── __init__.py

tests/
  ├── test_server.py     # Unit tests for server tools
  ├── test_integration.py # Integration tests
  └── conftest.py        # Pytest fixtures

docs/
  ├── CONTRIBUTING_WORKFLOW.md          # Comprehensive workflow guide (30 min read)
  ├── WORKFLOW_QUICK_START.md           # Quick reference for developers (5 min read)
  └── roadmap/                          # Development roadmap documentation
      ├── README.md                     # Entry point & navigation
      ├── ROADMAP.md                    # Complete specs (5 epics, 23 stories)
      ├── ROADMAP_VISUAL.md             # Visual timeline & diagrams
      ├── SPRINT_PLANNING.md            # Sprint breakdown (8+ sprints)
      ├── ROADMAP_INDEX.md              # Navigation guide
      └── ROADMAP_QUICK_REFERENCE.md    # One-page summary

pyproject.toml           # Project config, dependencies, tool settings
```

## Testing Structure

- **Test Markers**: Organized by resource type (auth, core, projects, epics, user_stories, tasks, issues, sprints) and test type (unit, integration, slow)
- **Session Fixture**: `session_setup` fixture in test_server.py creates mock authenticated sessions for testing
- **Mocking**: Uses `unittest.mock` to mock TaigaClientWrapper methods
- **Integration Tests**: Located in `tests/integration/` and marked with `@pytest.mark.integration`

## Common Issues & Solutions

### Session ID Validation
- Always use `_get_authenticated_client()` helper instead of directly accessing `active_sessions`
- This ensures both session existence and authentication status are verified
- Returns PermissionError if session is invalid or expired

### pytaigaclient Dependency
- Uses custom fork from `https://github.com/talhaorak/pyTaigaClient.git`
- Specified in `pyproject.toml` under `[tool.uv.sources]`
- Provides TaigaClient class and TaigaException

### Transport Mode Selection
- Server defaults to stdio when run without arguments
- Use `--sse` flag or set `TAIGA_TRANSPORT=sse` environment variable for SSE mode
- Client must match server transport mode

## Performance Considerations

The Taiga API client implements:
- Connection pooling for HTTP requests
- Rate limiting (100 requests/minute by default)
- Retry mechanism with exponential backoff for failed requests
- Session cleanup removes expired sessions from memory

## Docker Build & CI/CD Pipeline

This project uses automated GitHub Actions workflows to build, test, and publish Docker images to GitHub Container Registry (ghcr.io), implementing Principle VII of the constitution.

### GitHub Actions Workflow

**Location**: `.github/workflows/build-docker.yml`

**Triggers**:
- Every push to `master` branch → builds with `dev` tag
- Pre-release publication → builds with release candidate tag (e.g., `v1.2.0-rc.1`)
- Stable release publication → builds with semantic version tags (`v1.2.0`, `v1.2`, `v1`, `latest`)

**Quality Gates** (all must pass):
- `black --check src/` - Code formatting
- `isort --check-only src/` - Import organization
- `mypy src/` - Type checking
- `flake8 src/` - Linting
- `pytest --cov=src` - Test execution with >80% coverage requirement

### Dockerfile Best Practices

**Multi-Stage Build Pattern**:
The Dockerfile uses two stages to minimize runtime image size:
1. **Builder Stage**: Installs build tools, compiles dependencies with `uv`, creates `requirements.txt`
2. **Runtime Stage**: Copies only compiled packages, no build tools, runs as non-root user

**uv Package Manager Installation**:
When installing `uv` via the official installer script, note these patterns:
```dockerfile
# Install uv and move to system PATH
RUN curl -LsSf https://astral.sh/uv/install.sh | sh && \
    mv /root/.local/bin/uv /usr/local/bin/uv
```

**Key Gotchas**:
- The installer script outputs binaries to `/root/.local/bin`, NOT `/root/.cargo/bin` (despite Rust-like naming)
- Always verify installation path before using in subsequent RUN commands
- Use `uv pip install --system` for system-wide package installation in containers (not virtual environments)

**Compiled Dependencies**:
```dockerfile
# Generate requirements.txt with locked versions
RUN uv pip compile pyproject.toml -o requirements.txt && \
    uv pip install --system -r requirements.txt
```
This two-step approach locks dependency versions and enables reproducible builds across environments.

### Container Image Versioning

**Tag Strategy** (managed by GitHub Actions):
- `dev` - Development build from `master` branch; always latest commit
- `vX.Y.Z-rc.N` - Release candidate (e.g., `v1.2.0-rc.1`); pre-release versions
- `vX.Y.Z` - Stable release (e.g., `v1.2.0`); exact version match
- `vX.Y` - Latest patch in minor version (e.g., `v1.2`); floating version
- `vX` - Latest patch in major version (e.g., `v1`); floating version
- `latest` - Newest stable release; production only

**Usage Examples**:
```bash
# Pin to development build
docker pull ghcr.io/romainvaltier/pytaiga-mcp:dev

# Pin to specific release
docker pull ghcr.io/romainvaltier/pytaiga-mcp:v1.2.0

# Pin to latest patch in minor version
docker pull ghcr.io/romainvaltier/pytaiga-mcp:v1.2

# Always get latest stable
docker pull ghcr.io/romainvaltier/pytaiga-mcp:latest
```

### Registry Authentication

**GitHub Container Registry (ghcr.io)**:
- Uses `secrets.GITHUB_TOKEN` automatically provided by GitHub Actions
- No additional secrets configuration needed
- User authentication: `docker login ghcr.io -u $GITHUB_ACTOR`
- Token already has `packages:write` permission via workflow permissions

**Security Practices**:
- Credentials are never hardcoded in Dockerfile or source code
- Registry authentication isolated to CI/CD pipeline (`docker/login-action@v3`)
- `.env` files and `.env.example` MUST NOT contain registry credentials

## Release Management & Versioning

### Release Workflow Pattern

The project follows a **pre-release-first** pattern to ensure quality before declaring stable releases:

1. **Create Pre-Release (RC)**
   - Trigger: `gh release create vX.Y.Z-rc.1 --prerelease`
   - GitHub Actions automatically builds and publishes `vX.Y.Z-rc.1` tag
   - Release notes focus on features, testing instructions, known limitations
   - Include disclaimer about RC status and encourage community testing

2. **Validate in Real-World Usage**
   - Community tests RC in their environments
   - Report issues on GitHub Issues
   - Fix critical issues → create `vX.Y.Z-rc.2` if needed

3. **Create Stable Release**
   - Trigger: `gh release create vX.Y.Z` (without `--prerelease`)
   - GitHub Actions automatically creates semantic version tags:
     - `vX.Y.Z` (exact version)
     - `vX.Y` (latest patch in minor)
     - `vX` (latest patch in major)
     - `latest` (newest stable)

4. **Cleanup Obsolete Tags**
   - Before declaring milestone complete, delete old sprint/development tags
   - Keep only semantic version tags and `dev` long-term
   - Example: `git tag -d sprint4/us-2.6-delete-validation && git push origin :sprint4/us-2.6-delete-validation`

### Container Image Tagging Strategy

**Internal Tags** (development-only, not documented externally):
- `dev`: Created on every master push; always latest development build

**External Tags** (documented in release notes; users should pin to these):
- `vX.Y.Z-rc.N`: Pre-release candidate (e.g., `v0.2.0-rc.1`)
  - For community testing and validation
  - Subject to change before stable version
- `vX.Y.Z`: Stable release (exact, immutable version)
- `vX.Y`: Latest patch in minor version (floating; auto-updated)
- `vX`: Latest patch in major version (floating; auto-updated)
- `latest`: Newest stable release (floating; production-only)

**External Pull Examples**:
```bash
# Pre-release testing
docker pull ghcr.io/romainvaltier/pytaiga-mcp:v0.2.0-rc.1

# Pin to specific stable version (recommended for production)
docker pull ghcr.io/romainvaltier/pytaiga-mcp:v0.2.0

# Pin to minor version (gets latest patches automatically)
docker pull ghcr.io/romainvaltier/pytaiga-mcp:v0.2

# Always latest stable
docker pull ghcr.io/romainvaltier/pytaiga-mcp:latest
```

### Release Notes Guidelines

Release notes are the primary user-facing documentation. They MUST:
- ✅ Focus on features, capabilities, and improvements from user perspective
- ✅ Include deployment instructions and testing guidance
- ✅ Document known limitations and breaking changes
- ✅ Provide feedback and issue reporting channels
- ✅ For RCs: Include disclaimer about pre-release status

Release notes MUST NOT:
- ❌ Include internal process details or administrative overhead
- ❌ Document test framework specifics or tool configuration minutiae
- ❌ List commit-level changes (use git history for that)
- ❌ Include developer-facing implementation details

**Example RC Release Notes Structure**:
```markdown
## v0.2.0-rc.1 - Pre-Release Testing

Brief description of the release.

### Core Features
- Feature 1: User-facing value proposition
- Feature 2: What users can do with it

### Deployment & Operations
- Docker support details
- CI/CD pipeline summary
- Infrastructure requirements

### Quality & Testing
- Test coverage
- Code quality standards

### Known Limitations
- What's not included
- Compatibility notes

### Testing This RC
Quick start and testing instructions.

### Reporting Issues
GitHub Issues link and what to include.

---

**This is a pre-release candidate. Please test thoroughly and report feedback before the stable release.**
```

## Sprint 4 Patterns & Configurations

Sprint 4 (Server Hardening Phase 3-5) introduced the following new patterns and configurations:

### Code Quality Tools Configuration

**Type Checking (mypy)**:
- Python 3.10 compatibility: Use conditional import for `NotRequired`:
  ```python
  import sys
  if sys.version_info >= (3, 11):
      from typing import NotRequired
  else:
      from typing_extensions import NotRequired
  ```
- Configure in `pyproject.toml`:
  ```toml
  [tool.mypy]
  python_version = "3.10"
  disallow_untyped_defs = false
  ignore_missing_imports = true
  warn_return_any = false
  check_untyped_defs = false
  [[tool.mypy.overrides]]
  module = "pytaigaclient.*"
  ignore_missing_imports = true
  ```

**Linting (flake8)**:
- Use `.flake8` config file (not pyproject.toml) for compatibility:
  ```ini
  [flake8]
  max-line-length = 100
  ignore = E501,F401
  exclude = .git,__pycache__,venv,.venv
  ```
- Line length set to 100 to match black formatter

**TypedDict Patterns**:
- For partial optional fields, use inherited TypedDict with `total=False`:
  ```python
  class _RequiredFields(TypedDict):
      """Required fields."""
      status: str
      session_id: str

  class ResponseType(_RequiredFields, total=False):
      """Full response with optional fields."""
      optional_field: str
  ```

### Edge Case Testing Patterns

Sprint 4 testing focuses on:
- **Empty list handling**: Test all list operations return empty list correctly
- **Boundary values**: Test ID edge cases (zero, negative, max 32-bit int)
- **Large lists**: Test operations with 1000+ items
- **Error propagation**: Verify TaigaException and network errors are propagated
- **Session management**: Test expired/invalid sessions are properly rejected
- **Sequential operations**: Test bulk operations don't interfere with each other

Example test structure:
```python
class TestEmptyListHandling:
    @patch("src.server._get_authenticated_client")
    def test_list_projects_empty(self, mock_auth):
        """Should handle empty project list"""
        from src.server import list_projects
        mock_client = Mock()
        mock_auth.return_value = mock_client
        mock_client.api.projects.list.return_value = []

        result = list_projects(session_id="test")
        assert result == []
```

### Test Quality Gates

Phase 6 Quality Gates (all must pass for v0.2.0 release):
1. **Code Formatting**: `black src/` passes (100 char lines)
2. **Import Organization**: `isort src/` passes
3. **Type Checking**: `mypy src/` passes with Python 3.10 compatibility
4. **Linting**: `flake8 src/` passes (ignoring E501, F401)
5. **Test Coverage**: pytest --cov=src shows >70% coverage (target >85% post-MVP)
6. **Test Performance**: All tests complete in <10 seconds (currently ~1.2s)
7. **Test Flakiness**: Run full suite 3x with zero flaky tests
8. **Regression Testing**: 200+ tests pass consistently
9. **Documentation**: CLAUDE.md updated with new patterns
10. **End-to-End**: Manual verification of key workflows
