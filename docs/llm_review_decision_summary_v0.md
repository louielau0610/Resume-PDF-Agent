# LLM Review Decision Summary v0

## 概览 / Overview

M23 adds a deterministic local loader and summary workflow for `llm_rewrite_review_decisions.json`, the advisory decisions exported from the M22 browser LLM rewrite review UI.

M23 可以回答：

- 哪些 LLM rewrite candidates 被 approved、rejected、needs editing、ignored。
- 哪些 candidates 带有 reviewer notes。
- decisions file 是否包含 unknown candidate IDs、duplicate entries、unknown actions。
- `llm_rewrite_result.json` 中是否还有未审阅 candidates。
- 用户在手动处理前应注意哪些 warnings。

## 输入 / Inputs

- `llm_rewrite_review_decisions.json`: browser review UI exported decisions.
- `llm_rewrite_result.json`: optional M16 rewrite result used for candidate ID cross-checking.

If `llm_rewrite_result.json` is omitted, M23 still summarizes decision counts and warns that candidate cross-checking was skipped.

## 输出 / Outputs

- `llm_rewrite_review_decision_summary.json`: deterministic machine-readable summary.
- `llm_rewrite_review_decision_summary.md`: Chinese-first human-readable summary.

## CLI

```bash
py -m resume_pdf_agent summarize-llm-review-decisions \
  --result outputs/m23_llm_mock/llm_rewrite_result.json \
  --decisions outputs/m23_llm_mock/llm_rewrite_review_decisions.json \
  --output-json outputs/m23_llm_mock/llm_rewrite_review_decision_summary.json \
  --output-md outputs/m23_llm_mock/llm_rewrite_review_decision_summary.md
```

Use `--no-strict` by default to tolerate unknown actions as warnings. Use `--strict` to fail on unknown decision actions.

## Workflow Behavior

The normal resume workflow is unchanged by default. Optional workflow fields can point to an exported decisions file and request summary artifacts, but summary generation is advisory only and does not feed back into resume rendering or PDF generation.

The demo helper can create deterministic sample decisions and summarize them:

```bash
py scripts/run_demo_workflow.py --output-dir outputs/m23_demo --pdf-backend mock --include-llm-mock --write-llm-review-ui --write-llm-review-decision-summary
```

## Safety Boundaries

- This summary does not apply candidates.
- Approved candidates are not automatically inserted into `resume.html` or `resume.pdf`.
- Approval does not mean a claim is factually verified.
- M5 truthfulness checks and the M14 confirmation gate still apply.
- No real LLM API is called.
- No network request, scraping, database, authentication, or server workflow is added.
- Export remains PDF-only.

## Known Limitations

- M23 does not implement resume patching.
- M23 does not resolve truthfulness or confirmation items.
- M23 does not decide whether approved text is safe to publish.
- Duplicate and unknown decisions are reported as warnings for manual review.
