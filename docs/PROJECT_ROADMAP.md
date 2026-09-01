# Project Roadmap：Incident Agent Evaluation Lab

> 状态：Active planning baseline
>
> 版本：0.2
>
> 最近审查：2026-09-01

本路线图提前说明项目要解决的问题、真实场景、需求、技术手段和验收证据。十二周是目标窗口，不是按日期锁死的课程表；只有通过当前退出门槛才进入下一里程碑。窗口落后时缩小可选范围，不跳过门禁，也不形成“补课债”。

## 1. 问题与交付承诺

静态日志分类或一次性自然语言回答不能证明诊断系统会主动验证假设，也难以核验引用是否真实、工具行为是否安全、不同版本能否公平回归。

v0.1 同时交付，但主次不对等：

1. **独立评测器（主产品）**：不依赖 Agent 自述，逐 run 校验结构化契约、Ground Truth 隔离、证据引用、工具策略、诊断质量和运行成本；跨 run 的随机性由实验聚合器报告。
2. **最小参考诊断 Agent（首个受控被测对象）**：从有限症状出发，在预算内提出假设、调用注册的只读探针、更新判断并发布诊断或拒答。
3. **离线 replay 环境**：对版本化事故证据进行确定性回放，支持失败复现和版本比较。

Runbook RAG 是可独立评测的知识子系统。Kubernetes 是首个系统环境，不是项目永久边界；不同组件知识通过版本化 `SystemKnowledgePack（系统知识包）` 和数据适配器接入。

v0.1 不做自动修复、任意 shell/kubectl、复杂 UI、多 Agent 平台、通用评测 SaaS 或生产适用性宣传。

## 2. 核心数据流

```text
Public dataset / synthetic clean-room case
                  │
                  ▼
        Dataset adapter + provenance
                  │
          ┌───────┴────────┐
          ▼                ▼
   IncidentCase@1      GroundTruth
   Agent-visible        Evaluator-only
          │                │
          ▼                │
  Deterministic replay     │
          │                │
          ▼                │
 ReferenceAgentDriver = controller + Policy
          │
          ├──── read-only probes ───► replay
          │
          ▼
 RunRecord + DiagnosisReport@1
          │
          └────────────────────────► Independent evaluator ◄── GroundTruth
                                   │
                                   ▼
                         EvaluationRecord(s)
                gates + per-run metrics + terminal reason
                                  │
                                  ▼
                         Experiment aggregator
                completion + paired delta + variance + CI
```

ingestion 必须生成两个隔离视图：Agent runtime 只能取得 incident/evidence view；evaluator 只能在报告产生后，使用不编码答案的 opaque join key 通过 evaluator-only truth loader 加载 Ground Truth。Agent 包不得导入 truth loader。Ground Truth 不能通过字段、文件名、case ID、路径、manifest、检索索引、提示或工具结果泄漏。

参考 Agent 的控制器拥有其内部状态与停止条件；`Policy` 只能依据 Agent-visible snapshot 提出结构化下一步。外层 runner 永远拥有 Ground Truth firewall、工具网关、全局预算上限、规范化运行事件和最终 validator。其他 `AgentDriver` 可以拥有自己的内部编排，但不能绕过这些 runner 不变量。

`RunRecord` 永不包含 Ground Truth，只是可观察运行行为、预算、工具结果、失败与版本元数据的 canonical source。evaluator 在 report 冻结后加载 Ground Truth，并把逐项评分写入隔离的 `EvaluationRecord`；`RunRecord` 最多保存 opaque evaluation report ref。case/replay snapshot、RunRecord 与 EvaluationRecord 是三个权限不同的事实边界。

per-run evaluator 只生成隔离的 `EvaluationRecord`。experiment aggregator 只读取多个 `EvaluationRecord` 和冻结的 `BenchmarkSpec`，计算 completion、paired delta、flip、case-clustered interval 以及 Pareto/`inconclusive` 结论；它不读取 Agent 私有状态，也不回写 `RunRecord`。

## 3. 评测深度、受控变体与框架边界

### 3.1 两类确定性

