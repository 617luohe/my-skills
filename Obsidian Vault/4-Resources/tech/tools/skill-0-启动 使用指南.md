---
title: "skill-0-启动 使用指南"
aliases: ["启动技能指南", "新项目初始化指南"]
tags:
  - type/resource
  - domain/tech/tools
  - topic/skills-guide
created: 2026-06-18
status: published
confidence: sprout
source: "https://github.com/617luohe/my-skills"
skill: "0-启动"
---

# 0-启动 — 新项目初始化

> 一句话：新建 Python 项目一条龙——目录结构、uv 环境、pre-commit（Ruff + mypy + pytest）、git 初始化，全部自动化。

## 什么时候用

| 场景 | 说明 |
|------|------|
| 开始一个全新的 Python 项目 | 从零搭建标准项目骨架 |
| 需要统一的项目配置 | 确保每个新项目用同样的工具链（Ruff/mypy/pytest/pre-commit） |
| 快速试验一个新想法 | 脚手架就绪后立即可以写代码 |

**不适用**：已有项目的局部改动（用 4-开发），或非 Python 项目。

## 完整流程（12 步）

```
1. 确认项目信息 ── 名称、Python 版本、mypy strict?、Ruff 风格
2. 检测安装 uv  ── 如果未安装则自动装
3. 创建目录结构 ── src/project_name/ + tests/
4. 生成入口文件 ── main.py + 占位测试
5. 生成 .gitignore
6. 创建 uv 虚拟环境
7. 生成 pyproject.toml ── Ruff/mypy/pytest 配置
8. 生成 pre-commit config
9. 安装 pre-commit 钩子
10. git init + 首次提交
11. 配置任务管理 ── 本地 .scratch/todo.md 或 GitHub Issues
12. 验证清单 ── pytest 通过、pre-commit 通过、git 已初始化
```

## 案例演示

### 案例 1：标准新项目

```
用户：/0-启动

Claude：项目名称？
用户：data-pipeline

Claude：Python 版本？（默认 ≥3.12）
用户：≥3.12，用 uv

Claude：mypy 要 strict 吗？(y/N)
用户：N

Claude：Ruff 行长度用 88 还是 120？
用户：88

Claude：引号风格？双引号还是单引号？
用户：双引号

Claude：开始搭建...

       ✅ src/data_pipeline/ 已创建
       ✅ tests/ 已创建
       ✅ pyproject.toml 已生成（Ruff 88字符 + mypy 非strict）
       ✅ .pre-commit-config.yaml 已生成
       ✅ uv 虚拟环境已创建
       ✅ pre-commit 钩子已安装
       ✅ git 仓库已初始化（Initial project scaffold）

       任务管理方式？
       1. 本地模式 — .scratch/todo.md
       2. GitHub 模式 — GitHub Issues

用户：1

Claude：✅ .scratch/todo.md 已创建

       ── 验证清单 ──
       ✅ src/ 和 tests/ 目录结构正确
       ✅ uv run pytest 通过
       ✅ pre-commit run --all-files 通过
       ✅ git 仓库已初始化并有首次提交
       ✅ 任务管理方式已配置（本地模式）

       项目已就绪！
```

### 案例 2：自定义配置

```
用户：/0-启动 帮我建一个叫 api-gateway 的项目，Python 3.11，mypy strict

Claude：luohe，收到。

       确认信息：
       - 项目名：api-gateway
       - Python：≥3.11
       - mypy strict：yes
       - Ruff 行长度？（88/120）
       
用户：120

Claude：引号风格？
用户：单引号

Claude：开始搭建...

       ✅ 已生成 pyproject.toml
          [tool.ruff]
          line-length = 120
          
          [tool.ruff.format]
          quote-style = "single"
          
          [tool.mypy]
          strict = true

       ...（后续步骤同上）

       ✅ 项目已就绪。注意 mypy strict 模式下类型检查更严格，建议先跑一次看看。
```

### 案例 3：已有 uv 但缺项目结构

```
用户：/0-启动 我已经有一个目录了，只想加 pre-commit 和 pyproject.toml

Claude：luohe，检测到当前目录不为空。我会在现有文件基础上添加配置。
       已有文件不会被覆盖。
       
       确认：项目名称就用当前目录名 "my-utils"？
用户：对

Claude：Python 版本？
用户：3.10

Claude：⚠️ uv 要求 Python ≥ 3.12 才能用某些特性。建议 ≥ 3.12，是否升级？
用户：不了，用 3.10

Claude：收到。mypy strict？
用户：N
...
Claude：✅ pyproject.toml + .pre-commit-config.yaml 已添加。原有文件未改动。
```

## 生成的目录结构

```
project-name/
├── src/
│   └── project_name/
│       ├── __init__.py
│       └── main.py           # def main() + __name__ == "__main__"
├── tests/
│   ├── __init__.py
│   └── test_main.py          # 占位测试
├── .gitignore
├── .pre-commit-config.yaml   # Ruff + mypy + pytest
├── pyproject.toml             # 项目配置
└── README.md
```

## 注意事项

- 项目名中的连字符会自动转为下划线作为包名（`data-pipeline` → `data_pipeline`）
- 如果当前目录已有文件，不会覆盖——但建议在空目录中运行
- mypy strict 模式会强制完整的类型注解，小型脚本可能不需要
- 部署到 `.claude/skills/` 后，通过 `/0-启动` 或 `/use-skills 新建项目` 触发

## 相关技能

- [[skill-0-初始化CLAUDE 使用指南]] — 初始化 CLAUDE.md（建议启动后立即执行）
- [[skill-4-开发 使用指南]] — 有了项目骨架后，开始 TDD 编码
- [[skill-8-版本管理 使用指南]] — 后续的 git 操作
