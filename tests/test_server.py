import uuid
from unittest.mock import MagicMock, patch

import pytest

# Import the server module instead of specific functions
import src.server
from src.taiga_client import TaigaClientWrapper
from src.types import SessionInfo

# Test constants
TEST_HOST = "https://your-test-taiga-instance.com"
TEST_USERNAME = "test_user"
TEST_PASSWORD = "test_password"


class TestTaigaTools:
    @pytest.fixture
    def session_setup(self):
        """Create a session setup for testing"""
        # Generate a session ID
        session_id = str(uuid.uuid4())

        # Create mock client
        mock_client = MagicMock()
        mock_client.is_authenticated = True

        # Create SessionInfo
        session_info = SessionInfo(session_id=session_id, client=mock_client, username="test_user")

        # Store session info in active_sessions
        src.server.active_sessions[session_id] = session_info

        return session_id, mock_client

    def test_login(self):
        """Test the login functionality"""
        with patch.object(TaigaClientWrapper, "login", return_value=True):
            # Clear any existing sessions
            src.server.active_sessions.clear()

            # Call the login function
            result = src.server.login(TEST_HOST, TEST_USERNAME, TEST_PASSWORD)

            # Verify results
            assert "session_id" in result
            assert result["session_id"] in src.server.active_sessions

            # Get the session ID for cleanup
            session_id = result["session_id"]
            src.server.active_sessions.clear()

    def test_list_projects(self, session_setup):
        """Test list_projects functionality"""
        session_id, mock_client = session_setup

        # Setup list projects return - return actual dictionaries
        mock_client.api.projects.list.return_value = [{"id": 123, "name": "Test Project"}]

        # List projects and verify
        projects = src.server.list_projects(session_id)
        assert len(projects) == 1
        assert projects[0]["name"] == "Test Project"
        assert projects[0]["id"] == 123

    def test_update_project(self, session_setup):
        """Test update_project functionality"""
        session_id, mock_client = session_setup

        # Setup mock project
        mock_project = MagicMock()
        mock_project.id = 123
        mock_project.name = "Old Name"

        # Setup allowed parameters for the project model
        mock_client.api.projects.instance = MagicMock()
        mock_client.api.projects.instance.allowed_params = ["name", "description"]

        # Setup get project return
        mock_client.api.projects.get.return_value = mock_project

        # Update the project name
        result = src.server.update_project(session_id, 123, name="New Name")

        # Verify the update was called
        mock_project.update.assert_called_once()
        assert mock_project.name == "New Name"

    def test_list_user_stories(self, session_setup):
        """Test list_user_stories functionality"""
        session_id, mock_client = session_setup

        # Setup list user stories return - return actual dictionaries
        mock_client.api.user_stories.list.return_value = [{"id": 456, "subject": "Test User Story"}]

        # List user stories and verify
        stories = src.server.list_user_stories(session_id, 123)
        assert len(stories) == 1
        assert stories[0]["subject"] == "Test User Story"
        assert stories[0]["id"] == 456

        # Verify the correct project_id filter was used
        mock_client.api.user_stories.list.assert_called_once_with(project_id=123)

    def test_create_user_story(self, session_setup):
        """Test create_user_story functionality"""
        session_id, mock_client = session_setup

        # Setup create user story return - return actual dictionary
        mock_client.api.user_stories.create.return_value = {"id": 456, "subject": "New Story"}

        # Create user story and verify
        story = src.server.create_user_story(
            session_id, 123, "New Story", description="Test description"
        )
        assert story["subject"] == "New Story"
        assert story["id"] == 456

        # Verify the create was called with correct parameters
        mock_client.api.user_stories.create.assert_called_once_with(
            project=123, subject="New Story", description="Test description"
        )

    def test_list_tasks(self, session_setup):
        """Test list_tasks functionality"""
        session_id, mock_client = session_setup

        # Setup list tasks return - return actual dictionaries
        mock_client.api.tasks.list.return_value = [{"id": 789, "subject": "Test Task"}]

        # List tasks and verify
        tasks = src.server.list_tasks(session_id, 123)
        assert len(tasks) == 1
        assert tasks[0]["subject"] == "Test Task"
        assert tasks[0]["id"] == 789

        # Verify the correct project_id filter was used
        mock_client.api.tasks.list.assert_called_once_with(project_id=123)

    def test_list_user_stories_uses_project_id_parameter(self, session_setup):
        """Verify list_user_stories uses project_id= (not project=) parameter"""
        session_id, mock_client = session_setup
        mock_client.api.user_stories.list.return_value = []

        src.server.list_user_stories(session_id, 123)

        # Verify called with project_id parameter (not project=)
        mock_client.api.user_stories.list.assert_called_once_with(project_id=123)

    def test_list_tasks_uses_project_id_parameter(self, session_setup):
        """Verify list_tasks uses project_id= (not project=) parameter"""
        session_id, mock_client = session_setup
        mock_client.api.tasks.list.return_value = []

        src.server.list_tasks(session_id, 123)

        # Verify called with project_id parameter (not project=)
        mock_client.api.tasks.list.assert_called_once_with(project_id=123)

    def test_get_project_uses_unified_accessor(self, session_setup):
        """Verify get_project uses unified get_resource accessor (US-2.2)"""
        session_id, mock_client = session_setup
        mock_project = {"id": 123, "name": "Test"}
        mock_client.get_resource = MagicMock(return_value=mock_project)

        result = src.server.get_project(session_id, 123)

        # Verify called with get_resource wrapper
        mock_client.get_resource.assert_called_once_with("project", 123)
        assert result["id"] == 123


