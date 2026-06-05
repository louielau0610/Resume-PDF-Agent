# TODO

## M1-M9 Completed

- M1：Core schemas。
- M2：Static criteria knowledge base v0。
- M3：Resume type classifier。
- M4：Criteria-based gap analysis engine。
- M5：Truthfulness and unsupported-claim checker。
- M6：Criteria-aware bullet enhancement engine。
- M7：Internal template metadata matching。
- M8：HTML resume rendering。
- M9：PDF generation pipeline。

## M10: CLI/API Workflow Integration ✅ (current)

- 已完成 workflow Pydantic models。
- 已完成 serialization 和 I/O helpers。
- 已完成 `run_resume_workflow` orchestrator。
- 已完成 Typer CLI（`run-sample`、`run`、`list-criteria`、`list-templates`）。
- 已完成 `__main__.py`。
- 已完成示例输入 JSON。
- 已完成 M10 文档和测试。

## M11: Frontend Basic Workflow Page

- 建立基础前端工作流页面。
- 支持用户输入和结果下载入口。

## M12: Frontend UI Polish Based on User-Provided Sample Images

- 根据用户提供的样例图片优化视觉风格。
- 保持专业、清晰、适合简历生成工作流。

## Future Backlog (optional)

- User confirmation workflow before final PDF generation。
- Real JD parser with compliance checks。
- Optional LLM-assisted bullet rewriting after safeguards。
- Production PDF backend installation guide (WeasyPrint)。
