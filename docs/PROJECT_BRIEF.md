# Project Brief：云原生事故诊断 Agent 评测实验室

> 状态：Day 1 文档已完成；Ownership 口述复验待完成
> 版本：0.2
> 日期：2026-08-23
> 最近审查：2026-08-25

## 开工前的五句话

以下内容经过项目作者提问和修订，记录 Day 1 的暂定共享理解；是否已成为作者可独立辩护的能力，以后续口述复验为准：

1. 本项目以独立评测器为主产品，并构建一个最小可运行的云原生事故诊断 Agent 作为首个受控被测对象，用公开数据和可重复实验判断结论、证据、调查过程与安全边界。
2. 它不是静态日志分类器，因为 Agent 只获得有限的初始症状，还需要主动选择 metrics、logs、traces、events、topology 或测试结果等只读探针来验证假设。
3. Agent 先提出少量候选根因，再选择能够区分候选的探针，依据新观察支持、削弱或拒绝假设，最后发布诊断或拒答。
4. 首版只允许注册过的只读工具，因为诊断能力必须先被可靠评测；任意 shell、kubectl 或自动修复会引入难以控制和证明的安全风险。
5. 当证据不足、证据冲突无法消解、没有有效探针或调查预算耗尽时，系统必须返回 `insufficient_evidence`，不能用自然语言编造确定答案。

## 1. 项目背景

云原生事故可能同时涉及 Kubernetes、数据库、中间件、业务服务和平台约束。只用一段日志判断答案，无法评估调查过程，也容易受数据泄漏、近重复样例和模糊评分影响。本项目以公开数据构建确定性 replay，由独立评测器评价结论、证据和调查行为。

## 2. 目标用户

目标用户是诊断 Agent 开发者和 AI 测试/评测工程师。他们需要比较模型、提示、知识包和工具策略，复现失败并阻止质量或安全回归。本项目不是面向运维人员的完整平台，也不重建通用 trace、数据集、标注和实验管理产品。

## 3. 核心输入

每个事故从有限的告警、测试失败或用户症状开始，并绑定版本化 replay case。Agent 看不到根因标签，只能查询该 case 的 metrics、logs、traces、事件、拓扑、测试结果和公开 Runbook。SystemKnowledgePack（系统知识包，简称 System Pack）描述各系统的实体、拓扑、公开知识和允许探针。

## 4. 核心输出

Agent 输出版本化报告，状态只能是诊断完成或证据不足。`diagnosed` 必须包含 1～3 个排序原因，每个原因至少引用一条可核验观察；`insufficient_evidence` 必须包含 0 个候选原因，并记录限制和建议的只读检查。报告同时记录运行版本，且不保存模型隐藏思维链。

## 5. 核心机制

会话按“观察—假设—只读探针—证据—更新—发布或拒答”运行。项目自有 controller 只负责参考 Agent 的内部状态、局部停止和 `Policy` 提议预检；可替换的 `Policy` 只提出结构化下一步，不能直接执行工具或读取 Ground Truth。外层 runner 负责不可绕过的最终授权与工具执行、全局预算、canonical events 和 final validator。首版最多三个活跃假设、三轮更新和六次工具调用，模型或框架文本不能覆盖 runner 事实。

## 6. v0.1 范围

首版实现独立评测器、一个最小参考诊断 Agent、离线 replay、公开数据适配、受限工具和结构化诊断。per-run evaluator 为每次运行生成隔离的 `EvaluationRecord`；experiment aggregator 只基于多个记录和冻结的 `BenchmarkSpec` 计算完成率、配对差异、方差与区间，不回写 `RunRecord`。评测器先用手算 fixture 校验关键公式与跨字段约束，用 mutation 验证对指定错误的敏感性，并以无模型纵向切片验证门禁链路；这些测试不等于证明 evaluator 对所有错误都正确。之后比较 `A0` one-shot/no-probe 与 `A1` bounded-probes/no-RAG 两套调查配置，并在 `A1` 上只增加冻结 RAG 能力形成 `A2` 消融。LLM 方差与 replay 确定性分开报告。RAG 只检索可追溯的公开 Runbook，并独立评测。核心候选数据为 RCAEval，外部验证候选为 RCA100 或 AIOps2025。

## 7. 非目标

v0.1 不自动修复，不开放任意 shell 或 kubectl，不建设复杂 UI、通用工作流、多 Agent 平台或通用 Agent 评测 SaaS，也不训练基础模型。未知组件和缺失证据必须允许拒答。LangGraph 只可能作为核心纵向切片完成后的可选薄适配器，不是发布门槛。

## 8. 十二周成功标准

十二周内完成从公开 case、replay、Agent 调查、结构化报告到独立评测的纵向切片。硬门禁覆盖契约、工具策略、Ground Truth 泄漏、citation integrity 和可重复性；语义支持度进入证据质量，不与确定性引用完整性混淆。多维 scorecard 不以单一总分抵消安全失败。报告区分冻结集结果与小规模重复运行 pilot，必须完成 held-out system 验证；跨数据集外部验证在许可、映射和时间门禁通过时作为可选独立结果。统计证据不足时结论必须为 `inconclusive`，并支持五分钟演示。

## 9. 演进边界

v0.1 只冻结 `AgentDriver`、`RunRecord` 和 `BenchmarkSpec` 三个暂定框架中立接缝；它们能否跨任务复用仍是假设。`IncidentCase`、`DiagnosisReport`、probe、evidence、真值加载和根因指标保持领域专用。项目自有 `RunRecord` 是可观察运行行为、预算、工具结果、失败和版本元数据的 canonical source；case/replay snapshot 与 evaluator-only Ground Truth/EvaluationRecord 分别保持隔离。Phoenix、Langfuse 或 LangSmith 等平台未来只能接收字段白名单生成的 pre-evaluation 派生 trace。

完成 v0.1 后，可以选择一个真实竞赛 Agent 做时间盒迁移实验，验证第二个任务是否能复用运行、预算、事件和比较能力。一次迁移只能证明一次跨任务复用，不能据此宣称支持任意 Agent；具体竞赛、规则、许可和隐藏测试边界确定前，不进入当前契约。

## 10. 合规与所有权边界

项目从空仓库 clean-room 建立，不使用公司的代码、日志、规则、架构、命名或客户信息。公开资料须记录来源、版本、许可证和分发限制；原始及派生第三方 payload 默认均不提交，除非 data card 明确证明再分发权限。AI 可辅助起草和 Review，但项目作者必须核验判断、记录修改并能独立解释主要设计与测试。

实施顺序、需求和退出门槛见 [Project Roadmap](PROJECT_ROADMAP.md)，主产品和框架边界见 [ADR-0001](adr/0001-evaluator-first-reference-agent.md)。
