"""Load static criteria profiles from local JSON files."""

import json
from pathlib import Path

from resume_pdf_agent.criteria.knowledge_base import get_profile_file_map
from resume_pdf_agent.models import RoleCriteriaProfile

_CRITERIA_DATA_DIR = Path(__file__).resolve().parents[3] / "data" / "criteria_profiles"


def load_criteria_profile(profile_id: str) -> RoleCriteriaProfile:
    """Load and validate one static criteria profile by ID."""

    profile_file_map = get_profile_file_map()
    if profile_id not in profile_file_map:
        available = ", ".join(profile_file_map)
        raise ValueError(f"Unknown criteria profile_id '{profile_id}'. Available profiles: {available}")

    profile_path = _CRITERIA_DATA_DIR / profile_file_map[profile_id]
    with profile_path.open("r", encoding="utf-8") as file:
        profile_data = json.load(file)

    return RoleCriteriaProfile.model_validate(profile_data)


def load_all_criteria_profiles() -> list[RoleCriteriaProfile]:
    """Load and validate all static criteria profiles."""

    return [load_criteria_profile(profile_id) for profile_id in get_profile_file_map()]
