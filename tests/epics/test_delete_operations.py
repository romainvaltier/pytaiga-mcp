"""
Unit tests for delete epic operations.
Tests that delete_epic properly validates inputs, handles success paths, and manages errors.
"""

import pytest
from unittest.mock import Mock, patch
from pytaigaclient.exceptions import TaigaException


class TestDeleteEpicSuccess:
    """Test cases for successful delete_epic operations"""

    @patch("src.server._get_authenticated_client")
    def test_delete_epic_with_valid_id(self, mock_auth):
        """Should successfully delete epic with valid ID"""
        from src.server import delete_epic

        mock_client = Mock()
        mock_auth.return_value = mock_client

        result = delete_epic(session_id="test-session", epic_id=456)

        assert result["status"] == "deleted"
        assert result["epic_id"] == 456
        mock_client.api.epics.delete.assert_called_once_with(id=456)

    @patch("src.server._get_authenticated_client")
    def test_delete_epic_with_large_valid_id(self, mock_auth):
        """Should successfully delete epic with large valid ID"""
        from src.server import delete_epic

        mock_client = Mock()
        mock_auth.return_value = mock_client

        result = delete_epic(session_id="test-session", epic_id=888888)

        assert result["status"] == "deleted"
        assert result["epic_id"] == 888888
        mock_client.api.epics.delete.assert_called_once_with(id=888888)

    @patch("src.server._get_authenticated_client")
    def test_delete_epic_with_string_id_converted(self, mock_auth):
        """Should convert string epic ID to integer if valid"""
        from src.server import delete_epic

        mock_client = Mock()
        mock_auth.return_value = mock_client

        result = delete_epic(session_id="test-session", epic_id="789")

        assert result["status"] == "deleted"
        assert result["epic_id"] == 789
        mock_client.api.epics.delete.assert_called_once_with(id=789)


class TestDeleteEpicValidation:
    """Test cases for delete_epic input validation"""

    @patch("src.server._get_authenticated_client")
    def test_delete_epic_with_negative_id_rejected(self, mock_auth):
        """Should reject negative epic ID before API call"""
        from src.server import delete_epic

        mock_client = Mock()
        mock_auth.return_value = mock_client

        with pytest.raises(ValueError, match="positive integer"):
            delete_epic(session_id="test-session", epic_id=-5)

        # Verify API was NOT called
        mock_client.api.epics.delete.assert_not_called()

    @patch("src.server._get_authenticated_client")
    def test_delete_epic_with_zero_id_rejected(self, mock_auth):
        """Should reject zero epic ID before API call"""
        from src.server import delete_epic

        mock_client = Mock()
        mock_auth.return_value = mock_client

        with pytest.raises(ValueError, match="positive integer"):
            delete_epic(session_id="test-session", epic_id=0)

        mock_client.api.epics.delete.assert_not_called()

    @patch("src.server._get_authenticated_client")
    def test_delete_epic_with_invalid_string_rejected(self, mock_auth):
        """Should reject non-numeric string epic IDs"""
        from src.server import delete_epic

        mock_client = Mock()
        mock_auth.return_value = mock_client

        with pytest.raises(ValueError, match="integer"):
            delete_epic(session_id="test-session", epic_id="xyz")

        mock_client.api.epics.delete.assert_not_called()


class TestDeleteEpicErrors:
    """Test cases for delete_epic error handling"""

    @patch("src.server._get_authenticated_client")
    def test_delete_epic_not_found(self, mock_auth):
        """Should handle 404 error when epic doesn't exist"""
        from src.server import delete_epic

        mock_client = Mock()
        mock_auth.return_value = mock_client
        mock_client.api.epics.delete.side_effect = TaigaException("404 Not Found")

        with pytest.raises(TaigaException, match="404 Not Found"):
            delete_epic(session_id="test-session", epic_id=999)

    @patch("src.server._get_authenticated_client")
    def test_delete_epic_permission_denied(self, mock_auth):
        """Should handle 403 error when user lacks permission"""
        from src.server import delete_epic

        mock_client = Mock()
        mock_auth.return_value = mock_client
        mock_client.api.epics.delete.side_effect = TaigaException("403 Forbidden")

        with pytest.raises(TaigaException, match="403 Forbidden"):
            delete_epic(session_id="test-session", epic_id=456)

    @patch("src.server._get_authenticated_client")
    def test_delete_epic_has_related_stories(self, mock_auth):
        """Should handle error when epic has related user stories"""
        from src.server import delete_epic

        mock_client = Mock()
        mock_auth.return_value = mock_client
        mock_client.api.epics.delete.side_effect = TaigaException(
            "Cannot delete epic with related user stories"
        )

        with pytest.raises(TaigaException, match="Cannot delete epic"):
            delete_epic(session_id="test-session", epic_id=456)

    @patch("src.server._get_authenticated_client")
    def test_delete_epic_invalid_session(self, mock_auth):
        """Should reject invalid session ID"""
        from src.server import delete_epic

        mock_auth.side_effect = PermissionError("Invalid session")

        with pytest.raises(PermissionError, match="Invalid session"):
            delete_epic(session_id="invalid-session", epic_id=456)
