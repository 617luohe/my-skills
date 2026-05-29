# 计划评分模块 — 任务拆解

按依赖顺序排列的垂直切片，每个切片贯穿其所在层的全部层级（建表/工具 → 逻辑 → 测试/验证）。

---

## Task 1 — 评分配置表创建与数据初始化

**类型**: AFK  
**依赖**: 无  
**文件变更**:
- 新建 `结果对比工具/database/scoring_config.py` — 评分配置表 ORM 模型
- 新建 `scripts/init_scoring_config.py` — 创建表 + 写入 23 条初始配置数据的脚本

**内容**:
- 定义 `ScoringConfig` ORM 类，映射到本地 MySQL `sgjt_new` 库的 `scoring_config` 表
- 字段: `id`(PK), `item_code`, `category`, `item_name`, `score_per_unit`, `weight`, `higher_is_better`, `is_active`, `sort_order`, `formula_description`, `created_at`, `updated_at`
- 编写初始化脚本：CREATE TABLE + INSERT 23 条 CSV 中的评分项
- 验证：运行脚本后确认表存在、数据正确

---

## Task 2 — 评分数据类与上下文定义

**类型**: AFK  
**依赖**: 无  
**文件变更**:
- 新建 `src/evaluation/__init__.py`
- 新建 `src/evaluation/config.py`

**内容**:
- 定义纯数据类:
  - `ItemScore(item_code, name, category, raw_value, unit_score, weight, score)`
  - `CategoryScore(category, score, items: list[ItemScore])`
  - `PlanScoreResult(plan_id, total_score, category_scores, item_details)`
- 定义 `CalcContext(plan_info, materials, segments, main_indices, trans_indices, rolled_widths, rolled_thicks)`
- 定义 `MaterialSegments` 分段结果容器

---

## Task 3 — 分段工具与线性回归工具

**类型**: AFK  
**依赖**: Task 2  
**文件变更**:
- 新建 `src/evaluation/utils/__init__.py`
- 新建 `src/evaluation/utils/segmentation.py`
- 新建 `src/evaluation/utils/linear_fit.py`

**内容**:
- `segmentation.py`: 
  - 按物料标记分段: 区分烫辊段/过渡段/主轧段
  - 提取各段物料下标、宽度序列、厚度序列
  - 返回 `MaterialSegments` 对象
- `linear_fit.py`:
  - `linear_regression(x, y)` → `(slope, intercept, r_squared)`
  - `detect_outliers(values, std_threshold=2.0)` → `(outlier_indices, std)`
  - 处理边界情况: 数据点少于 3 个时返回 0 离散点

---

## Task 4 — 实现各级评分计算函数

**类型**: AFK  
**依赖**: Task 2, Task 3  
**文件变更**:
- 新建 `src/evaluation/calculators/__init__.py`
- 新建 `src/evaluation/calculators/counters.py`
- 新建 `src/evaluation/calculators/trend.py`
- 新建 `src/evaluation/calculators/rebound.py`
- 新建 `src/evaluation/calculators/concentration.py`
- 新建 `src/evaluation/calculators/peaks.py`
- 新建 `src/evaluation/calculators/kilometer.py`

**内容**:
每个文件实现其对应评分项的计算函数，签名统一为 `(ctx: CalcContext) -> float`：

- `counters.py`: `calc_main_rolling_count`, `calc_reusable_count`, `calc_main_gdc_count`, `calc_hot_count`, `calc_hot_cold_switch`
- `trend.py`: `calc_width_trend`, `calc_width_gdc_trend`, `calc_thick_trend`, `calc_thick_gdc_trend`
- `rebound.py`: `calc_width_rebound`, `calc_width_gdc_rebound`, `calc_thick_rebound`, `calc_thick_gdc_rebound`
- `concentration.py`: `calc_width_concentration`, `calc_thick_concentration`, `calc_sg_concentration`
- `peaks.py`: `calc_width_peak`, `calc_thick_peak`
- `kilometer.py`: `calc_roll_km_exceed`, `calc_tgc_km_exceed`

