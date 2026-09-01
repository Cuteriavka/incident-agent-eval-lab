# N00｜先观察一次真实的回放诊断

> 状态：Ready（N00A 可执行；N00B 等待学习者提供模型凭据）
> 上一站：项目定义
> 下一站：[N01｜从调查轨迹中发现评测缺口](N01_TRAJECTORY_GAPS.md)
> 今日入口：在仓库根目录运行 `.\.venv\Scripts\python.exe scripts\start_n00.py`，打开仓库外工作副本

## 1. 这一节点解决什么问题

此前的路线直接从 `IncidentCase`、replay、Ground Truth 隔离等抽象设计开始，你很难判断它们究竟要解决什么。N00 先倒过来：观察一个真实事故样本，亲手查询有限的只读证据，再观察一次上游 ReAct Agent 的调查轨迹。等你亲眼见到“它看到了什么、为什么查这个、哪里证据不足、最后如何作答”，N01 才讨论怎样评测这段过程。

本节点形成三个不可变 artifact：N00A 的人工 `orientation_report`、N00B 的 Agent `trajectory_projection`、N00C 的 `orientation_comparison`。它们不是 benchmark 分数，也不证明本项目已经支持 Cloud-OpsBench，更不证明某个 Agent 的准确率。

## 2. 具体案例和输入输出

固定案例是 Cloud-OpsBench 的 `trainticket/service/1`。项目准备脚本只把以下内容放进 **pre-reveal** 视图：

- 初始症状：`Partial Service Unreachability.`；
- 允许调用的只读工具名称、参数和描述；
- 只有在你发起合法工具调用后才返回的缓存观察结果。

你要生成的核心输出不是一句猜测，而是一条可追溯链：

```text
初始症状
  -> 选择只读探针
  -> 得到观察 observation
  -> 写出证据引用 evidence ref
  -> 更新假设
  -> 冻结人工诊断
```

N00B 再让一个上游 ReAct Agent 面对同一 pre-reveal 输入。人工诊断和 Agent 轨迹投影都冻结后，N00C 才能打开 **compare-only** 视图进行对照。

## 3. 先建立四个概念

### 3.1 症状不是根因

症状是当前可见的异常，例如“部分服务不可达”。它说明哪里表现不正常，却没有说明是服务进程、配置、依赖、网络还是平台资源导致。只复述症状，不构成诊断。

### 3.2 observation 不是 evidence

`observation` 是工具返回的原始或整理后的观察；`evidence` 是你在报告中明确引用、并用来支持或削弱某个判断的那部分观察。同一段工具输出可能含很多字段，但只有与假设有关、能被再次定位的内容才成为本次论证中的证据。

### 3.3 Ground Truth 不是给 Agent 的提示

Ground Truth 是 evaluator 在报告冻结后使用的答案或标注。若它提前出现在字段、文件名、路径、提示、RAG、工具结果或轨迹里，Agent 就可能“看答案作答”，评测失效。本教程采用仓库外的目录分区与 reveal 流程门禁：这不是不同用户权限形成的强安全隔离，但能让代码在冻结条件不满足时 fail closed。formal smoke 才会实现更强的运行时视图隔离。

### 3.4 replay-first 是可控的调查环境

这里的 replay 不是播放一段固定文本，而是：面对同一事故快照，同一个合法探针请求总能返回同一份缓存观察。它牺牲了 live 环境中的即时变化，换来安全、可重复和便于回归比较。最近的替代方案是直接连接真实 Kubernetes；它更接近生产，但会带来状态漂移、权限、副作用和无法复现的问题，所以不适合作为 v0.1 的第一环境。

## 4. Cloud-OpsBench 在这里扮演什么角色

Cloud-OpsBench 提供事故状态快照、缓存工具响应和上游 Agent 示例。它是本项目要观察的外部系统，不是本项目的实现。N00 使用固定上游版本和固定案例；第三方 checkout、缓存、标签、原始轨迹及派生 payload 全部保存在仓库外。

项目不直接调用上游随机选 case 的 `interact.py`，而是用自己的教学包装器固定选择 `benchmark/trainticket/service/1`。这样你的人工调查与 Agent 调查面对的是同一输入，之后才能比较“调查路径差异”，而不是把 case 差异误当成 Agent 差异。

