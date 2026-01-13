# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.0] - 2026-01-13

### Added - Server Hardening & Quality Improvements (Sprints 1-4)

#### Security Hardening (Sprint 1)
- **Input Validation Framework** (US-1.1, US-1.2, US-1.3)
  - Comprehensive input validation for all MCP tools
  - String length validation (max 1000 chars)
  - ID boundary validation (positive integers, max 32-bit)
  - Required parameter validation
  - Type-specific validation (emails, URLs, numeric values)
  - Custom error messages for validation failures

- **Session Management & TTL** (US-1.5)
  - Session-based authentication with UUID session IDs
  - Configurable session TTL (default 8 hours via SESSION_EXPIRY env var)
  - Session expiration detection and cleanup
  - Last access timestamp tracking
  - Concurrent session limits per user (configurable, default 5)
  - Background cleanup thread for expired sessions

- **HTTPS Enforcement** (US-1.4)
  - Required HTTPS for Taiga API connections
  - Configurable allow-HTTP for local development (ALLOW_HTTP_TAIGA env var)
  - Clear error messages for HTTPS violations

- **Rate Limiting & Login Protection** (US-1.6)
  - Login attempt tracking with sliding window
  - Configurable rate limits (default: 5 attempts per 15 minutes)
  - Automatic lockout after max attempts
  - Configurable lockout duration (default: 30 minutes)
  - Successful login resets attempt counter
  - Disable rate limiting with zero config

#### Error Handling & Logging (Sprint 2)
- **Comprehensive Error Handling** (US-2.1, US-2.2, US-2.3)
  - Structured error responses with error_code and message
  - TaigaException handling with API error propagation
  - PermissionError for invalid/expired sessions
  - ValueError for validation failures
  - Session validation before all operations
  - Automatic error logging with context

- **Logging Infrastructure** (US-2.4, US-2.5)
  - Structured logging with JSON output capability
  - Multiple log levels (DEBUG, INFO, WARNING, ERROR, CRITICAL)
  - Configurable via LOG_LEVEL environment variable
  - Log rotation support (max 10MB, 5 backups)
  - Session ID truncation for security
  - API call logging with request/response details
  - Exception stack traces for debugging

- **Input Validation in Operations** (US-2.6)
  - Validation for all delete operations
  - Validation for all create operations
  - Validation for all update operations
  - Comprehensive test coverage for validation paths

#### Code Quality & Testing (Sprint 3-4)
- **Complete Test Coverage** (US-3.3, US-3.4, US-3.5)
  - 417+ tests covering all functionality
  - Input validation test suite with 25+ test cases
  - Delete operation test suite with 105+ tests
  - Edge case & boundary testing (19 tests):
    - Empty list handling
    - ID boundary values (0, 1, max 32-bit)
    - Large list operations (1000-10000 items)
    - Error propagation
    - Session expiry handling
    - Bulk sequential operations
  - Session management tests (48+)
  - Rate limiting tests (28+)
  - Error handling tests (20+)
  - Integration tests for all workflows

- **Code Quality Standards** (Phase 6)
  - Code formatting with black (100 character line length)
  - Import organization with isort
  - Type checking with mypy (Python 3.10 compatible)
  - Linting with flake8 (zero violations)
  - Test performance: <2 seconds for full suite
  - Test flakiness: Zero flaky tests (verified across 3 runs)
  - Code coverage: 70% (with documented gaps for post-MVP improvement)

#### Type Safety
- **TypedDict Response Types** (src/types.py)
  - Strongly-typed response objects for all MCP tools
  - TypedDict classes for:
    - Authentication (LoginResponse, LogoutResponse, SessionStatusResponse)
    - CRUD operations (CreateResponse, UpdateResponse, DeleteResponse)
    - Resource types (ProjectResponse, UserStoryResponse, TaskResponse, IssueResponse, EpicResponse, MilestoneResponse, WikiPageResponse)
    - Status information (StatusResponse, PriorityResponse, SeverityResponse, IssueTypeResponse)
  - Proper handling of optional fields with inheritance pattern for Python 3.10 compatibility
  - Resource-specific lists with type aliases

