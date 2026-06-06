# 浏览器确认页面 (Browser-based Confirmation UI v0)

> 中文优先 | Chinese-first

## 概述

M20 添加了**本地静态浏览器确认审核页面**。它读取 M14 生成的 `confirmation_packet.json`，渲染为可在浏览器中打开的 `confirmation.html`，帮助用户审查确认项并准备决策 JSON 文件。

## 为什么是本地静态页面

- 不需要服务器
- 不提交数据到任何地方
- 不独立验证真实世界事实
- 完全离线可用

## 功能

- 按优先级分组显示确认项（blocking/high/medium/low）
- 每个确认项显示完整详情
- 浏览器端决策选择（approve/reject/needs_editing/provide_evidence/ignore_for_now）
- 自动生成 `confirmation_decisions.json`
- 复制到剪贴板 / 下载 JSON 文件
- 安全提示：仅批准您能亲自验证的声明

## CLI 使用

### 通过工作流生成

```bash
py -m resume_pdf_agent run-sample --output-dir outputs/confirm_ui_demo --pdf-backend mock --write-confirmation-packet --write-confirmation-ui --write-frontend-page
```

### 从已有 packet 渲染

```bash
py -m resume_pdf_agent render-confirmation-ui --packet outputs/confirm_ui_demo/confirmation_packet.json --output outputs/confirm_ui_demo/confirmation.html
```

### 加载决策文件

```bash
py -m resume_pdf_agent run-sample --output-dir outputs/confirm_ui_decided --pdf-backend mock --confirmation-decisions path/to/confirmation_decisions.json
```

## 安全声明

- 本地静态页面，不提交数据到服务器
- 不独立验证真实世界事实
- 不预测录用概率或面试结果
- 不声称知道内部筛选标准
- 不绕过 M14 确认门控

## 已知限制

- 本地静态页面，无服务器持久化
- 无数据库/认证
- 决策需手动保存和加载
- 不自动修改简历内容
