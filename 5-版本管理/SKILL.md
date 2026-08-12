---
name: 5-版本管理
description: Manage Git repositories, history, branches, remotes, rollback, and synchronization. 触发：提交、commit、push、版本管理、回滚、分支。
disable-model-invocation: false
---

# 5-版本管理 — Git 版本控制全流程

覆盖 git 核心操作。默认本地仓库，远程按需配置。命令详见 [references/commands.md](references/commands.md)。

## MUST 规则

1. **危险操作必须先确认。** `reset --hard`、`push --force`、`branch -D` 须用户明确同意。
2. **回滚默认 revert，不用 reset。** 除非用户明确要求 reset。
3. **首次推送用 `git branch --show-current` 设上游**，不写死 `main`。
4. **保存版本须用户明确授权。** `/2-开发`、`/3-检查` 不默认提交；审查通过且用户要求时才 `git add`/`commit`。

## 什么时候用

- 完成功能阶段要存盘、查看变更、回滚、推远程

对话示例见 [references/examples.md](references/examples.md)。

## 完成标准

**必须**：操作无错误退出码；push 后远端已收到；`git status` 状态清晰。

**可选**：commit message 符合约定；遵守分支保护。

**交接**：阶段收尾 → `/6-最后整理`；中途存盘 → 回到上游（如 `/2-开发`）。
