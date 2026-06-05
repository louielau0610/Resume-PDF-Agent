"""Tests for M14 confirmation packet builder."""

from __future__ import annotations

import pytest

from resume_pdf_agent.confirmation.packet import build_confirmation_packet
from resume_pdf_agent.models.confirmation import (
    ConfirmationItemStatus,
    ConfirmationItemType,
    ConfirmationPriority,
)
from resume_pdf_agent.models.enums import (
    EvidenceLevel,
    MetricStatus,
    ResumeType,
)
from resume_pdf_agent.models.resume_content import (
    ExperienceEntry,
    ExperienceType,
    ResumeBullet,
    ResumeContent,
)
from resume_pdf_agent.models.truthfulness import (
    ClaimEvidenceStatus,
    TruthfulnessCheckResult,
    TruthfulnessIssue,
    TruthfulnessIssueType,
    TruthfulnessSeverity,
)
from resume_pdf_agent.models.enhancement import (
    BulletEnhancementMode,
    BulletEnhancementResult,
    BulletEnhancementStatus,
    EnhancedBulletCandidate,
    ExperienceEnhancementResult,
)
from resume_pdf_agent.models.analysis import GapAnalysisResult
from resume_pdf_agent.models.enums import MatchLevel, RiskLevel


# ── Helpers ────────────────────────────────────────────────────────────────

def _make_resume_content(with_unsupported: bool = False) -> ResumeContent:
    bullets: list[ResumeBullet] = []
    if with_unsupported:
        bullets.append(
            ResumeBullet(
                text="Led a team of 50 people",
                source_experience_id="exp1",
                evidence_level=EvidenceLevel.UNSUPPORTED,
                metric_status=MetricStatus.NOT_APPLICABLE,
                needs_confirmation=True,
            )
        )
    else:
        bullets.append(
            ResumeBullet(
                text="Analyzed data using Python",
                source_experience_id="exp1",
                evidence_level=EvidenceLevel.USER_PROVIDED,
                metric_status=MetricStatus.USER_PROVIDED,
            )
        )

    from resume_pdf_agent.models.resume_content import ResumeSection

    return ResumeContent(
        resume_type=ResumeType.DATA_SCIENCE_RESUME,
        summary="Test summary",
        experiences=[
            ExperienceEntry(
                experience_id="exp1",
                experience_type=ExperienceType.PROJECT,
                title="Test Project",
                organization="Test Org",
                raw_description="Test description",
                responsibilities=["Did stuff"],
            )
        ],
        sections=[
            ResumeSection(
                heading="Experience",
                bullets=bullets,
            )
        ],
    )


def _make_truthfulness_result(
    with_issues: bool = False,
) -> TruthfulnessCheckResult:
    issues: list[TruthfulnessIssue] = []
    if with_issues:
        issues.append(
            TruthfulnessIssue(
                issue_id="t1",
                issue_type=TruthfulnessIssueType.UNSUPPORTED_EVIDENCE,
                severity=TruthfulnessSeverity.HIGH,
                source_type="experience",
                source_id="exp1",
                claim_text="Led a team of 50 people",
                evidence_status=ClaimEvidenceStatus.UNSUPPORTED,
                reason="No evidence of team size",
                suggested_action="Provide evidence or revise claim",
                related_criteria_ids=[],
            )
        )
    return TruthfulnessCheckResult(
        overall_risk_level=RiskLevel.HIGH if with_issues else RiskLevel.LOW,
        issues=issues,
        claims_checked=1,
        high_risk_count=1 if with_issues else 0,
        medium_risk_count=0,
        low_risk_count=0,
        safe_to_proceed=not with_issues,
        summary="Test truthfulness result",
    )


