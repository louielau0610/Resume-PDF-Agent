"""Pydantic models for M26 strict pre-application validation."""

from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, Field, model_validator


class LLMPreApplicationValidationStatus(str, Enum):
    """Validation status for a single planned candidate."""

    PASSED = "passed"
    BLOCKED = "blocked"
    NEEDS_MANUAL_EDIT = "needs_manual_edit"
    EXCLUDED = "excluded"
    UNMAPPED = "unmapped"
    WARNING = "warning"
    SKIPPED = "skipped"


class LLMPreApplicationBlockReason(str, Enum):
    """Reasons a candidate cannot pass pre-application validation."""

    PLAN_NOT_PLAN_ONLY = "plan_not_plan_only"
    APPLIED_CANDIDATES_PRESENT = "applied_candidates_present"
    CANDIDATE_NOT_PLANNED = "candidate_not_planned"
    CANDIDATE_REJECTED = "candidate_rejected"
    CANDIDATE_IGNORED = "candidate_ignored"
    CANDIDATE_NEEDS_EDIT = "candidate_needs_edit"
    CANDIDATE_UNMAPPED = "candidate_unmapped"
    MISSING_CANDIDATE_ID = "missing_candidate_id"
    MISSING_ORIGINAL_TEXT = "missing_original_text"
    MISSING_CANDIDATE_TEXT = "missing_candidate_text"
    MISSING_TARGET_SECTION = "missing_target_section"
    MISSING_TARGET_ITEM_ID = "missing_target_item_id"
    HAS_VALIDATION_WARNINGS = "has_validation_warnings"
    NEEDS_CONFIRMATION = "needs_confirmation"
    TRUTHFULNESS_NOT_VERIFIED = "truthfulness_not_verified"
    CONFIRMATION_REQUIRED = "confirmation_required"
    UNSUPPORTED_DECISION_ACTION = "unsupported_decision_action"
    DUPLICATE_DECISION = "duplicate_decision"
    UNKNOWN_CANDIDATE_ID = "unknown_candidate_id"
    SUMMARY_WARNING = "summary_warning"
    SOURCE_MISMATCH = "source_mismatch"
    UNSAFE_STATUS_TRANSITION = "unsafe_status_transition"
    EMPTY_CANDIDATE_TEXT = "empty_candidate_text"
    CANDIDATE_SAME_AS_ORIGINAL = "candidate_same_as_original"
    CANDIDATE_TOO_LONG = "candidate_too_long"
    CANDIDATE_TOO_SHORT = "candidate_too_short"
    UNSAFE_CLAIM_INDICATOR = "unsafe_claim_indicator"
    MANUAL_REVIEW_REQUIRED = "manual_review_required"


class LLMPreApplicationValidationItem(BaseModel):
    """Validation result for a single planned candidate application item."""

    candidate_id: str = Field(min_length=1)
    source_plan_status: str
    validation_status: LLMPreApplicationValidationStatus
    target_section: str | None = None
    target_item_id: str | None = None
    original_text_present: bool = False
    candidate_text_present: bool = False
    needs_confirmation: bool = True
    validation_warnings: list[str] = Field(default_factory=list)
    block_reasons: list[str] = Field(default_factory=list)
    manual_review_notes: list[str] = Field(default_factory=list)
    can_proceed_to_patch_preview: bool = False
    safety_notes: list[str] = Field(default_factory=list)


class LLMPreApplicationValidationReport(BaseModel):
    """Strict pre-application validation report — validation only, no application."""

    total_plan_items: int = Field(ge=0, default=0)
    passed_count: int = Field(ge=0, default=0)
    blocked_count: int = Field(ge=0, default=0)
    needs_manual_edit_count: int = Field(ge=0, default=0)
    excluded_count: int = Field(ge=0, default=0)
    unmapped_count: int = Field(ge=0, default=0)
    warning_count: int = Field(ge=0, default=0)
    can_proceed_to_patch_preview: bool = False
    items: list[LLMPreApplicationValidationItem] = Field(default_factory=list)
    global_warnings: list[str] = Field(default_factory=list)
    safety_notice: str = Field(min_length=1)
    source_files: dict[str, str] = Field(default_factory=dict)
    validation_only: bool = True
    final_resume_modified: bool = False
    patch_generated: bool = False
    summary: str = Field(min_length=1)

    @model_validator(mode="after")
    def _always_validation_only(self) -> LLMPreApplicationValidationReport:
        if self.validation_only is not True:
            raise ValueError("validation_only must always be True")
        if self.final_resume_modified is not False:
            raise ValueError("final_resume_modified must always be False")
        if self.patch_generated is not False:
            raise ValueError("patch_generated must always be False")
        return self
