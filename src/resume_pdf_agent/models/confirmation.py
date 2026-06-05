"""Pydantic models for M14 user confirmation workflow."""

from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, Field, model_validator


class ConfirmationItemType(str, Enum):
    """Types of items that may require user confirmation."""

    TRUTHFULNESS_ISSUE = "truthfulness_issue"
    UNSUPPORTED_CLAIM = "unsupported_claim"
    UNSUPPORTED_METRIC = "unsupported_metric"
    NEEDS_CONFIRMATION_BULLET = "needs_confirmation_bullet"
    RISKY_ENHANCED_BULLET = "risky_enhanced_bullet"
    UNVERIFIABLE_QUANTIFIED_CLAIM = "unverifiable_quantified_claim"
    LEADERSHIP_EXAGGERATION_RISK = "leadership_exaggeration_risk"
    MISSING_EVIDENCE = "missing_evidence"
    GAP_ANALYSIS_WARNING = "gap_analysis_warning"
    GENERIC_REVIEW_ITEM = "generic_review_item"


class ConfirmationPriority(str, Enum):
    """Priority levels for confirmation items."""

    INFO = "info"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    BLOCKING = "blocking"


class ConfirmationDecisionType(str, Enum):
    """Supported user decision types for confirmation items."""

    APPROVE = "approve"
    REJECT = "reject"
    NEEDS_EDITING = "needs_editing"
    PROVIDE_EVIDENCE = "provide_evidence"
    IGNORE_FOR_NOW = "ignore_for_now"


class ConfirmationItemStatus(str, Enum):
    """Status of a confirmation item after review."""

    PENDING = "pending"
    RESOLVED = "resolved"
    REJECTED = "rejected"
    NEEDS_EDITING = "needs_editing"
    IGNORED = "ignored"
    BLOCKED = "blocked"


class ConfirmationItem(BaseModel):
    """A single item requiring user review before final PDF generation.

    Each item represents a claim, metric, or issue detected by the
    truthfulness checker, bullet enhancement engine, or gap analysis
    that may need user attention.
    """

    item_id: str = Field(min_length=1)
    item_type: ConfirmationItemType
    priority: ConfirmationPriority
    status: ConfirmationItemStatus = ConfirmationItemStatus.PENDING
    source_stage: str
    source_id: str | None = None
    source_experience_id: str | None = None
    claim_text: str = Field(min_length=1)
    reason: str = Field(min_length=1)
    suggested_user_action: str = Field(min_length=1)
    related_criteria_ids: list[str] = Field(default_factory=list)
    risk_flags: list[str] = Field(default_factory=list)
    requires_user_decision: bool = False
    blocks_final_pdf: bool = False

    @model_validator(mode="after")
    def _blocking_priority_consistency(self) -> ConfirmationItem:
        if self.priority == ConfirmationPriority.BLOCKING and not self.blocks_final_pdf:
            self.blocks_final_pdf = True
        return self

    @model_validator(mode="after")
    def _blocking_implies_decision(self) -> ConfirmationItem:
        if self.blocks_final_pdf and not self.requires_user_decision:
            # Auto-set: if it blocks final PDF, user must decide.
            self.requires_user_decision = True
        return self


class ConfirmationPacket(BaseModel):
    """A collection of confirmation items for user review."""

    packet_id: str = Field(min_length=1)
    items: list[ConfirmationItem] = Field(default_factory=list)
    blocking_count: int = Field(ge=0, default=0)
    high_priority_count: int = Field(ge=0, default=0)
    pending_count: int = Field(ge=0, default=0)
    can_generate_final_pdf: bool = True
    warnings: list[str] = Field(default_factory=list)
    summary: str = Field(min_length=1)

    @model_validator(mode="after")
    def _summary_indicates_blocking(self) -> ConfirmationPacket:
        if not self.can_generate_final_pdf and self.blocking_count == 0:
            raise ValueError(
                "can_generate_final_pdf is false but blocking_count is 0"
            )
        return self


class ConfirmationDecision(BaseModel):
    """A single user decision on a confirmation item."""

    item_id: str = Field(min_length=1)
    decision: ConfirmationDecisionType
    user_note: str | None = None
    replacement_text: str | None = None
    provided_evidence: str | None = None

    @model_validator(mode="after")
    def _provide_evidence_requires_evidence(self) -> ConfirmationDecision:
        if (
            self.decision == ConfirmationDecisionType.PROVIDE_EVIDENCE
            and not self.provided_evidence
        ):
            raise ValueError(
                "Decision 'provide_evidence' requires provided_evidence to be non-empty"
            )
        return self

    @model_validator(mode="after")
    def _needs_editing_requires_detail(self) -> ConfirmationDecision:
        if self.decision == ConfirmationDecisionType.NEEDS_EDITING:
            if not self.replacement_text and not self.user_note:
                raise ValueError(
                    "Decision 'needs_editing' requires replacement_text or user_note"
                )
        return self


class ConfirmationDecisionSet(BaseModel):
    """A set of user decisions applied to a confirmation packet."""

    decisions: list[ConfirmationDecision] = Field(default_factory=list)
    reviewer_name: str | None = None
    reviewed_at: str | None = None
    notes: str | None = None


class ConfirmationReviewResult(BaseModel):
    """Result of applying user decisions to a confirmation packet."""

    packet_id: str = Field(min_length=1)
    decisions_applied: int = Field(ge=0, default=0)
    unresolved_items: list[ConfirmationItem] = Field(default_factory=list)
    resolved_items: list[ConfirmationItem] = Field(default_factory=list)
    rejected_items: list[ConfirmationItem] = Field(default_factory=list)
    needs_editing_items: list[ConfirmationItem] = Field(default_factory=list)
    can_generate_final_pdf: bool = True
    warnings: list[str] = Field(default_factory=list)
    summary: str = Field(min_length=1)
