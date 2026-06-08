# TODO

## M25 Completed

- M25 Manual Candidate Application Preview UI 已完成：可从 M24 `llm_rewrite_application_plan.json` 生成本地静态 `llm_rewrite_application_preview.html`，用于人工检查候选改写状态、原文、候选文本、阻止原因、验证警告和人工备注。
- M26 可作为下一阶段：Strict Pre-Application Validation Layer 或 Manual Patch Preview Without Resume Mutation；本次不实现 M26。

## M24 Completed

- M24 Candidate Application Planning Layer 已完成：可生成 plan-only `llm_rewrite_application_plan.json` / `.md`，用于人工审阅未来可能应用的 LLM candidates，但不自动修改最终简历。
- M25 可作为下一阶段：Manual Candidate Application Review / Patch Preview UI 或 Strict Plan Validation Before Candidate Application；本次不实现 M25。

## M23 Completed

- M23 LLM Review Decision Loader / Decision Summary 已完成：可本地读取 `llm_rewrite_review_decisions.json`，生成 advisory JSON/Markdown summary，并报告 undecided / unknown / duplicate / invalid decisions。
- M24 可作为下一阶段计划层：Candidate Application Planning Layer。M24 仍应保持 plan-only，不自动修改最终简历。

## M22.1 Completed

- M22.1 Safety Hardening / Autoescape Refactor 已完成：LLM 审阅 UI 启用 Jinja2 template-level autoescape，并保留候选仅供审阅、不自动应用、不调用真实 LLM API、不绕过 M5/M14 的安全边界。
- M23 仍作为下一阶段可选里程碑；本次不实现自动应用候选或真实 LLM provider 集成。

## M0-M21 Completed ✅

- M0：Project foundation。
- M1：Core schemas（UserProfile、ResumeContent、Criteria 等）。
- M2：Static criteria knowledge base v0（6 个角色 profile）。
- M3：Resume type classifier（8 种类型）。
- M4：Criteria-based gap analysis engine。
- M5：Truthfulness and unsupported-claim checker。
- M6：Criteria-aware bullet enhancement engine。
- M7：Internal template metadata matching（8 个模板）。
- M8：HTML resume rendering。
- M9：PDF generation pipeline（Mock/WeasyPrint/Playwright）。
- M10：CLI / programmatic workflow integration。
- M11：Frontend basic workflow page。
- M12：Frontend UI Polish（cinematic dark 主题）。
- M13：GitHub / Demo Packaging & Release Readiness。
- M14：User Confirmation Workflow ✅。
- M15：User-Provided JD Parser with Compliance ✅。
- M16：Optional LLM-Assisted Rewriting ✅。
- M16.1：Full Validation and CLI Regression ✅。
- M17：PDF Backend Setup Verification ✅。
- M18：Visual Regression Testing ✅。
- M18.1：Full Validation ✅。
- M19：Optional API Layer ✅。
- M19.1：API Docs and Optional Deps Verification ✅。
- M20：Browser Confirmation UI ✅。
- M20.1：Confirmation UI Verification Fix ✅。
- M21：Browser JD Upload UI ✅。
- M21.1：JD Upload UI Verification and Test Coverage ✅。
- M22：Browser-based LLM Rewrite Review UI ✅（当前）。

## M21: Browser JD Upload UI ✅ (current)

- 已完成 `models/jd_ui.py`：浏览器 JD 上传 UI Pydantic 模型。
- 已完成 `jd_ui/safety.py`：客户端风险标记检测。
- 已完成 `jd_ui/context.py`：UI 上下文构建器。
- 已完成 `jd_ui/renderer.py`：Jinja2 模板渲染器。
- 已完成 `jd_ui/templates/jd_upload_page.html.j2`：JD 输入页面模板。
- 已完成 `jd_ui/static/jd_upload_page.css`：暗色高级 CSS 主题（与 M12/M20 一致）。
- 已完成 `jd_ui/static/jd_upload_page.js`：本地 JS（标记检测、JSON 生成、复制/下载）。
- 已完成 `jd_ui/__init__.py`：包导出。
- 已集成到 models/__init__.py 和 CLI。
- 已创建 `docs/browser_jd_upload_ui_v0.md`：中文/英文文档。
- 已更新 PROJECT_STATUS.md 和 TODO.md。
- 未改变核心工作流逻辑。
- 测试：702 通过，2 跳过。


