"""
Error handling test suite for resource operations and API error scenarios.

Tests key error paths across resource types:
- Input validation errors
- Session authentication/authorization errors
- TaigaException errors (404, 403, conflict)
- Network errors and timeout handling
- Unexpected exception handling

Focuses on representative sampling to achieve 90%+ error path coverage.
Total: 38 tests across 7 resource types and 3 error categories.
"""

import uuid
from datetime import datetime, timedelta
from unittest.mock import MagicMock, patch

import pytest
from pytaigaclient.exceptions import TaigaException

import src.server
from src.types import SessionInfo


class TestErrorHandlingSetup:
    """Setup fixtures for error handling tests."""

    @pytest.fixture
    def authenticated_session(self):
        """Create an authenticated session for testing."""
        session_id = str(uuid.uuid4())
        mock_client = MagicMock()
        mock_client.is_authenticated = True

        session_info = SessionInfo(session_id=session_id, client=mock_client, username="test_user")
        src.server.active_sessions[session_id] = session_info

        yield session_id, mock_client

        # Cleanup
        if session_id in src.server.active_sessions:
            del src.server.active_sessions[session_id]


# ============================================================================
# CATEGORY 1: Input Validation Error Tests (14 tests)
# Tests that validate inputs are properly checked before API calls
# ============================================================================


class TestInputValidationErrors(TestErrorHandlingSetup):
    """Test input validation errors across resource types."""

    def test_create_project_empty_name(self, authenticated_session):
        """Test CREATE project fails with empty name."""
        session_id, _ = authenticated_session
        with pytest.raises(ValueError):
            src.server.create_project(session_id=session_id, name="", description="test")

    def test_create_project_empty_description(self, authenticated_session):
        """Test CREATE project fails with empty description."""
        session_id, _ = authenticated_session
        with pytest.raises(ValueError):
            src.server.create_project(session_id=session_id, name="Test", description="")

    def test_create_user_story_empty_subject(self, authenticated_session):
        """Test CREATE user story fails with empty subject."""
        session_id, _ = authenticated_session
        with pytest.raises(ValueError):
            src.server.create_user_story(session_id=session_id, project_id=1, subject="")

    def test_create_task_empty_subject(self, authenticated_session):
        """Test CREATE task fails with empty subject."""
        session_id, _ = authenticated_session
        with pytest.raises(ValueError):
            src.server.create_task(session_id=session_id, project_id=1, subject="")

    def test_create_issue_empty_subject(self, authenticated_session):
        """Test CREATE issue fails with empty subject."""
        session_id, _ = authenticated_session
        with pytest.raises(ValueError):
            src.server.create_issue(
                session_id=session_id,
                project_id=1,
                subject="",
                priority_id=1,
                status_id=1,
                severity_id=1,
                type_id=1,
            )

    def test_create_epic_empty_subject(self, authenticated_session):
        """Test CREATE epic fails with empty subject."""
        session_id, _ = authenticated_session
        with pytest.raises(ValueError):
            src.server.create_epic(session_id=session_id, project_id=1, subject="")

    def test_create_milestone_empty_name(self, authenticated_session):
        """Test CREATE milestone fails with empty name."""
        session_id, _ = authenticated_session
        with pytest.raises(ValueError):
            src.server.create_milestone(
                session_id=session_id,
                project_id=1,
                name="",
                estimated_start="2026-01-15",
                estimated_finish="2026-01-31",
            )

    def test_invalid_project_id_negative(self, authenticated_session):
        """Test that negative project ID is rejected."""
        session_id, _ = authenticated_session
        with pytest.raises(ValueError):
            src.server.create_user_story(session_id=session_id, project_id=-1, subject="Test")

    def test_project_name_too_long(self, authenticated_session):
        """Test that excessively long project name is rejected."""
        session_id, _ = authenticated_session
        long_name = "x" * 1001  # Exceeds max length
        with pytest.raises(ValueError):
            src.server.create_project(session_id=session_id, name=long_name, description="test")

    def test_project_description_too_long(self, authenticated_session):
        """Test that excessively long description is rejected."""
        session_id, _ = authenticated_session
        long_desc = "x" * 10001  # Exceeds max length
        with pytest.raises(ValueError):
            src.server.create_project(session_id=session_id, name="Test", description=long_desc)

    def test_user_story_subject_too_long(self, authenticated_session):
        """Test that excessively long subject is rejected."""
        session_id, _ = authenticated_session
        long_subject = "x" * 501
        with pytest.raises(ValueError):
            src.server.create_user_story(session_id=session_id, project_id=1, subject=long_subject)

    def test_task_subject_too_long(self, authenticated_session):
        """Test that excessively long task subject is rejected."""
        session_id, _ = authenticated_session
        long_subject = "x" * 501
        with pytest.raises(ValueError):
            src.server.create_task(session_id=session_id, project_id=1, subject=long_subject)

    def test_epic_subject_too_long(self, authenticated_session):
        """Test that excessively long epic subject is rejected."""
        session_id, _ = authenticated_session
        long_subject = "x" * 501
        with pytest.raises(ValueError):
            src.server.create_epic(session_id=session_id, project_id=1, subject=long_subject)

    def test_create_milestone_empty_dates(self, authenticated_session):
        """Test that milestone with empty dates is rejected."""
        session_id, _ = authenticated_session
        with pytest.raises(ValueError):
            src.server.create_milestone(
                session_id=session_id,
                project_id=1,
                name="Sprint 1",
                estimated_start="",
                estimated_finish="",
            )


