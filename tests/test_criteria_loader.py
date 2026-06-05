import pytest

from resume_pdf_agent.criteria import (
    get_available_profile_ids,
    load_all_criteria_profiles,
    load_criteria_profile,
)
from resume_pdf_agent.models import RoleCriteriaProfile

PRIVATE_CLAIM_PHRASES = [
    "internal company screening standard",
    "internal company screening algorithm",
    "confidential hiring criteria",
    "private hiring algorithm",
]

FAKE_URL_MARKERS = ["example.com", "fake", "placeholder"]


def _criterion_text(criterion) -> str:
    source = criterion.source
    return " ".join(
        [
            criterion.criterion_id,
            criterion.name,
            criterion.description,
            " ".join(criterion.evidence_required),
            " ".join(criterion.keywords),
            " ".join(criterion.positive_signals),
            " ".join(criterion.negative_signals),
            source.title or "",
            source.organization or "",
            source.url or "",
            source.notes or "",
        ]
    ).lower()


def test_load_criteria_profile_loads_each_profile_successfully():
    for profile_id in get_available_profile_ids():
        profile = load_criteria_profile(profile_id)
        assert isinstance(profile, RoleCriteriaProfile)
        assert profile.profile_id == profile_id


def test_load_all_criteria_profiles_returns_six_valid_profiles():
    profiles = load_all_criteria_profiles()

    assert len(profiles) == 6
    assert all(isinstance(profile, RoleCriteriaProfile) for profile in profiles)


def test_unknown_profile_id_raises_clear_error():
    with pytest.raises(ValueError, match="Unknown criteria profile_id"):
        load_criteria_profile("unknown_profile")


def test_every_profile_has_at_least_8_criteria():
    for profile in load_all_criteria_profiles():
        assert len(profile.criteria) >= 8


def test_every_criterion_has_valid_ranges_and_required_lists():
    for profile in load_all_criteria_profiles():
        for criterion in profile.criteria:
            assert 1 <= criterion.importance <= 5
            assert 0.0 <= criterion.confidence <= 1.0
            assert criterion.criterion_id.strip()
            assert criterion.name.strip()
            assert criterion.description.strip()
            assert criterion.evidence_required
            assert criterion.keywords


def test_no_criterion_claims_private_screening_access():
    for profile in load_all_criteria_profiles():
        profile_text = f"{profile.role_title} {profile.notes or ''}".lower()
        for phrase in PRIVATE_CLAIM_PHRASES:
            assert phrase not in profile_text
        for criterion in profile.criteria:
            text = _criterion_text(criterion)
            for phrase in PRIVATE_CLAIM_PHRASES:
                assert phrase not in text


def test_no_criterion_uses_fake_urls():
    for profile in load_all_criteria_profiles():
        for criterion in profile.criteria:
            url = criterion.source.url
            if url is None:
                continue
            assert url.startswith(("https://", "http://"))
            lowered_url = url.lower()
            for marker in FAKE_URL_MARKERS:
                assert marker not in lowered_url
