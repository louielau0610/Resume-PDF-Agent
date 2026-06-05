# TODO

## M0-M14 Completed ✅

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
- M14：User Confirmation Workflow ✅（当前）。

## M14: User Confirmation Workflow ✅ (current)

- 已完成 `models/confirmation.py`：确认工作流 Pydantic 模型。
- 已完成 `confirmation/packet.py`：从 truthfulness、enhancement、gap analysis、resume bullets 收集确认项。
- 已完成 `confirmation/decisions.py`：加载并应用用户决策。
- 已完成 `confirmation/markdown.py`：生成中文确认审核文档。
- 已完成 `confirmation/gate.py`：确认门控判断。
- 已集成到工作流编排器和 CLI。
- 已完成 7 个测试文件和文档。
- 未改变核心工作流逻辑（向后兼容）。
- 未添加 LLM 调用、JD 解析、Word/JPG/PNG 导出、Web 应用。

## Future Roadmap（路线图想法，尚未实现）

- 已完成 5 个核心文档：demo_walkthrough、architecture_diagram、github_project_overview、release_checklist、limitations_and_roadmap。
- 已完成 examples/ 目录：README + sample_data_science_demo。
- 已完成 scripts/：run_demo_workflow.py + validate_release_readiness.py。
- 已完成 tests/：test_release_readiness_docs.py + test_demo_script.py。
- 已更新 README.md、README.en.md、PROJECT_STATUS.md、TODO.md。
- 未改变核心工作流逻辑。
- 未添加 LLM 调用、JD 解析、Word/JPG/PNG 导出、Web 应用。

## Future Roadmap（路线图想法，尚未实现）

### M14: User Confirmation Workflow

- 在 PDF 生成前提供用户确认步骤。
- 允许用户查看、编辑和批准增强后的 bullet。
- 支持逐条确认需要用户确认的 claims。

### M15: Real JD Parser with Compliance Checks

- 支持用户上传真实岗位描述（文本/PDF/URL）。
- 从 JD 中提取结构化 criteria。
- 添加合规检查，确保不违反招聘平台使用条款。

### M16: Optional LLM-Assisted Rewriting After Safeguards

- 在证据充足、风险可控的前提下，提供可选的 LLM 辅助 bullet 改写。
- 改写前后都运行真实性检查。
- 用户可选择不启用 LLM 功能。

### M17: Production PDF Backend Setup Guide

- WeasyPrint 安装和配置指南（Windows/macOS/Linux）。
- 生产环境 PDF 渲染质量建议。
- 字体嵌入和中英文混排最佳实践。

### M18: Visual Regression Testing

- 自动化 PDF 渲染截图比对。
- HTML 输出结构回归测试。
- 仪表板页面视觉一致性检查。

### M19: Optional Web App / API Layer

- 如需要，提供 FastAPI 后端和简单前端。
- RESTful API 接口。
- 用户会话管理和历史记录。
