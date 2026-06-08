# resume_pdf_agent

## M28 Manual Patch Approval Checklist

M28 adds a manual approval checklist that generates `llm_rewrite_manual_patch_approval_checklist.json`, `.md`, and `.html` from M27 manual patch previews. Each `review_required` candidate includes 8 checklist questions (truthfulness evidence, target mapping, original text match, text quality, unsupported claim risk, confirmation gate, formatting consistency, human final decision), with all defaults set to `not_reviewed`. This is checklist-only — no final approval is granted by the system, no candidates are applied, and no executable patch is generated.

## M27 Manual Patch Preview Without Resume Mutation

M27 adds a manual patch preview layer that generates `llm_rewrite_manual_patch_preview.json`, `.md`, and `.html` from M24 application plans and M26 validation reports. Each preview-ready candidate shows original text, proposed replacement, target section/item, and a display-only diff preview. This is preview-only: no executable patch is generated, no candidates are applied, `resume.html` and `resume.pdf` are not modified, and M5 truthfulness checks plus the M14 confirmation gate are not bypassed.

## M26 Strict Pre-Application Validation

M26 adds a strict pre-application validation layer that performs deterministic safety checks on M24 application plans. Running `validate-llm-pre-application` generates `llm_rewrite_pre_application_validation.json` and `.md`, clearly listing which candidates pass, are blocked, need manual edit, are excluded, or unmapped. This is validation-only: it does not apply any LLM candidates, does not generate patches, does not modify `resume.html` or `resume.pdf`, and does not bypass M5 truthfulness checks or the M14 confirmation gate.

## M25 LLM Candidate Application Preview UI

M25 adds a local static `llm_rewrite_application_preview.html` page rendered from the M24 `llm_rewrite_application_plan.json`. It lets users inspect planned, blocked, needs-manual-edit, excluded, and unmapped candidates. It is a manual preview only: it does not apply candidates, does not modify `resume.html` or `resume.pdf`, and does not bypass M5 truthfulness checks or the M14 confirmation gate.

## M24 LLM Candidate Application Planning

M24 adds a plan-only LLM candidate application planning layer. It reads `llm_rewrite_result.json`, `llm_rewrite_review_decisions.json`, and an optional M23 summary to generate `llm_rewrite_application_plan.json` / `.md`. This is audit guidance only: it does not apply candidates, does not modify `resume.html` or `resume.pdf`, and does not bypass M5 truthfulness checks or the M14 confirmation gate.

## M23 LLM Review Decision Summary

M23 adds local loading and deterministic summary generation for `llm_rewrite_review_decisions.json`. It can produce `llm_rewrite_review_decision_summary.json` and `.md` with approved/rejected/needs-edit/ignored/note counts, unknown candidate IDs, duplicate entries, and warnings. This is advisory only: it does not apply LLM candidates, does not mutate the final resume, and does not bypass M5 truthfulness checks or the M14 confirmation gate.

## M22.1 Safety Hardening

M22.1 hardens the browser LLM rewrite review UI by enabling Jinja2 template-level autoescaping for `llm_review.html`. LLM candidates remain advisory only: the review UI does not automatically apply candidates, does not call any real LLM API, and does not bypass M5 truthfulness checks or the M14 confirmation gate.

> Criteria-aware AI resume PDF generation agent with role-fit analysis, truthfulness checks, template matching, HTML rendering, and deterministic PDF workflow.

`resume_pdf_agent` is a **criteria-aware AI resume PDF generation agent**. It does not call LLM APIs. Instead, it runs a deterministic 11-stage pipeline that compares a user's career profile against role-specific screening criteria, producing an ATS-friendly structured PDF resume and a static workflow dashboard.

## Current Status: M28

M28 manual approval checklist is the current milestone. Full test suite: 1005 passed, 2 skipped.

**Completed Milestones**: M0→M1→M2→M3→M4→M5→M6→M7→M8→M9→M10→M11→M12→M13→M14→M15→M16→M17→M18→M19→M20→M20.1→M21→M21.1→M22→M22.1→M23→M24→M25→M26→M26.1→M27→M27.1→**M28** ✅

## Architecture Overview

```
User JSON Input
→ Criteria Selection (6 role profiles)
→ Resume Type Classification (8 types)
→ Gap Analysis
→ Truthfulness Check
→ Bullet Enhancement
→ Template Matching (8 templates)
→ HTML Rendering
→ PDF Generation (Mock/WeasyPrint/Playwright)
→ Frontend Dashboard (cinematic dark theme)
```

See [`docs/architecture_diagram_v0.md`](docs/architecture_diagram_v0.md) for full Mermaid architecture diagrams.

## Key Features

| Feature | Description |
|---------|-------------|
| 🎯 Criteria-Aware | Resume optimization guided by role-specific screening criteria |
| 🔍 Truthfulness-First | Built-in checker detects unsupported claims |
| 📊 Explainable | Every decision backed by JSON artifacts |
| 🔒 Fully Local | No LLM API calls, no network, no data upload |
| 🎨 Cinematic Dark Dashboard | Pure CSS static dashboard, zero external dependencies |
| 🧪 305+ Tests | Full test coverage, deterministic and reproducible |

## Quick Start

### Requirements

- Python 3.11+
- No GPU, no LLM API key, no network required

### Install

```bash
git clone https://github.com/louielau0610/Resume-PDF-Agent.git
cd Resume-PDF-Agent
pip install -e ".[dev]"
```

### Run Demo

**Windows:**

