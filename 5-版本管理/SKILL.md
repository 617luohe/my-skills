---
name: 5-版本管理
description: Manage Git repositories, history, branches, remotes, rollback, and synchronization.
disable-model-invocation: false
---

# 5-版本管理 — Git 版本控制全流程

覆盖 git 版本管理全部核心操作。默认本地仓库，需连接远程时按需配置。

## MUST 规则

1. **危险操作必须先确认再执行。** `git reset --hard`、`git push --force`、`git branch -D` 需要用户明确同意。
2. **回滚默认用 revert，不用 reset。** 除非用户明确要求 reset。
3. **首次推送自动设置当前分支的上游分支。** 使用 `git branch --show-current` 动态获取分支名。
4. **保存版本必须由用户明确授权。** `/2-开发` 和 `/3-检查` 不默认提交；审查通过后，只有用户明确要求保存、提交或调用 `/5-版本管理`，才执行 `git add` 或 `git commit`。

### init — 初始化仓库

```bash
git init
```

如果已有仓库则跳过。自动创建 `.gitignore` 如果不存在（含 Python 标准规则）。

---

### save — 保存版本

```bash
git add <具体文件或目录>
git commit -m "<描述>"
```

**优先暂存具体文件**，避免 `git add .` 误提交敏感文件（如 `.env`、临时文件）。

如果未提供描述，自动根据变更生成提交信息。

新增文件时自动检测是否需更新 `.gitignore`。

---

### log — 查看历史

```bash
git log --oneline --graph
```

显示版本历史和分支图。

---

### diff — 查看变更

```bash
git diff                  # 未暂存的变更
git diff <commit>         # 与某个版本的差异
git diff <commit1>..<commit2>  # 两个版本间的差异
```

---

### rollback — 安全回滚

```bash
git revert <commit>       # 安全回滚（保留历史，推荐）
```

默认用 `git revert`。只在用户明确要求时才用 `git reset`。

---

### reset — 硬重置

```bash
git reset --hard <commit>  # 丢弃该版本之后的所有变更
```

**危险操作**。执行前必须确认你要丢弃的变更，获得你明确同意后才执行。

---

### branch — 分支管理

```bash
git branch <name>         # 创建分支
git checkout <name>       # 切换分支
git branch -d <name>      # 删除已合并的分支
```

---

### remote — 连接远程

```bash
git remote add origin <url>
git push -u origin $(git branch --show-current)
```

在你要求连接 GitHub 时执行。**动态获取当前分支名**，避免硬编码 `main`。首次推送后告知你后续可直接用 `push` 和 `pull`。

---

### guardrails — Git 安全护栏（可选）

为高风险仓库可选安装 PreToolUse 钩子，拦截危险命令（如 `git push`、`git reset --hard`、`git clean -fd`、`git branch -D`）。

执行前先问作用域：

- 仅当前项目（推荐）→ `.claude/settings.json`
- 全局所有项目 → `~/.claude/settings.json`

原则：合并现有 hooks 配置，不覆盖其他设置。

### push / pull — 同步远程

```bash
git push                  # 推送到远程
git pull                  # 拉取远程更新
```

仅在配置了远程仓库后可用。首次推送时自动设置上游分支。

---

## 什么时候用

- 完成一个功能阶段，需要保存进度
- 想查看改了什么东西
- 改坏了需要回滚到之前的版本
- 准备推送到 GitHub

## 案例

```
你：帮我保存一下进度，我改了用户模块
Claude：git add src/users.py tests/test_users.py && git commit -m "feat: 完成用户模块基础功能"
       [<当前分支> abc1234] feat: 完成用户模块基础功能

你：看看改了什么
Claude：git log --oneline --graph
       * abc1234 feat: 完成用户模块基础功能
       * def5678 初始项目脚手架

你：我想推送到 GitHub
Claude：仓库 URL 是什么？
你：https://github.com/user/project.git
Claude：git remote add origin https://github.com/user/project.git
       git push -u origin $(git branch --show-current)
```

## 完成标准

**必须满足**：

- Git 操作成功执行（commit/push/branch/merge 等），无错误退出码
- 如果执行了 push，远程仓库已收到提交
- 工作区状态清晰：`git status` 显示预期状态（clean 或明确的未暂存文件）

**可选验收**：

- commit message 符合项目约定（如果有 commitlint 配置）
- 分支保护规则已遵守（不直接 push 到 main/master，除非用户明确授权）

**交接**：

- 功能阶段收尾时，建议用户调用 `/6-最后整理` 沉淀产出
- 中途存盘时，回到上游 skill（如 `/2-开发`）继续执行
