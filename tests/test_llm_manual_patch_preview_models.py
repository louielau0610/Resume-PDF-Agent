"""Tests for M27 manual patch preview models."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from resume_pdf_agent.models.llm_manual_patch_preview import (
    LLMManualPatchPreviewBlockReason,
    LLMManualPatchPreviewItem,
    LLMManualPatchPreviewReport,
    LLMManualPatchPreviewStatus,
)


def test_preview_status_enum():
    assert LLMManualPatchPreviewStatus.PREVIEW_READY.value == "preview_ready"
    assert LLMManualPatchPreviewStatus.BLOCKED.value == "blocked"
    assert LLMManualPatchPreviewStatus.NEEDS_MANUAL_EDIT.value == "needs_manual_edit"
    assert LLMManualPatchPreviewStatus.EXCLUDED.value == "excluded"


def test_block_reason_enum():
    assert LLMManualPatchPreviewBlockReason.EXECUTABLE_PATCH_FORBIDDEN.value == "executable_patch_forbidden"
    assert LLMManualPatchPreviewBlockReason.TRUTHFULNESS_NOT_VERIFIED.value == "truthfulness_not_verified"


def test_preview_item_valid():
    item = LLMManualPatchPreviewItem(
        candidate_id="c1",
        preview_status=LLMManualPatchPreviewStatus.PREVIEW_READY,
        original_text="Original.",
        proposed_text="Proposed.",
        manual_instruction="Review manually.",
    )
    assert item.candidate_id == "c1"
    assert item.can_copy_for_manual_review is False  # default


def test_preview_item_requires_candidate_id():
    with pytest.raises(ValidationError):
        LLMManualPatchPreviewItem(
            candidate_id="",
            preview_status=LLMManualPatchPreviewStatus.PREVIEW_READY,
            manual_instruction="Review.",
        )


def test_preview_report_valid():
    report = LLMManualPatchPreviewReport(
        total_items=1,
        preview_ready_count=1,
        safety_notice="Test.",
        summary="Test.",
    )
    assert report.preview_only is True
    assert report.final_resume_modified is False
    assert report.executable_patch_generated is False


def test_preview_report_always_preview_only():
    with pytest.raises(ValidationError):
        LLMManualPatchPreviewReport(
            total_items=0,
            safety_notice="Test.",
            summary="Test.",
            preview_only=False,
        )


def test_preview_report_always_final_resume_modified_false():
    with pytest.raises(ValidationError):
        LLMManualPatchPreviewReport(
            total_items=0,
            safety_notice="Test.",
            summary="Test.",
            final_resume_modified=True,
        )


def test_preview_report_always_executable_patch_generated_false():
    with pytest.raises(ValidationError):
        LLMManualPatchPreviewReport(
            total_items=0,
            safety_notice="Test.",
            summary="Test.",
            executable_patch_generated=True,
        )


def test_preview_report_no_applied_candidates():
    report = LLMManualPatchPreviewReport(
        total_items=0,
        safety_notice="Test.",
        summary="Test.",
    )
    assert not hasattr(report, "applied_candidates")
    assert not hasattr(report, "patch_operations")


def test_preview_report_no_apply_fields():
    report = LLMManualPatchPreviewReport(
        total_items=0,
        safety_notice="Test.",
        summary="Test.",
    )
    assert not hasattr(report, "auto_apply")
    assert not hasattr(report, "update_resume")
    assert not hasattr(report, "execute_patch")
