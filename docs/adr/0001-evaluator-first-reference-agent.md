# ADR-0001：评测器优先、受限参考 Agent 与框架中立接缝

- **状态**：Accepted
- **日期**：2026-08-25
- **适用版本**：v0.1 规划基线

## 背景

项目需要同时证明 Agent 工程和 AI 测试/评测能力，但如果只做诊断 Agent，难以证明结论、证据和调查过程可靠；如果只做评测器，又缺少完全受控的真实被测 Agent。将多个框架 Agent 同时作为首版交付，还会让模型、提示、状态和工具差异混在一起，无法归因。

通用 Agent 评测与可观测产品已经覆盖 trace、数据集、实验、评分和展示。本项目的差异化应来自事故领域的确定性 replay、Ground Truth 隔离、只读工具策略、证据引用、正式拒答和过程评测，而不是重建完整平台。

## 决策

1. 独立评测器是主产品；最小参考诊断 Agent 是必须交付的首个受控被测对象。
2. `ReferenceAgentDriver = ProjectController + Policy`。controller 拥有参考 Agent 的内部状态和终止；外层 runner 永远拥有 Ground Truth firewall、工具网关、全局预算上限、canonical run events 和最终 validator。其他 `AgentDriver` 可以拥有内部编排，但不能绕过 runner 不变量。
3. MS-1 只用 `FixtureAgentDriver` 产生预设合法/非法报告。MS-2 才加入 ProjectController、ScriptedPolicy 和 LLMPolicy；完成 `PolicyDecision` 契约与 synthetic capability cases 后再选择首个模型供应商并记录 ADR。
4. A0/A1 是 one-shot 与有界主动调查的配置包对照，不能把全部差异只归因于 probe；A1/A2 在 versioned variant manifest 冻结其他字段后，才作为 RAG 消融。所有配置分别报告实际资源和成本。
5. 硬门禁与质量指标分离。每个 scheduled attempt 永久保留；deterministic hard-fail 标记 run 失败，config 只有纳入 runs 在指定安全/契约门禁上零违规才 eligible。基础设施失败进入 completion 分母，不得被静默重试替换。citation integrity 只覆盖引用存在、checksum、来源、版本和 Agent 可见性；语义支持度进入证据质量。多维 scorecard 允许 `inconclusive` 和 Pareto 取舍。
6. replay/evaluator 确定性与 LLM 随机性分开验证。per-run evaluator 只生成隔离的 `EvaluationRecord`；experiment aggregator 只读取多个记录和冻结的 `BenchmarkSpec`，计算 completion、paired delta、flip、case-clustered interval 与 Pareto/`inconclusive` 结论，不回写 `RunRecord`。v0.1 默认不承诺 winner；只有最终比较集全部重复且预注册的 95% case-clustered interval 与保护指标共同支持时，才作有边界的改善声明。
7. v0.1 只冻结 `AgentDriver`、`RunRecord` 和 `BenchmarkSpec` 三个暂定框架中立接缝，跨任务复用仍是假设；事故输入、输出、证据和指标保持领域专用。
8. LangGraph 是可选 `AgentDriver`：它可以拥有自己的内部 orchestration，但必须使用同一 runner 工具网关、全局预算、规范化 RunRecord 和 evaluator；它不阻塞 v0.1。OpenAI Agents SDK 或其他运行时也只能通过相同边界接入。
9. `RunRecord` 只对可观察运行行为、预算、工具结果、失败和版本元数据 canonical，并且永不包含 Ground Truth。case/replay snapshot 与 evaluator-only Ground Truth/EvaluationRecord 分别隔离。外部观测平台只接收字段白名单生成的 pre-evaluation 派生视图，并以 canary 负例阻断 Ground Truth、凭据和受限 payload。
10. 完成 v0.1 后，第二阶段可以用一个具体竞赛 Agent 做一至两周迁移实验。优化只读取 train/dev；sealed/hidden test 不进入 prompt、RAG、cache、trace 或逐轮调参。若 Agent 执行代码或写操作，必须新增 sandbox 与 side-effect policy。它不进入当前十二周门槛，也不构成“通用平台”声明。

## 被否决的方案

### 以诊断 Agent 为主、评测器为辅助

会削弱评测与测试开发的差异化，也容易退化为无法核验的 LLM demo。

### 首版同时实现自研、LangGraph 和 Agents SDK Agent

范围过大，且多个变量同时改变，难以把结果差异归因到某个设计因素。

### 将 LangGraph 或 Agents SDK 作为唯一核心运行时

可以更快获得编排能力，但会让首版最需要解释和测试的状态、预算、工具策略与事件语义被框架接管。

### 自建完整通用评测与可观测平台

会重复建设成熟产品已有的 trace、数据集、实验和 UI 能力，并挤占领域评测内核的时间。

## 后果

### 正向

- 评测器与被测 Agent 的主次和接口清楚。
- 可以用受控消融证明评测器对已知变化敏感。
- 状态、预算和安全边界可单测、可演示、可由作者解释。
- 后续框架或第二任务可以验证接缝，而不反向污染事故领域契约。

### 代价与风险

- 需要实现一个小型控制器，但必须限制为同步、短生命周期循环，不能演变成通用编排框架。
- 三次重复只能提供 pilot 方差信号，不能支持长期稳定性宣传。
- 三个通用接缝仍是假设；只有第二个真实任务接入后才能判断是否需要继续抽象。
- 外部框架 trace 映射到 `RunRecord` 可能丢失语义，适配器必须记录可映射、不可映射和合成字段。

## 重新评估触发器

- MS-2 入口、PolicyDecision 契约和 synthetic capability cases 已存在，需要选择首个模型供应商时。
- 自建纵向切片通过、考虑 LangGraph Adapter 时。
- 确定具体竞赛、规则、许可、任务 I/O 和隐藏测试边界时。
- 两个真实任务暴露出重复协议，需要抽象第四个以上通用接缝时。

## 决策资料

- [LangGraph overview](https://docs.langchain.com/oss/python/langgraph/overview)：低层状态编排、持久化和可恢复执行的定位。
- [OpenAI Agents SDK — Agents](https://openai.github.io/openai-agents-python/agents/)：SDK 托管循环与低层自行拥有循环的边界。
- [LangSmith Evaluation](https://docs.langchain.com/langsmith/evaluation)、[Langfuse](https://langfuse.com/docs)、[Arize Phoenix](https://arize.com/docs/phoenix/)、[Braintrust Experiments](https://www.braintrust.dev/docs/evaluate/run-evaluations)：现有数据集、实验、trace 与评测能力的官方说明。
