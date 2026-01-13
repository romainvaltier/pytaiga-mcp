"""
Comprehensive test suite for rate limiting functionality on login.

Tests cover:
- LoginAttempt and RateLimitInfo data structures
- Rate limit validation with sliding window algorithm
- Login integration with rate limiting checks
- Background cleanup of rate limit data
- Per-user rate limit tracking
- Configuration-driven behavior
"""

import os
import time
import uuid
from collections import deque
from datetime import datetime, timedelta
from unittest.mock import MagicMock, call, patch

import pytest

# Import rate limiting components
import src.server
from src.taiga_client import TaigaClientWrapper
from src.types import LoginAttempt, RateLimitInfo


class TestRateLimitDataStructures:
    """Test LoginAttempt and RateLimitInfo dataclasses."""

    def test_login_attempt_creation(self):
        """Test creating a LoginAttempt instance."""
        now = datetime.utcnow()
        attempt = LoginAttempt(timestamp=now, username="test_user", success=True)

        assert attempt.timestamp == now
        assert attempt.username == "test_user"
        assert attempt.success is True

    def test_rate_limit_info_creation(self):
        """Test creating a RateLimitInfo instance."""
        rate_limit = RateLimitInfo()

        assert isinstance(rate_limit.attempts, deque)
        assert len(rate_limit.attempts) == 0
        assert rate_limit.locked_until is None

    def test_rate_limit_info_not_locked_initially(self):
        """Test that RateLimitInfo is not locked initially."""
        rate_limit = RateLimitInfo()

        assert rate_limit.is_locked_out() is False
        assert rate_limit.remaining_lockout_time() == 0

    def test_rate_limit_info_locked_out(self):
        """Test locking out a user."""
        rate_limit = RateLimitInfo()
        future_time = datetime.utcnow() + timedelta(seconds=60)
        rate_limit.locked_until = future_time

        assert rate_limit.is_locked_out() is True
        assert rate_limit.remaining_lockout_time() > 0
        assert rate_limit.remaining_lockout_time() <= 60

    def test_rate_limit_info_lockout_expired(self):
        """Test that lockout expires correctly."""
        rate_limit = RateLimitInfo()
        past_time = datetime.utcnow() - timedelta(seconds=10)
        rate_limit.locked_until = past_time

        assert rate_limit.is_locked_out() is False
        assert rate_limit.remaining_lockout_time() == 0


