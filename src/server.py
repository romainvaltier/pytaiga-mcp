# server_fastmcp.py
import asyncio
import logging
import logging.config
import os
import threading
import uuid
from collections import deque
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Union

from mcp.server.fastmcp import FastMCP
from pytaigaclient.exceptions import TaigaException

from src.logging_utils import truncate_session_id

# Assuming taiga_client.py is in the same directory or accessible via PYTHONPATH
from src.taiga_client import TaigaClientWrapper
from src.types import (
    DeleteResponse,
    EpicList,
    EpicResponse,
    InviteResponse,
    IssueList,
    IssueResponse,
    IssueTypeList,
    LoginAttempt,
    LoginResponse,
    LogoutResponse,
    MemberList,
    MilestoneList,
    MilestoneResponse,
    PriorityList,
    ProjectList,
    ProjectResponse,
    RateLimitInfo,
    SessionInfo,
    SessionStatusResponse,
    SeverityList,
    StatusList,
    TaskList,
    TaskResponse,
    UserStoryList,
    UserStoryResponse,
    WikiPageList,
    WikiPageResponse,
)
from src.validators import (
    ValidationError,
    get_allowed_kwargs_for_resource,
    validate_description,
    validate_email,
    validate_epic_id,
    validate_issue_id,
    validate_kwargs,
    validate_milestone_id,
    validate_name,
    validate_positive_integer,
    validate_project_id,
    validate_string_length,
    validate_subject,
    validate_task_id,
    validate_user_id,
    validate_user_story_id,
)

# --- Logging Setup ---
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()],  # Log to stderr by default
)
logger = logging.getLogger(__name__)
# Quiet down pytaigaclient library logging if needed
logging.getLogger("pytaigaclient").setLevel(logging.WARNING)

# --- Session Management with TTL and Metadata ---
# Store active sessions: session_id -> SessionInfo instance
active_sessions: Dict[str, SessionInfo] = {}
# Track sessions by user for concurrent limit enforcement: username -> [session_id, ...]
sessions_by_user: Dict[str, List[str]] = {}
# Thread-safe lock for concurrent session operations (especially login)
_session_lock = threading.Lock()

# --- Rate Limiting with Sliding Window ---
# Track login attempts per username to prevent brute force attacks
rate_limit_data: Dict[str, RateLimitInfo] = {}
# Thread-safe lock for rate limit operations
_rate_limit_lock = threading.Lock()

# --- MCP Server Definition ---
# No lifespan needed for this approach
mcp = FastMCP("Taiga Bridge (Session ID)", dependencies=["pytaigaclient"])

# --- API Parameter Naming Conventions (enforced by pytaigaclient library) ---
# These conventions standardize how we call pytaigaclient methods throughout this module.
# Violations of these patterns may indicate library constraint issues or inconsistencies.
#
# LIST Operations:
#   - Standard: user_stories.list(project_id=project_id)
#   - Standard: tasks.list(project_id=project_id)
#   - Exception: milestones.list(project=project_id) - library requires "project=" not "project_id="
#   - Rationale: Taiga API query parameter is "project_id"; named parameters are explicit and self-documenting
#
# GET Operations:
#   - Standard (positional): user_stories.get(resource_id) - positional for most resources
#   - Exception (named): projects.get(project_id=project_id) - library requires named parameter
#   - Rationale: Projects library enforces named parameter; others accept positional
#
# UPDATE Operations:
#   - Projects: projects.update(project_id=id, version=v, project_data=dict)
#   - Others: resource.edit(resource_id=id, version=v, **kwargs)
#   - Rationale: Library enforces different method signatures
#
# CREATE Operations:
#   - Standard: resource.create(project=project_id, **kwargs) - library convention
#
# DELETE Operations:
#   - Standard: resource.delete(id=resource_id, version=version)
#
# NOTE: When adding new operations or resources, verify the expected parameter format
#       with pytaigaclient to ensure consistency with the patterns above.

# --- Session Cleanup Helper ---


def _cleanup_session(session_id: str) -> None:
    """
    Remove session from storage and user tracking.

    Ensures both active_sessions and sessions_by_user are updated,
    preventing memory leaks and maintaining consistent state.

    Args:
        session_id: The session ID to clean up
    """
    session_info = active_sessions.pop(session_id, None)
    if session_info:
        # Remove from user tracking
        user_sessions = sessions_by_user.get(session_info.username, [])
        if session_id in user_sessions:
            user_sessions.remove(session_id)
        # Clean up empty user lists
        if not user_sessions:
            sessions_by_user.pop(session_info.username, None)
        logger.debug(
            f"Cleaned up session for user '{session_info.username}': "
            f"{truncate_session_id(session_id)}"
        )


# --- Rate Limiting Helper Functions ---


def _check_rate_limit(username: str) -> None:
    """
    Check if user is rate limited due to too many failed login attempts.

    Uses sliding window algorithm to track attempts within configured time window.
    Applies lockout if threshold exceeded. Automatically cleans old attempts.

    Args:
        username: Username attempting login

    Raises:
        PermissionError: If user is locked out with remaining time in message
    """
    max_attempts = int(os.getenv("LOGIN_MAX_ATTEMPTS", "5"))
    window_seconds = int(os.getenv("LOGIN_RATE_WINDOW", "60"))
    lockout_seconds = int(os.getenv("LOGIN_LOCKOUT_DURATION", "900"))

    # Skip rate limiting if disabled (max_attempts = 0)
    if max_attempts == 0:
        return

    with _rate_limit_lock:
        if username not in rate_limit_data:
            return  # No attempts yet, allow login

        rate_info = rate_limit_data[username]

        # Check if currently locked out
        if rate_info.is_locked_out():
            remaining = rate_info.remaining_lockout_time()
            logger.warning(
                f"Login attempt blocked - user '{username}' is locked out "
                f"({remaining}s remaining)"
            )
            raise PermissionError(
                f"Too many failed login attempts. Account locked. "
                f"Try again in {remaining} seconds."
            )

        # Sliding window: Remove attempts outside the time window
        cutoff_time = datetime.utcnow() - timedelta(seconds=window_seconds)
        while rate_info.attempts and rate_info.attempts[0].timestamp < cutoff_time:
            rate_info.attempts.popleft()

        # Count failed attempts within window
        failed_attempts = [a for a in rate_info.attempts if not a.success]

        # Check if threshold would be exceeded with this attempt
        if len(failed_attempts) >= max_attempts:
            # Apply lockout
            rate_info.locked_until = datetime.utcnow() + timedelta(seconds=lockout_seconds)
            logger.warning(
                f"Rate limit threshold exceeded for user '{username}' "
                f"({len(failed_attempts)} failed attempts). "
                f"Applying {lockout_seconds}s lockout."
            )
            raise PermissionError(
                f"Too many failed login attempts ({max_attempts} in {window_seconds}s). "
                f"Account locked for {lockout_seconds} seconds."
            )


def _track_login_attempt(username: str, success: bool) -> None:
    """
    Record a login attempt for rate limiting purposes.

    Successful logins clear the lockout and failed attempt history.
    Failed attempts are added to the sliding window.

    Args:
        username: Username that attempted login
        success: Whether the login was successful
    """
    with _rate_limit_lock:
        if username not in rate_limit_data:
            rate_limit_data[username] = RateLimitInfo()

        rate_info = rate_limit_data[username]

        # Create attempt record
        attempt = LoginAttempt(timestamp=datetime.utcnow(), username=username, success=success)
        rate_info.attempts.append(attempt)

        # Clear lockout and failed attempts on successful login
        if success:
            rate_info.locked_until = None
            # Keep successful attempt but clear failed ones
            rate_info.attempts = deque([a for a in rate_info.attempts if a.success])
            logger.debug(f"Successful login cleared rate limit for user '{username}'")


# --- Helper Function for Session Validation ---


def _get_authenticated_client(session_id: str) -> TaigaClientWrapper:
    """
    Retrieves the authenticated TaigaClientWrapper for a given session ID.

    Performs three validation checks:
    1. Session exists
    2. Session has not expired (TTL check)
    3. Client is still authenticated

    Automatically cleans up expired/invalid sessions and updates last_accessed.

    Args:
        session_id: The session ID to validate

    Returns:
        TaigaClientWrapper: The authenticated client wrapper

    Raises:
        PermissionError: If session is invalid, expired, or not authenticated
    """
    session_info = active_sessions.get(session_id)

    # Check 1: Session exists
    if not session_info:
        logger.warning(f"Session not found: {truncate_session_id(session_id)}")
        raise PermissionError(
            f"Invalid session ID: '{truncate_session_id(session_id)}'. Please login again."
        )

    # Check 2: Session not expired
    if session_info.is_expired():
        logger.warning(
            f"Session expired for user '{session_info.username}': "
            f"{truncate_session_id(session_id)}"
        )
        _cleanup_session(session_id)
        raise PermissionError(
            f"Session expired. Please login again. "
            f"(Session ID: {truncate_session_id(session_id)})"
        )

    # Check 3: Client authenticated
    if not session_info.client.is_authenticated:
        logger.warning(f"Client authentication lost: {truncate_session_id(session_id)}")
        _cleanup_session(session_id)
        raise PermissionError(
            f"Session authentication lost: '{truncate_session_id(session_id)}'. "
            "Please login again."
        )

    # Update last accessed timestamp
    session_info.update_last_accessed()

    logger.debug(
        f"Valid session: {truncate_session_id(session_id)}, "
        f"user: {session_info.username}, "
        f"expires in: {session_info.time_until_expiry()}"
    )

    return session_info.client


def _assign_resource_to_user(
    session_id: str, resource_type: str, resource_id: int, user_id: int
) -> Dict[str, Any]:
    """
    Generic helper function to assign a resource to a user.

    Args:
        session_id: The session ID for authentication
        resource_type: The type of resource ('user_story', 'task', 'issue', 'epic')
        resource_id: The ID of the resource to assign
        user_id: The ID of the user to assign to

    Returns:
        The updated resource dictionary

    Implementation Notes:
        This is a factory function that consolidates duplication across
        assign_user_story_to_user, assign_task_to_user, assign_issue_to_user,
        and assign_epic_to_user.
    """
    # Validate inputs
    validate_positive_integer(resource_id, "resource_id")
    validate_positive_integer(user_id, "user_id")

    # Route to the appropriate update function based on resource type
    update_function_map = {
        "user_story": update_user_story,
        "task": update_task,
        "issue": update_issue,
        "epic": update_epic,
    }

    if resource_type not in update_function_map:
        raise ValueError(f"Unknown resource type: {resource_type}")

    update_func = update_function_map[resource_type]
    return update_func(session_id, resource_id, assigned_to=user_id)


