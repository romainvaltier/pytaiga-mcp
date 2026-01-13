"""
Unit tests for delete project operations.
Tests that delete_project properly validates inputs, handles success paths, and manages errors.
"""

import pytest
from unittest.mock import Mock, patch
from pytaigaclient.exceptions import TaigaException


class TestDeleteProjectSuccess:
    """Test cases for successful delete_project operations"""

    @patch("src.server._get_authenticated_client")
    def test_delete_project_with_valid_id(self, mock_auth):
        """Should successfully delete project with valid ID"""
        from src.server import delete_project

        mock_client = Mock()
        mock_auth.return_value = mock_client

        result = delete_project(session_id="test-session", project_id=123)

        assert result["status"] == "deleted"
        assert result["project_id"] == 123
        mock_client.api.projects.delete.assert_called_once_with(id=123)

    @patch("src.server._get_authenticated_client")
    def test_delete_project_with_large_valid_id(self, mock_auth):
        """Should successfully delete project with large valid ID"""
        from src.server import delete_project

        mock_client = Mock()
        mock_auth.return_value = mock_client

        result = delete_project(session_id="test-session", project_id=999999)

        assert result["status"] == "deleted"
        assert result["project_id"] == 999999
        mock_client.api.projects.delete.assert_called_once_with(id=999999)

    @patch("src.server._get_authenticated_client")
    def test_delete_project_with_string_id_converted(self, mock_auth):
        """Should convert string project ID to integer if valid"""
        from src.server import delete_project

        mock_client = Mock()
        mock_auth.return_value = mock_client

        result = delete_project(session_id="test-session", project_id="456")

        assert result["status"] == "deleted"
        assert result["project_id"] == 456
        mock_client.api.projects.delete.assert_called_once_with(id=456)


class TestDeleteProjectValidation:
    """Test cases for delete_project input validation"""

    @patch("src.server._get_authenticated_client")
    def test_delete_project_with_negative_id_rejected(self, mock_auth):
        """Should reject negative project ID before API call"""
        from src.server import delete_project

        mock_client = Mock()
        mock_auth.return_value = mock_client

        with pytest.raises(ValueError, match="positive integer"):
            delete_project(session_id="test-session", project_id=-1)

        # Verify API was NOT called
        mock_client.api.projects.delete.assert_not_called()

    @patch("src.server._get_authenticated_client")
    def test_delete_project_with_zero_id_rejected(self, mock_auth):
        """Should reject zero project ID before API call"""
        from src.server import delete_project

        mock_client = Mock()
        mock_auth.return_value = mock_client

        with pytest.raises(ValueError, match="positive integer"):
            delete_project(session_id="test-session", project_id=0)

        mock_client.api.projects.delete.assert_not_called()

    @patch("src.server._get_authenticated_client")
    def test_delete_project_with_invalid_string_rejected(self, mock_auth):
        """Should reject non-numeric string project IDs"""
        from src.server import delete_project

        mock_client = Mock()
        mock_auth.return_value = mock_client

        with pytest.raises(ValueError, match="integer"):
            delete_project(session_id="test-session", project_id="abc")

        mock_client.api.projects.delete.assert_not_called()


class TestDeleteProjectErrors:
    """Test cases for delete_project error handling"""

    @patch("src.server._get_authenticated_client")
    def test_delete_project_not_found(self, mock_auth):
        """Should handle 404 error when project doesn't exist"""
        from src.server import delete_project

        mock_client = Mock()
        mock_auth.return_value = mock_client
        mock_client.api.projects.delete.side_effect = TaigaException("404 Not Found")

        with pytest.raises(TaigaException, match="404 Not Found"):
            delete_project(session_id="test-session", project_id=999)

    @patch("src.server._get_authenticated_client")
    def test_delete_project_permission_denied(self, mock_auth):
        """Should handle 403 error when user lacks permission"""
        from src.server import delete_project

        mock_client = Mock()
        mock_auth.return_value = mock_client
        mock_client.api.projects.delete.side_effect = TaigaException("403 Forbidden")

        with pytest.raises(TaigaException, match="403 Forbidden"):
            delete_project(session_id="test-session", project_id=123)

    @patch("src.server._get_authenticated_client")
    def test_delete_project_has_dependencies(self, mock_auth):
        """Should handle error when project has dependencies"""
        from src.server import delete_project

        mock_client = Mock()
        mock_auth.return_value = mock_client
        mock_client.api.projects.delete.side_effect = TaigaException(
            "Cannot delete project with active epics"
        )

        with pytest.raises(TaigaException, match="Cannot delete project"):
            delete_project(session_id="test-session", project_id=123)

    @patch("src.server._get_authenticated_client")
    def test_delete_project_invalid_session(self, mock_auth):
        """Should reject invalid session ID"""
        from src.server import delete_project

        mock_auth.side_effect = PermissionError("Invalid session")

        with pytest.raises(PermissionError, match="Invalid session"):
            delete_project(session_id="invalid-session", project_id=123)
