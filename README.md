# resume_pdf_agent

`resume_pdf_agent` 是一个 criteria-aware 的 AI 简历 PDF 生成 Agent。当前系统已经具备用户画像 schema、静态 criteria knowledge base、简历类型分类、gap analysis、truthfulness checking、bullet enhancement、内部 template metadata matching、HTML resume rendering，以及 M9 的 PDF Generation Pipeline v0。

## 当前 M9 阶段

M9 添加 PDF Generation Pipeline v0：把 M8 渲染出的 HTML 转换成本地 PDF 文件，并返回结构化 `PDFGenerationResult`。

M9 的 PDF pipeline 会：

- 接收已有的 `HTMLRenderResult` 并生成 PDF。
- 或从 `UserProfile`、`ResumeContent`、`TemplateSelectionResult` 直接调用 M8 renderer 后生成 PDF。
- 使用 backend adapter 设计，默认偏好 WeasyPrint；如果 backend 不可用，会返回清晰的 skipped/failed 状态。
- 在测试中支持 deterministic mock backend，避免依赖系统级 PDF 渲染环境。
- 校验输出 PDF 文件存在、非空，并检查 `%PDF` header。
- 保留 HTML rendering warnings 和 PDF generation warnings。
- 在 result metadata 中提供中性的转换提醒：如果需要 Word/JPG/PNG，可在 PDF export 后使用外部 PDF conversion tool。

M9 只导出 PDF。它不实现 Word/JPG/PNG export，不实现 frontend UI，不做基于样例图的 UI polish，不调用 LLM API，不联网搜索或下载模板，也不声称知道任何公司的内部筛选标准。

## 已支持的内部模板 metadata

- ATS student basic
- Data science technical
- Software engineering technical
- Finance business
- Consulting business
- Research CV
- Product manager
- Design portfolio light

## 后续 Milestones

- M10：CLI or API workflow integration。
- M11：Frontend basic workflow page。
- M12：Frontend UI polish based on user-provided sample images。

## 验证命令

Windows:

```bash
py -m compileall src tests
py -m pytest -q
```

macOS 或 Linux:

```bash
python -m compileall src tests
pytest -q
```
