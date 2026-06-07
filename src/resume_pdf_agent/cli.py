"""Typer CLI entry point for resume_pdf_agent."""

from __future__ import annotations

from pathlib import Path

import typer

from resume_pdf_agent.models import PDFBackend
from resume_pdf_agent.models.frontend import FrontendPageOptions
from resume_pdf_agent.models.workflow import ResumeWorkflowInput, WorkflowRunStatus
from resume_pdf_agent.workflow import load_workflow_input_from_json, run_resume_workflow

_SAMPLE_INPUT_PATH = (
    Path(__file__).resolve().parent.parent.parent
    / "data"
    / "sample_inputs"
    / "sample_data_science_user.json"
)


app = typer.Typer(
    name="resume-pdf-agent",
    help="Criteria-aware AI resume PDF generation agent CLI.",
    no_args_is_help=True,
)

_criteria_app = typer.Typer(help="Criteria profile commands.")
_templates_app = typer.Typer(help="Template commands.")

app.add_typer(_criteria_app, name="criteria")
app.add_typer(_templates_app, name="templates")


def _print_summary(result, output_dir: str) -> None:
    """Print a concise workflow result summary."""

    typer.echo(f"Status:              {result.status.value}")
    typer.echo(f"Output directory:    {output_dir}")
    typer.echo(f"Criteria profile:    {result.selected_criteria_profile_id or 'N/A'}")
    typer.echo(f"Primary resume type: {result.primary_resume_type.value if result.primary_resume_type else 'N/A'}")
    typer.echo(f"Selected template:   {result.selected_template_id or 'N/A'}")
    typer.echo(f"HTML output:         {result.html_output_path or 'N/A'}")
    typer.echo(f"PDF output:          {result.pdf_output_path or 'N/A'}")
    typer.echo(f"Warnings:            {len(result.warnings)}")
    typer.echo(f"Errors:              {len(result.errors)}")
    # M14 confirmation
    if result.confirmation_packet_path:
        typer.echo(f"Confirmation packet: {result.confirmation_packet_path}")
    if result.confirmation_review_path:
        typer.echo(f"Confirmation review: {result.confirmation_review_path}")
    if result.confirmation_required:
        typer.echo(f"Confirmation:        REQUIRED before final PDF")
    typer.echo(f"Can generate PDF:    {result.can_generate_final_pdf}")
    # M15 JD
    if result.used_user_provided_jd:
        typer.echo(f"JD used:             Yes (compliance: {result.jd_compliance_status or 'N/A'})")
        if result.parsed_jd_path:
            typer.echo(f"Parsed JD:           {result.parsed_jd_path}")
        if result.jd_criteria_profile_path:
            typer.echo(f"JD criteria profile: {result.jd_criteria_profile_path}")
    # M16 LLM
    if result.llm_rewriting_used:
        typer.echo(f"LLM rewriting:       Used (result: {result.llm_rewrite_result_path or 'N/A'})")
    # M20 confirmation UI
    if result.confirmation_ui_path:
        typer.echo(f"Confirmation UI:     {result.confirmation_ui_path}")


def _write_frontend_page_if_enabled(
    workflow_input: ResumeWorkflowInput,
    result,
    output_dir: str,
) -> None:
    """Render frontend page if --write-frontend-page was passed."""
    from resume_pdf_agent.frontend import render_frontend_workflow_page

    page_result = render_frontend_workflow_page(
        workflow_input=workflow_input,
        workflow_result=result,
        output_path=Path(output_dir) / "index.html",
    )
    if page_result.output_path:
        typer.echo(f"Frontend page:       {page_result.output_path}")
    if page_result.warnings:
        typer.echo(f"Frontend warnings:   {len(page_result.warnings)}")
    if page_result.errors:
        typer.echo(f"Frontend errors:     {len(page_result.errors)}")


