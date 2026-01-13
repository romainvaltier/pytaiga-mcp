"""
Integration tests for delete operation conflict handling.
Tests cascade deletion, version conflicts, and dependency management.
"""

import pytest
from unittest.mock import Mock, patch
from pytaigaclient.exceptions import TaigaException


class TestDeleteCascadeHandling:
    """Test cases for cascade deletion handling"""

    @patch("src.server._get_authenticated_client")
    def test_delete_project_with_cascading_deletions(self, mock_auth):
        """Should handle successful cascade deletion of project and children"""
        from src.server import delete_project

        mock_client = Mock()
        mock_auth.return_value = mock_client

        # Project deletion should succeed even if it has child resources
        result = delete_project(session_id="test-session", project_id=100)

        assert result["status"] == "deleted"
        assert result["project_id"] == 100
        # API call should happen (Taiga backend handles cascade)
        mock_client.api.projects.delete.assert_called_once()

    @patch("src.server._get_authenticated_client")
    def test_delete_project_cascade_blocked_by_dependencies(self, mock_auth):
        """Should handle cascade blocking when project has dependencies"""
        from src.server import delete_project

        mock_client = Mock()
        mock_auth.return_value = mock_client
        mock_client.api.projects.delete.side_effect = TaigaException(
            "Cannot delete project: contains active epics that must be deleted first"
        )

        with pytest.raises(TaigaException, match="Cannot delete"):
            delete_project(session_id="test-session", project_id=100)

    @patch("src.server._get_authenticated_client")
    def test_delete_epic_cascade_blocked(self, mock_auth):
        """Should handle cascade blocking when epic has dependent stories"""
        from src.server import delete_epic

        mock_client = Mock()
        mock_auth.return_value = mock_client
        mock_client.api.epics.delete.side_effect = TaigaException(
            "Cannot delete epic: contains user stories that must be deleted first"
        )

        with pytest.raises(TaigaException, match="Cannot delete"):
            delete_epic(session_id="test-session", epic_id=50)


class TestDeleteVersionConflictHandling:
    """Test cases for version conflict resolution in delete operations"""

    @patch("src.server._get_authenticated_client")
    def test_delete_user_story_version_conflict_after_modification(self, mock_auth):
        """Should handle 409 conflict when user story was modified since retrieval"""
        from src.server import delete_user_story

        mock_client = Mock()
        mock_auth.return_value = mock_client
        mock_client.api.user_stories.delete.side_effect = TaigaException(
            "409 Conflict: version mismatch - user story was modified by user 'john' at 2024-01-12T15:30:00Z"
        )

        with pytest.raises(TaigaException, match="409.*version mismatch"):
            delete_user_story(session_id="test-session", user_story_id=200)

    @patch("src.server._get_authenticated_client")
    def test_delete_task_version_conflict_recoverable(self, mock_auth):
        """Should return clear error when version conflict occurs"""
        from src.server import delete_task

        mock_client = Mock()
        mock_auth.return_value = mock_client
        mock_client.api.tasks.delete.side_effect = TaigaException(
            "409 Conflict: Your changes conflict with concurrent modifications"
        )

        with pytest.raises(TaigaException, match="409.*conflict"):
            delete_task(session_id="test-session", task_id=250)

    @patch("src.server._get_authenticated_client")
    def test_delete_issue_version_conflict_multiple_attempts(self, mock_auth):
        """Should handle version conflict when delete is retried"""
        from src.server import delete_issue

        mock_client = Mock()
        mock_auth.return_value = mock_client
        # First call fails with version conflict
        mock_client.api.issues.delete.side_effect = [
            TaigaException("409 Conflict: version mismatch"),
            None,  # Second attempt would succeed
        ]

        # First attempt should fail
        with pytest.raises(TaigaException, match="409"):
            delete_issue(session_id="test-session", issue_id=300)

        # Verify API was called once (no automatic retry)
        assert mock_client.api.issues.delete.call_count == 1

    @patch("src.server._get_authenticated_client")
    def test_delete_milestone_version_conflict_with_timestamp(self, mock_auth):
        """Should include timestamp info in version conflict error"""
        from src.server import delete_milestone

        mock_client = Mock()
        mock_auth.return_value = mock_client
        conflict_error = TaigaException(
            "409 Conflict: Milestone version changed at 2024-01-12 15:45:30 UTC"
        )
        mock_client.api.milestones.delete.side_effect = conflict_error

        with pytest.raises(TaigaException) as exc_info:
            delete_milestone(session_id="test-session", milestone_id=350)

        assert "409" in str(exc_info.value) or "Conflict" in str(exc_info.value)


