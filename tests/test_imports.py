import resume_pdf_agent
from resume_pdf_agent import config
from resume_pdf_agent.pipeline import run_resume_pipeline


def test_package_can_be_imported():
    assert resume_pdf_agent.__version__ == "0.1.0"


def test_config_constants_are_available():
    assert config.PROJECT_NAME == "resume_pdf_agent"
    assert config.DEFAULT_LANGUAGE == "zh-CN"
    assert config.SUPPORTED_EXPORT_FORMATS == ["pdf"]


def test_run_resume_pipeline_returns_status_and_stages():
    result = run_resume_pipeline({"target_role": "software engineer intern"})

    assert "status" in result
    assert result["status"] == "redirect"
    assert "stages" in result
    assert "pdf_generation" in result["stages"]


def test_supported_export_formats_only_include_pdf():
    result = run_resume_pipeline({})

    assert result["supported_export_formats"] == ["pdf"]
