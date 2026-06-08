"""Pydantic models for M27 manual patch preview without resume mutation."""

from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, Field, model_validator


class LLMManualPatchPreviewStatus(str, Enum):
    PREVIEW_READY = "preview_ready"
    BLOCKED = "blocked"
    NEEDS_MANUAL_EDIT = "needs_manual_edit"
    EXCLUDED = "excluded"
    UNMAPPED = "unmapped"
    SKIPPED = "skipped"


class LLMManualPatchPreviewBlockReason(str, Enum):
    VALIDATION_NOT_PASSED = "validation_not_passed"
    VALIDATION_REPORT_NOT_VALIDATION_ONLY = "validation_report_not_validation_only"
    VALIDATION_REPORT_INDICATES_RESUME_MODIFIED = "validation_report_indicates_resume_modified"
    VALIDATION_REPORT_INDICATES_PATCH_GENERATED = "validation_report_indicates_patch_generated"
    MISSING_PLAN_ITEM = "missing_plan_item"
    MISSING_VALIDATION_ITEM = "missing_validation_item"
    MISSING_CANDIDATE_ID = "missing_candidate_id"
    MISSING_TARGET_SECTION = "missing_target_section"
    MISSING_TARGET_ITEM_ID = "missing_target_item_id"
    MISSING_ORIGINAL_TEXT = "missing_original_text"
    MISSING_CANDIDATE_TEXT = "missing_candidate_text"
    CANDIDATE_TEXT_SAME_AS_ORIGINAL = "candidate_text_same_as_original"
    CANDIDATE_NEEDS_CONFIRMATION = "candidate_needs_confirmation"
    CANDIDATE_HAS_VALIDATION_WARNINGS = "candidate_has_validation_warnings"
    CANDIDATE_BLOCKED_BY_M26 = "candidate_blocked_by_m26"
    TRUTHFULNESS_NOT_VERIFIED = "truthfulness_not_verified"
    CONFIRMATION_REQUIRED = "confirmation_required"
    EXECUTABLE_PATCH_FORBIDDEN = "executable_patch_forbidden"
    MANUAL_REVIEW_REQUIRED = "manual_review_required"


class LLMManualPatchPreviewItem(BaseModel):
    candidate_id: str = Field(min_length=1)
    preview_status: LLMManualPatchPreviewStatus
    target_section: str | None = None
    target_item_id: str | None = None
    original_text: str | None = None
    proposed_text: str | None = None
    diff_preview: list[str] = Field(default_factory=list)
    unified_diff_preview: str | None = None
    validation_status: str | None = None
    block_reasons: list[str] = Field(default_factory=list)
    safety_notes: list[str] = Field(default_factory=list)
    manual_instruction: str = Field(min_length=1)
    can_copy_for_manual_review: bool = False


class LLMManualPatchPreviewReport(BaseModel):
    preview_only: bool = True
    final_resume_modified: bool = False
    executable_patch_generated: bool = False
    total_items: int = Field(ge=0, default=0)
    preview_ready_count: int = Field(ge=0, default=0)
    blocked_count: int = Field(ge=0, default=0)
    needs_manual_edit_count: int = Field(ge=0, default=0)
    excluded_count: int = Field(ge=0, default=0)
    unmapped_count: int = Field(ge=0, default=0)
    skipped_count: int = Field(ge=0, default=0)
    items: list[LLMManualPatchPreviewItem] = Field(default_factory=list)
    global_warnings: list[str] = Field(default_factory=list)
    safety_notice: str = Field(min_length=1)
    source_files: dict[str, str] = Field(default_factory=dict)
    summary: str = Field(min_length=1)

    @model_validator(mode="after")
    def _always_preview_only(self) -> LLMManualPatchPreviewReport:
        if self.preview_only is not True:
            raise ValueError("preview_only must always be True")
        if self.final_resume_modified is not False:
            raise ValueError("final_resume_modified must always be False")
        if self.executable_patch_generated is not False:
            raise ValueError("executable_patch_generated must always be False")
        return self
