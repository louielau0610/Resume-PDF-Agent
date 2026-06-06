"""API route registration for M19 optional API layer.

Only used when FastAPI is available.
"""

from __future__ import annotations


def register_routes(app):
    """Register all API routes on a FastAPI application.

    Parameters
    ----------
    app : fastapi.FastAPI
        The FastAPI application instance.
    """
    from resume_pdf_agent.api.models import (
        APIHealthResponse,
        APIWorkflowRequest,
        APIWorkflowResponse,
    )
    from resume_pdf_agent.api.service import (
        build_api_health_response,
        list_api_artifacts,
        run_workflow_from_api_request,
    )

    @app.get("/", tags=["meta"])
    async def root():
        return {
            "service": "Resume PDF Agent API",
            "version": "0.1.0",
            "docs": "/docs",
        }

    @app.get("/health", response_model=APIHealthResponse, tags=["health"])
    async def health():
        """Health check endpoint."""
        return build_api_health_response()

    @app.post(
        "/workflow/run",
        response_model=APIWorkflowResponse,
        tags=["workflow"],
    )
    async def workflow_run(request: APIWorkflowRequest):
        """Run the resume workflow."""
        return run_workflow_from_api_request(request)

    @app.get(
        "/artifacts",
        response_model=list,
        tags=["artifacts"],
    )
    async def artifacts(output_dir: str):
        """List artifacts for a given output directory."""
        return list_api_artifacts(output_dir)
