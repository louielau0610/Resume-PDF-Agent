"""Pydantic models for M21 browser-based JD upload UI."""

from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, Field, model_validator


class JDUploadUIStatus(str, Enum):
    RENDERED = "rendered"
    RENDERED_WITH_WARNINGS = "rendered_with_warnings"
    FAILED = "failed"


class JDUploadUIOptions(BaseModel):
    include_copy_buttons: bool = True
    include_download_buttons: bool = True
    include_compliance_hints: bool = True
    include_workflow_json_generator: bool = True
    include_cli_instructions: bool = True
    language: str = "zh"


class JDClientComplianceHint(BaseModel):
    marker: str = Field(min_length=1)
    severity: str
    explanation: str = Field(min_length=1)
    suggested_action: str = Field(min_length=1)


class JDUploadUIResult(BaseModel):
    status: JDUploadUIStatus
    output_path: str | None = None
    html: str = ""
    warnings: list[str] = Field(default_factory=list)
    errors: list[str] = Field(default_factory=list)
    summary: str = Field(min_length=1)

    @model_validator(mode="after")
    def _rendered_requires_output(self) -> JDUploadUIResult:
        if self.status == JDUploadUIStatus.RENDERED:
            if not self.output_path:
                raise ValueError("output_path required when rendered")
            if not self.html:
                raise ValueError("html cannot be empty when rendered")
        return self
