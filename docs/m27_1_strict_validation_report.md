# M27.1 Strict Validation Report

## 验证日期 / Validation Date

2026-06-08

## 验证基线 / Validation Baseline

- **Commit**: `cdd0a6d` — M27 add manual patch preview artifacts
- **Branch**: `main`
- **Working tree**: Clean

## 验证结果 / Validation Results

### 1. compileall

```
py -m compileall src tests scripts -q
```

结果 / Result: **零语法错误** ✅

### 2. 全量测试 / Full Test Suite

```
py -m pytest -q
```

结果 / Result: **984 passed, 2 skipped** ✅

### 3. 专项测试 / Focused Tests

| 测试组 | 结果 |
|---|---|
| M27 (manual patch preview) | 36 passed ✅ |
| M26 (pre-application validation) | 39 passed ✅ |
| M25 (application preview UI) | 43 passed ✅ |
| M24 (application plan) | 45 passed ✅ |
| M23 (review decision) | 40 passed ✅ |
| M22 (review UI) | 79 passed ✅ |

### 4. Release Readiness

```
py scripts/validate_release_readiness.py
```

结果 / Result: **All release-readiness checks PASSED** ✅
- llm_manual_patch_preview 包存在 ✅
- llm_pre_application_validation 包存在 ✅
- ExportFormat 仅 pdf ✅
- 无禁止依赖 ✅

### 5. M27 CLI Smoke Test

```
py -m resume_pdf_agent preview-llm-manual-patch \
  --plan outputs/m27_1_manual/llm_rewrite_application_plan.json \
  --validation outputs/m27_1_manual/llm_rewrite_pre_application_validation.json \
  --output-json outputs/m27_1_manual/llm_rewrite_manual_patch_preview.json \
  --output-md outputs/m27_1_manual/llm_rewrite_manual_patch_preview.md \
  --output-html outputs/m27_1_manual/llm_rewrite_manual_patch_preview.html
```

结果 / Result: **EXIT 0** ✅
- Total items: 6
- Preview ready: 0, Blocked: 6（全部因 truthfulness_not_verified + confirmation_required + executable_patch_forbidden 被阻塞 — 预期行为）
- JSON/MD/HTML 全部生成

### 6. 制品内容验证 / Artifact Content Verification

| 检查项 | 结果 |
|---|---|
| preview_only = True | ✅ |
| final_resume_modified = False | ✅ |
| executable_patch_generated = False | ✅ |
| applied_candidates 不存在 | ✅ |
| patch_operations 不存在 | ✅ |
| 每个阻塞项包含 executable_patch_forbidden | ✅ (6/6) |
| 每个阻塞项包含 truthfulness_not_verified | ✅ (6/6) |
| 每个阻塞项包含 confirmation_required | ✅ (6/6) |
| Markdown 包含安全声明 | ✅ |
| HTML 无 "update resume" 控件 | ✅ |
| HTML 无 "execute patch" 控件 | ✅ |
| HTML 无外部 CDN | ✅ |
| HTML 无外部字体 | ✅ |
| PDF header 以 %PDF- 开头 | ✅ |
| ExportFormat = ['pdf'] | ✅ |
| resume.html SHA256 在 M27 验证前后不变 | ✅ |

### 7. Demo Workflow

```
py scripts/run_demo_workflow.py --output-dir outputs/m27_1_demo \
  --pdf-backend mock --include-llm-mock \
  --write-llm-review-ui --write-llm-review-decision-summary \
  --write-llm-application-plan --write-llm-application-preview-ui \
  --write-llm-pre-application-validation --write-llm-manual-patch-preview
```

结果 / Result: **EXIT 0** ✅
- 12/12 工件全部存在且非空
- M27 preview JSON: 9,582 bytes
- M27 preview MD: 8,461 bytes
- M27 preview HTML: 26,483 bytes

### 8. 安全保证 / Safety Guarantees

| 保证 | 状态 |
|---|---|
| 无候选自动应用 | ✅ |
| 无可执行补丁生成 | ✅ |
| 无最终简历修改 | ✅ |
| 无 .patch/.diff 文件 | ✅ |
| M5 真实性检查未被绕过 | ✅ |
| M14 确认门控未被绕过 | ✅ |
| M16 改写行为未变 | ✅ |
| 无真实 LLM API 调用 | ✅ |
| HTML/JS/CSS 本地静态，无网络请求 | ✅ |
| 无外部 CDN/字体 | ✅ |

## 结论 / Conclusion

M27（Manual Patch Preview Without Resume Mutation）通过所有严格验证检查。未发现回归或安全问题。M27.1 验证完成。

## 相关提交 / Related Commits

- `cdd0a6d` — M27 add manual patch preview artifacts（已推送到 origin/main）
- M27.1 验证报告文档（本文档）

## 下一步 / Next Steps

- M28：人工补丁审批检查清单（Human-Only Patch Approval Checklist），不应实现为可执行补丁。
