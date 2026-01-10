"""
Unit tests for the validators module.
Tests all validation functions to ensure proper input validation.
"""

import pytest

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
    validate_slug,
    validate_string_length,
    validate_subject,
    validate_task_id,
    validate_user_id,
    validate_user_story_id,
)


class TestPositiveIntegerValidation:
    """Test cases for validate_positive_integer"""

    def test_valid_positive_integer(self):
        """Should accept positive integers"""
        assert validate_positive_integer(1, "test_field") == 1
        assert validate_positive_integer(100, "test_field") == 100
        assert validate_positive_integer(999999, "test_field") == 999999

    def test_valid_string_integer(self):
        """Should convert string integers to int"""
        assert validate_positive_integer("42", "test_field") == 42

    def test_zero_rejected(self):
        """Should reject zero"""
        with pytest.raises(ValidationError, match="must be a positive integer"):
            validate_positive_integer(0, "test_field")

    def test_negative_integer_rejected(self):
        """Should reject negative integers"""
        with pytest.raises(ValidationError, match="must be a positive integer"):
            validate_positive_integer(-5, "test_field")

    def test_float_rejected(self):
        """Should reject non-integer floats"""
        with pytest.raises(ValidationError, match="must be an integer"):
            validate_positive_integer(3.14, "test_field")

    def test_invalid_string_rejected(self):
        """Should reject non-numeric strings"""
        with pytest.raises(ValidationError, match="must be an integer"):
            validate_positive_integer("abc", "test_field")

    def test_none_rejected(self):
        """Should reject None"""
        with pytest.raises(ValidationError, match="must be an integer"):
            validate_positive_integer(None, "test_field")


class TestStringLengthValidation:
    """Test cases for validate_string_length"""

    def test_valid_string(self):
        """Should accept valid strings"""
        assert validate_string_length("hello", "test_field") == "hello"
        assert validate_string_length("a", "test_field", max_length=10) == "a"

    def test_empty_string_rejected(self):
        """Should reject empty strings"""
        with pytest.raises(ValidationError, match="cannot be empty"):
            validate_string_length("", "test_field")

    def test_whitespace_only_rejected(self):
        """Should reject whitespace-only strings"""
        with pytest.raises(ValidationError, match="cannot be empty"):
            validate_string_length("   ", "test_field")

    def test_exceeds_max_length(self):
        """Should reject strings exceeding max length"""
        with pytest.raises(ValidationError, match="exceeds maximum length"):
            validate_string_length("a" * 1001, "test_field", max_length=1000)

    def test_non_string_rejected(self):
        """Should reject non-string types"""
        with pytest.raises(ValidationError, match="must be a string"):
            validate_string_length(123, "test_field")

    def test_at_max_length(self):
        """Should accept strings at max length"""
        s = "a" * 100
        assert validate_string_length(s, "test_field", max_length=100) == s


class TestEmailValidation:
    """Test cases for validate_email"""

    def test_valid_email(self):
        """Should accept valid email addresses"""
        assert validate_email("user@example.com") == "user@example.com"
        assert validate_email("john.doe+tag@domain.co.uk") == "john.doe+tag@domain.co.uk"

    def test_empty_email_rejected(self):
        """Should reject empty email"""
        with pytest.raises(ValidationError, match="cannot be empty"):
            validate_email("")

    def test_whitespace_only_rejected(self):
        """Should reject whitespace-only email"""
        with pytest.raises(ValidationError, match="cannot be empty"):
            validate_email("   ")

    def test_invalid_format_rejected(self):
        """Should reject invalid email formats"""
        invalid_emails = [
            "notanemail",
            "missing@domain",
            "@nodomain.com",
            "user@",
            "user name@example.com",
        ]
        for email in invalid_emails:
            with pytest.raises(ValidationError, match="Invalid email format"):
                validate_email(email)

    def test_email_too_long_rejected(self):
        """Should reject emails exceeding 254 characters"""
        long_email = "a" * 250 + "@example.com"
        with pytest.raises(ValidationError, match="exceeds maximum length"):
            validate_email(long_email)

    def test_non_string_rejected(self):
        """Should reject non-string types"""
        with pytest.raises(ValidationError, match="must be a string"):
            validate_email(123)

    def test_whitespace_trimmed(self):
        """Should trim whitespace from email"""
        assert validate_email("  user@example.com  ") == "user@example.com"


class TestIDValidation:
    """Test cases for ID validation functions"""

    def test_project_id_validation(self):
        """Should validate project ID"""
        assert validate_project_id(1) == 1
        with pytest.raises(ValidationError):
            validate_project_id(0)

    def test_user_id_validation(self):
        """Should validate user ID"""
        assert validate_user_id(42) == 42
        with pytest.raises(ValidationError):
            validate_user_id(-1)

    def test_task_id_validation(self):
        """Should validate task ID"""
        assert validate_task_id(100) == 100
        with pytest.raises(ValidationError):
            validate_task_id("invalid")

    def test_issue_id_validation(self):
        """Should validate issue ID"""
        assert validate_issue_id(50) == 50
        with pytest.raises(ValidationError):
            validate_issue_id(None)

    def test_epic_id_validation(self):
        """Should validate epic ID"""
        assert validate_epic_id(999) == 999
        with pytest.raises(ValidationError):
            validate_epic_id(0)

    def test_user_story_id_validation(self):
        """Should validate user story ID"""
        assert validate_user_story_id(200) == 200
        with pytest.raises(ValidationError):
            validate_user_story_id(-10)

    def test_milestone_id_validation(self):
        """Should validate milestone ID"""
        assert validate_milestone_id(75) == 75
        with pytest.raises(ValidationError):
            validate_milestone_id("abc")


