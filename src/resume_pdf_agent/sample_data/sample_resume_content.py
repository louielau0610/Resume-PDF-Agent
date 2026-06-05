"""Generic sample resume content for schema validation."""

from resume_pdf_agent.models import (
    EvidenceLevel,
    ExperienceEntry,
    ExperienceType,
    MetricStatus,
    ResumeBullet,
    ResumeContent,
    ResumeSection,
    ResumeType,
)

SAMPLE_RESUME_CONTENT = ResumeContent(
    resume_type=ResumeType.DATA_SCIENCE_RESUME,
    summary="Student candidate targeting data science internship roles.",
    experiences=[
        ExperienceEntry(
            experience_id="exp_project_course_recommender",
            experience_type=ExperienceType.PROJECT,
            title="Course Recommendation Analysis Project",
            organization="Example University",
            raw_description=(
                "Analyzed anonymized course review data for a class project and "
                "built baseline recommendation features."
            ),
            responsibilities=[
                "Cleaned tabular course review data for exploratory analysis.",
                "Compared simple similarity-based recommendation approaches.",
            ],
            tools_used=["Python", "pandas", "scikit-learn"],
            methods_used=["Exploratory data analysis", "Cosine similarity"],
            outcomes=[
                "Prepared a reproducible notebook and final class presentation.",
            ],
            evidence_notes=[
                "Based on coursework project description provided in sample profile.",
            ],
        ),
        ExperienceEntry(
            experience_id="exp_course_stats_modeling",
            experience_type=ExperienceType.COURSEWORK,
            title="Statistical Modeling Coursework",
            organization="Example University",
            responsibilities=[
                "Applied regression and hypothesis testing methods to class datasets.",
            ],
            tools_used=["R", "Python"],
            methods_used=["Linear regression", "Hypothesis testing"],
            outcomes=[
                "Submitted written reports explaining assumptions and model limitations.",
            ],
            evidence_notes=[
                "Coursework sample without fabricated impact metrics.",
            ],
        ),
    ],
    sections=[
        ResumeSection(
            heading="Projects",
            bullets=[
                ResumeBullet(
                    text=(
                        "Cleaned anonymized course review data and compared baseline "
                        "similarity methods in a reproducible Python notebook."
                    ),
                    source_experience_id="exp_project_course_recommender",
                    targeted_criteria_ids=[
                        "ds_python_data_analysis",
                        "ds_data_cleaning_visualization",
                    ],
                    evidence_level=EvidenceLevel.USER_PROVIDED,
                    metric_status=MetricStatus.NOT_APPLICABLE,
                    needs_confirmation=False,
                ),
                ResumeBullet(
                    text=(
                        "Presented project findings with clear assumptions, limitations, "
                        "and next-step recommendations for a course audience."
                    ),
                    source_experience_id="exp_project_course_recommender",
                    targeted_criteria_ids=["ds_action_result_clarity"],
                    evidence_level=EvidenceLevel.USER_PROVIDED,
                    metric_status=MetricStatus.NOT_APPLICABLE,
                    needs_confirmation=False,
                ),
            ],
        ),
        ResumeSection(
            heading="Coursework",
            bullets=[
                ResumeBullet(
                    text=(
                        "Applied regression and hypothesis testing to class datasets "
                        "and documented modeling assumptions in written reports."
                    ),
                    source_experience_id="exp_course_stats_modeling",
                    targeted_criteria_ids=["ds_statistical_reasoning"],
                    evidence_level=EvidenceLevel.USER_PROVIDED,
                    metric_status=MetricStatus.NOT_APPLICABLE,
                    needs_confirmation=False,
                )
            ],
        ),
    ],
)
