# AGENTS.md — 本仓库 AI 协作说明

面向在本项目中工作的 Agent：读者是**下一次会话里的你自己**，请保持与代码一致。

## 事实清单（须与代码一致）

- **入口**：`src/main.py`，通过 `argparse` 暴露标志位；勿臆造未实现的 CLI。
- **默认仓库**：`src/config.py` 中 `DEFAULT_REPOS`；Skill `.cursor/skills/weekly/SKILL.md` 与 `daily/SKILL.md` 内的表格应与之一致（用户若改默认仓库，两处同步）。
- **密钥**：仅 `GITEE_TOKEN`（`.env` 或环境变量）；**禁止**写入源码、禁止提交 `.env`。
- **产出**：CSV `data/source/work_content.csv`；拉取时间 `log/gitee_last_pull.json`；文档 `docs/*.md`（周报 / 日报由脚本生成）。
- **模块推断**：提交详情 API 变更文件路径的首层目录名（见 `src/gitee_api.py`）。

## 退出码（main）

| 码 | 含义 |
|----|------|
| `0` | 成功 |
| `2` | 需要拉取但未配置 `GITEE_TOKEN` |
| `3` | Gitee API 拉取失败 |
| `4` | `--repos-file` / `--repo` 解析或校验失败 |
| `5` | `--daily-date` 格式错误或单独使用 `--daily-date` 而未带 `--daily` |

## 修改约定

- 改 CLI 行为后同步更新：`README.md`、相关 Skill、本文件。
- 不在 `docs/` 手写长篇说明替代根目录 `README.md`；`docs/README.md` 仅说明目录用途。
- 用户规则要求中文回复用户；代码注释与文档语言可与仓库现有风格一致。

## 文档修订记录

- `2026-05-05`：首次创建，对齐周报/日报双模式与 Skills `weekly`、`daily`。
