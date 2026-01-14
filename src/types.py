"""
Type definitions for MCP Taiga Bridge responses.

Provides TypedDict classes for all MCP tool return types to enable
strict type checking and improved IDE support.
"""

import os
import sys
from collections import deque
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import TYPE_CHECKING, List, Optional

if TYPE_CHECKING:
    from src.taiga_client import TaigaClientWrapper

# For Python 3.10 compatibility, use typing_extensions for TypedDict and NotRequired
if sys.version_info >= (3, 12):
    from typing import NotRequired, TypedDict
else:
    from typing_extensions import NotRequired, TypedDict


# --- Authentication & Session Response Types ---


class LoginResponse(TypedDict):
    """Response from login tool."""

    session_id: str


class LogoutResponse(TypedDict):
    """Response from logout tool."""

    status: str
    session_id: str


class _SessionStatusRequired(TypedDict):
    """Required fields for session status response."""

    status: str
    session_id: str


class SessionStatusResponse(_SessionStatusRequired, total=False):
    """Response from session_status tool."""

    username: str
    reason: str
    created_at: str
    last_accessed: str
    expires_at: str
    time_until_expiry_seconds: int


# --- Status/Metadata Response Types ---


class StatusResponse(TypedDict):
    """Response for status objects (user story status, task status, etc)."""

    id: int
    name: str
    color: NotRequired[str]
    slug: NotRequired[str]
    order: NotRequired[int]


class PriorityResponse(TypedDict):
    """Response for issue priority objects."""

    id: int
    name: str
    color: NotRequired[str]
    order: NotRequired[int]


class SeverityResponse(TypedDict):
    """Response for issue severity objects."""

    id: int
    name: str
    color: NotRequired[str]
    order: NotRequired[int]


class IssueTypeResponse(TypedDict):
    """Response for issue type objects."""

    id: int
    name: str
    color: NotRequired[str]
    order: NotRequired[int]


# --- Standard Delete Response Type ---


class DeleteResponse(TypedDict, total=False):
    """Response from delete operations."""

    status: str
    project_id: int
    epic_id: int
    user_story_id: int
    task_id: int
    issue_id: int
    milestone_id: int


# --- Project Response Types ---


class ProjectResponse(TypedDict):
    """Response for project objects."""

    id: int
    name: str
    slug: str
    description: NotRequired[str]
    version: NotRequired[int]
    created_date: NotRequired[str]
    modified_date: NotRequired[str]
    owner: NotRequired[int]
    is_private: NotRequired[bool]
    default_owner_role: NotRequired[int]
    tags: NotRequired[List[str]]
    members: NotRequired[List[int]]


# --- User Story Response Types ---


class UserStoryResponse(TypedDict):
    """Response for user story objects."""

    id: int
    subject: str
    description: NotRequired[str]
    status: NotRequired[int]
    project: NotRequired[int]
    assigned_to: NotRequired[Optional[int]]
    version: NotRequired[int]
    created_date: NotRequired[str]
    modified_date: NotRequired[str]
    owner: NotRequired[int]
    epic: NotRequired[Optional[int]]
    milestone: NotRequired[Optional[int]]
    tags: NotRequired[List[str]]


# --- Task Response Types ---


class TaskResponse(TypedDict):
    """Response for task objects."""

    id: int
    subject: str
    description: NotRequired[str]
    status: NotRequired[int]
    project: NotRequired[int]
    user_story: NotRequired[Optional[int]]
    assigned_to: NotRequired[Optional[int]]
    version: NotRequired[int]
    created_date: NotRequired[str]
    modified_date: NotRequired[str]
    owner: NotRequired[int]
    tags: NotRequired[List[str]]


# --- Issue Response Types ---


class IssueResponse(TypedDict):
    """Response for issue objects."""

    id: int
    subject: str
    description: NotRequired[str]
    status: NotRequired[int]
    priority: NotRequired[int]
    severity: NotRequired[int]
    type: NotRequired[int]
    project: NotRequired[int]
    assigned_to: NotRequired[Optional[int]]
    version: NotRequired[int]
    created_date: NotRequired[str]
    modified_date: NotRequired[str]
    owner: NotRequired[int]
    tags: NotRequired[List[str]]


# --- Epic Response Types ---


class EpicResponse(TypedDict):
    """Response for epic objects."""

    id: int
    subject: str
    description: NotRequired[str]
    status: NotRequired[int]
    project: NotRequired[int]
    assigned_to: NotRequired[Optional[int]]
    version: NotRequired[int]
    created_date: NotRequired[str]
    modified_date: NotRequired[str]
    owner: NotRequired[int]
    color: NotRequired[str]
    user_stories: NotRequired[List[int]]


# --- Milestone Response Types ---