---

## Task 5 — B 类规则违规判定工具

**类型**: HITL（需确认复用方式）  
**依赖**: Task 2  
**文件变更**:
- 新建 `src/evaluation/utils/b_rule_check.py`

**内容**:
- 实现违规判定函数，供 `violations.py` 使用:
  - `check_width_violation(prev, curr)` → bool
  - `check_thick_violation(prev, curr)` → bool
  - `check_sg_violation(prev, curr)` → bool
- **HITL 原因**: 现有 `check_rules.py` 已有 B 类规则判定逻辑。需决策: 是复用现有代码还是重新实现一套轻量版本。复用可减少重复，但现有代码与评分模块的数据格式可能不完全匹配。

---

## Task 6 — 评分引擎 PlanScorer

**类型**: AFK  
**依赖**: Task 1, Task 4, Task 5  
**文件变更**:
- 新建 `src/evaluation/scorer.py`
- 修改 `src/evaluation/__init__.py` — 导出 `PlanScorer`

**内容**:
- `PlanScorer.__init__(config_items)`:
  - 接收从 scoring_config 表读取的配置列表
  - 构建 `item_code → config` 映射字典
- `PlanScorer.score(plan_info, materials)`:
  - 调用 `segmentation` 预处理物料数据 → `CalcContext`
  - 遍历 23 个已注册的计算函数，逐一计算
  - 每个计算函数传入 `CalcContext`，返回原始值
  - 用配置中的 `score_per_unit × weight` 换算为单项得分
  - 按分组聚合 → 返回 `PlanScoreResult`
- `PlanScorer.from_db(connection)`:
  - 查询 `scoring_config` 表，构造实例
- 错误处理: 单项计算异常抓取并记日志，返回 0 分不影响其他项

---

## Task 7 — 集成到结果分析工具

**类型**: HITL（需确认展示样式）  
**依赖**: Task 1, Task 6  
**文件变更**:
- 修改 `结果对比工具/data_dashboard.py`

**内容**:
- 在 `display_plan_statistics()` 之后新增评分展示区域
- 从本地 MySQL 加载 `scoring_config` → 创建 `PlanScorer` 实例
- 对当前选中计划的物料数据调用 `scorer.score()`
- 以可折叠分组列表形式展示:
  ```
  综合评分: 85.5
  ▼ 物料类型       45.0 分
    主轧数: 50 × 1.0 = 50.0
    可利用材: 3 × -1.0 = -3.0
    ...
  ▼ 轧宽           -12.0 分
    ...
  ```
- **HITL 原因**: 需要确认展示样式细节（颜色编码、排序方式、是否要同时展示人工计划和算法计划的评分对比等）

---

## Task 8 — 单元测试

**类型**: AFK  
**依赖**: Task 4, Task 6  
**文件变更**:
- 新建 `tests/evaluation/`
  - `test_counters.py`
  - `test_trend.py`
  - `test_rebound.py`
  - `test_concentration.py`
  - `test_peaks.py`
  - `test_kilometer.py`
  - `test_scorer.py`
  - `test_linear_fit.py`

**内容**:
- 为每个计算函数构造已知物料列表，验证输出值
- 边界情况测试：空列表、单条物料、缺失字段
- `PlanScorer.score()` 集成测试：完整流程验证

---

## 执行顺序

```
Task 1 (建表+初始化) ──→ Task 2 (数据类)
                            │
                            ├──→ Task 3 (工具函数)
                            │       │
                            │       └──→ Task 4 (计算函数) ──→ Task 6 (引擎) ──→ Task 7 (集成)
                            │                      ↑
                            └──→ Task 5 (B规则) ────┘
                                                      Task 8 (测试) ←──── 并行
```

所有 AFK 任务可独立开始。Task 5 和 Task 7 需要你的决策，会在执行到对应任务时提问。
