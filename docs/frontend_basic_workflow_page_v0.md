# 前端基础工作流页面 (Frontend Basic Workflow Page v0)

## M11 是什么

M11 在 M10 CLI / 程序化工作流之上添加了一个静态前端仪表板页面。
运行工作流后，可生成一个 `index.html` 文件，以可视化方式展示工作流结果。

## 为什么用静态 HTML 而不是 React/FastAPI

- M11 的目标是提供基础结果可视化，不构建交互式 Web 应用。
- 静态 HTML 可以在浏览器中直接打开，无需启动 web 服务器。
- 不引入 React、Vite、FastAPI、Flask 等额外依赖。
- 前端 UI polish 从 M12 开始，在用户提供样例图片后实现。

## 页面显示内容

- **工作流状态**：completed / completed_with_warnings / failed
- **摘要卡片**：选中的 criteria profile、简历类型、模板、输出目录
- **输入摘要**：姓名、目标角色、教育数量、经历数量、技能组数量
- **阶段时间线**：每个工作流阶段的状态、消息、警告数、错误数
- **警告/错误列表**：可折叠展开
- **Artifact 链接**：各阶段 JSON 文件的可点击链接
- **简历输出链接**：resume.html 和 resume.pdf
- **格式转换提醒**：仅在仪表板区域显示，不写入简历正文
- **页脚**：说明 v0 限制

## 从 CLI 生成页面

```bash
# 方式1：run-sample 带 --write-frontend-page
py -m resume_pdf_agent run-sample --output-dir outputs/sample_page --pdf-backend mock --write-frontend-page

# 方式2：render-page 命令（自动运行工作流后生成页面）
py -m resume_pdf_agent render-page --input data/sample_inputs/sample_data_science_user.json -o outputs/page_run
```

## 为什么不在浏览器中执行工作流

- 静态页面仅展示结果，不运行任何后端逻辑。
- 工作流由 Python 后端执行（通过 CLI 或程序化 API）。
- 页面不含任何远程数据获取或 API 调用。

## 为什么不现在做 UI Polish

- M11 是基础功能页面（v0），目标是结构正确而非视觉精美。
- M12 将在用户提供样例 UI 图片后进行针对性 UI polish。
- 当前 CSS 保持简洁可读，无外部依赖。

## 为什么转换提醒在简历正文之外

- 转换提醒是给用户的元数据提示，不应出现在简历的视觉内容中。
- 它仅显示在工作流仪表板页面和 `PDFGenerationResult` 元数据中。

## 为什么不导出 Word/JPG/PNG

- v0 只支持 PDF 导出。
- 格式转换提醒建议用户使用外部 PDF 转换工具。

## 已知限制

- 页面是静态的，不会自动刷新。
- 不包含 React/Vite/FastAPI/Flask/Streamlit。
- 不包含任何 Web 服务器功能。
- 不在浏览器中执行工作流。
- 不做 UI polish。
- 不调用 LLM API。
- 不实现联网搜索或模板下载。

## 未来改进

- M12：基于用户提供的样例图片做 UI polish。
- 可选的客户端状态管理与更丰富的交互。
- 如后续需要，可添加后端 API。
