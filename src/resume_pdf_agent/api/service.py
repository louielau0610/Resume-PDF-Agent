"""API service functions for M19 optional API layer.

Wraps the existing deterministic workflow behind API-style request/response
models without duplicating business logic.
"""

from __future__ import annotations

from importlib.metadata import version as _get_version
from importlib.util import find_spec
from pathlib import Path

from resume_pdf_agent.api.models import (
    APIArtifactView,
    APIHealthResponse,
    APIWorkflowMode,
    APIWorkflowRequest,
    APIWorkflowResponse,
)
from resume_pdf_agent.models.pdf import PDFBackend

_SAMPLE_INPUT_PATH = (
    Path(__file__).resolve().parent.parent.parent.parent
    / "data"
    / "sample_inputs"
    / "sample_data_science_user.json"
)


def build_api_health_response() -> APIHealthResponse:
    """Build a health check response showing feature and dependency status.

    Returns
    -------
    APIHealthResponse
    """
    try:
        pkg_version = _get_version("resume-pdf-agent")
    except Exception:
        pkg_version = None

    features = [
        "criteria_selection",
        "resume_classification",
        "gap_analysis",
        "truthfulness_check",
        "bullet_enhancement",
        "template_matching",
        "html_rendering",
        "pdf_generation",
        "workflow_orchestration",
        "frontend_dashboard",
        "user_confirmation",
        "jd_parser",
        "llm_rewrite",
        "pdf_diagnostics",
        "visual_regression",
    ]

    opt_deps = {
        "fastapi": find_spec("fastapi") is not None,
        "uvicorn": find_spec("uvicorn") is not None,
        "weasyprint": find_spec("weasyprint") is not None,
        "playwright": find_spec("playwright") is not None,
    }

    return APIHealthResponse(
        version=pkg_version,
        available_features=features,
        optional_dependencies=opt_deps,
        summary=(
            f"Resume PDF Agent API is available. "
            f"FastAPI: {'installed' if opt_deps['fastapi'] else 'not installed'}. "
            f"Uvicorn: {'installed' if opt_deps['uvicorn'] else 'not installed'}."
        ),
    )


def run_workflow_from_api_request(
    request: APIWorkflowRequest,
) -> APIWorkflowResponse:
    """Run the resume workflow from an API request.

    Parameters
    ----------
    request : APIWorkflowRequest
        The API request with workflow parameters.

    Returns
    -------
    APIWorkflowResponse
        Structured response with output paths and status.
    """
    from resume_pdf_agent.workflow.io import load_workflow_input_from_json
    from resume_pdf_agent.workflow.orchestrator import run_resume_workflow

    # ── Load input ──────────────────────────────────────────────────
    if request.mode == APIWorkflowMode.SAMPLE:
        if not _SAMPLE_INPUT_PATH.is_file():
            raise FileNotFoundError(
                f"Sample input not found: {_SAMPLE_INPUT_PATH}"
            )
        workflow_input = load_workflow_input_from_json(_SAMPLE_INPUT_PATH)
    elif request.workflow_input is not None:
        workflow_input = request.workflow_input
    else:
        raise ValueError(
            "workflow_input is required when mode is 'custom'"
        )

    # ── Apply overrides ─────────────────────────────────────────────
    workflow_input.output_dir = request.output_dir
    workflow_input.pdf_backend = PDFBackend(request.pdf_backend)

    if request.use_user_provided_jd:
        workflow_input.use_user_provided_jd = True
        if request.jd_file_path:
            workflow_input.jd_file_path = request.jd_file_path
        if request.jd_text:
            workflow_input.jd_text = request.jd_text

    workflow_input.require_confirmation_before_pdf = (
        request.require_confirmation_before_pdf
    )

    if request.enable_llm_rewriting:
        workflow_input.enable_llm_rewriting = True
        if request.llm_provider:
            workflow_input.llm_provider = request.llm_provider

    # ── Run workflow ────────────────────────────────────────────────
    result = run_resume_workflow(workflow_input)

    # ── Generate frontend page if requested ─────────────────────────
    frontend_path: str | None = None
    if request.write_frontend_page:
        try:
            from resume_pdf_agent.frontend import render_frontend_workflow_page

            page_result = render_frontend_workflow_page(
                workflow_input=workflow_input,
                workflow_result=result,
                output_path=Path(request.output_dir) / "index.html",
            )
            if page_result.output_path:
                frontend_path = str(page_result.output_path)
        except Exception:
            pass

    # ── List artifacts ──────────────────────────────────────────────
    artifacts = list_api_artifacts(request.output_dir)

    # ── Build response ──────────────────────────────────────────────
    return APIWorkflowResponse(
        status=result.status.value,
        output_dir=result.output_dir,
        selected_criteria_profile_id=result.selected_criteria_profile_id,
        primary_resume_type=(
            result.primary_resume_type.value
            if result.primary_resume_type
            else None
        ),
        selected_template_id=result.selected_template_id,
        html_output_path=result.html_output_path,
        pdf_output_path=result.pdf_output_path,
        frontend_page_path=frontend_path,
        confirmation_packet_path=result.confirmation_packet_path,
        parsed_jd_path=result.parsed_jd_path,
        jd_criteria_profile_path=result.jd_criteria_profile_path,
        llm_rewrite_result_path=result.llm_rewrite_result_path,
        warnings=list(result.warnings),
        errors=list(result.errors),
        artifacts=artifacts,
        summary=result.summary,
    )


def list_api_artifacts(output_dir: str | Path) -> list[APIArtifactView]:
    """List expected workflow artifacts under an output directory.

    Parameters
    ----------
    output_dir : str | Path
        Path to the workflow output directory.

    Returns
    -------
    list[APIArtifactView]
        List of artifact views with existence status.
    """
    od = Path(output_dir)
    expected = [
        ("index.html", "Frontend dashboard page"),
        ("resume.html", "Rendered resume HTML"),
        ("resume.pdf", "Generated resume PDF"),
        ("workflow_result.json", "Complete workflow result"),
        ("criteria_profile.json", "Selected criteria profile"),
        ("classification.json", "Resume type classification"),
        ("gap_analysis.json", "Gap analysis result"),
        ("truthfulness.json", "Truthfulness check result"),
        ("enhancement.json", "Bullet enhancement result"),
        ("template_selection.json", "Template selection result"),
        ("confirmation_packet.json", "User confirmation packet"),
        ("confirmation_review.md", "Confirmation review document"),
        ("parsed_jd.json", "Parsed job description"),
        ("jd_criteria_profile.json", "JD-derived criteria profile"),
        ("llm_rewrite_result.json", "LLM rewrite result"),
    ]

    artifacts: list[APIArtifactView] = []
    for name, desc in expected:
        file_path = od / name
        artifacts.append(
            APIArtifactView(
                artifact_type=name.rsplit(".", 1)[-1],
                path=str(file_path),
                description=desc,
                exists=file_path.is_file(),
            )
        )
    return artifacts