# ============================================================================
# CATEGORY 2: Session and Authentication Error Tests (4 tests)
# Tests for invalid and expired session handling
# ============================================================================


class TestSessionAuthenticationErrors(TestErrorHandlingSetup):
    """Test session validation and authentication errors."""

    def test_invalid_session_id(self):
        """Test handling of completely invalid session ID."""
        with pytest.raises(PermissionError):
            src.server.get_project(session_id="invalid-session", project_id=1)

    def test_invalid_session_id_get_user_story(self):
        """Test handling of invalid session for user story operation."""
        with pytest.raises(PermissionError):
            src.server.get_user_story(session_id="nonexistent-session", user_story_id=1)

    def test_expired_session_id(self):
        """Test handling of expired session."""
        session_id = str(uuid.uuid4())
        mock_client = MagicMock()

        session_info = SessionInfo(session_id=session_id, client=mock_client, username="test_user")
        # Force expiration
        session_info.expires_at = datetime.utcnow() - timedelta(hours=1)

        src.server.active_sessions[session_id] = session_info

        try:
            with pytest.raises(PermissionError):
                src.server.get_project(session_id=session_id, project_id=1)
        finally:
            if session_id in src.server.active_sessions:
                del src.server.active_sessions[session_id]

    def test_expired_session_get_tasks(self):
        """Test handling of expired session for tasks operation."""
        session_id = str(uuid.uuid4())
        mock_client = MagicMock()

        session_info = SessionInfo(session_id=session_id, client=mock_client, username="test_user")
        # Force expiration
        session_info.expires_at = datetime.utcnow() - timedelta(minutes=1)

        src.server.active_sessions[session_id] = session_info

        try:
            with pytest.raises(PermissionError):
                src.server.list_tasks(session_id=session_id, project_id=1)
        finally:
            if session_id in src.server.active_sessions:
                del src.server.active_sessions[session_id]


# ============================================================================
# CATEGORY 3: TaigaException and API Error Tests (16 tests)
# Tests for 404, 403, and conflict errors from Taiga API
# ============================================================================


