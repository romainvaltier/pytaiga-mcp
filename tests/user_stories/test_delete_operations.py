"""
Unit tests for delete user story operations.
Tests that delete_user_story properly validates inputs, handles success paths, and manages errors.
Includes validation from Phase 3 (US-2.6) implementation.
"""

import pytest
from unittest.mock import Mock, patch
from pytaigaclient.exceptions import TaigaException


class TestDeleteUserStorySuccess:
    """Test cases for successful delete_user_story operations"""

    @patch("src.server._get_authenticated_client")
    def test_delete_user_story_with_valid_id(self, mock_auth):
        """Should successfully delete user story with valid ID"""
        from src.server import delete_user_story

        mock_client = Mock()
        mock_auth.return_value = mock_client

        result = delete_user_story(session_id="test-session", user_story_id=200)

        assert result["status"] == "deleted"
        assert result["user_story_id"] == 200
        mock_client.api.user_stories.delete.assert_called_once_with(id=200)

    @patch("src.server._get_authenticated_client")
    def test_delete_user_story_with_large_valid_id(self, mock_auth):
        """Should successfully delete user story with large valid ID"""
        from src.server import delete_user_story

        mock_client = Mock()
        mock_auth.return_value = mock_client

        result = delete_user_story(session_id="test-session", user_story_id=555555)

        assert result["status"] == "deleted"
        assert result["user_story_id"] == 555555
        mock_client.api.user_stories.delete.assert_called_once_with(id=555555)

    @patch("src.server._get_authenticated_client")
    def test_delete_user_story_with_string_id_converted(self, mock_auth):
        """Should convert string user story ID to integer if valid"""
        from src.server import delete_user_story

        mock_client = Mock()
        mock_auth.return_value = mock_client

        result = delete_user_story(session_id="test-session", user_story_id="321")

        assert result["status"] == "deleted"
        assert result["user_story_id"] == 321
        mock_client.api.user_stories.delete.assert_called_once_with(id=321)


class TestDeleteUserStoryValidation:
    """Test cases for delete_user_story input validation (Phase 3 - US-2.6)"""

    @patch("src.server._get_authenticated_client")
    def test_delete_user_story_with_negative_id_rejected(self, mock_auth):
        """Should reject negative user story ID before API call (Phase 3 validation)"""
        from src.server import delete_user_story

        mock_client = Mock()
        mock_auth.return_value = mock_client

        with pytest.raises(ValueError, match="positive integer"):
            delete_user_story(session_id="test-session", user_story_id=-10)

        # Verify API was NOT called - validation happens first
        mock_client.api.user_stories.delete.assert_not_called()

    @patch("src.server._get_authenticated_client")
    def test_delete_user_story_with_zero_id_rejected(self, mock_auth):
        """Should reject zero user story ID before API call (Phase 3 validation)"""
        from src.server import delete_user_story

        mock_client = Mock()
        mock_auth.return_value = mock_client

        with pytest.raises(ValueError, match="positive integer"):
            delete_user_story(session_id="test-session", user_story_id=0)

        mock_client.api.user_stories.delete.assert_not_called()

    @patch("src.server._get_authenticated_client")
    def test_delete_user_story_with_invalid_string_rejected(self, mock_auth):
        """Should reject non-numeric string user story IDs"""
        from src.server import delete_user_story

        mock_client = Mock()
        mock_auth.return_value = mock_client

        with pytest.raises(ValueError, match="integer"):
            delete_user_story(session_id="test-session", user_story_id="invalid")

        mock_client.api.user_stories.delete.assert_not_called()


class TestDeleteUserStoryErrors:
    """Test cases for delete_user_story error handling"""

    @patch("src.server._get_authenticated_client")
    def test_delete_user_story_not_found(self, mock_auth):
        """Should handle 404 error when user story doesn't exist"""
        from src.server import delete_user_story

        mock_client = Mock()
        mock_auth.return_value = mock_client
        mock_client.api.user_stories.delete.side_effect = TaigaException("404 Not Found")

        with pytest.raises(TaigaException, match="404 Not Found"):
            delete_user_story(session_id="test-session", user_story_id=999)

    @patch("src.server._get_authenticated_client")
    def test_delete_user_story_permission_denied(self, mock_auth):
        """Should handle 403 error when user lacks permission"""
        from src.server import delete_user_story

        mock_client = Mock()
        mock_auth.return_value = mock_client
        mock_client.api.user_stories.delete.side_effect = TaigaException("403 Forbidden")

        with pytest.raises(TaigaException, match="403 Forbidden"):
            delete_user_story(session_id="test-session", user_story_id=200)

    @patch("src.server._get_authenticated_client")
    def test_delete_user_story_version_conflict(self, mock_auth):
        """Should handle 409 conflict error for version mismatches"""
        from src.server import delete_user_story

        mock_client = Mock()
        mock_auth.return_value = mock_client
        mock_client.api.user_stories.delete.side_effect = TaigaException(
            "409 Conflict: User story was modified by another user"
        )

        with pytest.raises(TaigaException, match="409 Conflict"):
            delete_user_story(session_id="test-session", user_story_id=200)

    @patch("src.server._get_authenticated_client")
    def test_delete_user_story_invalid_session(self, mock_auth):
        """Should reject invalid session ID"""
        from src.server import delete_user_story

        mock_auth.side_effect = PermissionError("Invalid session")

        with pytest.raises(PermissionError, match="Invalid session"):
            delete_user_story(session_id="invalid-session", user_story_id=200)
