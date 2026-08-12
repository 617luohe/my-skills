# Git 命令参考

## init — 初始化仓库

```bash
git init
```

已有仓库则跳过。无 `.gitignore` 时自动创建（含 Python 标准规则）。

## save — 保存版本

```bash
git add <具体文件或目录>
git commit -m "<描述>"
```

优先暂存具体文件，避免 `git add .` 误提交敏感文件。未提供描述时根据变更生成提交信息；新增文件时检测是否需更新 `.gitignore`。

## log — 查看历史

```bash
git log --oneline --graph
```

## diff — 查看变更

```bash
git diff                  # 未暂存
git diff <commit>         # 与某版本
git diff <commit1>..<commit2>
```

## rollback — 安全回滚

```bash
git revert <commit>       # 推荐：保留历史
```

默认 `git revert`；仅用户明确要求时用 `git reset`。

## reset — 硬重置

```bash
git reset --hard <commit>
```

危险操作，须用户明确同意。

## branch — 分支管理

```bash
git branch <name>
git checkout <name>
git branch -d <name>
```

## remote — 连接远程

```bash
git remote add origin <url>
git push -u origin $(git branch --show-current)
```

动态获取当前分支名，避免硬编码 `main`。

## guardrails — 安全护栏（可选）

PreToolUse 钩子拦截危险命令；作用域问用户（项目或全局），合并现有 hooks。

## push / pull — 同步远程

```bash
git push
git pull
```

仅配置远程后可用；首次推送自动设置上游分支。
