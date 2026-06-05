# resume_pdf_agent

`resume_pdf_agent` is a criteria-aware AI resume PDF generation agent. The project now has foundations for schemas, static criteria, resume type classification, gap analysis, truthfulness checking, bullet enhancement, internal template metadata matching, HTML resume rendering, and M9 PDF Generation Pipeline v0.

## Current Milestone: M9

M9 adds PDF Generation Pipeline v0. It converts M8 HTML output into local PDF files and returns a structured `PDFGenerationResult`.

The M9 PDF pipeline:

- Generates PDF from an existing `HTMLRenderResult`.
- Or calls the M8 renderer from `UserProfile`, `ResumeContent`, and `TemplateSelectionResult`, then generates PDF.
- Uses a backend adapter design, preferring WeasyPrint when available.
- Supports a deterministic mock backend for tests when system PDF dependencies are unavailable.
- Validates that the output PDF exists, is non-empty, and starts with a `%PDF` header.
- Preserves HTML rendering warnings and PDF generation warnings.
- Provides a neutral conversion reminder in result metadata: users who need Word/JPG/PNG can use an external PDF conversion tool after PDF export.

M9 only exports PDF. It does not implement Word/JPG/PNG export, frontend UI, sample-image-based UI polish, LLM API calls, online template search, template downloads, or claims about internal company screening standards.

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

- M10: CLI or API workflow integration.
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