def _unassign_resource_from_user(
    session_id: str, resource_type: str, resource_id: int
) -> Dict[str, Any]:
    """
    Generic helper function to unassign a resource from its current user.

    Args:
        session_id: The session ID for authentication
        resource_type: The type of resource ('user_story', 'task', 'issue', 'epic')
        resource_id: The ID of the resource to unassign

    Returns:
        The updated resource dictionary

    Implementation Notes:
        This is a factory function that consolidates duplication across
        unassign_user_story_from_user, unassign_task_from_user,
        unassign_issue_from_user, and unassign_epic_from_user.
    """
    # Validate inputs
    validate_positive_integer(resource_id, "resource_id")

    # Route to the appropriate update function based on resource type
    update_function_map = {
        "user_story": update_user_story,
        "task": update_task,
        "issue": update_issue,
        "epic": update_epic,
    }

    if resource_type not in update_function_map:
        raise ValueError(f"Unknown resource type: {resource_type}")

    update_func = update_function_map[resource_type]
    return update_func(session_id, resource_id, assigned_to=None)


# --- Background Session Cleanup ---


def _cleanup_expired_sessions_sync() -> int:
    """
    Synchronous cleanup of all expired sessions.

    Scans active_sessions for any sessions that have exceeded their TTL
    and removes them. Handles concurrent modification by creating a snapshot.

    Returns:
        int: Number of sessions cleaned up
    """
    expired_sessions = []

    # Create snapshot to avoid "dictionary changed size during iteration"
    for session_id, session_info in list(active_sessions.items()):
        if session_info.is_expired():
            expired_sessions.append(session_id)

    # Remove expired sessions
    for session_id in expired_sessions:
        _cleanup_session(session_id)

    if expired_sessions:
        logger.info(f"Background cleanup removed {len(expired_sessions)} expired sessions")

    return len(expired_sessions)


async def _background_session_cleanup():
    """
    Background task to periodically clean up expired sessions.

    Runs every SESSION_CLEANUP_INTERVAL seconds (default: 5 minutes).
    This prevents memory leaks and ensures expired sessions don't accumulate
    over time. Runs in a separate daemon thread to avoid blocking the main server.
    """
    cleanup_interval = int(os.getenv("SESSION_CLEANUP_INTERVAL", "300"))
    logger.info(f"Starting background session cleanup (interval: {cleanup_interval}s)")

    while True:
        try:
            await asyncio.sleep(cleanup_interval)
            _cleanup_expired_sessions_sync()
        except Exception as e:
            logger.error(f"Error in background cleanup: {e}", exc_info=True)


def _start_background_cleanup():
    """
    Start background cleanup task in separate daemon thread.

    Creates a new event loop in a daemon thread and runs the background
    cleanup task. The daemon thread will not prevent server shutdown.
    """
    loop = asyncio.new_event_loop()

    def run_loop():
        asyncio.set_event_loop(loop)
        loop.run_until_complete(_background_session_cleanup())

    cleanup_thread = threading.Thread(target=run_loop, daemon=True, name="SessionCleanup")
    cleanup_thread.start()
    logger.info("Background session cleanup thread started")


# Initialize cleanup on module load
_start_background_cleanup()


# --- Rate Limit Cleanup ---


def _cleanup_rate_limit_data_sync() -> int:
    """
    Clean up old rate limit data to prevent memory leaks.

    Removes entries where:
    - No active lockout
    - All attempts are older than 2x the rate window

    Returns:
        Number of entries cleaned up
    """
    window_seconds = int(os.getenv("LOGIN_RATE_WINDOW", "60"))
    cleanup_age = window_seconds * 2  # Keep data for 2x window
    cutoff_time = datetime.utcnow() - timedelta(seconds=cleanup_age)

    cleaned = 0
    with _rate_limit_lock:
        users_to_remove = []

        for username, rate_info in rate_limit_data.items():
            # Skip if locked out (keep lockout data)
            if rate_info.is_locked_out():
                continue

            # Remove if no attempts or all attempts are old
            if not rate_info.attempts or all(a.timestamp < cutoff_time for a in rate_info.attempts):
                users_to_remove.append(username)

        for username in users_to_remove:
            del rate_limit_data[username]
            cleaned += 1

    if cleaned > 0:
        logger.info(f"Rate limit cleanup removed {cleaned} user entries")

    return cleaned


async def _background_rate_limit_cleanup():
    """
    Background task to periodically clean up old rate limit data.

    Runs every RATE_LIMIT_CLEANUP_INTERVAL seconds (default: 5 minutes).
    Prevents memory accumulation from old login attempt records.
    """
    cleanup_interval = int(os.getenv("RATE_LIMIT_CLEANUP_INTERVAL", "300"))
    logger.info(f"Starting rate limit cleanup (interval: {cleanup_interval}s)")

    while True:
        try:
            await asyncio.sleep(cleanup_interval)
            _cleanup_rate_limit_data_sync()
        except Exception as e:
            logger.error(f"Error in rate limit cleanup: {e}", exc_info=True)


def _start_rate_limit_cleanup():
    """Start rate limit cleanup task in separate daemon thread."""
    loop = asyncio.new_event_loop()

    def run_loop():
        asyncio.set_event_loop(loop)
        loop.run_until_complete(_background_rate_limit_cleanup())

    cleanup_thread = threading.Thread(target=run_loop, daemon=True, name="RateLimitCleanup")
    cleanup_thread.start()
    logger.info("Rate limit cleanup thread started")


# Initialize rate limit cleanup on module load
_start_rate_limit_cleanup()


# --- MCP Tools ---


@mcp.tool(
    "login",
    description="Logs into a Taiga instance using username/password and returns a session_id for subsequent authenticated calls.",
)
def login(host: str, username: str, password: str) -> LoginResponse:
    """
    Authenticate with a Taiga instance and create an authenticated session.

    This tool initiates authentication with the Taiga API using username and password credentials.
    A unique session ID is returned for use in all subsequent API calls. The session remains valid
    for the configured TTL (default: 8 hours).

    Args:
        host: The base URL of the Taiga instance (must use HTTPS for security).
              Examples: https://api.taiga.io, https://taiga.company.com
        username: The Taiga username for authentication.
        password: The Taiga password for authentication.

    Returns:
        LoginResponse: Dictionary containing:
            - session_id: UUID string to use in subsequent authenticated calls
        Example: {"session_id": "550e8400-e29b-41d4-a716-446655440000"}

    Raises:
        ValueError: If the host URL doesn't use HTTPS (required for security).
        PermissionError: If user is rate limited (max login attempts exceeded).
        TaigaException: If authentication fails (invalid credentials).
        RuntimeError: If an unexpected server error occurs.

    Example:
        >>> result = login("https://api.taiga.io", "john_doe", "secure_password")
        >>> session_id = result["session_id"]
        >>> # Use session_id in subsequent tool calls
    """
    logger.info(f"Executing login tool for user '{username}' on host '{host}'")

    # Check rate limiting before attempting authentication
    try:
        _check_rate_limit(username)
    except PermissionError as e:
        logger.warning(f"Login rate limit exceeded for user '{username}': {e}")
        raise e

    try:
        wrapper = TaigaClientWrapper(host=host)
        login_successful = wrapper.login(username=username, password=password)

        if login_successful:
            # Thread-safe concurrent session limit enforcement
            max_sessions = int(os.getenv("MAX_CONCURRENT_SESSIONS", "5"))

            with _session_lock:
                user_sessions = sessions_by_user.get(username, [])

                # Enforce concurrent session limit
                if max_sessions > 0 and len(user_sessions) >= max_sessions:
                    oldest_session_id = user_sessions[0]
                    logger.warning(
                        f"User '{username}' exceeded max concurrent sessions ({max_sessions}). "
                        f"Removing oldest: {truncate_session_id(oldest_session_id)}"
                    )
                    _cleanup_session(oldest_session_id)

                # Generate session ID
                new_session_id = str(uuid.uuid4())

                # Create session with metadata
                session_info = SessionInfo(
                    session_id=new_session_id, client=wrapper, username=username
                )

                # Store session
                active_sessions[new_session_id] = session_info

                # Track by user
                if username not in sessions_by_user:
                    sessions_by_user[username] = []
                sessions_by_user[username].append(new_session_id)

            logger.info(
                f"Login successful for '{username}'. "
                f"Session: {truncate_session_id(new_session_id)}, "
                f"expires: {session_info.expires_at.isoformat()}"
            )

            # Track successful login for rate limiting
            _track_login_attempt(username, success=True)

            return {"session_id": new_session_id}
        else:
            # Should not happen if login raises exception on failure, but handle defensively
            logger.error(f"Login attempt for '{username}' returned False unexpectedly.")
            _track_login_attempt(username, success=False)
            raise RuntimeError("Login failed for an unknown reason.")

    except (ValueError, TaigaException) as e:
        logger.error(f"Login failed for '{username}': {e}", exc_info=False)
        # Track failed login for rate limiting
        _track_login_attempt(username, success=False)
        # Re-raise the exception - FastMCP will turn it into an error response
        raise e
    except Exception as e:
        logger.error(f"Unexpected error during login for '{username}': {e}", exc_info=True)
        # Track failed login for rate limiting
        _track_login_attempt(username, success=False)
        raise RuntimeError(f"An unexpected server error occurred during login: {e}")


# --- Project Tools ---