class TestDeleteResourceConflicts:
    """Test cases for handling conflicts during resource deletion"""

    @patch("src.server._get_authenticated_client")
    def test_delete_user_story_in_active_sprint_conflict(self, mock_auth):
        """Should handle conflict when deleting user story in active sprint"""
        from src.server import delete_user_story

        mock_client = Mock()
        mock_auth.return_value = mock_client
        mock_client.api.user_stories.delete.side_effect = TaigaException(
            "Cannot delete user story: assigned to active sprint (Sprint #5)"
        )

        with pytest.raises(TaigaException, match="Cannot delete.*active sprint"):
            delete_user_story(session_id="test-session", user_story_id=200)

    @patch("src.server._get_authenticated_client")
    def test_delete_task_linked_to_multiple_stories(self, mock_auth):
        """Should handle conflict when deleting task linked to stories"""
        from src.server import delete_task

        mock_client = Mock()
        mock_auth.return_value = mock_client
        mock_client.api.tasks.delete.side_effect = TaigaException(
            "Cannot delete task: linked to 3 user stories"
        )

        with pytest.raises(TaigaException, match="Cannot delete.*linked"):
            delete_task(session_id="test-session", task_id=250)

    @patch("src.server._get_authenticated_client")
    def test_delete_milestone_with_assigned_items(self, mock_auth):
        """Should handle conflict when milestone has assigned items"""
        from src.server import delete_milestone

        mock_client = Mock()
        mock_auth.return_value = mock_client
        mock_client.api.milestones.delete.side_effect = TaigaException(
            "Cannot delete milestone: 15 user stories assigned to it"
        )

        with pytest.raises(TaigaException, match="Cannot delete.*assigned"):
            delete_milestone(session_id="test-session", milestone_id=350)


class TestDeleteOperationSequencing:
    """Test cases for sequencing of multiple delete operations"""

    @patch("src.server._get_authenticated_client")
    def test_delete_multiple_items_success_sequence(self, mock_auth):
        """Should handle successful deletion of multiple items in sequence"""
        from src.server import delete_user_story, delete_task, delete_issue

        mock_client = Mock()
        mock_auth.return_value = mock_client

        # Delete three different resources successfully
        result1 = delete_user_story(session_id="test-session", user_story_id=200)
        result2 = delete_task(session_id="test-session", task_id=250)
        result3 = delete_issue(session_id="test-session", issue_id=300)

        assert result1["status"] == "deleted"
        assert result2["status"] == "deleted"
        assert result3["status"] == "deleted"

        # Verify all API calls were made
        assert mock_client.api.user_stories.delete.call_count == 1
        assert mock_client.api.tasks.delete.call_count == 1
        assert mock_client.api.issues.delete.call_count == 1

    @patch("src.server._get_authenticated_client")
    def test_delete_fails_on_second_item_in_sequence(self, mock_auth):
        """Should stop sequence when second delete fails"""
        from src.server import delete_user_story, delete_task

        mock_client = Mock()
        mock_auth.return_value = mock_client
        # First delete succeeds, second fails
        mock_client.api.user_stories.delete.return_value = None
        mock_client.api.tasks.delete.side_effect = TaigaException("404 Not Found")

        # First delete succeeds
        result1 = delete_user_story(session_id="test-session", user_story_id=200)
        assert result1["status"] == "deleted"

        # Second delete fails and raises exception
        with pytest.raises(TaigaException, match="404"):
            delete_task(session_id="test-session", task_id=999)

        # Both API calls were attempted
        assert mock_client.api.user_stories.delete.call_count == 1
        assert mock_client.api.tasks.delete.call_count == 1
