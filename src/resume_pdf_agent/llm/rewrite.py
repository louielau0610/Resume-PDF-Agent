"""LLM-assisted rewrite engine for M16.

Orchestrates optional LLM rewrite of resume bullets after deterministic
M6 enhancement and M5/M14 safeguards have run.
"""

from __future__ import annotations

import uuid

from resume_pdf_agent.llm.config import default_llm_rewrite_options
from resume_pdf_agent.llm.providers import get_llm_provider
from resume_pdf_agent.llm.validation import validate_llm_rewrite_candidate
from resume_pdf_agent.models.confirmation import ConfirmationPacket
from resume_pdf_agent.models.criteria import RoleCriteriaProfile
from resume_pdf_agent.models.enhancement import (
    BulletEnhancementResult,
    BulletEnhancementStatus,
)
from resume_pdf_agent.models.enums import EvidenceLevel, MetricStatus
from resume_pdf_agent.models.llm import (
    LLMProviderType,
    LLMRewriteCandidate,
    LLMRewriteMode,
    LLMRewriteOptions,
    LLMRewriteRequest,
    LLMRewriteResult,
    LLMRewriteStatus,
)
from resume_pdf_agent.models.resume_content import ResumeContent
from resume_pdf_agent.models.truthfulness import (
    RiskLevel,
    TruthfulnessCheckResult,
)


