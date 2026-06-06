"""Tests for M19 API service layer."""

from __future__ import annotations

from resume_pdf_agent.api.models import APIWorkflowMode, APIWorkflowRequest
from resume_pdf_agent.api.service import (
    build_api_health_response,
    list_api_artifacts,
    run_workflow_from_api_request,
)


class TestBuildApiHealthResponse:

    def test_returns_response(self):
        resp = build_api_health_response()
        assert resp.status == "ok"
        assert len(resp.available_features) > 0

    def test_reports_optional_deps(self):
        resp = build_api_health_response()
        assert "fastapi" in resp.optional_dependencies


class TestRunWorkflowFromApiRequest:

    def test_sample_mode_works(self):
        req = APIWorkflowRequest(
            mode=APIWorkflowMode.SAMPLE,
            output_dir="outputs/api_test_sample",
            pdf_backend="mock",
            write_frontend_page=False,
        )
        resp = run_workflow_from_api_request(req)
        assert resp.status in ("completed", "completed_with_warnings")
        assert resp.html_output_path is not None

    def test_sample_mode_generates_pdf(self):
        req = APIWorkflowRequest(
            mode=APIWorkflowMode.SAMPLE,
            output_dir="outputs/api_test_pdf",
            pdf_backend="mock",
            write_frontend_page=False,
        )
        resp = run_workflow_from_api_request(req)
        assert resp.pdf_output_path is not None

    def test_artifacts_listed(self):
        req = APIWorkflowRequest(
            mode=APIWorkflowMode.SAMPLE,
            output_dir="outputs/api_test_artifacts",
            pdf_backend="mock",
            write_frontend_page=False,
        )
        resp = run_workflow_from_api_request(req)
        assert len(resp.artifacts) > 0

    def test_no_raw_resume_content_in_response(self):
        req = APIWorkflowRequest(
            mode=APIWorkflowMode.SAMPLE,
            output_dir="outputs/api_test_no_raw",
            pdf_backend="mock",
            write_frontend_page=False,
        )
        resp = run_workflow_from_api_request(req)
        # Response should not contain raw HTML/PDF content
        resp_dict = resp.model_dump()
        for val in resp_dict.values():
            if isinstance(val, str) and len(val) > 500:
                # Long strings might be paths, but shouldn't be raw resume
                assert "<html" not in val.lower()


class TestListApiArtifacts:

    def test_empty_dir(self, tmp_path):
        artifacts = list_api_artifacts(tmp_path)
        assert len(artifacts) > 0
        assert all(a.exists is False for a in artifacts)

    def test_with_files(self, tmp_path):
        (tmp_path / "resume.html").write_text("test")
        artifacts = list_api_artifacts(tmp_path)
        resume = [a for a in artifacts if "resume.html" in a.path][0]
        assert resume.exists is True
