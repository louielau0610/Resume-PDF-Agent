# 项目状态

## Current Milestone

M19 Optional Web App / API Layer ✅

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