- **必须确定**：同一 case snapshot 和 probe request 的 replay observation、工具策略、硬门禁与 evaluator 计算结果。
- **不承诺确定**：真实 LLM 的决策文本和轨迹。每次运行记录模型、prompt、参数、知识包、预算、token、延迟、重试与失败；模型质量按重复运行分布报告。
- **无模型基线**：ScriptedPolicy、手算 fixture 和 mutation 先校验控制器/评测器的关键计算、已声明不变量与对指定错误的敏感性；这些测试不证明其对所有错误都正确，也不用响应缓存把模型随机性伪装成稳定性。

### 3.2 同一参考 Agent 的受控配置

| 变体 | 配置差异 | 可回答的问题 |
|---|---|---|
| A0 one-shot/no-probe | 一次决策，只用初始症状；不运行调查循环 | one-shot 配置与有界主动调查配置有何整体差异；不能把差异只归因于 probe |
| A1 bounded-probes/no-RAG | controller 循环与注册只读探针，无 RAG | 新观察能否支持、削弱或拒绝假设 |
| A2 bounded-probes+RAG | 在 A1 上只增加一种预先冻结、计入预算的 Runbook RAG 能力 | RAG 单因素消融是否带来可测增益或新失败 |

`FixtureAgentDriver` 是 MS-1 的确定性测试夹具，直接产生预设合法或非法报告，不包装成智能 Agent。MS-2 才实现 `ReferenceAgentDriver = ProjectController + ScriptedPolicy/LLMPolicy`。LangGraph 只可能在自建纵向切片通过后作为可选 `AgentDriver`；它可拥有内部 orchestration，但必须经 runner 工具网关并映射到同一 RunRecord。除非预先定义可归因差异，否则框架实现不参加诊断质量归因。

每个配置都在 `BenchmarkSpec` 的 versioned variant manifest 中冻结 driver/controller/policy/model/provider、base prompt、sampling、tool/RAG capability、corpus、case split、预算、retry、evaluator、primary metric、protected metrics、hard-gate eligibility 和 stop/exclusion rule。A0/A1 是调查配置包对照；只有 A1/A2 在上述字段不变且只打开一种 RAG 能力时才称为 RAG 消融。实际 token、tool、latency 和成本始终单独报告，不声称不同 capability 配置具有相同消耗。

### 3.3 评测停止线

1. **关键计算与门禁校验**：为每个硬门禁至少准备一组 pass/fail fixture；手算 expected value/delta 校验公式、分母和跨字段约束，mutation 验证对指定错误的敏感性。Ground Truth 泄漏另由依赖边界、可见性以及字段/路径/索引/export 扫描测试覆盖。
2. **硬门禁语义**：每个 scheduled attempt 都必须保留。某 run 出现 deterministic hard-fail 时标记失败；config 只有全部纳入评测的 runs 在指定安全/契约 gate 上零违规才 eligible。provider/tool 基础设施失败不等同安全违规，但必须进入 completion 分母，不能用静默重试后的成功 run 替换。
3. **多维 scorecard**：诊断、拒答、证据、调查过程、完成率、延迟、token/tool cost 和安全分别报告，不压成通用总分。
4. **受控比较**：冻结测试集上报告 A0/A1 调查配置包的 case-level paired delta，MS-3 再加入 A1/A2 RAG 消融。比较前冻结 variant manifest；同时换模型、prompt、工具、RAG、预算或 retry 的结果只能视为 end-to-end system comparison，不能归因到单项设计。
5. **随机性 pilot**：看结果前冻结 pilot manifest，确定 exact N（不少于 20）以及 system/fault-family、diagnosable/insufficient、安全失败和缺失模态的覆盖；每个最终配置至少重复三次。重复 run 嵌套在 case 内，不增加独立 case 数；按 case/fault group 汇总后做 paired cluster bootstrap，并预注册 95% CI、seed 和 resampling 次数。provider 无可靠 seed 时按 case 交错执行。
6. **结论边界**：v0.1 默认只报告 evaluator sensitivity、case-level paired delta 和 pilot variance，不承诺 winner。只有最终比较集全部重复，预注册主指标的 95% case-clustered interval 支持改善，且 protected metrics、completion、成本和安全没有不可接受退化时，才允许作有边界的“更好”声明；否则必须 `inconclusive` 或报告 Pareto 取舍。
7. **完成与失败分母**：terminal taxonomy 至少包含 `valid_diagnosis`、`valid_abstention`、`contract_failure`、`policy_failure`、`budget_exhausted`、`timeout`、`provider_or_tool_infra_failure`。completion 是 scheduled runs 中产生合法 terminal report 的比例；端到端质量以全部 scheduled runs 为分母，另报 conditional-on-completion 质量。attempt/retry 与 terminal reason 单列，规则写入 `BenchmarkSpec`。
8. **泛化**：v0.1 必须完成所选核心数据集的 held-out system 评测；若使用 RCAEval，则采用按近重复/fault group 冻结的三轮 LOSO，outer result 不反向调 prompt、RAG 或阈值。跨数据集外部验证仅在许可、映射和时间门禁通过时可选，且始终单独报告。

