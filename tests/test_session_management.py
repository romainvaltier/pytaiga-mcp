"""
Comprehensive test suite for session management and TTL enforcement.

Tests the SessionInfo dataclass, session lifecycle, TTL enforcement,
concurrent session limits, background cleanup, and all session-related
security features.
"""

import os
import time
import uuid
from datetime import datetime, timedelta
from unittest.mock import MagicMock, patch

import pytest

import src.server
from src.taiga_client import TaigaClientWrapper
from src.types import SessionInfo


class TestSessionInfo:
    """Unit tests for SessionInfo dataclass."""

    def test_session_info_creation_with_defaults(self):
        """Test SessionInfo creation with default values"""
        mock_client = MagicMock()
        session = SessionInfo(session_id="test-123", client=mock_client, username="testuser")

        assert session.session_id == "test-123"
        assert session.username == "testuser"
        assert session.client == mock_client
        assert session.created_at <= datetime.utcnow()
        assert session.last_accessed <= datetime.utcnow()
        assert session.expires_at > datetime.utcnow()

    def test_session_ttl_from_env_variable(self):
        """Test session TTL is set from SESSION_EXPIRY env variable"""
        mock_client = MagicMock()

        with patch.dict(os.environ, {"SESSION_EXPIRY": "3600"}):
            session = SessionInfo(session_id="test-456", client=mock_client, username="testuser")

            # TTL should be approximately 3600 seconds (1 hour)
            time_until_expiry = session.time_until_expiry()
            assert 3590 <= time_until_expiry.total_seconds() <= 3610

    def test_session_ttl_default_8_hours(self):
        """Test default TTL is 8 hours when not configured"""
        mock_client = MagicMock()

        # Ensure SESSION_EXPIRY is not set
        with patch.dict(os.environ, {}, clear=False):
            if "SESSION_EXPIRY" in os.environ:
                del os.environ["SESSION_EXPIRY"]

            session = SessionInfo(session_id="test-789", client=mock_client, username="testuser")

            # Default TTL should be 28800 seconds (8 hours)
            time_until_expiry = session.time_until_expiry()
            assert 28790 <= time_until_expiry.total_seconds() <= 28810

    def test_session_expiry_detection(self):
        """Test session expiry detection"""
        mock_client = MagicMock()
        session = SessionInfo(session_id="test-expiry", client=mock_client, username="testuser")

        # Fresh session should not be expired
        assert not session.is_expired()

        # Force expiration to past
        session.expires_at = datetime.utcnow() - timedelta(seconds=1)
        assert session.is_expired()

    def test_last_accessed_update(self):
        """Test last_accessed timestamp update"""
        mock_client = MagicMock()
        session = SessionInfo(session_id="test-accessed", client=mock_client, username="testuser")

        original_time = session.last_accessed
        time.sleep(0.01)  # Small delay to ensure time difference
        session.update_last_accessed()

        assert session.last_accessed > original_time

    def test_time_until_expiry_calculation(self):
        """Test time_until_expiry calculation"""
        mock_client = MagicMock()
        session = SessionInfo(session_id="test-ttl", client=mock_client, username="testuser")

        # Set expiry to 1 hour from now
        session.expires_at = datetime.utcnow() + timedelta(hours=1)
        time_left = session.time_until_expiry()

        # Should be approximately 1 hour (3600 seconds)
        assert 3590 <= time_left.total_seconds() <= 3610

    def test_zero_ttl_fallback_to_default(self):
        """Test that zero/negative TTL falls back to default 8 hours"""
        mock_client = MagicMock()

        with patch.dict(os.environ, {"SESSION_EXPIRY": "0"}):
            session = SessionInfo(
                session_id="test-zero-ttl", client=mock_client, username="testuser"
            )

            # Should fall back to 28800 seconds (8 hours)
            time_until_expiry = session.time_until_expiry()
            assert 28790 <= time_until_expiry.total_seconds() <= 28810