class TestFieldValidation:
    """Test cases for field-specific validation functions"""

    def test_subject_validation(self):
        """Should validate subject field"""
        assert validate_subject("Valid Subject") == "Valid Subject"
        with pytest.raises(ValidationError):
            validate_subject("")
        with pytest.raises(ValidationError):
            validate_subject("a" * 501)

    def test_description_validation(self):
        """Should validate description field"""
        assert validate_description("Valid description") == "Valid description"
        assert validate_description(None) is None
        with pytest.raises(ValidationError):
            validate_description("")

    def test_name_validation(self):
        """Should validate name field"""
        assert validate_name("Project Name") == "Project Name"
        with pytest.raises(ValidationError):
            validate_name("")
        with pytest.raises(ValidationError):
            validate_name("a" * 256)

    def test_slug_validation(self):
        """Should validate slug field"""
        assert validate_slug("valid-slug") == "valid-slug"
        assert validate_slug("valid-slug-123") == "valid-slug-123"

        with pytest.raises(ValidationError):
            validate_slug("")

        with pytest.raises(ValidationError, match="alphanumeric characters and hyphens"):
            validate_slug("invalid_slug")

        with pytest.raises(ValidationError, match="alphanumeric characters and hyphens"):
            validate_slug("invalid slug")


class TestKwargsValidation:
    """Test cases for kwargs validation"""

    def test_valid_kwargs(self):
        """Should accept valid kwargs"""
        allowed = {"field1", "field2", "field3"}
        kwargs = {"field1": "value1", "field2": "value2"}
        result = validate_kwargs(kwargs, allowed)
        assert result == kwargs

    def test_none_kwargs(self):
        """Should handle None kwargs"""
        result = validate_kwargs(None, {"field1"})
        assert result == {}

    def test_empty_kwargs(self):
        """Should handle empty kwargs"""
        result = validate_kwargs({}, {"field1"})
        assert result == {}

    def test_invalid_field_rejected(self):
        """Should reject invalid fields"""
        allowed = {"field1", "field2"}
        kwargs = {"field1": "value", "invalid_field": "value"}
        with pytest.raises(ValidationError, match="Invalid fields"):
            validate_kwargs(kwargs, allowed)

    def test_non_dict_kwargs_rejected(self):
        """Should reject non-dict kwargs"""
        with pytest.raises(ValidationError, match="must be a dictionary"):
            validate_kwargs("not a dict", {"field1"})

    def test_multiple_invalid_fields(self):
        """Should report multiple invalid fields"""
        allowed = {"field1"}
        kwargs = {"field1": "value", "bad1": "value", "bad2": "value"}
        with pytest.raises(ValidationError, match="Invalid fields"):
            validate_kwargs(kwargs, allowed)


class TestResourceKwargsAllowed:
    """Test cases for get_allowed_kwargs_for_resource"""

    def test_project_kwargs(self):
        """Should return allowed kwargs for project"""
        allowed = get_allowed_kwargs_for_resource("project")
        assert "description" in allowed
        assert "is_private" in allowed

    def test_epic_kwargs(self):
        """Should return allowed kwargs for epic"""
        allowed = get_allowed_kwargs_for_resource("epic")
        assert "description" in allowed
        assert "color" in allowed

    def test_user_story_kwargs(self):
        """Should return allowed kwargs for user_story"""
        allowed = get_allowed_kwargs_for_resource("user_story")
        assert "description" in allowed
        assert "assigned_to" in allowed
        assert "priority" in allowed

    def test_task_kwargs(self):
        """Should return allowed kwargs for task"""
        allowed = get_allowed_kwargs_for_resource("task")
        assert "description" in allowed
        assert "status" in allowed

    def test_issue_kwargs(self):
        """Should return allowed kwargs for issue"""
        allowed = get_allowed_kwargs_for_resource("issue")
        assert "description" in allowed
        assert "severity" in allowed

    def test_milestone_kwargs(self):
        """Should return allowed kwargs for milestone"""
        allowed = get_allowed_kwargs_for_resource("milestone")
        assert "name" in allowed

    def test_unknown_resource_rejected(self):
        """Should reject unknown resource types"""
        with pytest.raises(ValidationError, match="Unknown resource type"):
            get_allowed_kwargs_for_resource("unknown_resource")


class TestValidationErrorMessages:
    """Test that validation errors have clear, helpful messages"""

    def test_error_messages_include_field_name(self):
        """Error messages should include the field name"""
        with pytest.raises(ValidationError, match="project_id"):
            validate_project_id("invalid")

    def test_error_messages_are_specific(self):
        """Error messages should be specific about what was wrong"""
        with pytest.raises(ValidationError, match="positive integer"):
            validate_project_id(-5)

    def test_email_error_message_helpful(self):
        """Email validation error should be helpful"""
        with pytest.raises(ValidationError, match="Invalid email format"):
            validate_email("not-an-email")
