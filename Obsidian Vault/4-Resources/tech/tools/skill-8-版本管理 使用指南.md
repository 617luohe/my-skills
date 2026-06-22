---
title: "skill-8-版本管理 使用指南"
aliases: ["版本管理指南", "Git操作指南"]
tags:
  - type/resource
  - domain/tech/tools
  - topic/skills-guide
created: 2026-06-18
status: published
confidence: sprout
source: "https://github.com/617luohe/my-skills"
skill: "8-版本管理"
---

# 8-版本管理 — Git 版本控制全流程

> 一句话：覆盖 git 全部核心操作——初始化、保存、查看、回滚、分支、远程同步。默认本地仓库，按需连接 GitHub。

## 什么时候用

| 场景 | 说明 |
|------|------|
| 完成一个功能阶段 | 保存进度，打个 checkpoint |
| 想看改了什么 | 查看变更历史和 diff |
| 改坏了想回退 | 安全回滚到之前的版本 |
| 需要分支开发 | 创建/切换/合并分支 |
| 准备推送到 GitHub | 连接远程仓库，push/pull |

**不适用**：复杂的 git 操作如 rebase -i、cherry-pick、submodule——这些超出了技能的覆盖范围。

## 操作清单

```
init     — 初始化仓库
save     — 保存版本（add + commit）
log      — 查看历史（带分支图）
diff     — 查看变更
rollback — 安全回滚（revert，保留历史）
reset    — 硬重置（危险，需明确同意）
branch   — 分支管理（创建/切换/删除）
remote   — 连接 GitHub
push     — 推送到远程
pull     — 拉取远程更新
```

## 案例演示

### 案例 1：日常保存进度

```
用户：/8-版本管理 保存一下进度，我改完了用户模块

Claude：luohe。

       检查变更…
       修改：src/user/service.py
       新增：tests/test_user_service.py

       git add .
       git commit -m "feat: 完成用户模块基础功能"

       [main a1b2c3d] feat: 完成用户模块基础功能
        2 files changed, 145 insertions(+), 3 deletions(-)

       ✅ 已保存。
```

### 案例 2：查看历史和变更

```
用户：/8-版本管理 看看最近的提交记录

Claude：luohe。

       git log --oneline --graph

       * a1b2c3d (HEAD -> main) feat: 完成用户模块基础功能
       * b2c3d4e feat: 添加用户注册接口
       * c3d4e5f refactor: 提取邮件发送服务
       * d4e5f6g Initial project scaffold

用户：看看最后一个提交改了哪些文件

Claude：git diff HEAD~1 --stat

       src/user/service.py      | 85 ++++++++++++++++++
       tests/test_user_service.py | 60 ++++++++++++
       2 files changed, 145 insertions(+), 3 deletions(-)

用户：具体改了 service.py 的什么？

Claude：git diff HEAD~1 -- src/user/service.py

       +class UserService:
       +    def __init__(self, repo: UserRepository):
       +        self.repo = repo
       +
       +    def create_user(self, name: str, email: str) -> User:
       +        user = User(id=uuid4(), name=name, email=email)
       +        self.repo.save(user)
       +        return user
       ...
```

### 案例 3：安全回滚

```
用户：/8-版本管理 刚才的提交有问题，帮我回退

Claude：luohe。用 revert 安全回滚——保留历史记录。

       先确认：回滚 a1b2c3d "feat: 完成用户模块基础功能" 这个提交？

用户：对

Claude：git revert a1b2c3d

       [main e5f6g7h] Revert "feat: 完成用户模块基础功能"
        2 files changed, 3 insertions(+), 145 deletions(-)

       ✅ 已安全回滚。历史记录完整保留。
       如果想彻底丢弃（不保留历史），用 git reset --hard，
       但这是危险操作——需要我再确认一次。

用户：不用，revert 够了
```

### 案例 4：分支操作

```
用户：/8-版本管理 我要开始做退款功能了，帮我开个分支

Claude：luohe。

       git checkout -b feature/refund

       Switched to a new branch 'feature/refund'
       ✅ 已创建并切换到 feature/refund。

       [开发过程中…]

用户：/8-版本管理 退款做完了，保存并合回 main

Claude：luohe。

       先保存当前分支的改动：
       git add .
       git commit -m "feat: 实现退款功能"

       [feature/refund f6g7h8i] feat: 实现退款功能
        5 files changed, 320 insertions(+)

       切换到 main 并合并：
       git checkout main
       git merge feature/refund

       Updating e5f6g7h..f6g7h8i
       Fast-forward
        5 files changed, 320 insertions(+)

       分支已删除：
       git branch -d feature/refund
       Deleted branch feature/refund.

       ✅ 退款功能已合入 main。历史：
       * f6g7h8i (HEAD -> main) feat: 实现退款功能
       * e5f6g7h Revert "feat: 完成用户模块基础功能"
       * a1b2c3d feat: 完成用户模块基础功能
```

### 案例 5：连接 GitHub

```
用户：/8-版本管理 帮我推送到 GitHub

Claude：luohe，当前没有配置远程仓库。
       
       仓库 URL 是什么？

用户：https://github.com/617luohe/payment-service.git

Claude：git remote add origin https://github.com/617luohe/payment-service.git
       git push -u origin main

       Enumerating objects: 25, done.
       ...
       Branch 'main' set up to track remote branch 'main' from 'origin'.

       ✅ 已推送。后续直接用 git push / git pull 即可。
```

## 注意事项

- **默认用 `git revert`**，保留历史。`git reset --hard` 只在用户明确要求且二次确认后才执行
- `save` 操作会先 `git add .`，如果你有不想提交的改动，先手动 `git add` 指定文件
- 新增文件时自动检测是否需要更新 `.gitignore`
- 如果未提供 commit message，会根据变更内容自动生成

## 相关技能

- [[skill-4-开发 使用指南]] — 每完成一个测试循环就保存一次
- [[skill-9-最后整理 使用指南]] — 收尾时最后检查和同步
- [[skill-5-检查 使用指南]] — 审查通过后提交合并