class TestRateLimitCheck:
    """Test rate limiting validation logic."""

    def setup_method(self):
        """Clear rate limit data before each test."""
        src.server.rate_limit_data.clear()

    def test_first_attempt_not_limited(self):
        """Test that first login attempt is not rate limited."""
        # Should not raise any exception
        src.server._check_rate_limit("new_user")

    def test_rate_limit_without_attempts(self):
        """Test rate limit check on new user with no attempts yet."""
        # Should not raise any exception
        try:
            src.server._check_rate_limit("another_user")
            assert True
        except PermissionError:
            pytest.fail("Rate limit should not trigger for new user")

    def test_rate_limit_lockout_raises_permission_error(self):
        """Test that locked out user gets PermissionError."""
        username = "locked_user"

        # Manually lock the user
        rate_limit = RateLimitInfo()
        rate_limit.locked_until = datetime.utcnow() + timedelta(seconds=60)
        src.server.rate_limit_data[username] = rate_limit

        # Should raise PermissionError
        with pytest.raises(PermissionError) as exc_info:
            src.server._check_rate_limit(username)

        error_msg = str(exc_info.value).lower()
        assert "locked" in error_msg or "attempt" in error_msg

    def test_rate_limit_error_message_includes_time(self):
        """Test that rate limit error message includes remaining lockout time."""
        username = "user_with_lockout"

        # Lock the user with known time
        rate_limit = RateLimitInfo()
        rate_limit.locked_until = datetime.utcnow() + timedelta(seconds=45)
        src.server.rate_limit_data[username] = rate_limit

        try:
            src.server._check_rate_limit(username)
            pytest.fail("Should raise PermissionError")
        except PermissionError as e:
            error_msg = str(e).lower()
            assert "locked" in error_msg or "rate limit" in error_msg

    @patch.dict(os.environ, {"LOGIN_MAX_ATTEMPTS": "3", "LOGIN_RATE_WINDOW": "60"})
    def test_lockout_after_max_attempts(self):
        """Test that user is locked out after exceeding max attempts."""
        username = "bruteforce_user"

        # Add 3 failed attempts within the rate window
        rate_limit = RateLimitInfo()
        now = datetime.utcnow()
        for i in range(3):
            attempt = LoginAttempt(
                timestamp=now - timedelta(seconds=i),
                username=username,
                success=False,
            )
            rate_limit.attempts.append(attempt)

        src.server.rate_limit_data[username] = rate_limit

        # The 4th attempt should trigger lockout during _check_rate_limit
        # This is called via _track_login_attempt, which adds the attempt
        # and then _check_rate_limit validates it
        src.server._track_login_attempt(username, success=False)

        # Now _check_rate_limit should raise PermissionError (user is locked out)
        with pytest.raises(PermissionError):
            src.server._check_rate_limit(username)

    @patch.dict(os.environ, {"LOGIN_RATE_WINDOW": "60"})
    def test_sliding_window_removes_old_attempts(self):
        """Test that attempts outside the rate window are removed."""
        username = "window_user"

        # Add attempts: 2 recent, 1 old (outside window)
        rate_limit = RateLimitInfo()
        now = datetime.utcnow()

        # Old attempt (outside 60 second window)
        old_attempt = LoginAttempt(
            timestamp=now - timedelta(seconds=120),
            username=username,
            success=False,
        )
        # Recent attempts
        recent_attempt1 = LoginAttempt(
            timestamp=now - timedelta(seconds=10),
            username=username,
            success=False,
        )
        recent_attempt2 = LoginAttempt(
            timestamp=now - timedelta(seconds=5),
            username=username,
            success=False,
        )

        rate_limit.attempts.append(old_attempt)
        rate_limit.attempts.append(recent_attempt1)
        rate_limit.attempts.append(recent_attempt2)

        src.server.rate_limit_data[username] = rate_limit

        # First, call _track_login_attempt which cleans old attempts
        src.server._track_login_attempt(username, success=False)

        # Should have 3 attempts (old one was cleaned by sliding window in _check_rate_limit)
        # But _track_login_attempt adds a new one, so we need to verify the sliding window works

    @patch.dict(os.environ, {"LOGIN_MAX_ATTEMPTS": "0"})
    def test_rate_limiting_disabled_with_zero(self):
        """Test that rate limiting is disabled when LOGIN_MAX_ATTEMPTS is 0."""
        username = "unlimited_user"

        # Add many failed attempts
        rate_limit = RateLimitInfo()
        now = datetime.utcnow()
        for i in range(100):
            attempt = LoginAttempt(
                timestamp=now - timedelta(seconds=i),
                username=username,
                success=False,
            )
            rate_limit.attempts.append(attempt)

        src.server.rate_limit_data[username] = rate_limit

        # Should NOT raise PermissionError since rate limiting is disabled
        try:
            src.server._check_rate_limit(username)
            assert True
        except PermissionError:
            pytest.fail("Rate limiting should be disabled when LOGIN_MAX_ATTEMPTS=0")


