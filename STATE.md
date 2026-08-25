# Learning State

- 日期：2026-08-25
- 阶段：Day 1 — 项目定义与边界
- 当前状态：Provisional — Day 1 文档已完成，Ownership 口述复验待完成

## 已完成

- 建立本地原创 Git 仓库。
- 写明项目定位、v0.1 范围、非目标和十二周成功标准。
- 添加 README、MIT License、NOTICE 和基础 `.gitignore`。
- 明确当前没有 Agent 实现、第三方数据或评测结果。
- 明确 clean-room、第三方许可证和 AI 辅助边界。
- 明确项目同时交付最小参考诊断 Agent 和独立评测器。
- 经目标拷问确认独立评测器是主产品，参考诊断 Agent 是必须交付的首个受控被测对象。
- 接受“项目自有确定性 controller + 可替换 Policy”，以及 A0 无探针、A1 受限探针、A2 加 RAG 的受控变体。
- 接受硬门禁、多维 scorecard、冻结对照、小规模重复 pilot 和 held-out system 的有界评测深度。
- 接受 v0.1 只冻结 `AgentDriver`、`RunRecord`、`BenchmarkSpec` 三个接缝；LangGraph 为可选薄适配器，竞赛 Agent 为 post-v0.1 条件性迁移实验。
- 已创建 GitHub 远程仓库并跟踪 `origin/main`。

## 尚未进行

- 没有编写 Agent、Schema、工具或评测代码。
- 没有下载或提交任何数据。
- 没有产生或声称任何性能指标。
- 没有选择模型供应商、实现 LangGraph Adapter、接入观测平台或确定竞赛。

## 当前学习门槛

- 后续交互表明，`replay-first`、`SystemKnowledgePack` 和 v0.1 最小成功标准仍需要带具体案例的讲解与口述复验。
- 这不是已实现代码的缺陷，但属于硬学习门禁；复验前禁止进入 Day 2A 或 Schema 实现。
- 原 Day 2 Schema 任务作废，不允许直接进入 Schema 实现。

## AI 使用记录

- AI 完成：依据已确认的项目决策起草仓库文档，并解释 replay-first、System Pack 和最小成功标准。
- 项目作者完成：发现“评测诊断 Agent”的表述可能暗示项目不创建 Agent；追问陌生术语的来源；确认项目应同时实现最小参考诊断 Agent 和独立评测器。
- 修改的 AI 建议：将“只评估诊断 Agent”的模糊定位改为“构建最小参考诊断 Agent，并用独立评测器评测”。理由是前者无法说明被测 Agent 从何而来，也削弱了工具调用、假设更新和结构化输出的工程学习目标。
- 调整的 AI 建议：保留 System Pack 的模块化思想，但首次出现时改称 `SystemKnowledgePack（系统知识包）`。理由是 `SystemPack` 不是默认应知的行业术语，原文缺少定义。
- 保留的 AI 建议：保留 replay-first。理由是公开事故数据可以提供低成本、安全、可重复的调查环境，并便于隔离 Ground Truth 和进行回归对比；真实环境只作为后续 smoke test。
- 保留的 AI 建议：RAG 继续作为 Runbook 检索子系统。理由是项目核心是 Agent 的假设—探针—证据闭环及其评测，而不是再做一个通用知识库问答平台。
- 保留的 AI 建议：首版只开放注册过的只读工具。理由是先证明诊断和评测可靠性，避免任意 shell、kubectl 或自动修复扩大安全风险。
- 项目作者追问并确认：评测器是主产品，但参考 Agent 不能退化为脚本；评测深度必须同时覆盖确定性硬门禁与 LLM 方差，并通过同一 Agent 的受控变体呈现设计变化。
- 修改的 AI 建议：不把项目改成通用 Agent 评测平台；只保留三个框架中立接缝，并把现有观测平台视为未来可选导出后端。理由是避免与成熟平台同质化和提前抽象。
- 保留的 AI 建议：自建轻量 controller 为主、LangGraph 薄适配为次。理由是状态、预算、工具权限和事件本身属于需要评测与证明的项目资产。
- 延后的决定：首个模型供应商在 MS-2 入口、`PolicyDecision` 契约和 synthetic capability cases 就绪后选型；具体竞赛在 v0.1 结束后核验规则、许可与隐藏测试边界。
- 本轮“确认/接受”只记录共享架构决定，不等于项目作者已经达到 `Defendable`；仍以无提示口述和后续实现 Ownership Check 为准。

## Ownership Check（待复验）

- [ ] 能结合一个具体 case 解释为什么选择 replay-first。
- [ ] 能解释为什么 RAG 是子系统而不是项目本体。
- [ ] 能用自己的话说明 `SystemKnowledgePack` 的输入、输出和边界。
- [ ] 能解释为什么首版禁止任意 shell/kubectl。
- [ ] 能说明 evaluator 是主产品、Reference Agent 是首个受控 SUT、为何二者都必须交付，并从 `IncidentCase` 到评测报告口述 v0.1 最小纵向切片。
- [ ] 能指出一条修改或保留的 AI 建议及理由。

本轮新增的 controller/Policy、A0/A1/A2、随机性实验和框架接缝将在相关里程碑分别进行 Ownership Check，不扩张当前约 10 分钟的 Day 1 复验。

## 下一项唯一动作

进行一次约 10 分钟、带具体案例和 AI 讲解的 Day 1 Ownership 口述复验。通过后进入 Day 2A：只理解数据契约、provenance 和 Ground Truth 隔离，产出字段/规则表及合法、泄漏非法两个普通 JSON；不写 JSON Schema、不实现 Agent、不接入数据。
