"""Criteria-based gap analysis engine v0."""

from resume_pdf_agent.gap_analysis.analyzer import analyze_criteria_gap
from resume_pdf_agent.gap_analysis.evidence import extract_candidate_evidence
from resume_pdf_agent.gap_analysis.matcher import match_criterion_against_evidence

__all__ = [
    "analyze_criteria_gap",
    "extract_candidate_evidence",
    "match_criterion_against_evidence",
]
