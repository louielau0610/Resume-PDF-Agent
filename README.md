# resume_pdf_agent

安全优先、人工审阅驱动的简历 PDF 生成与 LLM 改写候选审阅工具。

`resume_pdf_agent` 是一个本地运行的 Python 项目，用于从结构化用户资料生成 ATS 友好的简历 HTML/PDF，并提供一条完整的 LLM 候选改写审阅链路：生成候选、浏览器本地审阅、汇总决策、生成应用计划、预览、验证、人工补丁预览、人工审批清单，以及最终人工编辑指引。系统不会自动把 LLM 候选写入最终简历。

## 核心价值

- 生成结构化 `resume.html` 和 `resume.pdf`。
- 使用 mock LLM workflow 生成可审阅的改写候选。
- 通过本地静态 HTML 页面审阅候选，不上传数据。
- 汇总本地审阅决策，生成 advisory summary。
- 生成 plan / preview / validation / manual checklist / final edit instruction artifacts。
- 始终保持 human-in-the-loop：最终简历内容不会被候选链路自动修改。

## 安全承诺

- 不自动应用 LLM candidates。
- 不生成可执行 patch。
- 系统不授予最终批准。
- 仅支持 PDF 导出格式。
- 所有 LLM 候选都需要人工审阅。
- 浏览器页面均为本地静态 HTML，无服务器提交。
- 不调用真实 LLM API；mock workflow 可离线运行。
- 不声称了解公司内部筛选标准。
- 不预测录用、面试或 offer 结果。

## 快速开始

```bash
py -m resume_pdf_agent run-sample --output-dir outputs/quickstart --pdf-backend mock --write-frontend-page
```

完整 release demo：

```bash
py scripts/run_demo_workflow.py --output-dir outputs/release_demo --pdf-backend mock --include-llm-mock --write-llm-review-ui --write-llm-review-decision-summary --write-llm-application-plan --write-llm-application-preview-ui --write-llm-pre-application-validation --write-llm-manual-patch-preview --write-llm-manual-approval-checklist --write-llm-human-final-edit-pack
```

## 主要输出

基础 workflow：

- `resume.html`: 结构化简历 HTML。
- `resume.pdf`: mock / WeasyPrint / Playwright 后端生成的 PDF。
- `index.html`: 本地 workflow dashboard。
- `workflow_result.json`: 完整运行结果。

LLM 审阅链路：

- `llm_rewrite_result.json`: LLM 改写候选。
- `llm_review.html`: 本地候选审阅 UI。
- `llm_rewrite_review_decisions.json`: 本地审阅决策。
- `llm_rewrite_review_decision_summary.json/.md`: 决策汇总。
- `llm_rewrite_application_plan.json/.md`: plan-only 应用计划。
- `llm_rewrite_application_preview.html`: 人工预览 UI。
- `llm_rewrite_pre_application_validation.json/.md`: 严格预应用验证。
- `llm_rewrite_manual_patch_preview.json/.md/.html`: 展示用人工补丁预览。
- `llm_rewrite_manual_patch_approval_checklist.json/.md/.html`: 人工审批清单。
- `llm_rewrite_human_final_edit_instruction_pack.json/.md/.html`: 最终人工编辑指引。

## CLI 概览

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

## 架构摘要

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

## 当前发布状态

- Release candidate: v0.1.0
- Scope: M0-M30 complete
- Baseline: full pytest expected at `1023 passed, 2 skipped`
- Export format: `pdf` only
- README: Chinese-first
- No more checklist layers are planned for v0.1.0. Future work should be based on real user feedback.

## 已知限制

- 默认演示使用 mock PDF / mock LLM workflow。
- 真实 LLM provider integration 不在 v0.1.0 范围内。
- LLM 候选链路只产生审阅与人工操作 artifacts，不修改最终简历。
- 不导出 DOCX/JPG/PNG。
- 浏览器页面是本地静态页面，不是生产 Web 应用。

## 文档

- [`docs/demo_walkthrough_v0.md`](docs/demo_walkthrough_v0.md)
- [`docs/launch_notes_v0.md`](docs/launch_notes_v0.md)
- [`docs/release_validation_report_v0.md`](docs/release_validation_report_v0.md)
- [`docs/promotion_copy_v0.md`](docs/promotion_copy_v0.md)
- [`docs/architecture_diagram_v0.md`](docs/architecture_diagram_v0.md)
- [`docs/limitations_and_roadmap_v0.md`](docs/limitations_and_roadmap_v0.md)

## License

MIT