@app.command("run")
def run_workflow(
    input_path: Path = typer.Option(
        ..., "--input", "-i",
        exists=True, file_okay=True, dir_okay=False, readable=True,
        help="Path to workflow input JSON file.",
    ),
    output_dir: str = typer.Option(
        "outputs/custom_run", "--output-dir", "-o",
        help="Output directory for generated artifacts.",
    ),
    pdf_backend: str = typer.Option(
        "mock", "--pdf-backend",
        help="PDF backend: mock, weasyprint, or playwright.",
    ),
    write_frontend_page: bool = typer.Option(
        False, "--write-frontend-page",
        help="Also render a static index.html workflow dashboard page.",
    ),
    require_confirmation_before_pdf: bool = typer.Option(
        False, "--require-confirmation-before-pdf",
        help="Require user confirmation before final PDF generation.",
    ),
    write_confirmation_packet: bool = typer.Option(
        True, "--write-confirmation-packet/--no-write-confirmation-packet",
        help="Write confirmation_packet.json and confirmation_review.md.",
    ),
    confirmation_decisions: str | None = typer.Option(
        None, "--confirmation-decisions",
        help="Path to confirmation decisions JSON file to apply.",
    ),
    # M15 JD options
    jd_file: str | None = typer.Option(
        None, "--jd-file",
        exists=False,
        help="Path to a local JD text file to use as criteria source.",
    ),
    use_user_provided_jd: bool = typer.Option(
        False, "--use-user-provided-jd/--no-use-user-provided-jd",
        help="Use user-provided JD as criteria source instead of static profiles.",
    ),
    write_jd_artifacts: bool = typer.Option(
        True, "--write-jd-artifacts/--no-write-jd-artifacts",
        help="Write parsed JD and JD-derived criteria artifacts.",
    ),
    # M16 LLM options
    enable_llm_rewriting: bool = typer.Option(
        False, "--enable-llm-rewriting/--no-enable-llm-rewriting",
        help="Enable optional LLM-assisted bullet rewriting (disabled by default).",
    ),
    llm_provider: str = typer.Option(
        "mock", "--llm-provider",
        help="LLM provider: mock (deterministic test), external (placeholder), or disabled.",
    ),
    write_llm_artifacts: bool = typer.Option(
        True, "--write-llm-artifacts/--no-write-llm-artifacts",
        help="Write LLM rewrite result artifact.",
    ),
    # M20 confirmation UI
    write_confirmation_ui: bool = typer.Option(
        False, "--write-confirmation-ui/--no-write-confirmation-ui",
        help="Write a browser confirmation review page (confirmation.html).",
    ),
) -> None:
    """Run the resume workflow from an explicit JSON input file."""

    workflow_input = load_workflow_input_from_json(input_path)

    # CLI overrides
    workflow_input.output_dir = output_dir
    try:
        workflow_input.pdf_backend = PDFBackend(pdf_backend)
    except ValueError:
        typer.echo(f"Error: Unknown PDF backend '{pdf_backend}'.", err=True)
        raise typer.Exit(code=2)

    # M14 overrides
    workflow_input.require_confirmation_before_pdf = require_confirmation_before_pdf
    workflow_input.write_confirmation_packet = write_confirmation_packet
    workflow_input.confirmation_decisions_path = confirmation_decisions
    # M15 JD overrides
    if jd_file:
        workflow_input.jd_file_path = jd_file
        workflow_input.use_user_provided_jd = True
    if use_user_provided_jd:
        workflow_input.use_user_provided_jd = True
    workflow_input.write_jd_artifacts = write_jd_artifacts
    # M16 LLM overrides
    workflow_input.enable_llm_rewriting = enable_llm_rewriting
    workflow_input.llm_provider = llm_provider
    workflow_input.write_llm_artifacts = write_llm_artifacts
    # M20 overrides
    workflow_input.write_confirmation_ui = write_confirmation_ui

    result = run_resume_workflow(workflow_input)
    _print_summary(result, output_dir)

    if write_frontend_page:
        _write_frontend_page_if_enabled(workflow_input, result, output_dir)

    if result.status == WorkflowRunStatus.FAILED:
        raise typer.Exit(code=1)


