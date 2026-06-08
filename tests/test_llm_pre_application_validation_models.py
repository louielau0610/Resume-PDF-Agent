"""Tests for M26 pre-application validation models."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from resume_pdf_agent.models.llm_pre_application_validation import (
    LLMPreApplicationBlockReason,
    LLMPreApplicationValidationItem,
    LLMPreApplicationValidationReport,
    LLMPreApplicationValidationStatus,
)


def test_validation_status_enum():
    """All expected status values exist."""
    assert LLMPreApplicationValidationStatus.PASSED.value == "passed"
    assert LLMPreApplicationValidationStatus.BLOCKED.value == "blocked"
    assert LLMPreApplicationValidationStatus.NEEDS_MANUAL_EDIT.value == "needs_manual_edit"
    assert LLMPreApplicationValidationStatus.EXCLUDED.value == "excluded"
    assert LLMPreApplicationValidationStatus.UNMAPPED.value == "unmapped"


def test_block_reason_enum():
    """Block reason enum has expected values."""
    assert LLMPreApplicationBlockReason.MISSING_CANDIDATE_ID.value == "missing_candidate_id"
    assert LLMPreApplicationBlockReason.NEEDS_CONFIRMATION.value == "needs_confirmation"
    assert LLMPreApplicationBlockReason.UNSAFE_CLAIM_INDICATOR.value == "unsafe_claim_indicator"


def test_validation_item_valid():
    """Valid validation item can be constructed."""
    item = LLMPreApplicationValidationItem(
        candidate_id="c1",
        source_plan_status="planned",
        validation_status=LLMPreApplicationValidationStatus.PASSED,
    )
    assert item.candidate_id == "c1"
    assert item.can_proceed_to_patch_preview is False  # default
    assert item.needs_confirmation is True  # default


def test_validation_item_missing_candidate_id():
    """Validation item requires candidate_id."""
    with pytest.raises(ValidationError):
        LLMPreApplicationValidationItem(
            candidate_id="",
            source_plan_status="planned",
            validation_status=LLMPreApplicationValidationStatus.PASSED,
        )


def test_validation_report_valid():
    """Valid validation report with required fields."""
    report = LLMPreApplicationValidationReport(
        total_plan_items=1,
        passed_count=1,
        items=[
            LLMPreApplicationValidationItem(
                candidate_id="c1",
                source_plan_status="planned",
                validation_status=LLMPreApplicationValidationStatus.PASSED,
            ),
        ],
        safety_notice="Test safety notice.",
        summary="Test summary.",
    )
    assert report.validation_only is True
    assert report.final_resume_modified is False
    assert report.patch_generated is False
    assert report.can_proceed_to_patch_preview is False  # default


def test_validation_report_always_validation_only():
    """validation_only must always be True."""
    with pytest.raises(ValidationError):
        LLMPreApplicationValidationReport(
            total_plan_items=0,
            safety_notice="Test.",
            summary="Test.",
            validation_only=False,
        )


def test_validation_report_always_final_resume_modified_false():
    """final_resume_modified must always be False."""
    with pytest.raises(ValidationError):
        LLMPreApplicationValidationReport(
            total_plan_items=0,
            safety_notice="Test.",
            summary="Test.",
            final_resume_modified=True,
        )


def test_validation_report_always_patch_generated_false():
    """patch_generated must always be False."""
    with pytest.raises(ValidationError):
        LLMPreApplicationValidationReport(
            total_plan_items=0,
            safety_notice="Test.",
            summary="Test.",
            patch_generated=True,
        )


def test_validation_report_no_applied_candidates_field():
    """Report model has no applied_candidates field."""
    report = LLMPreApplicationValidationReport(
        total_plan_items=0,
        safety_notice="Test.",
        summary="Test.",
    )
    assert not hasattr(report, "applied_candidates")
    assert not hasattr(report, "auto_apply")
    assert not hasattr(report, "update_resume")
