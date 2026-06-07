"""Input/output helpers for the workflow integrator."""

from __future__ import annotations

import json
from pathlib import Path

from resume_pdf_agent.models.resume_content import ResumeContent
from resume_pdf_agent.models.user_profile import UserProfile
from resume_pdf_agent.models.workflow import ResumeWorkflowInput, WorkflowArtifact


def ensure_output_dir(output_dir: str | Path) -> Path:
    """Create *output_dir* (including parents) and return its Path."""

    path = Path(output_dir)
    path.mkdir(parents=True, exist_ok=True)
    return path


def write_text_artifact(
    text: str,
    output_path: str | Path,
    artifact_type: str,
    description: str,
) -> WorkflowArtifact:
    """Write *text* to *output_path* (UTF-8) with parent directories created."""

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(text, encoding="utf-8")
    return WorkflowArtifact(
        artifact_type=artifact_type,
        path=str(output_path),
        description=description,
    )


def load_workflow_input_from_json(input_path: str | Path) -> ResumeWorkflowInput:
    """Load a ``ResumeWorkflowInput`` from a JSON file.

    The JSON structure must contain at minimum:

    .. code-block:: json

       {
         "user_profile": { ... },
         "resume_content": { ... }
       }

    Optional keys: ``target_role``, ``criteria_profile_id``, ``output_dir``,
    ``pdf_backend``, ``include_preview_reminder_panel``, ``write_intermediate_json``.
    """

    path = Path(input_path)
    if not path.is_file():
        raise FileNotFoundError(f"Workflow input file not found: {path}")

    raw = json.loads(path.read_text(encoding="utf-8"))

    if not isinstance(raw, dict):
        raise ValueError("Workflow input JSON must be a JSON object")

    if "user_profile" not in raw:
        raise ValueError("Workflow input JSON must contain 'user_profile' key")
    if "resume_content" not in raw:
        raise ValueError("Workflow input JSON must contain 'resume_content' key")

    user_profile = UserProfile(**raw["user_profile"])
    resume_content = ResumeContent(**raw["resume_content"])

    return ResumeWorkflowInput(
        user_profile=user_profile,
        resume_content=resume_content,
        target_role=raw.get("target_role"),
        criteria_profile_id=raw.get("criteria_profile_id"),
        output_dir=raw.get("output_dir", "outputs/workflow"),
        pdf_backend=raw.get("pdf_backend", "mock"),
        include_preview_reminder_panel=raw.get("include_preview_reminder_panel", False),
        write_intermediate_json=raw.get("write_intermediate_json", True),
        llm_review_decisions_path=raw.get("llm_review_decisions_path"),
        write_llm_review_decision_summary=raw.get("write_llm_review_decision_summary", False),
        llm_review_decision_summary_json_path=raw.get("llm_review_decision_summary_json_path"),
        llm_review_decision_summary_md_path=raw.get("llm_review_decision_summary_md_path"),
    )
