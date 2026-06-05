# 项目状态

## Current Milestone

M10 CLI/API Workflow Integration

## M0-M9 已完成

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

## M10 已完成内容

- 添加 workflow Pydantic models：`WorkflowStageName`、`WorkflowStageStatus`、`WorkflowRunStatus`、`WorkflowArtifact`、`WorkflowStageResult`、`ResumeWorkflowInput`、`ResumeWorkflowResult`。
- 添加 workflow serialization 和 I/O helpers。
- 添加 `run_resume_workflow` orchestrator：串联 criteria selection、classification、gap analysis、truthfulness、enhancement、template matching、HTML rendering、PDF generation。
- 添加 Typer CLI：`run-sample`、`run`、`list-criteria`、`list-templates`。
- 添加 `__main__.py` 支持 `py -m resume_pdf_agent`。
- 添加示例输入 JSON：`data/sample_inputs/sample_data_science_user.json`。
- 添加 M10 文档和测试。

## 尚未实现内容

- Frontend UI。
- Frontend UI polish based on sample images。
- Word/JPG/PNG export。
- Real LLM integration。
- Real JD ingestion/parsing。

## 重要产品约束

- 不联网搜索或下载简历模板。
- 不声称知道任何公司的内部简历筛选算法。
- 不调用 LLM API。
- v0 仍然只支持 PDF 导出。