@app.command("run-sample")
def run_sample(
    output_dir: str = typer.Option(
        "outputs/sample_run", "--output-dir", "-o",
        help="Output directory for generated artifacts.",
    ),
    pdf_backend: str = typer.Option(
        "mock", "--pdf-backend",
        help="PDF backend: mock, weasyprint, or playwright.",
    ),
    write_frontend_page: bool = typer.Option(
        False, "--write-frontend-page",
        help="Also render a static index.html workflow dashboard page.",
    ),
    require_confirmation_before_pdf: bool = typer.Option(
        False, "--require-confirmation-before-pdf",
        help="Require user confirmation before final PDF generation.",
    ),
    write_confirmation_packet: bool = typer.Option(
        True, "--write-confirmation-packet/--no-write-confirmation-packet",
        help="Write confirmation_packet.json and confirmation_review.md.",
    ),
    confirmation_decisions: str | None = typer.Option(
        None, "--confirmation-decisions",
        help="Path to confirmation decisions JSON file to apply.",
    ),
    # M15 JD options
    jd_file: str | None = typer.Option(
        None, "--jd-file",
        exists=False,
        help="Path to a local JD text file to use as criteria source.",
    ),
    use_user_provided_jd: bool = typer.Option(
        False, "--use-user-provided-jd/--no-use-user-provided-jd",
        help="Use user-provided JD as criteria source instead of static profiles.",
    ),
    write_jd_artifacts: bool = typer.Option(
        True, "--write-jd-artifacts/--no-write-jd-artifacts",
        help="Write parsed JD and JD-derived criteria artifacts.",
    ),
    # M16 LLM options
    enable_llm_rewriting: bool = typer.Option(
        False, "--enable-llm-rewriting/--no-enable-llm-rewriting",
        help="Enable optional LLM-assisted bullet rewriting (disabled by default).",
    ),
    llm_provider: str = typer.Option(
        "mock", "--llm-provider",
        help="LLM provider: mock (deterministic test), external (placeholder), or disabled.",
    ),
    write_llm_artifacts: bool = typer.Option(
        True, "--write-llm-artifacts/--no-write-llm-artifacts",
        help="Write LLM rewrite result artifact.",
    ),
    # M20 confirmation UI
    write_confirmation_ui: bool = typer.Option(
        False, "--write-confirmation-ui/--no-write-confirmation-ui",
        help="Write a browser confirmation review page (confirmation.html).",
    ),
) -> None:
    """Run the resume workflow using built-in sample data."""

    if not _SAMPLE_INPUT_PATH.is_file():
        typer.echo(
            f"Error: Sample data not found at {_SAMPLE_INPUT_PATH}.",
            err=True,
        )
        raise typer.Exit(code=2)

    workflow_input = load_workflow_input_from_json(_SAMPLE_INPUT_PATH)
    workflow_input.output_dir = output_dir
    try:
        workflow_input.pdf_backend = PDFBackend(pdf_backend)
    except ValueError:
        typer.echo(f"Error: Unknown PDF backend '{pdf_backend}'.", err=True)
        raise typer.Exit(code=2)

    # M14 overrides
    workflow_input.require_confirmation_before_pdf = require_confirmation_before_pdf
    workflow_input.write_confirmation_packet = write_confirmation_packet
    workflow_input.confirmation_decisions_path = confirmation_decisions
    # M15 JD overrides
    if jd_file:
        workflow_input.jd_file_path = jd_file
        workflow_input.use_user_provided_jd = True
    if use_user_provided_jd:
        workflow_input.use_user_provided_jd = True
    workflow_input.write_jd_artifacts = write_jd_artifacts
    # M16 LLM overrides
    workflow_input.enable_llm_rewriting = enable_llm_rewriting
    workflow_input.llm_provider = llm_provider
    workflow_input.write_llm_artifacts = write_llm_artifacts
    # M20 overrides
    workflow_input.write_confirmation_ui = write_confirmation_ui

    result = run_resume_workflow(workflow_input)
    _print_summary(result, output_dir)

    if write_frontend_page:
        _write_frontend_page_if_enabled(workflow_input, result, output_dir)

    if result.status == WorkflowRunStatus.FAILED:
        raise typer.Exit(code=1)


