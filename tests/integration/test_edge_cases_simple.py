"""
Edge case tests for core operations.
Tests empty lists, boundary values, and error handling.
"""

import pytest
from unittest.mock import Mock, patch
from pytaigaclient.exceptions import TaigaException


class TestEmptyListHandling:
    """Test cases for handling empty lists"""

    @patch("src.server._get_authenticated_client")
    def test_list_projects_empty(self, mock_auth):
        """Should handle empty project list"""
        from src.server import list_projects
        mock_client = Mock()
        mock_auth.return_value = mock_client
        mock_client.api.projects.list.return_value = []

        result = list_projects(session_id="test")
        assert result == []

    @patch("src.server._get_authenticated_client")
    def test_list_user_stories_empty(self, mock_auth):
        """Should handle empty user stories list"""
        from src.server import list_user_stories
        mock_client = Mock()
        mock_auth.return_value = mock_client
        mock_client.api.user_stories.list.return_value = []

        result = list_user_stories(session_id="test", project_id=1)
        assert result == []

    @patch("src.server._get_authenticated_client")
    def test_list_tasks_empty(self, mock_auth):
        """Should handle empty tasks list"""
        from src.server import list_tasks
        mock_client = Mock()
        mock_auth.return_value = mock_client
        mock_client.api.tasks.list.return_value = []

        result = list_tasks(session_id="test", project_id=1)
        assert result == []

    @patch("src.server._get_authenticated_client")
    def test_list_issues_empty(self, mock_auth):
        """Should handle empty issues list"""
        from src.server import list_issues
        mock_client = Mock()
        mock_auth.return_value = mock_client
        mock_client.api.issues.list.return_value = []

        result = list_issues(session_id="test", project_id=1)
        assert result == []


class TestBoundaryValues:
    """Test cases for ID boundary values"""

    @patch("src.server._get_authenticated_client")
    def test_delete_with_minimum_valid_id(self, mock_auth):
        """Should accept minimum valid ID (1)"""
        from src.server import delete_user_story
        mock_client = Mock()
        mock_auth.return_value = mock_client

        result = delete_user_story(session_id="test", user_story_id=1)
        assert result["status"] == "deleted"
        assert result["user_story_id"] == 1

    @patch("src.server._get_authenticated_client")
    def test_delete_with_maximum_valid_id(self, mock_auth):
        """Should accept very large valid ID"""
        from src.server import delete_issue
        mock_client = Mock()
        mock_auth.return_value = mock_client

        large_id = 2147483647  # Max 32-bit int
        result = delete_issue(session_id="test", issue_id=large_id)
        assert result["status"] == "deleted"
        assert result["issue_id"] == large_id

    @patch("src.server._get_authenticated_client")
    def test_delete_reject_zero_id(self, mock_auth):
        """Should reject zero ID"""
        from src.server import delete_milestone
        mock_client = Mock()
        mock_auth.return_value = mock_client

        with pytest.raises(ValueError):
            delete_milestone(session_id="test", milestone_id=0)

    @patch("src.server._get_authenticated_client")
    def test_delete_reject_negative_id(self, mock_auth):
        """Should reject negative ID"""
        from src.server import delete_task
        mock_client = Mock()
        mock_auth.return_value = mock_client

        with pytest.raises(ValueError):
            delete_task(session_id="test", task_id=-1)


class TestLargeListHandling:
    """Test cases for large list operations"""

    @patch("src.server._get_authenticated_client")
    def test_list_with_1000_items(self, mock_auth):
        """Should handle list with 1000 items"""
        from src.server import list_user_stories
        mock_client = Mock()
        mock_auth.return_value = mock_client
        items = [{"id": i, "title": f"Story {i}"} for i in range(1, 1001)]
        mock_client.api.user_stories.list.return_value = items

        result = list_user_stories(session_id="test", project_id=1)
        assert len(result) == 1000
        assert result[0]["id"] == 1
        assert result[999]["id"] == 1000

    @patch("src.server._get_authenticated_client")
    def test_list_with_10000_items(self, mock_auth):
        """Should handle list with 10000 items"""
        from src.server import list_tasks
        mock_client = Mock()
        mock_auth.return_value = mock_client
        items = [{"id": i, "title": f"Task {i}"} for i in range(1, 10001)]
        mock_client.api.tasks.list.return_value = items

        result = list_tasks(session_id="test", project_id=1)
        assert len(result) == 10000


