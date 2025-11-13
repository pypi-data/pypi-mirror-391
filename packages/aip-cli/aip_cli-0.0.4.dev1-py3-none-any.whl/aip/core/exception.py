from click import ClickException


class AuthException(ClickException):
    """Raised when authentication fails due to invalid or expired token."""

    def __init__(self, message="Authentication failed: Invalid or expired token."):
        super().__init__(message)
