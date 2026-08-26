# Contributing to incident-agent-eval-lab

本仓库采用轻量的 Issue 驱动开发流程。它的目标是让每项改动都能回答“为什么做、改了什么、如何验证”，并形成可追踪的项目与学习证据。

## 文档职责

- [`AGENTS.md`](AGENTS.md) 定义仓库工作约定和不可绕过的产品边界。
- [`docs/PROJECT_BRIEF.md`](docs/PROJECT_BRIEF.md) 定义项目问题、范围和成功标准。
- [`docs/PROJECT_ROADMAP.md`](docs/PROJECT_ROADMAP.md) 管理长期里程碑、需求和退出门槛。
- [`STATE.md`](STATE.md) 只记录当前阶段、当前门槛和学习主线的唯一下一动作。
- [`NOTICE.md`](NOTICE.md) 定义 clean-room、第三方署名和数据许可边界。
- Issue 描述一个当前可执行、可验收的问题。
- Pull Request（PR）提供该问题的实现、验证和取舍证据。

Roadmap 条目不会被一次性批量转换为 Issues。里程碑或学习交付只有在前置门禁通过、任务成为当前动作时才创建对应 Issue。bootstrap、仓库维护和真实缺陷可以单独建立 Issue，但不得借此宣称里程碑推进或绕过 `STATE.md` 的学习门禁。纯阅读、私人求职信息和不产生仓库证据的活动不进入公开 Issue。

建立本流程的 bootstrap Issue 属于仓库治理，不代表 MS-0 前进，因此不修改 `STATE.md`。

## 完整更新流程

### 1. 创建 Issue

选择“项目任务”或“缺陷报告”模板。填写背景、项目位置、输入输出、范围、非目标和最多三条验收标准。

Issue 不得包含公司代码、日志、架构、规则、客户信息、凭据或其他非公开材料，也不得粘贴 sealed/hidden Ground Truth payload。第三方 raw/derived payload 默认不提交；任何例外必须由 data card 明确证明再分发许可，并记录官方来源、版本、许可证、checksum、允许用途和分发限制。Ground Truth 必须与所有 Agent-visible artifacts 和 channels 隔离，Agent 包不能访问 evaluator-only truth loader。

### 2. 从最新 main 创建短分支

```powershell
git switch main
git pull --ff-only origin main
git switch -c <type>/<issue-number>-<short-description>
```

常用分支类型：

- `feat`：新增可观察能力；
- `fix`：修复缺陷；
- `docs`：只修改文档；
- `test`：增加或修正测试；
- `chore`：流程、工具或维护工作。

一个分支只处理一个主要 Issue。不要在已 Squash merge 的旧分支上继续下一项工作。

### 3. 小步提交并推送

提交信息说明一个逻辑变化，例如：

```text
docs: define contribution workflow
test: reject ground truth in agent-visible case
fix: enforce probe budget before execution
```

推送新分支：

```powershell
git push -u origin <branch-name>
```

### 4. 创建 Pull Request

PR 以 `main` 为目标分支，并在描述中填写：

```text
Closes #<issue-number>
```

同时记录实际验证证据、明确未修改的范围、`STATE.md` 是否需要更新，以及 clean-room、第三方许可、Ground Truth 和公开声明检查结果。

### 5. Review 与合并

确认 Issue 验收标准有可观察证据，且 P0/P1 风险已经解决：P0 指隐私、凭据、公司资料、Ground Truth、许可或危险写操作风险；P1 指改动不可执行、无法证明验收、破坏接口或产生无证据公开声明。个人项目默认使用 Squash merge，使一个 PR 在 `main` 上对应一个逻辑提交。

输出契约、Ground Truth 边界、工具权限、数据许可、CI 阈值或 `AgentDriver`、`RunRecord`、`BenchmarkSpec` 三个通用接缝的变更，必须先创建 `type:decision` Issue 并产出 ADR，不能夹带在普通 task PR 中。

PR 合入 `main` 后，正确关联的 Issue 会自动关闭。若没有自动关闭，先检查 PR 是否以默认分支为目标，以及 `Closes #<number>` 是否引用了正确 Issue。

### 6. 同步本地 main

```powershell
git switch main
git pull --ff-only origin main
git branch -d <merged-branch-name>
```

删除本地分支前先确认 PR 已合入；远端分支可以在 GitHub PR 页面删除。

## 标签

| 标签 | 用途 |
|---|---|
| `type:task` | 有明确产物和验收标准的项目任务 |
| `type:bug` | 可复现的错误或回归 |
| `type:decision` | 需要形成明确取舍的决定；仓库规定的关键边界变更必须产出 ADR |
| `area:docs` | 项目文档与公开说明 |
| `area:contracts` | 数据契约、Schema 和 validator |
| `area:data` | 数据适配、provenance 和许可证 |
| `area:agent` | Reference Agent、Policy 和工具调用 |
| `area:evaluation` | evaluator、指标、实验与报告 |
| `status:blocked` | 前置门禁或外部依赖尚未满足 |

标签只用于检索，不替代 Issue 中的上下文和验收标准。当前阶段不使用 GitHub Projects、Sprint 或工作量估算。

## 完成与 Ownership

文件存在或测试通过不自动等于任务完成。关闭 Issue 只说明工程验收已经完成，不自动表示作者达到 `Defendable`、满足某条 JD 或已经掌握相关能力。Ownership 未经实际口述和追问，只能记录为未检查；执行后应在 PR、`STATE.md` 或其他可追踪 artifact 中留下简短结果或引用。

关闭 Issue 前还应确认：

1. 验收结果能证明 Issue 描述的问题，而不只是证明命令成功。
2. 若声称 Ownership 已通过或能力达到 `Defendable`，作者必须能解释关键选择、预测一个边界输入，并说明最近替代方案的代价；否则将 Ownership 保持为“未检查”，不阻止工程 Issue 关闭。
3. `STATE.md`、Roadmap、Issue 和 PR 没有互相矛盾；如果任务不改变学习状态，应明确说明无需更新 `STATE.md`。
