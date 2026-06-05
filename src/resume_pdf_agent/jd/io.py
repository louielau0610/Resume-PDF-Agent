"""I/O helpers for M15 user-provided JD parser."""

from __future__ import annotations

from pathlib import Path

from resume_pdf_agent.models.jd import JDToCriteriaBuildResult, ParsedJD
from resume_pdf_agent.models.workflow import WorkflowArtifact


def load_jd_text_from_file(path: str | Path) -> str:
    """Load JD text from a local file (UTF-8).

    Parameters
    ----------
    path : str | Path
        Path to the JD text file.

    Returns
    -------
    str
        Raw JD text content.

    Raises
    ------
    FileNotFoundError
        If the file does not exist.
    """
    p = Path(path)
    if not p.is_file():
        raise FileNotFoundError(f"JD file not found: {p}")
    return p.read_text(encoding="utf-8")


def load_jd_from_workflow_json_field(data: dict) -> str | None:
    """Extract jd_text from a workflow JSON dict if present."""
    return data.get("jd_text") or None


def write_parsed_jd_artifact(
    parsed_jd: ParsedJD,
    output_path: str | Path,
) -> WorkflowArtifact:
    """Write a ParsedJD as a JSON artifact."""
    import json

    p = Path(output_path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(
        parsed_jd.model_dump_json(indent=2),
        encoding="utf-8",
    )
    return WorkflowArtifact(
        artifact_type="parsed_jd",
        path=str(p),
        description="Parsed user-provided job description",
    )


def write_jd_criteria_artifact(
    build_result: JDToCriteriaBuildResult,
    output_path: str | Path,
) -> WorkflowArtifact | None:
    """Write a JD-derived criteria profile as a JSON artifact.

    Returns None if no profile exists.
    """
    import json

    if build_result.criteria_profile is None:
        return None

    p = Path(output_path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(
        build_result.criteria_profile.model_dump_json(indent=2),
        encoding="utf-8",
    )
    return WorkflowArtifact(
        artifact_type="jd_criteria_profile",
        path=str(p),
        description="Criteria profile derived from user-provided JD",
    )
