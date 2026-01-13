"""
Unit tests for error paths in delete operations.
Tests that all delete operations properly handle common HTTP error responses.
Covers 404 (not found), 403 (permission denied), 409 (conflict) errors.
"""

import pytest
from unittest.mock import Mock, patch
from pytaigaclient.exceptions import TaigaException


class TestDeleteOperations404Errors:
    """Test cases for 404 Not Found errors across all delete operations"""

    @patch("src.server._get_authenticated_client")
    def test_delete_project_404(self, mock_auth):
        """Should propagate 404 error when project not found"""
        from src.server import delete_project

        mock_client = Mock()
        mock_auth.return_value = mock_client
        mock_client.api.projects.delete.side_effect = TaigaException("404 Not Found: Project does not exist")

        with pytest.raises(TaigaException, match="404"):
            delete_project(session_id="test-session", project_id=999)

    @patch("src.server._get_authenticated_client")
    def test_delete_epic_404(self, mock_auth):
        """Should propagate 404 error when epic not found"""
        from src.server import delete_epic

        mock_client = Mock()
        mock_auth.return_value = mock_client
        mock_client.api.epics.delete.side_effect = TaigaException("404 Not Found: Epic does not exist")

        with pytest.raises(TaigaException, match="404"):
            delete_epic(session_id="test-session", epic_id=999)

    @patch("src.server._get_authenticated_client")
    def test_delete_user_story_404(self, mock_auth):
        """Should propagate 404 error when user story not found"""
        from src.server import delete_user_story

        mock_client = Mock()
        mock_auth.return_value = mock_client
        mock_client.api.user_stories.delete.side_effect = TaigaException("404 Not Found: User story does not exist")

        with pytest.raises(TaigaException, match="404"):
            delete_user_story(session_id="test-session", user_story_id=999)

    @patch("src.server._get_authenticated_client")
    def test_delete_task_404(self, mock_auth):
        """Should propagate 404 error when task not found"""
        from src.server import delete_task

        mock_client = Mock()
        mock_auth.return_value = mock_client
        mock_client.api.tasks.delete.side_effect = TaigaException("404 Not Found: Task does not exist")

        with pytest.raises(TaigaException, match="404"):
            delete_task(session_id="test-session", task_id=999)

    @patch("src.server._get_authenticated_client")
    def test_delete_issue_404(self, mock_auth):
        """Should propagate 404 error when issue not found"""
        from src.server import delete_issue

        mock_client = Mock()
        mock_auth.return_value = mock_client
        mock_client.api.issues.delete.side_effect = TaigaException("404 Not Found: Issue does not exist")

        with pytest.raises(TaigaException, match="404"):
            delete_issue(session_id="test-session", issue_id=999)

    @patch("src.server._get_authenticated_client")
    def test_delete_milestone_404(self, mock_auth):
        """Should propagate 404 error when milestone not found"""
        from src.server import delete_milestone

        mock_client = Mock()
        mock_auth.return_value = mock_client
        mock_client.api.milestones.delete.side_effect = TaigaException("404 Not Found: Milestone does not exist")

        with pytest.raises(TaigaException, match="404"):
            delete_milestone(session_id="test-session", milestone_id=999)


class TestDeleteOperations403Errors:
    """Test cases for 403 Forbidden errors across all delete operations"""

    @patch("src.server._get_authenticated_client")
    def test_delete_project_403(self, mock_auth):
        """Should propagate 403 error when user lacks permission"""
        from src.server import delete_project

        mock_client = Mock()
        mock_auth.return_value = mock_client
        mock_client.api.projects.delete.side_effect = TaigaException("403 Forbidden: User lacks permission to delete project")

        with pytest.raises(TaigaException, match="403"):
            delete_project(session_id="test-session", project_id=123)

    @patch("src.server._get_authenticated_client")
    def test_delete_epic_403(self, mock_auth):
        """Should propagate 403 error when user lacks permission"""
        from src.server import delete_epic

        mock_client = Mock()
        mock_auth.return_value = mock_client
        mock_client.api.epics.delete.side_effect = TaigaException("403 Forbidden: User lacks permission to delete epic")

        with pytest.raises(TaigaException, match="403"):
            delete_epic(session_id="test-session", epic_id=456)

    @patch("src.server._get_authenticated_client")
    def test_delete_user_story_403(self, mock_auth):
        """Should propagate 403 error when user lacks permission"""
        from src.server import delete_user_story

        mock_client = Mock()
        mock_auth.return_value = mock_client
        mock_client.api.user_stories.delete.side_effect = TaigaException("403 Forbidden: User lacks permission to delete user story")

        with pytest.raises(TaigaException, match="403"):
            delete_user_story(session_id="test-session", user_story_id=200)

    @patch("src.server._get_authenticated_client")
    def test_delete_task_403(self, mock_auth):
        """Should propagate 403 error when user lacks permission"""
        from src.server import delete_task

        mock_client = Mock()
        mock_auth.return_value = mock_client
        mock_client.api.tasks.delete.side_effect = TaigaException("403 Forbidden: User lacks permission to delete task")

        with pytest.raises(TaigaException, match="403"):
            delete_task(session_id="test-session", task_id=250)

    @patch("src.server._get_authenticated_client")
    def test_delete_issue_403(self, mock_auth):
        """Should propagate 403 error when user lacks permission"""
        from src.server import delete_issue

        mock_client = Mock()
        mock_auth.return_value = mock_client
        mock_client.api.issues.delete.side_effect = TaigaException("403 Forbidden: User lacks permission to delete issue")

        with pytest.raises(TaigaException, match="403"):
            delete_issue(session_id="test-session", issue_id=300)

    @patch("src.server._get_authenticated_client")
    def test_delete_milestone_403(self, mock_auth):
        """Should propagate 403 error when user lacks permission"""
        from src.server import delete_milestone

        mock_client = Mock()
        mock_auth.return_value = mock_client
        mock_client.api.milestones.delete.side_effect = TaigaException("403 Forbidden: User lacks permission to delete milestone")

        with pytest.raises(TaigaException, match="403"):
            delete_milestone(session_id="test-session", milestone_id=350)


