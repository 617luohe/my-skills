# 脚手架细节

## uv 安装

```bash
# Windows
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
# macOS / Linux / WSL
curl -LsSf https://astral.sh/uv/install.sh | sh
```

## 初始化命令

```bash
uv init --package --vcs git <project-name>   # 新建目录
uv init --package --vcs git .                # 当前空目录
```

产出结构：

```
project-name/
├── src/project_name/__init__.py
├── pyproject.toml
├── README.md
├── .python-version
├── .gitignore
└── .git/
```

- 目录名非法包名时：`--name <pkg-name>`
- 指定 Python：`uv init --package --vcs git -p 3.12 <name>`
- 纯脚本：`uv init`（无 `--package`）

## tests + 环境

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
uv run pytest
git status --short --branch
```

## 按需追加

| 需求 | 命令 |
|------|------|
| ruff | `uv add --dev ruff` |
| mypy | `uv add --dev mypy` |
| pre-commit | `uv add --dev pre-commit` + 配置 + `uv run pre-commit install` |
| 运行时依赖 | `uv add <package>` |
| 推远程 | 交给 `/5-git` |

工具配置写进 `pyproject.toml` 的 `[tool.*]`。

## 验证清单

- [ ] `src/<pkg>/` 和 `tests/` 就位
- [ ] `.venv/` 和 `uv.lock` 已生成
- [ ] `uv run pytest` 通过
- [ ] git 已 init，产物保持未提交并已展示状态