@mcp.tool(
    "list_projects",
    description="Lists projects accessible to the user associated with the provided session_id.",
)
def list_projects(session_id: str) -> ProjectList:
    """
    List all projects accessible to the authenticated user.

    Retrieves a list of all Taiga projects that the authenticated user has access to.

    Args:
        session_id: The UUID session identifier from login.

    Returns:
        ProjectList: List of ProjectResponse dictionaries, each containing:
            - id: Project ID
            - name: Project name
            - slug: URL-safe project identifier
            - description: Project description (optional)
            - And other project metadata fields

    Raises:
        PermissionError: If the session_id is invalid or expired.

    Example:
        >>> projects = list_projects(session_id)
        >>> for project in projects:
        ...     print(f"{project['name']} ({project['slug']})")
    """
    logger.info(f"Executing list_projects for session {session_id[:8]}...")
    taiga_client_wrapper = _get_authenticated_client(session_id)  # Use wrapper variable name
    try:
        # Use pytaigaclient syntax: client.resource.method()
        projects = taiga_client_wrapper.api.projects.list()
        # Remove .to_dict() as pytaigaclient should return dicts
        logger.info(
            f"list_projects successful for session {session_id[:8]}, found {len(projects)} projects."
        )
        return projects  # Return directly
    except TaigaException as e:
        logger.error(f"Taiga API error listing projects: {e}", exc_info=False)
        raise e
    except Exception as e:
        logger.error(f"Unexpected error listing projects: {e}", exc_info=True)
        raise RuntimeError(f"Server error listing projects: {e}")


@mcp.tool(
    "list_all_projects",
    description="Lists all projects visible to the user (requires admin privileges for full list). Uses the provided session_id.",
)
def list_all_projects(session_id: str) -> ProjectList:
    """
    List all projects visible to the authenticated user.

    Similar to list_projects but includes additional projects depending on permissions.
    Admin users may see more projects than regular users.

    Args:
        session_id: The UUID session identifier from login.

    Returns:
        ProjectList: List of ProjectResponse dictionaries (same as list_projects).

    Raises:
        PermissionError: If the session_id is invalid or expired.

    Example:
        >>> all_projects = list_all_projects(session_id)
    """
    logger.info(f"Executing list_all_projects for session {session_id[:8]}...")
    # pytaigaclient's list() likely behaves similarly to python-taiga's
    return list_projects(session_id)  # Keep delegation


@mcp.tool(
    "get_project", description="Gets detailed information about a specific project by its ID."
)
def get_project(session_id: str, project_id: int) -> ProjectResponse:
    """
    Get detailed information about a specific project.

    Retrieves full details of a project including metadata, settings, and members.

    Args:
        session_id: The UUID session identifier from login.
        project_id: The numeric ID of the project.

    Returns:
        ProjectResponse: Project details including:
            - id: Project ID
            - name: Project name
            - slug: URL-safe identifier
            - description: Project description
            - is_private: Privacy flag
            - owner: Owner user ID
            - And other metadata

    Raises:
        PermissionError: If the session_id is invalid.
        TaigaException: If the project doesn't exist or access denied.

    Example:
        >>> project = get_project(session_id, 42)
        >>> print(f"Project: {project['name']} - {project['description']}")
    """
    logger.info(f"Executing get_project ID {project_id} for session {session_id[:8]}...")
    taiga_client_wrapper = _get_authenticated_client(session_id)  # Use wrapper variable name
    try:
        # Use unified resource accessor (US-2.2)
        project = taiga_client_wrapper.get_resource("project", project_id)
        return project  # Return directly
    except TaigaException as e:
        logger.error(f"Taiga API error getting project {project_id}: {e}", exc_info=False)
        raise e
    except Exception as e:
        logger.error(f"Unexpected error getting project {project_id}: {e}", exc_info=True)
        raise RuntimeError(f"Server error getting project: {e}")


@mcp.tool(
    "get_project_by_slug",
    description="Gets detailed information about a specific project by its slug.",
)
def get_project_by_slug(session_id: str, slug: str) -> ProjectResponse:
    """
    Get detailed information about a specific project by its slug.

    Retrieves project details using the URL-safe slug identifier instead of numeric ID.

    Args:
        session_id: The UUID session identifier from login.
        slug: The URL-safe project identifier (e.g., 'my-awesome-project').

    Returns:
        ProjectResponse: Project details (see get_project for field details).

    Raises:
        PermissionError: If the session_id is invalid.
        TaigaException: If the project doesn't exist or access denied.

    Example:
        >>> project = get_project_by_slug(session_id, "my-project")
        >>> print(project['id'])  # Get numeric ID for other operations
    """
    logger.info(f"Executing get_project_by_slug '{slug}' for session {session_id[:8]}...")
    taiga_client_wrapper = _get_authenticated_client(session_id)  # Use wrapper variable name
    try:
        # Use pytaigaclient syntax: client.resource.get(slug=...)
        project = taiga_client_wrapper.api.projects.get(slug=slug)
        return project  # Return directly
    except TaigaException as e:
        logger.error(f"Taiga API error getting project by slug '{slug}': {e}", exc_info=False)
        raise e
    except Exception as e:
        logger.error(f"Unexpected error getting project by slug '{slug}': {e}", exc_info=True)
        raise RuntimeError(f"Server error getting project by slug: {e}")


@mcp.tool("create_project", description="Creates a new project.")
def create_project(session_id: str, name: str, description: str, **kwargs) -> ProjectResponse:
    """
    Create a new Taiga project.

    Creates a new project in Taiga with the provided name and description.
    Additional project settings can be configured via optional kwargs.

    Args:
        session_id: The UUID session identifier from login.
        name: The project name (required, max 200 chars).
        description: Project description (required, max 1000 chars).
        **kwargs: Optional project settings:
            - is_private: Boolean, defaults to False
            - default_owner_role: Integer role ID
            - tags: List of tag strings

    Returns:
        ProjectResponse: The newly created project with:
            - id: Numeric project ID
            - name: Project name
            - slug: Auto-generated URL-safe identifier
            - description: Project description
            - And other metadata fields

    Raises:
        PermissionError: If the session_id is invalid.
        ValueError: If name or description is invalid.
        TaigaException: If project creation fails.

    Example:
        >>> project = create_project(
        ...     session_id,
        ...     "My Awesome Project",
        ...     "A project for awesome work",
        ...     is_private=True
        ... )
        >>> print(f"Created project with ID: {project['id']}")
    """
    logger.info(
        f"Executing create_project '{name}' for session {session_id[:8]} with data: {kwargs}"
    )
    taiga_client_wrapper = _get_authenticated_client(session_id)

    # Input validation
    try:
        name = validate_name(name)
        description = validate_description(description)
        allowed_kwargs = get_allowed_kwargs_for_resource("project")
        kwargs = validate_kwargs(kwargs, allowed_kwargs)
    except ValidationError as e:
        logger.warning(f"Input validation failed for create_project: {e}")
        raise ValueError(str(e))

    try:
        # Use pytaigaclient syntax: client.projects.create(name=..., description=..., **kwargs)
        new_project = taiga_client_wrapper.api.projects.create(
            name=name, description=description, **kwargs
        )
        logger.info(f"Project '{name}' created successfully (ID: {new_project.get('id', 'N/A')}).")
        return new_project  # Return the created project dict
    except TaigaException as e:
        logger.error(f"Taiga API error creating project '{name}': {e}", exc_info=False)
        raise e
    except Exception as e:
        logger.error(f"Unexpected error creating project '{name}': {e}", exc_info=True)
        raise RuntimeError(f"Server error creating project: {e}")


@mcp.tool("update_project", description="Updates details of an existing project.")
def update_project(session_id: str, project_id: int, **kwargs) -> ProjectResponse:
    """
    Update an existing project's details.

    Modifies one or more fields of an existing project. Only the fields provided in kwargs are updated.

    Args:
        session_id: The UUID session identifier from login.
        project_id: The numeric ID of the project to update.
        **kwargs: Project fields to update (name, description, is_private, tags, default_owner_role).

    Returns:
        ProjectResponse: The updated project details (see create_project for fields).

    Raises:
        PermissionError: If the session_id is invalid.
        ValueError: If project_id is invalid or update values are invalid.
        TaigaException: If project doesn't exist or update fails.

    Example:
        >>> updated = update_project(session_id, 42, description="Updated description")
        >>> print(f"Updated: {updated['description']}")
    """
    logger.info(
        f"Executing update_project ID {project_id} for session {session_id[:8]} with data: {kwargs}"
    )
    taiga_client_wrapper = _get_authenticated_client(session_id)  # Use wrapper variable name

    # Input validation
    try:
        project_id = validate_project_id(project_id)
        allowed_kwargs = get_allowed_kwargs_for_resource("project")
        kwargs = validate_kwargs(kwargs, allowed_kwargs)
    except ValidationError as e:
        logger.warning(f"Input validation failed for update_project: {e}")
        raise ValueError(str(e))

    try:
        # Use pytaigaclient update pattern: client.resource.update(id=..., data=...)
        if not kwargs:
            logger.info(f"No fields provided for update on project {project_id}")
            # Return current state if no updates provided
            return taiga_client_wrapper.get_resource("project", project_id)

        # First fetch the project to get its current version
        current_project = taiga_client_wrapper.get_resource("project", project_id)
        version = current_project.get("version")
        if not version:
            raise ValueError(f"Could not determine version for project {project_id}")

        # The project update method requires project_id, version, and project_data
        updated_project = taiga_client_wrapper.api.projects.update(
            project_id=project_id, version=version, project_data=kwargs
        )
        logger.info(f"Project {project_id} update request sent.")
        # Return the result from the update call
        return updated_project
    except TaigaException as e:
        logger.error(f"Taiga API error updating project {project_id}: {e}", exc_info=False)
        raise e
    except Exception as e:
        logger.error(f"Unexpected error updating project {project_id}: {e}", exc_info=True)
        raise RuntimeError(f"Server error updating project: {e}")


@mcp.tool("delete_project", description="Deletes a project by its ID. This is irreversible.")
def delete_project(session_id: str, project_id: int) -> DeleteResponse:
    """
    Delete a project permanently.

    Permanently deletes a project and all its associated data. This operation is irreversible.

    Args:
        session_id: The UUID session identifier from login.
        project_id: The numeric ID of the project to delete.

    Returns:
        DeleteResponse: Confirmation dictionary with:
            - status: "deleted" if successful

    Raises:
        PermissionError: If the session_id is invalid or user lacks permission to delete.
        ValueError: If project_id is invalid.
        TaigaException: If project doesn't exist or deletion fails.

    Example:
        >>> result = delete_project(session_id, 42)
        >>> print(result["status"])  # "deleted"
    """
    logger.warning(f"Executing delete_project ID {project_id} for session {session_id[:8]}...")
    taiga_client_wrapper = _get_authenticated_client(session_id)  # Use wrapper variable name

    # Input validation
    try:
        project_id = validate_project_id(project_id)
    except ValidationError as e:
        logger.warning(f"Input validation failed for delete_project: {e}")
        raise ValueError(str(e))

    try:
        # Use pytaigaclient syntax: client.resource.delete(id=...)
        taiga_client_wrapper.api.projects.delete(id=project_id)
        logger.info(f"Project {project_id} deleted successfully.")
        return {"status": "deleted", "project_id": project_id}
    except TaigaException as e:
        logger.error(f"Taiga API error deleting project {project_id}: {e}", exc_info=False)
        raise e
    except Exception as e:
        logger.error(f"Unexpected error deleting project {project_id}: {e}", exc_info=True)
        raise RuntimeError(f"Server error deleting project: {e}")


