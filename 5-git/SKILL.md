---
name: 5-git
description: Git 版本管理：初始化、保存、查看历史、回滚、分支与远程同步。
disable-model-invocation: false
---

# 5-git — Git 版本管理

处理 Git 保存、查看、回滚、分支和远程同步。

## 流程

1. 确认目标：初始化、查看、提交、回滚、分支还是远程同步；先读当前 `git status` 再动手。
2. **授权**：保存、提交、推送都要用户明确授权，只处理用户明确要求的内容。
3. **暂存**：优先 `git add <具体文件>`，不用 `git add .`。
4. **回滚**：默认 `git revert <commit>`，不用 `reset`。
5. **危险操作**（`reset --hard`、`push --force`、`branch -D`）：先确认影响范围再执行。
6. **首次推送**：`git push -u origin $(git branch --show-current)`，不硬编码 `main`。

## 常见任务速查

- 初始化：`git init`
- 保存：`git add <具体文件>` → `git commit`
- 历史：`git log --oneline --graph`
- 变更：`git diff`
- 回滚：`git revert <commit>`
- 分支：创建 / 切换 / 删除已合并分支
- 远程：`git remote add origin <url>`；首次 `git push -u origin $(git branch --show-current)`；后续 `git push` / `git pull`

## 完成标准

- Git 操作成功、无错误退出码，`git status` 处于预期状态。
- 提交或推送的范围、目标与用户授权一致。