def rewrite_bullets_with_llm(
    resume_content: ResumeContent,
    bullet_enhancement_result: BulletEnhancementResult | None = None,
    truthfulness_result: TruthfulnessCheckResult | None = None,
    confirmation_packet: ConfirmationPacket | None = None,
    criteria_profile: RoleCriteriaProfile | None = None,
    options: LLMRewriteOptions | None = None,
) -> LLMRewriteResult:
    """Optionally rewrite resume bullets using an LLM provider.

    This function is designed to be safe-by-default:
    - Disabled unless explicitly enabled.
    - Skips if truthfulness or confirmation gates are not met.
    - Validates all LLM output against original facts.
    - All LLM-generated bullets default to needs_confirmation=True.

    Parameters
    ----------
    resume_content : ResumeContent
        The source resume content.
    bullet_enhancement_result : BulletEnhancementResult | None
        Optional M6 deterministic enhancement result.
    truthfulness_result : TruthfulnessCheckResult | None
        Optional M5 truthfulness check result.
    confirmation_packet : ConfirmationPacket | None
        Optional M14 confirmation packet.
    criteria_profile : RoleCriteriaProfile | None
        Optional criteria profile for keyword alignment.
    options : LLMRewriteOptions | None
        Rewrite configuration. Uses safe defaults if None.

    Returns
    -------
    LLMRewriteResult
        Rewrite candidates and status.
    """
    opts = options or default_llm_rewrite_options()

    # ── Gate: disabled ───────────────────────────────────────────────
    if not opts.enabled:
        return LLMRewriteResult(
            status=LLMRewriteStatus.DISABLED,
            provider=opts.provider,
            summary="LLM rewriting is disabled.",
        )

    # ── Gate: provider unavailable ───────────────────────────────────
    if opts.provider == LLMProviderType.DISABLED:
        return LLMRewriteResult(
            status=LLMRewriteStatus.SKIPPED_DUE_TO_MISSING_PROVIDER,
            provider=opts.provider,
            summary="LLM provider is set to disabled. No rewriting performed.",
        )

    # ── Gate: truthfulness ───────────────────────────────────────────
    if opts.require_truthfulness_pass and truthfulness_result is not None:
        if (
            truthfulness_result.overall_risk_level == RiskLevel.HIGH
            or not truthfulness_result.safe_to_proceed
        ):
            return LLMRewriteResult(
                status=LLMRewriteStatus.SKIPPED_DUE_TO_SAFETY,
                provider=opts.provider,
                warnings=[
                    "LLM rewriting skipped: truthfulness check has high risk or "
                    "safe_to_proceed is false."
                ],
                summary="LLM rewriting skipped due to truthfulness safety gate.",
            )

    # ── Gate: confirmation packet ────────────────────────────────────
    if opts.require_confirmation_packet_clear and confirmation_packet is not None:
        if not confirmation_packet.can_generate_final_pdf:
            return LLMRewriteResult(
                status=LLMRewriteStatus.SKIPPED_DUE_TO_SAFETY,
                provider=opts.provider,
                warnings=[
                    "LLM rewriting skipped: confirmation packet blocks final PDF."
                ],
                summary="LLM rewriting skipped due to confirmation safety gate.",
            )

    # ── Get provider ─────────────────────────────────────────────────
    try:
        provider = get_llm_provider(opts.provider)
    except Exception as exc:
        return LLMRewriteResult(
            status=LLMRewriteStatus.SKIPPED_DUE_TO_MISSING_PROVIDER,
            provider=opts.provider,
            errors=[str(exc)],
            summary=f"Failed to initialize LLM provider: {exc}",
        )

    # ── Collect source texts ─────────────────────────────────────────
    all_warnings: list[str] = []
    all_errors: list[str] = []
    candidates: list[LLMRewriteCandidate] = []

    # Build a lookup of enhanced candidates by experience_id
    enhanced_map: dict[str, list] = {}
    if bullet_enhancement_result is not None:
        for exp_res in bullet_enhancement_result.experience_results:
            enhanced_map[exp_res.experience_id] = exp_res.candidates

    # Collect allowed keywords from criteria
    allowed_keywords: list[str] = []
    if criteria_profile is not None:
        for criterion in criteria_profile.criteria:
            allowed_keywords.extend(criterion.keywords)
    allowed_keywords = list(dict.fromkeys(allowed_keywords))  # dedup, preserve order

    for experience in resume_content.experiences:
        exp_candidates = enhanced_map.get(experience.experience_id, [])

        # Prefer M6 enhanced candidate text if safe
        source_texts: list[str] = []
        for ec in exp_candidates:
            if ec.status not in (
                BulletEnhancementStatus.SKIPPED_DUE_TO_TRUTHFULNESS_RISK,
            ):
                if ec.enhanced_text:
                    source_texts.append(ec.enhanced_text)

        # Fall back to original responsibilities
        if not source_texts:
            source_texts = experience.responsibilities

        for text in source_texts[:opts.max_candidates]:
            if not text or not text.strip():
                continue

            # Build allowed facts from experience evidence
            allowed_facts: list[str] = list(experience.outcomes)
            allowed_facts.extend(experience.responsibilities)
            allowed_facts.extend(experience.tools_used)
            allowed_facts.extend(experience.methods_used)

            request = LLMRewriteRequest(
                source_experience_id=experience.experience_id,
                original_text=text,
                deterministic_candidate_text=(
                    exp_candidates[0].enhanced_text if exp_candidates else None
                ),
                allowed_facts=allowed_facts,
                allowed_keywords=allowed_keywords,
                prohibited_additions=[
                    "metrics", "tools", "methods", "organizations",
                    "percentages", "revenue figures",
                ],
                mode=opts.mode,
            )

            # Call provider
            try:
                rewritten = provider.rewrite(request)
            except NotImplementedError as exc:
                return LLMRewriteResult(
                    status=LLMRewriteStatus.SKIPPED_DUE_TO_MISSING_PROVIDER,
                    provider=opts.provider,
                    errors=[str(exc)],
                    summary=f"LLM provider not available: {exc}",
                )
            except Exception as exc:
                all_errors.append(f"Provider error: {exc}")
                continue

            # Validate
            is_valid, val_warnings, val_errors = validate_llm_rewrite_candidate(
                request, rewritten, opts,
            )

            cid = f"llm_{uuid.uuid4().hex[:8]}"

            if not is_valid:
                candidates.append(
                    LLMRewriteCandidate(
                        candidate_id=cid,
                        source_experience_id=experience.experience_id,
                        original_text=text,
                        rewritten_text=rewritten,
                        provider=opts.provider,
                        mode=opts.mode,
                        status=LLMRewriteStatus.FAILED_VALIDATION,
                        evidence_level=EvidenceLevel.UNSUPPORTED,
                        needs_confirmation=True,
                        validation_warnings=val_warnings + val_errors,
                        risk_flags=["validation_failed"],
                        rationale="LLM output failed safety validation.",
                    )
                )
                all_warnings.extend(val_errors)
                continue

            # ── Determine evidence/metric status ───────────────────
            source_evidence = EvidenceLevel.REASONABLY_INFERRED
            source_metric = MetricStatus.NOT_APPLICABLE
            if exp_candidates:
                source_evidence = exp_candidates[0].evidence_level
                source_metric = exp_candidates[0].metric_status

            # LLM output should not be stronger than source
            evidence = source_evidence
            metric = source_metric

            candidates.append(
                LLMRewriteCandidate(
                    candidate_id=cid,
                    source_experience_id=experience.experience_id,
                    original_text=text,
                    rewritten_text=rewritten,
                    provider=opts.provider,
                    mode=opts.mode,
                    status=(
                        LLMRewriteStatus.REWRITTEN_WITH_WARNINGS
                        if val_warnings
                        else LLMRewriteStatus.REWRITTEN
                    ),
                    evidence_level=evidence,
                    metric_status=metric,
                    needs_confirmation=opts.mark_all_llm_output_needs_confirmation,
                    validation_warnings=val_warnings,
                    risk_flags=[],
                    rationale="LLM-assisted conservative rewrite.",
                )
            )
            all_warnings.extend(val_warnings)

    # ── Result ───────────────────────────────────────────────────────
    if not candidates:
        return LLMRewriteResult(
            status=LLMRewriteStatus.SKIPPED_DUE_TO_SAFETY,
            provider=opts.provider,
            warnings=all_warnings,
            errors=all_errors,
            summary="No candidates were generated after safety validation.",
        )

    needs_conf_count = sum(1 for c in candidates if c.needs_confirmation)

    return LLMRewriteResult(
        status=(
            LLMRewriteStatus.REWRITTEN_WITH_WARNINGS
            if all_warnings
            else LLMRewriteStatus.REWRITTEN
        ),
        provider=opts.provider,
        candidates=candidates,
        warnings=all_warnings,
        errors=all_errors,
        candidates_generated=len(candidates),
        candidates_requiring_confirmation=needs_conf_count,
        summary=(
            f"LLM rewrite complete: {len(candidates)} candidates generated, "
            f"{needs_conf_count} require confirmation. "
            f"Provider: {opts.provider.value}."
        ),
    )