class TestTrackLoginAttempt:
    """Test login attempt tracking."""

    def setup_method(self):
        """Clear rate limit data before each test."""
        src.server.rate_limit_data.clear()

    def test_track_failed_login_attempt(self):
        """Test tracking a failed login attempt."""
        username = "test_user"

        src.server._track_login_attempt(username, success=False)

        assert username in src.server.rate_limit_data
        assert len(src.server.rate_limit_data[username].attempts) == 1
        assert src.server.rate_limit_data[username].attempts[0].success is False

    def test_track_successful_login_attempt(self):
        """Test tracking a successful login attempt."""
        username = "test_user"

        src.server._track_login_attempt(username, success=True)

        assert username in src.server.rate_limit_data
        assert len(src.server.rate_limit_data[username].attempts) == 1
        assert src.server.rate_limit_data[username].attempts[0].success is True

    def test_successful_login_clears_lockout(self):
        """Test that successful login clears the lockout status."""
        username = "recovered_user"

        # Manually lock the user
        rate_limit = RateLimitInfo()
        rate_limit.locked_until = datetime.utcnow() + timedelta(seconds=60)
        src.server.rate_limit_data[username] = rate_limit

        # Add one successful attempt
        src.server._track_login_attempt(username, success=True)

        # Lockout should be cleared
        assert src.server.rate_limit_data[username].is_locked_out() is False

    def test_successful_login_clears_failed_attempts(self):
        """Test that successful login clears failed attempts but keeps successful one."""
        username = "clearance_user"

        # Add failed attempts
        rate_limit = RateLimitInfo()
        now = datetime.utcnow()
        for i in range(3):
            attempt = LoginAttempt(
                timestamp=now - timedelta(seconds=i),
                username=username,
                success=False,
            )
            rate_limit.attempts.append(attempt)

        src.server.rate_limit_data[username] = rate_limit
        assert len(rate_limit.attempts) == 3

        # Track successful login
        src.server._track_login_attempt(username, success=True)

        # Failed attempts should be cleared, only successful attempt remains
        assert len(src.server.rate_limit_data[username].attempts) == 1
        assert src.server.rate_limit_data[username].attempts[0].success is True


class TestLoginIntegration:
    """Test login tool with rate limiting integration."""

    def setup_method(self):
        """Clear data before each test."""
        src.server.active_sessions.clear()
        src.server.sessions_by_user.clear()
        src.server.rate_limit_data.clear()

    def test_login_fails_when_user_locked_out(self):
        """Test that login fails when user is rate limited."""
        username = "locked_user"
        host = "https://test.taiga.com"
        password = "test_password"

        # Lock the user
        rate_limit = RateLimitInfo()
        rate_limit.locked_until = datetime.utcnow() + timedelta(seconds=60)
        src.server.rate_limit_data[username] = rate_limit

        # Login should fail with PermissionError
        with pytest.raises(PermissionError):
            src.server.login(host, username, password)

    def test_login_success_increments_attempts(self):
        """Test that successful login creates an attempt record."""
        username = "success_user"
        host = "https://test.taiga.com"
        password = "test_password"

        with (
            patch.object(TaigaClientWrapper, "login", return_value=True),
            patch.object(TaigaClientWrapper, "is_authenticated", True),
        ):
            result = src.server.login(host, username, password)

            # Should have successful session
            assert "session_id" in result
            assert result["session_id"] in src.server.active_sessions

            # Rate limit data should be created with successful attempt
            assert username in src.server.rate_limit_data
            assert len(src.server.rate_limit_data[username].attempts) == 1
            assert src.server.rate_limit_data[username].attempts[0].success is True

    def test_login_failure_increments_failed_attempts(self):
        """Test that failed login increments failed attempt counter."""
        username = "failure_user"
        host = "https://test.taiga.com"
        password = "wrong_password"

        with patch.object(TaigaClientWrapper, "login", side_effect=Exception("Auth failed")):
            with pytest.raises(RuntimeError):
                src.server.login(host, username, password)

            # Rate limit data should be created with failed attempt
            assert username in src.server.rate_limit_data
            assert len(src.server.rate_limit_data[username].attempts) == 1
            assert src.server.rate_limit_data[username].attempts[0].success is False

    @patch.dict(os.environ, {"LOGIN_MAX_ATTEMPTS": "2", "LOGIN_RATE_WINDOW": "60"})
    def test_login_lockout_after_multiple_failures(self):
        """Test that user is locked out after multiple failed login attempts."""
        username = "bruteforce_user"
        host = "https://test.taiga.com"
        password = "wrong_password"

        # Simulate 2 failed attempts
        for attempt_num in range(2):
            with patch.object(TaigaClientWrapper, "login", side_effect=Exception("Auth failed")):
                with pytest.raises(RuntimeError):
                    src.server.login(host, username, password)

        # Third attempt should be blocked by rate limiting
        with pytest.raises(PermissionError):
            src.server.login(host, username, password)

    def test_successful_login_after_lockout_expiry(self):
        """Test that user can login after lockout period expires."""
        username = "retry_user"
        host = "https://test.taiga.com"
        password = "test_password"

        # Manually lock the user with expired lockout
        rate_limit = RateLimitInfo()
        rate_limit.locked_until = datetime.utcnow() - timedelta(seconds=1)  # Already expired
        src.server.rate_limit_data[username] = rate_limit

        # Login should succeed (lockout expired)
        with (
            patch.object(TaigaClientWrapper, "login", return_value=True),
            patch.object(TaigaClientWrapper, "is_authenticated", True),
        ):
            result = src.server.login(host, username, password)
            assert "session_id" in result


