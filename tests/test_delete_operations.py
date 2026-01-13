"""
Unit tests for delete operations validation.
Tests that all delete operations properly validate inputs and handle success/error paths.
"""

import pytest
from unittest.mock import Mock, patch


class TestValidDeleteOperations:
    """Test cases for valid delete operations across all resource types"""

    @patch("src.server._get_authenticated_client")
    def test_delete_user_story_valid(self, mock_auth):
        """Should successfully delete user story with valid ID"""
        from src.server import delete_user_story

        mock_client = Mock()
        mock_auth.return_value = mock_client

        result = delete_user_story(session_id="test-session", user_story_id=123)

        assert result["status"] == "deleted"
        assert result["user_story_id"] == 123
        mock_client.api.user_stories.delete.assert_called_once_with(id=123)

    @patch("src.server._get_authenticated_client")
    def test_delete_issue_valid(self, mock_auth):
        """Should successfully delete issue with valid ID"""
        from src.server import delete_issue

        mock_client = Mock()
        mock_auth.return_value = mock_client

        result = delete_issue(session_id="test-session", issue_id=456)

        assert result["status"] == "deleted"
        assert result["issue_id"] == 456
        mock_client.api.issues.delete.assert_called_once_with(id=456)

    @patch("src.server._get_authenticated_client")
    def test_delete_milestone_valid(self, mock_auth):
        """Should successfully delete milestone with valid ID"""
        from src.server import delete_milestone

        mock_client = Mock()
        mock_auth.return_value = mock_client

        result = delete_milestone(session_id="test-session", milestone_id=789)

        assert result["status"] == "deleted"
        assert result["milestone_id"] == 789
        mock_client.api.milestones.delete.assert_called_once_with(id=789)

    @patch("src.server._get_authenticated_client")
    def test_delete_user_story_validation_error_message(self, mock_auth):
        """Should provide clear validation error message for invalid user story ID"""
        from src.server import delete_user_story

        mock_client = Mock()
        mock_auth.return_value = mock_client

        with pytest.raises(ValueError) as exc_info:
            delete_user_story(session_id="test-session", user_story_id=-5)

        assert "positive integer" in str(exc_info.value)

    @patch("src.server._get_authenticated_client")
    def test_delete_issue_validation_error_message(self, mock_auth):
        """Should provide clear validation error message for invalid issue ID"""
        from src.server import delete_issue

        mock_client = Mock()
        mock_auth.return_value = mock_client

        with pytest.raises(ValueError) as exc_info:
            delete_issue(session_id="test-session", issue_id=-5)

        assert "positive integer" in str(exc_info.value)

    @patch("src.server._get_authenticated_client")
    def test_delete_milestone_validation_error_message(self, mock_auth):
        """Should provide clear validation error message for invalid milestone ID"""
        from src.server import delete_milestone

        mock_client = Mock()
        mock_auth.return_value = mock_client

        with pytest.raises(ValueError) as exc_info:
            delete_milestone(session_id="test-session", milestone_id=-5)

        assert "positive integer" in str(exc_info.value)