# --- User Story Tools ---


@mcp.tool(
    "list_user_stories",
    description="Lists user stories within a specific project, optionally filtered.",
)
def list_user_stories(session_id: str, project_id: int, **filters) -> UserStoryList:
    """
    List all user stories in a project.

    Retrieves user stories from a project with optional filtering by status, milestone, assignee, etc.

    Args:
        session_id: The UUID session identifier from login.
        project_id: The numeric ID of the project.
        **filters: Optional filter parameters:
            - milestone: Milestone/sprint ID
            - status: Status ID
            - assigned_to: User ID

    Returns:
        UserStoryList: List of UserStoryResponse dictionaries for the project.

    Raises:
        PermissionError: If the session_id is invalid.
        ValueError: If project_id is invalid.

    Example:
        >>> stories = list_user_stories(session_id, 42)
        >>> for story in stories:
        ...     print(f"{story['subject']} (status: {story.get('status')})")
    """
    logger.info(
        f"Executing list_user_stories for project {project_id}, session {session_id[:8]}, filters: {filters}"
    )
    taiga_client_wrapper = _get_authenticated_client(session_id)  # Use wrapper variable name

    # Input validation
    try:
        project_id = validate_project_id(project_id)
    except ValidationError as e:
        logger.warning(f"Input validation failed for list_user_stories: {e}")
        raise ValueError(str(e))

    try:
        # Use pytaigaclient syntax: client.resource.list(project_id=..., **filters)
        stories = taiga_client_wrapper.api.user_stories.list(project_id=project_id, **filters)
        return stories  # Return directly
    except TaigaException as e:
        logger.error(
            f"Taiga API error listing user stories for project {project_id}: {e}", exc_info=False
        )
        raise e
    except Exception as e:
        logger.error(
            f"Unexpected error listing user stories for project {project_id}: {e}", exc_info=True
        )
        raise RuntimeError(f"Server error listing user stories: {e}")


@mcp.tool("create_user_story", description="Creates a new user story within a project.")
def create_user_story(
    session_id: str, project_id: int, subject: str, **kwargs
) -> UserStoryResponse:
    """
    Create a new user story in a project.

    Creates a user story with the required subject and optional additional fields.

    Args:
        session_id: The UUID session identifier from login.
        project_id: The numeric ID of the project.
        subject: The user story title (required, max 500 chars).
        **kwargs: Optional fields:
            - description: Detailed description
            - epic: Epic ID
            - milestone: Milestone/Sprint ID
            - assigned_to: User ID to assign to
            - status: Status ID
            - tags: List of tag strings

    Returns:
        UserStoryResponse: The created user story with:
            - id: Numeric story ID
            - subject: Story title
            - project: Project ID
            - And other metadata fields

    Raises:
        PermissionError: If the session_id is invalid.
        ValueError: If project_id or subject is invalid.
        TaigaException: If creation fails.

    Example:
        >>> story = create_user_story(
        ...     session_id,
        ...     42,
        ...     "As a user, I want to login",
        ...     description="User authentication feature"
        ... )
        >>> print(f"Created story {story['id']}: {story['subject']}")
    """
    logger.info(
        f"Executing create_user_story '{subject}' in project {project_id}, session {session_id[:8]}..."
    )
    taiga_client_wrapper = _get_authenticated_client(session_id)  # Use wrapper variable name

    # Input validation
    try:
        project_id = validate_project_id(project_id)
        subject = validate_subject(subject)
        allowed_kwargs = get_allowed_kwargs_for_resource("user_story")
        kwargs = validate_kwargs(kwargs, allowed_kwargs)
    except ValidationError as e:
        logger.warning(f"Input validation failed for create_user_story: {e}")
        raise ValueError(str(e))

    try:
        # Use pytaigaclient syntax: client.resource.create(project=..., subject=..., **kwargs)
        story = taiga_client_wrapper.api.user_stories.create(
            project=project_id, subject=subject, **kwargs
        )
        logger.info(
            f"User story '{subject}' created successfully (ID: {story.get('id', 'N/A')})."
        )  # Use .get() for safety
        return story  # Return directly
    except TaigaException as e:
        logger.error(f"Taiga API error creating user story '{subject}': {e}", exc_info=False)
        raise e
    except Exception as e:
        logger.error(f"Unexpected error creating user story '{subject}': {e}", exc_info=True)
        raise RuntimeError(f"Server error creating user story: {e}")


@mcp.tool(
    "get_user_story", description="Gets detailed information about a specific user story by its ID."
)
def get_user_story(session_id: str, user_story_id: int) -> UserStoryResponse:
    """
    Get detailed information about a specific user story.

    Retrieves full details of a user story including description, status, assignments, etc.

    Args:
        session_id: The UUID session identifier from login.
        user_story_id: The numeric ID of the user story.

    Returns:
        UserStoryResponse: User story details including:
            - id: Story ID
            - subject: Story title
            - description: Full description
            - project: Project ID
            - assigned_to: Assigned user ID (or null)
            - status: Current status ID
            - And other metadata fields

    Raises:
        PermissionError: If the session_id is invalid.
        TaigaException: If the story doesn't exist or access denied.

    Example:
        >>> story = get_user_story(session_id, 123)
        >>> print(f"{story['subject']} - {story.get('description')}")
    """
    logger.info(f"Executing get_user_story ID {user_story_id} for session {session_id[:8]}...")
    taiga_client_wrapper = _get_authenticated_client(session_id)  # Use wrapper variable name
    try:
        # Use unified resource accessor (US-2.2)
        story = taiga_client_wrapper.get_resource("user_story", user_story_id)
        return story  # Return directly
    except TaigaException as e:
        logger.error(f"Taiga API error getting user story {user_story_id}: {e}", exc_info=False)
        raise e
    except Exception as e:
        logger.error(f"Unexpected error getting user story {user_story_id}: {e}", exc_info=True)
        raise RuntimeError(f"Server error getting user story: {e}")


@mcp.tool("update_user_story", description="Updates details of an existing user story.")
def update_user_story(session_id: str, user_story_id: int, **kwargs) -> Dict[str, Any]:
    """Updates a user story. Pass fields to update as keyword arguments (e.g., subject, description, status_id, assigned_to)."""
    logger.info(
        f"Executing update_user_story ID {user_story_id} for session {session_id[:8]} with data: {kwargs}"
    )
    taiga_client_wrapper = _get_authenticated_client(session_id)  # Use wrapper variable name
    try:
        # Use pytaigaclient update pattern: client.resource.edit for partial updates
        if not kwargs:
            logger.info(f"No fields provided for update on user story {user_story_id}")
            return taiga_client_wrapper.get_resource("user_story", user_story_id)

        # Get current user story data to retrieve version
        current_story = taiga_client_wrapper.get_resource("user_story", user_story_id)
        version = current_story.get("version")
        if not version:
            raise ValueError(f"Could not determine version for user story {user_story_id}")

        # Use edit method for partial updates with keyword arguments
        updated_story = taiga_client_wrapper.api.user_stories.edit(
            user_story_id=user_story_id, version=version, **kwargs
        )
        logger.info(f"User story {user_story_id} update request sent.")
        return updated_story
    except TaigaException as e:
        logger.error(f"Taiga API error updating user story {user_story_id}: {e}", exc_info=False)
        raise e
    except Exception as e:
        logger.error(f"Unexpected error updating user story {user_story_id}: {e}", exc_info=True)
        raise RuntimeError(f"Server error updating user story: {e}")


@mcp.tool("delete_user_story", description="Deletes a user story by its ID.")
def delete_user_story(session_id: str, user_story_id: int) -> DeleteResponse:
    """Deletes a user story by ID."""
    logger.warning(
        f"Executing delete_user_story ID {user_story_id} for session {session_id[:8]}..."
    )
    taiga_client_wrapper = _get_authenticated_client(session_id)  # Use wrapper variable name

    # Input validation
    try:
        user_story_id = validate_user_story_id(user_story_id)
    except ValidationError as e:
        logger.warning(f"Input validation failed for delete_user_story: {e}")
        raise ValueError(str(e))

    try:
        # Use pytaigaclient syntax: client.resource.delete(id=...)
        taiga_client_wrapper.api.user_stories.delete(id=user_story_id)
        logger.info(f"User story {user_story_id} deleted successfully.")
        return {"status": "deleted", "user_story_id": user_story_id}
    except TaigaException as e:
        logger.error(f"Taiga API error deleting user story {user_story_id}: {e}", exc_info=False)
        raise e
    except Exception as e:
        logger.error(f"Unexpected error deleting user story {user_story_id}: {e}", exc_info=True)
        raise RuntimeError(f"Server error deleting user story: {e}")


@mcp.tool(
    "assign_user_story_to_user", description="Assigns a specific user story to a specific user."
)
def assign_user_story_to_user(session_id: str, user_story_id: int, user_id: int) -> Dict[str, Any]:
    """Assigns a user story to a user."""
    logger.info(
        f"Executing assign_user_story_to_user: US {user_story_id} -> User {user_id}, session {session_id[:8]}..."
    )
    return _assign_resource_to_user(session_id, "user_story", user_story_id, user_id)


@mcp.tool(
    "unassign_user_story_from_user",
    description="Unassigns a specific user story (sets assigned user to null).",
)
def unassign_user_story_from_user(session_id: str, user_story_id: int) -> Dict[str, Any]:
    """Unassigns a user story."""
    logger.info(
        f"Executing unassign_user_story_from_user: US {user_story_id}, session {session_id[:8]}..."
    )
    return _unassign_resource_from_user(session_id, "user_story", user_story_id)


