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
  └── roadmap/           # Development roadmap documentation
      ├── README.md                    # Entry point & navigation
      ├── ROADMAP.md                   # Complete specs (5 epics, 23 stories)
      ├── ROADMAP_VISUAL.md            # Visual timeline & diagrams
      ├── SPRINT_PLANNING.md           # Sprint breakdown (8+ sprints)
      ├── ROADMAP_INDEX.md             # Navigation guide
      └── ROADMAP_QUICK_REFERENCE.md   # One-page summary

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
