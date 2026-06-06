"""Tests for M19 optional API app and routes (FastAPI conditional)."""

from __future__ import annotations

from importlib.util import find_spec

import pytest

FASTAPI_AVAILABLE = find_spec("fastapi") is not None


class TestCreateApiApp:

    def test_import_does_not_crash(self):
        """create_api_app can be imported without FastAPI installed."""
        from resume_pdf_agent.api.app import create_api_app
        assert callable(create_api_app)

    def test_raises_if_fastapi_missing(self):
        """If FastAPI is not installed, create_api_app raises."""
        from resume_pdf_agent.api.app import create_api_app
        if not FASTAPI_AVAILABLE:
            with pytest.raises(Exception):
                create_api_app()
        else:
            # FastAPI is available — should work
            app = create_api_app()
            assert app is not None


@pytest.mark.skipif(not FASTAPI_AVAILABLE, reason="FastAPI not installed")
class TestApiRoutes:

    def test_health_endpoint(self):
        from fastapi.testclient import TestClient
        from resume_pdf_agent.api.app import create_api_app

        app = create_api_app()
        client = TestClient(app)
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"

    def test_root_endpoint(self):
        from fastapi.testclient import TestClient
        from resume_pdf_agent.api.app import create_api_app

        app = create_api_app()
        client = TestClient(app)
        response = client.get("/")
        assert response.status_code == 200