@mcp.tool(
    "get_user_story_statuses",
    description="Lists the available statuses for user stories within a specific project.",
)
def get_user_story_statuses(session_id: str, project_id: int) -> List[Dict[str, Any]]:
    """Retrieves the list of user story statuses for a project."""
    logger.info(
        f"Executing get_user_story_statuses for project {project_id}, session {session_id[:8]}..."
    )
    taiga_client_wrapper = _get_authenticated_client(session_id)  # Use wrapper variable name
    try:
        # Use pytaigaclient syntax: client.resource.list(project_id=...)
        # Update resource name: user_story_statuses -> userstory_statuses
        statuses = taiga_client_wrapper.api.userstory_statuses.list(project_id=project_id)
        return statuses  # Return directly
    except TaigaException as e:
        logger.error(
            f"Taiga API error getting user story statuses for project {project_id}: {e}",
            exc_info=False,
        )
        raise e
    except Exception as e:
        logger.error(
            f"Unexpected error getting user story statuses for project {project_id}: {e}",
            exc_info=True,
        )
        raise RuntimeError(f"Server error getting user story statuses: {e}")


# --- Task Tools ---


@mcp.tool("list_tasks", description="Lists tasks within a specific project, optionally filtered.")
def list_tasks(session_id: str, project_id: int, **filters) -> TaskList:
    """
    List all tasks in a project.

    Retrieves tasks from a project with optional filtering by status, milestone, user story, assignee, etc.

    Args:
        session_id: The UUID session identifier from login.
        project_id: The numeric ID of the project.
        **filters: Optional filter parameters (milestone, status, user_story, assigned_to).

    Returns:
        TaskList: List of TaskResponse dictionaries for the project.

    Raises:
        PermissionError: If the session_id is invalid.
        ValueError: If project_id is invalid.

    Example:
        >>> tasks = list_tasks(session_id, 42)
    """
    logger.info(
        f"Executing list_tasks for project {project_id}, session {session_id[:8]}, filters: {filters}"
    )
    taiga_client_wrapper = _get_authenticated_client(session_id)  # Use wrapper variable name
    try:
        # Use pytaigaclient syntax: client.resource.list(project_id=..., **filters)
        tasks = taiga_client_wrapper.api.tasks.list(project_id=project_id, **filters)
        return tasks  # Return directly
    except TaigaException as e:
        logger.error(f"Taiga API error listing tasks for project {project_id}: {e}", exc_info=False)
        raise e
    except Exception as e:
        logger.error(f"Unexpected error listing tasks for project {project_id}: {e}", exc_info=True)
        raise RuntimeError(f"Server error listing tasks: {e}")


@mcp.tool("create_task", description="Creates a new task within a project.")
def create_task(session_id: str, project_id: int, subject: str, **kwargs) -> Dict[str, Any]:
    """Creates a task. Requires project_id and subject. Optional fields (description, milestone_id, status_id, user_story_id, assigned_to_id, etc.) via kwargs."""
    logger.info(
        f"Executing create_task '{subject}' in project {project_id}, session {session_id[:8]}..."
    )
    taiga_client_wrapper = _get_authenticated_client(session_id)  # Use wrapper variable name

    # Input validation
    try:
        project_id = validate_project_id(project_id)
        subject = validate_subject(subject)
        allowed_kwargs = get_allowed_kwargs_for_resource("task")
        kwargs = validate_kwargs(kwargs, allowed_kwargs)
    except ValidationError as e:
        logger.warning(f"Input validation failed for create_task: {e}")
        raise ValueError(str(e))

    try:
        # Use pytaigaclient syntax: client.resource.create(project=..., subject=..., **kwargs)
        task = taiga_client_wrapper.api.tasks.create(project=project_id, subject=subject, **kwargs)
        logger.info(f"Task '{subject}' created successfully (ID: {task.get('id', 'N/A')}).")
        return task  # Return directly
    except TaigaException as e:
        logger.error(f"Taiga API error creating task '{subject}': {e}", exc_info=False)
        raise e
    except Exception as e:
        logger.error(f"Unexpected error creating task '{subject}': {e}", exc_info=True)
        raise RuntimeError(f"Server error creating task: {e}")


@mcp.tool("get_task", description="Gets detailed information about a specific task by its ID.")
def get_task(session_id: str, task_id: int) -> Dict[str, Any]:
    """Retrieves task details by ID."""
    logger.info(f"Executing get_task ID {task_id} for session {session_id[:8]}...")
    taiga_client_wrapper = _get_authenticated_client(session_id)  # Use wrapper variable name
    try:
        # Tasks expects task_id as a positional argument
        task = taiga_client_wrapper.get_resource("task", task_id)
        return task  # Return directly
    except TaigaException as e:
        logger.error(f"Taiga API error getting task {task_id}: {e}", exc_info=False)
        raise e
    except Exception as e:
        logger.error(f"Unexpected error getting task {task_id}: {e}", exc_info=True)
        raise RuntimeError(f"Server error getting task: {e}")


@mcp.tool("update_task", description="Updates details of an existing task.")
def update_task(session_id: str, task_id: int, **kwargs) -> Dict[str, Any]:
    """Updates a task. Pass fields to update as keyword arguments (e.g., subject, description, status_id, assigned_to)."""
    logger.info(
        f"Executing update_task ID {task_id} for session {session_id[:8]} with data: {kwargs}"
    )
    taiga_client_wrapper = _get_authenticated_client(session_id)  # Use wrapper variable name

    # Input validation
    try:
        task_id = validate_task_id(task_id)
        allowed_kwargs = get_allowed_kwargs_for_resource("task")
        kwargs = validate_kwargs(kwargs, allowed_kwargs)
    except ValidationError as e:
        logger.warning(f"Input validation failed for update_task: {e}")
        raise ValueError(str(e))

    try:
        # Use pytaigaclient edit pattern for partial updates
        if not kwargs:
            logger.info(f"No fields provided for update on task {task_id}")
            return taiga_client_wrapper.get_resource("task", task_id)

        # Get current task data to retrieve version
        current_task = taiga_client_wrapper.get_resource("task", task_id)
        version = current_task.get("version")
        if not version:
            raise ValueError(f"Could not determine version for task {task_id}")

        # Use edit method for partial updates with keyword arguments
        updated_task = taiga_client_wrapper.api.tasks.edit(
            task_id=task_id, version=version, **kwargs
        )
        logger.info(f"Task {task_id} update request sent.")
        return updated_task
    except TaigaException as e:
        logger.error(f"Taiga API error updating task {task_id}: {e}", exc_info=False)
        raise e
    except Exception as e:
        logger.error(f"Unexpected error updating task {task_id}: {e}", exc_info=True)
        raise RuntimeError(f"Server error updating task: {e}")


@mcp.tool("delete_task", description="Deletes a task by its ID.")
def delete_task(session_id: str, task_id: int) -> DeleteResponse:
    """Deletes a task by ID."""
    logger.warning(f"Executing delete_task ID {task_id} for session {session_id[:8]}...")
    taiga_client_wrapper = _get_authenticated_client(session_id)  # Use wrapper variable name

    # Input validation
    try:
        task_id = validate_task_id(task_id)
    except ValidationError as e:
        logger.warning(f"Input validation failed for delete_task: {e}")
        raise ValueError(str(e))

    try:
        # Use pytaigaclient syntax: client.resource.delete(id=...)
        taiga_client_wrapper.api.tasks.delete(id=task_id)
        logger.info(f"Task {task_id} deleted successfully.")
        return {"status": "deleted", "task_id": task_id}
    except TaigaException as e:
        logger.error(f"Taiga API error deleting task {task_id}: {e}", exc_info=False)
        raise e
    except Exception as e:
        logger.error(f"Unexpected error deleting task {task_id}: {e}", exc_info=True)
        raise RuntimeError(f"Server error deleting task: {e}")


@mcp.tool("assign_task_to_user", description="Assigns a specific task to a specific user.")
def assign_task_to_user(session_id: str, task_id: int, user_id: int) -> Dict[str, Any]:
    """Assigns a task to a user."""
    logger.info(
        f"Executing assign_task_to_user: Task {task_id} -> User {user_id}, session {session_id[:8]}..."
    )
    return _assign_resource_to_user(session_id, "task", task_id, user_id)


@mcp.tool(
    "unassign_task_from_user", description="Unassigns a specific task (sets assigned user to null)."
)
def unassign_task_from_user(session_id: str, task_id: int) -> Dict[str, Any]:
    """Unassigns a task."""
    logger.info(f"Executing unassign_task_from_user: Task {task_id}, session {session_id[:8]}...")
    return _unassign_resource_from_user(session_id, "task", task_id)


# --- Issue Tools ---


@mcp.tool("list_issues", description="Lists issues within a specific project, optionally filtered.")
def list_issues(session_id: str, project_id: int, **filters) -> IssueList:
    """Lists issues for a project. Optional filters like 'milestone', 'status', 'priority', 'severity', 'type', 'assigned_to' can be passed as kwargs."""
    logger.info(
        f"Executing list_issues for project {project_id}, session {session_id[:8]}, filters: {filters}"
    )
    taiga_client_wrapper = _get_authenticated_client(session_id)  # Use wrapper variable name
    try:
        # Use pytaigaclient syntax: client.resource.list(project_id=..., **filters)
        issues = taiga_client_wrapper.api.issues.list(project_id=project_id, **filters)
        return issues  # Return directly
    except TaigaException as e:
        logger.error(
            f"Taiga API error listing issues for project {project_id}: {e}", exc_info=False
        )
        raise e
    except Exception as e:
        logger.error(
            f"Unexpected error listing issues for project {project_id}: {e}", exc_info=True
        )
        raise RuntimeError(f"Server error listing issues: {e}")


@mcp.tool("create_issue", description="Creates a new issue within a project.")
def create_issue(
    session_id: str,
    project_id: int,
    subject: str,
    priority_id: int,
    status_id: int,
    severity_id: int,
    type_id: int,
    **kwargs,
) -> Dict[str, Any]:
    """Creates an issue. Requires project_id, subject, priority_id, status_id, severity_id, type_id. Optional fields (description, assigned_to_id, etc.) via kwargs."""
    logger.info(
        f"Executing create_issue '{subject}' in project {project_id}, session {session_id[:8]}..."
    )
    taiga_client_wrapper = _get_authenticated_client(session_id)  # Use wrapper variable name
    if not subject:
        raise ValueError("Issue subject cannot be empty.")
    try:
        # Use pytaigaclient syntax: client.resource.create(...)
        # Assuming pytaigaclient expects _id suffix for relational fields in create, but 'project' for project itself
        issue = taiga_client_wrapper.api.issues.create(
            project=project_id,  # Changed project_id to project
            subject=subject,
            priority_id=priority_id,  # Assume _id suffix
            status_id=status_id,  # Assume _id suffix
            type_id=type_id,  # Assume _id suffix
            severity_id=severity_id,  # Assume _id suffix
            **kwargs,
        )
        logger.info(f"Issue '{subject}' created successfully (ID: {issue.get('id', 'N/A')}).")
        return issue  # Return directly
    except TaigaException as e:
        logger.error(f"Taiga API error creating issue '{subject}': {e}", exc_info=False)
        raise e
    except Exception as e:
        logger.error(f"Unexpected error creating issue '{subject}': {e}", exc_info=True)
        raise RuntimeError(f"Server error creating issue: {e}")


