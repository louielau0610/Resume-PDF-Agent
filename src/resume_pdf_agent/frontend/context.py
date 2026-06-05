"""Frontend page context builder for M11/M12."""

from __future__ import annotations

from pathlib import Path

from resume_pdf_agent.models.frontend import (
    FrontendArtifactLink,
    FrontendPageOptions,
    FrontendStageView,
)
from resume_pdf_agent.models.workflow import (
    ResumeWorkflowInput,
    ResumeWorkflowResult,
)
from resume_pdf_agent.frontend.safety import (
    escape_frontend_text,
    safe_relative_artifact_path,
)


def _status_label(status_value: str) -> str:
    """Map a workflow status to a human-readable label."""
    labels = {
        "completed": "Completed",
        "completed_with_warnings": "Completed (Warnings)",
        "failed": "Failed",
    }
    return labels.get(status_value, status_value)


def _display_resume_type(raw: str) -> str:
    """Convert resume_type enum value to display-friendly label."""
    if not raw:
        return ""
    return raw.replace("_", " ").title()


def _display_template_id(raw: str) -> str:
    """Convert template_id to display-friendly label."""
    if not raw:
        return ""
    return raw.replace("_", " ").title()


def _count_completed_stages(workflow_result: ResumeWorkflowResult) -> int:
    """Count stages that completed (with or without warnings)."""
    completed = 0
    for stage in workflow_result.stages:
        st = stage.status.value
        if st in ("completed", "completed_with_warnings"):
            completed += 1
    return completed


def _build_stage_views(
    workflow_result: ResumeWorkflowResult,
    output_dir: str,
) -> list[dict]:
    """Convert workflow stage results into frontend-safe stage views."""

    views: list[dict] = []
    for stage in workflow_result.stages:
        views.append({
            "stage": escape_frontend_text(stage.stage.value),
            "status": escape_frontend_text(stage.status.value),
            "message": escape_frontend_text(stage.message),
            "warnings_count": len(stage.warnings),
            "errors_count": len(stage.errors),
        })
    return views


def _build_artifact_links(
    workflow_result: ResumeWorkflowResult,
    output_dir: str,
) -> list[dict]:
    """Build safe artifact links relative to the output directory."""

    links: list[dict] = []
    for artifact in workflow_result.artifacts:
        rel_path = safe_relative_artifact_path(artifact.path, output_dir)
        links.append({
            "label": escape_frontend_text(artifact.artifact_type),
            "path": rel_path,
            "artifact_type": escape_frontend_text(artifact.artifact_type),
            "description": escape_frontend_text(artifact.description or ""),
        })
    return links


