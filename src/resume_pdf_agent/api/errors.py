"""API error helpers for M19 optional API layer."""

from __future__ import annotations


class OptionalDependencyError(ImportError):
    """Raised when an optional dependency is not installed."""

    def __init__(self, package: str, install_hint: str | None = None):
        hint = install_hint or f"pip install {package}"
        super().__init__(
            f"Optional dependency '{package}' is not installed. Install with: {hint}"
        )
        self.package = package
        self.install_hint = hint


def safe_error_message(exc: Exception) -> str:
    """Return a safe error message without stack trace or secrets."""
    return str(exc)


def api_error_response(message: str) -> dict:
    """Build a simple API error response dict."""
    return {
        "status": "error",
        "message": message,
    }