@mcp.tool("get_issue", description="Gets detailed information about a specific issue by its ID.")
def get_issue(session_id: str, issue_id: int) -> Dict[str, Any]:
    """Retrieves issue details by ID."""
    logger.info(f"Executing get_issue ID {issue_id} for session {session_id[:8]}...")
    taiga_client_wrapper = _get_authenticated_client(session_id)  # Use wrapper variable name
    try:
        # Issues expects issue_id as a positional argument
        issue = taiga_client_wrapper.get_resource("issue", issue_id)
        return issue  # Return directly
    except TaigaException as e:
        logger.error(f"Taiga API error getting issue {issue_id}: {e}", exc_info=False)
        raise e
    except Exception as e:
        logger.error(f"Unexpected error getting issue {issue_id}: {e}", exc_info=True)
        raise RuntimeError(f"Server error getting issue: {e}")


@mcp.tool("update_issue", description="Updates details of an existing issue.")
def update_issue(session_id: str, issue_id: int, **kwargs) -> Dict[str, Any]:
    """Updates an issue. Pass fields to update as keyword arguments (e.g., subject, description, status_id, assigned_to)."""
    logger.info(
        f"Executing update_issue ID {issue_id} for session {session_id[:8]} with data: {kwargs}"
    )
    taiga_client_wrapper = _get_authenticated_client(session_id)  # Use wrapper variable name
    try:
        # Use pytaigaclient edit pattern for partial updates
        if not kwargs:
            logger.info(f"No fields provided for update on issue {issue_id}")
            return taiga_client_wrapper.get_resource("issue", issue_id)

        # Get current issue data to retrieve version
        current_issue = taiga_client_wrapper.get_resource("issue", issue_id)
        version = current_issue.get("version")
        if not version:
            raise ValueError(f"Could not determine version for issue {issue_id}")

        # Use edit method for partial updates with keyword arguments
        updated_issue = taiga_client_wrapper.api.issues.edit(
            issue_id=issue_id, version=version, **kwargs
        )
        logger.info(f"Issue {issue_id} update request sent.")
        return updated_issue
    except TaigaException as e:
        logger.error(f"Taiga API error updating issue {issue_id}: {e}", exc_info=False)
        raise e
    except Exception as e:
        logger.error(f"Unexpected error updating issue {issue_id}: {e}", exc_info=True)
        raise RuntimeError(f"Server error updating issue: {e}")


@mcp.tool("delete_issue", description="Deletes an issue by its ID.")
def delete_issue(session_id: str, issue_id: int) -> DeleteResponse:
    """Deletes an issue by ID."""
    logger.warning(f"Executing delete_issue ID {issue_id} for session {session_id[:8]}...")
    taiga_client_wrapper = _get_authenticated_client(session_id)  # Use wrapper variable name

    # Input validation
    try:
        issue_id = validate_issue_id(issue_id)
    except ValidationError as e:
        logger.warning(f"Input validation failed for delete_issue: {e}")
        raise ValueError(str(e))

    try:
        # Use pytaigaclient syntax: client.resource.delete(id=...)
        taiga_client_wrapper.api.issues.delete(id=issue_id)
        logger.info(f"Issue {issue_id} deleted successfully.")
        return {"status": "deleted", "issue_id": issue_id}
    except TaigaException as e:
        logger.error(f"Taiga API error deleting issue {issue_id}: {e}", exc_info=False)
        raise e
    except Exception as e:
        logger.error(f"Unexpected error deleting issue {issue_id}: {e}", exc_info=True)
        raise RuntimeError(f"Server error deleting issue: {e}")


@mcp.tool("assign_issue_to_user", description="Assigns a specific issue to a specific user.")
def assign_issue_to_user(session_id: str, issue_id: int, user_id: int) -> Dict[str, Any]:
    """Assigns an issue to a user."""
    logger.info(
        f"Executing assign_issue_to_user: Issue {issue_id} -> User {user_id}, session {session_id[:8]}..."
    )
    return _assign_resource_to_user(session_id, "issue", issue_id, user_id)


@mcp.tool(
    "unassign_issue_from_user",
    description="Unassigns a specific issue (sets assigned user to null).",
)
def unassign_issue_from_user(session_id: str, issue_id: int) -> Dict[str, Any]:
    """Unassigns an issue."""
    logger.info(
        f"Executing unassign_issue_from_user: Issue {issue_id}, session {session_id[:8]}..."
    )
    return _unassign_resource_from_user(session_id, "issue", issue_id)


@mcp.tool(
    "get_issue_statuses",
    description="Lists the available statuses for issues within a specific project.",
)
def get_issue_statuses(session_id: str, project_id: int) -> List[Dict[str, Any]]:
    """Retrieves the list of issue statuses for a project."""
    logger.info(
        f"Executing get_issue_statuses for project {project_id}, session {session_id[:8]}..."
    )
    taiga_client_wrapper = _get_authenticated_client(session_id)  # Use wrapper variable name
    try:
        # Use pytaigaclient syntax: client.resource.list(project_id=...)
        statuses = taiga_client_wrapper.api.issue_statuses.list(project_id=project_id)
        return statuses  # Return directly
    except TaigaException as e:
        logger.error(
            f"Taiga API error getting issue statuses for project {project_id}: {e}", exc_info=False
        )
        raise e
    except Exception as e:
        logger.error(
            f"Unexpected error getting issue statuses for project {project_id}: {e}", exc_info=True
        )
        raise RuntimeError(f"Server error getting issue statuses: {e}")


@mcp.tool(
    "get_issue_priorities",
    description="Lists the available priorities for issues within a specific project.",
)
def get_issue_priorities(session_id: str, project_id: int) -> List[Dict[str, Any]]:
    """Retrieves the list of issue priorities for a project."""
    logger.info(
        f"Executing get_issue_priorities for project {project_id}, session {session_id[:8]}..."
    )
    taiga_client_wrapper = _get_authenticated_client(session_id)  # Use wrapper variable name
    try:
        # Use pytaigaclient syntax: client.resource.list(project_id=...)
        # Update resource name: priorities -> issue_priorities
        priorities = taiga_client_wrapper.api.issue_priorities.list(project_id=project_id)
        return priorities  # Return directly
    except TaigaException as e:
        logger.error(
            f"Taiga API error getting issue priorities for project {project_id}: {e}",
            exc_info=False,
        )
        raise e
    except Exception as e:
        logger.error(
            f"Unexpected error getting issue priorities for project {project_id}: {e}",
            exc_info=True,
        )
        raise RuntimeError(f"Server error getting issue priorities: {e}")


@mcp.tool(
    "get_issue_severities",
    description="Lists the available severities for issues within a specific project.",
)
def get_issue_severities(session_id: str, project_id: int) -> List[Dict[str, Any]]:
    """Retrieves the list of issue severities for a project."""
    logger.info(
        f"Executing get_issue_severities for project {project_id}, session {session_id[:8]}..."
    )
    taiga_client_wrapper = _get_authenticated_client(session_id)  # Use wrapper variable name
    try:
        # Use pytaigaclient syntax: client.resource.list(project_id=...)
        # Update resource name: severities -> issue_severities
        severities = taiga_client_wrapper.api.issue_severities.list(project_id=project_id)
        return severities  # Return directly
    except TaigaException as e:
        logger.error(
            f"Taiga API error getting issue severities for project {project_id}: {e}",
            exc_info=False,
        )
        raise e
    except Exception as e:
        logger.error(
            f"Unexpected error getting issue severities for project {project_id}: {e}",
            exc_info=True,
        )
        raise RuntimeError(f"Server error getting issue severities: {e}")


@mcp.tool(
    "get_issue_types", description="Lists the available types for issues within a specific project."
)
def get_issue_types(session_id: str, project_id: int) -> List[Dict[str, Any]]:
    """Retrieves the list of issue types for a project."""
    logger.info(f"Executing get_issue_types for project {project_id}, session {session_id[:8]}...")
    taiga_client_wrapper = _get_authenticated_client(session_id)  # Use wrapper variable name
    try:
        # Use pytaigaclient syntax: client.resource.list(project_id=...)
        types = taiga_client_wrapper.api.issue_types.list(project_id=project_id)
        return types  # Return directly
    except TaigaException as e:
        logger.error(
            f"Taiga API error getting issue types for project {project_id}: {e}", exc_info=False
        )
        raise e
    except Exception as e:
        logger.error(
            f"Unexpected error getting issue types for project {project_id}: {e}", exc_info=True
        )
        raise RuntimeError(f"Server error getting issue types: {e}")


# --- Epic Tools ---


@mcp.tool("list_epics", description="Lists epics within a specific project, optionally filtered.")
def list_epics(session_id: str, project_id: int, **filters) -> EpicList:
    """Lists epics for a project. Optional filters like 'status', 'assigned_to' can be passed as keyword arguments."""
    logger.info(
        f"Executing list_epics for project {project_id}, session {session_id[:8]}, filters: {filters}"
    )
    taiga_client_wrapper = _get_authenticated_client(session_id)  # Use wrapper variable name
    try:
        # Use pytaigaclient syntax: client.resource.list(project_id=..., **filters)
        epics = taiga_client_wrapper.api.epics.list(project_id=project_id, **filters)
        return epics  # Return directly
    except TaigaException as e:
        logger.error(f"Taiga API error listing epics for project {project_id}: {e}", exc_info=False)
        raise e
    except Exception as e:
        logger.error(f"Unexpected error listing epics for project {project_id}: {e}", exc_info=True)
        raise RuntimeError(f"Server error listing epics: {e}")


