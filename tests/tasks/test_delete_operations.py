"""
Unit tests for delete task operations.
Tests that delete_task properly validates inputs, handles success paths, and manages errors.
"""

import pytest
from unittest.mock import Mock, patch
from pytaigaclient.exceptions import TaigaException


class TestDeleteTaskSuccess:
    """Test cases for successful delete_task operations"""

    @patch("src.server._get_authenticated_client")
    def test_delete_task_with_valid_id(self, mock_auth):
        """Should successfully delete task with valid ID"""
        from src.server import delete_task

        mock_client = Mock()
        mock_auth.return_value = mock_client

        result = delete_task(session_id="test-session", task_id=250)

        assert result["status"] == "deleted"
        assert result["task_id"] == 250
        mock_client.api.tasks.delete.assert_called_once_with(id=250)

    @patch("src.server._get_authenticated_client")
    def test_delete_task_with_large_valid_id(self, mock_auth):
        """Should successfully delete task with large valid ID"""
        from src.server import delete_task

        mock_client = Mock()
        mock_auth.return_value = mock_client

        result = delete_task(session_id="test-session", task_id=777777)

        assert result["status"] == "deleted"
        assert result["task_id"] == 777777
        mock_client.api.tasks.delete.assert_called_once_with(id=777777)

    @patch("src.server._get_authenticated_client")
    def test_delete_task_with_string_id_converted(self, mock_auth):
        """Should convert string task ID to integer if valid"""
        from src.server import delete_task

        mock_client = Mock()
        mock_auth.return_value = mock_client

        result = delete_task(session_id="test-session", task_id="567")

        assert result["status"] == "deleted"
        assert result["task_id"] == 567
        mock_client.api.tasks.delete.assert_called_once_with(id=567)


class TestDeleteTaskValidation:
    """Test cases for delete_task input validation"""

    @patch("src.server._get_authenticated_client")
    def test_delete_task_with_negative_id_rejected(self, mock_auth):
        """Should reject negative task ID before API call"""
        from src.server import delete_task

        mock_client = Mock()
        mock_auth.return_value = mock_client

        with pytest.raises(ValueError, match="positive integer"):
            delete_task(session_id="test-session", task_id=-15)

        # Verify API was NOT called
        mock_client.api.tasks.delete.assert_not_called()

    @patch("src.server._get_authenticated_client")
    def test_delete_task_with_zero_id_rejected(self, mock_auth):
        """Should reject zero task ID before API call"""
        from src.server import delete_task

        mock_client = Mock()
        mock_auth.return_value = mock_client

        with pytest.raises(ValueError, match="positive integer"):
            delete_task(session_id="test-session", task_id=0)

        mock_client.api.tasks.delete.assert_not_called()

    @patch("src.server._get_authenticated_client")
    def test_delete_task_with_invalid_string_rejected(self, mock_auth):
        """Should reject non-numeric string task IDs"""
        from src.server import delete_task

        mock_client = Mock()
        mock_auth.return_value = mock_client

        with pytest.raises(ValueError, match="integer"):
            delete_task(session_id="test-session", task_id="notanid")

        mock_client.api.tasks.delete.assert_not_called()


class TestDeleteTaskErrors:
    """Test cases for delete_task error handling"""

    @patch("src.server._get_authenticated_client")
    def test_delete_task_not_found(self, mock_auth):
        """Should handle 404 error when task doesn't exist"""
        from src.server import delete_task

        mock_client = Mock()
        mock_auth.return_value = mock_client
        mock_client.api.tasks.delete.side_effect = TaigaException("404 Not Found")

        with pytest.raises(TaigaException, match="404 Not Found"):
            delete_task(session_id="test-session", task_id=999)

    @patch("src.server._get_authenticated_client")
    def test_delete_task_permission_denied(self, mock_auth):
        """Should handle 403 error when user lacks permission"""
        from src.server import delete_task

        mock_client = Mock()
        mock_auth.return_value = mock_client
        mock_client.api.tasks.delete.side_effect = TaigaException("403 Forbidden")

        with pytest.raises(TaigaException, match="403 Forbidden"):
            delete_task(session_id="test-session", task_id=250)

    @patch("src.server._get_authenticated_client")
    def test_delete_task_version_conflict(self, mock_auth):
        """Should handle 409 conflict error for version mismatches"""
        from src.server import delete_task

        mock_client = Mock()
        mock_auth.return_value = mock_client
        mock_client.api.tasks.delete.side_effect = TaigaException(
            "409 Conflict: Task was modified by another user"
        )

        with pytest.raises(TaigaException, match="409 Conflict"):
            delete_task(session_id="test-session", task_id=250)

    @patch("src.server._get_authenticated_client")
    def test_delete_task_invalid_session(self, mock_auth):
        """Should reject invalid session ID"""
        from src.server import delete_task

        mock_auth.side_effect = PermissionError("Invalid session")

        with pytest.raises(PermissionError, match="Invalid session"):
            delete_task(session_id="invalid-session", task_id=250)
