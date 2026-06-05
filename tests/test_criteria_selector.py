from resume_pdf_agent.criteria import select_criteria_profiles
from resume_pdf_agent.models import ExportFormat, ResumeType
from resume_pdf_agent.pipeline import run_resume_pipeline


def test_select_criteria_profiles_data_science_role():
    profiles = select_criteria_profiles("data science")

    assert profiles[0].profile_id == "data_science_intern"


def test_select_criteria_profiles_software_engineer_role():
    profiles = select_criteria_profiles("software engineer")

    assert profiles[0].profile_id == "software_engineering_intern"


def test_select_criteria_profiles_research_cv_resume_type():
    profiles = select_criteria_profiles(resume_type=ResumeType.RESEARCH_CV)

    assert profiles[0].profile_id == "research_assistant"


def test_select_criteria_profiles_returns_at_most_max_results():
    profiles = select_criteria_profiles(max_results=2)

    assert len(profiles) <= 2


def test_pipeline_placeholder_still_includes_criteria_aware_stages():
    result = run_resume_pipeline({"target_role": "consulting intern"})

    assert "criteria_selection" in result["stages"]
    assert "gap_analysis" in result["stages"]
    assert "criteria_aware_content_enhancement" in result["stages"]
    assert "pdf_generation" in result["stages"]


def test_export_format_still_only_includes_pdf():
    assert [item.value for item in ExportFormat] == ["pdf"]
