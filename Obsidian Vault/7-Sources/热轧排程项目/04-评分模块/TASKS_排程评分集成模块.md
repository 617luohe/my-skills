# 任务拆解: 排程评分集成模块

## 依赖图

```
Task 1 (评分数据存储) ──→ Task 2 (评分执行与CSV输出) ──→ Task 3 (主流程接入) ──→ Task 4 (端到端验证)
      AFK                         AFK                          AFK                      HITL
```

每个 Task 是可独立合并的垂直切片，前一步为后一步提供数据或能力。

---

## Task 1 — 评分数据存储 (AFK)

**目标**：在 `build_and_write_all_schedule_results()` 中，当构建粗排和蚁群结果时，将 `completed_plan` 和 `completed_info` 的副本存入 `self._score_candidates`。

**改动文件**：`src/unit_process.py`

**具体内容**：
1. 在 `__init__` 或声明区添加 `self._score_candidates: List[dict] = []`
2. 在 `build_and_write_all_schedule_results()` 中，每次 `build_result_data()` 调用后追加一条候选记录：

```python
self._score_candidates.append({
    "roll_no": roll_no,
    "suffix": scheduling_type_suffix or "",
    "completed_info": sql_build_data["completed_info"].copy(),
    "completed_plan": sql_build_data["completed_plan"].copy(),
})
```

**验证**：运行一次排程，在 `build_and_write_all_schedule_results()` 末尾加日志确认 `self._score_candidates` 有 1-2 条记录（无粗排时 1 条，有粗排时 2 条）。

**前置依赖**：无

---

## Task 2 — 评分执行与 CSV 输出 (AFK)

**目标**：新增 3 个辅助方法和 1 个核心方法，实现评分完整链路。

**改动文件**：`src/unit_process.py`

**具体内容**：

1. **`_load_scoring_config()`** — 从 DB 加载评分配置
   - 通过 `self.c.tidb_connect`（或对应连接的统一属性）获取 pymysql 连接
   - 查询 `scoring_config` 表，过滤 `is_active = 1`，按 `sort_order` 排序
   - 返回 `List[Dict[str, Any]]`（`ScoringConfigItem` 格式）

2. **`_extract_b_rule_config()`** — 从 `self.config_dict["rule_b"]` 提取 B 规则
   - 返回 `Dict[str, Any]` 含 `b_width_rules`、`b_thick_rules`、`b_sg_rules` 键
   - 若 `rule_b` 不可用或非 dict，返回空 dict

3. **`_write_score_csv(result: PlanScoreResult, is_coarse: bool)`** — 输出评分 CSV
   - 粗排文件名：`coarse_evaluation_score.csv`
   - 蚁群文件名：`main_evaluation_score.csv`
   - 每行一个评分项，列：`FLAG_NO, 排程类型, 评分分类, 评分项编码, 评分项名称, 原始值, 单位分值, 权重, 得分`
   - 编码：`utf-8-sig`
   - 保存到 `self._get_standard_backup_dir()`

4. **`score_and_save_results()`** — 遍历 `self._score_candidates` 执行评分
   - 若列表为空，直接返回
   - 首次调用时从 DB 加载配置，构造 `PlanScorer` 实例，缓存为 `self._scorer`
   - 对每条候选：
     - `plan_info` ← `cand["completed_plan"]` 第一行
     - `materials` ← `cand["completed_info"].to_dict(orient="records")`
     - `b_rule_config` ← `self._extract_b_rule_config()`
     - 调用 `scorer.score(plan_info, materials, b_rule_config)`
     - 调用 `self._write_score_csv(result, cand["roll_no"], cand["suffix"])`
     - 日志记录总分
   - 整体包裹 try/except，异常仅记录 warning

**验证**：单元测试 `_write_score_csv` 输出格式正确；调用 `score_and_save_results()` 确认评分流程不报错。

**前置依赖**：Task 1

---

## Task 3 — 主流程接入 (AFK)

**目标**：在 `entrance()` 和 `entrance_roll_replay()` 中调换调用顺序，使评分在结果构建完成后执行。

**改动文件**：`src/unit_process.py`

**具体内容**：

1. **`entrance()` 主排程流程**（第 3761-3813 行）：

原顺序：
```python
# 第3762-3765行: evaluation() — 此时只有 self.result
if self.result is not None and setting.EVALUATION:
    self.evaluation()

# 第3777行: 构建并写库
store_ok, store_msg = self.build_and_write_all_schedule_results()
```

新顺序：
```python
# 先构建并写库（此时粗排和蚁群结果都已就绪）
store_ok, store_msg = self.build_and_write_all_schedule_results()

# 再执行评价（评分 + PlanScorer）
if store_ok and setting.EVALUATION:
    self.evaluation()
```

注意：`evaluation()` 内的基础指标（`total_length`, `total_num`）仍然只基于 `self.result`（蚁群结果），新增的 PlanScorer 评分通过 `self._score_candidates` 获取两套数据。

2. **`entrance_roll_replay()` 重算流程**（第 4246-4261 行）：

同样调换 `evaluation()` 和 `build_and_write_all_schedule_results()` 的顺序。

3. **异常处理调整**：`evaluation()` 的异常处理从独立 try 块改为不阻断主流程的 warn-only 级别。

**验证**：运行完整排程，确认备份目录中 `*_evaluation_score.csv` 文件生成。

**前置依赖**：Task 2

---

## Task 4 — 端到端验证 (HITL)

**目标**：在测试环境运行完整排程，确认评分集成按预期工作。

**具体内容**：
1. 确保 `setting.EVALUATION = True`
2. 触发一次完整排程（含粗排 + 蚁群）
3. 确认备份目录下生成 `coarse_evaluation_score.csv` 和 `main_evaluation_score.csv`
4. 检查 CSV 内容：
   - 列名正确（FLAG_NO、排程类型、评分分类、评分项编码等）
   - 总分行存在且数值合理
   - 评分明细行数合理（约 23 项 × 2 份）
5. 关闭 `setting.EVALUATION` 确认评分不执行且不报错
6. 确认排程主流程正常完成，评分异常不影响写库

**决策点**：
- 评分结果文件名格式是否需要调整
- 评分结果中是否需要额外字段

**前置依赖**：Task 3