## M21.1: JD Upload UI Verification and Test Coverage ✅ (current)

- 已完成 `tests/test_jd_ui_context.py`：21 个上下文测试（模型/标记/安全声明）。
- 已完成 `tests/test_jd_ui_renderer.py`：22 个渲染器测试（HTML 结构/安全声明/CDN 检查）。
- 已完成 `tests/test_jd_ui_safety.py`：27 个安全测试（escape/静态 JS/CSS/渲染后 HTML）。
- 已完成 `tests/test_jd_ui_cli.py`：15 个 CLI 测试（render-jd-upload-ui/现有命令完整）。
- 已完成 `tests/test_jd_ui_regressions.py`：19 个回归测试（ExportFormat/无强制 Web 框架/READ ME 安全/向后兼容）。
- 手动 CLI 验证全部通过：render-jd-upload-ui、--write-jd-upload-ui、validate_release_readiness、后端 JD sanity workflow、ExportFormat。
- M15 后端 JD 合规行为不变。
- 默认工作流保持向后兼容。
- 未添加新功能。
- 全量测试：702 通过，2 跳过（新增 104 个 JD UI 测试）。


## M22: Browser-based LLM Rewrite Review UI ✅ (current)

- 已完成 `models/llm_review_ui.py`：LLM 审阅 UI Pydantic 模型。
- 已完成 `llm_review_ui/safety.py`：escape、路径安全、决策选项、验证函数。
- 已完成 `llm_review_ui/context.py`：UI 上下文构建器（分组/安全通知/决策选项）。
- 已完成 `llm_review_ui/renderer.py`：Jinja2 模板渲染器 + 从文件加载。
- 已完成 `llm_review_ui/templates/llm_review_page.html.j2`：审阅页面模板。
- 已完成 `llm_review_ui/static/llm_review_page.css`：暗色高级 CSS（与 M12/M20/M21 一致）。
- 已完成 `llm_review_ui/static/llm_review_page.js`：本地 JS（决策生成/复制/下载/筛选/折叠）。
- 已完成 `llm_review_ui/__init__.py`：包导出。
- 已集成到 models/__init__.py、CLI（render-llm-review-ui）、workflow 模型/编排器。
- 已更新 scripts/run_demo_workflow.py（--write-llm-review-ui）和 scripts/validate_release_readiness.py。
- 已创建 `docs/browser_llm_rewrite_review_ui_v0.md`：中文/英文文档。
- 已完成 5 个测试文件：context（18 个）、renderer（22 个）、safety（14 个）、CLI（8 个）、regressions（14 个）。
- M16 LLM 引擎行为不变。
- 默认工作流保持向后兼容。
- 未添加新功能（仅为审阅 UI 渲染）。
- 全量测试：778 通过，2 跳过（新增 76 个 LLM 审阅 UI 测试）。

## Future Roadmap（路线图想法，尚未实现）

- 已完成 5 个核心文档：demo_walkthrough、architecture_diagram、github_project_overview、release_checklist、limitations_and_roadmap。
- 已完成 examples/ 目录：README + sample_data_science_demo。
- 已完成 scripts/：run_demo_workflow.py + validate_release_readiness.py。
- 已完成 tests/：test_release_readiness_docs.py + test_demo_script.py。
- 已更新 README.md、README.en.md、PROJECT_STATUS.md、TODO.md。
- 未改变核心工作流逻辑。
- 未添加 LLM 调用、JD 解析、Word/JPG/PNG 导出、Web 应用。

## Future Roadmap（路线图想法，尚未实现）

### M22：产品打磨 / 稳定性

- 代码清理和重构。
- 测试覆盖率提升。
- 性能优化。
- 文档完善。

### 未来轨道

- 轨道 2：生产部署（认证、HTTPS、Docker、CI/CD）。
- 轨道 3：AI 增强（真实 LLM 集成、fine-tuning、多语言）。
- 轨道 4：平台化（多租户、SaaS、企业版）。
