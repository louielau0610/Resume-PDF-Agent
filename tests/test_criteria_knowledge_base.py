from pathlib import Path

from resume_pdf_agent.criteria import get_available_profile_ids, get_profile_file_map

EXPECTED_PROFILE_IDS = {
    "data_science_intern",
    "software_engineering_intern",
    "product_manager_intern",
    "finance_intern",
    "consulting_intern",
    "research_assistant",
}


def test_all_six_criteria_profile_json_files_exist():
    data_dir = Path(__file__).resolve().parents[1] / "data" / "criteria_profiles"

    for filename in get_profile_file_map().values():
        assert (data_dir / filename).exists()


def test_get_available_profile_ids_returns_expected_profiles():
    assert set(get_available_profile_ids()) == EXPECTED_PROFILE_IDS
    assert len(get_available_profile_ids()) == 6


def test_get_profile_file_map_returns_expected_mapping():
    file_map = get_profile_file_map()

    assert set(file_map) == EXPECTED_PROFILE_IDS
    assert file_map["data_science_intern"] == "data_science_intern.json"
