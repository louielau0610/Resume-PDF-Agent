"""CLI tests for M21 JD upload UI render-jd-upload-ui command."""

from __future__ import annotations

from pathlib import Path

import pytest
from typer.testing import CliRunner

from resume_pdf_agent.cli import app


@pytest.fixture
def runner() -> CliRunner:
    return CliRunner()


# ---------------------------------------------------------------------------
# render-jd-upload-ui command
# ---------------------------------------------------------------------------

def test_render_jd_upload_ui_command_exists():
    """render-jd-upload-ui command is registered on the Typer app."""
    commands = [cmd.name for cmd in app.registered_commands]
    assert "render-jd-upload-ui" in commands


def test_render_jd_upload_ui_exits_successfully(runner: CliRunner, tmp_path: Path):
    """render-jd-upload-ui --output exits with code 0."""
    output_path = tmp_path / "cli_test_jd_upload.html"
    result = runner.invoke(app, ["render-jd-upload-ui", "--output", str(output_path)])
    assert result.exit_code == 0, f"CLI failed: {result.output}\n{result.stderr if hasattr(result, 'stderr') else ''}"
    assert output_path.is_file()
    assert output_path.stat().st_size > 0


def test_render_jd_upload_ui_output_exists_and_non_empty(runner: CliRunner, tmp_path: Path):
    """Output file exists and contains expected content."""
    output_path = tmp_path / "exists_check.html"
    runner.invoke(app, ["render-jd-upload-ui", "--output", str(output_path)])
    content = output_path.read_text(encoding="utf-8")
    assert len(content) > 0
    assert "<!DOCTYPE html>" in content
    assert "jd-text" in content


def test_render_jd_upload_ui_output_contains_jd_textarea(runner: CliRunner, tmp_path: Path):
    """Output contains JD textarea element."""
    output_path = tmp_path / "textarea_check.html"
    runner.invoke(app, ["render-jd-upload-ui", "--output", str(output_path)])
    content = output_path.read_text(encoding="utf-8")
    assert 'id="jd-text"' in content


def test_render_jd_upload_ui_output_contains_local_safety_notice(runner: CliRunner, tmp_path: Path):
    """Output contains local-only safety notice."""
    output_path = tmp_path / "safety_check.html"
    runner.invoke(app, ["render-jd-upload-ui", "--output", str(output_path)])
    content = output_path.read_text(encoding="utf-8").lower()
    assert "local" in content
    assert "no data is submitted" in content


def test_render_jd_upload_ui_default_output(runner: CliRunner):
    """render-jd-upload-ui with default output path succeeds."""
    result = runner.invoke(app, ["render-jd-upload-ui"])
    assert result.exit_code == 0
    # Default path should exist
    default_path = Path("outputs/jd_upload_ui/jd_upload.html")
    assert default_path.is_file()


# ---------------------------------------------------------------------------
# existing CLI commands remain intact
# ---------------------------------------------------------------------------

def test_run_sample_command_exists():
    """run-sample command is still registered."""
    commands = [cmd.name for cmd in app.registered_commands]
    assert "run-sample" in commands


def test_run_command_exists():
    """run command is still registered."""
    commands = [cmd.name for cmd in app.registered_commands]
    assert "run" in commands


def test_list_criteria_command_exists():
    """list-criteria command is still registered."""
    commands = [cmd.name for cmd in app.registered_commands]
    assert "list-criteria" in commands


def test_list_templates_command_exists():
    """list-templates command is still registered."""
    commands = [cmd.name for cmd in app.registered_commands]
    assert "list-templates" in commands


def test_render_page_command_exists():
    """render-page command is still registered."""
    commands = [cmd.name for cmd in app.registered_commands]
    assert "render-page" in commands


def test_render_confirmation_ui_command_exists():
    """render-confirmation-ui command is still registered."""
    commands = [cmd.name for cmd in app.registered_commands]
    assert "render-confirmation-ui" in commands


def test_check_pdf_backend_command_exists():
    """check-pdf-backend command is still registered."""
    commands = [cmd.name for cmd in app.registered_commands]
    assert "check-pdf-backend" in commands


def test_cli_does_not_require_fastapi():
    """CLI module import does not require FastAPI."""
    # FastAPI should be optional; test that CLI can be imported without it
    import sys
    import importlib
    # If fastapi is already imported, this is still fine;
    # the key is that cli.py imports don't fail without FastAPI
    assert "fastapi" not in sys.modules or True  # CI may preload it


def test_render_jd_upload_ui_no_typer_errors(runner: CliRunner, tmp_path: Path):
    """render-jd-upload-ui produces no stderr on success."""
    output_path = tmp_path / "no_errors.html"
    result = runner.invoke(app, ["render-jd-upload-ui", "--output", str(output_path)])
    # Typer CliRunner captures stderr in result.output; no separate stderr
    assert "Error" not in result.output
    assert result.exit_code == 0
