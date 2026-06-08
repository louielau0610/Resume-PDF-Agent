"""Pydantic models for M29 human-only final edit instruction pack — no application, no patch, no approval."""

from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, Field, model_validator


class LLMHumanFinalEditItemStatus(str, Enum):
    INSTRUCTION_READY = "instruction_ready"
    BLOCKED = "blocked"
    NEEDS_MANUAL_EDIT = "needs_manual_edit"
    EXCLUDED = "excluded"
    UNMAPPED = "unmapped"
    SKIPPED = "skipped"


class LLMHumanFinalEditInstructionType(str, Enum):
    EVIDENCE_COLLECTION = "evidence_collection"
    TARGET_VERIFICATION = "target_verification"
    ORIGINAL_TEXT_CHECK = "original_text_check"
    PROPOSED_TEXT_REVIEW = "proposed_text_review"
    UNSUPPORTED_CLAIM_REVIEW = "unsupported_claim_review"
    FORMATTING_REVIEW = "formatting_review"
    MANUAL_EDIT_GUIDANCE = "manual_edit_guidance"
    FINAL_HUMAN_DECISION = "final_human_decision"


class LLMHumanFinalEditInstruction(BaseModel):
    instruction_id: str = Field(min_length=1)
    instruction_type: LLMHumanFinalEditInstructionType
    title: str = Field(min_length=1)
    description: str = Field(min_length=1)
    required: bool = True
    default_status: str = "not_started"
    safety_note: str | None = None


class LLMHumanFinalEditItem(BaseModel):
    candidate_id: str = Field(min_length=1)
    item_status: LLMHumanFinalEditItemStatus
    source_checklist_status: str
    target_section: str | None = None
    target_item_id: str | None = None
    original_text: str | None = None
    proposed_text: str | None = None
    diff_preview: list[str] = Field(default_factory=list)
    block_reasons: list[str] = Field(default_factory=list)
    safety_notes: list[str] = Field(default_factory=list)
    required_evidence: list[str] = Field(default_factory=list)
    human_instructions: list[LLMHumanFinalEditInstruction] = Field(default_factory=list)
    manual_copy_text: str | None = None
    human_decision_default: str = "not_reviewed"
    can_be_considered_for_human_edit: bool = False
    system_final_approval_granted: bool = False


class LLMHumanFinalEditInstructionPack(BaseModel):
    human_instruction_only: bool = True
    final_resume_modified: bool = False
    executable_patch_generated: bool = False
    final_approval_granted: bool = False
    total_items: int = Field(ge=0, default=0)
    instruction_ready_count: int = Field(ge=0, default=0)
    blocked_count: int = Field(ge=0, default=0)
    needs_manual_edit_count: int = Field(ge=0, default=0)
    excluded_count: int = Field(ge=0, default=0)
    unmapped_count: int = Field(ge=0, default=0)
    skipped_count: int = Field(ge=0, default=0)
    items: list[LLMHumanFinalEditItem] = Field(default_factory=list)
    global_warnings: list[str] = Field(default_factory=list)
    safety_notice: str = Field(min_length=1)
    source_files: dict[str, str] = Field(default_factory=dict)
    summary: str = Field(min_length=1)

    @model_validator(mode="after")
    def _always_human_instruction_only(self) -> LLMHumanFinalEditInstructionPack:
        if self.human_instruction_only is not True:
            raise ValueError("human_instruction_only must always be True")
        if self.final_resume_modified is not False:
            raise ValueError("final_resume_modified must always be False")
        if self.executable_patch_generated is not False:
            raise ValueError("executable_patch_generated must always be False")
        if self.final_approval_granted is not False:
            raise ValueError("final_approval_granted must always be False")
        return self
