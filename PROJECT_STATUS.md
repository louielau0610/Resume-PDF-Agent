# 项目状态

## M25 Manual Candidate Application Preview UI

M25 已完成：新增本地静态 `llm_rewrite_application_preview.html`，从 M24 `llm_rewrite_application_plan.json` 渲染人工预览页面，用于检查 planned / blocked / needs_manual_edit / excluded / unmapped candidates。M25 是 manual preview UI，不是 application engine；不会应用 LLM candidates，不会修改 `resume.html`/`resume.pdf`，也不会绕过 M5/M14。

## M24 Candidate Application Planning Layer

M24 已完成：新增 plan-only LLM candidate application planning layer，可生成 `llm_rewrite_application_plan.json` / `.md`。该层只做人工应用规划与审计，不会应用 LLM candidates，不会修改 `resume.html`/`resume.pdf`，也不会绕过 M5/M14。

## M23 LLM Review Decision Loader / Decision Summary

M23 已完成：新增本地 `llm_rewrite_review_decisions.json` loader、deterministic analyzer、JSON/Markdown summary artifacts，以及 `summarize-llm-review-decisions` CLI。M23 是 advisory decision summary workflow，不会应用 LLM candidates，不会修改 `resume.html`/`resume.pdf`，也不会绕过 M5/M14。

## M22.1 Safety Hardening / Autoescape Refactor

M22.1 已完成：浏览器端 LLM 改写审阅 UI 现在在 Jinja2 模板层启用 autoescape，并使用模板 JSON 转义保护嵌入的候选数据。该里程碑是安全加固，不是新功能里程碑；LLM 候选仍仅为建议，不会自动应用，不会调用真实 LLM API，也不会绕过 M5/M14。

## Current Documentation Milestone

M27.1 Strict Validation for M27（当前）

## 已完成里程碑

**M0-M12**：项目基础 → 确定性管线 → 前端仪表板
**M13**：Demo 打包 / GitHub 呈现 / 发布就绪（复刻）

**M14-M21**：
- M14：用户确认工作流 ✅
- M15：用户提供 JD 解析器（含合规检查） ✅
- M16：可选 LLM 改写适配器 ✅
- M16.1：全量验证和 CLI 回归检查 ✅
- M17：PDF Backend 设置验证 ✅
- M18：视觉回归测试 ✅
- M18.1：全量验证 ✅
- M19：可选 API 层 ✅
- M19.1：API 文档和可选依赖验证 ✅
- M20：浏览器端确认 UI ✅
- M20.1：确认 UI 验证修复 ✅
- M21：浏览器端 JD 上传 UI ✅
- M21.1：JD 上传 UI 验证与测试覆盖 ✅
- M22：浏览器端 LLM 改写审阅 UI ✅
- M22.1：LLM 审阅 UI autoescape 加固 ✅
- M23：LLM 审阅决策加载器 / 建议摘要 ✅
- M24：LLM 候选应用规划层 ✅
- M25：人工候选应用预览 UI ✅
- M26：严格预应用验证层 ✅
- M26.1：验证与文档完成 ✅
- M27：人工补丁预览（不修改简历） ✅
- M27.1：M27 严格验证 ✅

## 当前状态

M27 人工补丁预览已完成 — 全量测试 984 通过，2 跳过。项目现已具备完整的 LLM 安全管线：M16 改写 → M22 审阅 → M23 摘要 → M24 规划 → M25 预览 → M26 验证 → M27 补丁预览（均不自动应用候选，不生成可执行补丁）。项目现已具备完整的 LLM 安全管线：M16 改写 → M22 审阅 → M23 决策摘要 → M24 应用规划 → M25 预览 → M26 预应用验证（均不自动应用候选）。 — 新增 76 个专用 LLM 审阅 UI 测试（上下文/渲染器/安全/CLI/回归），全量测试 778 通过，2 跳过。所有手动 CLI 验证通过：mock LLM 生成、render-llm-review-ui、demo 脚本 --write-llm-review-ui、ExportFormat 仅 pdf。M16 LLM 引擎行为不变，默认工作流保持向后兼容。项目现已具备三张纯静态浏览器页面（M20 确认审核、M21 JD 输入、M22 LLM 改写审阅）。

## 下一计划里程碑

M22：产品打磨 / 稳定性（已到达商业化路线图中的轨道 1）

## M0-M15 已完成

- M0：项目基础结构、配置、异常、占位 pipeline 和基础测试。
- M1：用户画像、简历内容、criteria、analysis 和真实性 safeguard schemas。
- M2：静态 criteria knowledge base v0、loader 和 selector。
- M3：deterministic resume type classifier。
- M4：criteria-based gap analysis engine。
- M5：truthfulness and unsupported-claim checker。
- M6：criteria-aware bullet enhancement engine。
- M7：internal template metadata matching。
- M8：HTML resume rendering。
- M9：PDF generation pipeline。
- M10：CLI / programmatic workflow integration。
- M11：Frontend basic workflow page。
- M12：Frontend UI Polish（cinematic dark 主题）。
- M13：GitHub / Demo Packaging & Release Readiness。
- M14：User Confirmation Workflow ✅（当前）。

## M14 已完成内容

- `docs/demo_walkthrough_v0.md` — 完整本地演示导览（中文）。
- `docs/architecture_diagram_v0.md` — Mermaid 架构与工作流图（中文）。
- `docs/github_project_overview_v0.md` — 面向招聘方/技术评审的项目概览（中文+英文）。
- `docs/release_checklist_v0.md` — 发布检查清单（中文）。
- `docs/limitations_and_roadmap_v0.md` — 当前限制与未来路线图（中文）。
- `examples/README.md` — 示例目录说明（中文）。
- `examples/sample_data_science_demo.md` — 内置数据科学示例说明（中文）。
- `scripts/run_demo_workflow.py` — 演示工作流运行脚本。
- `scripts/validate_release_readiness.py` — 发布就绪验证脚本。
- `tests/test_release_readiness_docs.py` — M13 文档验证测试。
- `tests/test_demo_script.py` — 演示脚本验证测试。
- `README.md` — 全面更新为 M13 状态，添加架构、特性、安全边界、路线图等。
- `README.en.md` — 英文 README 同步更新。
- `PROJECT_STATUS.md` — 更新到 M13（本文档）。
- `TODO.md` — 更新里程碑和未来路线图。
- `.gitignore` — 确认忽略 `outputs/`、`__pycache__/`、`.pytest_cache/`。

M13 不实现新功能：无 LLM API、无 JD 解析、无 Word/JPG/PNG 导出、无 Web 应用。M13 是文档、演示打包和发布就绪里程碑。

## 尚未实现内容

- 真实 JD（岗位描述）解析。
- LLM 辅助 bullet 改写。
- 用户确认工作流。
- 生产 PDF Backend（WeasyPrint）安装指南。
- Word/JPG/PNG 导出。
- 生产 Web 应用（FastAPI/Flask/React）。
- 浏览器端工作流执行。
- 视觉回归测试。

## 重要产品约束

- 不联网搜索或下载简历模板。
- 不声称知道任何公司的内部简历筛选算法。
- 不调用 LLM API。
- v0 仍然只支持 PDF 导出。
- 不预测录用概率、面试概率或 offer 概率。
