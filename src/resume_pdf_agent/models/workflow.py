"""Pydantic models for M10 workflow integration."""

from __future__ import annotations

from enum import Enum
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field, model_validator

from resume_pdf_agent.models.enums import ResumeType
from resume_pdf_agent.models.pdf import PDFBackend
from resume_pdf_agent.models.resume_content import ResumeContent
from resume_pdf_agent.models.user_profile import UserProfile


class WorkflowStageName(str, Enum):
    """Names for each deterministic workflow stage."""

    USER_INTAKE = "user_intake"
    CRITERIA_SELECTION = "criteria_selection"
    RESUME_TYPE_CLASSIFICATION = "resume_type_classification"
    GAP_ANALYSIS = "gap_analysis"
    TRUTHFULNESS_CHECK = "truthfulness_check"
    CRITERIA_AWARE_CONTENT_ENHANCEMENT = "criteria_aware_content_enhancement"
    INTERNAL_TEMPLATE_MATCHING = "internal_template_matching"
    HTML_RENDERING = "html_rendering"
    PDF_GENERATION = "pdf_generation"
    CONFIRMATION_REVIEW = "confirmation_review"
    ARTIFACT_WRITING = "artifact_writing"
    REMINDER_PANEL = "reminder_panel"


class WorkflowStageStatus(str, Enum):
    """Status values for individual workflow stages."""

    PENDING = "pending"
    COMPLETED = "completed"
    COMPLETED_WITH_WARNINGS = "completed_with_warnings"
    SKIPPED = "skipped"
    FAILED = "failed"


class WorkflowRunStatus(str, Enum):
    """Overall workflow run status."""

    COMPLETED = "completed"
    COMPLETED_WITH_WARNINGS = "completed_with_warnings"
    FAILED = "failed"


class WorkflowArtifact(BaseModel):
    """Describes a single output artifact produced by the workflow."""

    artifact_type: str
    path: str
    description: str

    @model_validator(mode="after")
    def _path_not_empty(self) -> WorkflowArtifact:
        if not self.path:
            raise ValueError("artifact path cannot be empty")
        return self


class WorkflowStageResult(BaseModel):
    """Result for a single workflow stage."""

    stage: WorkflowStageName
    status: WorkflowStageStatus
    message: str
    warnings: list[str] = Field(default_factory=list)
    errors: list[str] = Field(default_factory=list)
    artifacts: list[WorkflowArtifact] = Field(default_factory=list)

    @model_validator(mode="after")
    def _message_not_empty(self) -> WorkflowStageResult:
        if not self.message:
            raise ValueError("stage message cannot be empty")
        return self


class ResumeWorkflowInput(BaseModel):
    """Input for a deterministic resume workflow run."""

    user_profile: UserProfile
    resume_content: ResumeContent
    target_role: str | None = None
    criteria_profile_id: str | None = None
    output_dir: str = "outputs/workflow"
    pdf_backend: PDFBackend = PDFBackend.MOCK
    include_preview_reminder_panel: bool = False
    write_intermediate_json: bool = True
    # M14: User confirmation workflow
    require_confirmation_before_pdf: bool = False
    write_confirmation_packet: bool = True
    confirmation_decisions_path: str | None = None
    # M15: User-provided JD
    jd_text: str | None = None
    jd_file_path: str | None = None
    use_user_provided_jd: bool = False
    write_jd_artifacts: bool = True
    # M16: Optional LLM rewriting
    enable_llm_rewriting: bool = False
    llm_provider: str | None = None
    write_llm_artifacts: bool = True
    # M20: Browser confirmation UI
    write_confirmation_ui: bool = False
    # M22: Browser LLM rewrite review UI
    write_llm_review_ui: bool = False

    @model_validator(mode="after")
    def _output_dir_not_empty(self) -> ResumeWorkflowInput:
        if not self.output_dir:
            raise ValueError("output_dir cannot be empty")
        return self


class ResumeWorkflowResult(BaseModel):
    """Structured result of a deterministic resume workflow run."""

    status: WorkflowRunStatus
    output_dir: str
    stages: list[WorkflowStageResult] = Field(default_factory=list)
    artifacts: list[WorkflowArtifact] = Field(default_factory=list)
    selected_criteria_profile_id: str | None = None
    primary_resume_type: ResumeType | None = None
    selected_template_id: str | None = None
    html_output_path: str | None = None
    pdf_output_path: str | None = None
    warnings: list[str] = Field(default_factory=list)
    errors: list[str] = Field(default_factory=list)
    conversion_reminder: str | None = None
    summary: str = ""
    # M14: User confirmation workflow
    confirmation_packet_path: str | None = None
    confirmation_review_path: str | None = None
    confirmation_required: bool = False
    can_generate_final_pdf: bool = True
    # M15: User-provided JD
    parsed_jd_path: str | None = None
    jd_criteria_profile_path: str | None = None
    jd_compliance_status: str | None = None
    used_user_provided_jd: bool = False
    # M16: Optional LLM rewriting
    llm_rewrite_result_path: str | None = None
    llm_rewriting_used: bool = False
    # M20: Browser confirmation UI
    confirmation_ui_path: str | None = None
    # M22: Browser LLM rewrite review UI
    llm_review_ui_path: str | None = None

    @model_validator(mode="after")
    def _summary_not_empty(self) -> ResumeWorkflowResult:
        if not self.summary:
            raise ValueError("summary cannot be empty")
        return self

    @model_validator(mode="after")
    def _status_consistent_with_errors(self) -> ResumeWorkflowResult:
        if self.errors and self.status != WorkflowRunStatus.FAILED:
            raise ValueError(
                f"WorkflowRunStatus must be '{WorkflowRunStatus.FAILED.value}' when errors are present"
            )
        return self
