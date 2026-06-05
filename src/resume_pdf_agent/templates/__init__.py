"""Internal template registry and selector."""

from resume_pdf_agent.templates.registry import (
    get_available_template_ids,
    load_all_template_profiles,
    load_template_profile,
)
from resume_pdf_agent.templates.selector import select_internal_template

__all__ = [
    "get_available_template_ids",
    "load_all_template_profiles",
    "load_template_profile",
    "select_internal_template",
]
