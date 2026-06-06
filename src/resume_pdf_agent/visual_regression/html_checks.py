"""Deterministic HTML structure checks for M18 visual regression testing.

Validates that rendered dashboard and resume HTML contain expected
structural markers without requiring browser rendering.
"""

from __future__ import annotations

import re

# ── Required M12 dashboard CSS classes ──────────────────────────────────
_REQUIRED_DASHBOARD_CLASSES = [
    "app-shell",
    "hero-panel",
    "metric-grid",
    "stage-timeline",
    "artifact-grid",
]

# ── Additional structural markers for dashboard ─────────────────────────
_DASHBOARD_STRUCTURAL_MARKERS = [
    "top-bar",
    "hero-meta",
    "metric-card",
    "section-panel",
    "stage-item",
    "artifact-button",
]

# ── Forbidden content patterns ──────────────────────────────────────────
_FORBIDDEN_PATTERNS: list[tuple[str, str]] = [
    (r"https?://cdn\.", "external CDN link"),
    (r"https?://fonts\.googleapis\.com", "external font import"),
    (r"https?://fonts\.gstatic\.com", "external font import"),
    (r"__NEXT_", "Next.js marker"),
    (r"data-reactroot", "React marker"),
    (r"vite", "Vite marker"),
    (r"fastapi", "FastAPI reference"),
    (r"streamlit", "Streamlit reference"),
    (r"hiring probability", "hiring probability claim"),
    (r"internal.screening", "internal screening claim"),
    (r"internal company screening", "internal screening claim"),
    (r"offer probability", "offer probability claim"),
]


def check_required_css_classes(html: str, required_classes: list[str]) -> list[str]:
    """Check that all required CSS classes are present in the HTML.

    Parameters
    ----------
    html : str
        HTML content to check.
    required_classes : list[str]
        List of CSS class names that must appear.

    Returns
    -------
    list[str]
        List of missing classes. Empty list means all present.
    """
    missing: list[str] = []
    for cls in required_classes:
        # Match class="..." or class='...' patterns
        if not re.search(rf'class=["\'][^"\']*\b{re.escape(cls)}\b', html):
            missing.append(cls)
    return missing


def check_dashboard_html_structure(html: str) -> list[str]:
    """Check that dashboard index.html has the expected M12 structure.

    Parameters
    ----------
    html : str
        The dashboard HTML content.

    Returns
    -------
    list[str]
        List of structural issues found. Empty list means pass.
    """
    issues: list[str] = []

    # Must be valid HTML document
    if "<!DOCTYPE html>" not in html and "<!doctype html>" not in html.lower():
        issues.append("Missing DOCTYPE declaration.")
    if "</html>" not in html:
        issues.append("Missing closing </html> tag.")

    # Required M12 classes
    missing = check_required_css_classes(html, _REQUIRED_DASHBOARD_CLASSES)
    for m in missing:
        issues.append(f"Missing required dashboard class: '{m}'.")

    # Additional structural markers (warn if many missing)
    missing_extra = check_required_css_classes(html, _DASHBOARD_STRUCTURAL_MARKERS)
    if len(missing_extra) > 3:
        issues.append(
            f"Many structural markers missing: {', '.join(missing_extra[:5])}"
        )

    # Must have workflow status displayed
    if "Workflow Dashboard" not in html and "Resume Intelligence Console" not in html:
        issues.append("Dashboard title/header not found.")

    # Forbidden content
    forbidden = check_no_forbidden_frontend_content(html)
    issues.extend(forbidden)

    return issues


def check_resume_html_structure(html: str) -> list[str]:
    """Check that resume.html has basic expected structure.

    Parameters
    ----------
    html : str
        The resume HTML content.

    Returns
    -------
    list[str]
        List of structural issues found.
    """
    issues: list[str] = []

    # Must be valid HTML
    if "<!DOCTYPE html>" not in html and "<!doctype html>" not in html.lower():
        issues.append("Resume HTML: Missing DOCTYPE.")
    if "</html>" not in html:
        issues.append("Resume HTML: Missing closing </html>.")

    # Must have content (not empty body)
    body_match = re.search(r"<body[^>]*>(.*?)</body>", html, re.DOTALL | re.IGNORECASE)
    if body_match:
        body_content = body_match.group(1).strip()
        if len(body_content) < 20:
            issues.append("Resume HTML body is very short or empty.")
    else:
        issues.append("Resume HTML: No <body> found.")

    # Should NOT contain dashboard-only classes
    dashboard_only = ["app-shell", "hero-panel", "stage-timeline", "artifact-grid"]
    for cls in dashboard_only:
        if re.search(rf'class=["\'][^"\']*\b{re.escape(cls)}\b', html):
            issues.append(f"Resume HTML contains dashboard class: '{cls}'.")

    # Forbidden content
    forbidden = check_no_forbidden_frontend_content(html)
    issues.extend(forbidden)

    return issues


def check_no_forbidden_frontend_content(html: str) -> list[str]:
    """Check that rendered HTML does not contain forbidden content.

    Parameters
    ----------
    html : str
        HTML content to check.

    Returns
    -------
    list[str]
        List of forbidden content issues found.
    """
    issues: list[str] = []
    html_lower = html.lower()

    for pattern, description in _FORBIDDEN_PATTERNS:
        if re.search(pattern, html_lower):
            issues.append(f"Forbidden content detected: {description}.")

    return issues
