# resume_pdf_agent

`resume_pdf_agent` 是一个 criteria-aware 的 AI 简历 PDF 生成 Agent。当前系统已经具备用户画像 schema、静态 criteria knowledge base、简历类型分类、gap analysis、truthfulness checking、bullet enhancement、内部 template metadata matching、HTML resume rendering，以及 M9 的 PDF Generation Pipeline v0。

## 当前 M11 阶段

M11 添加 Frontend Basic Workflow Page v0：生成静态 `index.html` 工作流仪表板页面。

M11 提供：

- **静态仪表板页面**：可视化展示工作流状态、阶段时间线、警告/错误、artifact 链接。
- **简历输出链接**：`resume.html` 和 `resume.pdf` 的直接链接。
- **格式转换提醒**：在仪表板区域显示，不写入简历正文。
- **不依赖 Web 服务器**：HTML 页面可直接在浏览器打开。

M11 不实现 React/FastAPI、不做 UI polish、不调用 LLM API、不运行 Web 服务器。

## Windows 示例命令

```bash
# 运行工作流并生成前端页面
py -m resume_pdf_agent run-sample --output-dir outputs/sample_page --pdf-backend mock --write-frontend-page

# 生成前端页面（自动运行工作流）
py -m resume_pdf_agent render-page --input data/sample_inputs/sample_data_science_user.json -o outputs/page_run

# 查看其他命令
py -m resume_pdf_agent run-sample --output-dir outputs/sample_run --pdf-backend mock
py -m resume_pdf_agent list-criteria
py -m resume_pdf_agent list-templates
```

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
