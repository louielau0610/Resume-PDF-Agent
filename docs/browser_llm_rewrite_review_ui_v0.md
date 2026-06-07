# Browser LLM Rewrite Review UI v0

## 概述 / Overview

M22 浏览器 LLM 改写审阅页面是一张纯静态 HTML 页面，用于审阅 M16 可选的 LLM 改写候选结果。该页面：

- 在浏览器中本地运行，无网络请求
- 从 `llm_rewrite_result.json` 加载候选数据
- 并排显示原始 bullet 与 LLM 改写候选文本
- 显示验证警告和风险标记
- 允许用户做出本地审阅决策（批准/拒绝/需要编辑/备注/忽略）
- 生成 `llm_rewrite_review_decisions.json` 供本地下载或复制
- 不会自动应用 LLM 候选到最终简历
- 不会调用任何真实 LLM API
- 不绕过 M5 真实性检查或 M14 确认门控

M22 provides a browser LLM rewrite review page. A local static HTML page helps users review M16 optional LLM rewrite candidates. It includes:

- Side-by-side original vs rewritten text comparison
- Validation warnings and risk flags display
- Local decision controls (approve/reject/edit/note/ignore)
- JSON decisions generation (copy/download)
- Does NOT apply candidates automatically
- Does NOT call any real LLM API
- Does NOT bypass M5 truthfulness or M14 confirmation

## 何时使用 / When to Use

- 用户在运行 M16 LLM 改写后希望审阅候选结果
- 用户希望在不自动应用的情况下比较原始 bullet 与改写候选
- 用户希望生成审阅决策 JSON 以供后续处理

- Users want to review LLM rewrite candidates after M16
- Users want to compare original bullets with rewrites without automatic application
- Users want to generate review decisions JSON for later processing

## 渲染 / Rendering

Generate mock LLM candidates:
```
py -m resume_pdf_agent run-sample --output-dir outputs/llm_review_demo --pdf-backend mock --enable-llm-rewriting --llm-provider mock --write-frontend-page
```

Render review UI:
```
py -m resume_pdf_agent render-llm-review-ui --result outputs/llm_review_demo/llm_rewrite_result.json --output outputs/llm_review_demo/llm_review.html
```

Demo script:
```
py scripts/run_demo_workflow.py --output-dir outputs/demo_llm_review_ui --pdf-backend mock --include-llm-mock --write-llm-review-ui
```

## 安全 / Safety

- 页面完全是本地的；不向任何服务器提交数据
- LLM 候选仅为措辞建议
- 仅批准您能够亲自验证的文本
- 此页面不会自动应用候选
- 此页面不会验证真实世界真实性
- 此页面不会绕过 M14 确认
- M5 真实性检查和 M14 确认门控保持权威
- 此页面不预测招聘概率
- 此页面不访问内部筛选标准

- Page is entirely local; no data submitted to any server
- LLM candidates are wording suggestions only
- Approve only text you can personally verify
- This page does NOT apply candidates automatically
- This page does NOT verify real-world truth
- This page does NOT bypass M14 confirmation
- M5 truthfulness checks and M14 confirmation gate remain authoritative
- This page does NOT predict hiring probability
- This page does NOT access internal screening standards

## 设计 / Design

### 组件 / Components

- Summary Cards: Provider, status, candidate count, confirmation count, warnings, errors
- Filter Bar: Filter by confirmation/risk/warning/clean
- Candidate Cards: candidate_id, source_experience_id, original_text, rewritten_text, provider, mode, status, evidence_level, metric_status, needs_confirmation, validation_warnings, risk_flags, rationale
- Decision Controls: approve_candidate, reject_candidate, needs_editing, provide_note, ignore_for_now
- Decision JSON Preview + Copy/Download
- CLI Instructions

### 样式 / Styling

- 暗色高级 CSS 主题（与 M12/M20/M21 一致）
- 响应式布局（并排文本在移动端堆叠）
- 无外部 CSS/JS 依赖

## 限制 / Limitations

- 本地静态页面仅
- 无服务器持久化
- 无数据库
- 无认证
- 无自动应用
- 无真实 LLM 调用
- 尚未有生产审阅工作流

## 相关模块 / Related Modules

- `src/resume_pdf_agent/llm_review_ui/` — M22 包
- `src/resume_pdf_agent/llm/` — M16 LLM 改写引擎
- `src/resume_pdf_agent/models/llm_review_ui.py` — M22 数据模型
- `src/resume_pdf_agent/cli.py` — `render-llm-review-ui` 命令