@app.command("list-criteria")
def list_criteria() -> None:
    """List available criteria profile IDs."""

    from resume_pdf_agent.criteria import get_available_profile_ids

    ids = get_available_profile_ids()
    typer.echo("Available criteria profile IDs:")
    for pid in ids:
        typer.echo(f"  - {pid}")


@app.command("list-templates")
def list_templates() -> None:
    """List available internal template IDs."""

    from resume_pdf_agent.templates import get_available_template_ids

    ids = get_available_template_ids()
    typer.echo("Available internal template IDs:")
    for tid in ids:
        typer.echo(f"  - {tid}")


@app.command("render-page")
def render_page(
    input_path: Path = typer.Option(
        ..., "--input", "-i",
        exists=True, file_okay=True, dir_okay=False, readable=True,
        help="Path to workflow input JSON file.",
    ),
    output_dir: str = typer.Option(
        "outputs/page_run", "--output-dir", "-o",
        help="Output directory for generated artifacts.",
    ),
    pdf_backend: str = typer.Option(
        "mock", "--pdf-backend",
        help="PDF backend: mock, weasyprint, or playwright.",
    ),
) -> None:
    """Run the full workflow and render a static index.html dashboard page."""

    from resume_pdf_agent.frontend import render_frontend_workflow_page

    workflow_input = load_workflow_input_from_json(input_path)
    workflow_input.output_dir = output_dir
    try:
        workflow_input.pdf_backend = PDFBackend(pdf_backend)
    except ValueError:
        typer.echo(f"Error: Unknown PDF backend '{pdf_backend}'.", err=True)
        raise typer.Exit(code=2)

    result = run_resume_workflow(workflow_input)
    _print_summary(result, output_dir)

    page_result = render_frontend_workflow_page(
        workflow_input=workflow_input,
        workflow_result=result,
        output_path=Path(output_dir) / "index.html",
    )
    if page_result.output_path:
        typer.echo(f"Frontend page:       {page_result.output_path}")

    if result.status == WorkflowRunStatus.FAILED:
        raise typer.Exit(code=1)


@app.command("check-pdf-backend")
def check_pdf_backend(
    backend: str = typer.Option(
        "all", "--backend",
        help="PDF backend to check: mock, weasyprint, playwright, or all.",
    ),
    output_dir: str | None = typer.Option(
        None, "--output-dir", "-o",
        help="Optional output directory for smoke test artifacts.",
    ),
    strict: bool = typer.Option(
        False, "--strict/--no-strict",
        help="Exit with non-zero if backend is unavailable.",
    ),
) -> None:
    """Check availability of PDF backends."""
    from resume_pdf_agent.models.pdf import PDFBackend
    from resume_pdf_agent.pdf.diagnostics import (
        get_all_pdf_backend_diagnostics,
        get_pdf_backend_diagnostics,
        summarize_pdf_backend_status,
    )

    typer.echo(summarize_pdf_backend_status())
    typer.echo()

    if backend == "all":
        backends = [PDFBackend.MOCK, PDFBackend.WEASYPRINT, PDFBackend.PLAYWRIGHT]
    else:
        try:
            backends = [PDFBackend(backend)]
        except ValueError:
            typer.echo(f"Error: Unknown backend '{backend}'.", err=True)
            raise typer.Exit(code=2)

    all_available = True
    for b in backends:
        diag = get_pdf_backend_diagnostics(b)
        status = "OK" if diag["available"] else "MISSING"
        typer.echo(f"[{status}] {b.value}: {diag['setup_hint']}")
        if not diag["available"]:
            all_available = False

    if output_dir and PDFBackend.MOCK in backends:
        typer.echo("\nRunning mock backend smoke test ...")
        try:
            from pathlib import Path
            from resume_pdf_agent.models.pdf import PDFGenerationOptions
            from resume_pdf_agent.models.rendering import HTMLRenderResult, HTMLRenderStatus
            from resume_pdf_agent.pdf.generator import generate_pdf_from_html_result

            od = Path(output_dir)
            od.mkdir(parents=True, exist_ok=True)
            html_result = HTMLRenderResult(
                status=HTMLRenderStatus.RENDERED,
                template_id="smoke_test",
                html="<html><body><p>Smoke test</p></body></html>",
                sections=[],
                summary="Smoke test.",
                output_path=str(od / "smoke_test.html"),
            )
            pdf_result = generate_pdf_from_html_result(
                html_render_result=html_result,
                output_path=od / "smoke_test.pdf",
                options=PDFGenerationOptions(backend=PDFBackend.MOCK),
            )
            typer.echo(f"  Smoke test PDF: {pdf_result.output_path or 'not generated'}")
        except Exception as exc:
            typer.echo(f"  Smoke test error: {exc}")

    if strict and not all_available:
        typer.echo("\nStrict mode: some backends are unavailable.", err=True)
        raise typer.Exit(code=1)


