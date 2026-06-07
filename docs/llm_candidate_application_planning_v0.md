# LLM Candidate Application Planning v0

## 概览 / Overview

M24 adds a deterministic Candidate Application Planning Layer for reviewed LLM rewrite candidates. It consumes M16 rewrite candidates and M22/M23 review decisions, then produces auditable plan-only artifacts.

M24 outputs:

- `llm_rewrite_application_plan.json`
- `llm_rewrite_application_plan.md`

These artifacts identify which candidates could be manually considered later, which are blocked, which require editing, which are excluded, and which cannot be mapped safely.

## Inputs

- `llm_rewrite_result.json`: M16 LLM rewrite candidates.
- `llm_rewrite_review_decisions.json`: M22 browser review decisions.
- `llm_rewrite_review_decision_summary.json`: optional M23 advisory summary.

## CLI

```bash
py -m resume_pdf_agent plan-llm-candidate-application \
  --result outputs/m24_llm_mock/llm_rewrite_result.json \
  --decisions outputs/m24_llm_mock/llm_rewrite_review_decisions.json \
  --summary outputs/m24_llm_mock/llm_rewrite_review_decision_summary.json \
  --output-json outputs/m24_llm_mock/llm_rewrite_application_plan.json \
  --output-md outputs/m24_llm_mock/llm_rewrite_application_plan.md
```

Use `--strict` to fail on unsupported decision actions.

## Workflow Behavior

The default workflow is unchanged. M24 runs only when explicitly requested through workflow options or the demo flag.

Demo:

```bash
py scripts/run_demo_workflow.py --output-dir outputs/m24_demo --pdf-backend mock --include-llm-mock --write-llm-review-ui --write-llm-review-decision-summary --write-llm-application-plan
```

## Safety Boundaries

- This is a plan-only artifact.
- No candidate is applied.
- `resume.html` and `resume.pdf` are not modified.
- This is not a resume patch.
- Approval does not mean factual verification.
- M5 truthfulness checks and M14 confirmation safeguards still apply.
- No real LLM API is called.
- No network, scraping, database, authentication, or production server workflow is added.
- Export remains PDF-only.

## Known Limitations

- M24 does not implement a patching engine.
- M24 does not modify enhanced bullets or final resume artifacts.
- M24 does not resolve M5 truthfulness or M14 confirmation items.
- Unmapped targets remain blocked for manual inspection.
