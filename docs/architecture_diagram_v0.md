# 架构与流程图 (Architecture Diagram v0)

> 中文优先 | Chinese-first

本文档使用 Mermaid 图表展示 `resume_pdf_agent` 的系统架构和工作流。

## A. 高层工作流管线 (High-Level Pipeline)

```mermaid
flowchart LR
    A[用户 JSON 输入<br/>UserProfile + ResumeContent] --> B[Criteria 选择<br/>Load & Select Profile]
    B --> C[简历类型分类<br/>Resume Type Classification]
    C --> D[差距分析<br/>Gap Analysis]
    D --> E[真实性检查<br/>Truthfulness Check]
    E --> F[Bullet 增强<br/>Bullet Enhancement]
    F --> G[模板匹配<br/>Template Matching]
    G --> H[HTML 渲染<br/>HTML Rendering]
    H --> I[PDF 生成<br/>PDF Generation]
    I --> J[前端仪表板<br/>Frontend Dashboard]

    style A fill:#1a1a2e,stroke:#e94560,color:#eee
    style J fill:#1a1a2e,stroke:#0f3460,color:#eee
```

## B. 模块依赖图 (Module Dependency)

```mermaid
graph TD
    subgraph "数据层 (Data Layer)"
        models[models<br/>Pydantic Schemas]
        sample_data[sample_data<br/>Sample Inputs]
    end

    subgraph "知识层 (Knowledge Layer)"
        criteria[criteria<br/>Knowledge Base & Selector]
        templates[templates<br/>Template Registry & Selector]
    end

    subgraph "分析引擎层 (Analysis Engine Layer)"
        classifier[classifier<br/>Resume Type Classifier]
        gap_analysis[gap_analysis<br/>Gap Analysis Engine]
        truthfulness[truthfulness<br/>Truthfulness Checker]
        enhancement[enhancement<br/>Bullet Enhancement]
    end

    subgraph "输出层 (Output Layer)"
        rendering[rendering<br/>HTML Renderer]
        pdf[pdf<br/>PDF Generator]
        frontend[frontend<br/>Dashboard Renderer]
    end

    subgraph "编排层 (Orchestration Layer)"
        workflow[workflow<br/>Pipeline Orchestrator]
        cli[cli<br/>Typer CLI]
    end

    models --> criteria
    models --> classifier
    models --> gap_analysis
    models --> truthfulness
    models --> enhancement
    models --> templates
    models --> rendering
    models --> pdf
    models --> frontend
    models --> workflow

    criteria --> workflow
    classifier --> workflow
    gap_analysis --> workflow
    truthfulness --> workflow
    enhancement --> workflow
    templates --> workflow
    rendering --> workflow
    pdf --> workflow
    frontend --> workflow

    cli --> workflow
    sample_data --> cli

    workflow --> rendering
    workflow --> pdf
    workflow --> frontend
```

## C. 产物流转图 (Artifact Flow)

```mermaid
flowchart TD
    input[输入<br/>sample_data_science_user.json] --> wf[工作流编排器<br/>run_resume_workflow]

    wf --> a1[criteria_profile.json<br/>匹配的 Criteria Profile]
    wf --> a2[classification.json<br/>分类结果]
    wf --> a3[gap_analysis.json<br/>差距分析结果]
    wf --> a4[truthfulness.json<br/>真实性检查结果]
    wf --> a5[enhancement.json<br/>Bullet 增强结果]
    wf --> a6[template_selection.json<br/>模板匹配结果]
    wf --> a7[workflow_result.json<br/>完整工作流结果]

    a1 --> html[resume.html<br/>结构化 HTML 简历]
    a2 --> html
    a3 --> html
    a5 --> html
    a6 --> html

    html --> pdf_output[resume.pdf<br/>PDF 简历]

    a1 --> dashboard[index.html<br/>静态工作流仪表板]
    a2 --> dashboard
    a3 --> dashboard
    a4 --> dashboard
    a5 --> dashboard
    a6 --> dashboard
    a7 --> dashboard
    html --> dashboard
    pdf_output --> dashboard

    style input fill:#16213e,stroke:#e94560,color:#eee
    style dashboard fill:#0f3460,stroke:#533483,color:#eee
    style pdf_output fill:#0f3460,stroke:#533483,color:#eee
```

## 数据流总结

1. **输入**：包含用户画像（`UserProfile`）和简历内容（`ResumeContent`）的 JSON 文件
2. **中间产物**：各阶段生成的 JSON 文件，记录分析结果和决策依据
3. **最终输出**：
   - `resume.html` — 可直接在浏览器查看的 ATS 友好简历
   - `resume.pdf` — 从 HTML 生成的 PDF
   - `index.html` — 工作流执行仪表板

## 技术栈

| 层级 | 技术 |
|------|------|
| 数据模型 | Pydantic v2 |
| 模板引擎 | Jinja2 |
| CLI 框架 | Typer |
| PDF 生成 | WeasyPrint（可选）/ Mock Backend |
| 测试框架 | pytest |
| 图表 | Mermaid（本文档） |

## 安全声明

- 不调用 LLM API（GPT-4、Claude、Gemini 等）
- 不联网搜索或获取外部数据
- 不声称知道任何公司的内部筛选标准
- 不预测录用概率
- 所有分析基于用户提供的确定性数据

---

*详见 `docs/limitations_and_roadmap_v0.md` 了解当前限制和未来路线图。*
