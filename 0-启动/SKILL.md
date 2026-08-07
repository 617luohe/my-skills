---
name: 0-启动
description: Python 项目最小初始化：项目结构 + 本地 git + uv 环境
disable-model-invocation: true
---

# 0-启动 — 新项目最小初始化

小项目开张只要三件事：**一个项目结构、一个本地 git、一个 uv 环境**。做完就能写代码。

## MUST 规则

1. **只做这三件事。** ruff / mypy / pre-commit / CI / 任务管理文件一律不装、不问、不生成——用户主动要才加（见「按需追加」）。
2. **只问一轮。** 项目名 + 位置。Python 版本不问，默认由 uv 选当前解释器并写入 `.python-version`；用户点名版本才用 `-p`。
3. **uv 缺失自动装，不问。**
4. **收尾必须验证。** `uv run pytest` 通过才算完成。

## 流程

### 1. 确认（一轮）

- **项目名** — 用于目录名和包名。带连字符没问题，uv 会把包目录转成下划线（`my-app` → `src/my_app/`）。
- **位置** — 新建子目录，还是在当前空目录里初始化。

### 2. 备好 uv

```bash
uv --version
```

没装就装，装完继续：

```bash
# Windows
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
# macOS / Linux / WSL
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### 3. 建结构 + git（一条命令）

```bash
uv init --package --vcs git <project-name>   # 新建目录
uv init --package --vcs git .                # 在当前空目录初始化
```

产出：

```
project-name/
├── src/project_name/__init__.py   # 带 main() 入口
├── pyproject.toml
├── README.md
├── .python-version
├── .gitignore                     # Python 标准规则 + .venv
└── .git/                          # 已 init，尚无提交
```

要点：
- 目录名不是合法包名时（比如以数字或下划线开头），补 `--name <pkg-name>`。
- 指定 Python 版本：`uv init --package --vcs git -p 3.12 <project-name>`。
- 纯脚本、不打包的一次性工具用 `uv init`（不带 `--package`）——扁平布局，根目录一个 `main.py`。

### 4. 加 tests + 建环境

```bash
mkdir tests
```

`tests/test_smoke.py`：

```python
def test_smoke() -> None:
    assert True
```

```bash
uv add --dev pytest
```

这一步顺带创建 `.venv/` 和 `uv.lock`，并把项目自身以可编辑方式装进环境——测试里 `from project_name import ...` 直接可用，不用配 path。

### 5. 验证 + 首次提交

```bash
uv run pytest
git add . && git commit -m "chore: 初始化项目"
```

## 按需追加

用户主动提了才做，各一行搞定，不主动推销：

| 需求 | 命令 |
|------|------|
| 代码检查 / 格式化 | `uv add --dev ruff` |
| 类型检查 | `uv add --dev mypy` |
| 提交前门禁 | `uv add --dev pre-commit` + 写 `.pre-commit-config.yaml` + `uv run pre-commit install` |
| 运行时依赖 | `uv add <package>` |
| 推远程 | 交给 `/5-版本管理` |

工具配置统一写进 `pyproject.toml` 的 `[tool.*]`，不另开配置文件。

## 验证清单

- [ ] `src/<pkg>/` 和 `tests/` 就位
- [ ] `.venv/` 和 `uv.lock` 已生成
- [ ] `uv run pytest` 通过
- [ ] git 已 init 且有首次提交

## 什么时候用

- 开一个新的 Python 项目，想立刻能写代码
- 手上一堆散装脚本，要收成一个正经项目

## 案例

```
你：/0-启动 新建一个项目叫 data-pipeline
Claude：在当前目录下新建 data-pipeline/ 子目录，还是就在这个目录初始化？
你：新建子目录
Claude：[uv init --package --vcs git data-pipeline → tests/test_smoke.py → uv add --dev pytest]
        1 passed。git 首次提交完成。
        环境就绪：uv run data-pipeline 跑入口，uv run pytest 跑测试。
        要 ruff / mypy / pre-commit 说一声，一行就加。
```
