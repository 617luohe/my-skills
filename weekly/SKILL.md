---
name: weekly
description: Runs the workspace weekly report pipeline (Gitee sync, CSV work log, Markdown weekly doc under docs/). Uses built-in default Gitee repos unless overridden via CLI or repos JSON. Use when the user types /weekly or asks for Gitee weekly report generation in this project.
disable-model-invocation: true
---

# Gitee 工作周报（一键）

## 在 Cursor 里怎么「敲命令」调用

Skill 标识符为 **`weekly`**（文件夹 `.cursor/skills/weekly/` 与下方 frontmatter `name` 须一致）。

在 **Agent（聊天）输入框**：输入 **`/weekly`** 回车，或 **`/`** 后从列表选择 **`weekly`**；也可用 **`@weekly`** 附加为上下文。

说明：Cursor 要求 `name` **仅含小写字母、数字、连字符**，不能使用带大写的写法（例如 **`/weekLy` 无效**），因此本仓库采用 **`/weekly`** 作为最短合规命名。

本 Skill 已设置 `disable-model-invocation: true`，适合手动 **`/`** 触发。

## 项目根目录

以包含 `src/main.py`、`requirements.txt` 的目录为根目录；在终端中先 `cd` 到该目录。

## 默认仓库与项目名称（未覆盖时使用）

| owner | repo | 周报中的项目名称 |
|-------|------|------------------|
| luohe666 | mark_by_line | 冷热集批排产-控制程序 |
| luohe666 | py_src_hot_rolling | 冷热集批排产-算法程序 |

依赖：`requirements.txt`；令牌为环境变量 `GITEE_TOKEN` 或根目录 `.env`（勿提交）。

完整目录说明与命令表见仓库根目录 **`README.md`**。

## 一键执行（默认仓库）

```bash
pip install -r requirements.txt
python src/main.py
```

语义简述：若 `log/gitee_last_pull.json` 表明当日已在本地 0 点之后成功拉取过，则跳过 Gitee，仅用 `data/source/work_content.csv` 生成周报；否则拉取并追加 CSV，再写 `docs/` 下按 ISO 周命名的周报文件。

常用标志：`--force-pull`、`--report-only`、`--report-days N`、`--since-days N`。

## 调用时覆盖仓库（任选其一）

**方式 A：** 重复 `--repo`，格式 `owner::repo::项目展示名`（双冒号三段）。

```bash
python src/main.py --repo "other_owner::other_repo::我的新项目-A"
python src/main.py --repo "myorg::svc-api::服务后端" --repo "myorg::svc-job::定时任务"
```

**方式 B：** `--repos-file PATH`（JSON 数组，路径相对项目根）。若同时提供 **`--repos-file`，仅以文件为准**。

```json
[
  { "owner": "luohe666", "repo": "mark_by_line", "project_label": "冷热集批排产-控制程序" },
  { "owner": "luohe666", "repo": "py_src_hot_rolling", "project_label": "冷热集批排产-算法程序" }
]
```

Agent：用户口头改仓库时再拼 `--repo` 或临时 JSON；未要求则不加覆盖参数。

## Agent 自检

- [ ] 工作目录为项目根
- [ ] 是否需覆盖默认仓库
- [ ] 命令结束并回报周报路径（及 CSV / log 摘要）