### 3.4 v0.1 的可复用接缝

- `AgentDriver`：启动一个符合协议的 system under test/runtime；它只能通过 runner 提供的工具网关和事件接口工作。v0.1 只执行 first-party driver，不运行不可信第三方代码。
- `RunRecord`：由 runner 生成 append-only sequence 和不可变字段，至少记录 benchmark/variant/case snapshot refs、driver/controller/policy versions、attempt/retry、预算、工具结果、成本、错误、termination 和 final artifact。Agent telemetry 位于独立 namespace，不能伪造或覆盖 tool result、budget、cost、sequence、termination 或 provenance。`RunRecord` 永不包含 Ground Truth。
- `BenchmarkSpec`：声明 case/evaluator 版本、能力等级、variant manifest、预算、retry、重复、切分、primary/protected metrics、hard-gate eligibility 与统计计划。

`IncidentCase`、`DiagnosisReport`、Hypothesis、Evidence、Probe、truth loader 和根因指标继续属于事故领域。v0.1 不实现动态插件发现、任意第三方代码执行、万能指标 DSL 或跨任务总榜。

evaluator 只从 runner-owned 字段和冻结 report 读取运行事实，再从隔离 truth loader 读取 Ground Truth。driver 伪造工具结果、成本、预算、序号、终止或 provenance 的负例必须失败。未来 exporter 只能读取 pre-evaluation、字段 allowlist 的 RunRecord projection；Ground Truth canary、凭据和 restricted payload 的导出负例必须被阻断。

## 4. 核心场景

| ID | 初始状态 | 系统行为 | 可观察结果 |
|---|---|---|---|
| S1 证据不足 | 只有告警或测试失败，现有证据无法区分候选原因 | Agent 在预算内查询允许的探针，保留未消除的不确定性 | 返回 `insufficient_evidence`，candidate cause 必须为 0，并列出限制和下一项只读检查 |
| S2 可诊断事故 | replay case 含可区分根因的多源证据 | Agent 提出少量假设，选择能区分它们的探针并更新置信度 | `diagnosed` 包含 1～3 个排序原因，每个原因至少一条可核验 evidence ref |
| S3 工具或安全失败 | 请求未知工具、越权参数、超时，或日志/Runbook 含恶意指令 | 工具层 fail closed；模型文本不能覆盖结构化错误 | 产生可审计的拒绝、超时或失败事件，策略违规为 0 |
| S4 版本回归比较 | 同一 case 和证据快照运行不同模型、prompt、策略或知识包 | 固定 replay 输入和评测版本，记录非确定性参数 | 结果可复现比较；外部 LLM 的方差单独报告，不承诺逐字一致 |
| S5 泛化验证 | 未见系统或另一公开数据集的冻结子集 | 通过适配器映射统一契约，不让外部样本反向调参 | 内部、留一系统和跨数据集结果分别报告，不合并成一个总分 |

## 5. 需求到证据矩阵

状态使用 `Planned / In progress / Blocked / Done`。`Done` 只表示工程退出门槛通过，不自动表示作者已达到面试可辩护水平。

