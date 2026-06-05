"""Frontend safety helpers for M11 static workflow page."""

from __future__ import annotations

import html
from pathlib import Path


def escape_frontend_text(value: str) -> str:
    """Escape user-provided text for safe HTML rendering.

    Uses Python's ``html.escape`` to convert ``<``, ``>``, ``&``, ``"``, ``'``
    to their HTML entity equivalents. This prevents accidental or malicious
    HTML/script injection from user-supplied content.
    """

    if not isinstance(value, str):
        return ""
    return html.escape(value, quote=True)


def safe_relative_artifact_path(path: str | Path, base_dir: str | Path) -> str:
    """Return *path* relative to *base_dir* if it is a descendant.

    If the path is outside *base_dir* (e.g. an absolute system path), the
    original path is escaped and returned, but no direct link is created.

    This prevents the frontend page from creating links to arbitrary local
    files outside the workflow output directory.
    """

    try:
        resolved_path = Path(path).resolve()
        base = Path(base_dir).resolve()
        relative = resolved_path.relative_to(base)
        return str(relative).replace("\\", "/")
    except (ValueError, OSError):
        # Path is outside base_dir; return escaped filename only
        return escape_frontend_text(Path(path).name)


def is_allowed_frontend_artifact(path: str | Path) -> bool:
    """Check whether *path* has an allowed extension for frontend display.

    Allowed: .html, .pdf, .json, .txt.
    Disallowed: .exe, .dll, .bat, .sh, and others.
    """

    allowed = {".html", ".pdf", ".json", ".txt"}
    suffix = Path(path).suffix.lower()
    return suffix in allowed
