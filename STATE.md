# Learning State

- 日期：2026-08-23
- 阶段：Day 1 — 项目定义与边界
- 当前状态：Day 1 文档已核验，Ownership Check 已完成

## 已完成

- 建立本地原创 Git 仓库。
- 写明项目定位、v0.1 范围、非目标和十二周成功标准。
- 添加 README、MIT License、NOTICE 和基础 `.gitignore`。
- 明确当前没有 Agent 实现、第三方数据或评测结果。
- 明确 clean-room、第三方许可证和 AI 辅助边界。
- 明确项目同时交付最小参考诊断 Agent 和独立评测器。
- 已创建 GitHub 远程仓库并跟踪 `origin/main`。

## 尚未进行

- 没有编写 Agent、Schema、工具或评测代码。
- 没有下载或提交任何数据。
- 没有产生或声称任何性能指标。

## 当前阻塞项

无工程或学习验收阻塞。

## AI 使用记录

- AI 完成：依据已确认的项目决策起草仓库文档，并解释 replay-first、System Pack 和最小成功标准。
- 项目作者完成：发现“评测诊断 Agent”的表述可能暗示项目不创建 Agent；追问陌生术语的来源；确认项目应同时实现最小参考诊断 Agent 和独立评测器。
- 修改的 AI 建议：将“只评估诊断 Agent”的模糊定位改为“构建最小参考诊断 Agent，并用独立评测器评测”。理由是前者无法说明被测 Agent 从何而来，也削弱了工具调用、假设更新和结构化输出的工程学习目标。
- 调整的 AI 建议：保留 System Pack 的模块化思想，但首次出现时改称 `SystemKnowledgePack（系统知识包）`。理由是 `SystemPack` 不是默认应知的行业术语，原文缺少定义。
- 保留的 AI 建议：保留 replay-first。理由是公开事故数据可以提供低成本、安全、可重复的调查环境，并便于隔离 Ground Truth 和进行回归对比；真实环境只作为后续 smoke test。
- 保留的 AI 建议：RAG 继续作为 Runbook 检索子系统。理由是项目核心是 Agent 的假设—探针—证据闭环及其评测，而不是再做一个通用知识库问答平台。
- 保留的 AI 建议：首版只开放注册过的只读工具。理由是先证明诊断和评测可靠性，避免任意 shell、kubectl 或自动修复扩大安全风险。

## Ownership Check

- [x] 能解释为什么选择 replay-first：可重复、低成本、安全，并支持 Ground Truth 隔离和回归测试。
- [x] 能解释为什么 RAG 是子系统而不是项目本体：RAG 只提供公开 Runbook，核心价值是 Agent 调查闭环和独立评测。
- [x] 能解释 SystemKnowledgePack 如何承载不同系统和组件知识：它封装实体、拓扑、别名、公开 Runbook、数据适配器和允许探针，不存放某个 case 的答案。
- [x] 能解释为什么首版禁止任意 shell/kubectl：防止越权和不可控副作用，让行为可审计、可回放。
- [x] 能说明 v0.1 的最小成功标准：至少一个公开 case 能经过 adapter、replay、最小参考 Agent、结构化报告和独立评测，并通过契约、泄漏、引用和工具策略门禁。
- [x] 能指出一条需要修改或保留的 AI 建议及理由：已修改 Agent 定位和术语说明，保留 replay-first、RAG 子系统与只读工具边界，理由见上。

## 下一项唯一动作

Day 2：只定义 `IncidentCase@1` 和 `DiagnosisReport@1` 的最小契约与示例，不实现 Agent、不接入数据。
