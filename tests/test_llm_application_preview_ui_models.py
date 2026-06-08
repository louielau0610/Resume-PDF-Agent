"""Model tests for M25 application preview UI."""

from __future__ import annotations

from resume_pdf_agent.models.llm_application_preview_ui import (
    LLMApplicationPreviewItemView,
    LLMApplicationPreviewPageContext,
    LLMApplicationPreviewStatusGroup,
)


def test_valid_preview_item_view():
    item = LLMApplicationPreviewItemView(
        candidate_id="c1",
        plan_status="planned",
        source_action="approve_candidate",
        original_text="Original.",
        candidate_text="Rewrite.",
        can_copy_candidate_text=True,
        safety_labels=["Plan only"],
    )
    assert item.candidate_id == "c1"
    assert item.can_copy_candidate_text is True


def test_valid_status_group():
    group = LLMApplicationPreviewStatusGroup(
        status="blocked",
        title="Blocked",
        description="Blocked items.",
        count=1,
        item_ids=["c1"],
    )
    assert group.count == 1


def test_valid_page_context_plan_only():
    context = LLMApplicationPreviewPageContext(
        page_title="Preview",
        generated_from="plan.json",
        plan_only=True,
        total_candidates=1,
        safety_notice="Plan only.",
    )
    assert context.plan_only is True


def test_preview_models_do_not_expose_application_mutation_fields():
    forbidden = {
        "applied_candidates",
        "apply_to_resume",
        "update_resume",
        "patch_resume",
    }
    for model in [
        LLMApplicationPreviewItemView,
        LLMApplicationPreviewPageContext,
        LLMApplicationPreviewStatusGroup,
    ]:
        assert forbidden.isdisjoint(model.model_fields)
