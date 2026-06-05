"""Tests for the M11 frontend safety helpers."""

from __future__ import annotations

from pathlib import Path

from resume_pdf_agent.frontend.safety import (
    escape_frontend_text,
    is_allowed_frontend_artifact,
    safe_relative_artifact_path,
)


def test_escape_frontend_text_escapes_html():
    """escape_frontend_text converts HTML special chars to entities."""
    assert escape_frontend_text("<script>alert(1)</script>") != "<script>alert(1)</script>"
    assert "&lt;" in escape_frontend_text("<script>alert(1)</script>")
    assert "<script>" not in escape_frontend_text("<script>alert(1)</script>")


def test_escape_frontend_text_escapes_quotes():
    """escape_frontend_text escapes both double and single quotes."""
    result = escape_frontend_text('He said "hello"')
    assert "&quot;" in result


def test_escape_frontend_text_preserves_safe_text():
    """escape_frontend_text does not modify safe text."""
    safe = "Hello World 123"
    assert escape_frontend_text(safe) == safe


def test_escape_frontend_text_handles_non_string():
    """escape_frontend_text returns empty string for non-string input."""
    assert escape_frontend_text(None) == ""
    assert escape_frontend_text(123) == ""


def test_safe_relative_artifact_path_inside_base(tmp_path: Path):
    """safe_relative_artifact_path returns relative path for descendants."""
    base = tmp_path / "outputs"
    base.mkdir()
    artifact = base / "resume.html"
    artifact.write_text("test")

    rel = safe_relative_artifact_path(artifact, base)
    assert rel == "resume.html"
    assert ".." not in rel


def test_safe_relative_artifact_path_outside_base():
    """safe_relative_artifact_path returns escaped filename for paths outside base."""
    outside = Path("/etc/passwd")
    result = safe_relative_artifact_path(outside, "/some/base")
    assert "/etc/passwd" not in result.lower()
    # Should only contain the filename
    assert "passwd" in result


def test_is_allowed_frontend_artifact_allows_html():
    """is_allowed_frontend_artifact allows .html files."""
    assert is_allowed_frontend_artifact(Path("outputs/resume.html")) is True


def test_is_allowed_frontend_artifact_allows_pdf():
    """is_allowed_frontend_artifact allows .pdf files."""
    assert is_allowed_frontend_artifact(Path("outputs/resume.pdf")) is True


def test_is_allowed_frontend_artifact_allows_json():
    """is_allowed_frontend_artifact allows .json files."""
    assert is_allowed_frontend_artifact(Path("outputs/data.json")) is True


def test_is_allowed_frontend_artifact_rejects_exe():
    """is_allowed_frontend_artifact rejects .exe files."""
    assert is_allowed_frontend_artifact(Path("malware.exe")) is False


def test_is_allowed_frontend_artifact_rejects_bat():
    """is_allowed_frontend_artifact rejects .bat files."""
    assert is_allowed_frontend_artifact(Path("script.bat")) is False
