"""Pydantic models for M22 browser-based LLM rewrite review UI."""

from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, Field, model_validator


class LLMReviewUIStatus(str, Enum):
    RENDERED = "rendered"
    RENDERED_WITH_WARNINGS = "rendered_with_warnings"
    FAILED = "failed"


class LLMReviewDecisionType(str, Enum):
    APPROVE_CANDIDATE = "approve_candidate"
    REJECT_CANDIDATE = "reject_candidate"
    NEEDS_EDITING = "needs_editing"
    PROVIDE_NOTE = "provide_note"
    IGNORE_FOR_NOW = "ignore_for_now"


class LLMReviewUIOptions(BaseModel):
    include_copy_buttons: bool = True
    include_download_buttons: bool = True
    include_risk_filters: bool = True
    include_decision_controls: bool = True
    include_cli_instructions: bool = True
    include_safety_notice: bool = True
    language: str = "zh"


class LLMReviewCandidateView(BaseModel):
    candidate_id: str = Field(min_length=1)
    source_experience_id: str | None = None
    original_text: str = Field(min_length=1)
    rewritten_text: str = Field(min_length=1)
    provider: str = Field(min_length=1)
    mode: str = Field(min_length=1)
    status: str = Field(min_length=1)
    evidence_level: str
    metric_status: str
    needs_confirmation: bool = True
    validation_warnings: list[str] = Field(default_factory=list)
    risk_flags: list[str] = Field(default_factory=list)
    rationale: str | None = None


class LLMReviewUIResult(BaseModel):
    status: LLMReviewUIStatus
    output_path: str | None = None
    html: str = ""
    warnings: list[str] = Field(default_factory=list)
    errors: list[str] = Field(default_factory=list)
    candidate_count: int = Field(ge=0, default=0)
    candidates_requiring_confirmation: int = Field(ge=0, default=0)
    summary: str = Field(min_length=1)

    @model_validator(mode="after")
    def _rendered_requires_output(self) -> LLMReviewUIResult:
        if self.status == LLMReviewUIStatus.RENDERED:
            if not self.output_path:
                raise ValueError("output_path required when rendered")
            if not self.html:
                raise ValueError("html cannot be empty when rendered")
        return self
