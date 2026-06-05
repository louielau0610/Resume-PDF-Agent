"""Deterministic claim extraction from structured resume content."""

import re

from resume_pdf_agent.models import ResumeClaim, ResumeContent


def normalize_claim_text(value: str) -> str:
    """Normalize claim text for deterministic rule checks."""

    cleaned = re.sub(r"[^a-z0-9+#.%/-]+", " ", value.lower())
    return " ".join(cleaned.split())


def _claim(
    claim_id: str,
    source_type: str,
    text: str | None,
    source_id: str | None = None,
    related_experience_id: str | None = None,
    **metadata,
) -> ResumeClaim | None:
    if not text or not text.strip():
        return None
    return ResumeClaim(
        claim_id=claim_id,
        source_type=source_type,
        source_id=source_id,
        text=text,
        normalized_text=normalize_claim_text(text),
        related_experience_id=related_experience_id,
        **metadata,
    )


def _append(claims: list[ResumeClaim], claim: ResumeClaim | None) -> None:
    if claim is not None:
        claims.append(claim)


def extract_resume_claims(resume_content: ResumeContent) -> list[ResumeClaim]:
    """Extract resume claims from summary, experiences, metrics, and bullets."""

    claims: list[ResumeClaim] = []
    _append(claims, _claim("summary:0", "summary", resume_content.summary))

    for exp_index, experience in enumerate(resume_content.experiences):
        exp_id = experience.experience_id
        _append(claims, _claim(f"experience:{exp_id}:raw_description", "raw_description", experience.raw_description, exp_id, exp_id))
        for index, responsibility in enumerate(experience.responsibilities):
            _append(claims, _claim(f"experience:{exp_id}:responsibility:{index}", "responsibility", responsibility, exp_id, exp_id))
        for index, tool in enumerate(experience.tools_used):
            _append(claims, _claim(f"experience:{exp_id}:tool:{index}", "tool", tool, exp_id, exp_id))
        for index, method in enumerate(experience.methods_used):
            _append(claims, _claim(f"experience:{exp_id}:method:{index}", "method", method, exp_id, exp_id))
        for index, outcome in enumerate(experience.outcomes):
            _append(claims, _claim(f"experience:{exp_id}:outcome:{index}", "outcome", outcome, exp_id, exp_id))
        for index, metric in enumerate(experience.metrics):
            metric_text = " ".join(
                part
                for part in [metric.name, metric.value, metric.unit, metric.context, metric.source_note]
                if part
            )
            _append(claims, _claim(f"experience:{exp_id}:metric:{index}", "metric", metric_text, exp_id, exp_id))
        for index, note in enumerate(experience.evidence_notes):
            _append(claims, _claim(f"experience:{exp_id}:evidence_note:{index}", "evidence_note", note, exp_id, exp_id))

    for section_index, section in enumerate(resume_content.sections):
        for bullet_index, bullet in enumerate(section.bullets):
            claim_id = f"section:{section_index}:bullet:{bullet_index}"
            _append(
                claims,
                _claim(
                    claim_id,
                    "resume_bullet",
                    bullet.text,
                    bullet.source_experience_id,
                    bullet.source_experience_id,
                    evidence_level=bullet.evidence_level,
                    metric_status=bullet.metric_status,
                    needs_confirmation=bullet.needs_confirmation,
                    risk_flags=bullet.risk_flags,
                    targeted_criteria_ids=bullet.targeted_criteria_ids,
                ),
            )
            for flag_index, risk_flag in enumerate(bullet.risk_flags):
                _append(
                    claims,
                    _claim(
                        f"{claim_id}:risk_flag:{flag_index}",
                        "risk_flag",
                        risk_flag,
                        bullet.source_experience_id,
                        bullet.source_experience_id,
                        evidence_level=bullet.evidence_level,
                        metric_status=bullet.metric_status,
                        needs_confirmation=bullet.needs_confirmation,
                        risk_flags=[risk_flag],
                        targeted_criteria_ids=bullet.targeted_criteria_ids,
                    ),
                )

    return claims