#### Configuration & Documentation
- **Environment Variables**
  - TAIGA_API_URL: Base URL for Taiga API (default: http://localhost:9000)
  - SESSION_EXPIRY: Session timeout in seconds (default: 28800 / 8 hours)
  - TAIGA_TRANSPORT: Transport mode - "stdio" or "sse" (default: stdio)
  - REQUEST_TIMEOUT: API request timeout in seconds (default: 30)
  - LOG_LEVEL: Logging level (default: INFO)
  - ALLOW_HTTP_TAIGA: Allow HTTP Taiga API for development (default: false)
  - MAX_CONCURRENT_SESSIONS: Max sessions per user (default: 5)
  - RATE_LIMIT_MAX_ATTEMPTS: Max login attempts (default: 5)
  - RATE_LIMIT_WINDOW_SECONDS: Rate limit window (default: 900 / 15 minutes)
  - RATE_LIMIT_LOCKOUT_SECONDS: Lockout duration (default: 1800 / 30 minutes)

- **Tool Configuration Files**
  - `.flake8`: Linting configuration (100 char max-line-length)
  - `.gitignore`: Git ignore patterns
  - `pyproject.toml`: Python project configuration with:
    - Build system (setuptools)
    - Dependencies (mcp, fastapi, uvicorn, pydantic, tenacity, etc.)
    - Development dependencies (pytest, black, isort, mypy, flake8)
    - Tool configurations (black, isort, mypy, pytest)

- **Documentation** (CLAUDE.md)
  - Project overview and architecture
  - Development patterns and best practices
  - Session management patterns
  - Resource access patterns
  - API parameter standardization
  - Development workflow and git process
  - Testing structure and patterns
  - Sprint 4 specific patterns and configurations

### Changed

- **Improved API Parameter Consistency**
  - Standardized LIST operations to use `project_id=` parameter
  - Standardized DELETE operations to use `id=` and `version=` parameters
  - GET operations use `get_resource()` accessor for consistency
  - Documentation of pytaigaclient library variations

### Fixed

- **Type Checking Compatibility** (Phase 6)
  - Fixed NotRequired import for Python 3.10 (conditional import from typing_extensions)
  - Fixed SessionStatusResponse TypedDict with inheritance pattern for partial optionals
  - Fixed type guards in RateLimitInfo methods
  - Configured mypy with Python 3.10 overrides for external libraries

- **Code Quality Issues** (Phase 6)
  - Fixed all black formatting violations (100 char line length)
  - Fixed import organization with isort
  - Fixed mypy type checking errors (42 → 0 errors)
  - Fixed flake8 linting (179 → 0 violations)

### Quality Metrics

- **Testing**: 417 tests passing (0 flaky, 0 regressions)
- **Performance**: Test suite completes in <2 seconds
- **Code Coverage**: 70% (up from 66% baseline)
- **Code Quality**: All checks passing (black, isort, mypy, flake8)
- **Security**: HTTPS enforcement, rate limiting, input validation, session management

### Released Features Summary

**Sprints 1-4 Deliverables** (22/22 user stories complete):
- Sprint 1: 6 stories - Input validation, session management, HTTPS enforcement
- Sprint 2: 6 stories - Error handling, logging infrastructure, operation validation
- Sprint 3: 5 stories - Input validation test suite, delete validation, error handling tests
- Sprint 4: 5 stories - Delete operation tests, edge case testing, quality gates
- Phase 6: 10 quality gate tasks - All PASSED (formatting, linting, type checking, testing)

### Technical Stack

- **Framework**: MCP (Model Context Protocol) with FastMCP
- **Language**: Python 3.10+
- **API Client**: pytaigaclient (custom fork)
- **Web Framework**: FastAPI + Uvicorn
- **Transport**: stdio (default) and SSE (Server-Sent Events)
- **Configuration**: python-dotenv
- **Validation**: pydantic + custom validators
- **Testing**: pytest with asyncio support
- **Code Quality**: black, isort, mypy, flake8

### Migration Guide

For users upgrading from 0.1.x:

1. **No Breaking Changes**: v0.2.0 is fully backward compatible with v0.1.0
2. **New Features**: All input validation is now enforced (previously warnings only)
3. **Session Management**: Sessions now expire after 8 hours (configurable)
4. **Rate Limiting**: Login attempts are now rate limited (5 attempts per 15 minutes)
5. **Environment Variables**: New optional env vars for configuration (see above)

### Known Limitations

- **Test Coverage**: 70% coverage achieved (documented gap for post-MVP improvement)
  - Uncovered areas: error paths in server.py, rarely-used utility functions
  - Post-v0.2.0 improvement: Target 85%+ coverage for v0.3.0
- **Documentation**: API endpoints documentation deferred to v0.3.0
- **Performance**: No performance optimizations applied (deferred to v0.3.0)

### Roadmap

**v0.3.0 (Code Quality & Features)** - Sprint 5-6:
- Improve test coverage to 85%+
- Add API documentation (OpenAPI/Swagger)
- Implement performance optimizations
- Add metrics and observability
- Enhance error messages and diagnostics

**v1.0.0 (Production Ready)** - Sprint 7-8:
- Production deployment guidelines
- Horizontal scaling support
- Advanced caching strategies
- Monitoring and alerting
- Backup and disaster recovery
- Security audit completion

---

**For complete implementation details, see**: [CLAUDE.md](CLAUDE.md), [docs/CONTRIBUTING_WORKFLOW.md](docs/CONTRIBUTING_WORKFLOW.md), [docs/roadmap/README.md](docs/roadmap/README.md)
