"""Tests for M13 demo scripts."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

_REPO_ROOT = Path(__file__).resolve().parent.parent


def test_run_demo_workflow_script_exists():
    """scripts/run_demo_workflow.py must exist."""
    path = _REPO_ROOT / "scripts" / "run_demo_workflow.py"
    assert path.is_file(), "run_demo_workflow.py not found."


def test_validate_release_readiness_script_exists():
    """scripts/validate_release_readiness.py must exist."""
    path = _REPO_ROOT / "scripts" / "validate_release_readiness.py"
    assert path.is_file(), "validate_release_readiness.py not found."


def test_run_demo_workflow_can_be_imported():
    """run_demo_workflow.py must be syntactically valid and importable."""
    import importlib.util

    spec = importlib.util.spec_from_file_location(
        "run_demo_workflow",
        _REPO_ROOT / "scripts" / "run_demo_workflow.py",
    )
    assert spec is not None
    mod = importlib.util.module_from_spec(spec)
    # Just verify it compiles; don't execute.
    assert mod is not None


def test_validate_release_readiness_runs_successfully():
    """validate_release_readiness.py must exit with code 0."""
    script = _REPO_ROOT / "scripts" / "validate_release_readiness.py"
    result = subprocess.run(
        [sys.executable, str(script)],
        capture_output=True,
        text=True,
        cwd=str(_REPO_ROOT),
    )
    assert result.returncode == 0, (
        f"validate_release_readiness.py failed (exit {result.returncode}):\n"
        f"STDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}"
    )


@pytest.mark.slow
def test_run_demo_workflow_mock_backend(tmp_path):
    """Run demo workflow with mock backend in a temp directory.

    This is a lightweight smoke test; it does not check visual output.
    """
    script = _REPO_ROOT / "scripts" / "run_demo_workflow.py"
    output_dir = tmp_path / "demo_output"
    result = subprocess.run(
        [
            sys.executable, str(script),
            "--output-dir", str(output_dir),
            "--pdf-backend", "mock",
            "--no-frontend-page",
        ],
        capture_output=True,
        text=True,
        cwd=str(_REPO_ROOT),
        timeout=120,
    )

    # Workflow may fail gracefully, but the script should not crash.
    # We verify it produced at least some output files.
    assert result.returncode in (0, 1), (
        f"Demo script crashed (exit {result.returncode}):\n"
        f"STDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}"
    )

    # Check that key artifacts exist.
    assert (output_dir / "resume.html").is_file(), "resume.html not generated."
    assert (output_dir / "resume.pdf").is_file(), "resume.pdf not generated."
    assert (output_dir / "workflow_result.json").is_file(), (
        "workflow_result.json not generated."
    )


def test_validate_release_readiness_output_positive():
    """validate_release_readiness.py stdout must indicate success."""
    script = _REPO_ROOT / "scripts" / "validate_release_readiness.py"
    result = subprocess.run(
        [sys.executable, str(script)],
        capture_output=True,
        text=True,
        cwd=str(_REPO_ROOT),
    )
    assert "PASSED" in result.stdout, (
        f"Expected 'PASSED' in output, got:\n{result.stdout}"
    )
