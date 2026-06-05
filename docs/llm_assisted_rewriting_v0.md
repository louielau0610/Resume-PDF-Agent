# LLM 辅助改写 (LLM-assisted Rewriting v0)

> 中文优先 | Chinese-first

## 概述

M16 添加了**可选的 LLM 辅助改写层**。在确定性 M6 bullet enhancement 和 M5/M14 安全门控之后，用户可以选择性地使用 LLM（语言模型）对简历 bullet 进行措辞润色。

**重要**：LLM 改写默认禁用，不会自动应用到最终简历。

## 为什么默认禁用

- LLM 输出可能引入幻觉（hallucination）
- 安全优先：所有 LLM 输出必须经过验证
- 用户控制：改写结果仅供审阅，不会自动替换原始内容
- 成本考虑：使用真实 LLM API 需要 API key 和网络

## 安全机制

### 输入门控

改写前检查：
- ✅ 真实性检查必须通过（无 HIGH 风险）
- ✅ 确认包不能有阻塞项（如果启用）
- ❌ 不满足条件 → 跳过改写

### 输出验证

LLM 生成的文本经过严格验证：
1. 不添加新的数字/百分比指标
2. 不添加新工具名称
3. 不添加新方法/框架
4. 不添加新组织/团队名称
5. 不夸大领导力（如 "led", "spearheaded", "owned"）
6. 所有 LLM 输出默认标记 `needs_confirmation=True`

### Evidence 保护

LLM 改写不会提升原始声明的证据等级：
- `UNSUPPORTED` → 保持 `UNSUPPORTED`
- `NEEDS_USER_CONFIRMATION` → 保持
- 不会变成 `USER_PROVIDED`

## Provider 策略

| Provider | 说明 |
|----------|------|
| `disabled` | 默认，不进行任何改写 |
| `mock` | 确定性模拟，用于测试和本地演示 |
| `external` | 占位符，未来真实 LLM 集成（当前未实现） |

## CLI 使用

```bash
# 默认（无 LLM 改写）
py -m resume_pdf_agent run-sample --output-dir outputs/sample_no_llm --pdf-backend mock --write-frontend-page

# Mock LLM 改写模式
py -m resume_pdf_agent run-sample --output-dir outputs/sample_llm_mock --pdf-backend mock --enable-llm-rewriting --llm-provider mock --write-frontend-page
```

## 输出产物

| 产物 | 说明 |
|------|------|
| `llm_rewrite_result.json` | LLM 改写结果，包含所有候选 bullet |

## 已知限制

- 无真实外部 LLM 集成（仅 mock）
- LLM 候选不会自动应用到最终简历
- 改写质量受 mock provider 限制
- 无浏览器端改写审阅 UI
- 不验证真实世界事实
- 不预测录用概率

## 未来改进

- 真实 LLM provider 适配器
- 用户审批后再应用 LLM 候选
- 并排改写审阅 UI (M22)
- 更丰富的幻觉检测
