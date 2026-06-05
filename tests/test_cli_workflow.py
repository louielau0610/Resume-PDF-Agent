"""Tests for the M10 Typer CLI."""

from __future__ import annotations

from pathlib import Path

import pytest
from typer.testing import CliRunner

from resume_pdf_agent.cli import app

runner = CliRunner()

_SAMPLE_INPUT_PATH = (
    Path(__file__).resolve().parent.parent
    / "data"
    / "sample_inputs"
    / "sample_data_science_user.json"
)


def test_cli_app_can_be_imported():
    """The Typer app can be imported."""
    assert app is not None


def test_run_sample_command_works_with_mock_backend(tmp_path: Path):
    """run-sample works with mock backend."""
    result = runner.invoke(
        app,
        [
            "run-sample",
            "--output-dir", str(tmp_path / "outputs" / "cli_sample"),
            "--pdf-backend", "mock",
        ],
    )
    assert result.exit_code == 0
    assert "Status:" in result.stdout
    assert "HTML output:" in result.stdout
    assert "PDF output:" in result.stdout


def test_run_command_works_with_input_file(tmp_path: Path):
    """run works with explicit input file and mock backend."""
    result = runner.invoke(
        app,
        [
            "run",
            "--input", str(_SAMPLE_INPUT_PATH),
            "--output-dir", str(tmp_path / "outputs" / "cli_run"),
            "--pdf-backend", "mock",
        ],
    )
    assert result.exit_code == 0
    assert "Status:" in result.stdout


def test_list_criteria_command():
    """list-criteria prints available criteria profile IDs."""
    result = runner.invoke(app, ["list-criteria"])
    assert result.exit_code == 0
    assert "data_science_intern" in result.stdout
    assert "software_engineering_intern" in result.stdout


def test_list_templates_command():
    """list-templates prints available template IDs."""
    result = runner.invoke(app, ["list-templates"])
    assert result.exit_code == 0
    assert "ats_student_basic" in result.stdout
    assert "data_science_technical" in result.stdout


def test_run_command_missing_input():
    """run without --input shows error."""
    result = runner.invoke(app, ["run"])
    assert result.exit_code != 0


def test_run_sample_creates_output_files(tmp_path: Path):
    """run-sample creates resume.html and resume.pdf."""
    out = tmp_path / "outputs" / "cli_files"
    result = runner.invoke(
        app,
        [
            "run-sample",
            "--output-dir", str(out),
            "--pdf-backend", "mock",
        ],
    )
    assert result.exit_code == 0
    assert (out / "resume.html").is_file()
    assert (out / "resume.pdf").is_file()


def test_invalid_pdf_backend_rejected(tmp_path: Path):
    """Invalid --pdf-backend value returns non-zero exit code."""
    result = runner.invoke(
        app,
        [
            "run-sample",
            "--output-dir", str(tmp_path / "outputs" / "bad_backend"),
            "--pdf-backend", "invalid_backend",
        ],
    )
    assert result.exit_code != 0


def test_cli_help():
    """CLI shows help."""
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "run-sample" in result.stdout
    assert "list-criteria" in result.stdout
    assert "list-templates" in result.stdout


def test_run_sample_prints_criteria_profile(tmp_path: Path):
    """run-sample output mentions criteria profile."""
    result = runner.invoke(
        app,
        [
            "run-sample",
            "--output-dir", str(tmp_path / "outputs" / "criteria_cli"),
            "--pdf-backend", "mock",
        ],
    )
    assert result.exit_code == 0
    assert "Criteria profile:" in result.stdout


def test_run_sample_prints_primary_resume_type(tmp_path: Path):
    """run-sample output mentions primary resume type."""
    result = runner.invoke(
        app,
        [
            "run-sample",
            "--output-dir", str(tmp_path / "outputs" / "type_cli"),
            "--pdf-backend", "mock",
        ],
    )
    assert result.exit_code == 0
    assert "Primary resume type:" in result.stdout


def test_run_sample_prints_selected_template(tmp_path: Path):
    """run-sample output mentions selected template."""
    result = runner.invoke(
        app,
        [
            "run-sample",
            "--output-dir", str(tmp_path / "outputs" / "tmpl_cli"),
            "--pdf-backend", "mock",
        ],
    )
    assert result.exit_code == 0
    assert "Selected template:" in result.stdout