class TestErrorHandling:
    """Test cases for error handling"""

    @patch("src.server._get_authenticated_client")
    def test_propagate_server_error(self, mock_auth):
        """Should propagate server errors"""
        from src.server import list_projects
        mock_client = Mock()
        mock_auth.return_value = mock_client
        mock_client.api.projects.list.side_effect = TaigaException("500 Internal Server Error")

        with pytest.raises(TaigaException, match="500"):
            list_projects(session_id="test")

    @patch("src.server._get_authenticated_client")
    def test_propagate_404_error(self, mock_auth):
        """Should propagate 404 errors"""
        from src.server import list_issues
        mock_client = Mock()
        mock_auth.return_value = mock_client
        mock_client.api.issues.list.side_effect = TaigaException("404 Not Found")

        with pytest.raises(TaigaException, match="404"):
            list_issues(session_id="test", project_id=999)

    @patch("src.server._get_authenticated_client")
    def test_propagate_timeout_error(self, mock_auth):
        """Should propagate timeout errors"""
        from src.server import list_issues
        mock_client = Mock()
        mock_auth.return_value = mock_client
        mock_client.api.issues.list.side_effect = TaigaException("Connection timeout")

        with pytest.raises(TaigaException, match="timeout"):
            list_issues(session_id="test", project_id=1)


class TestSessionExpiry:
    """Test cases for session management"""

    @patch("src.server._get_authenticated_client")
    def test_reject_invalid_session(self, mock_auth):
        """Should reject invalid session ID"""
        from src.server import get_project
        mock_auth.side_effect = PermissionError("Invalid session")

        with pytest.raises(PermissionError, match="Invalid"):
            get_project(session_id="invalid", project_id=1)

    @patch("src.server._get_authenticated_client")
    def test_reject_expired_session(self, mock_auth):
        """Should reject expired session"""
        from src.server import delete_user_story
        mock_auth.side_effect = PermissionError("Session expired")

        with pytest.raises(PermissionError, match="expired"):
            delete_user_story(session_id="expired", user_story_id=1)

    @patch("src.server._get_authenticated_client")
    def test_multiple_sessions_independent(self, mock_auth):
        """Should handle multiple independent sessions"""
        from src.server import list_issues

        call_count = [0]
        def auth_effect(session_id):
            call_count[0] += 1
            client = Mock()
            client.api.issues.list.return_value = [{"id": 1}]
            return client

        mock_auth.side_effect = auth_effect

        result1 = list_issues(session_id="session1", project_id=1)
        result2 = list_issues(session_id="session2", project_id=1)

        assert len(result1) == 1
        assert len(result2) == 1
        assert call_count[0] == 2  # Both sessions authenticated


class TestBulkSequentialOperations:
    """Test cases for sequential bulk operations"""

    @patch("src.server._get_authenticated_client")
    def test_sequential_deletes(self, mock_auth):
        """Should handle sequential delete operations"""
        from src.server import delete_milestone
        mock_client = Mock()
        mock_auth.return_value = mock_client

        for i in range(1, 101):
            result = delete_milestone(session_id="test", milestone_id=i)
            assert result["status"] == "deleted"

        assert mock_client.api.milestones.delete.call_count == 100

    @patch("src.server._get_authenticated_client")
    def test_sequential_gets(self, mock_auth):
        """Should handle sequential delete operations"""
        from src.server import delete_task
        mock_client = Mock()
        mock_auth.return_value = mock_client

        for i in range(1, 51):
            result = delete_task(session_id="test", task_id=i)
            assert result["status"] == "deleted"

        assert mock_client.api.tasks.delete.call_count == 50


class TestListSingleItem:
    """Test cases for lists with single items"""

    @patch("src.server._get_authenticated_client")
    def test_list_single_project(self, mock_auth):
        """Should handle list with single project"""
        from src.server import list_projects
        mock_client = Mock()
        mock_auth.return_value = mock_client
        mock_client.api.projects.list.return_value = [{"id": 1, "name": "Project"}]

        result = list_projects(session_id="test")
        assert len(result) == 1
        assert result[0]["id"] == 1
