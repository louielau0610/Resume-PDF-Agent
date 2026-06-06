"""Tests for M19 API models."""

from __future__ import annotations

import pytest

from resume_pdf_agent.api.models import (
    APIHealthResponse,
    APIWorkflowMode,
    APIWorkflowRequest,
    APIWorkflowResponse,
)


class TestAPIWorkflowRequest:

    def test_defaults(self):
        req = APIWorkflowRequest()
        assert req.mode == APIWorkflowMode.CUSTOM
        assert req.output_dir == "outputs/api_run"

    def test_sample_mode(self):
        req = APIWorkflowRequest(mode=APIWorkflowMode.SAMPLE)
        assert req.mode == APIWorkflowMode.SAMPLE

    def test_empty_output_dir_rejected(self):
        with pytest.raises(Exception):
            APIWorkflowRequest(output_dir="")


class TestAPIWorkflowResponse:

    def test_minimal_valid(self):
        resp = APIWorkflowResponse(
            status="completed",
            output_dir="outputs/test",
            summary="Test response.",
        )
        assert resp.status == "completed"

    def test_empty_summary_rejected(self):
        with pytest.raises(Exception):
            APIWorkflowResponse(
                status="completed",
                output_dir="outputs/test",
                summary="",
            )


class TestAPIHealthResponse:

    def test_defaults(self):
        resp = APIHealthResponse(summary="healthy")
        assert resp.status == "ok"

    def test_with_features(self):
        resp = APIHealthResponse(
            available_features=["workflow"],
            optional_dependencies={"fastapi": False},
            summary="ok",
        )
        assert "workflow" in resp.available_features
        assert resp.optional_dependencies["fastapi"] is False
