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


if __name__ == "__main__":
    app()
