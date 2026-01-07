
# CI Agent 示例（GitHub Actions + Python）

这个示例展示了一个最小可用的 **CI Agent**：在 CI 运行中捕获测试/构建日志，
由 Agent（Python 脚本）自动分析失败原因，生成可读的结论与修复建议，
并将结果自动评论到 Pull Request。

> 作用：让传统 CI 的“固定流程”升级为“智能化决策 + 自我解释 + 建议修复”。

## 目录结构

```
.
├── agent/
│   └── ci_agent.py           # 核心智能分析器（Agent）
├── .github/
│   └── workflows/
│       └── ci-agent.yml      # 工作流，运行测试并调用 Agent，回帖到 PR
└── README.md
```

## 使用方法

1. 将本目录内容提交到你的 GitHub 仓库。
2. 在 Pull Request 上，工作流会自动触发：
   - 运行测试（示例用 `pytest -q`，你可以替换为构建/其他脚本）
   - 将测试输出保存到 `pytest_output.txt`（即使失败也不中断，便于 Agent 分析）
   - 调用 `agent/ci_agent.py` 生成 `analysis.md`
   - 将 `analysis.md` 自动评论到 Pull Request

> 你可以根据自己的技术栈（.NET、Playwright、前端等）修改测试命令与分析规则。

## 环境变量（可选）

- `CI_AGENT_MODE`：默认 `basic`。你也可以设置为 `suggest-only`（仅建议）或 `strict`（发现失败即标红）。
- `PYTEST_CMD`：覆盖默认的 `pytest -q`。

## 本示例的智能能力

- 识别典型失败模式：
  - Playwright `TimeoutError` / 选择器不存在 / iframe 问题
  - Playwright 浏览器未安装（`Executable doesn't exist`）
  - .NET 常见路径问题：`Illegal characters in path`
  - 包管理/网络波动导致的临时失败（建议重试策略）
- 给出 **根因推断**、**修复建议** 与 **后续行动**。

> 注意：本示例不直接修改代码，仅自动评论到 PR。你可以在此基础上扩展为自动提交修复 PR。

## 自定义扩展建议

- 将 `ci_agent.py` 的规则改为 **正则 + 领域知识**（例如 WinForms/设计时异常）
- 接入 LLM（OpenAI/Azure OpenAI）增强推理：
  - 通过环境变量注入 API Key
  - 增加“日志 → 结论”生成的自然语言质量
- 增加自动修复：
  - 在建议稳定后，自动生成 patch 并通过 `create-pull-request` action 发起修复 PR

---

欢迎按实际项目需求迭代这个 Agent，逐步把 CI 的失败率和人工排查时间降到最低。
