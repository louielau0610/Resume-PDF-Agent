"""Tests for M14 confirmation markdown renderer."""

from __future__ import annotations

from resume_pdf_agent.confirmation.markdown import render_confirmation_review_markdown
from resume_pdf_agent.models.confirmation import (
    ConfirmationItem,
    ConfirmationItemType,
    ConfirmationPacket,
    ConfirmationPriority,
)


def _make_packet() -> ConfirmationPacket:
    items = [
        ConfirmationItem(
            item_id="item1",
            item_type=ConfirmationItemType.UNSUPPORTED_CLAIM,
            priority=ConfirmationPriority.BLOCKING,
            source_stage="truthfulness_check",
            claim_text="Led a team of 50 people",
            reason="No evidence for team size",
            suggested_user_action="请提供团队规模的证明",
            blocks_final_pdf=True,
            requires_user_decision=True,
        ),
    ]
    return ConfirmationPacket(
        packet_id="test_packet",
        items=items,
        blocking_count=1,
        high_priority_count=0,
        pending_count=1,
        can_generate_final_pdf=False,
        summary="测试包",
    )


class TestRenderConfirmationReviewMarkdown:

    def test_renders_chinese_title(self):
        """Markdown should include Chinese title."""
        packet = _make_packet()
        md = render_confirmation_review_markdown(packet)
        assert "简历确认审核报告" in md

    def test_renders_packet_summary(self):
        """Markdown should include packet summary section."""
        packet = _make_packet()
        md = render_confirmation_review_markdown(packet)
        assert "确认包概览" in md
        assert "test_packet" in md

    def test_renders_item_table(self):
        """Markdown should include an item table."""
        packet = _make_packet()
        md = render_confirmation_review_markdown(packet)
        assert "确认项列表" in md
        assert "item1" in md

    def test_renders_instructions(self):
        """Markdown should include review instructions."""
        packet = _make_packet()
        md = render_confirmation_review_markdown(packet)
        assert "如何审核" in md
        assert "仅批准您个人可以验证的声明" in md

    def test_renders_safety_declarations(self):
        """Markdown should include safety declarations."""
        packet = _make_packet()
        md = render_confirmation_review_markdown(packet)
        assert "不独立验证真实世界事实" in md
        assert "不预测录用概率" in md
        assert "不调用 LLM API" in md

    def test_no_hiring_probability_claim(self):
        """Markdown must not claim hiring probability."""
        packet = _make_packet()
        md = render_confirmation_review_markdown(packet)
        assert "hiring probability" not in md.lower()

    def test_no_internal_screening_claim(self):
        """Markdown must not claim internal screening access."""
        packet = _make_packet()
        md = render_confirmation_review_markdown(packet)
        assert "internal screening" not in md.lower()
