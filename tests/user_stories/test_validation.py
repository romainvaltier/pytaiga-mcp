"""
Unit tests for user story validation in delete operations.
Tests that delete_user_story properly validates input before API calls.
"""

import pytest
from unittest.mock import Mock, patch

from src.validators import ValidationError


class TestDeleteUserStoryValidation:
    """Test cases for delete_user_story input validation"""

    @patch("src.server._get_authenticated_client")
    def test_delete_user_story_with_negative_id_rejected(self, mock_auth):
        """Should reject negative user story ID before API call"""
        # Import here to avoid circular imports
        from src.server import delete_user_story

        mock_client = Mock()
        mock_auth.return_value = mock_client

        # Should raise ValueError due to validation failure
        with pytest.raises(ValueError, match="user_story_id must be a positive integer"):
            delete_user_story(session_id="test-session-123", user_story_id=-1)

        # Verify API was NOT called
        mock_client.api.user_stories.delete.assert_not_called()

    @patch("src.server._get_authenticated_client")
    def test_delete_user_story_with_zero_id_rejected(self, mock_auth):
        """Should reject zero user story ID before API call"""
        from src.server import delete_user_story

        mock_client = Mock()
        mock_auth.return_value = mock_client

        with pytest.raises(ValueError, match="user_story_id must be a positive integer"):
            delete_user_story(session_id="test-session-123", user_story_id=0)

        mock_client.api.user_stories.delete.assert_not_called()

    @patch("src.server._get_authenticated_client")
    def test_delete_user_story_with_valid_id_calls_api(self, mock_auth):
        """Should accept valid positive user story ID and call API"""
        from src.server import delete_user_story

        mock_client = Mock()
        mock_auth.return_value = mock_client

        # Valid call should succeed
        result = delete_user_story(session_id="test-session-123", user_story_id=42)

        # Verify API was called with correct ID
        mock_client.api.user_stories.delete.assert_called_once_with(id=42)
        assert result["status"] == "deleted"
        assert result["user_story_id"] == 42

    @patch("src.server._get_authenticated_client")
    def test_delete_user_story_with_string_id_converted(self, mock_auth):
        """Should convert string IDs to integers if valid"""
        from src.server import delete_user_story

        mock_client = Mock()
        mock_auth.return_value = mock_client

        result = delete_user_story(session_id="test-session-123", user_story_id="42")

        mock_client.api.user_stories.delete.assert_called_once_with(id=42)
        assert result["user_story_id"] == 42

    @patch("src.server._get_authenticated_client")
    def test_delete_user_story_with_invalid_string_rejected(self, mock_auth):
        """Should reject non-numeric string IDs"""
        from src.server import delete_user_story

        mock_client = Mock()
        mock_auth.return_value = mock_client

        with pytest.raises(ValueError, match="user_story_id must be an integer"):
            delete_user_story(session_id="test-session-123", user_story_id="abc")

        mock_client.api.user_stories.delete.assert_not_called()
