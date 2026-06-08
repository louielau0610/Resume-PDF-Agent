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
    # M23 LLM review decision summary
    if result.llm_review_decision_summary_json_path:
        typer.echo(f"LLM review summary:  {result.llm_review_decision_summary_json_path}")
    if result.llm_review_decision_summary_md_path:
        typer.echo(f"LLM review summary:  {result.llm_review_decision_summary_md_path}")
    # M24 LLM application plan
    if result.llm_application_plan_json_path:
        typer.echo(f"LLM app plan:        {result.llm_application_plan_json_path}")
    if result.llm_application_plan_md_path:
        typer.echo(f"LLM app plan:        {result.llm_application_plan_md_path}")
    # M25 LLM application preview UI
    if result.llm_application_preview_ui_path:
        typer.echo(f"LLM app preview UI:  {result.llm_application_preview_ui_path}")


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
    llm_review_decisions: str | None = typer.Option(
        None, "--llm-review-decisions",
        help="Path to llm_rewrite_review_decisions.json for advisory summary generation.",
    ),
    write_llm_review_decision_summary: bool = typer.Option(
        False, "--write-llm-review-decision-summary/--no-write-llm-review-decision-summary",
        help="Write advisory LLM review decision summary artifacts.",
    ),
    write_llm_application_plan: bool = typer.Option(
        False, "--write-llm-application-plan/--no-write-llm-application-plan",
        help="Write plan-only LLM candidate application artifacts.",
    ),
    write_llm_application_preview_ui: bool = typer.Option(
        False, "--write-llm-application-preview-ui/--no-write-llm-application-preview-ui",
        help="Write a local static manual LLM candidate application preview page.",
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
    # M23 overrides
    workflow_input.llm_review_decisions_path = llm_review_decisions
    workflow_input.write_llm_review_decision_summary = write_llm_review_decision_summary
    workflow_input.write_llm_application_plan = write_llm_application_plan
    workflow_input.write_llm_application_preview_ui = write_llm_application_preview_ui

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
    llm_review_decisions: str | None = typer.Option(
        None, "--llm-review-decisions",
        help="Path to llm_rewrite_review_decisions.json for advisory summary generation.",
    ),
    write_llm_review_decision_summary: bool = typer.Option(
        False, "--write-llm-review-decision-summary/--no-write-llm-review-decision-summary",
        help="Write advisory LLM review decision summary artifacts.",
    ),
    write_llm_application_plan: bool = typer.Option(
        False, "--write-llm-application-plan/--no-write-llm-application-plan",
        help="Write plan-only LLM candidate application artifacts.",
    ),
    write_llm_application_preview_ui: bool = typer.Option(
        False, "--write-llm-application-preview-ui/--no-write-llm-application-preview-ui",
        help="Write a local static manual LLM candidate application preview page.",
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
    # M23 overrides
    workflow_input.llm_review_decisions_path = llm_review_decisions
    workflow_input.write_llm_review_decision_summary = write_llm_review_decision_summary
    workflow_input.write_llm_application_plan = write_llm_application_plan
    workflow_input.write_llm_application_preview_ui = write_llm_application_preview_ui

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


@app.command("summarize-llm-review-decisions")
def summarize_llm_review_decisions(
    decisions_path: str = typer.Option(
        ..., "--decisions",
        help="Path to llm_rewrite_review_decisions.json.",
    ),
    result_path: str | None = typer.Option(
        None, "--result",
        help="Optional path to llm_rewrite_result.json for candidate ID cross-checking.",
    ),
    output_json: str | None = typer.Option(
        None, "--output-json",
        help="Optional output path for llm_rewrite_review_decision_summary.json.",
    ),
    output_md: str | None = typer.Option(
        None, "--output-md",
        help="Optional output path for llm_rewrite_review_decision_summary.md.",
    ),
    strict: bool = typer.Option(
        False, "--strict/--no-strict",
        help="Fail on unknown decision actions.",
    ),
) -> None:
    """Summarize local LLM rewrite review decisions without applying candidates."""
    from resume_pdf_agent.llm_review_decisions import summarize_llm_review_decisions_to_files

    try:
        summary = summarize_llm_review_decisions_to_files(
            decisions_path=decisions_path,
            result_path=result_path,
            output_json_path=output_json,
            output_md_path=output_md,
            strict=strict,
        )
    except Exception as exc:
        typer.echo(f"Error: {exc}", err=True)
        raise typer.Exit(code=1)

    typer.echo("LLM Review Decision Summary")
    typer.echo(f"Candidates:           {summary.total_candidates}")
    typer.echo(f"Decisions:            {summary.total_decisions}")
    typer.echo(f"Approved:             {summary.approved_count}")
    typer.echo(f"Rejected:             {summary.rejected_count}")
    typer.echo(f"Needs edit:           {summary.needs_edit_count}")
    typer.echo(f"Notes:                {summary.note_count}")
    typer.echo(f"Ignored:              {summary.ignored_count}")
    typer.echo(f"Warnings:             {len(summary.warnings)}")
    if output_json:
        typer.echo(f"JSON summary:         {output_json}")
    if output_md:
        typer.echo(f"Markdown summary:     {output_md}")


@app.command("plan-llm-candidate-application")
def plan_llm_candidate_application(
    result_path: str = typer.Option(
        ..., "--result",
        help="Path to llm_rewrite_result.json.",
    ),
    decisions_path: str = typer.Option(
        ..., "--decisions",
        help="Path to llm_rewrite_review_decisions.json.",
    ),
    summary_path: str | None = typer.Option(
        None, "--summary",
        help="Optional path to llm_rewrite_review_decision_summary.json.",
    ),
    output_json: str | None = typer.Option(
        None, "--output-json",
        help="Optional output path for llm_rewrite_application_plan.json.",
    ),
    output_md: str | None = typer.Option(
        None, "--output-md",
        help="Optional output path for llm_rewrite_application_plan.md.",
    ),
    strict: bool = typer.Option(
        False, "--strict/--no-strict",
        help="Fail on unknown decision actions.",
    ),
) -> None:
    """Create a plan-only LLM candidate application artifact."""
    from resume_pdf_agent.llm_application_plan import plan_llm_candidate_application_to_files

    try:
        plan = plan_llm_candidate_application_to_files(
            result_path=result_path,
            decisions_path=decisions_path,
            summary_path=summary_path,
            output_json_path=output_json,
            output_md_path=output_md,
            strict=strict,
        )
    except Exception as exc:
        typer.echo(f"Error: {exc}", err=True)
        raise typer.Exit(code=1)

    typer.echo("LLM Candidate Application Plan (plan-only)")
    typer.echo("No candidates were applied; final resume artifacts were not modified.")
    typer.echo(f"Candidates:           {plan.total_candidates}")
    typer.echo(f"Decisions:            {plan.total_decisions}")
    typer.echo(f"Planned:              {plan.planned_count}")
    typer.echo(f"Blocked:              {plan.blocked_count}")
    typer.echo(f"Needs manual edit:    {plan.needs_manual_edit_count}")
    typer.echo(f"Excluded:             {plan.excluded_count}")
    typer.echo(f"Unmapped:             {plan.unmapped_count}")
    typer.echo(f"Warnings:             {len(plan.warnings)}")
    if output_json:
        typer.echo(f"JSON plan:            {output_json}")
    if output_md:
        typer.echo(f"Markdown plan:        {output_md}")


@app.command("render-llm-application-preview-ui")
def render_llm_application_preview_ui(
    plan_path: str = typer.Option(
        ..., "--plan",
        help="Path to llm_rewrite_application_plan.json.",
    ),
    output: str = typer.Option(
        "outputs/llm_application_preview/llm_rewrite_application_preview.html",
        "--output",
        help="Output path for llm_rewrite_application_preview.html.",
    ),
) -> None:
    """Render a local static manual preview page from an M24 application plan."""
    from resume_pdf_agent.llm_application_preview_ui import (
        render_llm_application_preview_ui_from_plan_file,
    )

    result = render_llm_application_preview_ui_from_plan_file(plan_path, output)
    if result.output_path:
        typer.echo("LLM Candidate Application Preview UI (plan-only)")
        typer.echo("No candidates were applied; final resume artifacts were not modified.")
        typer.echo(f"Preview UI:           {result.output_path}")
        typer.echo(f"Candidates:           {result.total_candidates}")
        typer.echo(f"Planned:              {result.planned_count}")
        typer.echo(f"Blocked:              {result.blocked_count}")
        typer.echo(f"Needs manual edit:    {result.needs_manual_edit_count}")
        typer.echo(f"Excluded:             {result.excluded_count}")
        typer.echo(f"Unmapped:             {result.unmapped_count}")
        typer.echo(f"Warnings:             {len(result.warnings)}")
    if result.errors:
        for e in result.errors:
            typer.echo(f"Error: {e}", err=True)
        raise typer.Exit(code=1)


@app.command("validate-llm-pre-application")
def validate_llm_pre_application(
    plan_path: str = typer.Option(
        ..., "--plan",
        help="Path to llm_rewrite_application_plan.json.",
    ),
    result_path: str | None = typer.Option(
        None, "--result",
        help="Optional path to llm_rewrite_result.json for cross-checking.",
    ),
    decisions_path: str | None = typer.Option(
        None, "--decisions",
        help="Optional path to llm_rewrite_review_decisions.json.",
    ),
    summary_path: str | None = typer.Option(
        None, "--summary",
        help="Optional path to llm_rewrite_review_decision_summary.json.",
    ),
    output_json: str | None = typer.Option(
        None, "--output-json",
        help="Optional output path for llm_rewrite_pre_application_validation.json.",
    ),
    output_md: str | None = typer.Option(
        None, "--output-md",
        help="Optional output path for llm_rewrite_pre_application_validation.md.",
    ),
    strict: bool = typer.Option(
        False, "--strict/--no-strict",
        help="Fail on missing optional cross-check files.",
    ),
) -> None:
    """Run strict pre-application validation on an LLM application plan. Validation only — no candidates are applied."""
    from resume_pdf_agent.llm_pre_application_validation import write_pre_application_validation_to_files

    try:
        report = write_pre_application_validation_to_files(
            plan_path=plan_path,
            output_json_path=output_json,
            output_md_path=output_md,
            result_path=result_path,
            decisions_path=decisions_path,
            summary_path=summary_path,
            strict=strict,
        )
    except Exception as exc:
        typer.echo(f"Error: {exc}", err=True)
        raise typer.Exit(code=1)

    typer.echo("Pre-Application Validation Report (validation only)")
    typer.echo("No candidates were applied; no patch was generated.")
    typer.echo(f"Total plan items:     {report.total_plan_items}")
    typer.echo(f"Passed:               {report.passed_count}")
    typer.echo(f"Blocked:              {report.blocked_count}")
    typer.echo(f"Needs manual edit:    {report.needs_manual_edit_count}")
    typer.echo(f"Excluded:             {report.excluded_count}")
    typer.echo(f"Unmapped:             {report.unmapped_count}")
    typer.echo(f"Warnings:             {report.warning_count}")
    typer.echo(f"Can proceed:          {'Yes' if report.can_proceed_to_patch_preview else 'No'}")
    if output_json:
        typer.echo(f"JSON report:          {output_json}")
    if output_md:
        typer.echo(f"Markdown report:      {output_md}")


@app.command("preview-llm-manual-patch")
def preview_llm_manual_patch(
    plan_path: str = typer.Option(
        ..., "--plan",
        help="Path to llm_rewrite_application_plan.json.",
    ),
    validation_path: str = typer.Option(
        ..., "--validation",
        help="Path to llm_rewrite_pre_application_validation.json.",
    ),
    output_json: str | None = typer.Option(
        None, "--output-json",
        help="Optional output path for llm_rewrite_manual_patch_preview.json.",
    ),
    output_md: str | None = typer.Option(
        None, "--output-md",
        help="Optional output path for llm_rewrite_manual_patch_preview.md.",
    ),
    output_html: str | None = typer.Option(
        None, "--output-html",
        help="Optional output path for llm_rewrite_manual_patch_preview.html.",
    ),
    strict: bool = typer.Option(
        False, "--strict/--no-strict",
        help="Not used; reserved for future strict-mode checks.",
    ),
) -> None:
    """Generate manual patch-preview artifacts. Preview only — no candidates are applied and no executable patch is generated."""
    from resume_pdf_agent.llm_manual_patch_preview import write_manual_patch_preview_to_files

    try:
        report = write_manual_patch_preview_to_files(
            plan_path=plan_path,
            validation_path=validation_path,
            output_json_path=output_json,
            output_md_path=output_md,
            output_html_path=output_html,
        )
    except Exception as exc:
        typer.echo(f"Error: {exc}", err=True)
        raise typer.Exit(code=1)

    typer.echo("Manual Patch Preview (preview only)")
    typer.echo("No candidates were applied; no executable patch was generated.")
    typer.echo(f"Total items:          {report.total_items}")
    typer.echo(f"Preview ready:        {report.preview_ready_count}")
    typer.echo(f"Blocked:              {report.blocked_count}")
    typer.echo(f"Needs manual edit:    {report.needs_manual_edit_count}")
    typer.echo(f"Excluded:             {report.excluded_count}")
    typer.echo(f"Unmapped:             {report.unmapped_count}")
    typer.echo(f"Skipped:              {report.skipped_count}")
    if output_json:
        typer.echo(f"JSON preview:         {output_json}")
    if output_md:
        typer.echo(f"Markdown preview:     {output_md}")
    if output_html:
        typer.echo(f"HTML preview:         {output_html}")


@app.command("build-llm-manual-approval-checklist")
def build_llm_manual_approval_checklist(
    preview_path: str = typer.Option(
        ..., "--preview",
        help="Path to llm_rewrite_manual_patch_preview.json.",
    ),
    output_json: str | None = typer.Option(
        None, "--output-json",
        help="Optional output path for llm_rewrite_manual_patch_approval_checklist.json.",
    ),
    output_md: str | None = typer.Option(
        None, "--output-md",
        help="Optional output path for llm_rewrite_manual_patch_approval_checklist.md.",
    ),
    output_html: str | None = typer.Option(
        None, "--output-html",
        help="Optional output path for llm_rewrite_manual_patch_approval_checklist.html.",
    ),
    strict: bool = typer.Option(
        False, "--strict/--no-strict",
        help="Not used; reserved for future strict-mode checks.",
    ),
) -> None:
    """Build a manual approval checklist from M27 patch preview. Checklist only — no final approval granted, no candidates applied."""
    from resume_pdf_agent.llm_manual_approval_checklist import write_manual_approval_checklist_to_files

    try:
        report = write_manual_approval_checklist_to_files(
            preview_path=preview_path,
            output_json_path=output_json,
            output_md_path=output_md,
            output_html_path=output_html,
        )
    except Exception as exc:
        typer.echo(f"Error: {exc}", err=True)
        raise typer.Exit(code=1)

    typer.echo("Manual Approval Checklist (checklist only)")
    typer.echo("No final approval granted; no candidates applied; no executable patch generated.")
    typer.echo(f"Total items:          {report.total_items}")
    typer.echo(f"Review required:      {report.review_required_count}")
    typer.echo(f"Blocked:              {report.blocked_count}")
    typer.echo(f"Needs manual edit:    {report.needs_manual_edit_count}")
    typer.echo(f"Excluded:             {report.excluded_count}")
    typer.echo(f"Unmapped:             {report.unmapped_count}")
    typer.echo(f"Skipped:              {report.skipped_count}")
    if output_json:
        typer.echo(f"JSON checklist:       {output_json}")
    if output_md:
        typer.echo(f"Markdown checklist:   {output_md}")
    if output_html:
        typer.echo(f"HTML checklist:       {output_html}")


if __name__ == "__main__":
    app()
