"""Safety helpers for deterministic HTML rendering."""

from html import escape

from resume_pdf_agent.models import RenderSection

HIGH_RISK_TOKENS = {
    "unsupported",
    "fabricated",
    "truthfulness_risk",
    "high_risk",
    "unsupported_metric",
}


def escape_html_text(value: str) -> str:
    """Escape user-provided text for insertion into HTML."""

    return escape(value, quote=True)


def is_safe_render_item(
    needs_confirmation: bool,
    risk_flags: list[str],
    include_confirmation_needed: bool = True,
) -> bool:
    """Return whether an item is safe enough to use as rendered resume content."""

    normalized_flags = {flag.strip().lower() for flag in risk_flags}
    has_high_risk_flag = bool(normalized_flags.intersection(HIGH_RISK_TOKENS))
    if has_high_risk_flag:
        return False
    if needs_confirmation and not include_confirmation_needed:
        return False
    return True


def collect_render_warnings_from_bullets(
    sections: list[RenderSection],
) -> list[str]:
    """Collect deterministic warnings from section item safety metadata."""

    warnings: list[str] = []
    for section in sections:
        for item in section.items:
            if item.needs_confirmation:
                warnings.append(
                    f"Section '{section.section_id}' includes an item that needs user confirmation."
                )
            if item.risk_flags:
                flags = ", ".join(sorted(set(item.risk_flags)))
                warnings.append(
                    f"Section '{section.section_id}' includes an item with risk flags: {flags}."
                )
    return warnings