数据来源、版本、许可证和校验和记录见 [Cloud-OpsBench 数据教程](../../data/CLOUDOPSBENCH_TUTORIAL.md)。上游资料以 [Cloud-OpsBench 仓库](https://github.com/LLM4Ops/Cloud-OpsBench) 为准。

## 5. N00A：人工调查，不需要模型 API

不要直接运行 Git 跟踪的 starter notebook。运行本节顶部的一条启动命令，它会把 starter 复制到仓库外，并在那里启动 JupyterLab；原始探针输出只会保存在外部工作副本。看到固定 `case_ref`、症状和 9 个工具族即表示准备就绪。

按顺序运行到 N00A。今天只完成一个 TODO：填写 `orientation_report`。先按工具族和参数关键词把 1680 个注册调用筛成最多 10 个候选，再选择 3～6 个有区分力的探针。每次都写清五件事：

| 字段 | 你要回答的问题 |
|---|---|
| `step` | 这是第几步？ |
| `probe_ref` | 调用了哪个已注册工具与参数？ |
| `observation_summary` | 返回结果中看到了什么？只用自己的话概括。 |
| `effect_on_hypothesis` | 这条观察支持、削弱还是无法区分哪个候选？ |
| `why_next` | 为什么下一步要继续这样查？ |

一个合理的调查不是“把所有工具跑一遍”。先写两个以上仍可能成立的候选解释，再选择最能区分它们的探针。如果某个查询不能改变下一步，就把它标为低价值或冗余查询。

人工报告至少包含：

- `symptom`：初始症状；
- `case_ref` 与 `tutorial_manifest_sha256`：把人工报告绑定到当前固定 case 与准备版本；
- `initial_hypotheses`：查询前至少两个仍可能成立的候选解释；
- `steps`：顺序编号、`probe_ref`、观察摘要、对假设的影响和下一步理由；
- `frozen_diagnosis`：当前最可能解释，或 `insufficient_evidence`；
- `limitations`：尚未看到什么，因此还不能确定什么；
- `probe_value_assessment`：引用一个高价值和一个低价值探针，并分别说明理由。

完成后运行冻结单元格。脚本会校验引用是否来自允许的工具返回，并生成不可变 hash。这个 hash 不是证明你“答对了”，而是证明你没有在看到答案后悄悄改写先前判断。

## 6. 为什么此时必须暂停

N00A 冻结后，状态进入：

```text
N00A -> N00-WAITING-KEY -> N00B -> N00C -> N01
```

目前没有模型 API Key，所以你应停在 `N00-WAITING-KEY`。这不是学习失败，也不需要重做 N00A。更不能为了继续而提前揭示 Ground Truth。

## 7. N00B：观察一次真实 ReAct 轨迹

取得一个由你提供的 OpenAI-compatible API 凭据后，运行项目包装器，而不是把 key 写入上游 YAML。包装器从环境变量读取凭据，在内存中构造调用参数，固定 case 和最大步数，并把原始轨迹留在仓库外。runner 代码直接来自已校验 pinned ZIP 的仓库外 `runner_code_view`，其 workspace 指向同次准备生成的 `agent_run_view`：它保留诊断所需 snapshot，却使用不含 `metadata.result` 的 metadata，且不包含 process label 或 golden trajectory。

N00B 解锁时只做三步配置：

1. 复制 `.n00b.local.example.json` 为 Git 已忽略的 `.n00b.local.json`，只填写外部结果目录、HTTPS endpoint、模型名、最大步数和“保存 key 的环境变量名”；这里绝不能写 key 值。
2. 在当前 PowerShell 进程隐藏输入 key：`[Environment]::SetEnvironmentVariable('YOUR_PROVIDER_API_KEY', (Read-Host 'API key' -MaskInput), 'Process')`。变量名必须与本地 JSON 的 `api_key_env` 一致。
3. 复制 notebook readiness 单元显示的绝对路径 `--preflight` 命令；通过后去掉 `--preflight`，只执行一次真实运行。

远程 endpoint 必须使用 HTTPS；HTTP 只允许本机 loopback。preflight 会在把 key 交给上游客户端前重新校验 human freeze、manifest、从 pinned ZIP 提取的 runner 代码树、外部路径、预算和既有 trace。

这一小节关注 ReAct 的最小闭环：模型先根据当前信息提出一个动作，环境执行允许的只读工具，再把新观察交还模型，直到它发布 final answer 或耗尽步数。我们不把模型的隐藏思维当证据；能够审计的是工具名、参数、工具返回引用、终止原因和最终报告。

N00B 的通过条件是：

1. 至少一次真实模型调用成功，并产生一个可解析的合法动作或 final answer；
2. 所有工具调用都在冻结 allowlist 中，终止原因是 `final_answer` 或明确记录的 `max_steps`；
3. 只保存 allowlist 允许的 `trajectory_projection`，并冻结其 hash。

Agent 可以诊断错误。一个结构合法但推理路径有缺陷的真实轨迹，正是 N01 需要的材料。认证失败、额度不足、模型不可用或零成功调用则不算通过。

自动门禁只能证明“项目 wrapper 记录了非空模型响应，并形成绑定 manifest 的合法轨迹”，不能对远程 provider 做密码学意义的调用证明。是否真的发生远程调用还要由你观察终端成功状态并核对 provider 的私有用量记录；这属于 Ownership Check，不进入公开仓库，也不能由 synthetic 单元测试替代。

## 8. 轨迹为什么只能保存投影

上游原始轨迹可能混有完整 prompt、原始工具输出、绝对路径和 API 信息。N00B 只生成项目定义的私有投影：case ref、冻结的模型/配置/预算引用、终止原因、有序工具名与参数、匹配的 `probe_ref`、观察值 hash、final answer，以及非敏感 token/延迟合计。观察摘要来自人工报告或 N00C 的原创比较，不从第三方 raw observation 自动复制。该投影和其他 N00 生成物都留在仓库外；独立 public-export 门禁实现前不得提交 Git。

以下内容一律不得进入仓库：`metadata.result`、完整 prompt、原始 observation/tool cache、process label、golden trajectory、原始模型输出、绝对路径、带凭据的 endpoint 和任何 secret。

## 9. N00C：冻结之后再比较

只有合法人工诊断、经 N00B wrapper 校验的 Agent 投影、二者 hash 与运行 marker 全部匹配时，compare-only loader 才能打开真值与过程标注。你随后填写并冻结独立的 `orientation_comparison`，只写项目原创的差异摘要，不复制第三方 payload 或 Ground Truth 原文：

- 人和 Agent 的结论分别是什么；
- 哪一步证据最有区分力；
- 哪个探针有用，哪个低价值或冗余；
- 即使 final answer 正确，调查过程还有什么风险；
- 下一节点需要哪些 evaluator 检查。

揭示后的案例永久标记为 `tutorial/dev-only`。它不能再进入 Agent prompt、RAG 索引、正式 fixture、held-out split 或性能指标。

## 10. 完成标准与边界

N00A 当前只检查三件事：

1. 报告必填字段存在，且每条证据引用都来自已注册探针；
2. 你能解释一个高价值探针和一个低价值探针；
3. 人工诊断已冻结；Git 跟踪的 starter notebook 保持空输出，实际工作副本与所有第三方输出位于仓库外。

完整 N00 还要求 N00B 的真实轨迹投影通过校验，并在 N00C 写出 human-vs-Agent 差异。单个案例无论答对与否，都不能形成准确率、泛化、兼容性或“更好 Agent”的公开结论。

### 交给 N01 的输入

N01 只能读取：冻结的 `orientation_report`、去除 Ground Truth 的 `trajectory_projection`，以及不复述真值的 `orientation_comparison`。它不能读取上游原始轨迹或第三方原始 payload。

### 你完成后应能回答

- replay-first 为什么适合本项目的第一阶段？
- 为什么 observation 不能自动等于 evidence？
- 为什么必须先冻结人和 Agent 的输出，再揭示 Ground Truth？
- 一个 final answer 正确的 Agent，调查过程仍可能差在哪里？
