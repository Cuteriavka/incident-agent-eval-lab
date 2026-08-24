# Project Roadmap：Incident Agent Evaluation Lab

> 状态：Active planning baseline  
> 版本：0.1  
> 最近审查：2026-08-25

本路线图提前说明项目要解决的问题、真实场景、需求、技术手段和验收证据。十二周是目标窗口，不是按日期锁死的课程表；只有通过当前退出门槛才进入下一里程碑。窗口落后时缩小可选范围，不跳过门禁，也不形成“补课债”。

## 1. 问题与交付承诺

静态日志分类或一次性自然语言回答不能证明诊断系统会主动验证假设，也难以核验引用是否真实、工具行为是否安全、不同版本能否公平回归。

v0.1 同时交付：

1. **最小参考诊断 Agent**：从有限症状出发，在预算内提出假设、调用注册的只读探针、更新判断并发布诊断或拒答。
2. **独立评测器**：不依赖 Agent 自述，校验结构化契约、Ground Truth 隔离、证据引用、工具策略、诊断质量和运行成本。
3. **离线 replay 环境**：对版本化事故证据进行确定性回放，支持失败复现和版本比较。

Runbook RAG 是可独立评测的知识子系统。Kubernetes 是首个系统环境，不是项目永久边界；不同组件知识通过版本化 `SystemKnowledgePack（系统知识包）` 和数据适配器接入。

v0.1 不做自动修复、任意 shell/kubectl、复杂 UI、多 Agent 平台或生产适用性宣传。

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
 Reference Agent ──read-only probes
          │
          ▼
  DiagnosisReport@1
          │
          └───────────────► Independent evaluator
                                   │
                                   ▼
                     gates + metrics + bad cases
