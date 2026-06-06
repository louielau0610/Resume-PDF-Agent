"""Pydantic models for M19 optional API layer."""

from __future__ import annotations

from enum import Enum
from pathlib import Path

from pydantic import BaseModel, Field

from resume_pdf_agent.models.pdf import PDFBackend
from resume_pdf_agent.models.workflow import ResumeWorkflowInput


class APIWorkflowMode(str, Enum):
    """API workflow run mode."""

    SAMPLE = "sample"
    CUSTOM = "custom"


class APIWorkflowRequest(BaseModel):
    """Request to run the resume workflow via API."""

    mode: APIWorkflowMode = APIWorkflowMode.CUSTOM
    workflow_input: ResumeWorkflowInput | None = None
    output_dir: str = Field(default="outputs/api_run", min_length=1)
    pdf_backend: PDFBackend = PDFBackend.MOCK
    write_frontend_page: bool = True
    use_user_provided_jd: bool = False
    jd_text: str | None = None
    jd_file_path: str | None = None
    require_confirmation_before_pdf: bool = False
    enable_llm_rewriting: bool = False
    llm_provider: str | None = None


class APIArtifactView(BaseModel):
    """A lightweight view of a workflow output artifact."""

    artifact_type: str
    path: str
    description: str | None = None
    exists: bool = False


class APIWorkflowResponse(BaseModel):
    """Response from a workflow run via API."""

    status: str
    output_dir: str
    selected_criteria_profile_id: str | None = None
    primary_resume_type: str | None = None
    selected_template_id: str | None = None
    html_output_path: str | None = None
    pdf_output_path: str | None = None
    frontend_page_path: str | None = None
    confirmation_packet_path: str | None = None
    parsed_jd_path: str | None = None
    jd_criteria_profile_path: str | None = None
    llm_rewrite_result_path: str | None = None
    warnings: list[str] = Field(default_factory=list)
    errors: list[str] = Field(default_factory=list)
    artifacts: list[APIArtifactView] = Field(default_factory=list)
    summary: str = Field(min_length=1)


class APIHealthResponse(BaseModel):
    """Health check response for the API layer."""

    status: str = "ok"
    version: str | None = None
    available_features: list[str] = Field(default_factory=list)
    optional_dependencies: dict[str, bool] = Field(default_factory=dict)
    summary: str = Field(min_length=1)
