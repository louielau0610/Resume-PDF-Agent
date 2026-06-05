"""Confirmation packet builder for M14.

Collects risky or uncertain items from truthfulness, enhancement, and
gap analysis results into a reviewable ConfirmationPacket.
"""

from __future__ import annotations

import uuid

from resume_pdf_agent.models.confirmation import (
    ConfirmationItem,
    ConfirmationItemStatus,
    ConfirmationItemType,
    ConfirmationPacket,
    ConfirmationPriority,
)
from resume_pdf_agent.models.enhancement import (
    BulletEnhancementResult,
    BulletEnhancementStatus,
    ExperienceEnhancementResult,
)
from resume_pdf_agent.models.resume_content import ResumeContent
from resume_pdf_agent.models.truthfulness import (
    TruthfulnessCheckResult,
    TruthfulnessIssueType,
    TruthfulnessSeverity,
)
from resume_pdf_agent.models.analysis import GapAnalysisResult
from resume_pdf_agent.models.enums import EvidenceLevel, MetricStatus


def _make_item_id(prefix: str) -> str:
    """Generate a stable, deterministic item ID."""
    short = uuid.uuid4().hex[:8]
    return f"{prefix}_{short}"


def _severity_to_priority(severity: TruthfulnessSeverity) -> ConfirmationPriority:
    """Map truthfulness severity to confirmation priority."""
    mapping = {
        TruthfulnessSeverity.HIGH: ConfirmationPriority.BLOCKING,
        TruthfulnessSeverity.MEDIUM: ConfirmationPriority.HIGH,
        TruthfulnessSeverity.LOW: ConfirmationPriority.MEDIUM,
        TruthfulnessSeverity.INFO: ConfirmationPriority.LOW,
    }
    return mapping.get(severity, ConfirmationPriority.INFO)


def _issue_type_to_item_type(issue_type: TruthfulnessIssueType) -> ConfirmationItemType:
    """Map truthfulness issue type to confirmation item type."""
    mapping = {
        TruthfulnessIssueType.UNSUPPORTED_EVIDENCE: ConfirmationItemType.UNSUPPORTED_CLAIM,
        TruthfulnessIssueType.UNSUPPORTED_METRIC: ConfirmationItemType.UNSUPPORTED_METRIC,
        TruthfulnessIssueType.NEEDS_CONFIRMATION: ConfirmationItemType.NEEDS_CONFIRMATION_BULLET,
        TruthfulnessIssueType.UNVERIFIABLE_QUANTIFIED_CLAIM: ConfirmationItemType.UNVERIFIABLE_QUANTIFIED_CLAIM,
        TruthfulnessIssueType.LEADERSHIP_EXAGGERATION_RISK: ConfirmationItemType.LEADERSHIP_EXAGGERATION_RISK,
        TruthfulnessIssueType.METRIC_WITHOUT_SOURCE: ConfirmationItemType.UNSUPPORTED_METRIC,
        TruthfulnessIssueType.TOOL_OR_METHOD_NOT_SUPPORTED: ConfirmationItemType.UNSUPPORTED_CLAIM,
        TruthfulnessIssueType.SOURCE_EXPERIENCE_MISMATCH: ConfirmationItemType.MISSING_EVIDENCE,
        TruthfulnessIssueType.RISK_FLAG: ConfirmationItemType.GENERIC_REVIEW_ITEM,
        TruthfulnessIssueType.GAP_ANALYSIS_WARNING: ConfirmationItemType.GAP_ANALYSIS_WARNING,
        TruthfulnessIssueType.GENERIC_TRUTHFULNESS_WARNING: ConfirmationItemType.GENERIC_REVIEW_ITEM,
    }
    return mapping.get(issue_type, ConfirmationItemType.GENERIC_REVIEW_ITEM)


def _should_block_pdf(
    item_type: ConfirmationItemType,
    priority: ConfirmationPriority,
) -> bool:
    """Determine if a confirmation item should block final PDF generation."""
    # Blocking items
    blocking_types = {
        ConfirmationItemType.UNSUPPORTED_CLAIM,
        ConfirmationItemType.UNSUPPORTED_METRIC,
    }
    if item_type in blocking_types:
        return True
    if priority == ConfirmationPriority.BLOCKING:
        return True
    return False


