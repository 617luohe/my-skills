---
name: daily
description: Runs the same Gitee sync policy as weekly but writes a Markdown daily report from CSV for one calendar day under docs/. Default repos match weekly skill unless overridden. Use when the user types /daily or asks for Gitee daily report generation in this project.
disable-model-invocation: true
---

# Gitee 工作日报（一键）

## 在 Cursor 里调用

Skill 标识符为 **`daily`**。在 Agent 输入 **`/daily`**，或 **`@daily`** 附加。

须与目录 `.cursor/skills/daily/` 及 frontmatter `name` 一致（仅小写、数字、连字符）。

## 项目根目录

包含 `src/main.py`、`requirements.txt` 的目录；终端先 `cd` 到该根目录。

## 默认仓库与项目名称

与周报 Skill **`weekly`** 相同；覆盖方式相同：`--repo` 或 `--repos-file`。

| owner | repo | 日报中的项目名称 |
|-------|------|------------------|
| luohe666 | mark_by_line | 冷热集批排产-控制程序 |
| luohe666 | py_src_hot_rolling | 冷热集批排产-算法程序 |

完整说明见 **`README.md`**。

## 一键执行

```bash
pip install -r requirements.txt
python src/main.py --daily
```

语义与周报相同：按 `log/gitee_last_pull.json` 判断是否在当日 0 点后已拉取；需要时同步 Gitee → 追加 `data/source/work_content.csv` → 生成 **`docs/YYYY-MM-DD日报.md`**（统计日为**本地日历当天**，可用 `--daily-date` 指定）。

仅生成文档、不拉取：`python src/main.py --daily --report-only`

常用：`--force-pull`、`--daily-date YYYY-MM-DD`、`--since-days N`、`--repo` / `--repos-file`。

## Agent 自检

- [ ] 项目根目录
- [ ] 是否覆盖仓库 / 指定 `--daily-date`
- [ ] 结束并回报日报路径
