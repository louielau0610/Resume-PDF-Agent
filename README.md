# resume_pdf_agent

`resume_pdf_agent` 是一个 criteria-aware 的 AI 简历 PDF 生成 Agent。当前系统已经具备用户画像 schema、静态 criteria knowledge base、简历类型分类、gap analysis、truthfulness checking、bullet enhancement、内部 template metadata matching、HTML resume rendering，以及 M9 的 PDF Generation Pipeline v0。

## 当前 M12 阶段

M12 添加 Frontend UI Polish：将静态工作流仪表板从基础布局升级为 cinematic dark 风格的高级仪表板。

M12 提供：

- **暗色电影感仪表板**：黑色/深灰背景，大圆角卡片，低饱和度强调色
- **语义化布局**：app-shell、hero-panel、metric-grid、stage-timeline
- **纯 CSS 实现**：无外部图片/字体/CDN 依赖
- **保持所有 M11 功能**：工作流状态、阶段时间线、警告/错误、artifact 链接
- **不改变任何后端逻辑**：工作流、PDF 生成、HTML 渲染均不受影响

M12 不实现 React/FastAPI、不做 Word/JPG/PNG export、不调用 LLM API。

## Windows 示例命令

```bash
# 运行工作流并生成精修前端页面
py -m resume_pdf_agent run-sample --output-dir outputs/sample_page --pdf-backend mock --write-frontend-page

# 在浏览器中查看
# 打开 outputs/sample_page/index.html
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

无。M12 是当前最新 milestone。

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
