"""Deterministic rule-based resume type classifier v0."""

from collections import defaultdict

from resume_pdf_agent.classifier.features import (
    extract_experience_type_features,
    extract_profile_text_features,
    extract_resume_content_text_features,
    normalize_text,
)
from resume_pdf_agent.classifier.rules import (
    RECOMMENDED_SECTIONS,
    RESUME_TYPE_KEYWORDS,
    SOURCE_WEIGHTS,
)
from resume_pdf_agent.models import (
    ClassificationSignal,
    ResumeContent,
    ResumeType,
    ResumeTypeClassificationResult,
    ResumeTypeScore,
    RoleCriteriaProfile,
    UserProfile,
)

_MEANINGFUL_THRESHOLD = 4.0
_LOW_CONFIDENCE_THRESHOLD = 0.45


def _split_feature(feature: str) -> tuple[str, str]:
    if ":" not in feature:
        return "additional_text", feature
    source, text = feature.split(":", 1)
    return source, text


def _keyword_matches(text: str, keyword: str) -> bool:
    normalized_keyword = normalize_text(keyword)
    normalized_text = f" {normalize_text(text)} "
    if len(normalized_keyword) == 1:
        return f" {normalized_keyword} " in normalized_text
    return normalized_keyword in normalized_text


def _score_text_feature(feature: str) -> list[ClassificationSignal]:
    source, text = _split_feature(feature)
    weight = SOURCE_WEIGHTS.get(source, SOURCE_WEIGHTS["additional_text"])
    signals: list[ClassificationSignal] = []
    for resume_type, keywords in RESUME_TYPE_KEYWORDS.items():
        for keyword in keywords:
            if _keyword_matches(text, keyword):
                signals.append(
                    ClassificationSignal(
                        source=source,
                        matched_text=text,
                        resume_type=resume_type,
                        weight=weight,
                        reason=f"Matched keyword '{normalize_text(keyword)}' from {source}.",
                    )
                )
                break
    return signals


def _criteria_profile_signals(criteria_profiles: list[RoleCriteriaProfile] | None) -> list[ClassificationSignal]:
    signals: list[ClassificationSignal] = []
    if not criteria_profiles:
        return signals
    for profile in criteria_profiles:
        for index, resume_type in enumerate(profile.resume_types):
            signals.append(
                ClassificationSignal(
                    source="selected_criteria_profile",
                    matched_text=profile.role_title,
                    resume_type=resume_type,
                    weight=max(SOURCE_WEIGHTS["selected_criteria_profile"] - (0.5 * index), 0.0),
                    reason=f"Selected criteria profile '{profile.profile_id}' supports {resume_type.value}.",
                )
            )
    return signals


def _compute_confidence(ranked_types: list[ResumeTypeScore]) -> float:
    top = ranked_types[0]
    second_score = ranked_types[1].score if len(ranked_types) > 1 else 0.0
    if top.score <= 0:
        return 0.2

    separation = max(top.score - second_score, 0.0) / max(top.score, 1.0)
    signal_strength = min(top.score / 20.0, 1.0)
    signal_count = min(len(top.signals) / 4.0, 1.0)
    confidence = (0.20 * separation) + (0.50 * signal_strength) + (0.30 * signal_count)
    return round(max(0.0, min(confidence, 1.0)), 2)


def _build_ranked_scores(
    signals_by_type: dict[ResumeType, list[ClassificationSignal]],
    max_ranked_types: int,
) -> list[ResumeTypeScore]:
    scores = [
        ResumeTypeScore(
            resume_type=resume_type,
            score=round(sum(signal.weight for signal in signals), 2),
            signals=signals,
        )
        for resume_type, signals in signals_by_type.items()
    ]
    for resume_type in ResumeType:
        if resume_type not in signals_by_type:
            scores.append(ResumeTypeScore(resume_type=resume_type, score=0.0, signals=[]))
    scores.sort(key=lambda item: (-item.score, item.resume_type.value))
    return scores[: max(1, max_ranked_types)]


def classify_resume_type(
    user_profile: UserProfile,
    resume_content: ResumeContent | None = None,
    criteria_profiles: list[RoleCriteriaProfile] | None = None,
    max_ranked_types: int = 3,
) -> ResumeTypeClassificationResult:
    """Classify the best-fit resume type using deterministic rules."""

    features = []
    features.extend(extract_profile_text_features(user_profile))
    features.extend(extract_resume_content_text_features(resume_content))
    features.extend(extract_experience_type_features(resume_content))

    signals_by_type: dict[ResumeType, list[ClassificationSignal]] = defaultdict(list)
    for feature in features:
        for signal in _score_text_feature(feature):
            signals_by_type[signal.resume_type].append(signal)
    for signal in _criteria_profile_signals(criteria_profiles):
        signals_by_type[signal.resume_type].append(signal)

    ranked_types = _build_ranked_scores(signals_by_type, max_ranked_types)
    top = ranked_types[0]
    warnings: list[str] = []

    if top.score < _MEANINGFUL_THRESHOLD:
        primary_resume_type = ResumeType.GENERAL_STUDENT_RESUME
        if ranked_types[0].resume_type != ResumeType.GENERAL_STUDENT_RESUME:
            ranked_types = [
                ResumeTypeScore(
                    resume_type=ResumeType.GENERAL_STUDENT_RESUME,
                    score=top.score,
                    signals=signals_by_type.get(ResumeType.GENERAL_STUDENT_RESUME, []),
                ),
                *[item for item in ranked_types if item.resume_type != ResumeType.GENERAL_STUDENT_RESUME],
            ][: max(1, max_ranked_types)]
        warnings.append("No strong resume type signal was found; using general_student_resume fallback.")
    else:
        primary_resume_type = top.resume_type

    confidence = _compute_confidence(ranked_types)

    if not user_profile.target_roles:
        warnings.append("target_roles is empty; classification may be less specific.")
    if resume_content is None:
        warnings.append("resume_content is missing; classification uses profile and criteria signals only.")
    if top.score < _MEANINGFUL_THRESHOLD:
        warnings.append("no strong signal was found.")
    if confidence < _LOW_CONFIDENCE_THRESHOLD:
        warnings.append("classification is low-confidence.")

    explanation = (
        f"Rule-based v0 classifier selected {primary_resume_type.value} from "
        f"{len(features)} text features and "
        f"{len(criteria_profiles or [])} selected criteria profile(s). "
        "This is a resume formatting and positioning signal, not an interview or offer prediction."
    )

    return ResumeTypeClassificationResult(
        primary_resume_type=primary_resume_type,
        ranked_types=ranked_types,
        confidence=confidence,
        recommended_sections=RECOMMENDED_SECTIONS[primary_resume_type],
        explanation=explanation,
        warnings=warnings,
    )
