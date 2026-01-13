"""
Unit tests for milestone validation in delete operations.
Tests that delete_milestone properly validates input before API calls.
"""

import pytest
from unittest.mock import Mock, patch

from src.validators import ValidationError


class TestDeleteMilestoneValidation:
    """Test cases for delete_milestone input validation"""

    @patch("src.server._get_authenticated_client")
    def test_delete_milestone_with_negative_id_rejected(self, mock_auth):
        """Should reject negative milestone ID before API call"""
        from src.server import delete_milestone

        mock_client = Mock()
        mock_auth.return_value = mock_client

        with pytest.raises(ValueError, match="milestone_id must be a positive integer"):
            delete_milestone(session_id="test-session-123", milestone_id=-1)

        # Verify API was NOT called
        mock_client.api.milestones.delete.assert_not_called()

    @patch("src.server._get_authenticated_client")
    def test_delete_milestone_with_zero_id_rejected(self, mock_auth):
        """Should reject zero milestone ID before API call"""
        from src.server import delete_milestone

        mock_client = Mock()
        mock_auth.return_value = mock_client

        with pytest.raises(ValueError, match="milestone_id must be a positive integer"):
            delete_milestone(session_id="test-session-123", milestone_id=0)

        mock_client.api.milestones.delete.assert_not_called()

    @patch("src.server._get_authenticated_client")
    def test_delete_milestone_with_valid_id_calls_api(self, mock_auth):
        """Should accept valid positive milestone ID and call API"""
        from src.server import delete_milestone

        mock_client = Mock()
        mock_auth.return_value = mock_client

        result = delete_milestone(session_id="test-session-123", milestone_id=42)

        # Verify API was called with correct ID
        mock_client.api.milestones.delete.assert_called_once_with(id=42)
        assert result["status"] == "deleted"
        assert result["milestone_id"] == 42

    @patch("src.server._get_authenticated_client")
    def test_delete_milestone_with_string_id_converted(self, mock_auth):
        """Should convert string IDs to integers if valid"""
        from src.server import delete_milestone

        mock_client = Mock()
        mock_auth.return_value = mock_client

        result = delete_milestone(session_id="test-session-123", milestone_id="42")

        mock_client.api.milestones.delete.assert_called_once_with(id=42)
        assert result["milestone_id"] == 42

    @patch("src.server._get_authenticated_client")
    def test_delete_milestone_with_invalid_string_rejected(self, mock_auth):
        """Should reject non-numeric string IDs"""
        from src.server import delete_milestone

        mock_client = Mock()
        mock_auth.return_value = mock_client

        with pytest.raises(ValueError, match="milestone_id must be an integer"):
            delete_milestone(session_id="test-session-123", milestone_id="abc")

        mock_client.api.milestones.delete.assert_not_called()
