# PRD: 排程评分集成模块

## Problem Statement

排程系统已完成粗轧规则排程和蚁群优化算法两阶段排程，并拥有独立的 `PlanScorer` 评分引擎。但目前评分引擎仅在离线/评测模式下可用，未嵌入排程主流程。每次排程运行后，粗排结果和蚁群结果缺乏自动化的质量评分，评分结果也未以结构化方式持久化到备份目录供后续分析。

## Solution

在排程主流程中嵌入评分步骤：当粗排和蚁群算法完成、结果数据构建完毕后，调用 `PlanScorer` 分别对两套排程结果进行评分，将评分明细以 CSV 格式保存到当前辊期的备份目录中。

## User Stories

- As a 排程工程师, I want 排程运行后自动获得粗排和蚁群结果的评分，以便快速评估排程质量
- As a 排程工程师, I want 评分结果以 CSV 保存到备份目录，以便存档和后续分析
- As a 系统维护者, I want 评分异常不影响主流程，以便排程仍能正常完成

## Implementation Decisions

### 程序结构

调换 `entrance()` 中两步调用的顺序：

```
原顺序:  算法 → evaluation() → build_and_write_all_schedule_results() → DB写入
新顺序:  算法 → build_and_write_all_schedule_results() → evaluation() → 返回
```

### 评分数据来源

- `build_and_write_all_schedule_results()` 中在调用 `build_result_data()` 后，将粗排和蚁群结果的 `completed_plan` 和 `completed_info` 副本存入 `self._score_candidates` 列表
- `evaluation()` 内的评分步骤遍历 `_score_candidates`，使用 `PlanScorer.score(plan_info, materials, b_rule_config)` 评分

### PlanScorer 构造

- **评分配置**：从 DB `scoring_config` 表加载（通过 `Communication` 实例获取连接）
- **加载时机**：首次评分时懒加载，缓存在 `self._scorer` 中，单次运行只加载一次
- **B 规则**：从 `self.config_dict["rule_b"]` 提取，封装为 `{b_width_rules, b_thick_rules, b_sg_rules}` 格式

### CSV 输出格式

两个文件，存到 `self._get_standard_backup_dir()` 返回的备份目录：

| 文件 | 内容 |
|------|------|
| `coarse_evaluation_score.csv` | 粗排评分明细 |
| `main_evaluation_score.csv` | 蚁群结果评分明细 |

每行一个评分项，列结构：

| FLAG_NO | 排程类型 | 评分分类 | 评分项编码 | 评分项名称 | 原始值 | 单位分值 | 权重 | 得分 |
|---------|---------|---------|-----------|---------|-------|---------|-----|------|

### 控制标志

- 复用 `setting.EVALUATION`，统一控制基础评估和 PlanScorer 评分
- 评分失败仅记录警告，不阻塞排程主流程

### 涉及文件

| 文件 | 改动 |
|------|------|
| `src/unit_process.py` | 新增 `score_and_save_results()`、`_load_scoring_config()`、`_extract_b_rule_config()`、`_write_score_csv()` 方法；修改 `entrance()`、`entrance_roll_replay()` 调用顺序；修改 `build_and_write_all_schedule_results()` 存储评分候选数据 |

## Testing Decisions

- 评分集成不引入新的独立测试模块
- 验证方式：在测试环境运行一次完整排程，确认备份目录下出现 `coarse_evaluation_score.csv` 和 `main_evaluation_score.csv`，内容格式正确、数值合理
- `PlanScorer` 各评分项的单元测试已在 `src/evaluation/` 中覆盖

## Out of Scope

- 评分结果写库（当前仅存 CSV）
- 评分结果可视化（后续在计划统计/结果分析工具中扩展）
- 评分阈值和告警（当前仅记录分值，不判断优劣）
- 跨辊期评分对比分析
