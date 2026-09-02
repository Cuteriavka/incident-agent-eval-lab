# Incident Agent Evaluation Lab

一个以独立评测器为主产品、以受限参考诊断 Agent 为首个被测对象，并以公开数据和确定性回放为基础的个人 clean-room 项目。

> **Status:** Planning — no evaluation results yet.

## 项目做什么

- 将公开事故数据归一化为可重复执行的 replay case。
- 实现一个最小参考诊断 Agent：在有限预算内提出候选假设，并调用已注册的只读探针获取 metrics、logs、traces、events、topology 或测试结果。
- 输出带证据引用的结构化诊断；证据不足时返回 `insufficient_evidence`。
- 用硬门禁与多维 scorecard 分别评估根因、拒答、证据、探针、安全、完成率、延迟和成本。
- 通过无探针、受限探针和 RAG 开关的受控变体，以及小规模重复运行，区分设计变化与 LLM 方差。
- 将公开 Runbook RAG 作为可独立评测的知识子系统。

## 项目不做什么

- 不自动执行修复。
- 不开放任意 shell、kubectl、文件访问或动态脚本。
- 不建设复杂 Web UI、通用运维平台或多 Agent 编排平台。
- 不重建通用 trace、数据集、标注或实验管理平台，也不宣称当前支持任意 Agent。
- 不使用或复刻任何公司的代码、日志、规则、提示、架构、内部命名或客户信息。
- 不宣称已经适用于真实生产环境，也不发布未经实验验证的性能指标。

## 当前阶段

仓库目前处于真实案例定向与最小切片准备阶段：

- 尚无 Agent 或评测实现。
- 已提供 Cloud-OpsBench 单案例的实践 notebook、安全准备脚本和测试；第三方数据只保存在仓库外。
- 尚未完成真实模型 Agent 运行，也未揭示引导 case 的 Ground Truth。
- 尚无基线、实验结果或性能提升数据。

当前推进入口见 [线性项目推进路径](docs/learning/LEARNING_PATH.md) 和 [N00 notebook](notebooks/00_cloudopsbench_orientation.ipynb)。完整问题定义见 [Project Brief](docs/PROJECT_BRIEF.md)，问题、场景、需求、技术手段和退出门槛见 [Project Roadmap](docs/PROJECT_ROADMAP.md)，主产品与参考 Agent 的边界见 [ADR-0001](docs/adr/0001-evaluator-first-reference-agent.md)。

### 当前唯一启动入口（Windows）

环境与仓库外案例数据准备完成后，在仓库根目录只运行：

```powershell
.\.venv\Scripts\python.exe scripts\start_n00.py
```

该命令把受 Git 跟踪的空输出 starter 复制到仓库外并打开工作副本。看到固定 `case_ref`、症状和 9 个工具族即表示 N00A 已就绪；不要直接运行仓库中的 starter。

## 计划使用的公开数据

- [Cloud-OpsBench](https://github.com/LLM4Ops/Cloud-OpsBench)：当前只用于一个固定、永久 `tutorial/dev-only` 案例的定向观察；不产生兼容性或性能声明。
- [RCAEval](https://github.com/phamquiluan/RCAEval)：传统 RCA 对照与后续核心数据候选，须在数据审计后再决定。
- RCA100 / AIOps2025：外部交叉验证候选，正式接入前将单独核验来源、版本和许可证。

原始及派生第三方 payload 默认都不会随本仓库重新分发，除非对应 data card 明确证明再分发权限。后续仅提供可审计的下载说明、校验和、数据卡与适配器；原创 clean-room fixture 可在记录 provenance 后提交。

## 许可证

本项目原创内容采用 [MIT License](LICENSE)。第三方数据、文档或代码仍受各自许可证约束，详见 [NOTICE](NOTICE.md)。
