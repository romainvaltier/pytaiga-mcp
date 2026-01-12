<!--
  SYNC IMPACT REPORT: Constitution v1.0.0 Initial Creation
  - Version: Created at v1.0.0 (first constitution adoption)
  - Five core principles established for Taiga MCP Bridge
  - Governance framework aligned with GitHub Flow workflow
  - Templates updated for consistency with these principles
-->

# Taiga MCP Bridge Constitution

## Core Principles

### I. Session-Based Security First
All authentication and resource access MUST be mediated through explicit session management. Every tool invocation MUST include a valid `session_id` parameter validated via `_get_authenticated_client()`. This eliminates ambient authority and ensures audit traceability for all operations.

**Enforcement**: Any tool proposal without session validation is rejected. Sessions expire per `SESSION_EXPIRY` config; clients MUST handle `PermissionError` gracefully.

### II. API Parameter Standardization
All pytaigaclient method calls MUST follow strict, documented parameter conventions. LIST operations use `project_id=`, GET operations use named/positional per library requirements, UPDATE/CREATE/DELETE operations use their designated signatures. Centralize library quirks in `TaigaClientWrapper.get_resource()`.

**Enforcement**: Code review MUST verify parameter conformance against CLAUDE.md API Parameter Standardization section. No direct `api.{resource}.get()` calls allowed; always use abstracted wrappers.

### III. Independent Resource Access Pattern
All resource retrieval MUST use the unified `TaigaClientWrapper.get_resource(resource_type, resource_id)` accessor pattern. This centralizes pytaigaclient variations and ensures consistent error handling and logging across all resource types (project, user_story, task, issue, epic, milestone, wiki_page).

**Enforcement**: Code review catches direct API calls and enforces use of accessor wrappers. Logging MUST capture resource access for debugging.

### IV. Test-First Discipline with Markers
Tests are organized by resource type (auth, core, projects, epics, user_stories, tasks, issues, sprints) and test type (unit, integration, slow). New features MUST include tests that fail before implementation. Minimum coverage threshold is 80%; PRs without test improvements are blocked.

**Enforcement**: CI/CD gates coverage >80%. Integration tests marked `@pytest.mark.integration` for selective runs. `pytest -m` commands verify correct markers are applied.

### V. Transport Agnosticity & Configuration
The server MUST support both stdio (default, CLI clients) and SSE (web clients) transport modes without code branching. All configuration sourced from environment variables or `.env` file. No hardcoded production values allowed.

**Enforcement**: All transport-specific code isolated in transport layer. Configuration tests verify both modes initialize correctly. Environment variable documentation required in README and code comments.

## Development Workflow & Quality Gates

### Branching & Commit Discipline
- **Branch Naming**: `feature/EPIC-#-description`, `fix/description`, `test/description`, `refactor/description`, `docs/description`, `chore/description`
- **Commit Format**: Conventional Commits with epic reference (e.g., `feat(EPIC-1): description`)
- **Merge Strategy**: Squash and merge to keep history clean; one PR per user story

### Definition of Done (Mandatory for all PRs)
- Code formatted (`black`, `isort`) and type-checked (`mypy`, no errors)
- Linting passes (`flake8`)
- Tests written for new functionality; all tests passing with >80% coverage
- Integration tests added for feature areas
- PR reviewed and approved by at least one other developer
- Documentation updated if applicable
- Roadmap story marked complete in `docs/roadmap/SPRINT_PLANNING.md`

### Code Review Checklist
- Session validation via `_get_authenticated_client()`
- API parameters conform to standardized patterns (CLAUDE.md section)
- Resource access uses `get_resource()` wrapper
- Test coverage >80%, markers correctly applied
- No hardcoded configuration values
- Error handling catches `TaigaException` explicitly
- Breaking changes documented and approved

## Roadmap Integration

The project roadmap (`docs/roadmap/`) defines 5 Epics, 23 User Stories (239 points), and 8+ sprints over 16-20 weeks toward three release milestones:
- **v0.2.0 (MVP)**: Core session-based CRUD operations
- **v0.3.0 (Features)**: Advanced query, filtering, and resource management
- **v1.0.0 (Production)**: Security hardening, observability, performance optimization

All PR work MUST reference and align with active sprint stories. Roadmap status updated after PR merge.

## Governance

### Amendment Procedure
1. **Proposal**: Document amendment rationale (principle change, enforcement gap, new requirement)
2. **Discussion**: Code review discussion or team meeting (must involve >1 contributor)
3. **Ratification**: Agreement from active maintainers; update version per semver rules
4. **Propagation**: Update CLAUDE.md, templates, and roadmap documentation; commit as `docs: amend constitution to vX.Y.Z`

### Version Policy
- **MAJOR**: Backward-incompatible governance change (e.g., authentication model redesign, principle removal)
- **MINOR**: New principle, new mandatory section, materially expanded guidance
- **PATCH**: Clarifications, wording refinements, typo fixes, non-semantic enforcement updates

### Compliance Review
- Quarterly review of constitution adherence (spot-check 3-5 PRs for checklist completion)
- Annual full roadmap review and constitution alignment assessment
- Runtime guidance in CLAUDE.md supersedes boilerplate; updates to CLAUDE.md trigger patch version bump

### Dispute Resolution
When a PR conflicts with constitution principles:
1. Commenter references specific principle and enforcement rule
2. PR author responds with data/rationale or agrees to refactor
3. If unresolved after 48 hours, escalate to project maintainers for decision
4. Decision documented in PR comment (link to constitution principle for future reference)

**Version**: 1.0.0 | **Ratified**: 2026-01-12 | **Last Amended**: 2026-01-12
