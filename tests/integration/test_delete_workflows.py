"""
Integration tests for complete delete operation workflows.
Tests end-to-end delete workflows across multiple resource types and scenarios.
"""

import pytest
from unittest.mock import Mock, patch, call
from pytaigaclient.exceptions import TaigaException


class TestDeleteCompleteWorkflows:
    """Test cases for complete delete workflows"""

    @patch("src.server._get_authenticated_client")
    def test_delete_project_complete_workflow(self, mock_auth):
        """Should handle complete project deletion workflow"""
        from src.server import delete_project

        mock_client = Mock()
        mock_auth.return_value = mock_client

        # Test workflow: validate session, validate input, delete, return result
        result = delete_project(session_id="valid-session-123", project_id=42)

        # Verify authentication check happened (implicit from _get_authenticated_client)
        mock_auth.assert_called_once_with("valid-session-123")

        # Verify input validation (implicit from validation functions)
        # Verify API call
        mock_client.api.projects.delete.assert_called_once_with(id=42)

        # Verify response
        assert result["status"] == "deleted"
        assert result["project_id"] == 42

    @patch("src.server._get_authenticated_client")
    def test_delete_user_story_complete_workflow_with_validation(self, mock_auth):
        """Should handle complete user story deletion with validation"""
        from src.server import delete_user_story

        mock_client = Mock()
        mock_auth.return_value = mock_client

        # Test workflow with validation
        result = delete_user_story(session_id="valid-session-456", user_story_id=100)

        # Verify session check
        mock_auth.assert_called_once_with("valid-session-456")

        # Verify API call
        mock_client.api.user_stories.delete.assert_called_once_with(id=100)

        # Verify response
        assert result["status"] == "deleted"
        assert result["user_story_id"] == 100

    @patch("src.server._get_authenticated_client")
    def test_delete_invalid_input_fails_before_api_call_workflow(self, mock_auth):
        """Should fail on invalid input before making API call"""
        from src.server import delete_user_story

        mock_client = Mock()
        mock_auth.return_value = mock_client

        # Test workflow: validation should fail BEFORE API call
        with pytest.raises(ValueError, match="positive integer"):
            delete_user_story(session_id="valid-session", user_story_id=-1)

        # Verify API was NOT called
        mock_client.api.user_stories.delete.assert_not_called()

    @patch("src.server._get_authenticated_client")
    def test_delete_invalid_session_fails_immediately_workflow(self, mock_auth):
        """Should fail immediately on invalid session"""
        from src.server import delete_issue

        mock_auth.side_effect = PermissionError("Invalid session")

        # Test workflow: session validation should fail FIRST
        with pytest.raises(PermissionError, match="Invalid session"):
            delete_issue(session_id="invalid-session", issue_id=200)

        # Verify authentication was checked
        mock_auth.assert_called_once()

    @patch("src.server._get_authenticated_client")
    def test_delete_api_not_found_error_workflow(self, mock_auth):
        """Should handle complete API 404 error workflow"""
        from src.server import delete_epic

        mock_client = Mock()
        mock_auth.return_value = mock_client
        mock_client.api.epics.delete.side_effect = TaigaException("404 Not Found: Epic not found")

        # Test workflow: validation passes, API fails
        with pytest.raises(TaigaException, match="404"):
            delete_epic(session_id="valid-session", epic_id=999)

        # Verify API was attempted
        mock_client.api.epics.delete.assert_called_once()


class TestDeleteWorkflowSequencing:
    """Test cases for sequencing workflows with multiple resources"""

    @patch("src.server._get_authenticated_client")
    def test_delete_task_then_user_story_workflow(self, mock_auth):
        """Should handle workflow: delete task, then delete user story"""
        from src.server import delete_task, delete_user_story

        mock_client = Mock()
        mock_auth.return_value = mock_client

        # Workflow step 1: delete task
        task_result = delete_task(session_id="session-1", task_id=10)
        assert task_result["status"] == "deleted"
        assert task_result["task_id"] == 10

        # Workflow step 2: delete user story
        story_result = delete_user_story(session_id="session-1", user_story_id=20)
        assert story_result["status"] == "deleted"
        assert story_result["user_story_id"] == 20

        # Verify sequence of API calls
        assert mock_client.api.tasks.delete.call_count == 1
        assert mock_client.api.user_stories.delete.call_count == 1

    @patch("src.server._get_authenticated_client")
    def test_delete_three_issues_workflow(self, mock_auth):
        """Should handle workflow: delete three issues in sequence"""
        from src.server import delete_issue

        mock_client = Mock()
        mock_auth.return_value = mock_client

        issue_ids = [100, 101, 102]
        results = []

        for issue_id in issue_ids:
            result = delete_issue(session_id="session-1", issue_id=issue_id)
            results.append(result)

        # Verify all deletes succeeded
        assert len(results) == 3
        for i, result in enumerate(results):
            assert result["status"] == "deleted"
            assert result["issue_id"] == issue_ids[i]

        # Verify API was called three times
        assert mock_client.api.issues.delete.call_count == 3

    @patch("src.server._get_authenticated_client")
    def test_delete_workflow_fails_on_third_item(self, mock_auth):
        """Should handle workflow failure: first two succeed, third fails"""
        from src.server import delete_milestone

        mock_client = Mock()
        mock_auth.return_value = mock_client

        # Configure: first two succeed, third fails
        mock_client.api.milestones.delete.side_effect = [
            None,  # First succeeds
            None,  # Second succeeds
            TaigaException("404 Not Found"),  # Third fails
        ]

        # Workflow step 1 & 2: succeed
        result1 = delete_milestone(session_id="session-1", milestone_id=1)
        assert result1["status"] == "deleted"

        result2 = delete_milestone(session_id="session-1", milestone_id=2)
        assert result2["status"] == "deleted"

        # Workflow step 3: fails
        with pytest.raises(TaigaException, match="404"):
            delete_milestone(session_id="session-1", milestone_id=999)

        # Verify all three API calls were attempted
        assert mock_client.api.milestones.delete.call_count == 3


