# resume_pdf_agent

`resume_pdf_agent` is a criteria-aware AI resume PDF generation agent. The project now has foundations for schemas, static criteria, resume type classification, gap analysis, truthfulness checking, bullet enhancement, internal template metadata matching, HTML resume rendering, and M9 PDF Generation Pipeline v0.

## Current Milestone: M10

M10 adds CLI / Programmatic Workflow Integration, connecting all M0–M9 deterministic modules into a usable local pipeline.

M10 provides:

- **Programmatic API**: `resume_pdf_agent.workflow.run_resume_workflow` for end-to-end execution.
- **CLI**: Typer-based CLI with `run-sample`, `run`, `list-criteria`, and `list-templates` commands.
- **Structured intermediate outputs**: Optional JSON artifacts for criteria profile, classification, gap analysis, truthfulness, enhancement, and template selection.
- **Final outputs**: `resume.html` and `resume.pdf` (mock PDF backend used for tests/sample runs).
- **Deterministic sample**: Built-in `data/sample_inputs/sample_data_science_user.json`.

M10 does NOT implement frontend UI, UI polish, LLM API calls, online template search, or Word/JPG/PNG export.

## Windows Example Commands

```bash
py -m resume_pdf_agent run-sample --output-dir outputs/sample_run --pdf-backend mock
py -m resume_pdf_agent run --input data/sample_inputs/sample_data_science_user.json -o outputs/custom_run
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

- M11: Frontend basic workflow page.
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