def _make_enhancement_result(with_confirmation: bool = False) -> BulletEnhancementResult:
    candidates: list[EnhancedBulletCandidate] = []
    if with_confirmation:
        candidates.append(
            EnhancedBulletCandidate(
                candidate_id="c1",
                source_experience_id="exp1",
                original_text="Did stuff",
                enhanced_text="Led analysis of 50-person team",
                mode=BulletEnhancementMode.CRITERIA_ALIGNMENT,
                status=BulletEnhancementStatus.NEEDS_USER_CONFIRMATION,
                targeted_criteria_ids=[],
                evidence_level=EvidenceLevel.UNSUPPORTED,
                metric_status=MetricStatus.UNSUPPORTED,
                needs_confirmation=True,
                risk_flags=["unsupported_evidence"],
                rationale="Added team size, but evidence is unsupported",
            )
        )
    return BulletEnhancementResult(
        resume_type=ResumeType.DATA_SCIENCE_RESUME,
        experience_results=[
            ExperienceEnhancementResult(
                experience_id="exp1",
                title="Test Project",
                candidates=candidates,
            )
        ],
        candidates_generated=len(candidates),
        candidates_requiring_confirmation=len(candidates),
        safe_candidates_count=0,
        summary="Test enhancement result",
    )


def _make_gap_result() -> GapAnalysisResult:
    return GapAnalysisResult(
        profile_id="data_science_intern",
        overall_match_level=MatchLevel.MEDIUM,
        truthfulness_warnings=["Warning: low evidence coverage"],
    )


# ── Tests ──────────────────────────────────────────────────────────────────


