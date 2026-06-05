from resume_pdf_agent.enhancement.safeguards import (
    collect_truthfulness_blockers,
    has_high_risk_truthfulness_issue,
    is_claim_safe_to_enhance,
    sanitize_metric_text,
    should_include_metric,
)
from resume_pdf_agent.models import (
    EvidenceLevel,
    Metric,
    MetricStatus,
    RiskLevel,
    TruthfulnessCheckResult,
    TruthfulnessIssue,
    TruthfulnessIssueType,
    TruthfulnessSeverity,
    ClaimEvidenceStatus,
)


def _high_risk_result():
    issue = TruthfulnessIssue(
        issue_id="issue_1",
        issue_type=TruthfulnessIssueType.UNSUPPORTED_EVIDENCE,
        severity=TruthfulnessSeverity.HIGH,
        source_type="resume_bullet",
        source_id="exp_1",
        claim_text="Unsupported claim",
        evidence_status=ClaimEvidenceStatus.UNSUPPORTED,
        reason="Unsupported evidence.",
        suggested_action="Remove or verify.",
    )
    return TruthfulnessCheckResult(
        overall_risk_level=RiskLevel.HIGH,
        issues=[issue],
        claims_checked=1,
        high_risk_count=1,
        medium_risk_count=0,
        low_risk_count=0,
        safe_to_proceed=False,
        summary="Risk found.",
    )


def test_high_risk_truthfulness_issue_is_detected_by_experience():
    result = _high_risk_result()

    assert has_high_risk_truthfulness_issue(result, "exp_1") is True
    assert has_high_risk_truthfulness_issue(result, "exp_2") is False
    assert collect_truthfulness_blockers(result, "exp_1")


def test_metric_inclusion_requires_source_support():
    unsupported = Metric(name="accuracy", value="0.9")
    supported = Metric(name="accuracy", value="0.9", source_note="user provided")

    assert should_include_metric(unsupported) is False
    assert sanitize_metric_text(unsupported) is None
    assert should_include_metric(supported) is True
    assert "accuracy" in sanitize_metric_text(supported)


def test_claim_safety_respects_m1_safeguards():
    assert is_claim_safe_to_enhance(
        EvidenceLevel.USER_PROVIDED,
        MetricStatus.NOT_APPLICABLE,
        False,
        [],
    )
    assert not is_claim_safe_to_enhance(EvidenceLevel.UNSUPPORTED, MetricStatus.NOT_APPLICABLE, False, [])
    assert not is_claim_safe_to_enhance(EvidenceLevel.USER_PROVIDED, MetricStatus.UNSUPPORTED, False, [])
    assert not is_claim_safe_to_enhance(EvidenceLevel.USER_PROVIDED, MetricStatus.NOT_APPLICABLE, True, [])
    assert not is_claim_safe_to_enhance(EvidenceLevel.USER_PROVIDED, MetricStatus.NOT_APPLICABLE, False, ["risk"])
