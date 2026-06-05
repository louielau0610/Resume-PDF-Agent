# resume_pdf_agent

`resume_pdf_agent` is a criteria-aware AI resume PDF generation agent. The project now has foundations for schemas, static criteria, resume type classification, gap analysis, truthfulness checking, bullet enhancement, internal template metadata matching, HTML resume rendering, and M9 PDF Generation Pipeline v0.

## Current Milestone: M12

M12 adds Frontend UI Polish: upgrades the static workflow dashboard to a cinematic dark-themed premium layout.

M12 provides:

- **Dark cinematic dashboard**: black/deep-gray background, large rounded cards, low-saturation accents
- **Semantic layout**: app-shell, hero-panel, metric-grid, stage-timeline
- **Pure CSS**: no external images/fonts/CDN dependencies
- **Preserves all M11 functionality**: workflow status, stage timeline, warnings/errors, artifact links
- **No backend changes**: workflow, PDF generation, HTML rendering are unaffected

M12 does NOT implement React/FastAPI, Word/JPG/PNG export, or LLM API calls.

## Windows Example Commands

```bash
# Run workflow and generate polished frontend page
py -m resume_pdf_agent run-sample --output-dir outputs/sample_page --pdf-backend mock --write-frontend-page

# Open in browser: outputs/sample_page/index.html
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

None. M12 is the latest milestone.

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