### A. 契约与领域边界

| ID | 问题或需求 | 技术手段 | 最近替代方案与取舍 | 验收证据 | 依赖 | 状态 |
|---|---|---|---|---|---|---|
| R-A1 | 不同数据源需要稳定、版本化的 Agent 输入 | `IncidentCase@1` 字段规则、JSON Schema、版本字段 | 任意 Python `dict` 起步快，但无法统一验证和演进 | 合法/非法 fixture、schema test、兼容性说明 | MS-0 | Planned |
| R-A2 | Agent 输出必须可机器验证且允许拒答 | `DiagnosisReport@1`、枚举状态、证据引用、独立 validator | 纯自然语言更自由，但无法建立硬门禁 | diagnosed 1～3 原因/拒答 0 原因/坏引用三类测试 | R-A1 | Planned |
| R-A3 | 真值不得污染被测系统 | 两个隔离视图、opaque join key、evaluator-only truth loader、依赖边界测试 | 同一 JSON 内隐藏字段仍可能被提示或工具读到 | Agent 包不可导入 truth loader；字段、文件名、manifest、索引和 API 泄漏测试 | R-A1 | Planned |
| R-A4 | 评测器不能与内置 Agent 或某一框架粘死 | 三个暂定接缝、runner-owned immutable fields、driver conformance/malicious-driver tests | 现在构建完整插件平台会产生未经第二场景验证的抽象 | MS-1 FixtureAgentDriver 契约样例；MS-2 Fixture/Reference drivers 共用 evaluator；伪造 tool/budget/cost/sequence/termination/provenance 均失败 | R-A1/R-A2 | Planned |

### B. 数据适配与 replay

| ID | 问题或需求 | 技术手段 | 最近替代方案与取舍 | 验收证据 | 依赖 | 状态 |
|---|---|---|---|---|---|---|
| R-B1 | 公开数据字段和语义不同 | dataset adapter、provenance、data card、版本/校验和 | 直接在 Agent 中处理原始字段会耦合数据集 | 一个冻结 fixture 可转换且来源可追溯 | R-A1/R-A3/R-B3 | Planned |
| R-B2 | 调查失败必须可重复 | 版本化 evidence store、确定性 probe result、replay session | live-first 更真实，但不稳定、昂贵且难隔离真值 | 同一快照的工具返回和硬门禁结果一致 | R-A1/R-A3 | Planned |
| R-B3 | 外部数据许可不能被 MIT 覆盖 | 下载器、data card、NOTICE、raw/derived third-party payload ignore | 将数据提交仓库更方便，但有许可和体积风险 | 来源、版本、许可、checksum、分发限制齐全 | 无 | Planned |

### C. 参考 Agent 与只读工具

| ID | 问题或需求 | 技术手段 | 最近替代方案与取舍 | 验收证据 | 依赖 | 状态 |
|---|---|---|---|---|---|---|
| R-C1 | Agent 需要主动验证而不是猜答案 | 假设—探针—证据—更新状态机，最多 3 个候选/3 轮 | 一次生成结论实现简单，但不能评估调查行为 | 至少一例假设被新证据削弱或拒绝 | R-B2/R-A2 | Planned |
| R-C2 | 工具调用必须受控且可审计 | allowlist、参数 Schema、预算、超时、结构化错误事件 | 通用 shell/kubectl 灵活，但权限和副作用不可证明 | 未知工具、越权、超时、预算耗尽测试 | R-B2 | Planned |
| R-C3 | 不同系统知识不能硬编码成万能规则 | `SystemKnowledgePack`：实体、拓扑、别名、公开 Runbook、允许探针 | 单一巨型 Skill 易把 case 答案和组件知识混在一起 | 更换知识包不改 Agent 核心循环 | R-C1 | Planned |
| R-C4 | LLM 或框架提议不能绕过系统不变量 | 项目自有确定性 controller + `Policy.decide(snapshot)`；provider adapter 只产出结构化提议 | 让 SDK Runner 拥有循环更快，但状态、预算与事件边界难独立证明 | 非法 PolicyDecision 被拒；ScriptedPolicy 与一个 LLMPolicy 走同一 controller | R-A4/R-C1/R-C2 | Planned |

