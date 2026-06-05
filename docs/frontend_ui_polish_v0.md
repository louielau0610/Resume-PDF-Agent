# 前端 UI 精修 (Frontend UI Polish v0)

## M12 是什么

M12 在 M11 静态工作流仪表板基础上进行 UI 精修，采用用户提供的视觉参考风格，将页面从基础布局升级为 cinematic dark 风格的高级仪表板。

## 用户提供的参考风格

- **暗色电影感背景**：黑色/深灰/炭灰色 canvas
- **大圆角卡片布局**：hero panel、metric grid、section panel
- **极简排版**：系统字体、大写标签、稀疏高对比度文字
- **低饱和度强调色**：蓝灰/银灰/软青色点缀
- **安静的高级氛围**：非彩色 SaaS dashboard 风格
- **无外部图片/CDN/字体依赖**

## M12 为什么不做完美视觉复制

- 用户明确表示：结果不需要完美匹配参考图片。
- 稳定性优先于精确视觉模仿。
- CSS 纯文本实现，无外部资源加载。
- 不依赖 GPU 加速或复杂动画。

## M12 相对于 M11 的变化

### 模板结构
- 从 `wf-*` 前缀改为语义化类名：`app-shell`、`hero-panel`、`metric-grid`、`section-panel`、`stage-timeline`、`footer-note`
- 新增 top bar 状态指示器
- Hero panel 整合了 criteria profile / resume type / template / output directory
- 新增 metric grid（stages 完成数、warnings 数、errors 数、artifacts 数）
- Input summary 改用 grid 布局
- Stage timeline 重新设计为圆点 + 标签样式
- Artifact links 改为卡片按钮网格布局
- Resume outputs 改为大圆角按钮
- 整体采用 dark theme

### CSS
- 全面重写为暗色主题
- 使用 CSS 变量管理颜色
- 添加径向渐变背景（纯 CSS，无图片）
- 所有卡片圆角增大
- 状态颜色映射到暗色调
- Pills/tags 替代旧 badges
- 响应式和打印回退保留

### Context
- 新增 `status_label`：人类可读状态标签
- 新增 `stages_completed` / `stages_total`：阶段进度
- 新增 `primary_resume_type_display`：格式化的简历类型显示
- 新增 `selected_template_id_display`：格式化的模板 ID 显示

## 未发生变化的部分

- **工作流逻辑**：完全没有改动
- **PDF 生成逻辑**：完全没有改动
- **Resume HTML 渲染逻辑**：完全没有改动
- **CLI 命令**：`run-sample --write-frontend-page`、`render-page` 保持不变
- **不引入 React/FastAPI/web server**
- **不引入 Word/JPG/PNG export**
- **不调用 LLM API**
- **转换提醒仍在简历正文之外**

## 生成精修仪表板

```bash
py -m resume_pdf_agent run-sample --output-dir outputs/sample_page --pdf-backend mock --write-frontend-page
```

然后在浏览器中打开 `outputs/sample_page/index.html`。

## 已知限制

- 纯静态 HTML，无 Web 服务器
- 无外部字体/图片/CDN
- 无 React/FastAPI/Streamlit
- 不执行浏览器端工作流
- 不做 Word/JPG/PNG 导出

## 未来改进

- 可选用户选择主题
- 可选更丰富的仪表板预览
- 可选生产环境前端
