"""
Type definitions for MCP Taiga Bridge responses.

Provides TypedDict classes for all MCP tool return types to enable
strict type checking and improved IDE support.
"""

from typing import List, Optional, TypedDict

try:
    from typing import NotRequired
except ImportError:
    # Python < 3.11
    from typing_extensions import NotRequired


# --- Authentication & Session Response Types ---


class LoginResponse(TypedDict):
    """Response from login tool."""

    session_id: str


class LogoutResponse(TypedDict):
    """Response from logout tool."""

    status: str
    session_id: str


class SessionStatusResponse(TypedDict):
    """Response from session_status tool."""

    status: str
    session_id: str
    username: NotRequired[str]
    reason: NotRequired[str]


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


class DeleteResponse(TypedDict):
    """Response from delete operations."""

    status: str


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