@app.command("render-confirmation-ui")
def render_confirmation_ui(
    packet_path: str = typer.Option(
        ..., "--packet",
        help="Path to confirmation_packet.json file.",
    ),
    output: str = typer.Option(
        ..., "--output",
        help="Output path for confirmation.html.",
    ),
) -> None:
    """Render a static browser confirmation review page from a confirmation packet."""
    from resume_pdf_agent.confirmation_ui import render_confirmation_ui_from_packet_file

    result = render_confirmation_ui_from_packet_file(packet_path, output)
    if result.output_path:
        typer.echo(f"Confirmation UI:      {result.output_path}")
        typer.echo(f"Items:                {result.item_count}")
        typer.echo(f"Blocking:             {result.blocking_count}")
    if result.errors:
        for e in result.errors:
            typer.echo(f"Error: {e}", err=True)
        raise typer.Exit(code=1)


@app.command("render-jd-upload-ui")
def render_jd_upload_ui(
    output: str = typer.Option(
        "outputs/jd_upload_ui/jd_upload.html", "--output",
        help="Output path for jd_upload.html.",
    ),
) -> None:
    """Render a static browser JD intake page for preparing JD input."""
    from resume_pdf_agent.jd_ui import render_jd_upload_ui_page

    result = render_jd_upload_ui_page(output)
    if result.output_path:
        typer.echo(f"JD Upload UI:         {result.output_path}")
    if result.errors:
        for e in result.errors:
            typer.echo(f"Error: {e}", err=True)
        raise typer.Exit(code=1)


@app.command("render-llm-review-ui")
def render_llm_review_ui(
    result_path: str = typer.Option(
        ..., "--result",
        help="Path to llm_rewrite_result.json.",
    ),
    output: str = typer.Option(
        "outputs/llm_review/llm_review.html", "--output",
        help="Output path for llm_review.html.",
    ),
) -> None:
    """Render a static browser LLM rewrite review page from an llm_rewrite_result.json."""
    from resume_pdf_agent.llm_review_ui import render_llm_review_ui_from_result_file

    result = render_llm_review_ui_from_result_file(result_path, output)
    if result.output_path:
        typer.echo(f"LLM Review UI:        {result.output_path}")
        typer.echo(f"Candidates:           {result.candidate_count}")
        typer.echo(f"Needs confirmation:   {result.candidates_requiring_confirmation}")
    if result.errors:
        for e in result.errors:
            typer.echo(f"Error: {e}", err=True)
        raise typer.Exit(code=1)


if __name__ == "__main__":
    app()
