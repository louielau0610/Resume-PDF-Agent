# Browser JD Upload UI v0

## 概述 / Overview

M21 浏览器岗位描述（JD）上传界面是一张纯静态 HTML 页面，用于帮助用户在运行 CLI 之前准备 JD 文本。该页面：

- 在浏览器中本地运行，无网络请求
- 提供客户端标记检测（机密/内部文档等）
- 生成 jd_text.txt 和 jd_payload.json 供 CLI 使用
- 包含一次性下载和复制按钮
- 不替代后端 M15 合规检查

M21 provides a browser JD intake page. A local static HTML page helps users prepare JD text before running CLI. It includes:

- Client-side marker detection (confidential/internal)
- Generates jd_text.txt and jd_payload.json for CLI
- One-time download and copy buttons
- Does NOT replace backend M15 compliance check

## 何时使用 / When to Use

- 用户希望在与后端交互前审查 JD 内容
- 用户希望生成正确的 CLI 输入文件
- 用户需要了解哪些 JD 类型不被支持

- Users want to review JD content before backend interaction
- Users want to generate correct CLI input files
- Users need to understand which JD types are unsupported

## 渲染 / Rendering

```
py -m resume_pdf_agent render-jd-upload-ui --output outputs/jd_upload_ui/jd_upload.html
```

## 安全 / Safety

- 页面完全是本地的；不向任何服务器提交数据
- 包含合规提示，但后端 M15 检查是权威的
- 页面不预测招聘概率
- 页面无法访问内部筛选标准

- Page is entirely local; no data submitted to any server
- Includes compliance hints, but backend M15 check is authoritative
- Page does NOT predict hiring probability
- Page cannot access internal screening standards

## 设计 / Design

### 组件 / Components

- JD Textarea：主 JD 输入区域
- Metadata Row：可选的目标角色和输出目录
- Compliance Hints Panel：客户端标记检测结果
- Artifact Tabs：生成的 jd_text.txt 和 jd_payload.json 预览
- Action Buttons：复制、下载、本地分析
- CLI Instructions：用户在生成工件后的后续步骤

### 样式 / Styling

- 暗色高级 CSS 主题（与 M12/M20 一致）
- 响应式布局（移动端兼容）
- 无外部 CSS/JS 依赖

## 限制 / Limitations

- 客户端合规检查仅检测已知标记；后端 M15 检查是权威的
- 不执行 JD 解析；仍需要 M15 后端步骤
- 无用户认证或会话管理
- 无数据处理

## 相关模块 / Related Modules

- `src/resume_pdf_agent/jd_ui/` — M21 包
- `src/resume_pdf_agent/jd/` — M15 后端 JD 解析器
- `src/resume_pdf_agent/models/jd_ui.py` — M21 数据模型
- `src/resume_pdf_agent/cli.py` — `render-jd-upload-ui` 命令
