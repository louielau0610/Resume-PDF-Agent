"""Tests for M11 CLI frontend page integration."""

from __future__ import annotations

from pathlib import Path

import pytest
from typer.testing import CliRunner

from resume_pdf_agent.cli import app

runner = CliRunner()


def test_run_sample_with_write_frontend_page(tmp_path: Path):
    """run-sample --write-frontend-page writes index.html."""
    out = tmp_path / "outputs" / "cli_frontend"
    result = runner.invoke(
        app,
        [
            "run-sample",
            "--output-dir", str(out),
            "--pdf-backend", "mock",
            "--write-frontend-page",
        ],
    )
    assert result.exit_code == 0
    assert (out / "index.html").is_file()
    assert "Frontend page:" in result.stdout


def test_run_with_write_frontend_page(tmp_path: Path):
    """run --write-frontend-page writes index.html."""
    sample_input = (
        Path(__file__).resolve().parent.parent
        / "data"
        / "sample_inputs"
        / "sample_data_science_user.json"
    )
    out = tmp_path / "outputs" / "cli_run_frontend"
    result = runner.invoke(
        app,
        [
            "run",
            "--input", str(sample_input),
            "--output-dir", str(out),
            "--pdf-backend", "mock",
            "--write-frontend-page",
        ],
    )
    assert result.exit_code == 0
    assert (out / "index.html").is_file()


def test_render_page_command(tmp_path: Path):
    """render-page command runs workflow and writes index.html."""
    sample_input = (
        Path(__file__).resolve().parent.parent
        / "data"
        / "sample_inputs"
        / "sample_data_science_user.json"
    )
    out = tmp_path / "outputs" / "page_cmd"
    result = runner.invoke(
        app,
        [
            "render-page",
            "--input", str(sample_input),
            "--output-dir", str(out),
            "--pdf-backend", "mock",
        ],
    )
    assert result.exit_code == 0
    assert (out / "index.html").is_file()
    assert "Frontend page:" in result.stdout


def test_existing_commands_still_work():
    """Existing commands run-sample, run, list-criteria, list-templates still work."""
    # run-sample (without --write-frontend-page)
    import tempfile, os
    with tempfile.TemporaryDirectory() as td:
        result = runner.invoke(
            app,
            ["run-sample", "--output-dir", td, "--pdf-backend", "mock"],
        )
        assert result.exit_code == 0

    # list-criteria
    result = runner.invoke(app, ["list-criteria"])
    assert result.exit_code == 0
    assert "data_science_intern" in result.stdout

    # list-templates
    result = runner.invoke(app, ["list-templates"])
    assert result.exit_code == 0
    assert "ats_student_basic" in result.stdout


def test_run_sample_without_frontend_page_does_not_write_index(tmp_path: Path):
    """run-sample without --write-frontend-page does NOT write index.html."""
    out = tmp_path / "outputs" / "no_frontend"
    result = runner.invoke(
        app,
        [
            "run-sample",
            "--output-dir", str(out),
            "--pdf-backend", "mock",
        ],
    )
    assert result.exit_code == 0
    assert not (out / "index.html").is_file()


def test_render_page_help():
    """render-page has help text."""
    result = runner.invoke(app, ["render-page", "--help"])
    assert result.exit_code == 0
    assert "index.html" in result.stdout.lower() or "dashboard" in result.stdout.lower()
