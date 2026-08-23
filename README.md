# Incident Agent Evaluation Lab

一个以公开数据和确定性回放为基础，用于评估云原生事故诊断 Agent 的结论、证据和工具使用过程的个人 clean-room 项目。

> **Status:** Planning — no evaluation results yet.

## 项目做什么

- 将公开事故数据归一化为可重复执行的 replay case。
- 让单个 Agent 在有限预算内提出候选假设，并调用已注册的只读探针获取 metrics、logs、traces、events、topology 或测试结果。
- 输出带证据引用的结构化诊断；证据不足时返回 `insufficient_evidence`。
- 分别评估根因结论、证据质量、探针有效性、安全策略、延迟和成本。
- 将公开 Runbook RAG 作为可独立评测的知识子系统。

## 项目不做什么

- 不自动执行修复。
- 不开放任意 shell、kubectl、文件访问或动态脚本。
- 不建设复杂 Web UI、通用运维平台或多 Agent 编排平台。
- 不使用或复刻任何公司的代码、日志、规则、提示、架构、内部命名或客户信息。
- 不宣称已经适用于真实生产环境，也不发布未经实验验证的性能指标。

## 当前阶段

仓库目前只包含项目定义、合规边界和学习状态记录：

- 尚无 Agent 或评测实现。
- 尚未下载或包含任何第三方数据。
- 尚无基线、实验结果或性能提升数据。

完整问题定义见 [Project Brief](docs/PROJECT_BRIEF.md)。

## 计划使用的公开数据

- [RCAEval](https://github.com/phamquiluan/RCAEval)：核心开发与留一系统验证候选。
- RCA100 / AIOps2025：外部交叉验证候选，正式接入前将单独核验来源、版本和许可证。

原始数据不会随本仓库重新分发。后续仅提供可审计的下载说明、校验和、数据卡与适配器。

## 许可证

本项目原创内容采用 [MIT License](LICENSE)。第三方数据、文档或代码仍受各自许可证约束，详见 [NOTICE](NOTICE.md)。
