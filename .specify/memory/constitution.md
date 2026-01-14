<!--
  SYNC IMPACT REPORT: Constitution v1.3.0 Release Management & Tag Hygiene Refinements
  - Version: v1.2.0 → v1.3.0 (MINOR: Release management guidance added, tagging refined)
  - Clarified externally-facing container image tags (removed `test` tag from public API)
  - Added release management pattern: pre-release candidates before stable releases
  - Introduced tag hygiene requirement: cleanup obsolete tags to keep repository clean
  - Added guidance on release notes as external communication (not administrative)
  - Rationale: v0.2.0-rc.1 creation and tag cleanup revealed best practices for
    release workflow and public-facing communication
  - Files flagged for update: CLAUDE.md (release management section), GitHub Actions workflow docs
  - Date: 2026-01-14
-->

# Taiga MCP Bridge Constitution

## Core Principles

### I. Session-Based Security First
All authentication and resource access MUST be mediated through explicit session management. Every tool invocation MUST include a valid `session_id` parameter validated via `_get_authenticated_client()`. This eliminates ambient authority and ensures audit traceability for all operations.

**Enforcement**: Any tool proposal without session validation is rejected. Sessions expire per `SESSION_EXPIRY` config; clients MUST handle `PermissionError` gracefully.

**Anti-Pattern**: Credentials (username, password) MUST NEVER be stored in environment variables, `.env` files, or container configuration. Credentials are passed dynamically at login time by clients; the server never persists them. This prevents credential leakage in logs, backups, or container images.

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

### VI. Infrastructure Independence & Configuration Hygiene
The MCP server MUST deploy independently from Taiga, connecting to external instances via runtime parameters (host URL passed at login). The server MUST NOT require hardcoded or pre-configured Taiga endpoints, credentials, or instance-specific settings. Configuration MUST reflect operational concerns only (timeouts, limits, logging), never authentication secrets or deployment topology.

**Enforcement**:
- Code review rejects any `TAIGA_*` environment variable that encodes a Taiga host/credentials.
- `docker-compose.yml` and deployment templates do NOT include Taiga backend/database services.
- `.env.example` documents only security/operational settings; `.env` SHOULD NOT be committed to version control.
- All client authentication passes (host, username, password) as parameters to the `login` tool.

**Rationale**: Enables the same MCP server image to connect to dev, staging, or production Taiga without rebuild or configuration change. Prevents credentials leaking in container images or environment variable dumps. Supports multi-tenant and hybrid deployment scenarios.

### VII. Build & Deployment Automation & Registry Discipline
All code changes MUST trigger automated quality gates (formatting, type checking, linting, test execution) via CI/CD pipelines. Container images MUST be built, tagged with semantic versioning, and published to a container registry (GitHub Container Registry) as part of the release process. Release workflows MUST follow a pre-release-first model: test release candidates before declaring stable releases.

**Enforcement**:
- CI/CD pipeline (GitHub Actions) runs on every push to master and on release publication.
- Pipeline MUST execute: `black --check`, `isort --check`, `mypy`, `flake8`, `pytest --cov` with >80% coverage threshold.
- **Internal tags** (development only, not documented externally): `dev` for every master push.
- **Pre-release tags**: `vX.Y.Z-rc.N` (e.g., `v0.2.0-rc.1`) on pre-release publication; used for validation testing.
- **Stable release tags**: `vX.Y.Z` (exact), `vX.Y` (latest patch), `vX` (latest patch), `latest` (newest stable) on stable release publication.
- Registry MUST be GitHub Container Registry (`ghcr.io`); no hardcoded registry credentials in source code.
- Pipeline MUST reject builds that fail quality gates; only passing builds produce deployable artifacts.
- **Tag Hygiene**: Old sprint/development tags MUST be deleted before declaring milestones; only version tags and `dev` remain.

**Release Management Pattern**:
1. Create pre-release (RC) - tests full CI/CD pipeline, allows community validation
2. Validate in real-world usage - fix issues if needed in subsequent RCs
3. Create stable release - automatic semantic version tagging
4. Cleanup obsolete tags - remove old sprint/development tags for repository cleanliness

**Rationale**: Automated validation prevents quality regressions. Pre-release-first pattern enables real-world testing before declaring stable versions. Semantic versioning on container images enables pinning and rollback. Decoupling code quality checks from manual PR review reduces human error. Tag cleanup maintains repository hygiene and clarity of version history.

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
- No credentials, host URLs, or instance-specific settings in environment config
- Error handling catches `TaigaException` explicitly
- Breaking changes documented and approved
- Deployment templates (docker-compose, k8s) do not include Taiga services
- CI/CD validation passed (GitHub Actions green; no quality gate overrides)

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

### Version Policy (Constitution)
- **MAJOR**: Backward-incompatible governance change (e.g., authentication model redesign, principle removal)
- **MINOR**: New principle, new mandatory section, materially expanded guidance
- **PATCH**: Clarifications, wording refinements, typo fixes, non-semantic enforcement updates

### Container Image Tagging & Release Strategy
**Internal Tags** (not documented externally; development-only):
- **dev**: Automatic tag on every master branch push; always latest development build

**External Tags** (documented in release notes; users should pin to these):
- **vX.Y.Z-rc.N**: Pre-release release candidate (e.g., `v0.2.0-rc.1`); auto-tagged on pre-release publication
  - For testing and community validation before stable release
  - Subject to change before stable version
- **vX.Y.Z**: Stable release (e.g., `v0.2.0`); exact, immutable version match
- **vX.Y**: Latest patch in minor version (e.g., `v0.2`); floating tag for automatic updates
- **vX**: Latest patch in major version (e.g., `v0`); floating tag for automatic updates
- **latest**: Newest stable release; floating tag for users who want latest stable

**Tag Cleanup Policy**:
- Obsolete sprint/development tags (e.g., `sprint4/us-2.6-delete-validation`) deleted before milestone release
- Only semantic version tags and `dev` retained long-term
- Reduces repository clutter and clarifies version history

### Release Notes & External Communication
- Release notes are the primary user-facing documentation - MUST focus on features and capabilities, not administrative details
- Release notes MUST include: features, deployment instructions, testing guidance, known limitations, and feedback channels
- Release notes SHOULD NOT include: internal process details, test framework specifics, or tool configuration minutiae
- Pre-release notes SHOULD include disclaimer about RC status and encourage testing/feedback

### Compliance Review
- Quarterly review of constitution adherence (spot-check 3-5 PRs for checklist completion)
- Annual full roadmap review and constitution alignment assessment
- Runtime guidance in CLAUDE.md supersedes boilerplate; updates to CLAUDE.md trigger patch version bump
- Release workflow audits verify RC→stable pattern followed and tag cleanup completed

### Dispute Resolution
When a PR conflicts with constitution principles:
1. Commenter references specific principle and enforcement rule
2. PR author responds with data/rationale or agrees to refactor
3. If unresolved after 48 hours, escalate to project maintainers for decision
4. Decision documented in PR comment (link to constitution principle for future reference)

**Version**: 1.3.0 | **Ratified**: 2026-01-12 | **Last Amended**: 2026-01-14
