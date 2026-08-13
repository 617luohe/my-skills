---
name: 0-启动
description: 仅初始化 Python + uv 项目：最小项目结构、本地 git、uv 环境与 smoke test；不作为通用项目启动器。
disable-model-invocation: false
---

# 0-启动 — Python + uv 项目最小初始化

仅服务 Python + uv 项目：**项目结构 + 本地 git + uv 环境**。其他语言或包管理器交回 `/0-询问luohe`。细节见 [references/scaffold.md](references/scaffold.md)。

## MUST 规则

1. **只做这三件事。** ruff/mypy/pre-commit/CI 不装不问不生成——用户主动要才加。
2. **只问一轮。** 项目名 + 位置；Python 版本默认由 uv 选，点名才用 `-p`。
3. **uv 缺失自动装，不问。**
4. **收尾必须 `uv run pytest` 通过。**

## 流程

1. **确认** — 项目名 + 位置（新建子目录 vs 当前空目录）
2. **备好 uv** — `uv --version`，缺失则安装
3. **建结构 + git** — `uv init --package --vcs git <name>` 或 `.`
4. **加 tests + 环境** — `tests/test_smoke.py` + `uv add --dev pytest`
5. **验证并保持未提交** — `uv run pytest` + `git status`；不 commit，保存版本交 `/5-版本管理`

## 交付回报

- 变更清单、Git 状态（是否未提交）、pytest 结果、下一阶段推荐

## 什么时候用

- 新开 Python 项目、散装脚本收成正经项目

示例见 [references/examples.md](references/examples.md)。
