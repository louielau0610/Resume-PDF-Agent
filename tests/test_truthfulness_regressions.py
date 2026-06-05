from resume_pdf_agent.models import (
    EvidenceLevel,
    ExportFormat,
    MetricStatus,
    ResumeBullet,
    ResumeContent,
    ResumeSection,
    ResumeType,
    RiskLevel,
)
from resume_pdf_agent.pipeline import run_resume_pipeline
from resume_pdf_agent.truthfulness import check_truthfulness


def test_issues_are_deduplicated_deterministically():
    content = ResumeContent(
        resume_type=ResumeType.DATA_SCIENCE_RESUME,
        sections=[
            ResumeSection(
                heading="Projects",
                bullets=[
                    ResumeBullet(
                        text="Unsupported claim.",
                        evidence_level=EvidenceLevel.UNSUPPORTED,
                        metric_status=MetricStatus.NOT_APPLICABLE,
                    ),
                    ResumeBullet(
                        text="Unsupported claim.",
                        evidence_level=EvidenceLevel.UNSUPPORTED,
                        metric_status=MetricStatus.NOT_APPLICABLE,
                    ),
                ],
            )
        ],
    )

    result = check_truthfulness(content)
    issue_keys = [(issue.issue_type, issue.claim_text, issue.reason) for issue in result.issues]

    assert len(issue_keys) == len(set(issue_keys))


def test_risk_counts_and_overall_risk_level_are_valid():
    result = check_truthfulness(
        ResumeContent(
            resume_type=ResumeType.DATA_SCIENCE_RESUME,
            sections=[
                ResumeSection(
                    heading="Projects",
                    bullets=[
                        ResumeBullet(
                            text="Unsupported claim.",
                            evidence_level=EvidenceLevel.UNSUPPORTED,
                            metric_status=MetricStatus.NOT_APPLICABLE,
                        )
                    ],
                )
            ],
        )
    )

    assert result.high_risk_count >= 1
    assert result.medium_risk_count >= 1
    assert result.low_risk_count >= 0
    assert result.overall_risk_level in set(RiskLevel)


def test_checker_does_not_mention_probability_or_internal_access():
    result = check_truthfulness(
        ResumeContent(
            resume_type=ResumeType.DATA_SCIENCE_RESUME,
            sections=[
                ResumeSection(
                    heading="Projects",
                    bullets=[
                        ResumeBullet(
                            text="Analyzed data.",
                            evidence_level=EvidenceLevel.USER_PROVIDED,
                            metric_status=MetricStatus.NOT_APPLICABLE,
                        )
                    ],
                )
            ],
        )
    )
    text = " ".join([result.summary, *result.warnings, *[issue.reason for issue in result.issues]]).lower()

    assert "hiring probability" not in text
    assert "offer probability" not in text
    assert "internal company screening" not in text


def test_pipeline_placeholder_includes_truthfulness_check_and_criteria_stages():
    result = run_resume_pipeline({"target_role": "data science intern"})

    assert "truthfulness_check" in result["stages"]
    assert "criteria_aware_content_enhancement" in result["stages"]
    assert "M5 deterministic truthfulness checker" in result["message"]


def test_export_format_still_only_includes_pdf():
    assert [item.value for item in ExportFormat] == ["pdf"]
