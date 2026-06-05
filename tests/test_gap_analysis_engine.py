from resume_pdf_agent.gap_analysis import analyze_criteria_gap
from resume_pdf_agent.models import (
    EducationEntry,
    ExperienceEntry,
    ExperienceType,
    MatchLevel,
    Metric,
    ResumeContent,
    ResumeType,
    SkillGroup,
    UserProfile,
)
from resume_pdf_agent.sample_data import (
    SAMPLE_CRITERIA_PROFILE,
    SAMPLE_RESUME_CONTENT,
    SAMPLE_USER_PROFILE,
)


def _result_by_id(result, criterion_id):
    return next(item for item in result.criteria_results if item.criterion_id == criterion_id)


def test_data_science_sample_produces_gap_analysis_result():
    result = analyze_criteria_gap(
        SAMPLE_USER_PROFILE,
        SAMPLE_CRITERIA_PROFILE,
        SAMPLE_RESUME_CONTENT,
    )

    assert result.profile_id == SAMPLE_CRITERIA_PROFILE.profile_id
    assert len(result.criteria_results) == len(SAMPLE_CRITERIA_PROFILE.criteria)
    assert result.overall_match_level in set(MatchLevel)


def test_profile_with_python_sql_statistics_and_ml_gets_relevant_stronger_matches():
    profile = UserProfile(
        full_name="Data Candidate",
        education=[
            EducationEntry(
                institution="Example University",
                degree="Bachelor",
                major="Statistics",
                core_courses=["Probability", "Database Systems"],
            )
        ],
        target_roles=["Data Science Intern"],
        skills=[SkillGroup(category="Data", skills=["Python", "SQL", "pandas", "scikit-learn"])],
    )
    content = ResumeContent(
        resume_type=ResumeType.DATA_SCIENCE_RESUME,
        experiences=[
            ExperienceEntry(
                experience_id="exp_ml",
                experience_type=ExperienceType.PROJECT,
                title="Machine Learning Project",
                raw_description="Built a machine learning model with Python and SQL data.",
                tools_used=["Python", "SQL", "pandas", "scikit-learn"],
                methods_used=["Model evaluation", "Regression"],
                outcomes=["Prepared model evaluation report."],
            )
        ],
    )

    result = analyze_criteria_gap(profile, SAMPLE_CRITERIA_PROFILE, content)

    assert _result_by_id(result, "ds_python_data_analysis").match_level in {
        MatchLevel.STRONG,
        MatchLevel.MEDIUM,
    }
    assert _result_by_id(result, "ds_sql_database_familiarity").match_level in {
        MatchLevel.STRONG,
        MatchLevel.MEDIUM,
    }
    assert _result_by_id(result, "ds_ml_project_evidence").match_level in {
        MatchLevel.STRONG,
        MatchLevel.MEDIUM,
    }


def test_profile_without_sql_reports_sql_missing_evidence_or_keyword():
    profile = UserProfile(
        full_name="No SQL",
        education=[
            EducationEntry(
                institution="Example University",
                degree="Bachelor",
                major="Statistics",
                core_courses=["Probability"],
            )
        ],
        target_roles=["Data Science Intern"],
        skills=[SkillGroup(category="Data", skills=["Python", "pandas"])],
    )

    result = analyze_criteria_gap(profile, SAMPLE_CRITERIA_PROFILE, None)
    sql_result = _result_by_id(result, "ds_sql_database_familiarity")

    assert "SQL" in sql_result.missing_evidence or "SQL" in result.missing_keywords


def test_impact_quantification_uses_metrics_or_outcomes_without_fabrication():
    profile = SAMPLE_USER_PROFILE
    with_metric = ResumeContent(
        resume_type=ResumeType.DATA_SCIENCE_RESUME,
        experiences=[
            ExperienceEntry(
                experience_id="exp_metric",
                experience_type=ExperienceType.PROJECT,
                title="Evaluated Model",
                metrics=[Metric(name="accuracy", value="0.82", source_note="user provided")],
            )
        ],
    )

    metric_result = analyze_criteria_gap(profile, SAMPLE_CRITERIA_PROFILE, with_metric)
    sample_result = analyze_criteria_gap(profile, SAMPLE_CRITERIA_PROFILE, SAMPLE_RESUME_CONTENT)
    no_content_result = analyze_criteria_gap(profile, SAMPLE_CRITERIA_PROFILE, None)

    assert _result_by_id(metric_result, "ds_measurable_impact_when_provided").match_level == MatchLevel.STRONG
    assert _result_by_id(sample_result, "ds_measurable_impact_when_provided").match_level == MatchLevel.MEDIUM
    assert _result_by_id(no_content_result, "ds_measurable_impact_when_provided").match_level == MatchLevel.MISSING
    all_actions = " ".join(
        action for item in no_content_result.criteria_results for action in item.suggested_actions
    )
    assert "30%" not in all_actions


def test_missing_keywords_are_deduplicated():
    result = analyze_criteria_gap(SAMPLE_USER_PROFILE, SAMPLE_CRITERIA_PROFILE, None)

    assert len(result.missing_keywords) == len(set(result.missing_keywords))
