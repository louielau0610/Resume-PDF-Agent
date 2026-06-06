# 视觉回归测试 (Visual Regression Testing v0)

> 中文优先 | Chinese-first

## 概述

M18 添加了**确定性视觉/结构回归检查**，确保未来代码更改不会意外破坏：

- 前端仪表板 HTML 结构（M12 的 cinematic dark 主题）
- 简历 HTML 结构（M8）
- 输出产物完整性（PDF header、文件存在）
- 安全内容检查（无脚本注入、无 CDN 外链等）

## 为什么需要回归检查

随着项目模块增多（目前已 17+ 个模块），前端模板、渲染逻辑和 PDF 生成的改动可能引入难以察觉的回归。M18 提供自动化结构级验证。

## 检查类型

| 检查类型 | 说明 | 是否需要浏览器 |
|----------|------|--------------|
| Dashboard HTML 结构 | 验证 app-shell、hero-panel、metric-grid 等 M12 CSS 类 | ❌ 不需要 |
| Resume HTML 结构 | 验证 DOCTYPE、body 内容、无 dashboard 类污染 | ❌ 不需要 |
| 安全内容检查 | 检测 script 注入、CDN 外链、禁用声明 | ❌ 不需要 |
| PDF 产物验证 | 文件存在、非空、%PDF header | ❌ 不需要 |
| 快照归一化 | HTML 文本清洗和时间戳替换 | ❌ 不需要 |
| 截图诊断 | 可选的 Playwright 截图 | ✅ 需要 Playwright |

## 运行回归检查

```bash
# 基础检查（不需要浏览器）
py scripts/run_visual_regression_checks.py --output-dir outputs/visual_regression_check

# 包含截图（需要 Playwright）
py scripts/run_visual_regression_checks.py --output-dir outputs/vr_screenshot_check --capture-screenshots
```

## 已知限制

- 不执行像素级图像对比
- 不保证跨浏览器/OS 的渲染一致性
- Mock PDF 足以用于回归测试
- 截图功能需要 Playwright（可选）
- 无 Word/JPG/PNG 导出

## 未来改进

- 像素级截图 diff 工具
- 跨版本快照对比
- CI/CD 集成（GitHub Actions）
