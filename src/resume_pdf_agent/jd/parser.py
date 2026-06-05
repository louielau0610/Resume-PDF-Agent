"""Deterministic user-provided JD parser for M15.

Parses JD text into structured fields without LLM/NLP libraries.
"""

from __future__ import annotations

import re
import uuid

from resume_pdf_agent.jd.compliance import check_jd_compliance
from resume_pdf_agent.models.jd import (
    JDComplianceStatus,
    JDSourceType,
    ParsedJD,
)

# ── Known skill/tool keywords ────────────────────────────────────────────
_KNOWN_SKILLS: set[str] = {
    "python", "r", "sql", "excel", "tableau", "power bi", "powerbi",
    "java", "c++", "c#", "javascript", "typescript", "react", "node.js",
    "nodejs", "git", "docker", "aws", "azure", "gcp",
    "machine learning", "deep learning", "statistics", "data analysis",
    "data visualization", "data cleaning", "model evaluation",
    "financial modeling", "valuation", "market research",
    "product management", "user research", "prd", "competitor analysis",
    "literature review", "pandas", "numpy", "scikit-learn", "sklearn",
    "matplotlib", "seaborn", "pytorch", "tensorflow", "keras",
    "spark", "hadoop", "kafka", "redis", "mongodb", "postgresql",
    "mysql", "linux", "bash", "agile", "scrum", "jira", "confluence",
    "figma", "sketch", "adobe", "photoshop",
}

# ── Heading patterns for section detection ──────────────────────────────
_HEADING_PATTERNS: dict[str, list[str]] = {
    "responsibilities": [
        "responsibilities", "what you will do", "what you'll do",
        "about the role", "role description", "job description",
        "key responsibilities", "duties", "the role",
        "what you'll be doing",
    ],
    "required_qualifications": [
        "requirements", "basic qualifications", "minimum qualifications",
        "qualifications", "what you need", "required qualifications",
        "required skills", "must have", "what we're looking for",
        "who you are",
    ],
    "preferred_qualifications": [
        "preferred qualifications", "nice to have", "bonus points",
        "preferred skills", "desired qualifications", "good to have",
        "bonus qualifications",
    ],
    "education": [
        "education", "educational requirements", "degree",
    ],
}

# ── Seniority inference from role title ─────────────────────────────────
_SENIORITY_PATTERNS: list[tuple[str, str]] = [
    ("intern", "intern"),
    ("entry level", "entry_level"),
    ("entry-level", "entry_level"),
    ("junior", "junior"),
    ("jr.", "junior"),
    ("senior", "senior"),
    ("sr.", "senior"),
    ("lead", "senior"),
    ("principal", "senior"),
    ("staff", "senior"),
    ("manager", "mid"),
    ("mid", "mid"),
    ("mid-level", "mid"),
    ("director", "senior"),
    ("head of", "senior"),
    ("vp", "senior"),
]


def normalize_jd_text(value: str) -> str:
    """Normalize raw JD text: collapse whitespace, strip, normalize line endings."""
    value = value.replace("\r\n", "\n").replace("\r", "\n")
    # Collapse multiple blank lines
    value = re.sub(r"\n{3,}", "\n\n", value)
    # Strip leading/trailing whitespace
    value = value.strip()
    return value


def _extract_first_line_role_title(text: str) -> str | None:
    """Heuristic: first non-empty line might be role title."""
    lines = [l.strip() for l in text.split("\n") if l.strip()]
    if not lines:
        return None
    first = lines[0]
    # Skip if too long (probably not a title)
    if len(first) > 120:
        return None
    # Skip if looks like a section heading
    if first.lower().startswith(("about", "job", "position", "company")):
        return None
    return first


def _extract_metadata_field(text: str, field_label: str) -> str | None:
    """Extract a labeled metadata field from text."""
    pattern = rf"^{field_label}\s*[:：]\s*(.+)$"
    for line in text.split("\n"):
        m = re.match(pattern, line.strip(), re.IGNORECASE)
        if m:
            return m.group(1).strip()
    return None


