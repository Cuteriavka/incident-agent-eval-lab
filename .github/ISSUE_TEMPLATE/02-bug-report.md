---
name: 缺陷报告
about: 报告一个可复现且不包含敏感信息的项目缺陷
title: "bug: "
labels: "type:bug"
assignees: ""
---

## 问题描述

<!-- 清楚说明发生了什么，以及它影响哪项契约、门禁或用户结果。 -->

## 复现条件与步骤

<!-- 只使用公开、synthetic clean-room 或已获许可的输入。不得粘贴公司日志、凭据或客户信息。 -->

1. <!-- 填写复现步骤 -->
2. <!-- 可选 -->
3. <!-- 可选 -->

## 实际结果

<!-- 附最小错误信息、失败测试或可公开的运行记录引用。 -->

## 预期结果

<!-- 描述可观察行为，不要只写“应当成功”。 -->

## 影响与边界

- 影响的版本或 commit：
- 影响的模块或 Roadmap 需求：
- 是否涉及 Ground Truth、工具权限、第三方数据或公开声明：

## 验收标准

<!-- 最多三项，其中至少一项应能在修复前失败、修复后通过。 -->

1. <!-- 填写验收标准 -->
2. <!-- 可选 -->
3. <!-- 可选 -->

## 安全与数据检查

- [ ] 复现材料不包含凭据、公司非公开材料或客户信息。
- [ ] Ground Truth 未通过任何 Agent-visible artifact 或 channel 泄漏，包括字段、case ID、文件名、路径、manifest、prompt、RAG corpus/index、cache、工具结果、`RunRecord` 或 exporter/trace；Agent 包不能访问 truth loader，只有 evaluator 可在报告冻结后通过隔离的 truth loader 加载真值。
- [ ] Issue 正文和附件不包含 sealed/hidden Ground Truth payload。
- [ ] 本 Issue 使用 clean-room fixture；或第三方 raw/derived payload 不提交，且任何再分发例外已有 data card 明确证明许可并记录完整 provenance。
