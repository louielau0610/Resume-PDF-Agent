# Demo Walkthrough v0

This walkthrough demonstrates the v0.1.0 release workflow. It uses local sample data, mock PDF generation, and mock LLM rewrite candidates. No real LLM API is called.

## 1. Run the basic sample

```bash
py -m resume_pdf_agent run-sample --output-dir outputs/quickstart --pdf-backend mock --write-frontend-page
```

Expected core artifacts:

- `outputs/quickstart/resume.html`
- `outputs/quickstart/resume.pdf`
- `outputs/quickstart/index.html`
- `outputs/quickstart/workflow_result.json`

## 2. Run the full release demo

```bash
py scripts/run_demo_workflow.py --output-dir outputs/release_demo --pdf-backend mock --include-llm-mock --write-llm-review-ui --write-llm-review-decision-summary --write-llm-application-plan --write-llm-application-preview-ui --write-llm-pre-application-validation --write-llm-manual-patch-preview --write-llm-manual-approval-checklist --write-llm-human-final-edit-pack
```

This command runs the normal resume workflow and then generates the complete safe LLM candidate review chain.

## 3. Generate PDF

The workflow writes:

- `resume.html`
- `resume.pdf`

The mock backend writes a deterministic PDF-like artifact beginning with `%PDF`, which is sufficient for local test and release validation.

## 4. Generate mock LLM candidates

With `--include-llm-mock`, the demo writes:

- `llm_rewrite_result.json`

These candidates are suggestions only. They are not applied to the final resume.

## 5. Review UI

With `--write-llm-review-ui`, the demo writes:

- `llm_review.html`

This is a local static browser page for inspecting LLM rewrite candidates. It does not submit data and does not modify resume files.

## 6. Decision summary

With `--write-llm-review-decision-summary`, the demo creates deterministic sample decisions and writes:

- `llm_rewrite_review_decisions.json`
- `llm_rewrite_review_decision_summary.json`
- `llm_rewrite_review_decision_summary.md`

The summary is advisory and does not apply candidates.

## 7. Application plan

With `--write-llm-application-plan`, the demo writes:

- `llm_rewrite_application_plan.json`
- `llm_rewrite_application_plan.md`

This plan classifies candidates as planned, blocked, needs manual edit, excluded, or unmapped. It remains plan-only.

## 8. Application preview

With `--write-llm-application-preview-ui`, the demo writes:

- `llm_rewrite_application_preview.html`

This page previews candidate text and target mapping for manual inspection only.

## 9. Pre-application validation

With `--write-llm-pre-application-validation`, the demo writes:

- `llm_rewrite_pre_application_validation.json`
- `llm_rewrite_pre_application_validation.md`

This validation checks whether candidate application would be safe to consider manually. It does not change the resume.

## 10. Manual patch preview

With `--write-llm-manual-patch-preview`, the demo writes:

- `llm_rewrite_manual_patch_preview.json`
- `llm_rewrite_manual_patch_preview.md`
- `llm_rewrite_manual_patch_preview.html`

This is a display-only preview. It is not an executable patch.

## 11. Manual approval checklist

With `--write-llm-manual-approval-checklist`, the demo writes:

- `llm_rewrite_manual_patch_approval_checklist.json`
- `llm_rewrite_manual_patch_approval_checklist.md`
- `llm_rewrite_manual_patch_approval_checklist.html`

The checklist requires human review. The system does not grant approval.

## 12. Human final edit instruction pack

With `--write-llm-human-final-edit-pack`, the demo writes:

- `llm_rewrite_human_final_edit_instruction_pack.json`
- `llm_rewrite_human_final_edit_instruction_pack.md`
- `llm_rewrite_human_final_edit_instruction_pack.html`

This is the final human-only instruction layer. Any actual edit must be performed manually outside the system.

## Safety Checks

The release demo should preserve these boundaries:

- `resume.html` and `resume.pdf` are not modified by LLM candidate artifacts.
- No `.patch` or `.diff` files are generated.
- No `applied_candidates` field appears in final workflow artifacts.
- No `patch_operations` field appears in final workflow artifacts.
- Export format remains `pdf` only.