def build_confirmation_packet(
    resume_content: ResumeContent,
    truthfulness_result: TruthfulnessCheckResult | None = None,
    bullet_enhancement_result: BulletEnhancementResult | None = None,
    gap_analysis_result: GapAnalysisResult | None = None,
) -> ConfirmationPacket:
    """Build a confirmation packet from workflow analysis results.

    Parameters
    ----------
    resume_content : ResumeContent
        The user's resume content with bullets to review.
    truthfulness_result : TruthfulnessCheckResult | None
        Result from the truthfulness checking stage.
    bullet_enhancement_result : BulletEnhancementResult | None
        Result from the bullet enhancement stage.
    gap_analysis_result : GapAnalysisResult | None
        Result from the gap analysis stage.

    Returns
    -------
    ConfirmationPacket
        Structured packet of items needing user review.
    """
    items: list[ConfirmationItem] = []

    # ── A. Truthfulness issues ──────────────────────────────────────────
    if truthfulness_result is not None:
        for issue in truthfulness_result.issues:
            item_type = _issue_type_to_item_type(issue.issue_type)
            priority = _severity_to_priority(issue.severity)
            blocks = _should_block_pdf(item_type, priority)

            items.append(
                ConfirmationItem(
                    item_id=_make_item_id("truth"),
                    item_type=item_type,
                    priority=priority,
                    source_stage="truthfulness_check",
                    source_id=issue.issue_id,
                    source_experience_id=issue.source_id,
                    claim_text=issue.claim_text,
                    reason=issue.reason,
                    suggested_user_action=issue.suggested_action,
                    related_criteria_ids=list(issue.related_criteria_ids),
                    risk_flags=[],
                    requires_user_decision=priority in (
                        ConfirmationPriority.BLOCKING,
                        ConfirmationPriority.HIGH,
                        ConfirmationPriority.MEDIUM,
                    ),
                    blocks_final_pdf=blocks,
                )
            )

    # ── B. Bullet enhancement candidates ────────────────────────────────
    if bullet_enhancement_result is not None:
        for exp_result in bullet_enhancement_result.experience_results:
            for candidate in exp_result.candidates:
                # Check if this candidate needs confirmation
                needs_review = (
                    candidate.needs_confirmation
                    or candidate.status
                    in (
                        BulletEnhancementStatus.NEEDS_USER_CONFIRMATION,
                        BulletEnhancementStatus.SKIPPED_DUE_TO_TRUTHFULNESS_RISK,
                    )
                    or bool(candidate.risk_flags)
                )
                if not needs_review:
                    continue

                # Determine priority based on evidence/metric status

                is_unsupported_evidence = (
                    candidate.evidence_level == EvidenceLevel.UNSUPPORTED
                )
                is_unsupported_metric = (
                    candidate.metric_status == MetricStatus.UNSUPPORTED
                )

                if is_unsupported_evidence or is_unsupported_metric:
                    priority = ConfirmationPriority.BLOCKING
                    item_type = (
                        ConfirmationItemType.UNSUPPORTED_CLAIM
                        if is_unsupported_evidence
                        else ConfirmationItemType.UNSUPPORTED_METRIC
                    )
                elif candidate.risk_flags:
                    priority = ConfirmationPriority.HIGH
                    item_type = ConfirmationItemType.RISKY_ENHANCED_BULLET
                else:
                    priority = ConfirmationPriority.MEDIUM
                    item_type = ConfirmationItemType.RISKY_ENHANCED_BULLET

                blocks = _should_block_pdf(item_type, priority)

                items.append(
                    ConfirmationItem(
                        item_id=_make_item_id("enh"),
                        item_type=item_type,
                        priority=priority,
                        source_stage="criteria_aware_content_enhancement",
                        source_id=candidate.candidate_id,
                        source_experience_id=candidate.source_experience_id,
                        claim_text=candidate.enhanced_text,
                        reason=candidate.rationale,
                        suggested_user_action=(
                            "请检查增强后的 bullet 是否准确反映了您的真实经历。"
                        ),
                        related_criteria_ids=list(candidate.targeted_criteria_ids),
                        risk_flags=list(candidate.risk_flags),
                        requires_user_decision=True,
                        blocks_final_pdf=blocks,
                    )
                )

    # ── C. ResumeContent bullets requiring confirmation ─────────────────
    for section in resume_content.sections:
        for bullet in section.bullets:
            if not bullet.needs_confirmation and not bullet.risk_flags:

                if (
                    bullet.evidence_level
                    not in (
                        EvidenceLevel.UNSUPPORTED,
                        EvidenceLevel.NEEDS_USER_CONFIRMATION,
                    )
                    and bullet.metric_status != MetricStatus.UNSUPPORTED
                ):
                    continue

            is_unsupported_evidence = (
                bullet.evidence_level == EvidenceLevel.UNSUPPORTED
            )
            is_unsupported_metric = (
                bullet.metric_status == MetricStatus.UNSUPPORTED
            )

            if is_unsupported_evidence:
                item_type = ConfirmationItemType.UNSUPPORTED_CLAIM
                priority = ConfirmationPriority.BLOCKING
            elif is_unsupported_metric:
                item_type = ConfirmationItemType.UNSUPPORTED_METRIC
                priority = ConfirmationPriority.BLOCKING
            elif bullet.needs_confirmation:
                item_type = ConfirmationItemType.NEEDS_CONFIRMATION_BULLET
                priority = ConfirmationPriority.HIGH
            else:
                item_type = ConfirmationItemType.GENERIC_REVIEW_ITEM
                priority = ConfirmationPriority.MEDIUM

            blocks = _should_block_pdf(item_type, priority)

            items.append(
                ConfirmationItem(
                    item_id=_make_item_id("bullet"),
                    item_type=item_type,
                    priority=priority,
                    source_stage="resume_content",
                    source_experience_id=bullet.source_experience_id,
                    claim_text=bullet.text,
                    reason=(
                        "该声明缺少足够的证据支撑"
                        if is_unsupported_evidence
                        else "该指标缺少来源"
                        if is_unsupported_metric
                        else "该 bullet 需要用户确认"
                    ),
                    suggested_user_action=(
                        "请提供能够证明该声明的证据，或修改声明使其与已有证据一致。"
                    ),
                    related_criteria_ids=list(bullet.targeted_criteria_ids),
                    risk_flags=list(bullet.risk_flags),
                    requires_user_decision=True,
                    blocks_final_pdf=blocks,
                )
            )

    # ── D. Gap analysis warnings ────────────────────────────────────────
    if gap_analysis_result is not None:
        for warning_text in gap_analysis_result.truthfulness_warnings:
            items.append(
                ConfirmationItem(
                    item_id=_make_item_id("gap"),
                    item_type=ConfirmationItemType.GAP_ANALYSIS_WARNING,
                    priority=ConfirmationPriority.MEDIUM,
                    source_stage="gap_analysis",
                    claim_text=warning_text,
                    reason="差距分析阶段检测到的真实性警告。",
                    suggested_user_action="请检查该警告是否影响您的简历可信度。",
                    related_criteria_ids=[],
                    risk_flags=[],
                    requires_user_decision=False,
                    blocks_final_pdf=False,
                )
            )

    # ── Sort: blocking → high → medium → low → info ─────────────────────
    _priority_order = {
        ConfirmationPriority.BLOCKING: 0,
        ConfirmationPriority.HIGH: 1,
        ConfirmationPriority.MEDIUM: 2,
        ConfirmationPriority.LOW: 3,
        ConfirmationPriority.INFO: 4,
    }
    items.sort(key=lambda i: _priority_order.get(i.priority, 99))

    # ── Compute counts ──────────────────────────────────────────────────
    blocking_count = sum(
        1 for i in items if i.priority == ConfirmationPriority.BLOCKING
    )
    high_priority_count = sum(
        1 for i in items if i.priority == ConfirmationPriority.HIGH
    )
    pending_count = sum(
        1 for i in items if i.status == ConfirmationItemStatus.PENDING
    )
    can_generate = blocking_count == 0

    # ── Build summary ───────────────────────────────────────────────────
    summary_parts = [
        f"确认包共 {len(items)} 项需要审核。",
        f"其中阻塞项 {blocking_count} 个，高优先级 {high_priority_count} 个。",
    ]
    if can_generate:
        summary_parts.append("当前可以生成最终 PDF。")
    else:
        summary_parts.append(
            f"存在 {blocking_count} 个阻塞项，在审核完成前无法生成最终 PDF。"
        )

    return ConfirmationPacket(
        packet_id=_make_item_id("packet"),
        items=items,
        blocking_count=blocking_count,
        high_priority_count=high_priority_count,
        pending_count=pending_count,
        can_generate_final_pdf=can_generate,
        warnings=[],
        summary="".join(summary_parts),
    )
