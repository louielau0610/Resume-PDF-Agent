# resume_pdf_agent

`resume_pdf_agent` 是一个 criteria-aware 的 AI 简历 PDF 生成 Agent。当前系统已经具备用户画像 schema、静态 criteria knowledge base、简历类型分类、gap analysis、truthfulness checking、bullet enhancement、内部 template metadata matching、HTML resume rendering，以及 M9 的 PDF Generation Pipeline v0。

## 当前 M10 阶段

M10 添加 CLI / Programmatic Workflow Integration：将 M0-M9 所有确定性模块串联为可用的本地工作流。

M10 提供：

- **程序化 API**：`resume_pdf_agent.workflow.run_resume_workflow` 函数，一站式运行端到端工作流。
- **CLI 入口**：基于 Typer 的命令行工具，支持 `run-sample`、`run`、`list-criteria`、`list-templates` 四个命令。
- **结构化中间输出**：可按需输出 criteria profile、classification、gap analysis、truthfulness、enhancement、template selection 的 JSON artifact。
- **最终输出**：`resume.html` 和 `resume.pdf`（测试/示例运行使用 mock PDF backend）。
- **确定性示例工作流**：内置 `data/sample_inputs/sample_data_science_user.json`。

M10 不实现 frontend UI、不做 UI polish、不调用 LLM API、不搜索在线模板、不实现 Word/JPG/PNG export。

## Windows 示例命令

```bash
py -m resume_pdf_agent run-sample --output-dir outputs/sample_run --pdf-backend mock
py -m resume_pdf_agent run --input data/sample_inputs/sample_data_science_user.json -o outputs/custom_run
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
