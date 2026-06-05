# 工作流集成 (Workflow Integration v0)

## M10 是什么

M10 将 M0 到 M9 的所有确定性模块串联为一个可用的本地工作流，提供程序化 API 和 CLI 两种使用方式。

## 为什么用 CLI + 程序化 API 而不是前端 UI

- M10 的目标是确保后端模块正确串联，能够端到端运行。
- CLI 和程序化 API 便于自动化测试、CI 集成和脚本化使用。
- 前端 UI 从 M11 开始实现，M12 根据用户提供的样例图做 UI polish。
- M10 不实现前端 UI。

## 端到端确定性工作流阶段

1. **User Intake**：验证工作流输入。
2. **Criteria Selection**：根据 `target_role` 或指定 `criteria_profile_id` 选择 criteria profile。
3. **Resume Type Classification**：使用 M3 分类器确定简历类型。
4. **Gap Analysis**：使用 M4 引擎分析用户证据与角色 criteria 的差距。
5. **Truthfulness Check**：使用 M5 检查简历内容的真实性和不支持声明。
6. **Criteria-Aware Content Enhancement**：使用 M6 生成增强的 bullet candidates。
7. **Internal Template Matching**：使用 M7 选择最佳内部模板。
8. **HTML Rendering**：使用 M8 渲染 HTML 简历。
9. **PDF Generation**：使用 M9 将 HTML 转换为 PDF（测试用 mock backend）。
10. **Artifact Writing**：收集所有输出 artifacts。
11. **Reminder Panel**：添加格式转换提醒（仅元数据，不写入简历正文）。

## CLI 命令

### run-sample

```bash
py -m resume_pdf_agent run-sample --output-dir outputs/sample_run --pdf-backend mock
```

使用内置示例数据运行完整工作流。

### run

```bash
py -m resume_pdf_agent run --input data/sample_inputs/sample_data_science_user.json -o outputs/custom_run
```

从指定 JSON 文件加载输入并运行工作流。

### list-criteria

```bash
py -m resume_pdf_agent list-criteria
```

列出所有可用的 criteria profile ID。

### list-templates

```bash
py -m resume_pdf_agent list-templates
```

列出所有可用的内部模板 ID。

## 输入 JSON 结构

```json
{
  "user_profile": { ... },
  "resume_content": { ... },
  "target_role": "Data Science Intern",
  "criteria_profile_id": null,
  "output_dir": "outputs/sample_run",
  "pdf_backend": "mock",
  "include_preview_reminder_panel": false,
  "write_intermediate_json": true
}
```

必填字段：`user_profile`、`resume_content`。
可选字段：`target_role`、`criteria_profile_id`、`output_dir`、`pdf_backend`、`include_preview_reminder_panel`、`write_intermediate_json`。

## 输出 Artifacts

当 `write_intermediate_json` 为 `true` 时，输出目录包含：

- `criteria_profile.json`：选中的 criteria profile
- `classification.json`：简历类型分类结果
- `gap_analysis.json`：gap 分析结果
- `truthfulness.json`：真实性检查结果
- `enhancement.json`：bullet 增强结果
- `template_selection.json`：模板选择结果
- `resume.html`：渲染后的 HTML 简历
- `resume.pdf`：生成的 PDF 简历（mock backend 生成最小有效 PDF）

## 为什么测试使用 Mock PDF Backend

- Mock backend 生成最小有效 PDF（含 `%PDF` header），确保测试确定性和不依赖系统级 PDF 渲染库（如 WeasyPrint）。
- 当用户安装了 WeasyPrint 后，可通过 `--pdf-backend weasyprint` 使用生产级 PDF 渲染。

## 如何后续使用 WeasyPrint

```bash
pip install weasyprint
py -m resume_pdf_agent run-sample --output-dir outputs/sample_run --pdf-backend weasyprint
```

## 为什么不实现 Word/JPG/PNG Export

- v0 只支持 PDF 导出。
- 如果用户需要 Word/JPG/PNG，系统在 result metadata 中提供中性的转换提醒（不写入简历正文）。

## 为什么转换提醒是元数据而不是简历正文内容

- 转换提醒是给用户的提示，不应该出现在简历的视觉内容中。
- 它仅作为 `conversion_reminder` 字段出现在 `ResumeWorkflowResult` 中。

## 为什么不实现前端 UI

- 前端 UI 从 M11 开始实现。
- M10 专注于后端模块的正确串联。

## 为什么不基于样例图做 UI Polish

- UI polish 从 M12 开始，在用户提供样例图片后实现。

## 已知限制

- 不调用 LLM API。
- 不实现联网搜索或模板下载。
- 不实现 Word/JPG/PNG 导出。
- 不实现前端 UI。
- 不声称提高录用概率。
- 不声称知道任何公司的内部筛选标准。

## 未来改进

- API/Web 集成（如后续需要）。
- M11：前端基础工作流页面。
- M12：基于用户提供的样例图做 UI polish。
- 用户确认工作流（生成 PDF 前确认）。
- Real JD parser with compliance checks。
- Optional LLM-assisted bullet rewriting after safeguards。
- Production PDF backend installation guide。
