"""Pydantic models for M11 static frontend workflow page."""

from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, Field, model_validator


class FrontendPageStatus(str, Enum):
    """Status of a generated frontend workflow page."""

    RENDERED = "rendered"
    RENDERED_WITH_WARNINGS = "rendered_with_warnings"
    FAILED = "failed"


class FrontendArtifactLink(BaseModel):
    """A link to a local artifact displayed on the frontend page."""

    label: str
    path: str
    artifact_type: str
    description: str | None = None

    @model_validator(mode="after")
    def _path_not_empty(self) -> FrontendArtifactLink:
        if not self.path:
            raise ValueError("artifact link path cannot be empty")
        return self


class FrontendStageView(BaseModel):
    """Stage information rendered in the frontend timeline."""

    stage: str
    status: str
    message: str
    warnings_count: int = 0
    errors_count: int = 0

    @model_validator(mode="after")
    def _message_not_empty(self) -> FrontendStageView:
        if not self.message:
            raise ValueError("stage view message cannot be empty")
        return self


class FrontendPageOptions(BaseModel):
    """Options controlling what appears on the frontend workflow page."""

    include_artifact_links: bool = True
    include_stage_timeline: bool = True
    include_warnings: bool = True
    include_errors: bool = True
    include_resume_html_link: bool = True
    include_pdf_link: bool = True
    include_conversion_reminder: bool = True
    language: str = "en"


class FrontendPageResult(BaseModel):
    """Result of rendering a frontend workflow dashboard page."""

    status: FrontendPageStatus
    output_path: str | None = None
    html: str = ""
    warnings: list[str] = Field(default_factory=list)
    errors: list[str] = Field(default_factory=list)
    artifact_links: list[FrontendArtifactLink] = Field(default_factory=list)
    summary: str = ""

    @model_validator(mode="after")
    def _summary_not_empty(self) -> FrontendPageResult:
        if not self.summary:
            raise ValueError("summary cannot be empty")
        return self

    @model_validator(mode="after")
    def _html_required_for_rendered(self) -> FrontendPageResult:
        rendered_statuses = {
            FrontendPageStatus.RENDERED,
            FrontendPageStatus.RENDERED_WITH_WARNINGS,
        }
        if self.status in rendered_statuses and not self.html:
            raise ValueError(
                f"html cannot be empty when status is '{self.status.value}'"
            )
        return self

    @model_validator(mode="after")
    def _output_path_required_for_rendered(self) -> FrontendPageResult:
        rendered_statuses = {
            FrontendPageStatus.RENDERED,
            FrontendPageStatus.RENDERED_WITH_WARNINGS,
        }
        if self.status in rendered_statuses and not self.output_path:
            raise ValueError(
                f"output_path is required when status is '{self.status.value}'"
            )
        return self
