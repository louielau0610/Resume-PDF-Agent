"""Models for M24 LLM candidate application planning."""

from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, Field, model_validator


class LLMApplicationPlanStatus(str, Enum):
    """Plan-only candidate application statuses."""

    PLANNED = "planned"
    BLOCKED = "blocked"
    NEEDS_MANUAL_EDIT = "needs_manual_edit"
    EXCLUDED = "excluded"
    UNMAPPED = "unmapped"


class LLMApplicationBlockReason(str, Enum):
    """Reasons a candidate cannot be safely planned for direct application."""

    NOT_APPROVED = "not_approved"
    REJECTED = "rejected"
    IGNORED = "ignored"
    NEEDS_EDIT = "needs_edit"
    UNDECIDED = "undecided"
    HAS_VALIDATION_WARNINGS = "has_validation_warnings"
    NEEDS_CONFIRMATION = "needs_confirmation"
    UNKNOWN_CANDIDATE_ID = "unknown_candidate_id"
    DUPLICATE_DECISION = "duplicate_decision"
    MISSING_ORIGINAL_TEXT = "missing_original_text"
    MISSING_CANDIDATE_TEXT = "missing_candidate_text"
    UNSAFE_OR_UNMAPPED_TARGET = "unsafe_or_unmapped_target"
    UNSUPPORTED_ACTION = "unsupported_action"
    SUMMARY_WARNING = "summary_warning"
    TRUTHFULNESS_NOT_VERIFIED = "truthfulness_not_verified"
    CONFIRMATION_REQUIRED = "confirmation_required"


class LLMCandidateApplicationPlanItem(BaseModel):
    """Plan-only application guidance for one LLM rewrite candidate."""

    candidate_id: str = Field(min_length=1)
    source_action: str = Field(min_length=1)
    plan_status: LLMApplicationPlanStatus
    target_section: str | None = None
    target_item_id: str | None = None
    original_text: str | None = None
    candidate_text: str | None = None
    provider: str | None = None
    risk_level: str | None = None
    needs_confirmation: bool = True
    validation_warnings: list[str] = Field(default_factory=list)
    block_reasons: list[LLMApplicationBlockReason] = Field(default_factory=list)
    manual_review_notes: list[str] = Field(default_factory=list)
    decision_note: str | None = None
    application_instruction: str = Field(min_length=1)


class LLMCandidateApplicationPlan(BaseModel):
    """Plan-only artifact describing possible future manual candidate application."""

    total_candidates: int = Field(ge=0, default=0)
    total_decisions: int = Field(ge=0, default=0)
    planned_count: int = Field(ge=0, default=0)
    blocked_count: int = Field(ge=0, default=0)
    needs_manual_edit_count: int = Field(ge=0, default=0)
    excluded_count: int = Field(ge=0, default=0)
    unmapped_count: int = Field(ge=0, default=0)
    items: list[LLMCandidateApplicationPlanItem] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    safety_notice: str = Field(min_length=1)
    source_files: dict[str, str] = Field(default_factory=dict)
    plan_only: bool = True
    summary: str = Field(min_length=1)

    @model_validator(mode="after")
    def _always_plan_only(self) -> LLMCandidateApplicationPlan:
        if self.plan_only is not True:
            raise ValueError("LLM application plans must always be plan_only=True")
        return self
