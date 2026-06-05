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

## M11: Frontend Basic Workflow Page ✅ (current)

- 已完成 frontend Pydantic models。
- 已完成 frontend safety helpers。
- 已完成 frontend context builder。
- 已完成 static page renderer（Jinja2 模板 + CSS/JS）。
- 已完成 CLI 集成（`--write-frontend-page`、`render-page`）。
- 已完成 workflow_result.json 输出。
- 已完成 M11 文档和测试。

## M12: Frontend UI Polish Based on User-Provided Sample Images

- 根据用户提供的样例图片优化视觉风格。
- 保持专业、清晰、适合简历生成工作流。
- **M12 必须在用户提供样例 UI 图片后才能开始。**

## Future Backlog (optional)

- User confirmation workflow before final PDF generation。
- Real JD parser with compliance checks。
- Optional LLM-assisted bullet rewriting after safeguards。
- Production PDF backend installation guide (WeasyPrint)。
