# Browser LLM Application Preview UI v0

## 概览 / Overview

M25 新增本地静态的 Manual Candidate Application Preview UI。它读取 M24 生成的 `llm_rewrite_application_plan.json`，渲染 `llm_rewrite_application_preview.html`，帮助用户人工检查 planned、blocked、needs_manual_edit、excluded、unmapped 候选改写。

该页面只做预览和审计，不会应用候选文本，不会修改最终简历，也不会生成会改变简历内容的 patch。

## 输入

- `llm_rewrite_application_plan.json`: M24 plan-only application plan。

## 输出

- `llm_rewrite_application_preview.html`: 完全本地的静态 HTML 页面。

页面包含 source files、count summary、status groups、original text、proposed candidate text、target mapping、decision action、block reasons、validation warnings、manual review notes、needs-confirmation marker 和 safety gates still required。

## CLI

```bash
py -m resume_pdf_agent render-llm-application-preview-ui \
  --plan outputs/m24_llm_mock/llm_rewrite_application_plan.json \
  --output outputs/m25_application_preview/llm_rewrite_application_preview.html
```

## Workflow Behavior

默认 workflow 不变。只有显式启用 `write_llm_application_preview_ui` 时才会渲染预览页。启用后如果存在 M24 plan JSON，会写出 `llm_rewrite_application_preview.html`；如果没有可用 plan JSON，会记录 warning 并继续。

Demo:

```bash
py scripts/run_demo_workflow.py \
  --output-dir outputs/m25_demo \
  --pdf-backend mock \
  --include-llm-mock \
  --write-llm-review-ui \
  --write-llm-review-decision-summary \
  --write-llm-application-plan \
  --write-llm-application-preview-ui
```

## Safety Boundaries

- No candidate is applied.
- `resume.html` and `resume.pdf` are not modified by the preview renderer.
- The preview page is not an application engine.
- The preview page is not a resume patch generator.
- Approval or planned status does not mean factual verification.
- M5 truthfulness checks and M14 confirmation gate still apply.
- No real LLM API is called.
- No LLM provider integration is added.
- No network call, scraping, database, authentication, upload, or server workflow is added.
- No external CDN, fonts, images, CSS, or JavaScript are used.
- Export remains PDF-only.
- No Word/JPG/PNG export is added.
- No hiring probability, interview probability, offer probability, ATS internal scoring, or internal screening claim is made.

## Known Limitations

- M25 does not apply or edit resume content.
- M25 does not resolve truthfulness or confirmation requirements.
- M25 does not infer missing target mappings.
- M25 does not validate that proposed text is factually true.
- Copy controls are only for manual review.
