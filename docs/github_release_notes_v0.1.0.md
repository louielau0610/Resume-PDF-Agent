# GitHub Release Notes v0.1.0

## Summary

v0.1.0 is the first public release candidate for `resume_pdf_agent`. It consolidates the deterministic resume PDF workflow and the complete safe LLM candidate review chain through M30.

## Highlights

- Generate structured resume HTML/PDF artifacts.
- Run a local mock LLM rewrite candidate workflow.
- Review candidates in static browser pages.
- Produce decision summaries, application plans, preview UI, validation reports, manual patch previews, approval checklists, and final human edit instructions.
- Preserve strict safety boundaries: no automatic candidate application, no executable patch generation, no system-granted final approval.

## Validation

See [`docs/release_validation_report_v0.md`](release_validation_report_v0.md) for the exact validation run.

## Scope Freeze

No more checklist layers are planned for v0.1.0. Future work should be driven by real user feedback.
