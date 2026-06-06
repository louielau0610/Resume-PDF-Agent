"""Tests for M18 visual regression artifact validation."""

from __future__ import annotations

from pathlib import Path

from resume_pdf_agent.visual_regression.artifacts import (
    collect_expected_visual_artifacts,
    validate_pdf_artifact,
    validate_workflow_visual_artifacts,
)


class TestValidatePdfArtifact:

    def test_missing_pdf(self):
        issues = validate_pdf_artifact("/nonexistent/path.pdf")
        assert any("not found" in i for i in issues)

    def test_valid_mock_pdf(self, tmp_path):
        pdf = tmp_path / "test.pdf"
        pdf.write_bytes(b"%PDF-1.4 mock content")
        issues = validate_pdf_artifact(pdf)
        assert issues == []

    def test_invalid_header(self, tmp_path):
        pdf = tmp_path / "bad.pdf"
        pdf.write_bytes(b"NOT A PDF")
        issues = validate_pdf_artifact(pdf)
        assert any("header" in i for i in issues)

    def test_empty_pdf(self, tmp_path):
        pdf = tmp_path / "empty.pdf"
        pdf.write_bytes(b"")
        issues = validate_pdf_artifact(pdf)
        assert any("empty" in i for i in issues)


class TestCollectExpectedVisualArtifacts:

    def test_returns_dict(self, tmp_path):
        result = collect_expected_visual_artifacts(tmp_path)
        assert "index.html" in result
        assert "resume.pdf" in result


class TestValidateWorkflowVisualArtifacts:

    def test_empty_dir(self, tmp_path):
        issues = validate_workflow_visual_artifacts(tmp_path)
        assert len(issues) > 0  # missing required files

    def test_all_present(self, tmp_path):
        (tmp_path / "index.html").write_text("test")
        (tmp_path / "resume.html").write_text("test")
        (tmp_path / "resume.pdf").write_bytes(b"%PDF-1.4")
        issues = validate_workflow_visual_artifacts(tmp_path)
        assert issues == []
