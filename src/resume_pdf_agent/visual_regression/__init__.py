"""M18 Visual Regression Testing package."""

from resume_pdf_agent.visual_regression.artifacts import (
    collect_expected_visual_artifacts,
    validate_pdf_artifact,
    validate_workflow_visual_artifacts,
)
from resume_pdf_agent.visual_regression.html_checks import (
    check_dashboard_html_structure,
    check_no_forbidden_frontend_content,
    check_resume_html_structure,
)
from resume_pdf_agent.visual_regression.optional_screenshots import (
    capture_html_screenshot_if_available,
    is_playwright_available,
)
from resume_pdf_agent.visual_regression.snapshots import (
    compare_snapshot_text,
    extract_stable_snapshot_sections,
    normalize_html_for_snapshot,
    write_snapshot,
)

__all__ = [
    "capture_html_screenshot_if_available",
    "check_dashboard_html_structure",
    "check_no_forbidden_frontend_content",
    "check_resume_html_structure",
    "collect_expected_visual_artifacts",
    "compare_snapshot_text",
    "extract_stable_snapshot_sections",
    "is_playwright_available",
    "normalize_html_for_snapshot",
    "validate_pdf_artifact",
    "validate_workflow_visual_artifacts",
    "write_snapshot",
]
