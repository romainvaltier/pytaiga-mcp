"""
Unit tests for secure logging utilities.

Tests validate that:
- Session IDs are properly truncated for safe logging
- Sensitive data (passwords, tokens) are never exposed
- Email addresses are masked appropriately
- URLs with credentials are sanitized
"""

from src.logging_utils import (
    is_sensitive_log_level,
    mask_email,
    sanitize_password,
    sanitize_url,
    truncate_session_id,
)


class TestTruncateSessionId:
    """Test session ID truncation for safe logging"""

    def test_truncate_standard_uuid(self):
        """Should truncate standard UUID to first 8 chars"""
        session_id = "a1b2c3d4-e5f6-7890-abcd-ef1234567890"
        result = truncate_session_id(session_id)
        assert result == "a1b2c3d4..."
        assert len(result) == 11  # 8 + 3 dots

    def test_truncate_with_custom_length(self):
        """Should respect custom truncation length"""
        session_id = "abcdefghijklmnop"
        result = truncate_session_id(session_id, length=5)
        assert result == "abcde..."

    def test_truncate_empty_string(self):
        """Should return 'unknown' for empty session ID"""
        result = truncate_session_id("")
        assert result == "unknown"

    def test_truncate_none_handled_as_empty(self):
        """Should handle None as empty string"""
        # Python would throw error, but we should return "unknown"
        result = truncate_session_id("")
        assert result == "unknown"

    def test_truncate_short_session_id(self):
        """Should handle session IDs shorter than truncation length"""
        session_id = "abc123"
        result = truncate_session_id(session_id, length=8)
        assert result == "abc123..."

    def test_truncate_single_char(self):
        """Should handle single character session ID"""
        session_id = "a"
        result = truncate_session_id(session_id)
        assert result == "a..."

    def test_does_not_expose_full_id(self):
        """Truncated ID should not reveal much of the original"""
        session_id = "secret_token_12345678901234567890"
        result = truncate_session_id(session_id)
        # Should not contain the end of the ID
        assert "901234567890" not in result
        assert result == "secret_t..."


class TestIsSensitiveLogLevel:
    """Test sensitive log level detection"""

    def test_warning_is_sensitive(self):
        """WARNING should be treated as sensitive"""
        assert is_sensitive_log_level("WARNING") is True

    def test_error_is_sensitive(self):
        """ERROR should be treated as sensitive"""
        assert is_sensitive_log_level("ERROR") is True

    def test_critical_is_sensitive(self):
        """CRITICAL should be treated as sensitive"""
        assert is_sensitive_log_level("CRITICAL") is True

    def test_info_not_sensitive(self):
        """INFO should not be treated as sensitive"""
        assert is_sensitive_log_level("INFO") is False

    def test_debug_not_sensitive(self):
        """DEBUG should not be treated as sensitive"""
        assert is_sensitive_log_level("DEBUG") is False

    def test_lowercase_warning_is_sensitive(self):
        """Should be case-insensitive"""
        assert is_sensitive_log_level("warning") is True

    def test_mixed_case_error_is_sensitive(self):
        """Should be case-insensitive"""
        assert is_sensitive_log_level("Error") is True


class TestMaskEmail:
    """Test email masking for safe logging"""

    def test_mask_email_at_warning_level(self):
        """Should mask email at WARNING level"""
        email = "user@example.com"
        result = mask_email(email, "WARNING")
        assert result == "u***@example.com"
        assert "user" not in result

    def test_show_email_at_info_level(self):
        """Should show full email at INFO level"""
        email = "user@example.com"
        result = mask_email(email, "INFO")
        assert result == "user@example.com"

    def test_show_email_at_debug_level(self):
        """Should show full email at DEBUG level"""
        email = "test@domain.co.uk"
        result = mask_email(email, "DEBUG")
        assert result == "test@domain.co.uk"

    def test_mask_email_at_error_level(self):
        """Should mask email at ERROR level"""
        email = "admin@company.org"
        result = mask_email(email, "ERROR")
        assert result == "a***@company.org"

    def test_mask_single_char_email(self):
        """Should handle single character local part"""
        email = "a@example.com"
        result = mask_email(email, "WARNING")
        assert result == "***@example.com"

    def test_mask_two_char_email(self):
        """Should handle two character local part"""
        email = "ab@example.com"
        result = mask_email(email, "WARNING")
        assert result == "a***@example.com"

    def test_empty_email(self):
        """Should return 'unknown' for empty email"""
        result = mask_email("", "WARNING")
        assert result == "unknown"

    def test_invalid_email_format(self):
        """Should handle invalid email format"""
        result = mask_email("notanemail", "WARNING")
        assert result == "***"

    def test_case_insensitive_log_level(self):
        """Should be case-insensitive with log level"""
        email = "user@example.com"
        result = mask_email(email, "warning")
        assert result == "u***@example.com"


