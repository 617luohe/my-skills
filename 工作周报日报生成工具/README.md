# 工作周报 / 日报生成工具

从 Gitee 仓库拉取提交（可选）、写入本地工作明细 CSV，并生成 Markdown **周报**（按 ISO 周命名）或 **日报**（按自然日命名）。

## 环境

- Python 3.10+（开发验证使用 Python 3.12）
- 依赖：`pip install -r requirements.txt`

## 配置

1. 复制 `.env.example` 为 `.env`（`.env` 已被 `.gitignore` 忽略）。
2. 在 `.env` 或环境中设置 **`GITEE_TOKEN`**（Gitee 私人令牌，勿提交、勿粘贴到即时通讯）。

## 目录结构（概要）

| 路径 | 说明 |
|------|------|
| `src/main.py` | CLI 入口 |
| `src/config.py` | 默认仓库列表、`resolve_repos` |
| `data/source/work_content.csv` | 提交摘要明细（按 `sha` 去重追加） |
| `log/gitee_last_pull.json` | 上次成功从 Gitee 拉取的时间戳 |
| `docs/` | 生成的周报 / 日报 Markdown（见 `docs/README.md`） |
| `.cursor/skills/weekly/` | Cursor Skill：手动 **`/weekly`** |
| `.cursor/skills/daily/` | Cursor Skill：手动 **`/daily`** |

## 默认 Gitee 仓库

可在 `src/config.py` 的 `DEFAULT_REPOS` 中修改；运行时也可用 `--repo` / `--repos-file` 覆盖（详见 `--help`）。

| owner | repo | 周报/日报中的项目名称 |
|-------|------|------------------------|
| luohe666 | mark_by_line | 冷热集批排产-控制程序 |
| luohe666 | py_src_hot_rolling | 冷热集批排产-算法程序 |

## 命令行（在项目根目录执行）

```bash
python src/main.py
```

- **周报**：默认生成 `docs/` 下 `YYYY年第WW周周报.md`；正文默认汇总 CSV 中最近 **14** 个自然日（可用 `--report-days N`）。
- **日报**：`python src/main.py --daily` → `docs/YYYY-MM-DD日报.md`；可用 `--daily-date YYYY-MM-DD`（须与 `--daily` 同时使用）。
- **仅生成文档、不请求 Gitee**：`--report-only`。
- **强制重新拉取**：`--force-pull`。
- **只同步 CSV、不写 Markdown**：`--skip-report`。
- **自定义拉取起始**：`--since-days N`（自本地今日往前第 N 天 0 时起）。
- **覆盖仓库**：`--repo "owner::repo::展示名"`（可重复），或 `--repos-file path/to.json`（JSON 数组；若提供文件则优先于 `--repo`）。

同步策略简述：若 `log/gitee_last_pull.json` 中的时间在**本地日历当日 0 点之后**，且未指定 `--force-pull`，则跳过远端拉取，仅用现有 CSV 生成文档。

## Cursor Agent Skills

在 Cursor Agent 输入 **`/weekly`** 或 **`/daily`**（须与 `.cursor/skills/<name>/SKILL.md` 中 `name` 一致）。详见各 Skill 文件正文。

## 文档修订记录

- `2026-05-05`：首次补充本 README，与当前代码及 Skills 对齐。
