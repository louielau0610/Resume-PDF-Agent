# 项目状态

## Current Milestone

## Current Milestone

M11 Frontend Basic Workflow Page

## M0-M10 已完成

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

## M11 已完成内容

- 添加 frontend Pydantic models：`FrontendPageStatus`、`FrontendArtifactLink`、`FrontendStageView`、`FrontendPageOptions`、`FrontendPageResult`。
- 添加 frontend safety helpers：`escape_frontend_text`、`safe_relative_artifact_path`、`is_allowed_frontend_artifact`。
- 添加 frontend context builder：`build_frontend_page_context`。
- 添加 static page renderer：`render_frontend_workflow_page`、`render_frontend_page_from_output_dir`。
- 添加 Jinja2 模板 `workflow_page.html.j2`（工作流仪表板页面）。
- 添加静态 CSS 和 JS 文件（无外部依赖）。
- CLI 添加 `--write-frontend-page` 选项（`run` 和 `run-sample` 命令）。
- CLI 添加 `render-page` 命令。
- 工作流 orchestrator 添加 `workflow_result.json` 输出。
- 添加 M11 文档和测试。

## 尚未实现内容

- Frontend UI polish based on sample images。
- Word/JPG/PNG export。
- Real LLM integration。
- Real JD ingestion/parsing。
- Browser-based workflow execution。

## 重要产品约束

- 不联网搜索或下载简历模板。
- 不声称知道任何公司的内部简历筛选算法。
- 不调用 LLM API。
- v0 仍然只支持 PDF 导出。