class TestDeleteOperations409Errors:
    """Test cases for 409 Conflict errors across all delete operations"""

    @patch("src.server._get_authenticated_client")
    def test_delete_project_409_version_conflict(self, mock_auth):
        """Should propagate 409 conflict when project was modified"""
        from src.server import delete_project

        mock_client = Mock()
        mock_auth.return_value = mock_client
        mock_client.api.projects.delete.side_effect = TaigaException("409 Conflict: Project was modified by another user")

        with pytest.raises(TaigaException, match="409"):
            delete_project(session_id="test-session", project_id=123)

    @patch("src.server._get_authenticated_client")
    def test_delete_epic_409_version_conflict(self, mock_auth):
        """Should propagate 409 conflict when epic was modified"""
        from src.server import delete_epic

        mock_client = Mock()
        mock_auth.return_value = mock_client
        mock_client.api.epics.delete.side_effect = TaigaException("409 Conflict: Epic was modified by another user")

        with pytest.raises(TaigaException, match="409"):
            delete_epic(session_id="test-session", epic_id=456)

    @patch("src.server._get_authenticated_client")
    def test_delete_user_story_409_version_conflict(self, mock_auth):
        """Should propagate 409 conflict when user story was modified"""
        from src.server import delete_user_story

        mock_client = Mock()
        mock_auth.return_value = mock_client
        mock_client.api.user_stories.delete.side_effect = TaigaException("409 Conflict: User story was modified by another user")

        with pytest.raises(TaigaException, match="409"):
            delete_user_story(session_id="test-session", user_story_id=200)

    @patch("src.server._get_authenticated_client")
    def test_delete_task_409_version_conflict(self, mock_auth):
        """Should propagate 409 conflict when task was modified"""
        from src.server import delete_task

        mock_client = Mock()
        mock_auth.return_value = mock_client
        mock_client.api.tasks.delete.side_effect = TaigaException("409 Conflict: Task was modified by another user")

        with pytest.raises(TaigaException, match="409"):
            delete_task(session_id="test-session", task_id=250)

    @patch("src.server._get_authenticated_client")
    def test_delete_issue_409_version_conflict(self, mock_auth):
        """Should propagate 409 conflict when issue was modified"""
        from src.server import delete_issue

        mock_client = Mock()
        mock_auth.return_value = mock_client
        mock_client.api.issues.delete.side_effect = TaigaException("409 Conflict: Issue was modified by another user")

        with pytest.raises(TaigaException, match="409"):
            delete_issue(session_id="test-session", issue_id=300)

    @patch("src.server._get_authenticated_client")
    def test_delete_milestone_409_version_conflict(self, mock_auth):
        """Should propagate 409 conflict when milestone was modified"""
        from src.server import delete_milestone

        mock_client = Mock()
        mock_auth.return_value = mock_client
        mock_client.api.milestones.delete.side_effect = TaigaException("409 Conflict: Milestone was modified by another user")

        with pytest.raises(TaigaException, match="409"):
            delete_milestone(session_id="test-session", milestone_id=350)


class TestDeleteOperationConsistentErrors:
    """Test that all delete operations handle errors consistently"""

    @patch("src.server._get_authenticated_client")
    def test_all_delete_operations_reject_invalid_session(self, mock_auth):
        """All delete operations should reject invalid session ID"""
        from src.server import (
            delete_project,
            delete_epic,
            delete_user_story,
            delete_task,
            delete_issue,
            delete_milestone,
        )

        mock_auth.side_effect = PermissionError("Invalid session")

        operations = [
            (delete_project, {"session_id": "invalid", "project_id": 1}),
            (delete_epic, {"session_id": "invalid", "epic_id": 1}),
            (delete_user_story, {"session_id": "invalid", "user_story_id": 1}),
            (delete_task, {"session_id": "invalid", "task_id": 1}),
            (delete_issue, {"session_id": "invalid", "issue_id": 1}),
            (delete_milestone, {"session_id": "invalid", "milestone_id": 1}),
        ]

        for operation, kwargs in operations:
            with pytest.raises(PermissionError, match="Invalid session"):
                operation(**kwargs)

    @patch("src.server._get_authenticated_client")
    def test_all_delete_operations_propagate_404_errors(self, mock_auth):
        """All delete operations should propagate 404 errors from API"""
        from src.server import (
            delete_project,
            delete_epic,
            delete_user_story,
            delete_task,
            delete_issue,
            delete_milestone,
        )

        mock_client = Mock()
        mock_auth.return_value = mock_client

        operations_and_resources = [
            (delete_project, {"session_id": "test", "project_id": 999}, "projects"),
            (delete_epic, {"session_id": "test", "epic_id": 999}, "epics"),
            (delete_user_story, {"session_id": "test", "user_story_id": 999}, "user_stories"),
            (delete_task, {"session_id": "test", "task_id": 999}, "tasks"),
            (delete_issue, {"session_id": "test", "issue_id": 999}, "issues"),
            (delete_milestone, {"session_id": "test", "milestone_id": 999}, "milestones"),
        ]

        for operation, kwargs, resource in operations_and_resources:
            mock_client.reset_mock()
            getattr(mock_client.api, resource).delete.side_effect = TaigaException("404 Not Found")

            with pytest.raises(TaigaException, match="404"):
                operation(**kwargs)