def build_frontend_page_context(
    workflow_input: ResumeWorkflowInput,
    workflow_result: ResumeWorkflowResult,
    options: FrontendPageOptions | None = None,
) -> dict:
    """Build a Jinja2 context dict for the static workflow dashboard page.

    The returned dict is safe for HTML rendering — all user-supplied text
    is escaped, artifact paths are constrained to the output directory,
    and no hiring-probability or internal-screening claims are included.
    """

    opts = options or FrontendPageOptions()
    output_dir = workflow_result.output_dir

    # --- safe scalar values ---
    status = escape_frontend_text(workflow_result.status.value)
    criteria_id = escape_frontend_text(
        workflow_result.selected_criteria_profile_id or ""
    )
    primary_type = escape_frontend_text(
        workflow_result.primary_resume_type.value
        if workflow_result.primary_resume_type
        else ""
    )
    template_id = escape_frontend_text(
        workflow_result.selected_template_id or ""
    )
    target_role = escape_frontend_text(
        workflow_input.target_role
        or (workflow_input.user_profile.target_roles[0]
            if workflow_input.user_profile.target_roles
            else "")
    )
    page_title = "Resume PDF Agent — Workflow Dashboard"

    # --- safe output paths ---
    html_output_rel = ""
    pdf_output_rel = ""
    if workflow_result.html_output_path:
        html_output_rel = safe_relative_artifact_path(
            workflow_result.html_output_path, output_dir
        )
    if workflow_result.pdf_output_path:
        pdf_output_rel = safe_relative_artifact_path(
            workflow_result.pdf_output_path, output_dir
        )

    # --- conversion reminder (outside resume body) ---
    conversion_reminder = escape_frontend_text(
        workflow_result.conversion_reminder or ""
    )

    # --- warnings & errors ---
    warnings_list = [escape_frontend_text(w) for w in workflow_result.warnings]
    errors_list = [escape_frontend_text(e) for e in workflow_result.errors]

    # --- input summary (no raw full content) ---
    input_summary = {
        "full_name": escape_frontend_text(
            workflow_input.user_profile.full_name
        ),
        "education_count": len(workflow_input.user_profile.education),
        "experience_count": len(workflow_input.resume_content.experiences),
        "skill_group_count": len(workflow_input.user_profile.skills),
        "target_role": target_role,
    }

    # --- stage timeline ---
    stage_views = _build_stage_views(workflow_result, output_dir)

    # --- artifact links ---
    artifact_links = _build_artifact_links(workflow_result, output_dir)

    # --- M14 confirmation paths ---
    confirmation_packet_rel = ""
    confirmation_review_rel = ""
    if getattr(workflow_result, "confirmation_packet_path", None):
        confirmation_packet_rel = safe_relative_artifact_path(
            workflow_result.confirmation_packet_path, output_dir
        )
    if getattr(workflow_result, "confirmation_review_path", None):
        confirmation_review_rel = safe_relative_artifact_path(
            workflow_result.confirmation_review_path, output_dir
        )

    # M15 JD paths
    parsed_jd_rel = ""
    jd_criteria_profile_rel = ""
    if getattr(workflow_result, "parsed_jd_path", None):
        parsed_jd_rel = safe_relative_artifact_path(
            workflow_result.parsed_jd_path, output_dir
        )
    if getattr(workflow_result, "jd_criteria_profile_path", None):
        jd_criteria_profile_rel = safe_relative_artifact_path(
            workflow_result.jd_criteria_profile_path, output_dir
        )

    # M16 LLM paths
    llm_rewrite_result_rel = ""
    if getattr(workflow_result, "llm_rewrite_result_path", None):
        llm_rewrite_result_rel = safe_relative_artifact_path(
            workflow_result.llm_rewrite_result_path, output_dir
        )

    return {
        "page_title": page_title,
        "status": status,
        "status_label": _status_label(workflow_result.status.value),
        "output_dir": escape_frontend_text(output_dir),
        "selected_criteria_profile_id": criteria_id,
        "primary_resume_type": primary_type,
        "primary_resume_type_display": _display_resume_type(primary_type),
        "selected_template_id": template_id,
        "selected_template_id_display": _display_template_id(template_id),
        "html_output_path": html_output_rel,
        "pdf_output_path": pdf_output_rel,
        "conversion_reminder": conversion_reminder,
        "warnings": warnings_list,
        "errors": errors_list,
        "warnings_count": len(warnings_list),
        "errors_count": len(errors_list),
        "stages_completed": _count_completed_stages(workflow_result),
        "stages_total": len(workflow_result.stages),
        "stage_views": stage_views,
        "artifact_links": artifact_links,
        "input_summary": input_summary,
        "options": {
            "include_artifact_links": opts.include_artifact_links,
            "include_stage_timeline": opts.include_stage_timeline,
            "include_warnings": opts.include_warnings,
            "include_errors": opts.include_errors,
            "include_resume_html_link": opts.include_resume_html_link,
            "include_pdf_link": opts.include_pdf_link,
            "include_conversion_reminder": opts.include_conversion_reminder,
            "language": opts.language,
        },
        "summary": escape_frontend_text(workflow_result.summary),
        # M14 confirmation
        "confirmation_required": getattr(workflow_result, "confirmation_required", False),
        "can_generate_final_pdf": getattr(workflow_result, "can_generate_final_pdf", True),
        "confirmation_packet_path": confirmation_packet_rel,
        "confirmation_review_path": confirmation_review_rel,
        # M15 JD
        "used_user_provided_jd": getattr(workflow_result, "used_user_provided_jd", False),
        "jd_compliance_status": getattr(workflow_result, "jd_compliance_status", ""),
        "parsed_jd_path": parsed_jd_rel,
        "jd_criteria_profile_path": jd_criteria_profile_rel,
        # M16 LLM
        "llm_rewriting_used": getattr(workflow_result, "llm_rewriting_used", False),
        "llm_rewrite_result_path": llm_rewrite_result_rel,
    }
