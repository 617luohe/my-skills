---
name: 2-开发
description: 按已确认契约实现非平凡改动，发现并运行项目原生 test/type/lint/build；行为变更加载内部 TDD vocabulary。触发：开发、实现、编码、implement。
disable-model-invocation: false
---

# 2-开发 — 宿主与语言中立的实现

每个开发切片使用 fresh context，只依赖磁盘契约、目标代码和可验证证据。Manifest dependency 使用 canonical name `vocabulary/tdd`；运行时加载 `/tdd`。

## 1. 固定切片契约

- 从 `docs/plans/<feature>/`、issue 或用户明确 spec 提取一个垂直切片、验收标准、范围外事项、依赖和 HITL 点。
- 加载项目实际存在的 agent 指令、领域上下文和 ADR；不从旧聊天补写缺失决策。
- 契约缺失、矛盾或仍有架构取舍时停止，返回 `/1-规划`。

完成条件：切片边界和每条验收标准均可检查。

## 2. 发现项目原生命令

检查项目清单、任务运行器、构建配置、贡献文档和 CI，确定仓库已经定义的：

- test 命令
- type-check 命令
- lint/format-check 命令
- build 命令

只运行项目已有命令或其文档化参数，不根据语言猜工具，不为完成检查临时引入依赖。某类检查未配置时明确记录“项目未配置”。

完成条件：适用命令及来源已记录，未配置项已说明。

## 3. 实现

- 行为变更必须加载 `/tdd`，按一个垂直行为完成 RED → GREEN → REFACTOR。
- 纯文档、格式或机械生成物按契约执行最小改动，并记录无需新增行为测试的理由。
- 遵守项目现有风格与边界；只修改切片所需内容。
- 遇到 `[HITL]` 决策点时暂停并等待用户。

完成条件：切片验收标准已实现；本次产生的无用依赖、调试输出和临时文件已清理。

## 4. 验证与自检

1. 开发循环中运行最小受影响 test。
2. 完成后运行项目适用的完整 test、type-check、lint 和 build 命令。
3. 检查验收标准、范围外事项、明显重复、命名和公共接口变化。
4. 检查失败则做最小修复并重跑受影响检查；无法运行时记录命令、阻塞原因和残余风险。

完成条件：所有已配置且适用的原生命令通过，或每个未运行项都有可复现阻塞说明。

## 5. 正式审查交接

保持改动未提交，在 fresh context 交给 `/3-检查`：

- **fixed point/base**：实际审查基点、`git log <fixed-point>..HEAD --oneline` 与 `git diff <fixed-point>...HEAD` 提交差异。
- **spec**：任务、PRD、issue 或验收标准路径。
- **diff**：`git diff --cached`、`git diff`，以及 `git ls-files --others --exclude-standard` 返回的未跟踪文件列表与内容。
- **证据**：原生 test/type/lint/build 命令与结果，含未配置或阻塞项。

未跟踪文件不得因不在 Git diff 中而漏审。无意纳入本次变更的用户文件必须在交接中逐项显式排除并说明理由，不得静默省略。

## 复评回环

FAIL 时逐条最小修复并重跑适用原生检查，再以同一 fixed point、spec、diff 和新证据复评。PASS WITH WARNINGS 默认停止；只有用户选择修复的 warning 才进入回环。未修复或拒绝的意见必须写明理由。

## 边界

本技能不 commit、不 push、不发布。正式审查通过后，仍需用户明确授权才能进入 `/5-版本管理`。
