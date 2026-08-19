# 5-版本管理 — 对话示例

```
你：帮我保存一下进度，我改了用户模块
Claude：git add src/users.py tests/test_users.py && git commit -m "feat: 完成用户模块基础功能"

你：看看改了什么
Claude：git log --oneline --graph

你：我想推送到 GitHub
Claude：仓库 URL 是什么？
你：https://github.com/user/project.git
Claude：git remote add origin https://github.com/user/project.git
       git push -u origin $(git branch --show-current)
```