class TestTaigaAPINotFoundErrors(TestErrorHandlingSetup):
    """Test 404 Not Found error handling."""

    def test_get_project_not_found(self, authenticated_session):
        """Test GET project with 404 error."""
        session_id, mock_client = authenticated_session
        mock_client.get_resource.side_effect = TaigaException({"detail": "Not found."}, 404)

        with pytest.raises(TaigaException):
            src.server.get_project(session_id=session_id, project_id=99999)

    def test_get_user_story_not_found(self, authenticated_session):
        """Test GET user story with 404 error."""
        session_id, mock_client = authenticated_session
        mock_client.get_resource.side_effect = TaigaException({"detail": "Not found."}, 404)

        with pytest.raises(TaigaException):
            src.server.get_user_story(session_id=session_id, user_story_id=99999)

    def test_get_task_not_found(self, authenticated_session):
        """Test GET task with 404 error."""
        session_id, mock_client = authenticated_session
        mock_client.get_resource.side_effect = TaigaException({"detail": "Not found."}, 404)

        with pytest.raises(TaigaException):
            src.server.get_task(session_id=session_id, task_id=99999)

    def test_get_issue_not_found(self, authenticated_session):
        """Test GET issue with 404 error."""
        session_id, mock_client = authenticated_session
        mock_client.get_resource.side_effect = TaigaException({"detail": "Not found."}, 404)

        with pytest.raises(TaigaException):
            src.server.get_issue(session_id=session_id, issue_id=99999)

    def test_get_epic_not_found(self, authenticated_session):
        """Test GET epic with 404 error."""
        session_id, mock_client = authenticated_session
        mock_client.get_resource.side_effect = TaigaException({"detail": "Not found."}, 404)

        with pytest.raises(TaigaException):
            src.server.get_epic(session_id=session_id, epic_id=99999)

    def test_get_milestone_not_found(self, authenticated_session):
        """Test GET milestone with 404 error."""
        session_id, mock_client = authenticated_session
        mock_client.get_resource.side_effect = TaigaException({"detail": "Not found."}, 404)

        with pytest.raises(TaigaException):
            src.server.get_milestone(session_id=session_id, milestone_id=99999)

    def test_list_wiki_pages_not_found(self, authenticated_session):
        """Test LIST wiki pages with 404 error."""
        session_id, mock_client = authenticated_session
        mock_client.api.wiki.list.side_effect = TaigaException(
            {"detail": "Project not found."}, 404
        )

        with pytest.raises(TaigaException):
            src.server.list_wiki_pages(session_id=session_id, project_id=99999)

    def test_get_wiki_page_not_found(self, authenticated_session):
        """Test GET wiki page with 404 error."""
        session_id, mock_client = authenticated_session
        mock_client.get_resource.side_effect = TaigaException({"detail": "Not found."}, 404)

        with pytest.raises(TaigaException):
            src.server.get_wiki_page(session_id=session_id, wiki_page_id=99999)


class TestTaigaAPIForbiddenErrors(TestErrorHandlingSetup):
    """Test 403 Forbidden error handling."""

    def test_get_project_forbidden(self, authenticated_session):
        """Test GET project with 403 Forbidden."""
        session_id, mock_client = authenticated_session
        mock_client.get_resource.side_effect = TaigaException({"detail": "Permission denied."}, 403)

        with pytest.raises(TaigaException):
            src.server.get_project(session_id=session_id, project_id=1)

    def test_get_user_story_forbidden(self, authenticated_session):
        """Test GET user story with 403 Forbidden."""
        session_id, mock_client = authenticated_session
        mock_client.get_resource.side_effect = TaigaException({"detail": "Permission denied."}, 403)

        with pytest.raises(TaigaException):
            src.server.get_user_story(session_id=session_id, user_story_id=1)

    def test_list_tasks_forbidden(self, authenticated_session):
        """Test LIST tasks with 403 Forbidden."""
        session_id, mock_client = authenticated_session
        mock_client.api.tasks.list.side_effect = TaigaException(
            {"detail": "Permission denied."}, 403
        )

        with pytest.raises(TaigaException):
            src.server.list_tasks(session_id=session_id, project_id=1)

    def test_list_issues_forbidden(self, authenticated_session):
        """Test LIST issues with 403 Forbidden."""
        session_id, mock_client = authenticated_session
        mock_client.api.issues.list.side_effect = TaigaException(
            {"detail": "Permission denied."}, 403
        )

        with pytest.raises(TaigaException):
            src.server.list_issues(session_id=session_id, project_id=1)


