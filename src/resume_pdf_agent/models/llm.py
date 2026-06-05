"""Pydantic models for M16 optional LLM-assisted rewriting."""

from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, Field, model_validator

from resume_pdf_agent.models.enums import EvidenceLevel, MetricStatus


class LLMProviderType(str, Enum):
    """Supported LLM provider types."""

    DISABLED = "disabled"
    MOCK = "mock"
    EXTERNAL = "external"


class LLMRewriteMode(str, Enum):
    """Rewrite style modes."""

    CLARITY = "clarity"
    CONCISE = "concise"
    ATS_ALIGNED = "ats_aligned"
    IMPACT_FRAMING = "impact_framing"
    CONSERVATIVE_POLISH = "conservative_polish"


class LLMRewriteStatus(str, Enum):
    """Status of an LLM rewrite operation."""

    DISABLED = "disabled"
    REWRITTEN = "rewritten"
    REWRITTEN_WITH_WARNINGS = "rewritten_with_warnings"
    SKIPPED_DUE_TO_SAFETY = "skipped_due_to_safety"
    SKIPPED_DUE_TO_MISSING_PROVIDER = "skipped_due_to_missing_provider"
    FAILED_VALIDATION = "failed_validation"


class LLMRewriteOptions(BaseModel):
    """Configuration options for LLM-assisted rewriting."""

    enabled: bool = False
    provider: LLMProviderType = LLMProviderType.DISABLED
    mode: LLMRewriteMode = LLMRewriteMode.CONSERVATIVE_POLISH
    max_candidates: int = Field(ge=1, default=3)
    require_truthfulness_pass: bool = True
    require_confirmation_packet_clear: bool = False
    mark_all_llm_output_needs_confirmation: bool = True
    allow_new_metrics: bool = False
    allow_new_tools: bool = False
    allow_new_methods: bool = False
    allow_new_organizations: bool = False

    @model_validator(mode="after")
    def _disabled_implies_provider_disabled(self) -> LLMRewriteOptions:
        if not self.enabled and self.provider != LLMProviderType.DISABLED:
            self.provider = LLMProviderType.DISABLED
        return self


class LLMRewriteRequest(BaseModel):
    """A single bullet rewrite request sent to an LLM provider."""

    source_experience_id: str | None = None
    original_text: str = Field(min_length=1)
    deterministic_candidate_text: str | None = None
    allowed_facts: list[str] = Field(default_factory=list)
    allowed_keywords: list[str] = Field(default_factory=list)
    prohibited_additions: list[str] = Field(default_factory=list)
    targeted_criteria_ids: list[str] = Field(default_factory=list)
    mode: LLMRewriteMode = LLMRewriteMode.CONSERVATIVE_POLISH


class LLMRewriteCandidate(BaseModel):
    """A single LLM-rewritten bullet candidate."""

    candidate_id: str = Field(min_length=1)
    source_experience_id: str | None = None
    original_text: str = Field(min_length=1)
    rewritten_text: str = Field(min_length=1)
    provider: LLMProviderType
    mode: LLMRewriteMode
    status: LLMRewriteStatus
    evidence_level: EvidenceLevel = EvidenceLevel.NEEDS_USER_CONFIRMATION
    metric_status: MetricStatus = MetricStatus.NOT_APPLICABLE
    needs_confirmation: bool = True
    validation_warnings: list[str] = Field(default_factory=list)
    risk_flags: list[str] = Field(default_factory=list)
    rationale: str = ""


class LLMRewriteResult(BaseModel):
    """Result of an LLM-assisted rewrite operation."""

    status: LLMRewriteStatus
    provider: LLMProviderType
    candidates: list[LLMRewriteCandidate] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    errors: list[str] = Field(default_factory=list)
    candidates_generated: int = Field(ge=0, default=0)
    candidates_requiring_confirmation: int = Field(ge=0, default=0)
    summary: str = Field(min_length=1)

    @model_validator(mode="after")
    def _failed_validation_has_reason(self) -> LLMRewriteResult:
        if self.status == LLMRewriteStatus.FAILED_VALIDATION:
            if not self.warnings and not self.errors:
                raise ValueError(
                    "failed_validation status requires warnings or errors"
                )
        return self
