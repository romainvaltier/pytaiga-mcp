"""
Unit tests for delete issue operations.
Tests that delete_issue properly validates inputs, handles success paths, and manages errors.
Includes validation from Phase 3 (US-2.6) implementation.
"""

import pytest
from unittest.mock import Mock, patch
from pytaigaclient.exceptions import TaigaException


class TestDeleteIssueSuccess:
    """Test cases for successful delete_issue operations"""

    @patch("src.server._get_authenticated_client")
    def test_delete_issue_with_valid_id(self, mock_auth):
        """Should successfully delete issue with valid ID"""
        from src.server import delete_issue

        mock_client = Mock()
        mock_auth.return_value = mock_client

        result = delete_issue(session_id="test-session", issue_id=300)

        assert result["status"] == "deleted"
        assert result["issue_id"] == 300
        mock_client.api.issues.delete.assert_called_once_with(id=300)

    @patch("src.server._get_authenticated_client")
    def test_delete_issue_with_large_valid_id(self, mock_auth):
        """Should successfully delete issue with large valid ID"""
        from src.server import delete_issue

        mock_client = Mock()
        mock_auth.return_value = mock_client

        result = delete_issue(session_id="test-session", issue_id=444444)

        assert result["status"] == "deleted"
        assert result["issue_id"] == 444444
        mock_client.api.issues.delete.assert_called_once_with(id=444444)

    @patch("src.server._get_authenticated_client")
    def test_delete_issue_with_string_id_converted(self, mock_auth):
        """Should convert string issue ID to integer if valid"""
        from src.server import delete_issue

        mock_client = Mock()
        mock_auth.return_value = mock_client

        result = delete_issue(session_id="test-session", issue_id="654")

        assert result["status"] == "deleted"
        assert result["issue_id"] == 654
        mock_client.api.issues.delete.assert_called_once_with(id=654)


class TestDeleteIssueValidation:
    """Test cases for delete_issue input validation (Phase 3 - US-2.6)"""

    @patch("src.server._get_authenticated_client")
    def test_delete_issue_with_negative_id_rejected(self, mock_auth):
        """Should reject negative issue ID before API call (Phase 3 validation)"""
        from src.server import delete_issue

        mock_client = Mock()
        mock_auth.return_value = mock_client

        with pytest.raises(ValueError, match="positive integer"):
            delete_issue(session_id="test-session", issue_id=-20)

        # Verify API was NOT called - validation happens first
        mock_client.api.issues.delete.assert_not_called()

    @patch("src.server._get_authenticated_client")
    def test_delete_issue_with_zero_id_rejected(self, mock_auth):
        """Should reject zero issue ID before API call (Phase 3 validation)"""
        from src.server import delete_issue

        mock_client = Mock()
        mock_auth.return_value = mock_client

        with pytest.raises(ValueError, match="positive integer"):
            delete_issue(session_id="test-session", issue_id=0)

        mock_client.api.issues.delete.assert_not_called()

    @patch("src.server._get_authenticated_client")
    def test_delete_issue_with_invalid_string_rejected(self, mock_auth):
        """Should reject non-numeric string issue IDs"""
        from src.server import delete_issue

        mock_client = Mock()
        mock_auth.return_value = mock_client

        with pytest.raises(ValueError, match="integer"):
            delete_issue(session_id="test-session", issue_id="notvalid")

        mock_client.api.issues.delete.assert_not_called()


class TestDeleteIssueErrors:
    """Test cases for delete_issue error handling"""

    @patch("src.server._get_authenticated_client")
    def test_delete_issue_not_found(self, mock_auth):
        """Should handle 404 error when issue doesn't exist"""
        from src.server import delete_issue

        mock_client = Mock()
        mock_auth.return_value = mock_client
        mock_client.api.issues.delete.side_effect = TaigaException("404 Not Found")

        with pytest.raises(TaigaException, match="404 Not Found"):
            delete_issue(session_id="test-session", issue_id=999)

    @patch("src.server._get_authenticated_client")
    def test_delete_issue_permission_denied(self, mock_auth):
        """Should handle 403 error when user lacks permission"""
        from src.server import delete_issue

        mock_client = Mock()
        mock_auth.return_value = mock_client
        mock_client.api.issues.delete.side_effect = TaigaException("403 Forbidden")

        with pytest.raises(TaigaException, match="403 Forbidden"):
            delete_issue(session_id="test-session", issue_id=300)

    @patch("src.server._get_authenticated_client")
    def test_delete_issue_version_conflict(self, mock_auth):
        """Should handle 409 conflict error for version mismatches"""
        from src.server import delete_issue

        mock_client = Mock()
        mock_auth.return_value = mock_client
        mock_client.api.issues.delete.side_effect = TaigaException(
            "409 Conflict: Issue was modified by another user"
        )

        with pytest.raises(TaigaException, match="409 Conflict"):
            delete_issue(session_id="test-session", issue_id=300)

    @patch("src.server._get_authenticated_client")
    def test_delete_issue_invalid_session(self, mock_auth):
        """Should reject invalid session ID"""
        from src.server import delete_issue

        mock_auth.side_effect = PermissionError("Invalid session")

        with pytest.raises(PermissionError, match="Invalid session"):
            delete_issue(session_id="invalid-session", issue_id=300)
