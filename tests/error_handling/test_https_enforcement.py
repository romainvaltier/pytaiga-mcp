"""
Unit tests for HTTPS enforcement in taiga_client.py login.

Tests validate that:
- Non-HTTPS URLs are rejected by default
- ALLOW_HTTP_TAIGA=true bypasses the check
- Error messages guide users to use HTTPS
- Proper logging of security decisions
"""

import os
from unittest.mock import MagicMock, patch

import pytest

from src.taiga_client import TaigaClientWrapper


class TestHTTPSEnforcement:
    """Test HTTPS enforcement in TaigaClientWrapper.login()"""

    def test_https_url_accepted(self):
        """Should accept HTTPS URLs"""
        wrapper = TaigaClientWrapper(host="https://taiga.example.com")
        assert wrapper.host == "https://taiga.example.com"

    def test_http_url_rejected_by_default(self):
        """Should reject HTTP URLs when ALLOW_HTTP_TAIGA is not set"""
        wrapper = TaigaClientWrapper(host="http://localhost:9000")

        # Ensure env var is not set
        with patch.dict(os.environ, {}, clear=False):
            if "ALLOW_HTTP_TAIGA" in os.environ:
                del os.environ["ALLOW_HTTP_TAIGA"]

            with pytest.raises(ValueError) as exc_info:
                wrapper.login(username="test", password="test")

            assert "HTTPS" in str(exc_info.value)
            assert "ALLOW_HTTP_TAIGA" in str(exc_info.value)

    def test_http_url_allowed_with_env_var(self):
        """Should allow HTTP URLs when ALLOW_HTTP_TAIGA=true"""
        wrapper = TaigaClientWrapper(host="http://localhost:9000")

        with patch.dict(os.environ, {"ALLOW_HTTP_TAIGA": "true"}):
            # Mock the TaigaClient to avoid actual API call
            with patch("src.taiga_client.TaigaClient") as mock_client:
                mock_instance = MagicMock()
                mock_client.return_value = mock_instance
                mock_instance.auth.login.return_value = None
                mock_instance.auth_token = "test_token"

                # Should not raise an error
                result = wrapper.login(username="test", password="test")
                assert result is True

    def test_env_var_case_insensitive(self):
        """ALLOW_HTTP_TAIGA should be case-insensitive"""
        wrapper = TaigaClientWrapper(host="http://localhost:9000")

        # Test with "True" (capital T)
        with patch.dict(os.environ, {"ALLOW_HTTP_TAIGA": "True"}):
            with patch("src.taiga_client.TaigaClient") as mock_client:
                mock_instance = MagicMock()
                mock_client.return_value = mock_instance
                mock_instance.auth.login.return_value = None
                mock_instance.auth_token = "test_token"

                result = wrapper.login(username="test", password="test")
                assert result is True

    def test_env_var_false_rejects_http(self):
        """ALLOW_HTTP_TAIGA=false should reject HTTP"""
        wrapper = TaigaClientWrapper(host="http://localhost:9000")

        with patch.dict(os.environ, {"ALLOW_HTTP_TAIGA": "false"}):
            with pytest.raises(ValueError) as exc_info:
                wrapper.login(username="test", password="test")

            assert "HTTPS" in str(exc_info.value)

    def test_error_message_guides_user(self):
        """Error message should guide user to use HTTPS"""
        wrapper = TaigaClientWrapper(host="http://taiga.example.com")

        with patch.dict(os.environ, {}, clear=False):
            if "ALLOW_HTTP_TAIGA" in os.environ:
                del os.environ["ALLOW_HTTP_TAIGA"]

            with pytest.raises(ValueError) as exc_info:
                wrapper.login(username="test", password="test")

            error_msg = str(exc_info.value)
            assert "HTTPS" in error_msg
            assert "security" in error_msg.lower()
            assert "ALLOW_HTTP_TAIGA" in error_msg

    def test_https_enforcement_logs_warning_with_allow_http(self, caplog):
        """Should log warning when HTTP is used with ALLOW_HTTP_TAIGA=true"""
        wrapper = TaigaClientWrapper(host="http://localhost:9000")

        with patch.dict(os.environ, {"ALLOW_HTTP_TAIGA": "true"}):
            with patch("src.taiga_client.TaigaClient") as mock_client:
                mock_instance = MagicMock()
                mock_client.return_value = mock_instance
                mock_instance.auth.login.return_value = None
                mock_instance.auth_token = "test_token"

                wrapper.login(username="test", password="test")

                # Check that warning was logged
                assert any("insecure" in record.message.lower() for record in caplog.records)

    def test_https_enforcement_logs_error_on_rejection(self, caplog):
        """Should log error when HTTP is rejected"""
        wrapper = TaigaClientWrapper(host="http://localhost:9000")

        with patch.dict(os.environ, {}, clear=False):
            if "ALLOW_HTTP_TAIGA" in os.environ:
                del os.environ["ALLOW_HTTP_TAIGA"]

            with pytest.raises(ValueError):
                wrapper.login(username="test", password="test")

            # Check that error was logged
            assert any("HTTPS" in record.message for record in caplog.records)

    def test_https_with_port_accepted(self):
        """Should accept HTTPS URLs with port numbers"""
        wrapper = TaigaClientWrapper(host="https://taiga.example.com:8443")
        assert wrapper.host == "https://taiga.example.com:8443"

    def test_localhost_http_rejected_by_default(self):
        """Should reject localhost HTTP even though it's local"""
        wrapper = TaigaClientWrapper(host="http://localhost:9000")

        with patch.dict(os.environ, {}, clear=False):
            if "ALLOW_HTTP_TAIGA" in os.environ:
                del os.environ["ALLOW_HTTP_TAIGA"]

            with pytest.raises(ValueError) as exc_info:
                wrapper.login(username="test", password="test")

            assert "HTTPS" in str(exc_info.value)

    def test_localhost_https_accepted(self):
        """Should accept localhost with HTTPS"""
        wrapper = TaigaClientWrapper(host="https://localhost:9000")
        assert wrapper.host == "https://localhost:9000"

    def test_empty_allow_http_env_var_rejects(self):
        """Empty ALLOW_HTTP_TAIGA should be treated as false"""
        wrapper = TaigaClientWrapper(host="http://localhost:9000")

        with patch.dict(os.environ, {"ALLOW_HTTP_TAIGA": ""}):
            with pytest.raises(ValueError):
                wrapper.login(username="test", password="test")

    def test_https_check_before_authentication(self):
        """HTTPS check should happen before attempting authentication"""
        wrapper = TaigaClientWrapper(host="http://localhost:9000")

        with patch.dict(os.environ, {}, clear=False):
            if "ALLOW_HTTP_TAIGA" in os.environ:
                del os.environ["ALLOW_HTTP_TAIGA"]

            with patch("src.taiga_client.TaigaClient") as mock_client:
                with pytest.raises(ValueError):
                    wrapper.login(username="test", password="test")

                # TaigaClient should not be instantiated
                mock_client.assert_not_called()
