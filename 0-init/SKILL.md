---
name: 0-init
description: Python 项目最小初始化：项目结构 + 本地 git + uv 环境
disable-model-invocation: false
---

# 0-init — 新项目最小初始化

小项目开张只要三件事：**一个项目结构、一个本地 git、一个 uv 环境**。做完就能写代码。

## 核心规则

1. 只做项目结构、本地 git、uv 环境。
2. 只问一轮：项目名和位置。
3. `uv` 缺失时自动安装。
4. 结束前必须跑通 `uv run pytest`。

## 流程

1. **确认**：项目名与初始化位置。
2. **备好 uv**：检查 `uv --version`；没有就安装。
3. **建结构 + git**：运行 `uv init --package --vcs git`，新建目录或在当前空目录初始化。
4. **补 smoke test**：创建 `tests/test_smoke.py`，安装 `pytest`。
5. **验证**：运行 `uv run pytest` 和 `git status --short --branch`，保持未提交。

## 按需追加

用户主动提了才做，各一行搞定，按需追加：

| 需求              | 命令                                                                                   |
| ----------------- | -------------------------------------------------------------------------------------- |
| 代码检查 / 格式化 | `uv add --dev ruff`                                                                    |
| 类型检查          | `uv add --dev mypy`                                                                    |
| 提交前门禁        | `uv add --dev pre-commit` + 写 `.pre-commit-config.yaml` + `uv run pre-commit install` |
| 运行时依赖        | `uv add <package>`                                                                     |
| 推远程            | 交给 `/5-git`                                                                     |

## 完成标准

- `src/<pkg>/`、`tests/`、`pyproject.toml`、`.git/` 已就位。
- `uv run pytest` 通过。
- 已展示 `git status`，且初始化产物保持未提交。
