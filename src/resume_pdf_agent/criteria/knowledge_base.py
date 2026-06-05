"""Constants for the static criteria knowledge base v0."""

PROFILE_FILE_MAP: dict[str, str] = {
    "data_science_intern": "data_science_intern.json",
    "software_engineering_intern": "software_engineering_intern.json",
    "product_manager_intern": "product_manager_intern.json",
    "finance_intern": "finance_intern.json",
    "consulting_intern": "consulting_intern.json",
    "research_assistant": "research_assistant.json",
}


def get_available_profile_ids() -> list[str]:
    """Return stable criteria profile IDs available in v0."""

    return list(PROFILE_FILE_MAP.keys())


def get_profile_file_map() -> dict[str, str]:
    """Return a copy of the profile ID to JSON filename mapping."""

    return dict(PROFILE_FILE_MAP)
