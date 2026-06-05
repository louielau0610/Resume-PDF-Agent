# 项目状态

## Current Milestone

## Current Milestone

M12 Frontend UI Polish

## M0-M11 已完成

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

## M12 已完成内容

- CSS 全面重写为 cinematic dark 主题（CSS 变量、径向渐变背景、大圆角卡片）。
- HTML 模板重构为语义化布局：`app-shell`、`hero-panel`、`metric-grid`、`section-panel`、`stage-timeline`、`footer-note`。
- Context builder 添加 `status_label`、`stages_completed`/`stages_total`、display-friendly 名称。
- 不改变工作流逻辑、PDF 生成逻辑、HTML 渲染逻辑。
- 无外部依赖：无 CDN、无字体、无图片、无图标库。
- 添加 M12 文档。

## 尚未实现内容

- Word/JPG/PNG export。
- Real LLM integration。
- Real JD ingestion/parsing。
- Browser-based workflow execution。
- Production web app。

## 重要产品约束

- 不联网搜索或下载简历模板。
- 不声称知道任何公司的内部简历筛选算法。
- 不调用 LLM API。
- v0 仍然只支持 PDF 导出。
