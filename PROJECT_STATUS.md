# 项目状态

## Current Milestone

M9 PDF Generation Pipeline

## M0-M8 已完成

- M0：项目基础结构、配置、异常、占位 pipeline 和基础测试。
- M1：用户画像、简历内容、criteria、analysis 和真实性 safeguard schemas。
- M2：静态 criteria knowledge base v0、loader 和 selector。
- M3：deterministic resume type classifier。
- M4：criteria-based gap analysis engine。
- M5：truthfulness and unsupported-claim checker。
- M6：criteria-aware bullet enhancement engine。
- M7：internal template metadata matching。
- M8：HTML resume rendering。

## M9 已完成内容

- 添加 PDF generation schemas：`PDFGenerationOptions`、`PDFGenerationResult`、backend/status/page format enums。
- 添加 PDF options helpers 和 conversion reminder metadata。
- 添加 PDF output validation：文件存在、非空、`%PDF` header。
- 添加 backend availability checks。
- 添加 WeasyPrint adapter 入口；当前环境未安装 WeasyPrint 时会返回 backend unavailable。
- 添加 deterministic mock backend 用于测试。
- 添加从 `HTMLRenderResult` 生成 PDF 的函数。
- 添加从 `UserProfile` + `ResumeContent` + `TemplateSelectionResult` 调用 M8 renderer 后生成 PDF 的函数。
- 添加 M9 文档和测试。

## 尚未实现内容

- CLI/API workflow integration。
- Frontend UI。
- Frontend UI polish based on sample images。
- Word/JPG/PNG export。

## 重要产品约束

- 不联网搜索或下载简历模板。
- 不声称知道任何公司的内部简历筛选算法。
- 不调用 LLM API。
- M9 只从 M8 HTML 输出生成 PDF，不重写简历内容。
- v0 仍然只支持 PDF 导出。