```bash
py -m compileall src tests
py -m pytest -q
py -m resume_pdf_agent run-sample --output-dir outputs/demo_run --pdf-backend mock --write-frontend-page
```

**macOS / Linux:**

```bash
python -m compileall src tests
pytest -q
python -m resume_pdf_agent run-sample --output-dir outputs/demo_run --pdf-backend mock --write-frontend-page
```

### View in Browser

```bash
# View HTML resume
# Open outputs/demo_run/resume.html

# View workflow dashboard
# Open outputs/demo_run/index.html
```

## CLI Commands

```bash
# Run with built-in sample data
py -m resume_pdf_agent run-sample --output-dir outputs/my_run --pdf-backend mock --write-frontend-page

# Run with custom JSON input
py -m resume_pdf_agent run --input path/to/input.json --output-dir outputs/my_run

# List available criteria profiles
py -m resume_pdf_agent list-criteria

# List available templates
py -m resume_pdf_agent list-templates
```

## Output Artifacts

After running the demo, `outputs/demo_run/` contains:

| Artifact | Description |
|----------|-------------|
| `criteria_profile.json` | Matched criteria profile |
| `classification.json` | Resume type classification |
| `gap_analysis.json` | Criteria gap analysis |
| `truthfulness.json` | Truthfulness check results |
| `enhancement.json` | Bullet enhancement candidates |
| `template_selection.json` | Template matching results |
| `workflow_result.json` | Complete workflow results |
| `resume.html` | ATS-friendly structured HTML resume |
| `resume.pdf` | PDF resume |
| `index.html` | Static workflow dashboard |

## Supported Criteria Profiles

- `data_science_intern`
- `software_engineering_intern`
- `product_manager_intern`
- `finance_intern`
- `consulting_intern`
- `research_assistant`

## Supported Templates

- `data_science_technical`
- `software_engineering_technical`
- `finance_business`
- `consulting_business`
- `research_cv`
- `product_manager`
- `design_portfolio_light`
- `ats_student_basic`

## Safety Boundaries

✅ **What we do:**
- Deterministic rule-based analysis (no LLM hallucination risk)
- Fully local execution (no data upload)
- Truthfulness checking (flags unsupported claims)
- Traceable decisions (JSON artifacts for every stage)

❌ **What we do NOT do:**
- Do NOT call LLM APIs (GPT-4, Claude, Gemini, etc.)
- Do NOT claim knowledge of any company's internal screening standards
- Do NOT predict hiring/interview/offer probability
- Do NOT export Word (.docx), JPG, or PNG
- Do NOT provide a web application (no FastAPI/Flask/React)
- Do NOT scrape or fetch data from the internet

## Known Limitations

- Static criteria knowledge base (6 role profiles)
- No real JD (Job Description) parsing
- No LLM-assisted rewriting
- Mock PDF backend for demos (WeasyPrint optional)
- PDF-only export format
- Static frontend dashboard (no browser-based workflow execution)
- No user confirmation workflow
- No visual regression tests

See [`docs/limitations_and_roadmap_v0.md`](docs/limitations_and_roadmap_v0.md) for details.

## Roadmap

| Milestone | Content | Status |
|-----------|---------|--------|
| M0-M13 | Foundation → Complete deterministic pipeline + docs/demo | ✅ Done |
| M14 | User confirmation workflow | 🔜 Planned |
| M15 | Real JD parser | 🔜 Planned |
| M16 | Optional LLM-assisted rewriting | 🔜 Planned |
| M17 | Production PDF backend guide | 🔜 Planned |
| M18 | Visual regression testing | 🔜 Planned |
| M19 | Optional web app/API layer | 🔜 Planned |

## Tests

```bash
# Windows
py -m compileall src tests scripts
py -m pytest -q

# macOS / Linux
python -m compileall src tests scripts
pytest -q
```

## Project Structure

```
resume_pdf_agent/
├── src/resume_pdf_agent/   # Core source code
│   ├── models/             # Pydantic data models (M1)
│   ├── criteria/           # Criteria knowledge base (M2)
│   ├── classifier/         # Resume type classification (M3)
│   ├── gap_analysis/       # Gap analysis (M4)
│   ├── truthfulness/       # Truthfulness checking (M5)
│   ├── enhancement/        # Bullet enhancement (M6)
│   ├── templates/          # Template matching (M7)
│   ├── rendering/          # HTML rendering (M8)
│   ├── pdf/                # PDF generation (M9)
│   ├── workflow/           # Workflow orchestration (M10)
│   └── frontend/           # Frontend dashboard (M11/M12)
├── data/                   # Sample inputs and profile data
├── docs/                   # Documentation (M13)
├── examples/               # Example descriptions (M13)
├── scripts/                # Demo and validation scripts (M13)
└── tests/                  # Tests
```

## Documentation Index

- [`docs/demo_walkthrough_v0.md`](docs/demo_walkthrough_v0.md) — Demo walkthrough
- [`docs/architecture_diagram_v0.md`](docs/architecture_diagram_v0.md) — Architecture diagrams
- [`docs/github_project_overview_v0.md`](docs/github_project_overview_v0.md) — Project overview
- [`docs/limitations_and_roadmap_v0.md`](docs/limitations_and_roadmap_v0.md) — Limitations & roadmap
- [`docs/release_checklist_v0.md`](docs/release_checklist_v0.md) — Release checklist
- [`PROJECT_STATUS.md`](PROJECT_STATUS.md) — Project status
- [`TODO.md`](TODO.md) — TODOs & roadmap

## License

MIT