# --- Tests for US-2.2: Consistent Resource Access Patterns ---


class TestResourceAccessPatterns:
    """Test suite for unified resource access patterns (US-2.2)."""

    @pytest.fixture
    def wrapper_with_auth(self):
        """Create authenticated TaigaClientWrapper for testing."""
        wrapper = TaigaClientWrapper("https://test.com")
        wrapper.api = MagicMock()
        wrapper.api.auth_token = "test-token"
        return wrapper

    def test_get_resource_project_uses_named_parameter(self, wrapper_with_auth):
        """Verify get_resource uses named parameter for projects."""
        wrapper_with_auth.api.projects.get.return_value = {"id": 123, "name": "Test"}

        result = wrapper_with_auth.get_resource("project", 123)

        # Verify named parameter used
        wrapper_with_auth.api.projects.get.assert_called_once_with(project_id=123)
        assert result["id"] == 123

    def test_get_resource_user_story_uses_positional_parameter(self, wrapper_with_auth):
        """Verify get_resource uses positional parameter for user stories."""
        wrapper_with_auth.api.user_stories.get.return_value = {
            "id": 456,
            "subject": "Story",
        }

        result = wrapper_with_auth.get_resource("user_story", 456)

        # Verify positional parameter used
        wrapper_with_auth.api.user_stories.get.assert_called_once_with(456)
        assert result["id"] == 456

    def test_get_resource_task(self, wrapper_with_auth):
        """Verify get_resource works for tasks."""
        wrapper_with_auth.api.tasks.get.return_value = {"id": 789, "subject": "Task"}

        result = wrapper_with_auth.get_resource("task", 789)

        wrapper_with_auth.api.tasks.get.assert_called_once_with(789)
        assert result["id"] == 789

    def test_get_resource_issue(self, wrapper_with_auth):
        """Verify get_resource works for issues."""
        wrapper_with_auth.api.issues.get.return_value = {"id": 101, "subject": "Issue"}

        result = wrapper_with_auth.get_resource("issue", 101)

        wrapper_with_auth.api.issues.get.assert_called_once_with(101)
        assert result["id"] == 101

    def test_get_resource_epic(self, wrapper_with_auth):
        """Verify get_resource works for epics."""
        wrapper_with_auth.api.epics.get.return_value = {"id": 202, "name": "Epic"}

        result = wrapper_with_auth.get_resource("epic", 202)

        wrapper_with_auth.api.epics.get.assert_called_once_with(202)
        assert result["id"] == 202

    def test_get_resource_milestone(self, wrapper_with_auth):
        """Verify get_resource works for milestones."""
        wrapper_with_auth.api.milestones.get.return_value = {
            "id": 303,
            "name": "Milestone",
        }

        result = wrapper_with_auth.get_resource("milestone", 303)

        wrapper_with_auth.api.milestones.get.assert_called_once_with(303)
        assert result["id"] == 303

    def test_get_resource_wiki_page(self, wrapper_with_auth):
        """Verify get_resource works for wiki pages."""
        wrapper_with_auth.api.wiki.get.return_value = {"id": 404, "title": "Page"}

        result = wrapper_with_auth.get_resource("wiki_page", 404)

        wrapper_with_auth.api.wiki.get.assert_called_once_with(404)
        assert result["id"] == 404

    def test_get_resource_invalid_type_raises_error(self, wrapper_with_auth):
        """Verify invalid resource type raises ValueError."""
        with pytest.raises(ValueError) as exc_info:
            wrapper_with_auth.get_resource("invalid_type", 123)

        assert "Unknown resource type 'invalid_type'" in str(exc_info.value)
        assert "Valid types:" in str(exc_info.value)
        assert "project" in str(exc_info.value)

    def test_get_resource_requires_authentication(self):
        """Verify get_resource enforces authentication."""
        wrapper = TaigaClientWrapper("https://test.com")
        wrapper.api = None  # Not authenticated

        with pytest.raises(PermissionError) as exc_info:
            wrapper.get_resource("project", 123)

        assert "not authenticated" in str(exc_info.value).lower()

    def test_get_resource_all_types_in_mapping(self, wrapper_with_auth):
        """Verify all resource types in RESOURCE_MAPPING work correctly."""
        from src.taiga_client import RESOURCE_MAPPING

        # Test each resource type has expected configuration
        for resource_type, config in RESOURCE_MAPPING.items():
            assert "accessor" in config
            assert "get_pattern" in config
            assert "id_param" in config
            assert config["get_pattern"] in ("named", "positional")

            # Create mock for this resource
            accessor_name = config["accessor"]
            mock_resource = MagicMock()
            mock_resource.get.return_value = {"id": 999, "type": resource_type}
            setattr(wrapper_with_auth.api, accessor_name, mock_resource)

            # Call get_resource
            result = wrapper_with_auth.get_resource(resource_type, 999)

            # Verify result
            assert result["id"] == 999
            mock_resource.get.assert_called()
