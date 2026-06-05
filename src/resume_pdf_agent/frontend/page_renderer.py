"""Static frontend workflow page renderer for M11."""

from __future__ import annotations

from pathlib import Path

from jinja2 import Environment, FileSystemLoader

from resume_pdf_agent.frontend.context import build_frontend_page_context
from resume_pdf_agent.frontend.safety import escape_frontend_text
from resume_pdf_agent.models.frontend import (
    FrontendPageOptions,
    FrontendPageResult,
    FrontendPageStatus,
)
from resume_pdf_agent.models.workflow import (
    ResumeWorkflowInput,
    ResumeWorkflowResult,
)
from resume_pdf_agent.workflow.io import ensure_output_dir, load_workflow_input_from_json
from resume_pdf_agent.workflow.orchestrator import run_resume_workflow
from resume_pdf_agent.workflow.serialization import model_to_plain_dict

_FRONTEND_DIR = Path(__file__).resolve().parent
_TEMPLATE_DIR = _FRONTEND_DIR / "templates"
_STATIC_DIR = _FRONTEND_DIR / "static"


def _create_frontend_environment() -> Environment:
    return Environment(
        loader=FileSystemLoader(str(_TEMPLATE_DIR)),
        autoescape=False,  # we handle escaping ourselves in context builder
        trim_blocks=True,
        lstrip_blocks=True,
    )


def _read_static_file(filename: str) -> str:
    path = _STATIC_DIR / filename
    if path.is_file():
        return path.read_text(encoding="utf-8")
    return ""


def render_frontend_workflow_page(
    workflow_input: ResumeWorkflowInput,
    workflow_result: ResumeWorkflowResult,
    output_path: str | Path,
    options: FrontendPageOptions | None = None,
) -> FrontendPageResult:
    """Render a static HTML workflow dashboard page.

    Parameters
    ----------
    workflow_input : ResumeWorkflowInput
        The validated workflow input.
    workflow_result : ResumeWorkflowResult
        The completed workflow result.
    output_path : str | Path
        Where to write the ``index.html`` dashboard file.
    options : FrontendPageOptions | None
        Display options controlling what sections appear.

    Returns
    -------
    FrontendPageResult
        Structured result with status, output_path, html, and metadata.
    """

    opts = options or FrontendPageOptions()
    output_path = Path(output_path)

    try:
        # Build context (all values are already escaped)
        context = build_frontend_page_context(
            workflow_input=workflow_input,
            workflow_result=workflow_result,
            options=opts,
        )

        # Load static assets
        css = _read_static_file("frontend_basic.css")
        js = _read_static_file("frontend_basic.js")

        context["css"] = css
        context["js"] = js

        # Render template
        env = _create_frontend_environment()
        template = env.get_template("workflow_page.html.j2")
        html = template.render(**context)

        # Write output
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(html, encoding="utf-8")

        # Determine status
        warnings: list[str] = []
        if workflow_result.warnings:
            status = FrontendPageStatus.RENDERED_WITH_WARNINGS
            warnings = [
                escape_frontend_text(w) for w in workflow_result.warnings
            ]
        else:
            status = FrontendPageStatus.RENDERED

        summary = (
            f"Frontend workflow page rendered to {output_path}. "
            f"Status: {workflow_result.status.value}. "
            f"Warnings: {len(workflow_result.warnings)}. "
            f"Errors: {len(workflow_result.errors)}."
        )

        return FrontendPageResult(
            status=status,
            output_path=str(output_path),
            html=html,
            warnings=warnings,
            errors=[escape_frontend_text(e) for e in workflow_result.errors],
            summary=summary,
        )

    except Exception as exc:
        return FrontendPageResult(
            status=FrontendPageStatus.FAILED,
            output_path=None,
            html="",
            warnings=[],
            errors=[str(exc)],
            summary=f"Failed to render frontend page: {exc}",
        )


def render_frontend_page_from_output_dir(
    workflow_input_path: str | Path,
    workflow_result_path: str | Path,
    output_path: str | Path,
    options: FrontendPageOptions | None = None,
) -> FrontendPageResult:
    """Load workflow input/result from JSON files and render a dashboard page.

    This is a convenience wrapper that deserializes JSON files, then calls
    :func:`render_frontend_workflow_page`.
    """

    import json

    from resume_pdf_agent.models.workflow import ResumeWorkflowInput, ResumeWorkflowResult

    input_path = Path(workflow_input_path)
    result_path = Path(workflow_result_path)

    if not input_path.is_file():
        raise FileNotFoundError(f"Workflow input file not found: {input_path}")
    if not result_path.is_file():
        raise FileNotFoundError(f"Workflow result file not found: {result_path}")

    workflow_input = load_workflow_input_from_json(input_path)

    raw = json.loads(result_path.read_text(encoding="utf-8"))
    workflow_result = ResumeWorkflowResult(**raw)

    return render_frontend_workflow_page(
        workflow_input=workflow_input,
        workflow_result=workflow_result,
        output_path=output_path,
        options=options,
    )
