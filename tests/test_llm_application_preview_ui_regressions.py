"""Regression tests for M25 application preview UI."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from resume_pdf_agent.models.enums import ExportFormat


def test_export_format_remains_pdf_only():
    assert [item.value for item in ExportFormat] == ["pdf"]


def test_no_forbidden_core_dependencies():
    text = Path("pyproject.toml").read_text(encoding="utf-8").lower()
    core = text.split("[project.optional-dependencies]")[0]
    forbidden = [
        "fastapi",
        "flask",
        "react",
        "vite",
        "next",
        "vue",
        "svelte",
        "streamlit",
        "openai",
        "anthropic",
    ]
    for value in forbidden:
        assert value not in core


def test_m22_review_ui_still_importable():
    from resume_pdf_agent.llm_review_ui import render_llm_review_ui_from_result_file

    assert callable(render_llm_review_ui_from_result_file)


def test_m23_summary_still_importable():
    from resume_pdf_agent.llm_review_decisions import summarize_llm_review_decisions_to_files

    assert callable(summarize_llm_review_decisions_to_files)


def test_m24_plan_still_importable():
    from resume_pdf_agent.llm_application_plan import plan_llm_candidate_application_to_files

    assert callable(plan_llm_candidate_application_to_files)


def test_m25_preview_does_not_expose_application_engine_terms():
    html_template = Path(
        "src/resume_pdf_agent/llm_application_preview_ui/templates/llm_application_preview_page.html.j2"
    ).read_text(encoding="utf-8")
    forbidden = [
        "Accept and apply",
        "Auto apply",
        "Update resume",
        "Patch resume",
        ">Submit<",
        ">Upload<",
    ]
    for phrase in forbidden:
        assert phrase not in html_template


def test_release_readiness_passes_with_m25_checks():
    result = subprocess.run(
        [sys.executable, "scripts/validate_release_readiness.py"],
        text=True,
        capture_output=True,
        check=False,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert "render-llm-application-preview-ui" in result.stdout


def test_demo_script_supports_m25_flag():
    result = subprocess.run(
        [sys.executable, "scripts/run_demo_workflow.py", "--help"],
        text=True,
        capture_output=True,
        check=False,
    )
    assert result.returncode == 0
    assert "--write-llm-application-preview-ui" in result.stdout