```

ingestion 必须生成两个隔离视图：Agent runtime 只能取得 incident/evidence view；evaluator 只能在报告产生后，使用不编码答案的 opaque join key 通过 evaluator-only truth loader 加载 Ground Truth。Agent 包不得导入 truth loader。Ground Truth 不能通过字段、文件名、case ID、路径、manifest、检索索引、提示或工具结果泄漏。

## 3. 核心场景

| ID | 初始状态 | 系统行为 | 可观察结果 |
|---|---|---|---|
| S1 证据不足 | 只有告警或测试失败，现有证据无法区分候选原因 | Agent 在预算内查询允许的探针，保留未消除的不确定性 | 返回 `insufficient_evidence`，candidate cause 必须为 0，并列出限制和下一项只读检查 |
| S2 可诊断事故 | replay case 含可区分根因的多源证据 | Agent 提出少量假设，选择能区分它们的探针并更新置信度 | `diagnosed` 包含 1～3 个排序原因，每个原因至少一条可核验 evidence ref |
| S3 工具或安全失败 | 请求未知工具、越权参数、超时，或日志/Runbook 含恶意指令 | 工具层 fail closed；模型文本不能覆盖结构化错误 | 产生可审计的拒绝、超时或失败事件，策略违规为 0 |
| S4 版本回归比较 | 同一 case 和证据快照运行不同模型、prompt、策略或知识包 | 固定 replay 输入和评测版本，记录非确定性参数 | 结果可复现比较；外部 LLM 的方差单独报告，不承诺逐字一致 |
| S5 泛化验证 | 未见系统或另一公开数据集的冻结子集 | 通过适配器映射统一契约，不让外部样本反向调参 | 内部、留一系统和跨数据集结果分别报告，不合并成一个总分 |

## 4. 需求到证据矩阵

状态使用 `Planned / In progress / Blocked / Done`。`Done` 只表示工程退出门槛通过，不自动表示作者已达到面试可辩护水平。

### A. 契约与领域边界

| ID | 问题或需求 | 技术手段 | 最近替代方案与取舍 | 验收证据 | 依赖 | 状态 |
|---|---|---|---|---|---|---|
| R-A1 | 不同数据源需要稳定、版本化的 Agent 输入 | `IncidentCase@1` 字段规则、JSON Schema、版本字段 | 任意 Python `dict` 起步快，但无法统一验证和演进 | 合法/非法 fixture、schema test、兼容性说明 | MS-0 | Planned |
| R-A2 | Agent 输出必须可机器验证且允许拒答 | `DiagnosisReport@1`、枚举状态、证据引用、独立 validator | 纯自然语言更自由，但无法建立硬门禁 | diagnosed 1～3 原因/拒答 0 原因/坏引用三类测试 | R-A1 | Planned |
| R-A3 | 真值不得污染被测系统 | 两个隔离视图、opaque join key、evaluator-only truth loader、依赖边界测试 | 同一 JSON 内隐藏字段仍可能被提示或工具读到 | Agent 包不可导入 truth loader；字段、文件名、manifest、索引和 API 泄漏测试 | R-A1 | Planned |

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

### D. Runbook RAG 子系统

| ID | 问题或需求 | 技术手段 | 最近替代方案与取舍 | 验收证据 | 依赖 | 状态 |
|---|---|---|---|---|---|---|
| R-D1 | 诊断需要可追溯知识，而非模型记忆 | 文档切分、检索、来源/版本引用、检索结果契约 | 通用问答 RAG 容易把项目重心移到 UI 和聊天 | 检索 recall/precision、引用存在性、错误文档案例 | R-C3 | Planned |
| R-D2 | 文档内容可能包含恶意或无关指令 | 文档视为不可信数据、指令/证据通道分离、安全用例 | 直接拼接上下文实现快，但易受 prompt injection | 恶意 Runbook 不改变工具策略 | R-D1/R-C2 | Planned |

### E. 独立评测、指标与 CI

| ID | 问题或需求 | 技术手段 | 最近替代方案与取舍 | 验收证据 | 依赖 | 状态 |
|---|---|---|---|---|---|---|
| R-E1 | 没有 LLM 时也要证明评测链路有效 | 固定规则/脚本化 baseline、合法与错误报告 fixture | 一开始只接 LLM 会把模型问题与评测器问题混在一起 | baseline 可从 case 到 report 再到 evaluator | R-A2/R-B2 | Planned |
| R-E2 | 只看根因准确率会掩盖证据和拒答问题 | Top-k、macro-F1、evidence P/R、coverage/selective risk、工具效率 | 单一总分易掩盖安全失败和数据分布差异 | 指标单元测试、小样本手算、分组报告 | R-E1 | Planned |
| R-E3 | 质量或安全回归必须阻断 | 硬门禁先行；基线后再定相对质量阈值；CI 固定 fixture | 预写准确率阈值没有实验依据 | Schema/策略/泄漏/引用门禁与回归报告 | R-E2 | Planned |

### F. 泛化、发布与演示

| ID | 问题或需求 | 技术手段 | 最近替代方案与取舍 | 验收证据 | 依赖 | 状态 |
|---|---|---|---|---|---|---|
| R-F1 | 同一数据分布内的结果不能证明泛化 | RCAEval 留一系统；经许可审核后选择一个外部冻结子集 | 混合后随机切分易产生近重复和调参泄漏 | 内部/留一系统/外部结果分报 | R-B1/R-E2 | Planned |
| R-F2 | 作品必须能被他人复现和核验所有权 | 环境锁定、ADR、data card、eval report、坏案例、5 分钟 demo | 只展示录屏或 README 无法证明实现与调试能力 | 干净环境最小运行、成功/失败案例、声明可追溯 | 所有核心项 | Planned |

## 5. 里程碑与退出门槛

### MS-0 — Foundation（目标窗口：第 1 周附近）

- **Outcome**：项目问题、边界、合规和学习门禁清楚。
- **Exit gate**：约 10 分钟复验中，AI 先用具体 case 讲解 5～7 分钟；作者随后无提示口述约 2 分钟，必须正确画出 Agent/evaluator/GT 数据流，解释 replay-first、RAG 子系统、`SystemKnowledgePack`、只读工具边界和一个替代方案代价；剩余时间用于边界追问和记录。
- **Deferred**：Schema、数据和 Agent 代码。
- **状态**：In progress。文档已完成，口述 Ownership 仍需复验。

### MS-1 — Contracted replay slice（第 1～3 周目标窗口）

- **Outcome**：不依赖 LLM 的最小 case → replay → report → validator 纵向切片。
- **Requirements**：R-A1～R-A3、R-B2、R-E1。这里只使用原创 clean-room fixture；第三方 adapter 与许可门禁留到 MS-3。
- **Exit gate**：一个手工 clean-room fixture 可加载、回放并生成合法拒答；Ground Truth 隔离测试通过。
- **Deferred**：公开数据批量接入和模型 Agent。

### MS-2 — Restricted reference Agent（第 3～6 周目标窗口）

- **Outcome**：最小参考 Agent 能用只读探针验证假设。
- **Requirements**：R-C1～R-C3。
- **Exit gate**：allowlist、预算、错误/超时和结构化事件测试通过；至少一个假设因证据更新。
- **Deferred**：自动修复、通用 shell 和 live 集群依赖。

### MS-3 — Knowledge and evaluation baseline（第 5～8 周目标窗口）

- **Outcome**：Runbook RAG、诊断质量与坏案例形成第一份可重复报告。
- **Requirements**：R-B1、R-B3、R-D1～R-D2、R-E2。
- **Exit gate**：第三方数据先通过许可、checksum、data card 和 provenance 门禁；引用可核验，RAG 指标与端到端指标分开，至少完成一次错误分类与修正。
- **Deferred**：复杂 UI、多个 Agent、LLM judge 作为事实裁判。

### MS-4 — Generalization and gates（第 8～11 周目标窗口）

- **Outcome**：留一系统和跨数据集验证，硬门禁进入 CI。
- **Requirements**：R-E3、R-F1。
- **Exit gate**：内部、留一系统和外部结果分报；数据许可与切分经审查；质量阈值有基线依据。
- **Deferred**：大规模 live benchmark。

### MS-5 — v0.1 evidence package（第 10～12 周目标窗口）

- **Outcome**：可公开、可复现、可面试追问的证据包。
- **Requirements**：R-F2。
- **Exit gate**：干净环境可运行最小演示；README、ADR、数据卡、报告、坏案例和 5 分钟 demo 互相可追溯。
- **Deferred**：生产化承诺与自动修复。

## 6. 阶段复审与决策点

- **MS-1 末**：契约、真值隔离和指标小样本是否真的能区分正确与错误实现。
- **MS-3 末**：选择一个许可证明确的外部数据集；决定 RAG 是否带来可测增益。
- **MS-5 末**：根据资源与 JD 证据决定是否增加 AIOpsLab 的 5～10 个只读 live smoke case。

影响输出契约、Ground Truth 边界、工具权限、数据许可或 CI 阈值的变更必须新增 ADR。具体模型和 API 必须可替换，并记录版本、参数、成本和重复运行方差。

## 7. 当前门槛

- 当前里程碑：MS-0 — In progress。
- 当前唯一动作：完成带讲解的 Day 1 Ownership 口述复验。
- 复验通过后的动作：Day 2A 只理解数据契约、provenance 和 Ground Truth 隔离，产出字段/规则表及两个普通 JSON；不写 JSON Schema。

每日状态见 [`STATE.md`](../STATE.md)，问题定义见 [`PROJECT_BRIEF.md`](PROJECT_BRIEF.md)，第三方边界见 [`NOTICE.md`](../NOTICE.md)。