class TestBuildConfirmationPacket:
    """Tests for build_confirmation_packet."""

    def test_empty_inputs_returns_empty_packet(self):
        """Empty/minimal inputs produce a packet with no or few items."""
        rc = _make_resume_content()
        packet = build_confirmation_packet(rc)
        assert packet.packet_id
        assert len(packet.items) == 0
        assert packet.can_generate_final_pdf is True
        assert packet.blocking_count == 0

    def test_unsupported_evidence_creates_blocking_item(self):
        """Unsupported evidence creates a blocking confirmation item."""
        rc = _make_resume_content(with_unsupported=True)
        packet = build_confirmation_packet(rc)
        assert len(packet.items) >= 1
        blocking = [i for i in packet.items if i.blocks_final_pdf]
        assert len(blocking) >= 1
        assert blocking[0].priority in (
            ConfirmationPriority.BLOCKING,
            ConfirmationPriority.HIGH,
        )

    def test_unsupported_metric_creates_blocking_item(self):
        """Unsupported metric creates a blocking confirmation item."""
        from resume_pdf_agent.models.resume_content import ResumeSection

        rc = ResumeContent(
            resume_type=ResumeType.DATA_SCIENCE_RESUME,
            experiences=[
                ExperienceEntry(
                    experience_id="exp1",
                    experience_type=ExperienceType.PROJECT,
                    title="Test",
                    organization="Org",
                    raw_description="desc",
                )
            ],
            sections=[
                ResumeSection(
                    heading="Experience",
                    bullets=[
                        ResumeBullet(
                            text="Improved accuracy by 50%",
                            source_experience_id="exp1",
                            evidence_level=EvidenceLevel.USER_PROVIDED,
                            metric_status=MetricStatus.UNSUPPORTED,
                        )
                    ],
                )
            ],
        )
        packet = build_confirmation_packet(rc)
        assert len(packet.items) >= 1
        assert any(
            i.item_type == ConfirmationItemType.UNSUPPORTED_METRIC
            for i in packet.items
        )

    def test_needs_confirmation_bullet_creates_item(self):
        """A bullet with needs_confirmation=True creates a confirmation item."""
        from resume_pdf_agent.models.resume_content import ResumeSection

        rc = ResumeContent(
            resume_type=ResumeType.DATA_SCIENCE_RESUME,
            experiences=[
                ExperienceEntry(
                    experience_id="exp1",
                    experience_type=ExperienceType.PROJECT,
                    title="Test",
                    organization="Org",
                    raw_description="desc",
                )
            ],
            sections=[
                ResumeSection(
                    heading="Experience",
                    bullets=[
                        ResumeBullet(
                            text="Need to verify this",
                            source_experience_id="exp1",
                            evidence_level=EvidenceLevel.NEEDS_USER_CONFIRMATION,
                            metric_status=MetricStatus.NOT_APPLICABLE,
                            needs_confirmation=True,
                        )
                    ],
                )
            ],
        )
        packet = build_confirmation_packet(rc)
        assert len(packet.items) >= 1

    def test_truthfulness_issues_create_items(self):
        """Truthfulness issues are collected into confirmation items."""
        rc = _make_resume_content()
        tr = _make_truthfulness_result(with_issues=True)
        packet = build_confirmation_packet(rc, truthfulness_result=tr)
        assert len(packet.items) >= 1
        assert any(
            i.source_stage == "truthfulness_check" for i in packet.items
        )

    def test_enhancement_candidates_create_items(self):
        """Enhancement candidates requiring confirmation are collected."""
        rc = _make_resume_content()
        er = _make_enhancement_result(with_confirmation=True)
        packet = build_confirmation_packet(rc, bullet_enhancement_result=er)
        assert len(packet.items) >= 1
        assert any(
            i.source_stage == "criteria_aware_content_enhancement"
            for i in packet.items
        )

    def test_gap_analysis_warnings_create_items(self):
        """Gap analysis truthfulness_warnings create items."""
        rc = _make_resume_content()
        gr = _make_gap_result()
        packet = build_confirmation_packet(rc, gap_analysis_result=gr)
        gap_items = [
            i for i in packet.items
            if i.item_type == ConfirmationItemType.GAP_ANALYSIS_WARNING
        ]
        assert len(gap_items) >= 1

    def test_packet_counts_are_correct(self):
        """Blocking/high/pending counts are accurate."""
        rc = _make_resume_content(with_unsupported=True)
        packet = build_confirmation_packet(rc)
        # blocking_count should match items with BLOCKING priority
        blocking = sum(
            1 for i in packet.items
            if i.priority == ConfirmationPriority.BLOCKING
        )
        assert packet.blocking_count == blocking
        assert packet.pending_count == len(packet.items)

    def test_packet_dedup_produces_stable_ids(self):
        """Item IDs should be unique and non-empty."""
        rc = _make_resume_content(with_unsupported=True)
        tr = _make_truthfulness_result(with_issues=True)
        packet = build_confirmation_packet(rc, truthfulness_result=tr)
        ids = [i.item_id for i in packet.items]
        assert len(ids) == len(set(ids))  # all unique
        assert all(ids)  # all non-empty

    def test_can_generate_final_pdf_no_blocking(self):
        """Without blocking items, can_generate_final_pdf is True."""
        rc = _make_resume_content()
        packet = build_confirmation_packet(rc)
        assert packet.can_generate_final_pdf is True

    def test_can_generate_final_pdf_with_blocking(self):
        """With blocking items, can_generate_final_pdf is False."""
        rc = _make_resume_content(with_unsupported=True)
        packet = build_confirmation_packet(rc)
        assert packet.can_generate_final_pdf is False

    def test_ordering_blocking_first(self):
        """Items are ordered: blocking first, then high, medium, low, info."""
        rc = _make_resume_content(with_unsupported=True)
        tr = _make_truthfulness_result(with_issues=True)
        gr = _make_gap_result()
        packet = build_confirmation_packet(
            rc, truthfulness_result=tr, gap_analysis_result=gr,
        )
        priorities = [i.priority for i in packet.items]
        order_map = {
            ConfirmationPriority.BLOCKING: 0,
            ConfirmationPriority.HIGH: 1,
            ConfirmationPriority.MEDIUM: 2,
            ConfirmationPriority.LOW: 3,
            ConfirmationPriority.INFO: 4,
        }
        for j in range(len(priorities) - 1):
            assert order_map[priorities[j]] <= order_map[priorities[j + 1]]


# ── Model validation tests ─────────────────────────────────────────────────

class TestConfirmationModels:
    """Tests for confirmation Pydantic model validation."""

    def test_confirmation_item_basic(self):
        """Basic ConfirmationItem creation."""
        from resume_pdf_agent.models.confirmation import ConfirmationItem

        item = ConfirmationItem(
            item_id="test1",
            item_type=ConfirmationItemType.UNSUPPORTED_CLAIM,
            priority=ConfirmationPriority.BLOCKING,
            source_stage="test",
            claim_text="Test claim",
            reason="Test reason",
            suggested_user_action="Test action",
        )
        # blocking priority should auto-set blocks_final_pdf
        assert item.blocks_final_pdf is True
        assert item.requires_user_decision is True
        assert item.status == ConfirmationItemStatus.PENDING