def _extract_section_items(text: str, section_key: str) -> list[str]:
    """Extract bullet/list items under a recognized heading."""
    patterns = _HEADING_PATTERNS.get(section_key, [])
    if not patterns:
        return []

    lines = text.split("\n")
    in_section = False
    items: list[str] = []

    for line in lines:
        stripped = line.strip().lower()
        # Remove leading bullet markers for heading detection
        clean = re.sub(r"^[-•*#>\s]+", "", stripped).strip()

        # Check if this line is a heading
        is_heading = any(
            clean == pat or clean.startswith(pat)
            for pat in patterns
        )

        if is_heading:
            in_section = True
            continue

        # Check if we've moved to another section
        if in_section and clean and (
            clean.endswith(":") or clean.endswith("：")
        ):
            # Could be a sub-heading; check if it matches another section
            other_section = False
            for other_key, other_pats in _HEADING_PATTERNS.items():
                if other_key == section_key:
                    continue
                for op in other_pats:
                    if clean == op or clean.startswith(op):
                        other_section = True
                        break
                if other_section:
                    break
            if other_section:
                in_section = False
                continue

        if in_section:
            # Extract bullet content
            bullet_match = re.match(r"^[-•*>]\s*(.+)", line.strip())
            if bullet_match:
                item_text = bullet_match.group(1).strip()
                if item_text and len(item_text) > 3:
                    items.append(item_text)
            elif stripped and not stripped.endswith((":", "：")):
                # Non-bullet line that looks like a plain sentence
                if len(stripped) > 20:
                    items.append(line.strip())

    return items


def _extract_skills_from_text(text: str) -> list[str]:
    """Extract known skill/tool keywords from text."""
    text_lower = text.lower()
    found: set[str] = set()
    for skill in _KNOWN_SKILLS:
        # Use word boundary for short skills
        if len(skill) <= 3:
            pattern = re.compile(rf"\b{re.escape(skill)}\b", re.IGNORECASE)
        else:
            pattern = re.compile(re.escape(skill), re.IGNORECASE)
        if pattern.search(text_lower):
            found.add(skill)
    return sorted(found)


def _infer_seniority(text: str) -> str:
    """Infer seniority level from role title and text."""
    text_lower = text.lower()
    for pattern, level in _SENIORITY_PATTERNS:
        if pattern in text_lower:
            return level
    return "unknown"


def parse_user_provided_jd(
    jd_text: str,
    source_type: JDSourceType = JDSourceType.USER_PROVIDED_TEXT,
) -> ParsedJD:
    """Parse user-provided JD text into a structured ParsedJD.

    Runs compliance check first. If blocked, returns minimal ParsedJD
    with empty extracted fields.

    Parameters
    ----------
    jd_text : str
        Raw JD text.
    source_type : JDSourceType
        How the JD was provided.

    Returns
    -------
    ParsedJD
        Structured parsed result.
    """
    jd_id = f"jd_{uuid.uuid4().hex[:8]}"
    normalized = normalize_jd_text(jd_text)

    # Run compliance first
    compliance = check_jd_compliance(jd_text, source_type=source_type)

    # ── If blocked, return minimal result ────────────────────────────
    if compliance.status == JDComplianceStatus.BLOCKED:
        return ParsedJD(
            jd_id=jd_id,
            source_type=source_type,
            raw_text=jd_text,
            normalized_text=normalized,
            compliance_result=compliance,
            warnings=["JD parsing blocked due to compliance issues."],
        )

    # ── Safe to parse ────────────────────────────────────────────────
    sections_found: list[str] = []

    # Role title
    role_title = _extract_first_line_role_title(normalized)

    # Metadata fields
    company_name = _extract_metadata_field(normalized, "Company") or _extract_metadata_field(normalized, "Organization")
    location = _extract_metadata_field(normalized, "Location")
    employment_type = _extract_metadata_field(normalized, "Employment Type") or _extract_metadata_field(normalized, "Job Type")

    # Seniority
    seniority = _infer_seniority(normalized)

    # Sections
    responsibilities = _extract_section_items(normalized, "responsibilities")
    if responsibilities:
        sections_found.append("responsibilities")

    required_qualifications = _extract_section_items(normalized, "required_qualifications")
    if required_qualifications:
        sections_found.append("required_qualifications")

    preferred_qualifications = _extract_section_items(normalized, "preferred_qualifications")
    if preferred_qualifications:
        sections_found.append("preferred_qualifications")

    education_requirements = _extract_section_items(normalized, "education")
    if education_requirements:
        sections_found.append("education")

    # Skills/tools from known keywords
    skills = _extract_skills_from_text(normalized)
    if skills:
        sections_found.append("skills")

    # Keywords = all skills + extracted terms
    keywords = list(skills)

    parser_warnings: list[str] = list(compliance.warnings)
    if not sections_found:
        parser_warnings.append(
            "No standard JD sections detected. The text may not be a proper job description."
        )

    return ParsedJD(
        jd_id=jd_id,
        source_type=source_type,
        raw_text=jd_text,
        normalized_text=normalized,
        role_title=role_title,
        company_name=company_name,
        location=location,
        employment_type=employment_type,
        seniority_level=seniority,
        responsibilities=responsibilities,
        required_qualifications=required_qualifications,
        preferred_qualifications=preferred_qualifications,
        skills=skills,
        tools=skills,  # skills and tools overlap in simple extraction
        education_requirements=education_requirements,
        keywords=keywords,
        sections_found=sections_found,
        compliance_result=compliance,
        warnings=parser_warnings,
    )
