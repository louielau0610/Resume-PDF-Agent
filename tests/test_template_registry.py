import pytest

from resume_pdf_agent.models import InternalTemplateProfile
from resume_pdf_agent.templates.registry import (
    get_available_template_ids,
    load_all_template_profiles,
    load_template_profile,
)

EXPECTED_TEMPLATE_IDS = {
    "ats_student_basic",
    "data_science_technical",
    "software_engineering_technical",
    "finance_business",
    "consulting_business",
    "research_cv",
    "product_manager",
    "design_portfolio_light",
}


def test_get_available_template_ids_returns_all_expected_ids():
    assert set(get_available_template_ids()) == EXPECTED_TEMPLATE_IDS


def test_load_template_profile_loads_each_profile():
    for template_id in get_available_template_ids():
        template = load_template_profile(template_id)
        assert isinstance(template, InternalTemplateProfile)
        assert template.template_id == template_id
        assert template.sections
        assert 1 <= template.visual_complexity <= 5


def test_load_all_template_profiles_returns_eight_profiles():
    profiles = load_all_template_profiles()

    assert len(profiles) == 8
    assert all(isinstance(profile, InternalTemplateProfile) for profile in profiles)


def test_unknown_template_id_raises_clear_error():
    with pytest.raises(ValueError, match="Unknown template_id"):
        load_template_profile("unknown_template")