class TestSessionValidation:
    """Test session validation and TTL enforcement."""

    def setup_method(self):
        """Clear sessions before each test"""
        src.server.active_sessions.clear()
        src.server.sessions_by_user.clear()

    def test_valid_session_retrieval(self):
        """Test successful retrieval of valid session"""
        mock_client = MagicMock()
        mock_client.is_authenticated = True

        session_id = str(uuid.uuid4())
        session_info = SessionInfo(session_id=session_id, client=mock_client, username="testuser")
        src.server.active_sessions[session_id] = session_info

        # Should return the client without raising exception
        returned_client = src.server._get_authenticated_client(session_id)
        assert returned_client == mock_client

    def test_session_not_found_raises_error(self):
        """Test that invalid session ID raises PermissionError"""
        with pytest.raises(PermissionError, match="Invalid session ID"):
            src.server._get_authenticated_client("nonexistent-session")

    def test_expired_session_rejected(self):
        """Test that expired sessions are rejected"""
        mock_client = MagicMock()
        mock_client.is_authenticated = True

        session_id = str(uuid.uuid4())
        session_info = SessionInfo(session_id=session_id, client=mock_client, username="testuser")
        # Force expiration
        session_info.expires_at = datetime.utcnow() - timedelta(seconds=1)

        src.server.active_sessions[session_id] = session_info

        # Should raise PermissionError and clean up session
        with pytest.raises(PermissionError, match="Session expired"):
            src.server._get_authenticated_client(session_id)

        # Session should be cleaned up
        assert session_id not in src.server.active_sessions

    def test_unauthenticated_client_rejected(self):
        """Test that unauthenticated clients are rejected"""
        mock_client = MagicMock()
        mock_client.is_authenticated = False

        session_id = str(uuid.uuid4())
        session_info = SessionInfo(session_id=session_id, client=mock_client, username="testuser")

        src.server.active_sessions[session_id] = session_info

        # Should raise PermissionError and clean up
        with pytest.raises(PermissionError, match="authentication lost"):
            src.server._get_authenticated_client(session_id)

        # Session should be cleaned up
        assert session_id not in src.server.active_sessions

    def test_last_accessed_timestamp_updated(self):
        """Test that last_accessed is updated on validation"""
        mock_client = MagicMock()
        mock_client.is_authenticated = True

        session_id = str(uuid.uuid4())
        session_info = SessionInfo(session_id=session_id, client=mock_client, username="testuser")
        original_time = session_info.last_accessed

        src.server.active_sessions[session_id] = session_info

        time.sleep(0.01)  # Small delay
        src.server._get_authenticated_client(session_id)

        # last_accessed should be updated
        assert session_info.last_accessed > original_time


class TestSessionCleanup:
    """Test session cleanup helper function."""

    def setup_method(self):
        """Clear sessions before each test"""
        src.server.active_sessions.clear()
        src.server.sessions_by_user.clear()

    def test_cleanup_session_removes_from_storage(self):
        """Test that _cleanup_session removes session from storage"""
        mock_client = MagicMock()
        session_id = str(uuid.uuid4())
        session_info = SessionInfo(session_id=session_id, client=mock_client, username="testuser")

        src.server.active_sessions[session_id] = session_info
        src.server.sessions_by_user["testuser"] = [session_id]

        # Cleanup
        src.server._cleanup_session(session_id)

        # Should be removed
        assert session_id not in src.server.active_sessions
        assert "testuser" not in src.server.sessions_by_user

    def test_cleanup_session_removes_user_tracking(self):
        """Test that cleanup properly updates sessions_by_user"""
        mock_client = MagicMock()
        session_id1 = str(uuid.uuid4())
        session_id2 = str(uuid.uuid4())

        for sid in [session_id1, session_id2]:
            session_info = SessionInfo(session_id=sid, client=mock_client, username="testuser")
            src.server.active_sessions[sid] = session_info

        src.server.sessions_by_user["testuser"] = [session_id1, session_id2]

        # Cleanup first session
        src.server._cleanup_session(session_id1)

        # Second session should still exist
        assert session_id1 not in src.server.active_sessions
        assert session_id2 in src.server.active_sessions
        assert src.server.sessions_by_user["testuser"] == [session_id2]

    def test_cleanup_removes_empty_user_list(self):
        """Test that empty user lists are removed"""
        mock_client = MagicMock()
        session_id = str(uuid.uuid4())
        session_info = SessionInfo(session_id=session_id, client=mock_client, username="testuser")

        src.server.active_sessions[session_id] = session_info
        src.server.sessions_by_user["testuser"] = [session_id]

        # Cleanup
        src.server._cleanup_session(session_id)

        # User tracking should be completely removed
        assert "testuser" not in src.server.sessions_by_user


