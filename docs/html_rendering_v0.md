# HTML Rendering v0

## 概述

M8 添加 deterministic HTML Resume Rendering v0。它把结构化简历数据渲染为干净、ATS-friendly、可作为后续 PDF generation 输入的 HTML。

M8 只负责 HTML，不生成 PDF，不实现 frontend UI，不做样例图驱动的 UI polish，不调用 LLM API，也不联网搜索或下载模板。

## 输入

- `UserProfile`：用户姓名、联系方式、教育、技能、语言、奖项等公开简历信息。
- `ResumeContent`：结构化 experience、resume sections 和带 evidence metadata 的 bullets。
- `TemplateSelectionResult`：M7 选择出的内部 template metadata，用于决定 template id 和 section 顺序。
- `BulletEnhancementResult | None`：M6 的可选 bullet enhancement 输出。
- `HTMLRenderOptions`：控制是否内联 CSS、是否显示 preview reminder panel、是否显示 truthfulness warnings、ATS-friendly mode、section item 上限和语言。

## 输出

`HTMLRenderResult` 包含：

- `status`：`rendered`、`rendered_with_warnings` 或 skip 状态。
- `template_id`：实际使用的 template id；缺失 template file 时会 fallback 到 `ats_student_basic`。
- `html`：渲染后的 HTML 字符串。
- `css`：内联 CSS 内容，或在关闭 `include_css` 时为 `None`。
- `sections_rendered`：实际有内容的 section id。
- `warnings`：confirmation、risk flags、template fallback 等渲染提醒。
- `output_path`：调用 `write_rendered_html` 后写入的本地路径。
- `summary`：渲染摘要。

## Render Context

`build_resume_render_context` 会构造公开渲染上下文：

- full name
- contact lines
- selected template id
- template display name
- sections
- warnings
- preview reminder panel text

它不会暴露隐藏内部数据，不会加入 hiring probability，也不会声称知道公司内部筛选规则。

## Template Metadata 如何影响 Section 顺序

M8 使用 `TemplateSelectionResult.selected_template.sections` 中的 metadata 顺序构造 section。每个 template section 的 `section_id`、`heading`、`required` 和 `max_items` 会影响输出。

渲染器只渲染有内容的 section；required section 可以进入 render context，但真实 HTML body 只输出有 items 的 section，避免生成空的视觉内容。

## Enhanced Bullets 的使用方式

当 `BulletEnhancementResult` 存在时，M8 会优先选择 safe enhanced bullet candidates：

- candidate status 必须是 `enhanced` 或 `unchanged`。
- high-risk flags 会阻止 candidate 进入 resume body。
- 需要用户确认的 enhanced candidate 默认不作为 safe candidate 使用。

如果没有可用 enhanced bullet，M8 会回退到 `ResumeContent.sections` 中的 bullets；如果仍没有 bullets，则使用 `ExperienceEntry` 中用户提供的 title、organization、responsibilities、tools、methods 或 outcomes 形成保守条目。

## Unsafe 或 Confirmation-needed 内容

M8 不会静默吞掉风险状态。`needs_confirmation` 或 `risk_flags` 会被收集到 `HTMLRenderResult.warnings`，并且在 `include_truthfulness_warnings=True` 时显示在 preview wrapper 的 warning 区域。

用户提供的 HTML/script 会被转义，不会作为 raw HTML 插入。

## 为什么 M8 不生成 PDF

PDF generation 是 M9 的范围。M8 只提供稳定的 HTML 输入，便于后续选择 PDF engine、page sizing、print validation 和 export workflow。

## 为什么 M8 不实现 Frontend UI

Frontend basic workflow page 是 M11 的范围。M8 的目标是 backend rendering foundation，不包含浏览器交互、表单、下载按钮或前端状态管理。

## 为什么 M8 不做样例图 UI Polish

样例图驱动的 UI polish 是 M12 的范围，并且需要用户提供 sample images。M8 的模板只做干净、保守、ATS-friendly 的 HTML，不模仿任何视觉样例。

## Reminder Panel 的位置

PDF/Word/JPG/PNG reminder 默认不嵌入真实简历正文。只有 `include_preview_reminder_panel=True` 时，提醒才会出现在 preview wrapper 中，并位于 `#resume-document` 外部。

提醒文本为：

> Current v0 output is designed for PDF generation. If you need Word, JPG, or PNG later, use an external PDF conversion tool after PDF export.

## 已知限制

- M8 不做 PDF page break 质量验证。
- M8 不实现最终 pipeline 串联。
- M8 不解析真实 JD。
- M8 不调用 LLM。
- M8 不做前端 UI。
- M8 不输出 Word/JPG/PNG。
- v0 templates 的差异主要是 metadata-driven section order 和轻量 class name，未做复杂视觉设计。

## Future Improvements

- M9：PDF generation pipeline。
- M10：CLI/API workflow integration。
- M11：Frontend basic workflow page。
- M12：sample-image-based frontend UI polish。
