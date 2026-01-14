<p align="center">
<picture>
  <img src="https://taiga.io/media/images/favicon.width-44.png">
</picture>
</p>

# Taiga MCP Bridge


[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)
[![Version 0.2.0-rc.1](https://img.shields.io/badge/version-0.2.0--rc.1-yellow.svg)](https://github.com/romainvaltier/pytaiga-mcp/releases/tag/v0.2.0-rc.1)
[![Tests: 417 Passing](https://img.shields.io/badge/tests-417%20passing-brightgreen.svg)](./specs/001-server-hardening/tasks.md)
[![Code Quality: Passing](https://img.shields.io/badge/code%20quality-passing-brightgreen.svg)](./CLAUDE.md)

## Overview

The Taiga MCP Bridge is a powerful integration layer that connects [Taiga](https://taiga.io/) project management platform with the Model Context Protocol (MCP), enabling AI tools and workflows to interact seamlessly with Taiga's resources.

This bridge provides a comprehensive set of tools and resources for AI agents to:
- Create and manage projects, epics, user stories, tasks, and issues in Taiga
- Track sprints and milestones
- Assign and update work items
- Query detailed information about project artifacts
- Manage project members and permissions

By using the MCP standard, this bridge allows AI systems to maintain contextual awareness about project state and perform complex project management tasks programmatically.

## v0.2.0-rc.1 - Pre-Release Candidate 🚀

**Status**: First release candidate for v0.2.0 MVP. Ready for community testing and feedback.

This release marks the completion of the **Security Hardening & Quality Improvements epic** with 22 user stories across 4 sprints. We've added comprehensive Docker deployment support, GitHub Actions CI/CD pipeline, and automated quality gates.

### ✅ What's in v0.2.0-rc.1

**Security Hardening**
- Input validation for all MCP tools (string length, ID boundaries, types)
- Session management with TTL (8 hours default, configurable)
- HTTPS enforcement for production security
- Rate limiting with automatic lockout (5 attempts per 15 minutes)
- Concurrent session limits (default: 5 per user)

**Error Handling & Logging**
- Structured error responses with error codes and messages
- Comprehensive JSON logging with multiple levels
- TaigaException propagation with API error details
- Session validation before all operations

**Code Quality**
- 417+ tests with zero flaky tests (0 regressions)
- Test performance: <2 seconds for full suite
- Code quality: black, isort, mypy, flake8 - all passing
- Type safety with TypedDict response objects
- Python 3.10 compatibility

**Deployment & DevOps**
- Docker container images published to GitHub Container Registry (ghcr.io)
- Multi-stage Docker build for optimized image size
- Docker Compose templates for quick deployment
- GitHub Actions CI/CD pipeline with automated quality gates on every push
- Semantic versioning for container images (dev, rc, stable)

**Documentation**
- Complete CLAUDE.md with development patterns and release management
- Comprehensive error handling guide
- Configuration examples and best practices
- [Full Release Notes](https://github.com/romainvaltier/pytaiga-mcp/releases/tag/v0.2.0-rc.1)

### Quality Metrics

| Metric | Result |
|--------|--------|
| Tests Passing | 417+ |
| Test Flakiness | Zero flaky tests |
| Test Performance | <2 seconds |
| Code Coverage | 70% |
| Code Formatting | ✅ black |
| Import Organization | ✅ isort |
| Type Checking | ✅ mypy (0 errors) |
| Linting | ✅ flake8 (0 violations) |

### Testing This RC

We encourage you to test v0.2.0-rc.1 and provide feedback before the stable release:

```bash
# Pull and run the RC image
docker pull ghcr.io/romainvaltier/pytaiga-mcp:v0.2.0-rc.1
docker-compose up

# Or run tests locally
pytest tests/ -v --cov=src
```

**Please report issues** on [GitHub Issues](https://github.com/romainvaltier/pytaiga-mcp/issues) with:
- Your Python version and platform
- Steps to reproduce
- Expected vs actual behavior

---

⚠️ **Release Status**: This is a pre-release candidate. Features and APIs may change before the stable v0.2.0 release. For production use, wait for the stable release.

---

## Features

### Comprehensive Resource Support

The bridge supports the following Taiga resources with complete CRUD operations:

- **Projects**: Create, update, and manage project settings and metadata
- **Epics**: Manage large features that span multiple sprints
- **User Stories**: Handle detailed requirements and acceptance criteria
- **Tasks**: Track smaller units of work within user stories
- **Issues**: Manage bugs, questions, and enhancement requests
- **Sprints (Milestones)**: Plan and track work in time-boxed intervals

## Installation

### Quick Start with Docker (Recommended for RC Testing)

The easiest way to test v0.2.0-rc.1 is with Docker:

```bash
docker pull ghcr.io/romainvaltier/pytaiga-mcp:v0.2.0-rc.1
docker-compose up
```

See [Docker Build & CI/CD Pipeline](./CLAUDE.md#docker-build--cicd-pipeline) in CLAUDE.md for advanced Docker options.

### Local Installation

This project uses [uv](https://github.com/astral-sh/uv) for fast, reliable Python package management.

#### Prerequisites

- Python 3.10 or higher
- uv package manager

#### Basic Installation

```bash
# Clone the repository
git clone https://github.com/your-org/pyTaigaMCP.git
cd pyTaigaMCP

# Install dependencies
./install.sh
```

#### Development Installation

For development (includes testing and code quality tools):

```bash
./install.sh --dev
```

#### Manual Installation

If you prefer to install manually:

```bash
# Production dependencies only
uv pip install -e .

# With development dependencies
uv pip install -e ".[dev]"
```

## Configuration

The bridge can be configured through environment variables or a `.env` file:

| Environment Variable | Description | Default |
| --- | --- | --- |
| `TAIGA_API_URL` | Base URL for the Taiga API | http://localhost:9000 |
| `SESSION_EXPIRY` | Session expiration time in seconds | 28800 (8 hours) |
| `TAIGA_TRANSPORT` | Transport mode (stdio or sse) | stdio |
| `REQUEST_TIMEOUT` | API request timeout in seconds | 30 |
| `MAX_CONNECTIONS` | Maximum number of HTTP connections | 10 |
| `MAX_KEEPALIVE_CONNECTIONS` | Max keepalive connections | 5 |
| `RATE_LIMIT_REQUESTS` | Max requests per minute | 100 |
| `LOG_LEVEL` | Logging level | INFO |
| `LOG_FILE` | Path to log file | taiga_mcp.log |

Create a `.env` file in the project root to set these values:

```
TAIGA_API_URL=https://api.taiga.io/api/v1/
TAIGA_TRANSPORT=sse
LOG_LEVEL=DEBUG
```

### Security Configuration

#### HTTPS Enforcement

By default, the bridge enforces HTTPS for all Taiga API connections to prevent credentials from being transmitted over unencrypted connections.

**How it works:**
- Login attempts to non-HTTPS URLs are rejected with a clear error message
- The error message guides users to use HTTPS URLs
- For local development, you can disable this check with `ALLOW_HTTP_TAIGA=true`

**Environment Variable:**
```bash
# Disable HTTPS enforcement for local development (NOT RECOMMENDED for production)
ALLOW_HTTP_TAIGA=true
```

**Example:**
```python
# This will be REJECTED by default:
client.call_tool("login", {
    "host": "http://taiga.example.com",  # ❌ Error: Must use HTTPS
    "username": "user",
    "password": "pass"
})

# This will be ACCEPTED:
client.call_tool("login", {
    "host": "https://taiga.example.com",  # ✅ Correct: Uses HTTPS
    "username": "user",
    "password": "pass"
})
```

⚠️ **Security Warning:** Only disable HTTPS enforcement in development environments. Production systems must always use HTTPS.

## Usage

### With stdio mode

Paste the following json in your Claude App's or Cursor's mcp settings section:

```json
{
    "mcpServers": {
        "taigaApi": {
            "command": "uv",
            "args": [
                "--directory",
                "<path to local pyTaigaMCP folder>",
                "run",
                "src/server.py"
            ],
            "env": {
                "TAIGA_TRANSPORT": "<stdio|sse>",                
                "TAIGA_API_URL": "<Taiga API Url (ex: http://localhost:9000)",
                "TAIGA_USERNAME": "<taiga username>",
                "TAIGA_PASSWORD": "<taiga password>"
            }
        }
}
```

### Running the Bridge

Start the MCP server with:

```bash
# Default stdio transport
./run.sh

# For SSE transport
./run.sh --sse
```

Or manually:

```bash
# For stdio transport (default)
uv run python src/server.py

# For SSE transport
uv run python src/server.py --sse
```

### Transport Modes

The server supports two transport modes:

1. **stdio (Standard Input/Output)** - Default mode for terminal-based clients
2. **SSE (Server-Sent Events)** - Web-based transport with server push capabilities

You can set the transport mode in several ways:
- Using the `--sse` flag with run.sh or server.py (default is stdio)
- Setting the `TAIGA_TRANSPORT` environment variable 
- Adding `TAIGA_TRANSPORT=sse` to your `.env` file

### Authentication Flow

This MCP bridge uses a session-based authentication model:

1. **Login**: Clients must first authenticate using the `login` tool:
   ```python
   session = client.call_tool("login", {
       "username": "your_taiga_username",
       "password": "your_taiga_password",
       "host": "https://api.taiga.io" # Optional
   })
   # Save the session_id from the response
   session_id = session["session_id"]
   ```

2. **Using Tools and Resources**: Include the `session_id` in every API call:
   ```python
   # For resources, include session_id in the URI
   projects = client.get_resource(f"taiga://projects?session_id={session_id}")
   
   # For project-specific resources
   epics = client.get_resource(f"taiga://projects/123/epics?session_id={session_id}")
   
   # For tools, include session_id as a parameter
   new_project = client.call_tool("create_project", {
       "session_id": session_id,
       "name": "New Project",
       "description": "Description"
   })
   ```

3. **Check Session Status**: You can check if your session is still valid:
   ```python
   status = client.call_tool("session_status", {"session_id": session_id})
   # Returns information about session validity and remaining time
   ```

4. **Logout**: When finished, you can logout to terminate the session:
   ```python
   client.call_tool("logout", {"session_id": session_id})
   ```

### Example: Complete Project Creation Workflow

Here's a complete example of creating a project with epics and user stories:

```python
from mcp.client import Client

# Initialize MCP client
client = Client()

# Authenticate and get session ID
auth_result = client.call_tool("login", {
    "username": "admin",
    "password": "password123",
    "host": "https://taiga.mycompany.com"
})
session_id = auth_result["session_id"]

# Create a new project
project = client.call_tool("create_project", {
    "session_id": session_id,
    "name": "My New Project",
    "description": "A test project created via MCP"
})
project_id = project["id"]

# Create an epic
epic = client.call_tool("create_epic", {
    "session_id": session_id,
    "project_id": project_id,
    "subject": "User Authentication",
    "description": "Implement user authentication features"
})
epic_id = epic["id"]

# Create a user story in the epic
story = client.call_tool("create_user_story", {
    "session_id": session_id,
    "project_id": project_id,
    "subject": "User Login",
    "description": "As a user, I want to log in with my credentials",
    "epic_id": epic_id
})

# Logout when done
client.call_tool("logout", {"session_id": session_id})
```

## Development

### Project Structure

```
pyTaigaMCP/
├── src/
│   ├── server.py          # MCP server implementation with tools
│   ├── taiga_client.py    # Taiga API client with all CRUD operations
│   ├── tools.py           # MCP tools definitions
│   └── config.py          # Configuration settings with Pydantic
├── tests/
│   ├── conftest.py        # Shared pytest fixtures
│   ├── unit/              # Unit tests
│   └── integration/       # Integration tests
├── pyproject.toml         # Project configuration and dependencies
├── install.sh             # Installation script
├── run.sh                 # Server execution script
└── README.md              # Project documentation
```

### Testing

Run tests with pytest:

```bash
# Run all tests
pytest

# Run only unit tests
pytest tests/unit/

# Run only integration tests
pytest tests/integration/

# Run tests with specific markers
pytest -m "auth"  # Authentication tests
pytest -m "core"  # Core functionality tests

# Run tests with coverage reporting
pytest --cov=src
```

### Debugging and Inspection

Use the included inspector tool for debugging:

```bash
# Default stdio transport
./inspect.sh

# For SSE transport
./inspect.sh --sse

# For development mode
./inspect.sh --dev
```

## Error Handling

All API operations return standardized error responses in the following format:

```json
{
  "status": "error",
  "error_type": "ExceptionClassName",
  "message": "Detailed error message"
}
```

## Performance Considerations

The bridge implements several performance optimizations:

1. **Connection Pooling**: Reuses HTTP connections for better performance
2. **Rate Limiting**: Prevents overloading the Taiga API
3. **Retry Mechanism**: Automatically retries failed requests with exponential backoff
4. **Session Cleanup**: Regularly cleans up expired sessions to free resources

## 🗺️ Development Roadmap

For a comprehensive development roadmap with detailed planning, epics, sprints, and user stories, please see the **[Roadmap Documentation](docs/roadmap/)**:

- **📊 [ROADMAP_VISUAL.md](docs/roadmap/ROADMAP_VISUAL.md)** - Visual timeline, epics, and dependencies
- **📋 [SPRINT_PLANNING.md](docs/roadmap/SPRINT_PLANNING.md)** - Detailed sprint breakdown and team planning
- **📚 [ROADMAP.md](docs/roadmap/ROADMAP.md)** - Complete technical specifications and acceptance criteria
- **🚀 [ROADMAP_INDEX.md](docs/roadmap/ROADMAP_INDEX.md)** - Navigation guide and quick start
- **⚡ [ROADMAP_QUICK_REFERENCE.md](docs/roadmap/ROADMAP_QUICK_REFERENCE.md)** - One-page printable summary

**Quick Facts**:
- **Total Effort**: 239 story points across 5 epics
- **Timeline**: 16-20 weeks (2 developers)
- **Target**: Production-ready v1.0.0 with 85%+ code coverage and A-grade security
- **Current Status**: MVP with 35% coverage; roadmap planned for hardening and expansion

Start with [`docs/roadmap/README.md`](docs/roadmap/README.md) for navigation guidance.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Install development dependencies (`./install.sh --dev`)
4. Make your changes
5. Run tests (`pytest`)
6. Commit your changes (`git commit -m 'Add some amazing feature'`)
7. Push to the branch (`git push origin feature/amazing-feature`)
8. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- [Taiga](https://www.taiga.io/) for their excellent project management platform
- [Model Context Protocol (MCP)](https://github.com/mcp-foundation/specification) for the standardized AI communication framework
- All contributors who have helped shape this project