class TestConcurrentSessionLimits:
    """Test concurrent session limit enforcement."""

    def setup_method(self):
        """Clear sessions before each test"""
        src.server.active_sessions.clear()
        src.server.sessions_by_user.clear()

    def test_concurrent_session_limit_enforced(self):
        """Test that max concurrent sessions per user is enforced"""
        with patch.dict(os.environ, {"MAX_CONCURRENT_SESSIONS": "2"}):
            with patch.object(TaigaClientWrapper, "login", return_value=True):
                # First login
                result1 = src.server.login("https://test.com", "user1", "pass")
                session1 = result1["session_id"]

                # Second login
                result2 = src.server.login("https://test.com", "user1", "pass")
                session2 = result2["session_id"]

                # Both should exist
                assert session1 in src.server.active_sessions
                assert session2 in src.server.active_sessions
                assert len(src.server.sessions_by_user.get("user1", [])) == 2

                # Third login should remove oldest
                result3 = src.server.login("https://test.com", "user1", "pass")
                session3 = result3["session_id"]

                # Only 2 should exist
                assert session1 not in src.server.active_sessions
                assert session2 in src.server.active_sessions
                assert session3 in src.server.active_sessions
                assert len(src.server.sessions_by_user.get("user1", [])) == 2

    def test_unlimited_sessions_with_zero_config(self):
        """Test that unlimited sessions work when MAX_CONCURRENT_SESSIONS=0"""
        with patch.dict(os.environ, {"MAX_CONCURRENT_SESSIONS": "0"}):
            with patch.object(TaigaClientWrapper, "login", return_value=True):
                # Create many sessions
                sessions = []
                for i in range(10):
                    result = src.server.login("https://test.com", "user1", "pass")
                    sessions.append(result["session_id"])

                # All should exist
                for session_id in sessions:
                    assert session_id in src.server.active_sessions

                assert len(src.server.sessions_by_user.get("user1", [])) == 10

    def test_different_users_separate_limits(self):
        """Test that session limits are per-user"""
        with patch.dict(os.environ, {"MAX_CONCURRENT_SESSIONS": "1"}):
            with patch.object(TaigaClientWrapper, "login", return_value=True):
                # User1 creates session
                result1 = src.server.login("https://test.com", "user1", "pass")
                session1 = result1["session_id"]

                # User2 creates session
                result2 = src.server.login("https://test.com", "user2", "pass")
                session2 = result2["session_id"]

                # Both should exist (limit is per-user)
                assert session1 in src.server.active_sessions
                assert session2 in src.server.active_sessions
                assert src.server.sessions_by_user["user1"] == [session1]
                assert src.server.sessions_by_user["user2"] == [session2]


class TestBackgroundCleanup:
    """Test background session cleanup functionality."""

    def setup_method(self):
        """Clear sessions before each test"""
        src.server.active_sessions.clear()
        src.server.sessions_by_user.clear()

    def test_cleanup_removes_expired_sessions(self):
        """Test that background cleanup removes expired sessions"""
        mock_client = MagicMock()
        mock_client.is_authenticated = True

        # Create one valid and one expired session
        valid_id = str(uuid.uuid4())
        expired_id = str(uuid.uuid4())

        valid_session = SessionInfo(session_id=valid_id, client=mock_client, username="user1")

        expired_session = SessionInfo(session_id=expired_id, client=mock_client, username="user2")
        expired_session.expires_at = datetime.utcnow() - timedelta(seconds=1)

        src.server.active_sessions[valid_id] = valid_session
        src.server.active_sessions[expired_id] = expired_session
        src.server.sessions_by_user["user1"] = [valid_id]
        src.server.sessions_by_user["user2"] = [expired_id]

        # Run cleanup
        cleaned = src.server._cleanup_expired_sessions_sync()

        # Should clean up 1 session
        assert cleaned == 1
        assert valid_id in src.server.active_sessions
        assert expired_id not in src.server.active_sessions
        assert "user2" not in src.server.sessions_by_user

    def test_cleanup_returns_count(self):
        """Test that cleanup returns the number of sessions cleaned"""
        mock_client = MagicMock()

        # Create 3 expired sessions
        for i in range(3):
            session_id = str(uuid.uuid4())
            session_info = SessionInfo(
                session_id=session_id, client=mock_client, username=f"user{i}"
            )
            session_info.expires_at = datetime.utcnow() - timedelta(seconds=1)
            src.server.active_sessions[session_id] = session_info
            src.server.sessions_by_user[f"user{i}"] = [session_id]

        # Run cleanup
        cleaned = src.server._cleanup_expired_sessions_sync()

        assert cleaned == 3

    def test_cleanup_handles_empty_sessions(self):
        """Test that cleanup handles empty sessions dict gracefully"""
        src.server.active_sessions.clear()
        src.server.sessions_by_user.clear()

        # Should not raise error and return 0
        cleaned = src.server._cleanup_expired_sessions_sync()
        assert cleaned == 0


