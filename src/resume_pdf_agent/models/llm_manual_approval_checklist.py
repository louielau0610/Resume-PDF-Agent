"""Pydantic models for M28 manual approval checklist — human-only, no application."""

from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, Field, model_validator


class LLMManualApprovalChecklistItemStatus(str, Enum):
    REVIEW_REQUIRED = "review_required"
    BLOCKED = "blocked"
    NEEDS_MANUAL_EDIT = "needs_manual_edit"
    EXCLUDED = "excluded"
    UNMAPPED = "unmapped"
    SKIPPED = "skipped"


class LLMManualApprovalChecklistQuestionType(str, Enum):
    TRUTHFULNESS_EVIDENCE = "truthfulness_evidence"
    TARGET_MAPPING = "target_mapping"
    ORIGINAL_TEXT_MATCH = "original_text_match"
    PROPOSED_TEXT_QUALITY = "proposed_text_quality"
    UNSUPPORTED_CLAIM_RISK = "unsupported_claim_risk"
    CONFIRMATION_GATE = "confirmation_gate"
    FORMATTING_CONSISTENCY = "formatting_consistency"
    HUMAN_FINAL_DECISION = "human_final_decision"


class LLMManualApprovalChecklistQuestion(BaseModel):
    question_id: str = Field(min_length=1)
    question_type: LLMManualApprovalChecklistQuestionType
    prompt: str = Field(min_length=1)
    required: bool = True
    default_answer: str = "not_reviewed"
    allowed_answers: list[str] = Field(default_factory=lambda: ["not_reviewed", "yes", "no", "needs_more_info"])
    safety_note: str | None = None


class LLMManualApprovalChecklistItem(BaseModel):
    candidate_id: str = Field(min_length=1)
    checklist_status: LLMManualApprovalChecklistItemStatus
    source_preview_status: str
    target_section: str | None = None
    target_item_id: str | None = None
    original_text: str | None = None
    proposed_text: str | None = None
    diff_preview: list[str] = Field(default_factory=list)
    block_reasons: list[str] = Field(default_factory=list)
    safety_notes: list[str] = Field(default_factory=list)
    questions: list[LLMManualApprovalChecklistQuestion] = Field(default_factory=list)
    human_decision_default: str = "not_reviewed"
    can_be_considered_for_manual_edit: bool = False
    manual_instruction: str = Field(min_length=1)


class LLMManualApprovalChecklistReport(BaseModel):
    checklist_only: bool = True
    final_resume_modified: bool = False
    executable_patch_generated: bool = False
    final_approval_granted: bool = False
    total_items: int = Field(ge=0, default=0)
    review_required_count: int = Field(ge=0, default=0)
    blocked_count: int = Field(ge=0, default=0)
    needs_manual_edit_count: int = Field(ge=0, default=0)
    excluded_count: int = Field(ge=0, default=0)
    unmapped_count: int = Field(ge=0, default=0)
    skipped_count: int = Field(ge=0, default=0)
    items: list[LLMManualApprovalChecklistItem] = Field(default_factory=list)
    global_warnings: list[str] = Field(default_factory=list)
    safety_notice: str = Field(min_length=1)
    source_files: dict[str, str] = Field(default_factory=dict)
    summary: str = Field(min_length=1)

    @model_validator(mode="after")
    def _always_checklist_only(self) -> LLMManualApprovalChecklistReport:
        if self.checklist_only is not True:
            raise ValueError("checklist_only must always be True")
        if self.final_resume_modified is not False:
            raise ValueError("final_resume_modified must always be False")
        if self.executable_patch_generated is not False:
            raise ValueError("executable_patch_generated must always be False")
        if self.final_approval_granted is not False:
            raise ValueError("final_approval_granted must always be False")
        return self
