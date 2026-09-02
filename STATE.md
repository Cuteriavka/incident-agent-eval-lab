# 项目状态

- 日期：2026-09-02
- 项目阶段：MS-0 — Foundation
- 当前节点：N00A — Cloud-OpsBench 人工定向调查
- 当前状态：Ready — 可离线执行，不需要模型 API

## 已完成

- 确认独立 evaluator 是主产品，受限 Reference Agent 是首个受控被测对象，两者都属于 v0.1。
- 将推进路径整理为线性节点：N00 真实案例观察 → N01 轨迹/评测缺口 → N02 契约与 Ground Truth 隔离 → N03 clean-room replay/evaluator 切片。
- 建立 `uv + Python 3.12` 本地实践环境、固定版本数据记录、案例准备脚本、空输出 starter notebook 和仓库外工作簿启动器。
- 在仓库外准备 Cloud-OpsBench 固定版本与 `trainticket/service/1` 的 pre-reveal/compare-only 双视图。
- 为报告引用、冻结顺序、轨迹投影和 notebook 公开策略建立自动化测试。

## 尚未完成

- 项目作者尚未填写并冻结 N00A 的人工 `orientation_report`。
- 尚未提供模型 API Key，因此没有运行 N00B 的真实上游 ReAct Agent。
- 尚未揭示教学 case 的 Ground Truth，也没有进行 N00C 比较。
- 没有实现本项目的 Reference Agent、replay、契约或 evaluator。
- 没有基线分数、性能提升、数据集兼容性或泛化结论。

## 可见性与合规状态

- 第三方 checkout、缓存、原始/派生 payload、原始 Agent 轨迹和实际 notebook 输出均留在仓库外。
- 公开仓库当前只允许不能直接执行的空输出 starter、项目原创说明和测试代码。N00 生成的报告、投影、比较、hash 与 marker 在独立导出门禁实现前全部保持仓库外私有。
- N00 人工诊断和 Agent 轨迹投影都冻结前，compare-only loader 不得揭示 Ground Truth。
- N00 引导 case 在揭示后永久为 `tutorial/dev-only`，不得进入 prompt、RAG、正式 fixture、held-out split 或指标。

## 当前阻塞与状态转换

当前无阻塞：N00A 可离线完成。N00A 冻结后进入 `N00-WAITING-KEY`；API Key 是 N00B 的外部依赖，不是 N00A 的前置条件，也不要求重做 N00A。

```text
N00A -> N00-WAITING-KEY -> N00B -> N00C -> N01
```

## AI 与作者所有权

- AI 已完成：节点骨架、案例包装器、测试和 notebook 起始模板；这些属于待作者核验的辅助实现。
- 项目作者必须完成：亲自选择探针、概括观察、冻结人工诊断、解释一个高价值与低价值查询，并在 N00C 形成自己的比较结论。
- 只有通过节点 Ownership Check，相关能力才能从 `Implemented` 升级为 `Defendable`。

## 下一项唯一动作

在仓库根目录运行 `.\.venv\Scripts\python.exe scripts\start_n00.py`，在打开的仓库外工作副本中从头运行到 N00A，填写唯一 TODO 并通过人工报告冻结检查。看到固定 `case_ref`、症状和 9 个工具族即表示就绪；今天不要运行 N00B/N00C，也不要查找 case 答案。
