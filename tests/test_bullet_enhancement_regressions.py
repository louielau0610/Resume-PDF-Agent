from resume_pdf_agent.enhancement import enhance_resume_bullets
from resume_pdf_agent.models import (
    ClaimEvidenceStatus,
    EvidenceLevel,
    EnhancedBulletCandidate,
    BulletEnhancementMode,
    BulletEnhancementStatus,
    ExportFormat,
    ExperienceEntry,
    ExperienceType,
    Metric,
    MetricStatus,
    ResumeContent,
    ResumeType,
    RiskLevel,
    TruthfulnessCheckResult,
    TruthfulnessIssue,
    TruthfulnessIssueType,
    TruthfulnessSeverity,
)
from resume_pdf_agent.pipeline import run_resume_pipeline


def test_unsupported_metadata_forces_confirmation_on_candidate_model():
    candidate = EnhancedBulletCandidate(
        candidate_id="candidate_1",
        enhanced_text="Unsupported draft.",
        mode=BulletEnhancementMode.CONSERVATIVE_REWRITE,
        status=BulletEnhancementStatus.NEEDS_USER_CONFIRMATION,
        evidence_level=EvidenceLevel.UNSUPPORTED,
        metric_status=MetricStatus.UNSUPPORTED,
        needs_confirmation=False,
        rationale="Testing validation.",
    )

    assert candidate.needs_confirmation is True


def test_high_risk_truthfulness_blocks_unsafe_enhancement():
    content = ResumeContent(
        resume_type=ResumeType.DATA_SCIENCE_RESUME,
        experiences=[
            ExperienceEntry(
                experience_id="exp_1",
                experience_type=ExperienceType.PROJECT,
                title="Risky Project",
                tools_used=["Python"],
            )
        ],
    )
    issue = TruthfulnessIssue(
        issue_id="issue_1",
        issue_type=TruthfulnessIssueType.UNSUPPORTED_EVIDENCE,
        severity=TruthfulnessSeverity.HIGH,
        source_type="resume_bullet",
        source_id="exp_1",
        claim_text="Unsupported claim",
        evidence_status=ClaimEvidenceStatus.UNSUPPORTED,
        reason="Unsupported.",
        suggested_action="Remove.",
    )
    truth = TruthfulnessCheckResult(
        overall_risk_level=RiskLevel.HIGH,
        issues=[issue],
        claims_checked=1,
        high_risk_count=1,
        medium_risk_count=0,
        low_risk_count=0,
        safe_to_proceed=False,
        summary="High risk.",
    )

    result = enhance_resume_bullets(content, truthfulness_result=truth)

    assert result.experience_results[0].skipped_reasons
    assert result.candidates_generated == 0


def test_engine_does_not_include_unsupported_metrics():
    content = ResumeContent(
        resume_type=ResumeType.DATA_SCIENCE_RESUME,
        experiences=[
            ExperienceEntry(
                experience_id="exp_1",
                experience_type=ExperienceType.PROJECT,
                title="Metric Project",
                tools_used=["Python"],
                metrics=[Metric(name="accuracy", value="0.99")],
            )
        ],
    )

    result = enhance_resume_bullets(content)
    text = " ".join(c.enhanced_text for r in result.experience_results for c in r.candidates)

    assert "0.99" not in text


def test_engine_output_avoids_probability_internal_access_and_llm_claims():
    content = ResumeContent(
        resume_type=ResumeType.DATA_SCIENCE_RESUME,
        experiences=[
            ExperienceEntry(
                experience_id="exp_1",
                experience_type=ExperienceType.PROJECT,
                title="Analysis Project",
                tools_used=["Python"],
            )
        ],
    )
    result = enhance_resume_bullets(content)
    text = " ".join(
        [
            result.summary,
            *result.global_warnings,
            *result.truthfulness_blockers,
            *[c.enhanced_text + " " + c.rationale for r in result.experience_results for c in r.candidates],
        ]
    ).lower()

    assert "hiring probability" not in text
    assert "internal company screening" not in text
    assert "llm" not in text


def test_pipeline_placeholder_includes_enhancement_stage():
    result = run_resume_pipeline({"target_role": "data science intern"})

    assert "criteria_aware_content_enhancement" in result["stages"]
    assert "M11 added" in result["message"]


def test_export_format_still_only_includes_pdf():
    assert [item.value for item in ExportFormat] == ["pdf"]
