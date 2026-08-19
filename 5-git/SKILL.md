---
name: 5-git
description: Git 版本管理：初始化、保存、查看历史、回滚、分支与远程同步。
disable-model-invocation: false
---

# 5-git — Git 版本管理

处理 Git 保存、查看、回滚、分支和远程同步。

## 核心规则

1. 保存、提交、推送都要用户明确授权。
2. 危险操作先确认：`reset --hard`、`push --force`、`branch -D`。
3. 回滚默认用 `git revert`，不用 `reset`。
4. 优先暂存具体文件，不用 `git add .`。
5. 首次推送用当前分支名设置上游，不硬编码 `main`。

## 常见任务

- 初始化仓库：`git init`
- 保存版本：`git add <具体文件>` → `git commit`
- 查看历史：`git log --oneline --graph`
- 查看变更：`git diff`
- 安全回滚：`git revert <commit>`
- 分支管理：创建 / 切换 / 删除已合并分支
- 连接远程：`git remote add origin <url>`
- 首次推送：`git push -u origin $(git branch --show-current)`
- 后续同步：`git push` / `git pull`

## 流程

1. 先确认目标：初始化、查看、提交、回滚、分支还是远程同步。
2. 先读当前仓库状态，再执行对应 Git 操作。
3. 涉及提交或推送时，只处理用户明确要求的内容。
4. 涉及远程时，先确认 remote 和当前分支。
5. 涉及危险操作时，再次确认影响范围后执行。

## 完成标准

- Git 操作成功完成，且无错误退出码。
- 若执行了提交或推送，范围与目标和用户授权一致。
- 操作后 `git status` 处于预期状态。