### D. Runbook RAG 子系统

| ID | 问题或需求 | 技术手段 | 最近替代方案与取舍 | 验收证据 | 依赖 | 状态 |
|---|---|---|---|---|---|---|
| R-D1 | 诊断需要可追溯知识，而非模型记忆 | 文档切分、检索、来源/版本引用、检索结果契约 | 通用问答 RAG 容易把项目重心移到 UI 和聊天 | 检索 recall/precision、引用存在性、错误文档案例 | R-C3 | Planned |
| R-D2 | 文档内容可能包含恶意或无关指令 | 文档视为不可信数据、指令/证据通道分离、安全用例 | 直接拼接上下文实现快，但易受 prompt injection | 恶意 Runbook 不改变工具策略 | R-D1/R-C2 | Planned |

### E. 独立评测、指标与 CI

| ID | 问题或需求 | 技术手段 | 最近替代方案与取舍 | 验收证据 | 依赖 | 状态 |
|---|---|---|---|---|---|---|
| R-E1 | 没有 LLM 时也要证明评测链路有效 | 固定规则/脚本化 baseline、合法与错误报告 fixture | 一开始只接 LLM 会把模型问题与评测器问题混在一起 | baseline 可从 case 到 report 再到 evaluator | R-A2/R-B2 | Planned |
| R-E2 | 只看根因准确率会掩盖证据和拒答问题 | Top-k、macro-F1、evidence P/R、coverage/selective risk、工具效率；citation integrity 与语义支持度分层 | 单一总分易掩盖安全失败和数据分布差异 | 指标单元测试、小样本手算；引用存在/checksum/source/version/可见性硬门禁，相关性进入证据质量 | R-E1 | Planned |
| R-E3 | 质量或安全回归必须阻断 | 硬门禁先行；基线后再定相对质量阈值；CI 固定 fixture | 预写准确率阈值没有实验依据 | Schema/策略/泄漏/引用门禁与回归报告 | R-E2 | Planned |
| R-E4 | 单次 LLM 运行不能证明某个 Agent 更好 | A0/A1 调查配置包对照、A1/A2 RAG 消融、VariantManifest、case-level paired delta、分层重复 pilot、失败分母 | 多框架、多模型同时变化看似丰富，但无法归因 | 预注册 manifest/stat plan、全部 scheduled runs、多维 scorecard；默认不承诺 winner，允许 `inconclusive` | R-E1/R-E2/R-C4 | Planned |

### F. 泛化、发布与演示

| ID | 问题或需求 | 技术手段 | 最近替代方案与取舍 | 验收证据 | 依赖 | 状态 |
|---|---|---|---|---|---|---|
| R-F1 | 同一数据分布内的结果不能证明泛化 | 核心数据 held-out system；RCAEval 使用 group-aware 三轮 LOSO；外部冻结子集为门禁通过后的可选项 | 混合后随机切分易产生近重复和调参泄漏 | dev/每轮 outer system 分报且 outer 不反向调参；external 若存在则单列 | R-B1/R-E2/R-E4 | Planned |
| R-F2 | 作品必须能被他人复现和核验所有权 | 环境锁定、ADR、data card、eval report、坏案例、5 分钟 demo | 只展示录屏或 README 无法证明实现与调试能力 | 干净环境最小运行、成功/失败案例、声明可追溯 | 所有核心项 | Planned |

## 6. 里程碑与退出门槛

### MS-0 — Foundation（目标窗口：第 1 周附近）

- **Outcome**：项目问题、边界、合规和学习门禁清楚；作者先对一个真实 replay case 建立直观认识。
- **Learning orientation**：按 [N00](learning/nodes/N00_CLOUDOPSBENCH_ORIENTATION.md) 完成固定 Cloud-OpsBench 教学 case。先冻结人工调查，再运行一次真实上游 ReAct 轨迹并冻结其 allowlist 投影，最后才揭示真值进行比较。这个 case 永久为 `tutorial/dev-only`，不进入指标或 held-out split。
- **Exit gate**：N00 完成后，作者无提示说明 evaluator 是主产品、Reference Agent 是首个受控 SUT、为何二者都要交付，并用刚观察的 case 解释 replay-first、Ground Truth 隔离、RAG 子系统、`SystemKnowledgePack`、只读工具边界和一个替代方案代价。
- **Deferred**：项目自己的 Schema、replay/Agent/evaluator 实现，以及公开数据性能评测。
- **状态**：In progress。当前执行 N00A；尚未运行真实模型，也未揭示 Ground Truth。

