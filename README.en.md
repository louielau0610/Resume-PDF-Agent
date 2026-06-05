# resume_pdf_agent

`resume_pdf_agent` is a criteria-aware AI resume PDF generation agent. The project now has foundations for schemas, static criteria, resume type classification, gap analysis, truthfulness checking, bullet enhancement, internal template metadata matching, HTML resume rendering, and M9 PDF Generation Pipeline v0.

## Current Milestone: M11

M11 adds Frontend Basic Workflow Page v0 — a static HTML dashboard for workflow runs.

M11 provides:

- **Static dashboard page**: Shows workflow status, stage timeline, warnings/errors, and artifact links.
- **Resume output links**: Direct links to `resume.html` and `resume.pdf`.
- **Conversion reminder**: Shown in the dashboard area only, not in the resume body.
- **No web server needed**: The HTML page opens directly in a browser.

M11 does NOT implement React/FastAPI, UI polish, LLM API calls, or a web server.

## Windows Example Commands

```bash
# Run workflow and generate frontend page
py -m resume_pdf_agent run-sample --output-dir outputs/sample_page --pdf-backend mock --write-frontend-page

# Generate frontend page (auto-runs workflow)
py -m resume_pdf_agent render-page --input data/sample_inputs/sample_data_science_user.json -o outputs/page_run

# Other commands
py -m resume_pdf_agent run-sample --output-dir outputs/sample_run --pdf-backend mock
py -m resume_pdf_agent list-criteria
py -m resume_pdf_agent list-templates
```

## Supported Internal Template Metadata

- ATS student basic
- Data science technical
- Software engineering technical
- Finance business
- Consulting business
- Research CV
- Product manager
- Design portfolio light

## Upcoming Milestones

- M12: Frontend UI polish based on user-provided sample images.

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
