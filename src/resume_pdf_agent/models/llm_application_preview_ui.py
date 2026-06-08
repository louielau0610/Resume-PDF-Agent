"""Models for M25 manual LLM application preview UI."""

from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, Field, model_validator


class LLMApplicationPreviewUIStatus(str, Enum):
    """Rendering status for the M25 preview UI."""

    RENDERED = "rendered"
    FAILED = "failed"


class LLMApplicationPreviewStatusGroup(BaseModel):
    """Summary for one plan status group."""

    status: str = Field(min_length=1)
    title: str = Field(min_length=1)
    description: str = Field(min_length=1)
    count: int = Field(ge=0)
    item_ids: list[str] = Field(default_factory=list)


class LLMApplicationPreviewItemView(BaseModel):
    """Display view for one plan item."""

    candidate_id: str = Field(min_length=1)
    plan_status: str = Field(min_length=1)
    source_action: str | None = None
    target_section: str | None = None
    target_item_id: str | None = None
    original_text: str | None = None
    candidate_text: str | None = None
    provider: str | None = None
    risk_level: str | None = None
    needs_confirmation: bool = True
    validation_warnings: list[str] = Field(default_factory=list)
    block_reasons: list[str] = Field(default_factory=list)
    manual_review_notes: list[str] = Field(default_factory=list)
    decision_note: str | None = None
    application_instruction: str | None = None
    can_copy_candidate_text: bool = False
    safety_labels: list[str] = Field(default_factory=list)


class LLMApplicationPreviewPageContext(BaseModel):
    """Complete static page context for the M25 preview UI."""

    page_title: str = Field(min_length=1)
    generated_from: str = Field(min_length=1)
    plan_only: bool = True
    source_files: dict[str, str] = Field(default_factory=dict)
    total_candidates: int = Field(ge=0, default=0)
    planned_count: int = Field(ge=0, default=0)
    blocked_count: int = Field(ge=0, default=0)
    needs_manual_edit_count: int = Field(ge=0, default=0)
    excluded_count: int = Field(ge=0, default=0)
    unmapped_count: int = Field(ge=0, default=0)
    warnings: list[str] = Field(default_factory=list)
    safety_notice: str = Field(min_length=1)
    status_groups: list[LLMApplicationPreviewStatusGroup] = Field(default_factory=list)
    items: list[LLMApplicationPreviewItemView] = Field(default_factory=list)
    static_css: str = ""
    static_js: str = ""

    @model_validator(mode="after")
    def _always_plan_only(self) -> LLMApplicationPreviewPageContext:
        if self.plan_only is not True:
            raise ValueError("LLM application preview UI must always be plan_only=True")
        return self


class LLMApplicationPreviewUIResult(BaseModel):
    """Result returned by the M25 renderer."""

    status: LLMApplicationPreviewUIStatus
    output_path: str | None = None
    html: str = ""
    warnings: list[str] = Field(default_factory=list)
    errors: list[str] = Field(default_factory=list)
    total_candidates: int = Field(ge=0, default=0)
    planned_count: int = Field(ge=0, default=0)
    blocked_count: int = Field(ge=0, default=0)
    needs_manual_edit_count: int = Field(ge=0, default=0)
    excluded_count: int = Field(ge=0, default=0)
    unmapped_count: int = Field(ge=0, default=0)
    summary: str = Field(min_length=1)

    @model_validator(mode="after")
    def _rendered_requires_output(self) -> LLMApplicationPreviewUIResult:
        if self.status == LLMApplicationPreviewUIStatus.RENDERED:
            if not self.output_path:
                raise ValueError("output_path required when rendered")
            if not self.html:
                raise ValueError("html cannot be empty when rendered")
        return self
