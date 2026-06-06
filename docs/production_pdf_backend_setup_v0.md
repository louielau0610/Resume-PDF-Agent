# 生产 PDF Backend 设置指南 (Production PDF Backend Setup v0)

> 中文优先 | Chinese-first

## 概述

M17 添加了 PDF backend 诊断工具和 WeasyPrint 设置验证。帮助用户了解和使用生产级 PDF 生成。

## Mock Backend vs 生产 Backend

| 特性 | Mock Backend | WeasyPrint |
|------|-------------|------------|
| 用途 | 确定性测试 | 生产 PDF 生成 |
| 安装 | 无需 | `pip install weasyprint` |
| 输出 | 最小 PDF-like 字节 | 真实渲染的 PDF |
| 默认 | ✅ 测试默认 | 需显式指定 |
| 系统依赖 | 无 | 可能需要 GTK/Pango 等 |

## 检查 Backend 可用性

```bash
# 检查所有 backend
py -m resume_pdf_agent check-pdf-backend

# 检查指定 backend
py -m resume_pdf_agent check-pdf-backend --backend mock
py -m resume_pdf_agent check-pdf-backend --backend weasyprint

# 运行验证脚本
py scripts/verify_pdf_backend.py --backend all --output-dir outputs/pdf_backend_check
```

## 安装 WeasyPrint

```bash
pip install weasyprint
```

> **注意**：某些系统可能需要额外的原生库（如 GTK、Pango）。
> 请查阅 WeasyPrint 官方文档获取 OS 特定的安装说明：
> https://doc.courtbouillon.org/weasyprint/stable/first_steps.html#installation

> 本项目不捆绑系统依赖。如需帮助，请参考 WeasyPrint 官方文档。

## 使用 WeasyPrint 生成 PDF

安装 WeasyPrint 后：

```bash
py -m resume_pdf_agent run-sample --output-dir outputs/real_pdf_test --pdf-backend weasyprint --write-frontend-page
```

## 使用 Mock Backend（测试默认）

```bash
py -m resume_pdf_agent run-sample --output-dir outputs/sample_mock --pdf-backend mock --write-frontend-page
```

## 诊断输出示例

```
PDF Backend Status Summary
========================================
  mock: AVAILABLE
    Hint: Mock backend requires no installation.
  weasyprint: AVAILABLE (production recommended)
    Hint: WeasyPrint is available and ready for PDF generation.
  playwright: UNAVAILABLE
    Error: Playwright package is not installed.

Default for tests: mock (always available, deterministic)
Recommended for production: weasyprint
```

## 已知限制

- 无 Word/JPG/PNG 导出
- 无可视回归测试
- 不保证跨系统的 PDF 渲染一致性
- Mock backend 不产生真实 PDF 渲染
- Playwright 不是默认生产 backend

## 未来改进

- 可视化回归测试 (M18)
- 可选的 Word/JPG/PNG 导出 (M23)

---

*本指南是 M17 的一部分。WeasyPrint 是可选的，不是项目必需的。*
