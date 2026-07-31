# ADR 0001: 固定知识库自动发布（Auto-publish to the Fixed Vault）

**Status:** Accepted

## Context

noteall 需要把资料整理后发布到固定个人知识库（`C:\Users\Administrator\Documents\Obsidian Vault`，Git 远端为 `origin/master`）。通用 `/5-版本管理` 要求每次用户明确授权，无法支撑"整理成功后自动 commit/push"的流水线需求。当前 hooks 也没有 Noteall 专用 Git 自动化。

驱动因素：
- 个人固定 Vault 是唯一写入目标，无多仓库歧义。
- 用户已确认自动 commit/push 的授权范围仅限该 Vault 的 Noteall 流水线。
- 模型自由组合 Git 命令容易越界（如 `git add .`、冲突猜测解决）。

## Decision

在 noteall 流水线内部定义一个**窄范围、固定仓库、确定性脚本驱动**的 Publish 阶段，不修改通用 `/5-版本管理` 的授权原则：

1. 只允许操作固定 Vault；仓库校验失败即停止，不回退到当前工作目录。
2. 开始时工作区不干净 → 停止，不处理资料。
3. 不使用 `git add .`；只暂存本次流水线记录的 owned paths。
4. 无实际变更 → 不创建空提交。
5. 远端冲突 → 停止并报告，不自动解决。
6. push 失败 → 保留本地提交并报告 commit hash；下次运行先补推遗留提交。
7. Git 操作优先由确定性脚本（Python 状态机）执行，模型不自由组合命令。
8. 提交信息不含敏感正文。

## Consequences

- 好处：收录→发布全自动，个人知识库可定时增量同步；Git 行为可测试、可故障注入。
- 成本：Vault 工作区需保持干净，否则流水线停止；自动合并允许远端变更合入本地，用户需接受该同步策略。
- 风险：远端出现内容冲突时流水线停顿，需人工处理；这是有意的安全停止，不接受自动解决。
- 后续：本授权不扩展到其他仓库；若未来需要多 Vault，需重开此 ADR。

## Alternatives considered

- 每次由用户手动授权 `/5-版本管理`：违背"自动流水线"目标，被用户否决。
- 让模型临场组合 Git 命令：行为不可预测，难以保证不变量（`git add .`、冲突猜测），被否决。
- 在通用 hooks 中配置 Vault 自动提交：作用范围过广，影响所有仓库，被否决。
