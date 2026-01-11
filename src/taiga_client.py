# taiga_client.py
import logging
import os
from typing import Optional

# Replace python-taiga import
# from taiga import TaigaAPI
# from taiga.exceptions import TaigaException
from pytaigaclient import TaigaClient  # Import the new client

# Assuming pytaigaclient also has a base exception
from pytaigaclient.exceptions import TaigaException

# Ensure logger is named correctly for hierarchy
logger = logging.getLogger(__name__)

# --- Resource Type Mapping for Consistent Access Patterns (US-2.2) ---
# Maps MCP resource names to pytaigaclient resource accessor names and parameter patterns.
# This centralizes knowledge about pytaigaclient API variations (named vs positional parameters).
# Used by get_resource() method to provide unified resource retrieval interface.
RESOURCE_MAPPING = {
    "project": {
        "accessor": "projects",
        "get_pattern": "named",  # projects.get(project_id=id)
        "id_param": "project_id",
    },
    "user_story": {
        "accessor": "user_stories",
        "get_pattern": "positional",  # user_stories.get(id)
        "id_param": "user_story_id",
    },
    "task": {
        "accessor": "tasks",
        "get_pattern": "positional",
        "id_param": "task_id",
    },
    "issue": {
        "accessor": "issues",
        "get_pattern": "positional",
        "id_param": "issue_id",
    },
    "epic": {
        "accessor": "epics",
        "get_pattern": "positional",
        "id_param": "epic_id",
    },
    "milestone": {
        "accessor": "milestones",
        "get_pattern": "positional",
        "id_param": "milestone_id",
    },
    "wiki_page": {
        "accessor": "wiki",
        "get_pattern": "positional",
        "id_param": "wiki_page_id",
    },
}


class TaigaClientWrapper:
    """
    A wrapper around the pytaiga-client library to manage API instance
    and authentication state.
    """

    def __init__(self, host: str):
        if not host:
            raise ValueError("Taiga host URL cannot be empty.")
        # Store host, but initialize client later during login/token auth
        self.host = host
        # Use the new client type
        self.api: Optional[TaigaClient] = None
        logger.info(f"TaigaClientWrapper initialized for host: {self.host}")

    def login(self, username: str, password: str) -> bool:
        """
        Authenticates with the Taiga instance using username and password.
        Uses pytaigaclient.

        Enforces HTTPS for security. Can be disabled for local development with
        ALLOW_HTTP_TAIGA=true environment variable.
        """
        try:
            logger.info(f"Attempting login for user '{username}' on {self.host}")

            # HTTPS Enforcement (US-1.4)
            if not self.host.startswith("https://"):
                allow_http = os.getenv("ALLOW_HTTP_TAIGA", "false").lower() == "true"
                if not allow_http:
                    error_msg = (
                        "Taiga host must use HTTPS for security. "
                        "Set ALLOW_HTTP_TAIGA=true to bypass for local development."
                    )
                    logger.error(f"HTTPS validation failed: {error_msg}")
                    raise ValueError(error_msg)
                else:
                    logger.warning(
                        f"HTTPS enforcement disabled via ALLOW_HTTP_TAIGA=true. "
                        f"Connecting to {self.host} over HTTP is insecure!"
                    )

            # Initialize the client here
            api_instance = TaigaClient(host=self.host)
            # Use the auth resource's login method
            api_instance.auth.login(username=username, password=password)
            self.api = api_instance
            logger.info(f"Login successful for user '{username}'. Auth token acquired.")
            return True
        except ValueError:
            # Re-raise ValueError from HTTPS validation without wrapping
            raise
        except TaigaException as e:
            logger.error(f"Taiga login failed for user '{username}': {e}", exc_info=False)
            self.api = None
            raise e
        except Exception as e:
            logger.error(
                f"An unexpected error occurred during login for user '{username}': {e}",
                exc_info=True,
            )
            self.api = None
            # Wrap unexpected errors in TaigaException if needed, or re-raise
            raise TaigaException(f"Unexpected login error: {e}")

    # Add method for token authentication if needed by pytaigaclient
    # def set_token(self, token: str, token_type: str = "Bearer"):
    #     logger.info(f"Initializing TaigaClient with token on {self.host}")
    #     self.api = TaigaClient(host=self.host, auth_token=token, token_type=token_type)
    #     logger.info("TaigaClient initialized with token.")

    @property
    def is_authenticated(self) -> bool:
        """Checks if the client is currently authenticated (has an API instance with a token)."""
        # Check if api exists and has a token
        return self.api is not None and self.api.auth_token is not None

    def _ensure_authenticated(self):
        """Internal helper to check authentication before API calls."""
        if not self.is_authenticated:
            logger.error("Action required authentication, but client is not logged in.")
            # Use a standard exception type that FastMCP might handle better,
            # or a custom one if needed. PermissionError fits well.
            raise PermissionError("Client not authenticated. Please login first.")

    def get_resource(self, resource_type: str, resource_id: int):
        """
        Unified resource getter handling pytaigaclient parameter variations (US-2.2).

        Provides a consistent interface for retrieving any Taiga resource type,
        abstracting away the differences in how pytaigaclient requires parameters
        (some resources use named parameters, others use positional).

        Args:
            resource_type: Resource type key from RESOURCE_MAPPING.
                          Valid values: 'project', 'user_story', 'task', 'issue',
                          'epic', 'milestone', 'wiki_page'
            resource_id: Integer ID of the resource to retrieve

        Returns:
            Resource object from pytaigaclient (dict-like response)

        Raises:
            ValueError: If resource_type is not recognized or not in RESOURCE_MAPPING
            TaigaException: If API call fails (raised from pytaigaclient)
            PermissionError: If client not authenticated

        Example:
            >>> client.get_resource("project", 123)
            {'id': 123, 'name': 'My Project', ...}
            >>> client.get_resource("user_story", 456)
            {'id': 456, 'subject': 'User Story', ...}
        """
        self._ensure_authenticated()

        # Validate resource type
        if resource_type not in RESOURCE_MAPPING:
            valid_types = ", ".join(RESOURCE_MAPPING.keys())
            raise ValueError(
                f"Unknown resource type '{resource_type}'. " f"Valid types: {valid_types}"
            )

        # Get resource configuration
        resource_config = RESOURCE_MAPPING[resource_type]
        accessor_name = resource_config["accessor"]
        get_pattern = resource_config["get_pattern"]
        id_param = resource_config["id_param"]

        # Get the resource accessor from pytaigaclient
        resource_accessor = getattr(self.api, accessor_name)

        # Call get() with appropriate parameter pattern
        if get_pattern == "named":
            # Projects use: projects.get(project_id=id)
            logger.debug(
                f"Calling {accessor_name}.get({id_param}={resource_id}) with named parameter"
            )
            return resource_accessor.get(**{id_param: resource_id})
        else:
            # Others use: resource.get(id) with positional parameter
            logger.debug(f"Calling {accessor_name}.get({resource_id}) with positional parameter")
            return resource_accessor.get(resource_id)


# No changes needed to _ensure_authenticated or is_authenticated property logic,
# just the types and method calls within login.