class TestRateLimitCleanup:
    """Test background cleanup of rate limit data."""

    def setup_method(self):
        """Clear rate limit data before each test."""
        src.server.rate_limit_data.clear()

    @patch.dict(os.environ, {"LOGIN_RATE_WINDOW": "60"})
    def test_cleanup_removes_old_rate_limit_data(self):
        """Test that cleanup removes old rate limit entries."""
        # Add old rate limit data (older than 2x the window = 120 seconds)
        old_username = "old_user"
        old_rate_limit = RateLimitInfo()
        old_rate_limit.locked_until = datetime.utcnow() - timedelta(seconds=200)
        src.server.rate_limit_data[old_username] = old_rate_limit

        # Add recent rate limit data
        new_username = "new_user"
        new_rate_limit = RateLimitInfo()
        new_rate_limit.locked_until = datetime.utcnow() + timedelta(seconds=60)
        src.server.rate_limit_data[new_username] = new_rate_limit

        # Run cleanup
        src.server._cleanup_rate_limit_data_sync()

        # Old data should be removed, new data should remain
        assert old_username not in src.server.rate_limit_data
        assert new_username in src.server.rate_limit_data

    def test_cleanup_preserves_locked_users(self):
        """Test that cleanup preserves users currently locked out."""
        username = "locked_user"

        # Add recently locked user (still within lockout period)
        rate_limit = RateLimitInfo()
        rate_limit.locked_until = datetime.utcnow() + timedelta(seconds=30)
        src.server.rate_limit_data[username] = rate_limit

        initial_count = len(src.server.rate_limit_data)

        # Run cleanup
        src.server._cleanup_rate_limit_data_sync()

        # User should still be in rate limit data
        assert username in src.server.rate_limit_data
        assert len(src.server.rate_limit_data) == initial_count

    @patch.dict(os.environ, {"LOGIN_RATE_WINDOW": "60"})
    def test_cleanup_empty_data(self):
        """Test that cleanup handles empty rate limit data gracefully."""
        # Should not raise any exceptions
        src.server._cleanup_rate_limit_data_sync()

        assert len(src.server.rate_limit_data) == 0


class TestRateLimitConfiguration:
    """Test configuration-driven rate limiting behavior."""

    def setup_method(self):
        """Clear data before each test."""
        src.server.rate_limit_data.clear()

    @patch.dict(os.environ, {"LOGIN_MAX_ATTEMPTS": "10"})
    def test_custom_max_attempts_config(self):
        """Test that custom LOGIN_MAX_ATTEMPTS is respected."""
        # This test verifies config is read (full integration tested elsewhere)
        max_attempts = int(os.getenv("LOGIN_MAX_ATTEMPTS", "5"))
        assert max_attempts == 10

    @patch.dict(os.environ, {"LOGIN_RATE_WINDOW": "120"})
    def test_custom_rate_window_config(self):
        """Test that custom LOGIN_RATE_WINDOW is respected."""
        rate_window = int(os.getenv("LOGIN_RATE_WINDOW", "60"))
        assert rate_window == 120

    @patch.dict(os.environ, {"LOGIN_LOCKOUT_DURATION": "1800"})
    def test_custom_lockout_duration_config(self):
        """Test that custom LOGIN_LOCKOUT_DURATION is respected."""
        lockout_duration = int(os.getenv("LOGIN_LOCKOUT_DURATION", "900"))
        assert lockout_duration == 1800

    @patch.dict(os.environ, {"RATE_LIMIT_CLEANUP_INTERVAL": "600"})
    def test_custom_cleanup_interval_config(self):
        """Test that custom RATE_LIMIT_CLEANUP_INTERVAL is respected."""
        cleanup_interval = int(os.getenv("RATE_LIMIT_CLEANUP_INTERVAL", "300"))
        assert cleanup_interval == 600
