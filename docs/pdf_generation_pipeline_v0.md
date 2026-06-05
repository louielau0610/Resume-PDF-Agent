# PDF Generation Pipeline v0

## 概述

M9 添加 PDF Generation Pipeline v0。它把 M8 已经生成的 HTML 转换成本地 PDF 文件，并返回结构化 `PDFGenerationResult`。

M9 不重写简历内容，不生成 Word/JPG/PNG，不实现 frontend UI，不做样例图驱动 UI polish，不调用 LLM API，也不联网搜索模板。

## 输入

M9 支持两种入口：

- `generate_pdf_from_html_result(html_render_result, output_path, options)`：从已有 `HTMLRenderResult` 生成 PDF。
- `generate_resume_pdf(user_profile, resume_content, template_selection_result, bullet_enhancement_result, output_path, html_options, pdf_options)`：先调用 M8 `render_resume_html`，再生成 PDF。

输入对象包括：

- `HTMLRenderResult`
- `UserProfile`
- `ResumeContent`
- `TemplateSelectionResult`
- optional `BulletEnhancementResult`
- `PDFGenerationOptions`

## 输出

`PDFGenerationResult` 包含：

- `status`：`generated`、`generated_with_warnings`、`skipped_backend_unavailable` 或 `failed`。
- `backend`：实际请求的 backend。
- `output_path`：成功生成时的本地 PDF 路径。
- `file_size_bytes`：成功生成时的文件大小。
- `page_format`：`A4` 或 `Letter`。
- `warnings`：HTML rendering warnings 和 PDF generation warnings。
- `errors`：backend unavailable、backend failure 或 output validation errors。
- `conversion_reminder`：可选的外部转换提醒。
- `summary`：生成摘要。

## 为什么 PDF Generation 与 HTML Rendering 分离

HTML rendering 负责内容结构、section 顺序、HTML escaping 和 ATS-friendly markup。PDF generation 负责 backend availability、HTML-to-PDF conversion、本地文件写入和输出验证。

分离后，M8 可以独立测试内容安全，M9 可以独立测试 backend 和文件输出。

## Backend Strategy

M9 使用 adapter 设计：

- `weasyprint`：默认偏好的生产 backend。如果环境安装并可 import，则用于 HTML-to-PDF。
- `playwright`：保留 backend 枚举和 availability check；M9 不实现完整 Playwright adapter。
- `mock`：仅用于测试，写入最小 `%PDF` header 文件，不代表生产 PDF rendering。

当前环境未安装 WeasyPrint，因此项目没有在 M9 修改 dependency list。实际部署时可以安装 WeasyPrint 后使用默认 backend。

## Backend Availability

`is_pdf_backend_available` 不会安装任何依赖，也不访问网络。

当 backend 不可用时：

- `fail_on_backend_unavailable=False`：返回 `skipped_backend_unavailable`。
- `fail_on_backend_unavailable=True`：返回 `failed` 并带清晰 error。

M9 不会在没有文件生成时假装 PDF 生成成功。

## 为什么 Tests 使用 Mock Backend

HTML-to-PDF backend 在 Windows 或 CI 中可能依赖额外系统库。mock backend 让接口、路径创建、PDF header validation、warning propagation 和 result metadata 可以 deterministic 测试。

mock backend 输出只用于测试，不是生产 PDF renderer。

## 为什么 M9 不导出 Word/JPG/PNG

v0 只支持 PDF。Word/JPG/PNG export 是明确的 non-goal，避免在 PDF pipeline 中混入额外格式和不稳定转换逻辑。

如果用户之后需要 Word/JPG/PNG，可以在 PDF export 后使用外部 PDF conversion tool。

## Conversion Reminder 的位置

转换提醒属于 `PDFGenerationResult.conversion_reminder` metadata，未来可在 preview UI 中显示。它不会插入真实 resume HTML body，也不会成为 PDF 简历正文内容。

提醒文本：

> Current v0 output is PDF. If you need Word, JPG, or PNG, use an external PDF conversion tool after export.

## 为什么 M9 不实现 Frontend UI

Frontend basic workflow page 是 M11 的范围。M9 只实现 backend PDF generation API。

## 为什么 M9 不做样例图 UI Polish

样例图驱动的 UI polish 是 M12 的范围，并且需要用户提供 sample images。M9 不修改视觉模板，也不模仿样例图。

## 已知限制

- 当前环境未安装 WeasyPrint，默认 backend 在本地测试中会显示 unavailable。
- M9 不做视觉回归检查。
- M9 不检查 PDF page count。
- M9 不实现完整 production pipeline。
- M9 不导出 Word/JPG/PNG。
- Playwright backend 在 M9 仅保留 adapter 入口和 unavailable/failed 行为。

## Future Improvements

- PDF visual regression checks。
- PDF page count inspection。
- M10：CLI/API integration。
- M11：frontend basic page。
- M12：sample-image-based UI polish。
- 仅在未来明确加入时，才考虑 optional Word/JPG/PNG export。