### MS-1 — Contracted replay slice（第 1～3 周目标窗口）

- **Outcome**：不依赖 LLM 的最小 case → replay → report → validator 纵向切片。
- **Requirements**：R-A1～R-A4、R-B1～R-B3、R-E1。核心纵向切片先且只使用原创 clean-room fixture。
- **Exit gate**：一个手工 clean-room fixture 可由 `FixtureAgentDriver` 生成预设合法拒答并进入 validator/evaluator；Ground Truth 隔离测试通过，最小 `AgentDriver`/`RunRecord`/`BenchmarkSpec` 接缝有契约样例。之后才能用一个不同于 N00、从未揭示过答案的公开 case 做 formal smoke；它必须先通过 data card、许可/provenance 和双视图 adapter 审查，并走同一 runner/evaluator。MS-1 不实现 controller/Policy，不报告 benchmark 性能。
- **Deferred**：公开数据批量接入、模型 Agent 和数据集兼容性声明。

### MS-2 — Restricted reference Agent（第 3～6 周目标窗口）

- **Outcome**：项目自有 controller、ScriptedPolicy 和一个 LLMPolicy 形成最小参考 Agent；A0/A1 可进行调查配置包比较。
- **Requirements**：R-C1～R-C4。
- **Exit gate**：Fixture/Reference drivers 共用同一 evaluator；allowlist、预算、错误/超时、非法 PolicyDecision、恶意 driver 和结构化事件测试通过；至少一个假设因新证据被支持、削弱或拒绝；模型供应商选择有 ADR。
- **Deferred**：自动修复、通用 shell 和 live 集群依赖。

### MS-3 — Knowledge and evaluation baseline（第 5～8 周目标窗口）

- **Outcome**：Runbook RAG、A0/A1 调查配置包比较、A1/A2 RAG 消融、诊断质量与坏案例形成第一份可重复报告。
- **Requirements**：R-B1、R-B3、R-D1～R-D2、R-E2、R-E4。
- **Exit gate**：第三方数据先通过许可、checksum、data card 和 provenance 门禁；冻结并保存 A0/A1/A2 variant manifests，A0/A1 明标为 end-to-end 调查配置包对照，机器 diff 证明 A1/A2 只改变一种计入预算的 RAG capability/corpus；同 case paired report 保留全部 scheduled runs、completion 与 failure denominator，默认不宣称 winner；引用可核验，RAG 指标与端到端指标分开，scorecard 不用单一总分；至少完成一次错误分类与修正。
- **Deferred**：复杂 UI、多个 Agent、LLM judge 作为事实裁判。

### MS-4 — Generalization and gates（第 8～11 周目标窗口）

- **Outcome**：held-out system、随机性 pilot 和可选跨数据集验证，硬门禁进入 CI。
- **Requirements**：R-E3、R-E4、R-F1。
- **Exit gate**：内部开发、held-out system 和可选 external 结果分报；若核心集为 RCAEval，三份预冻结 outer split manifests 与三轮结果全部存在，fault/near-duplicate group 不跨边界，dev 与每个 outer fold 分报，首次查看 outer 结果后 variant/prompt/RAG/阈值 hash 保持不变；若只完成一轮，只能标为 single held-out，不能将 R-F1 设为 Done。另须冻结 exact N≥20 的分层重复 pilot，报告独立 case 数、重复数、flip、completion、失败、成本和 case-clustered 区间；数据许可与切分经审查，质量阈值只用 dev 制定并在 held-out 前冻结。
- **Deferred**：大规模 live benchmark；LangGraph Adapter 是进度允许时的可选项，不属于退出门槛。