class TestTaigaAPIConflictErrors(TestErrorHandlingSetup):
    """Test 409 Conflict error handling (version mismatches)."""

    def test_delete_project_with_dependencies(self, authenticated_session):
        """Test DELETE project fails when it has dependencies."""
        session_id, mock_client = authenticated_session
        mock_client.api.projects.delete.side_effect = TaigaException(
            {"detail": "Cannot delete project with active user stories"}, 409
        )

        with pytest.raises(TaigaException):
            src.server.delete_project(session_id=session_id, project_id=1)

    def test_delete_epic_forbidden(self, authenticated_session):
        """Test DELETE epic with forbidden error."""
        session_id, mock_client = authenticated_session
        mock_client.api.epics.delete.side_effect = TaigaException(
            {"detail": "Permission denied."}, 403
        )

        with pytest.raises(TaigaException):
            src.server.delete_epic(session_id=session_id, epic_id=1)

    def test_delete_milestone_not_found(self, authenticated_session):
        """Test DELETE milestone with not found error."""
        session_id, mock_client = authenticated_session
        mock_client.api.milestones.delete.side_effect = TaigaException(
            {"detail": "Not found."}, 404
        )

        with pytest.raises(TaigaException):
            src.server.delete_milestone(session_id=session_id, milestone_id=99999)

    def test_delete_user_story_cascade_error(self, authenticated_session):
        """Test DELETE user story fails with cascade error."""
        session_id, mock_client = authenticated_session
        mock_client.api.user_stories.delete.side_effect = TaigaException(
            {"detail": "Cannot delete story with linked tasks"}, 409
        )

        with pytest.raises(TaigaException):
            src.server.delete_user_story(session_id=session_id, user_story_id=1)


# ============================================================================
# CATEGORY 4: Network and Exception Error Tests (4 tests)
# Tests for network timeouts, connection errors, and unexpected exceptions
# ============================================================================


class TestNetworkAndExceptionErrors(TestErrorHandlingSetup):
    """Test network errors and unexpected exception handling."""

    def test_connection_timeout_on_list(self, authenticated_session):
        """Test connection timeout wrapped in RuntimeError."""
        session_id, mock_client = authenticated_session
        mock_client.api.projects.list.side_effect = TimeoutError("Connection timeout")

        with pytest.raises(RuntimeError):
            src.server.list_projects(session_id=session_id)

    def test_connection_error_on_create(self, authenticated_session):
        """Test connection error on create operation."""
        session_id, mock_client = authenticated_session
        mock_client.api.user_stories.create.side_effect = ConnectionError("Connection refused")

        with pytest.raises(RuntimeError):
            src.server.create_user_story(session_id=session_id, project_id=1, subject="Test")

    def test_read_timeout_on_get(self, authenticated_session):
        """Test read timeout on GET operation."""
        session_id, mock_client = authenticated_session
        mock_client.get_resource.side_effect = TimeoutError("Read timeout")

        with pytest.raises(RuntimeError):
            src.server.get_user_story(session_id=session_id, user_story_id=1)

    def test_generic_exception_on_delete(self, authenticated_session):
        """Test generic exception handling on delete."""
        session_id, mock_client = authenticated_session
        mock_client.api.issues.delete.side_effect = Exception("Unexpected error")

        with pytest.raises(RuntimeError):
            src.server.delete_issue(session_id=session_id, issue_id=1)