class TestSessionStatus:
    """Test session_status tool response metadata."""

    def setup_method(self):
        """Clear sessions before each test"""
        src.server.active_sessions.clear()
        src.server.sessions_by_user.clear()

    def test_session_status_returns_metadata(self):
        """Test that session_status returns all metadata fields"""
        mock_client = MagicMock()
        mock_client.is_authenticated = True
        mock_client.api.users.me = MagicMock(return_value={"username": "testuser"})

        session_id = str(uuid.uuid4())
        session_info = SessionInfo(session_id=session_id, client=mock_client, username="testuser")

        src.server.active_sessions[session_id] = session_info

        # Call session_status
        result = src.server.session_status(session_id)

        # Check response
        assert result["status"] == "active"
        assert result["session_id"] == session_id
        assert result["username"] == "testuser"
        assert "created_at" in result
        assert "last_accessed" in result
        assert "expires_at" in result
        assert "time_until_expiry_seconds" in result

        # Check timestamps are ISO format (contain 'T' between date and time)
        assert "T" in result["created_at"]
        assert result["time_until_expiry_seconds"] > 0

    def test_session_status_expired_session(self):
        """Test session_status with expired session"""
        mock_client = MagicMock()
        session_id = str(uuid.uuid4())
        session_info = SessionInfo(session_id=session_id, client=mock_client, username="testuser")
        session_info.expires_at = datetime.utcnow() - timedelta(seconds=1)

        src.server.active_sessions[session_id] = session_info
        src.server.sessions_by_user["testuser"] = [session_id]

        # Call session_status
        result = src.server.session_status(session_id)

        # Should be inactive and cleaned up
        assert result["status"] == "inactive"
        assert result["reason"] == "expired"
        assert session_id not in src.server.active_sessions

    def test_session_status_not_found(self):
        """Test session_status with non-existent session"""
        result = src.server.session_status("nonexistent")

        assert result["status"] == "inactive"
        assert result["reason"] == "not_found"


@pytest.mark.integration
class TestSessionLifecycle:
    """Integration tests for complete session lifecycle."""

    def setup_method(self):
        """Clear sessions before each test"""
        src.server.active_sessions.clear()
        src.server.sessions_by_user.clear()

    def test_full_session_lifecycle(self):
        """Test complete session lifecycle: login -> use -> logout"""
        with patch.object(TaigaClientWrapper, "login", return_value=True):
            with patch("src.server.TaigaClientWrapper") as MockClient:
                # Setup mock client instance
                mock_instance = MagicMock()
                mock_instance.is_authenticated = True
                mock_instance.login.return_value = True
                mock_instance.api.users.me.return_value = {"username": "testuser"}
                MockClient.return_value = mock_instance

                # Login
                login_result = src.server.login("https://test.com", "testuser", "pass")
                session_id = login_result["session_id"]

                # Verify session exists
                assert session_id in src.server.active_sessions
                status = src.server.session_status(session_id)
                assert status["status"] == "active"

                # Logout
                logout_result = src.server.logout(session_id)
                assert logout_result["status"] == "logged_out"

                # Verify session is gone
                assert session_id not in src.server.active_sessions
                status = src.server.session_status(session_id)
                assert status["status"] == "inactive"