@mcp.tool("create_epic", description="Creates a new epic within a project.")
def create_epic(session_id: str, project_id: int, subject: str, **kwargs) -> Dict[str, Any]:
    """Creates an epic. Requires project_id and subject. Optional fields (description, status_id, assigned_to_id, color, etc.) via kwargs."""
    logger.info(
        f"Executing create_epic '{subject}' in project {project_id}, session {session_id[:8]}..."
    )
    taiga_client_wrapper = _get_authenticated_client(session_id)  # Use wrapper variable name

    # Input validation
    try:
        project_id = validate_project_id(project_id)
        subject = validate_subject(subject)
        allowed_kwargs = get_allowed_kwargs_for_resource("epic")
        kwargs = validate_kwargs(kwargs, allowed_kwargs)
    except ValidationError as e:
        logger.warning(f"Input validation failed for create_epic: {e}")
        raise ValueError(str(e))

    try:
        # Use pytaigaclient syntax: client.resource.create(project=..., subject=..., **kwargs)
        epic = taiga_client_wrapper.api.epics.create(project=project_id, subject=subject, **kwargs)
        logger.info(f"Epic '{subject}' created successfully (ID: {epic.get('id', 'N/A')}).")
        return epic  # Return directly
    except TaigaException as e:
        logger.error(f"Taiga API error creating epic '{subject}': {e}", exc_info=False)
        raise e
    except Exception as e:
        logger.error(f"Unexpected error creating epic '{subject}': {e}", exc_info=True)
        raise RuntimeError(f"Server error creating epic: {e}")


@mcp.tool("get_epic", description="Gets detailed information about a specific epic by its ID.")
def get_epic(session_id: str, epic_id: int) -> Dict[str, Any]:
    """Retrieves epic details by ID."""
    logger.info(f"Executing get_epic ID {epic_id} for session {session_id[:8]}...")
    taiga_client_wrapper = _get_authenticated_client(session_id)  # Use wrapper variable name
    try:
        # Epics expects epic_id as a positional argument
        epic = taiga_client_wrapper.get_resource("epic", epic_id)
        return epic  # Return directly
    except TaigaException as e:
        logger.error(f"Taiga API error getting epic {epic_id}: {e}", exc_info=False)
        raise e
    except Exception as e:
        logger.error(f"Unexpected error getting epic {epic_id}: {e}", exc_info=True)
        raise RuntimeError(f"Server error getting epic: {e}")


@mcp.tool("update_epic", description="Updates details of an existing epic.")
def update_epic(session_id: str, epic_id: int, **kwargs) -> Dict[str, Any]:
    """Updates an epic. Pass fields to update as keyword arguments (e.g., subject, description, status_id, assigned_to, color)."""
    logger.info(
        f"Executing update_epic ID {epic_id} for session {session_id[:8]} with data: {kwargs}"
    )
    taiga_client_wrapper = _get_authenticated_client(session_id)  # Use wrapper variable name

    # Input validation
    try:
        epic_id = validate_epic_id(epic_id)
        allowed_kwargs = get_allowed_kwargs_for_resource("epic")
        kwargs = validate_kwargs(kwargs, allowed_kwargs)
    except ValidationError as e:
        logger.warning(f"Input validation failed for update_epic: {e}")
        raise ValueError(str(e))

    try:
        # Use pytaigaclient edit pattern for partial updates
        if not kwargs:
            logger.info(f"No fields provided for update on epic {epic_id}")
            return taiga_client_wrapper.get_resource("epic", epic_id)

        # Get current epic data to retrieve version
        current_epic = taiga_client_wrapper.get_resource("epic", epic_id)
        version = current_epic.get("version")
        if not version:
            raise ValueError(f"Could not determine version for epic {epic_id}")

        # Use edit method for partial updates with keyword arguments
        updated_epic = taiga_client_wrapper.api.epics.edit(
            epic_id=epic_id, version=version, **kwargs
        )
        logger.info(f"Epic {epic_id} update request sent.")
        return updated_epic
    except TaigaException as e:
        logger.error(f"Taiga API error updating epic {epic_id}: {e}", exc_info=False)
        raise e
    except Exception as e:
        logger.error(f"Unexpected error updating epic {epic_id}: {e}", exc_info=True)
        raise RuntimeError(f"Server error updating epic: {e}")


@mcp.tool("delete_epic", description="Deletes an epic by its ID.")
def delete_epic(session_id: str, epic_id: int) -> DeleteResponse:
    """Deletes an epic by ID."""
    logger.warning(f"Executing delete_epic ID {epic_id} for session {session_id[:8]}...")
    taiga_client_wrapper = _get_authenticated_client(session_id)  # Use wrapper variable name

    # Input validation
    try:
        epic_id = validate_epic_id(epic_id)
    except ValidationError as e:
        logger.warning(f"Input validation failed for delete_epic: {e}")
        raise ValueError(str(e))

    try:
        # Use pytaigaclient syntax: client.resource.delete(id=...)
        taiga_client_wrapper.api.epics.delete(id=epic_id)
        logger.info(f"Epic {epic_id} deleted successfully.")
        return {"status": "deleted", "epic_id": epic_id}
    except TaigaException as e:
        logger.error(f"Taiga API error deleting epic {epic_id}: {e}", exc_info=False)
        raise e
    except Exception as e:
        logger.error(f"Unexpected error deleting epic {epic_id}: {e}", exc_info=True)
        raise RuntimeError(f"Server error deleting epic: {e}")


@mcp.tool("assign_epic_to_user", description="Assigns a specific epic to a specific user.")
def assign_epic_to_user(session_id: str, epic_id: int, user_id: int) -> Dict[str, Any]:
    """Assigns an epic to a user."""
    logger.info(
        f"Executing assign_epic_to_user: Epic {epic_id} -> User {user_id}, session {session_id[:8]}..."
    )
    return _assign_resource_to_user(session_id, "epic", epic_id, user_id)


@mcp.tool(
    "unassign_epic_from_user", description="Unassigns a specific epic (sets assigned user to null)."
)
def unassign_epic_from_user(session_id: str, epic_id: int) -> Dict[str, Any]:
    """Unassigns an epic."""
    logger.info(f"Executing unassign_epic_from_user: Epic {epic_id}, session {session_id[:8]}...")
    return _unassign_resource_from_user(session_id, "epic", epic_id)


# --- Milestone (Sprint) Tools ---


@mcp.tool("list_milestones", description="Lists milestones (sprints) within a specific project.")
def list_milestones(session_id: str, project_id: int) -> MilestoneList:
    """Lists milestones for a project."""
    logger.info(f"Executing list_milestones for project {project_id}, session {session_id[:8]}...")
    taiga_client_wrapper = _get_authenticated_client(session_id)  # Use wrapper variable name
    try:
        # Use pytaigaclient syntax: client.resource.list(project_id=...)
        milestones = taiga_client_wrapper.api.milestones.list(project_id=project_id)
        return milestones  # Return directly
    except TaigaException as e:
        logger.error(
            f"Taiga API error listing milestones for project {project_id}: {e}", exc_info=False
        )
        raise e
    except Exception as e:
        logger.error(
            f"Unexpected error listing milestones for project {project_id}: {e}", exc_info=True
        )
        raise RuntimeError(f"Server error listing milestones: {e}")


@mcp.tool("create_milestone", description="Creates a new milestone (sprint) within a project.")
def create_milestone(
    session_id: str, project_id: int, name: str, estimated_start: str, estimated_finish: str
) -> Dict[str, Any]:
    """Creates a milestone. Requires project_id, name, estimated_start (YYYY-MM-DD), and estimated_finish (YYYY-MM-DD)."""
    logger.info(
        f"Executing create_milestone '{name}' in project {project_id}, session {session_id[:8]}..."
    )
    taiga_client_wrapper = _get_authenticated_client(session_id)  # Use wrapper variable name
    if not all([name, estimated_start, estimated_finish]):
        raise ValueError("Milestone requires name, estimated_start, and estimated_finish.")
    try:
        # Use pytaigaclient syntax: client.resource.create(...)
        milestone = taiga_client_wrapper.api.milestones.create(
            project=project_id,  # Changed project_id to project
            name=name,
            estimated_start=estimated_start,
            estimated_finish=estimated_finish,
        )
        logger.info(f"Milestone '{name}' created successfully (ID: {milestone.get('id', 'N/A')}).")
        return milestone  # Return directly
    except TaigaException as e:
        logger.error(f"Taiga API error creating milestone '{name}': {e}", exc_info=False)
        raise e
    except Exception as e:
        logger.error(f"Unexpected error creating milestone '{name}': {e}", exc_info=True)
        raise RuntimeError(f"Server error creating milestone: {e}")


@mcp.tool(
    "get_milestone", description="Gets detailed information about a specific milestone by its ID."
)
def get_milestone(session_id: str, milestone_id: int) -> Dict[str, Any]:
    """Retrieves milestone details by ID."""
    logger.info(f"Executing get_milestone ID {milestone_id} for session {session_id[:8]}...")
    taiga_client_wrapper = _get_authenticated_client(session_id)  # Use wrapper variable name
    try:
        # Milestones expects milestone_id as a positional argument
        milestone = taiga_client_wrapper.get_resource("milestone", milestone_id)
        return milestone  # Return directly
    except TaigaException as e:
        logger.error(f"Taiga API error getting milestone {milestone_id}: {e}", exc_info=False)
        raise e
    except Exception as e:
        logger.error(f"Unexpected error getting milestone {milestone_id}: {e}", exc_info=True)
        raise RuntimeError(f"Server error getting milestone: {e}")


@mcp.tool("update_milestone", description="Updates details of an existing milestone.")
def update_milestone(session_id: str, milestone_id: int, **kwargs) -> Dict[str, Any]:
    """Updates a milestone. Pass fields to update as kwargs (e.g., name, estimated_start, estimated_finish)."""
    logger.info(
        f"Executing update_milestone ID {milestone_id} for session {session_id[:8]} with data: {kwargs}"
    )
    taiga_client_wrapper = _get_authenticated_client(session_id)  # Use wrapper variable name
    try:
        # Use pytaigaclient edit pattern for partial updates
        if not kwargs:
            logger.info(f"No fields provided for update on milestone {milestone_id}")
            return taiga_client_wrapper.get_resource("milestone", milestone_id)

        # Get current milestone data to retrieve version
        current_milestone = taiga_client_wrapper.get_resource("milestone", milestone_id)
        version = current_milestone.get("version")
        if not version:
            raise ValueError(f"Could not determine version for milestone {milestone_id}")

        # Use edit method for partial updates with keyword arguments
        updated_milestone = taiga_client_wrapper.api.milestones.edit(
            milestone_id=milestone_id, version=version, **kwargs
        )
        logger.info(f"Milestone {milestone_id} update request sent.")
        return updated_milestone
    except TaigaException as e:
        logger.error(f"Taiga API error updating milestone {milestone_id}: {e}", exc_info=False)
        raise e
    except Exception as e:
        logger.error(f"Unexpected error updating milestone {milestone_id}: {e}", exc_info=True)
        raise RuntimeError(f"Server error updating milestone: {e}")