class TestDeleteWorkflowErrorHandling:
    """Test cases for error handling in delete workflows"""

    @patch("src.server._get_authenticated_client")
    def test_delete_workflow_with_session_expiry_mid_operation(self, mock_auth):
        """Should handle session expiry during delete operation"""
        from src.server import delete_project, delete_epic

        mock_client = Mock()

        # Session valid for first call, expires for second
        def auth_side_effect(session_id):
            if session_id == "session-1":
                return mock_client
            raise PermissionError("Session expired")

        mock_auth.side_effect = auth_side_effect

        # First call succeeds
        mock_auth.side_effect = lambda s: mock_client
        result1 = delete_project(session_id="session-1", project_id=100)
        assert result1["status"] == "deleted"

        # Second call fails with expired session
        mock_auth.side_effect = PermissionError("Session expired")
        with pytest.raises(PermissionError, match="Session expired"):
            delete_epic(session_id="session-1", epic_id=200)

    @patch("src.server._get_authenticated_client")
    def test_delete_workflow_with_permission_escalation_attempt(self, mock_auth):
        """Should reject delete with insufficient permissions throughout workflow"""
        from src.server import delete_user_story, delete_task

        mock_client = Mock()
        mock_auth.return_value = mock_client

        # All delete attempts should fail with permission error
        mock_client.api.user_stories.delete.side_effect = TaigaException("403 Forbidden")
        mock_client.api.tasks.delete.side_effect = TaigaException("403 Forbidden")

        # First delete attempt fails
        with pytest.raises(TaigaException, match="403"):
            delete_user_story(session_id="session-1", user_story_id=100)

        # Second delete attempt also fails (session still valid, but permission denied)
        with pytest.raises(TaigaException, match="403"):
            delete_task(session_id="session-1", task_id=200)

    @patch("src.server._get_authenticated_client")
    def test_delete_workflow_partial_success_on_cascade_failure(self, mock_auth):
        """Should handle workflow where cascade delete partially succeeds"""
        from src.server import delete_project

        mock_client = Mock()
        mock_auth.return_value = mock_client

        # First delete succeeds
        mock_client.api.projects.delete.return_value = None

        result1 = delete_project(session_id="session-1", project_id=100)
        assert result1["status"] == "deleted"

        # Second delete fails due to cascade
        mock_client.api.projects.delete.side_effect = TaigaException(
            "Cannot delete project: contains 5 epics"
        )

        with pytest.raises(TaigaException, match="Cannot delete project"):
            delete_project(session_id="session-1", project_id=101)


class TestDeleteWorkflowReturnTypes:
    """Test cases for return type consistency across delete workflows"""

    @patch("src.server._get_authenticated_client")
    def test_all_delete_operations_return_consistent_structure(self, mock_auth):
        """Should return consistent response structure across all delete operations"""
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

        operations = [
            (delete_project, {"session_id": "s", "project_id": 1}),
            (delete_epic, {"session_id": "s", "epic_id": 2}),
            (delete_user_story, {"session_id": "s", "user_story_id": 3}),
            (delete_task, {"session_id": "s", "task_id": 4}),
            (delete_issue, {"session_id": "s", "issue_id": 5}),
            (delete_milestone, {"session_id": "s", "milestone_id": 6}),
        ]

        for operation, kwargs in operations:
            result = operation(**kwargs)

            # All should have "status" field
            assert "status" in result
            assert result["status"] == "deleted"

            # All should have a resource ID field
            assert any(k.endswith("_id") for k in result.keys())
