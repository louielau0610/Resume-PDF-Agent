# resume_pdf_agent

A safety-first, human-reviewed resume PDF generator with local LLM rewrite candidate review.

`resume_pdf_agent` is a local Python project that turns structured career data into ATS-friendly resume HTML/PDF artifacts. It also provides a complete LLM candidate review chain: candidate generation, local browser review, decision summaries, application planning, preview, validation, manual patch preview, manual approval checklist, and final human edit instructions. The system never automatically writes LLM candidates into the final resume.

## Core Value

- Generate structured `resume.html` and `resume.pdf`.
- Generate mock LLM rewrite candidates for review.
- Review candidates in local static browser pages.
- Summarize local review decisions.
- Produce plan / preview / validation / manual checklist / final edit instruction artifacts.
- Keep final content human-controlled.

## Safety Promise

- No automatic LLM candidate application.
- No executable patch generation.
- No final approval granted by the system.
- PDF-only export.
- Human-in-the-loop review.
- Local static review pages.
- No real LLM API call required for the mock workflow.
- No claim of access to company-internal screening standards.
- No prediction of recruiting outcomes.

## Quick Start

```bash
py -m resume_pdf_agent run-sample --output-dir outputs/quickstart --pdf-backend mock --write-frontend-page
```

Full release demo:

```bash
py scripts/run_demo_workflow.py --output-dir outputs/release_demo --pdf-backend mock --include-llm-mock --write-llm-review-ui --write-llm-review-decision-summary --write-llm-application-plan --write-llm-application-preview-ui --write-llm-pre-application-validation --write-llm-manual-patch-preview --write-llm-manual-approval-checklist --write-llm-human-final-edit-pack
```

## Output Artifacts

Core workflow:

- `resume.html`: structured resume HTML.
- `resume.pdf`: generated PDF.
- `index.html`: local workflow dashboard.
- `workflow_result.json`: complete workflow result.

LLM review chain:

- `llm_rewrite_result.json`
- `llm_review.html`
- `llm_rewrite_review_decisions.json`
- `llm_rewrite_review_decision_summary.json/.md`
- `llm_rewrite_application_plan.json/.md`
- `llm_rewrite_application_preview.html`
- `llm_rewrite_pre_application_validation.json/.md`
- `llm_rewrite_manual_patch_preview.json/.md/.html`
- `llm_rewrite_manual_patch_approval_checklist.json/.md/.html`
- `llm_rewrite_human_final_edit_instruction_pack.json/.md/.html`

## CLI Overview

```bash
py -m resume_pdf_agent run-sample --output-dir outputs/demo --pdf-backend mock
py -m resume_pdf_agent run --input data/sample_inputs/sample_data_science_user.json --output-dir outputs/custom
py -m resume_pdf_agent render-llm-review-ui --result outputs/demo/llm_rewrite_result.json --output outputs/demo/llm_review.html
py -m resume_pdf_agent summarize-llm-review-decisions --decisions outputs/demo/llm_rewrite_review_decisions.json --result outputs/demo/llm_rewrite_result.json
py -m resume_pdf_agent plan-llm-candidate-application --result outputs/demo/llm_rewrite_result.json --decisions outputs/demo/llm_rewrite_review_decisions.json
py -m resume_pdf_agent render-llm-application-preview-ui --plan outputs/demo/llm_rewrite_application_plan.json --output outputs/demo/llm_rewrite_application_preview.html
py -m resume_pdf_agent validate-llm-pre-application --plan outputs/demo/llm_rewrite_application_plan.json
py -m resume_pdf_agent preview-llm-manual-patch --plan outputs/demo/llm_rewrite_application_plan.json --validation outputs/demo/llm_rewrite_pre_application_validation.json
py -m resume_pdf_agent build-llm-manual-approval-checklist --preview outputs/demo/llm_rewrite_manual_patch_preview.json
py -m resume_pdf_agent build-llm-human-final-edit-pack --checklist outputs/demo/llm_rewrite_manual_patch_approval_checklist.json
```

## Architecture Summary

```text
UserProfile + ResumeContent
  -> criteria selection
  -> resume type classification
  -> gap analysis
  -> truthfulness check
  -> bullet enhancement
  -> template matching
  -> HTML rendering
  -> PDF generation
  -> optional static dashboards

Optional LLM review chain:
  M16 rewrite candidates
  -> M22 local review UI
  -> M23 decision summary
  -> M24 application plan
  -> M25 preview UI
  -> M26 validation
  -> M27 manual patch preview
  -> M28 manual approval checklist
  -> M29 human final edit instruction pack
```

## Release Status

- Release candidate: v0.1.0
- Scope: M0-M30 complete
- Baseline: full pytest expected at `1023 passed, 2 skipped`
- Export format: `pdf` only
- No more checklist layers are planned for v0.1.0. Future work should be based on real user feedback.

## Known Limitations

- The default demo uses mock PDF / mock LLM workflows.
- Real LLM provider integration is outside v0.1.0 scope.
- The LLM candidate chain produces review and manual-operation artifacts only.
- No DOCX/JPG/PNG export.
- Browser pages are local static pages, not a production web application.

## Docs

- [`docs/demo_walkthrough_v0.md`](docs/demo_walkthrough_v0.md)
- [`docs/launch_notes_v0.md`](docs/launch_notes_v0.md)
- [`docs/release_validation_report_v0.md`](docs/release_validation_report_v0.md)
- [`docs/promotion_copy_v0.md`](docs/promotion_copy_v0.md)
- [`docs/architecture_diagram_v0.md`](docs/architecture_diagram_v0.md)
- [`docs/limitations_and_roadmap_v0.md`](docs/limitations_and_roadmap_v0.md)

## License

MIT
