"""
Integration tests for delete operation validation.
Tests that delete operations work correctly with validation across CRUD workflows.
"""

import pytest
from unittest.mock import Mock, patch


class TestDeleteOperationValidationIntegration:
    """Integration tests for delete operations with validation"""

    @patch("src.server._get_authenticated_client")
    def test_delete_user_story_validation_integration(self, mock_auth):
        """
        Integration test: delete_user_story validation in context of CRUD workflow
        Tests that validation happens before API call in complete workflow
        """
        from src.server import delete_user_story

        mock_client = Mock()
        mock_auth.return_value = mock_client

        # Test 1: Invalid input is rejected before API
        with pytest.raises(ValueError, match="positive integer"):
            delete_user_story(session_id="test-session", user_story_id=-1)

        # Verify API was not called
        mock_client.api.user_stories.delete.assert_not_called()

        # Test 2: Valid input succeeds and calls API
        result = delete_user_story(session_id="test-session", user_story_id=100)
        assert result["status"] == "deleted"
        assert result["user_story_id"] == 100
        mock_client.api.user_stories.delete.assert_called_once()

    @patch("src.server._get_authenticated_client")
    def test_delete_issue_validation_integration(self, mock_auth):
        """
        Integration test: delete_issue validation in context of CRUD workflow
        Tests that validation happens before API call in complete workflow
        """
        from src.server import delete_issue

        mock_client = Mock()
        mock_auth.return_value = mock_client

        # Test 1: Invalid input is rejected before API
        with pytest.raises(ValueError, match="positive integer"):
            delete_issue(session_id="test-session", issue_id=0)

        # Verify API was not called
        mock_client.api.issues.delete.assert_not_called()

        # Test 2: Valid input succeeds and calls API
        result = delete_issue(session_id="test-session", issue_id=200)
        assert result["status"] == "deleted"
        assert result["issue_id"] == 200
        mock_client.api.issues.delete.assert_called_once()

    @patch("src.server._get_authenticated_client")
    def test_delete_milestone_validation_integration(self, mock_auth):
        """
        Integration test: delete_milestone validation in context of CRUD workflow
        Tests that validation happens before API call in complete workflow
        """
        from src.server import delete_milestone

        mock_client = Mock()
        mock_auth.return_value = mock_client

        # Test 1: Invalid input is rejected before API
        with pytest.raises(ValueError, match="positive integer"):
            delete_milestone(session_id="test-session", milestone_id=-10)

        # Verify API was not called
        mock_client.api.milestones.delete.assert_not_called()

        # Test 2: Valid input succeeds and calls API
        result = delete_milestone(session_id="test-session", milestone_id=300)
        assert result["status"] == "deleted"
        assert result["milestone_id"] == 300
        mock_client.api.milestones.delete.assert_called_once()

    @patch("src.server._get_authenticated_client")
    def test_all_delete_operations_have_consistent_validation(self, mock_auth):
        """
        Integration test: all three delete operations have consistent validation
        Ensures error messages and behavior are consistent across operations
        """
        from src.server import delete_user_story, delete_issue, delete_milestone

        mock_client = Mock()
        mock_auth.return_value = mock_client

        # All three should reject negative IDs with similar error messages
        operations = [
            (delete_user_story, {"session_id": "test-session", "user_story_id": -1}),
            (delete_issue, {"session_id": "test-session", "issue_id": -1}),
            (delete_milestone, {"session_id": "test-session", "milestone_id": -1}),
        ]

        for operation, kwargs in operations:
            with pytest.raises(ValueError, match="positive integer"):
                operation(**kwargs)

    @patch("src.server._get_authenticated_client")
    def test_delete_operations_with_string_ids_converted(self, mock_auth):
        """
        Integration test: delete operations properly convert string IDs to integers
        Ensures consistent handling of string input across operations
        """
        from src.server import delete_user_story, delete_issue, delete_milestone

        mock_client = Mock()
        mock_auth.return_value = mock_client

        # All three operations should accept and convert string IDs
        result1 = delete_user_story(session_id="test-session", user_story_id="42")
        assert result1["user_story_id"] == 42

        result2 = delete_issue(session_id="test-session", issue_id="43")
        assert result2["issue_id"] == 43

        result3 = delete_milestone(session_id="test-session", milestone_id="44")
        assert result3["milestone_id"] == 44
