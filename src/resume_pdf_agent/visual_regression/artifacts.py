"""Output artifact validation for M18 visual regression."""

from __future__ import annotations

from pathlib import Path


def collect_expected_visual_artifacts(output_dir: str | Path) -> dict[str, bool]:
    """Check which visual artifacts exist in an output directory.

    Parameters
    ----------
    output_dir : str | Path
        Path to the workflow output directory.

    Returns
    -------
    dict[str, bool]
        Mapping of artifact name to existence.
    """
    od = Path(output_dir)
    return {
        "index.html": (od / "index.html").is_file(),
        "resume.html": (od / "resume.html").is_file(),
        "resume.pdf": (od / "resume.pdf").is_file(),
        "workflow_result.json": (od / "workflow_result.json").is_file(),
        "confirmation_packet.json": (od / "confirmation_packet.json").is_file(),
        "confirmation_review.md": (od / "confirmation_review.md").is_file(),
        "parsed_jd.json": (od / "parsed_jd.json").is_file(),
        "jd_criteria_profile.json": (od / "jd_criteria_profile.json").is_file(),
        "llm_rewrite_result.json": (od / "llm_rewrite_result.json").is_file(),
    }


def validate_workflow_visual_artifacts(output_dir: str | Path) -> list[str]:
    """Validate essential visual artifacts in a workflow output directory.

    Parameters
    ----------
    output_dir : str | Path
        Path to the workflow output directory.

    Returns
    -------
    list[str]
        List of issues found. Empty list means pass.
    """
    issues: list[str] = []
    artifacts = collect_expected_visual_artifacts(output_dir)

    # Required artifacts
    required = ["index.html", "resume.html", "resume.pdf"]
    for name in required:
        if not artifacts[name]:
            issues.append(f"Missing required artifact: {name}")

    # PDF validation
    pdf_path = Path(output_dir) / "resume.pdf"
    issues.extend(validate_pdf_artifact(pdf_path))

    return issues


def validate_pdf_artifact(output_path: str | Path) -> list[str]:
    """Validate a PDF file artifact.

    Checks existence, non-empty, and PDF header.

    Parameters
    ----------
    output_path : str | Path
        Path to the PDF file.

    Returns
    -------
    list[str]
        List of issues found.
    """
    issues: list[str] = []
    p = Path(output_path)

    if not p.is_file():
        issues.append(f"PDF not found: {p}")
        return issues

    size = p.stat().st_size
    if size == 0:
        issues.append(f"PDF is empty: {p}")

    # Check PDF header
    try:
        header = p.read_bytes()[:5]
        if header != b"%PDF-":
            issues.append(f"PDF missing header: {p} (got {header!r})")
    except Exception as exc:
        issues.append(f"PDF read error: {exc}")

    return issues
