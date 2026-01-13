"""
Unit tests for delete milestone operations.
Tests that delete_milestone properly validates inputs, handles success paths, and manages errors.
Includes validation from Phase 3 (US-2.6) implementation.
Note: In Taiga, milestones are often referred to as sprints in project management contexts.
"""

import pytest
from unittest.mock import Mock, patch
from pytaigaclient.exceptions import TaigaException


class TestDeleteMilestoneSuccess:
    """Test cases for successful delete_milestone operations"""

    @patch("src.server._get_authenticated_client")
    def test_delete_milestone_with_valid_id(self, mock_auth):
        """Should successfully delete milestone with valid ID"""
        from src.server import delete_milestone

        mock_client = Mock()
        mock_auth.return_value = mock_client

        result = delete_milestone(session_id="test-session", milestone_id=350)

        assert result["status"] == "deleted"
        assert result["milestone_id"] == 350
        mock_client.api.milestones.delete.assert_called_once_with(id=350)

    @patch("src.server._get_authenticated_client")
    def test_delete_milestone_with_large_valid_id(self, mock_auth):
        """Should successfully delete milestone with large valid ID"""
        from src.server import delete_milestone

        mock_client = Mock()
        mock_auth.return_value = mock_client

        result = delete_milestone(session_id="test-session", milestone_id=333333)

        assert result["status"] == "deleted"
        assert result["milestone_id"] == 333333
        mock_client.api.milestones.delete.assert_called_once_with(id=333333)

    @patch("src.server._get_authenticated_client")
    def test_delete_milestone_with_string_id_converted(self, mock_auth):
        """Should convert string milestone ID to integer if valid"""
        from src.server import delete_milestone

        mock_client = Mock()
        mock_auth.return_value = mock_client

        result = delete_milestone(session_id="test-session", milestone_id="789")

        assert result["status"] == "deleted"
        assert result["milestone_id"] == 789
        mock_client.api.milestones.delete.assert_called_once_with(id=789)


class TestDeleteMilestoneValidation:
    """Test cases for delete_milestone input validation (Phase 3 - US-2.6)"""

    @patch("src.server._get_authenticated_client")
    def test_delete_milestone_with_negative_id_rejected(self, mock_auth):
        """Should reject negative milestone ID before API call (Phase 3 validation)"""
        from src.server import delete_milestone

        mock_client = Mock()
        mock_auth.return_value = mock_client

        with pytest.raises(ValueError, match="positive integer"):
            delete_milestone(session_id="test-session", milestone_id=-25)

        # Verify API was NOT called - validation happens first
        mock_client.api.milestones.delete.assert_not_called()

    @patch("src.server._get_authenticated_client")
    def test_delete_milestone_with_zero_id_rejected(self, mock_auth):
        """Should reject zero milestone ID before API call (Phase 3 validation)"""
        from src.server import delete_milestone

        mock_client = Mock()
        mock_auth.return_value = mock_client

        with pytest.raises(ValueError, match="positive integer"):
            delete_milestone(session_id="test-session", milestone_id=0)

        mock_client.api.milestones.delete.assert_not_called()

    @patch("src.server._get_authenticated_client")
    def test_delete_milestone_with_invalid_string_rejected(self, mock_auth):
        """Should reject non-numeric string milestone IDs"""
        from src.server import delete_milestone

        mock_client = Mock()
        mock_auth.return_value = mock_client

        with pytest.raises(ValueError, match="integer"):
            delete_milestone(session_id="test-session", milestone_id="wrongid")

        mock_client.api.milestones.delete.assert_not_called()


class TestDeleteMilestoneErrors:
    """Test cases for delete_milestone error handling"""

    @patch("src.server._get_authenticated_client")
    def test_delete_milestone_not_found(self, mock_auth):
        """Should handle 404 error when milestone doesn't exist"""
        from src.server import delete_milestone

        mock_client = Mock()
        mock_auth.return_value = mock_client
        mock_client.api.milestones.delete.side_effect = TaigaException("404 Not Found")

        with pytest.raises(TaigaException, match="404 Not Found"):
            delete_milestone(session_id="test-session", milestone_id=999)

    @patch("src.server._get_authenticated_client")
    def test_delete_milestone_permission_denied(self, mock_auth):
        """Should handle 403 error when user lacks permission"""
        from src.server import delete_milestone

        mock_client = Mock()
        mock_auth.return_value = mock_client
        mock_client.api.milestones.delete.side_effect = TaigaException("403 Forbidden")

        with pytest.raises(TaigaException, match="403 Forbidden"):
            delete_milestone(session_id="test-session", milestone_id=350)

    @patch("src.server._get_authenticated_client")
    def test_delete_milestone_version_conflict(self, mock_auth):
        """Should handle 409 conflict error for version mismatches"""
        from src.server import delete_milestone

        mock_client = Mock()
        mock_auth.return_value = mock_client
        mock_client.api.milestones.delete.side_effect = TaigaException(
            "409 Conflict: Milestone was modified by another user"
        )

        with pytest.raises(TaigaException, match="409 Conflict"):
            delete_milestone(session_id="test-session", milestone_id=350)

    @patch("src.server._get_authenticated_client")
    def test_delete_milestone_has_related_items(self, mock_auth):
        """Should handle error when milestone has related items"""
        from src.server import delete_milestone

        mock_client = Mock()
        mock_auth.return_value = mock_client
        mock_client.api.milestones.delete.side_effect = TaigaException(
            "Cannot delete milestone with active user stories"
        )

        with pytest.raises(TaigaException, match="Cannot delete milestone"):
            delete_milestone(session_id="test-session", milestone_id=350)

    @patch("src.server._get_authenticated_client")
    def test_delete_milestone_invalid_session(self, mock_auth):
        """Should reject invalid session ID"""
        from src.server import delete_milestone

        mock_auth.side_effect = PermissionError("Invalid session")

        with pytest.raises(PermissionError, match="Invalid session"):
            delete_milestone(session_id="invalid-session", milestone_id=350)
