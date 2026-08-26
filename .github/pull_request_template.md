## 关联 Issue

<!-- 将编号替换为本 PR 解决的 Issue。只有合入默认分支后才会自动关闭。 -->

Closes #

## 为什么修改

<!-- 用一到三句话说明问题、目的和预期可观察结果。 -->

## 修改内容

- <!-- 填写修改内容 -->

## 明确未修改

- <!-- 填写未修改范围 -->

## 验证证据

<!-- 列出实际执行的测试、文档链接检查、演示或 Ownership Check；不要只写“已验证”。 -->

- [ ] 验收标准 1：
- [ ] 验收标准 2：
- [ ] 验收标准 3：

条件性证据（涉及数据、Ground Truth、工具权限、架构决定或公开指标时，填写 data card、负例测试、ADR 或报告链接；不适用时写 N/A 及理由）：

- <!-- 填写链接或 N/A 理由 -->

## 状态与所有权

- [ ] 已判断 `STATE.md` 是否需要更新；如不需要，已在下方解释。
- `STATE.md` 处理说明：
- Ownership 结果：未检查 / 已检查（链接或摘要）/ 不适用（理由）
- [ ] 若已检查，作者能解释关键选择、一个边界输入和最近替代方案的代价。

## Clean-room、安全与声明

- [ ] 不包含公司代码、日志、规则、架构、名称、客户信息、凭据或其他非公开材料。
- [ ] 第三方 raw/derived payload 默认不提交；任何例外均有 data card 明确证明再分发许可，并记录官方来源、版本、许可证、checksum、允许用途和分发限制。
- [ ] 第三方代码或文档许可证兼容，且已保留署名并记录修改；若不适用已在条件性证据中说明。
- [ ] Ground Truth 未通过任何 Agent-visible artifact 或 channel 泄漏，包括字段、case ID、文件名、路径、manifest、prompt、RAG corpus/index、cache、工具结果、`RunRecord` 或 exporter/trace；Agent 包不能访问 truth loader，只有 evaluator 可在报告冻结后通过隔离的 truth loader 加载真值，受影响路径有 canary/negative test。
- [ ] v0.1 未加入任意 shell、kubectl、filesystem access、动态脚本、写操作或自动修复能力；未来版本若要改变边界，必须先明确版本范围并完成 ADR 与安全审查。
- [ ] 未声称未经可复现实验证明的生产能力、数据集兼容性或性能提升。
