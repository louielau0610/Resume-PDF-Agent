"""Optional FastAPI app factory for M19 API layer.

FastAPI is optional. This module raises a clear error if FastAPI
is not installed.
"""

from __future__ import annotations

from importlib.util import find_spec


def create_api_app():
    """Create a FastAPI application instance.

    Returns
    -------
    FastAPI
        A configured FastAPI app with workflow routes registered.

    Raises
    ------
    OptionalDependencyError
        If FastAPI is not installed.
    """
    if find_spec("fastapi") is None:
        from resume_pdf_agent.api.errors import OptionalDependencyError

        raise OptionalDependencyError(
            package="fastapi",
            install_hint="pip install resume-pdf-agent[api]",
        )

    from fastapi import FastAPI

    from resume_pdf_agent.api.routes import register_routes

    app = FastAPI(
        title="Resume PDF Agent API",
        description="Criteria-aware AI resume PDF generation agent API.",
        version="0.1.0",
    )

    register_routes(app)

    return app