@mcp.tool("delete_milestone", description="Deletes a milestone by its ID.")
def delete_milestone(session_id: str, milestone_id: int) -> DeleteResponse:
    """Deletes a milestone by ID."""
    logger.warning(f"Executing delete_milestone ID {milestone_id} for session {session_id[:8]}...")
    taiga_client_wrapper = _get_authenticated_client(session_id)  # Use wrapper variable name

    # Input validation
    try:
        milestone_id = validate_milestone_id(milestone_id)
    except ValidationError as e:
        logger.warning(f"Input validation failed for delete_milestone: {e}")
        raise ValueError(str(e))

    try:
        # Use pytaigaclient syntax: client.resource.delete(id=...)
        taiga_client_wrapper.api.milestones.delete(id=milestone_id)
        logger.info(f"Milestone {milestone_id} deleted successfully.")
        return {"status": "deleted", "milestone_id": milestone_id}
    except TaigaException as e:
        logger.error(f"Taiga API error deleting milestone {milestone_id}: {e}", exc_info=False)
        raise e
    except Exception as e:
        logger.error(f"Unexpected error deleting milestone {milestone_id}: {e}", exc_info=True)
        raise RuntimeError(f"Server error deleting milestone: {e}")


# --- User Management Tools ---


@mcp.tool("get_project_members", description="Lists members of a specific project.")
def get_project_members(session_id: str, project_id: int) -> MemberList:
    """Retrieves the list of members for a project."""
    logger.info(
        f"Executing get_project_members for project {project_id}, session {session_id[:8]}..."
    )
    taiga_client_wrapper = _get_authenticated_client(session_id)  # Use wrapper variable name
    try:
        # Use pytaigaclient memberships resource list method
        members = taiga_client_wrapper.api.memberships.list(project_id=project_id)
        return members  # Return directly
    except TaigaException as e:
        logger.error(
            f"Taiga API error getting members for project {project_id}: {e}", exc_info=False
        )
        raise e
    except Exception as e:
        logger.error(
            f"Unexpected error getting members for project {project_id}: {e}", exc_info=True
        )
        raise RuntimeError(f"Server error getting project members: {e}")


@mcp.tool(
    "invite_project_user", description="Invites a user to a project by email with a specific role."
)
def invite_project_user(
    session_id: str, project_id: int, email: str, role_id: int
) -> Dict[str, Any]:
    """Invites a user via email to join the project with the specified role ID."""
    logger.info(
        f"Executing invite_project_user {email} to project {project_id} (role {role_id}), session {session_id[:8]}..."
    )
    taiga_client_wrapper = _get_authenticated_client(session_id)  # Use wrapper variable name
    if not email:
        raise ValueError("Email cannot be empty.")
    try:
        # Use pytaigaclient memberships resource invite method
        # Check pytaigaclient signature for param names (project, email, role_id)
        invitation_result = taiga_client_wrapper.api.memberships.invite(
            project=project_id, email=email, role_id=role_id  # Changed project_id to project
        )
        logger.info(f"Invitation request sent to {email} for project {project_id}.")
        # Return the result from the invite call (might be dict or status)
        return (
            invitation_result
            if isinstance(invitation_result, dict)
            else {"status": "invited", "email": email, "details": invitation_result}
        )
    except TaigaException as e:
        logger.error(
            f"Taiga API error inviting user {email} to project {project_id}: {e}", exc_info=False
        )
        raise e
    except Exception as e:
        logger.error(
            f"Unexpected error inviting user {email} to project {project_id}: {e}", exc_info=True
        )
        raise RuntimeError(f"Server error inviting user: {e}")


# --- Wiki Tools ---


@mcp.tool("list_wiki_pages", description="Lists wiki pages within a specific project.")
def list_wiki_pages(session_id: str, project_id: int) -> WikiPageList:
    """Lists wiki pages for a project."""
    logger.info(f"Executing list_wiki_pages for project {project_id}, session {session_id[:8]}...")
    taiga_client_wrapper = _get_authenticated_client(session_id)  # Use wrapper variable name
    try:
        # Use pytaigaclient syntax: client.wiki.list(project_id=...)
        pages = taiga_client_wrapper.api.wiki.list(project_id=project_id)
        return pages  # Return directly
    except TaigaException as e:
        logger.error(
            f"Taiga API error listing wiki pages for project {project_id}: {e}", exc_info=False
        )
        raise e
    except Exception as e:
        logger.error(
            f"Unexpected error listing wiki pages for project {project_id}: {e}", exc_info=True
        )
        raise RuntimeError(f"Server error listing wiki pages: {e}")


@mcp.tool("get_wiki_page", description="Gets a specific wiki page by its ID.")
def get_wiki_page(session_id: str, wiki_page_id: int) -> WikiPageResponse:
    """Retrieves wiki page details by ID."""
    logger.info(f"Executing get_wiki_page ID {wiki_page_id} for session {session_id[:8]}...")
    taiga_client_wrapper = _get_authenticated_client(session_id)  # Use wrapper variable name
    try:
        # Wiki expects wiki_page_id as a positional argument
        page = taiga_client_wrapper.get_resource("wiki_page", wiki_page_id)
        return page  # Return directly
    except TaigaException as e:
        logger.error(f"Taiga API error getting wiki page {wiki_page_id}: {e}", exc_info=False)
        raise e
    except Exception as e:
        logger.error(f"Unexpected error getting wiki page {wiki_page_id}: {e}", exc_info=True)
        raise RuntimeError(f"Server error getting wiki page: {e}")


# --- Session Management Tools ---


@mcp.tool("logout", description="Invalidates the current session_id.")
def logout(session_id: str) -> LogoutResponse:
    """
    Terminate an authenticated session.

    Invalidates the provided session_id, preventing further use of this session for API calls.
    This should be called when the client is done with Taiga operations to clean up resources.

    Args:
        session_id: The UUID session identifier returned from login.

    Returns:
        LogoutResponse: Dictionary containing:
            - status: "logged_out" if successful, "session_not_found" if already invalid
            - session_id: The session_id that was logged out

    Example:
        >>> result = logout(session_id)
        >>> print(result["status"])  # "logged_out"
    """
    logger.info(f"Executing logout for session: {truncate_session_id(session_id)}")

    session_info = active_sessions.get(session_id)
    if session_info:
        username = session_info.username
        _cleanup_session(session_id)
        logger.info(f"Logout successful: {truncate_session_id(session_id)}, user: {username}")
        return {"status": "logged_out", "session_id": session_id}
    else:
        logger.warning(
            f"Logout attempted for non-existent session: {truncate_session_id(session_id)}"
        )
        return {"status": "session_not_found", "session_id": session_id}


@mcp.tool(
    "session_status", description="Checks if the provided session_id is currently active and valid."
)
def session_status(session_id: str) -> SessionStatusResponse:
    """
    Check the current status of an authenticated session.

    Validates whether a session_id is still active and the underlying Taiga token is valid.
    Automatically cleans up expired or invalid sessions. Returns detailed session metadata
    including creation time, last access time, and expiration time.

    Args:
        session_id: The UUID session identifier returned from login.

    Returns:
        SessionStatusResponse: Dictionary containing:
            - status: "active", "inactive", or "error"
            - session_id: The session_id being checked
            - username: (optional) The authenticated username if status is "active"
            - created_at: (optional) ISO timestamp when session was created
            - last_accessed: (optional) ISO timestamp of last session access
            - expires_at: (optional) ISO timestamp when session expires
            - time_until_expiry_seconds: (optional) Seconds until expiration
            - reason: (optional) Reason for inactive/error status (e.g., "token_invalid", "not_found")

    Example:
        >>> result = session_status(session_id)
        >>> if result["status"] == "active":
        ...     print(f"Logged in as: {result['username']}")
        ...     print(f"Expires at: {result['expires_at']}")
        ... else:
        ...     print("Session expired, please login again")
    """
    logger.debug(f"Checking status for session: {truncate_session_id(session_id)}")

    session_info = active_sessions.get(session_id)

    # Session not found
    if not session_info:
        return {"status": "inactive", "session_id": session_id, "reason": "not_found"}

    # Check if expired
    if session_info.is_expired():
        _cleanup_session(session_id)
        return {
            "status": "inactive",
            "session_id": session_id,
            "reason": "expired",
            "username": session_info.username,
        }

    # Check if authenticated
    if not session_info.client.is_authenticated:
        _cleanup_session(session_id)
        return {
            "status": "inactive",
            "session_id": session_id,
            "reason": "token_invalid",
            "username": session_info.username,
        }

    # Active session - verify with API
    try:
        me = session_info.client.api.users.me()
        username = me.get("username", session_info.username)

        return {
            "status": "active",
            "session_id": session_id,
            "username": username,
            "created_at": session_info.created_at.isoformat(),
            "last_accessed": session_info.last_accessed.isoformat(),
            "expires_at": session_info.expires_at.isoformat(),
            "time_until_expiry_seconds": int(session_info.time_until_expiry().total_seconds()),
        }
    except Exception as e:
        logger.error(f"Error checking session status: {e}", exc_info=True)
        _cleanup_session(session_id)
        return {"status": "error", "session_id": session_id, "reason": f"api_error: {str(e)}"}


# --- Run the server ---
if __name__ == "__main__":
    import sys

    # Determine transport mode from environment variable or command-line args
    transport = os.getenv("TAIGA_TRANSPORT", "stdio").lower()

    # Support --sse command-line flag for backward compatibility
    if "--sse" in sys.argv:
        transport = "sse"

    logger.info(f"Starting MCP server with transport: {transport}")
    mcp.run(transport=transport)
