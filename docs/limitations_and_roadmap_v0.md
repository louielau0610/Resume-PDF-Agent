# 限制与路线图 (Limitations & Roadmap v0)

## 当前限制

### 知识库限制

- **静态 criteria 知识库**：当前使用手动整理的 6 个角色 profile（data_science_intern, software_engineering_intern, product_manager_intern, finance_intern, consulting_intern, research_assistant），而非实时 JD 解析。
- **无真实 JD 解析**：不支持从用户上传的岗位描述中自动提取 criteria。
- **无在线数据**：不联网搜索或获取最新招聘信息。

### 引擎限制

- **无 LLM 调用**：所有模块（分类、gap 分析、真实性检查、bullet 增强）使用确定性规则，不使用 GPT-4、Claude、Gemini 等模型。
- **规则引擎 v0**：分类关键词、匹配规则和增强策略是硬编码的，可能无法覆盖所有边缘情况。
- **静态模板集**：8 个内部模板，不支持自定义模板上传。

### 输出限制

- **仅 PDF 导出**：不支持 Word (.docx)、JPG、PNG 导出。
- **Mock PDF backend**：测试和演示使用 mock backend，生成最小有效 PDF。生产环境需要安装 WeasyPrint。
- **静态前端仪表板**：`index.html` 是离线静态页面，不能自动刷新或执行后端工作流。

### 交互限制

- **无用户确认工作流**：生成 PDF 前不提供确认/编辑步骤。
- **无浏览器端工作流执行**：所有计算在 Python 后端完成。
- **无 Web 应用**：不提供 FastAPI/Flask/Streamlit 等 Web 服务。

### 测试限制

- **无可视回归测试**：不自动化比对 PDF/HTML 的渲染截图。
- **无性能基准测试**：未测试大数据量或高并发场景。

## 路线图 (Roadmap)

以下里程碑是**路线图想法**，尚未实现：

### M14: User Confirmation Workflow

- 在 PDF 生成前提供用户确认步骤。
- 允许用户查看、编辑和批准增强后的 bullet。
- 支持逐条确认需要用户确认的 claims。

### M15: Real JD Parser with Compliance Checks

- 支持用户上传真实岗位描述（文本/PDF/URL）。
- 从 JD 中提取结构化 criteria。
- 添加合规检查，确保不违反招聘平台使用条款。

### M16: Optional LLM-Assisted Rewriting After Safeguards

- 在证据充足、风险可控的前提下，提供可选的 LLM 辅助 bullet 改写。
- 改写前后都运行真实性检查。
- 用户可选择不启用 LLM 功能。

### M17: Production PDF Backend Setup Guide

- WeasyPrint 安装和配置指南（Windows/macOS/Linux）。
- 生产环境 PDF 渲染质量建议。
- 字体嵌入和中英文混排最佳实践。

### M18: Visual Regression Testing

- 自动化 PDF 渲染截图比对。
- HTML 输出结构回归测试。
- 仪表板页面视觉一致性检查。

### M19: Optional Web App / API Layer

- 如需要，提供 FastAPI 后端和简单前端。
- RESTful API 接口。
- 用户会话管理和历史记录。

---

**注意**：M14-M19 是路线图想法，不在当前 v0 实现范围内。实现顺序和范围可能根据实际需求调整。
