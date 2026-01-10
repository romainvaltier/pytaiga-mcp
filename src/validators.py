"""
Input Validation Module

Provides validation functions for all user inputs to ensure data integrity
and prevent invalid data from reaching the Taiga API.
"""

import re
from typing import Any, Dict

# Regular expression for email validation (RFC 5322 simplified)
EMAIL_REGEX = re.compile(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")

# Maximum lengths for common fields
MAX_LENGTHS = {
    "subject": 500,
    "description": 10000,
    "name": 255,
    "slug": 255,
    "default_owner_role": 100,
    "comment": 5000,
}

# Allowed kwargs fields per resource type
ALLOWED_KWARGS = {
    "project": {"description", "is_private", "default_owner_role", "tags"},
    "epic": {"description", "color"},
    "user_story": {"description", "assigned_to", "sprint", "status", "priority", "tags"},
    "task": {"description", "assigned_to", "user_story", "status", "priority", "tags"},
    "issue": {"description", "assigned_to", "status", "priority", "severity", "type", "tags"},
    "milestone": {"name", "estimated_start", "estimated_finish"},
}


class ValidationError(ValueError):
    """Raised when input validation fails."""

    pass


def validate_positive_integer(value: Any, field_name: str) -> int:
    """
    Validate that a value is a positive integer.

    Args:
        value: The value to validate
        field_name: Name of the field for error messages

    Returns:
        The validated integer value

    Raises:
        ValidationError: If value is not a positive integer
    """
    # Reject floats explicitly
    if isinstance(value, float):
        raise ValidationError(f"{field_name} must be an integer, got float")

    try:
        int_value = int(value)
    except (TypeError, ValueError):
        raise ValidationError(f"{field_name} must be an integer, got {type(value).__name__}")

    if int_value <= 0:
        raise ValidationError(f"{field_name} must be a positive integer, got {int_value}")

    return int_value


def validate_string_length(value: str, field_name: str, max_length: int = 1000) -> str:
    """
    Validate that a string is not empty and doesn't exceed max length.

    Args:
        value: The string to validate
        field_name: Name of the field for error messages
        max_length: Maximum allowed length

    Returns:
        The validated string

    Raises:
        ValidationError: If string is invalid
    """
    if not isinstance(value, str):
        raise ValidationError(f"{field_name} must be a string, got {type(value).__name__}")

    if not value.strip():
        raise ValidationError(f"{field_name} cannot be empty")

    if len(value) > max_length:
        raise ValidationError(f"{field_name} exceeds maximum length of {max_length} characters")

    return value


def validate_email(email: str) -> str:
    """
    Validate email address format.

    Args:
        email: Email address to validate

    Returns:
        The validated email

    Raises:
        ValidationError: If email format is invalid
    """
    if not isinstance(email, str):
        raise ValidationError(f"Email must be a string, got {type(email).__name__}")

    email = email.strip()

    if not email:
        raise ValidationError("Email cannot be empty")

    if not EMAIL_REGEX.match(email):
        raise ValidationError(f"Invalid email format: {email}")

    if len(email) > 254:  # RFC 5321
        raise ValidationError("Email exceeds maximum length of 254 characters")

    return email


def validate_project_id(project_id: Any) -> int:
    """Validate project ID."""
    return validate_positive_integer(project_id, "project_id")


def validate_user_id(user_id: Any) -> int:
    """Validate user ID."""
    return validate_positive_integer(user_id, "user_id")


def validate_task_id(task_id: Any) -> int:
    """Validate task ID."""
    return validate_positive_integer(task_id, "task_id")


def validate_issue_id(issue_id: Any) -> int:
    """Validate issue ID."""
    return validate_positive_integer(issue_id, "issue_id")


def validate_epic_id(epic_id: Any) -> int:
    """Validate epic ID."""
    return validate_positive_integer(epic_id, "epic_id")


def validate_user_story_id(user_story_id: Any) -> int:
    """Validate user story ID."""
    return validate_positive_integer(user_story_id, "user_story_id")


def validate_milestone_id(milestone_id: Any) -> int:
    """Validate milestone/sprint ID."""
    return validate_positive_integer(milestone_id, "milestone_id")


def validate_subject(subject: str) -> str:
    """Validate subject/title field."""
    max_len = MAX_LENGTHS.get("subject", 500)
    return validate_string_length(subject, "subject", max_len)


def validate_description(description: str) -> str:
    """Validate description field."""
    if description is None:
        return None
    max_len = MAX_LENGTHS.get("description", 10000)
    return validate_string_length(description, "description", max_len)


def validate_name(name: str) -> str:
    """Validate name field."""
    max_len = MAX_LENGTHS.get("name", 255)
    return validate_string_length(name, "name", max_len)


def validate_slug(slug: str) -> str:
    """Validate slug field."""
    max_len = MAX_LENGTHS.get("slug", 255)
    slug = validate_string_length(slug, "slug", max_len)

    # Slug should only contain alphanumeric and hyphens
    if not re.match(r"^[a-z0-9\-]+$", slug.lower()):
        raise ValidationError(f"Slug must contain only alphanumeric characters and hyphens: {slug}")

    return slug


def validate_kwargs(kwargs: Dict[str, Any], allowed_fields: set) -> Dict[str, Any]:
    """
    Validate and whitelist kwargs for a resource.

    Args:
        kwargs: Dictionary of keyword arguments
        allowed_fields: Set of allowed field names

    Returns:
        The validated kwargs dictionary

    Raises:
        ValidationError: If invalid fields are present
    """
    if kwargs is None:
        return {}

    if not isinstance(kwargs, dict):
        raise ValidationError(f"kwargs must be a dictionary, got {type(kwargs).__name__}")

    # Check for invalid fields
    invalid_fields = set(kwargs.keys()) - allowed_fields
    if invalid_fields:
        raise ValidationError(
            f"Invalid fields for this resource: {invalid_fields}. "
            f"Allowed fields: {allowed_fields}"
        )

    return kwargs


def get_allowed_kwargs_for_resource(resource_type: str) -> set:
    """
    Get the set of allowed kwargs for a resource type.

    Args:
        resource_type: Type of resource (project, epic, user_story, task, issue, milestone)

    Returns:
        Set of allowed field names

    Raises:
        ValidationError: If resource type is unknown
    """
    if resource_type not in ALLOWED_KWARGS:
        raise ValidationError(f"Unknown resource type: {resource_type}")

    return ALLOWED_KWARGS[resource_type]