### MS-5 — v0.1 evidence package（第 10～12 周目标窗口）

- **Outcome**：可公开、可复现、可面试追问的证据包。
- **Requirements**：R-F2。
- **Exit gate**：干净环境可运行最小演示；README、ADR、数据卡、报告、坏案例和 5 分钟 demo 互相可追溯。
- **Deferred**：生产化承诺、自动修复、通用评测平台和竞赛 Agent 迁移。LangGraph 薄适配器未完成不阻塞发布。

## 7. 阶段复审与决策点

- **MS-1 末**：契约、真值隔离、恶意 driver 和指标小样本能否触发预期门禁/变化；再用一个未揭示公开 case 做 formal smoke，验证 adapter 接缝而非性能；不选择最终模型供应商。
- **MS-2 入口**：完成 `PolicyDecision` 契约和三个 synthetic capability case 后，再依据结构化输出、工具调用、成本和可用性选择首个模型供应商并新增 ADR。
- **MS-3 末**：决定是否接入外部数据集；仅在许可、映射、资源和时间门禁通过时选择一个冻结候选，无合格候选不阻塞 v0.1；同时判断 RAG 是否带来可测增益或新失败。
- **MS-4/5**：只有核心门禁和报告不受影响时，才实现可选 LangGraph Adapter；否则推迟到 v0.2。
- **MS-5 末**：根据资源与 JD 证据，在 AIOpsLab 的 5～10 个只读 live smoke case 与一个竞赛 Agent 迁移实验之间选择一个下一阶段切片，不并行增加第二主项目。

影响输出契约、Ground Truth 边界、工具权限、数据许可、CI 阈值或三个通用接缝的变更必须新增 ADR。具体模型和 API 必须可替换，并记录版本、参数、成本和重复运行方差。当前主产品与框架选择见 [ADR-0001](adr/0001-evaluator-first-reference-agent.md)。

## 8. v0.1 之后的条件性方向

- **竞赛 Agent portability experiment**：只有确定公开规则、任务 I/O、允许动作、评分、许可和隐藏测试边界后才立项；时间盒一至两周，一个 Agent、一个任务切片、一个 adapter、一个 compatibility/evaluation report。优化只读 train/dev 反馈；sealed/hidden test 只作一次或受限确认，不进入 prompt、RAG、cache、trace 或逐轮调参，leaderboard 不能当 case-level truth。若 Agent 执行代码或有写操作，必须新增 sandbox、网络/资源限制和 side-effect policy，不能放松 incident read-only 边界。
- **现有观测平台 exporter**：项目自有 `RunRecord` 保持运行行为 canonical；未来只能从字段 allowlist 的 pre-evaluation projection 导出 OpenTelemetry/OpenInference trace 到 Phoenix、Langfuse 或 LangSmith，不自建 trace viewer，且必须有 GT canary/credential/restricted-payload 阻断测试。
- **抽象门禁**：第二个真实任务先实现自己的领域 evaluator；只有两个领域暴露出重复结构后，才考虑抽出 `CaseEnvelope`、`EnvironmentPort` 或更多插件协议。
- **公开声明**：一次第二领域接入只能称为“一次跨任务复用验证”，不能称为支持任意 Agent 或通用 Agent 评测平台。

## 9. 当前门槛

- 当前里程碑：MS-0 — In progress。
- 当前学习节点：N00A — 对固定 Cloud-OpsBench case 完成人工只读调查并冻结报告。
- 当前唯一动作：打开 [`00_cloudopsbench_orientation.ipynb`](../notebooks/00_cloudopsbench_orientation.ipynb)，运行到 N00A 冻结检查；不揭示 Ground Truth。
- 后续顺序：等待模型凭据 → N00B 真实 ReAct 运行 → N00C 冻结后比较 → N01 轨迹评测缺口。不得直接跳到 Schema。

每日状态见 [`STATE.md`](../STATE.md)，问题定义见 [`PROJECT_BRIEF.md`](PROJECT_BRIEF.md)，第三方边界见 [`NOTICE.md`](../NOTICE.md)。
