# resume_pdf_agent

`resume_pdf_agent` is a criteria-aware AI resume PDF generation agent. It helps students, internship applicants, and early-career candidates turn career profiles, public job requirements, official hiring guidance, user-provided JD text, and manually curated role criteria into truthful, ATS-friendly PDF resume content.

This is not a general resume beautification chatbot. The project is designed as a controlled workflow that diagnoses and optimizes resumes against public, explainable, role-specific screening criteria. It does not claim to know any company's internal resume screening algorithm.

## Product Constraints

- Version 0 does not search the web for resume templates.
- Version 0 exports PDF only.
- Word, JPG, and PNG export are out of scope; users may use external AI tools or PDF conversion tools if needed.
- The project must not fabricate achievements, unsupported metrics, or company-specific internal criteria.
- Later criteria sources should be public job descriptions, official career pages, official hiring guides, university career guidance, user-provided JD text, and manually curated criteria.
- Frontend UI polish is out of scope for now and will be handled later based on user-provided sample images.

## Long-Term Pipeline

1. User Intake
2. Criteria Retrieval / Selection
3. Criteria Extraction / Normalization
4. Candidate Profile Structuring
5. Gap Analysis
6. Truthfulness Check
7. Criteria-aware Bullet Enhancement
8. Resume Type Classification
9. Internal Template Matching
10. HTML Rendering
11. PDF Generation
12. Reminder Panel

## Current Milestone: M4

M4 adds Criteria-based Gap Analysis Engine v0: a deterministic, rule-based diagnostic module. It compares `UserProfile`, optional `ResumeContent`, and one M2 `RoleCriteriaProfile`, then returns criteria-level match results, strengths, weaknesses, missing keywords, diagnostic suggested actions, and basic truthfulness warnings.

M4 helps answer:

- Which criteria are strongly supported by user evidence
- Which criteria are partial, weak, or missing
- Which important keywords are missing
- Which claims have unsupported evidence, unsupported metrics, confirmation needs, or risk flags
- What real evidence the user should add before future resume generation

Gap analysis does not rewrite resume bullets, predict hiring success, or represent internal company screening rules.

M4 does not implement LLM calls, real job description analysis, resume rewriting, full truthfulness checker logic, template matching, HTML rendering, PDF generation, frontend UI, or external export formats.

## Local Development

Python 3.11 or later is recommended.

Windows:

```bash
py -m venv .venv
.venv\Scripts\activate
py -m pip install -e ".[dev]"
```

If `python` is unavailable on Windows, use `py -m ...`.

macOS or Linux:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[dev]"
```

## Validation

Windows:

```bash
py -m compileall src tests
py -m pytest -q
```

macOS or Linux:

```bash
python -m compileall src tests
pytest -q
```
