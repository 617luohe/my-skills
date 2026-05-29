---
title: "PRD-排程评分集成模块"
aliases: ["评分集成模块"]
tags:
  - domain/manufacturing
  - type/prd
  - status/completed
created: 2026-05-27
updated: 2026-05-27
---

# PRD: 排程评分集成模块

> 将 PlanScorer 评分引擎从离线评测嵌入排程主流程，每次排程运行后自动评分并输出 CSV。

关联项目：[[冷热集批排产项目]]

## 背景

排程系统已完成粗轧规则排程 + 蚁群优化两阶段，拥有独立 PlanScorer 评分引擎。但评分仅离线可用，粗排和蚁群结果缺乏自动化的质量评分与持久化存档。

## 解决方案

在主流程 `entrance()` 中调换调用顺序：
```
原顺序: 算法 → evaluation() → build_and_write_all_schedule_results() → DB写入
新顺序: 算法 → build_and_write_all_schedule_results() → evaluation() → 返回
```

### 关键设计

- **评分候选数据**：`build_and_write_all_schedule_results()` 中将粗排和蚁群结果的 `completed_plan` / `completed_info` 副本存入 `self._score_candidates`
- **PlanScorer 构造**：从 DB `scoring_config` 表加载配置，懒加载 + 单次缓存
- **CSV 输出**：`coarse_evaluation_score.csv` + `main_evaluation_score.csv`，存至备份目录
- **异常隔离**：评分失败仅 warning，不阻塞主流程

### 涉及文件

| 文件 | 改动 |
|------|------|
| `src/unit_process.py` | 新增 `score_and_save_results()` / `_load_scoring_config()` / `_extract_b_rule_config()` / `_write_score_csv()`；修改 `entrance()`、`entrance_roll_replay()` |

## 不在此范围

- 评分结果写库
- 评分可视化
- 评分阈值与告警
- 跨辊期对比分析
