# resume_pdf_agent

> Criteria-aware AI resume PDF generation agent with role-fit analysis, truthfulness checks, template matching, HTML rendering, and deterministic PDF workflow.

`resume_pdf_agent` is a **criteria-aware AI resume PDF generation agent**. It does not call LLM APIs. Instead, it runs a deterministic 11-stage pipeline that compares a user's career profile against role-specific screening criteria, producing an ATS-friendly structured PDF resume and a static workflow dashboard.

## Current Status: M13

M13 completes GitHub/demo packaging & release readiness, including full documentation, architecture diagrams, demo scripts, and a release checklist.

**Completed Milestones**: M0 → M1 → M2 → M3 → M4 → M5 → M6 → M7 → M8 → M9 → M10 → M11 → M12 → **M13** ✅

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
