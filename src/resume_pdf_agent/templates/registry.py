"""Registry utilities for internal template metadata profiles."""

import json
from pathlib import Path

from resume_pdf_agent.models import InternalTemplateProfile

TEMPLATE_FILE_MAP: dict[str, str] = {
    "ats_student_basic": "ats_student_basic.json",
    "data_science_technical": "data_science_technical.json",
    "software_engineering_technical": "software_engineering_technical.json",
    "finance_business": "finance_business.json",
    "consulting_business": "consulting_business.json",
    "research_cv": "research_cv.json",
    "product_manager": "product_manager.json",
    "design_portfolio_light": "design_portfolio_light.json",
}

_TEMPLATE_DATA_DIR = Path(__file__).resolve().parents[3] / "data" / "template_profiles"


def get_available_template_ids() -> list[str]:
    """Return stable internal template IDs."""

    return list(TEMPLATE_FILE_MAP.keys())


def get_template_file_map() -> dict[str, str]:
    """Return a copy of the template ID to filename mapping."""

    return dict(TEMPLATE_FILE_MAP)


def load_template_profile(template_id: str) -> InternalTemplateProfile:
    """Load and validate one internal template metadata profile."""

    if template_id not in TEMPLATE_FILE_MAP:
        available = ", ".join(TEMPLATE_FILE_MAP)
        raise ValueError(f"Unknown template_id '{template_id}'. Available templates: {available}")
    path = _TEMPLATE_DATA_DIR / TEMPLATE_FILE_MAP[template_id]
    with path.open("r", encoding="utf-8") as file:
        data = json.load(file)
    return InternalTemplateProfile.model_validate(data)


def load_all_template_profiles() -> list[InternalTemplateProfile]:
    """Load all internal template metadata profiles in deterministic order."""

    return [load_template_profile(template_id) for template_id in TEMPLATE_FILE_MAP]