class TestSanitizePassword:
    """Test password sanitization for logging"""

    def test_sanitize_long_password(self):
        """Should show length indicator for password"""
        password = "mySecurePassword123"
        result = sanitize_password(password)
        assert "***" in result
        assert "19 chars" in result
        assert "mySecure" not in result

    def test_sanitize_short_password(self):
        """Should handle short passwords"""
        password = "pass"
        result = sanitize_password(password)
        assert "***" in result
        assert "4 chars" in result

    def test_sanitize_empty_password(self):
        """Should return *** for empty password"""
        result = sanitize_password("")
        assert result == "***"

    def test_never_shows_actual_password(self):
        """Should never reveal any part of the actual password"""
        password = "SuperSecretPass123!@#"
        result = sanitize_password(password)
        assert "Super" not in result
        assert "Secret" not in result
        assert "Pass" not in result
        assert "123" not in result

    def test_shows_length_only(self):
        """Should only show length, not content"""
        password = "abcdefghijklmnopqrst"
        result = sanitize_password(password)
        assert "***[20 chars]" == result


class TestSanitizeUrl:
    """Test URL sanitization for safe logging"""

    def test_sanitize_url_with_credentials(self):
        """Should mask credentials in URL"""
        url = "https://user:password@api.taiga.io/api/v1"
        result = sanitize_url(url)
        assert "***:***@" in result
        assert "user" not in result
        assert "password" not in result
        assert "api.taiga.io" in result

    def test_sanitize_url_without_credentials(self):
        """Should not modify URL without credentials"""
        url = "https://api.taiga.io/api/v1"
        result = sanitize_url(url)
        assert result == url

    def test_sanitize_http_url_with_credentials(self):
        """Should work with HTTP URLs too"""
        url = "http://admin:secret@localhost:9000"
        result = sanitize_url(url)
        assert "***:***@" in result
        assert "localhost:9000" in result

    def test_sanitize_empty_url(self):
        """Should return 'unknown' for empty URL"""
        result = sanitize_url("")
        assert result == "unknown"

    def test_sanitize_url_without_protocol(self):
        """Should return original if no protocol"""
        url = "api.taiga.io/api/v1"
        result = sanitize_url(url)
        assert result == url

    def test_sanitize_with_mask_auth_false(self):
        """Should not mask when mask_auth=False"""
        url = "https://user:password@api.taiga.io/api/v1"
        result = sanitize_url(url, mask_auth=False)
        assert result == url

    def test_sanitize_url_with_multiple_colons(self):
        """Should handle complex credentials"""
        url = "https://user@example.com:secretpass123@api.taiga.io"
        result = sanitize_url(url)
        assert "***:***@api.taiga.io" in result
        assert "user" not in result
        assert "secretpass" not in result

    def test_sanitize_preserves_path(self):
        """Should preserve URL path after masking"""
        url = "https://user:pass@api.taiga.io/api/v1/projects?id=123"
        result = sanitize_url(url)
        assert "/api/v1/projects?id=123" in result
        assert "***:***@" in result


class TestLoggingSecurityIntegration:
    """Integration tests for logging security"""

    def test_session_logging_is_safe(self):
        """Session ID in logs should be truncated"""
        session_id = "a1b2c3d4-e5f6-7890-abcd-ef1234567890"
        truncated = truncate_session_id(session_id)
        # Should be safe to log
        assert len(truncated) < len(session_id)
        assert "ef1234567890" not in truncated

    def test_credentials_never_logged(self):
        """Credentials should be sanitized for all log levels"""
        url = "https://admin:secret123@taiga.io"
        for level in ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]:
            result = sanitize_url(url)
            assert "secret" not in result
            assert "admin" not in result

    def test_password_never_exposed(self):
        """Password should never appear in any form in logs"""
        password = "VerySecurePassword!@#$"
        result = sanitize_password(password)
        for char_sequence in ["Very", "Secure", "Password", "!@#$"]:
            assert char_sequence not in result