class MilestoneResponse(TypedDict):
    """Response for milestone (sprint) objects."""

    id: int
    name: str
    slug: NotRequired[str]
    project: NotRequired[int]
    estimated_start: NotRequired[str]
    estimated_finish: NotRequired[str]
    version: NotRequired[int]
    created_date: NotRequired[str]
    modified_date: NotRequired[str]
    owner: NotRequired[int]
    is_closed: NotRequired[bool]


# --- User/Member Response Types ---


class MemberResponse(TypedDict):
    """Response for project member objects."""

    id: int
    user: NotRequired[int]
    username: NotRequired[str]
    email: NotRequired[str]
    full_name: NotRequired[str]
    role: NotRequired[int]


class InviteResponse(TypedDict):
    """Response from invite_project_user tool."""

    id: int
    project: int
    email: str
    role: int


# --- Wiki Response Types ---


class WikiPageResponse(TypedDict):
    """Response for wiki page objects."""

    id: int
    slug: str
    title: NotRequired[str]
    content: NotRequired[str]
    project: NotRequired[int]
    version: NotRequired[int]
    created_date: NotRequired[str]
    modified_date: NotRequired[str]
    owner: NotRequired[int]


# --- Collection Response Types ---
# These are type aliases for common list return patterns

ProjectList = List[ProjectResponse]
UserStoryList = List[UserStoryResponse]
TaskList = List[TaskResponse]
IssueList = List[IssueResponse]
EpicList = List[EpicResponse]
MilestoneList = List[MilestoneResponse]
MemberList = List[MemberResponse]
WikiPageList = List[WikiPageResponse]
StatusList = List[StatusResponse]
PriorityList = List[PriorityResponse]
SeverityList = List[SeverityResponse]
IssueTypeList = List[IssueTypeResponse]


# --- Session Management Types ---


@dataclass
class SessionInfo:
    """
    Session metadata and client wrapper for authenticated sessions.

    Tracks session lifecycle with TTL enforcement and last access timestamps.
    Used to store session information with automatic expiration based on
    SESSION_EXPIRY environment variable (default: 8 hours).

    Attributes:
        session_id: UUID string identifying the session
        client: Authenticated TaigaClientWrapper instance
        username: Username of authenticated user
        created_at: Timestamp when session was created
        last_accessed: Timestamp of most recent session access
        expires_at: Timestamp when session expires
    """

    session_id: str
    client: "TaigaClientWrapper"  # Avoid circular import
    username: str
    created_at: datetime = field(default_factory=datetime.utcnow)
    last_accessed: datetime = field(default_factory=datetime.utcnow)
    expires_at: Optional[datetime] = None

    def __post_init__(self):
        """Set expiration time based on SESSION_EXPIRY config."""
        if self.expires_at is None:
            ttl_seconds = int(os.getenv("SESSION_EXPIRY", "28800"))
            if ttl_seconds <= 0:
                ttl_seconds = 28800  # Fallback to 8 hours
            self.expires_at = self.created_at + timedelta(seconds=ttl_seconds)

    def is_expired(self) -> bool:
        """Check if session has expired based on TTL."""
        if self.expires_at is None:
            return False
        return datetime.utcnow() >= self.expires_at

    def update_last_accessed(self) -> None:
        """Update last accessed timestamp to current time."""
        self.last_accessed = datetime.utcnow()

    def time_until_expiry(self) -> timedelta:
        """Calculate time remaining until expiration."""
        if self.expires_at is None:
            return timedelta(seconds=0)
        return self.expires_at - datetime.utcnow()


# --- Rate Limiting Types ---


@dataclass
class LoginAttempt:
    """
    Track individual login attempt for rate limiting.

    Attributes:
        timestamp: When the attempt occurred
        username: Username that attempted login
        success: Whether login was successful
    """

    timestamp: datetime
    username: str
    success: bool


@dataclass
class RateLimitInfo:
    """
    Rate limit tracking per user with sliding window.

    Tracks recent login attempts in a deque (sliding window) and enforces
    lockout periods after threshold exceeded.

    Attributes:
        attempts: Queue of recent LoginAttempt objects (sliding window)
        locked_until: Timestamp when lockout expires (None if not locked)
    """

    attempts: deque = field(default_factory=deque)
    locked_until: Optional[datetime] = None

    def is_locked_out(self) -> bool:
        """Check if user is currently locked out."""
        if self.locked_until is None:
            return False
        return datetime.utcnow() < self.locked_until

    def remaining_lockout_time(self) -> int:
        """Return seconds remaining in lockout period."""
        if not self.is_locked_out():
            return 0
        # Type guard: is_locked_out() ensures locked_until is not None
        assert self.locked_until is not None
        return int((self.locked_until - datetime.utcnow()).total_seconds())
