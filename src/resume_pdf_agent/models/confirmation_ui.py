"""Pydantic models for M20 browser-based confirmation UI."""

from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, Field, model_validator

from resume_pdf_agent.models.confirmation import ConfirmationDecisionType


class ConfirmationUIStatus(str, Enum):
    """Status of confirmation UI rendering."""

    RENDERED = "rendered"
    RENDERED_WITH_WARNINGS = "rendered_with_warnings"
    FAILED = "failed"


class ConfirmationUIDecisionOption(BaseModel):
    """A single decision option for the UI."""

    decision: ConfirmationDecisionType
    label: str
    description: str


class ConfirmationUIItemView(BaseModel):
    """A confirmation item as displayed in the UI."""

    item_id: str = Field(min_length=1)
    item_type: str
    priority: str
    status: str
    source_stage: str
    source_id: str | None = None
    source_experience_id: str | None = None
    claim_text: str = Field(min_length=1)
    reason: str = Field(min_length=1)
    suggested_user_action: str = Field(min_length=1)
    risk_flags: list[str] = Field(default_factory=list)
    blocks_final_pdf: bool = False
    requires_user_decision: bool = False


class ConfirmationUIOptions(BaseModel):
    """Options for confirmation UI page rendering."""

    include_copy_button: bool = True
    include_download_button: bool = True
    include_priority_filters: bool = True
    include_decision_controls: bool = True
    include_raw_packet_summary: bool = False
    language: str = "zh"


class ConfirmationUIResult(BaseModel):
    """Result of confirmation UI page rendering."""

    status: ConfirmationUIStatus
    output_path: str | None = None
    html: str = ""
    warnings: list[str] = Field(default_factory=list)
    errors: list[str] = Field(default_factory=list)
    item_count: int = Field(ge=0, default=0)
    blocking_count: int = Field(ge=0, default=0)
    summary: str = Field(min_length=1)

    @model_validator(mode="after")
    def _rendered_requires_output(self) -> ConfirmationUIResult:
        if self.status == ConfirmationUIStatus.RENDERED:
            if not self.output_path:
                raise ValueError("output_path required when rendered")
            if not self.html:
                raise ValueError("html cannot be empty when rendered")
        return self
