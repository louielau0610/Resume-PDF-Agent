"""Deterministic internal template selector."""

from resume_pdf_agent.models import (
    BulletEnhancementResult,
    GapAnalysisResult,
    ResumeContent,
    ResumeTypeClassificationResult,
    RoleCriteriaProfile,
    TemplateMatchReason,
    TemplateScore,
    TemplateSelectionResult,
    UserProfile,
)
from resume_pdf_agent.templates.constraints import (
    estimate_resume_density,
    has_portfolio_signals,
    has_project_heavy_signals,
    has_research_signals,
    recommended_sections_for_template,
)
from resume_pdf_agent.templates.registry import load_all_template_profiles, load_template_profile


def _add_reason(reasons: list[TemplateMatchReason], reason_type: str, message: str, weight: float) -> None:
    if weight > 0:
        reasons.append(TemplateMatchReason(reason_type=reason_type, message=message, weight=weight))


def select_internal_template(
    user_profile: UserProfile | None = None,
    resume_content: ResumeContent | None = None,
    classification_result: ResumeTypeClassificationResult | None = None,
    criteria_profile: RoleCriteriaProfile | None = None,
    gap_analysis_result: GapAnalysisResult | None = None,
    bullet_enhancement_result: BulletEnhancementResult | None = None,
    max_ranked_templates: int = 3,
) -> TemplateSelectionResult:
    """Select internal template metadata without rendering HTML or PDF."""

    templates = load_all_template_profiles()
    portfolio = has_portfolio_signals(user_profile, resume_content)
    research = has_research_signals(resume_content, criteria_profile)
    project_heavy = has_project_heavy_signals(resume_content)
    density = estimate_resume_density(resume_content, bullet_enhancement_result)
    scores: list[TemplateScore] = []

    for template in templates:
        reasons: list[TemplateMatchReason] = []
        if classification_result and classification_result.primary_resume_type in template.supported_resume_types:
            _add_reason(reasons, "primary_resume_type", "Template supports classified primary resume type.", 8.0)
        if criteria_profile:
            matches = set(criteria_profile.resume_types).intersection(template.supported_resume_types)
            _add_reason(reasons, "criteria_resume_type", "Template supports criteria profile resume type.", 5.0 if matches else 0.0)
        if resume_content and resume_content.resume_type in template.supported_resume_types:
            _add_reason(reasons, "content_resume_type", "Template supports resume_content resume_type.", 5.0)
        if user_profile:
            text = " ".join(user_profile.target_roles + user_profile.target_industries).lower()
            if any(role.lower() in text for role in template.recommended_roles + template.recommended_industries):
                _add_reason(reasons, "profile_text", "Template role or industry metadata matches user profile.", 3.0)
        if template.ats_friendly:
            _add_reason(reasons, "ats_friendly", "ATS-friendly metadata bonus.", 1.0)
        if template.supports_one_page_layout:
            _add_reason(reasons, "one_page", "One-page layout support bonus.", 0.75)
        if portfolio and template.supports_portfolio_link:
            _add_reason(reasons, "portfolio", "Portfolio evidence matches template capability.", 6.0)
        if not portfolio and template.template_id == "design_portfolio_light":
            _add_reason(reasons, "portfolio_missing_penalty_offset", "No portfolio evidence for design template.", 0.0)
        if research and template.supports_research_outputs:
            _add_reason(reasons, "research", "Research signals match template capability.", 6.0)
        if project_heavy and template.supports_project_heavy_layout:
            _add_reason(reasons, "project_heavy", "Project-heavy content matches template capability.", 2.0)
        if template.density == density:
            _add_reason(reasons, "density", "Estimated content density matches template density.", 1.0)
        if bullet_enhancement_result and bullet_enhancement_result.truthfulness_blockers:
            _add_reason(reasons, "truthfulness_blockers", "Conservative ATS-friendly template preferred when blockers exist.", 1.0 if template.ats_friendly else 0.0)

        score = sum(reason.weight for reason in reasons)
        if template.template_id == "design_portfolio_light" and not portfolio:
            score = 0.0
        if template.template_id == "research_cv" and not research:
            score = max(0.0, score - 2.0)
        scores.append(TemplateScore(template_id=template.template_id, score=round(score, 2), reasons=reasons))

    scores.sort(key=lambda item: (-item.score, item.template_id))
    if not scores or scores[0].score <= 1.75:
        selected = load_template_profile("ats_student_basic")
        selected_score = next((score for score in scores if score.template_id == selected.template_id), None)
        if selected_score:
            scores = [selected_score] + [score for score in scores if score.template_id != selected.template_id]
    else:
        selected = load_template_profile(scores[0].template_id)

    ranked = scores[: max(1, max_ranked_templates)]
    if selected.template_id not in {score.template_id for score in ranked}:
        selected_score = next(score for score in scores if score.template_id == selected.template_id)
        ranked = [selected_score] + ranked[:-1]

    warnings: list[str] = []
    if classification_result is None:
        warnings.append("No classification_result provided; template selection used fallback signals.")
    if resume_content is None:
        warnings.append("No resume_content provided; template selection may be less specific.")
    if selected.supports_portfolio_link and not portfolio:
        warnings.append("Portfolio-capable template selected without portfolio evidence.")
    if selected.supports_research_outputs and not research:
        warnings.append("Research template selected without clear research evidence.")
    if bullet_enhancement_result and bullet_enhancement_result.truthfulness_blockers:
        warnings.append("Bullet enhancement has truthfulness blockers; rendering should remain conservative.")
    if selected.visual_complexity >= 4:
        warnings.append("Selected template has higher visual complexity; verify ATS readability later.")

    return TemplateSelectionResult(
        selected_template_id=selected.template_id,
        selected_template=selected,
        ranked_templates=ranked,
        recommended_sections=recommended_sections_for_template(selected, resume_content),
        warnings=warnings,
        summary=f"Selected internal template metadata '{selected.template_id}' for later rendering. No HTML or PDF was generated.",
    )
