from resume_pdf_agent.models import (
    EvidenceLevel,
    ExperienceEntry,
    ExperienceType,
    Metric,
    MetricStatus,
    ResumeBullet,
    ResumeContent,
    ResumeSection,
    ResumeType,
)
from resume_pdf_agent.truthfulness import extract_resume_claims


def test_extract_resume_claims_extracts_summary_experiences_metrics_and_bullets():
    content = ResumeContent(
        resume_type=ResumeType.DATA_SCIENCE_RESUME,
        summary="Data science candidate with Python experience.",
        experiences=[
            ExperienceEntry(
                experience_id="exp_1",
                experience_type=ExperienceType.PROJECT,
                title="Forecasting Project",
                raw_description="Built a forecasting model.",
                responsibilities=["Analyzed data."],
                tools_used=["Python"],
                methods_used=["Regression"],
                outcomes=["Prepared a report."],
                metrics=[Metric(name="accuracy", value="0.82", source_note="user provided")],
                evidence_notes=["Course project evidence."],
            )
        ],
        sections=[
            ResumeSection(
                heading="Projects",
                bullets=[
                    ResumeBullet(
                        text="Built a Python forecasting model.",
                        source_experience_id="exp_1",
                        targeted_criteria_ids=["criterion_1"],
                        evidence_level=EvidenceLevel.USER_PROVIDED,
                        metric_status=MetricStatus.USER_PROVIDED,
                    )
                ],
            )
        ],
    )

    claims = extract_resume_claims(content)
    text = " ".join(claim.text for claim in claims)

    assert "Data science candidate" in text
    assert "Built a forecasting model." in text
    assert "accuracy 0.82 user provided" in text
    assert "Built a Python forecasting model." in text
    bullet_claim = next(claim for claim in claims if claim.source_type == "resume_bullet")
    assert bullet_claim.evidence_level == EvidenceLevel.USER_PROVIDED
    assert bullet_claim.metric_status == MetricStatus.USER_PROVIDED
    assert bullet_claim.related_experience_id == "exp_1"
    assert bullet_claim.targeted_criteria_ids == ["criterion_1"]
