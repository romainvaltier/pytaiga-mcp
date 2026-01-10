"""
Secure Logging Utilities

Provides functions to sanitize sensitive data in log messages to prevent
exposure of session IDs, authentication tokens, passwords, and other
confidential information.
"""


def truncate_session_id(session_id: str, length: int = 8) -> str:
    """
    Truncate session ID for safe logging.

    Shows only the first N characters of the session ID followed by ellipsis.
    This allows identifying sessions in logs while protecting sensitive info.

    Args:
        session_id: The full session ID to truncate
        length: Number of characters to show (default: 8)

    Returns:
        Truncated session ID in format "abcd1234..." or "unknown" if empty

    Example:
        >>> truncate_session_id("a1b2c3d4-e5f6-7890-abcd-ef1234567890")
        'a1b2c3d4...'
    """
    if not session_id:
        return "unknown"
    return f"{session_id[:length]}..."


def is_sensitive_log_level(log_level: str) -> bool:
    """
    Check if a log level should not include sensitive data like email.

    Args:
        log_level: Log level name (e.g., "WARNING", "ERROR", "INFO", "DEBUG")

    Returns:
        True if log level is WARNING, ERROR, or CRITICAL (should be careful with data)
        False if log level is INFO or DEBUG (can include more details)
    """
    sensitive_levels = {"WARNING", "ERROR", "CRITICAL"}
    return log_level.upper() in sensitive_levels


def mask_email(email: str, log_level: str = "INFO") -> str:
    """
    Mask email address for safe logging at sensitive levels.

    Args:
        email: Email address to mask
        log_level: Log level determining masking behavior

    Returns:
        Masked email at WARNING/ERROR level, full email at INFO/DEBUG level

    Example:
        >>> mask_email("user@example.com", "WARNING")
        'u***@example.com'
        >>> mask_email("user@example.com", "INFO")
        'user@example.com'
    """
    if not email:
        return "unknown"

    if not is_sensitive_log_level(log_level):
        # INFO and DEBUG levels can include full email
        return email

    # For WARNING, ERROR, CRITICAL: mask the local part
    parts = email.split("@")
    if len(parts) != 2:
        return "***"

    local, domain = parts
    if len(local) <= 1:
        masked_local = "***"
    else:
        masked_local = local[0] + "***"

    return f"{masked_local}@{domain}"


def sanitize_password(password: str) -> str:
    """
    Sanitize password for logging (never show the actual password).

    Args:
        password: Password to sanitize

    Returns:
        Safe representation of password ("***" or length indicator)

    Example:
        >>> sanitize_password("mySecurePassword123")
        '***[19 chars]'
    """
    if not password:
        return "***"
    return f"***[{len(password)} chars]"


def sanitize_url(url: str, mask_auth: bool = True) -> str:
    """
    Sanitize URL for safe logging (mask authentication credentials if present).

    Args:
        url: URL to sanitize
        mask_auth: Whether to mask username/password in URL (default: True)

    Returns:
        Sanitized URL with credentials masked if present

    Example:
        >>> sanitize_url("https://user:pass@api.taiga.io/api/v1")
        'https://***:***@api.taiga.io/api/v1'
    """
    if not url:
        return "unknown"

    if not mask_auth or "://" not in url:
        return url

    # Split by protocol
    protocol, rest = url.split("://", 1)

    # Check if there are credentials
    if "@" not in rest:
        return url

    auth, domain = rest.rsplit("@", 1)

    # Don't expose the actual auth details
    return f"{protocol}://***:***@{domain}"
