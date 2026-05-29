# PRD — 热轧排程计划评分模块

## Problem Statement

热轧排程系统每生成一个辊期计划，目前缺乏量化的评价手段来判断计划质量的好坏。计划员只能凭经验判断一个计划是否"合理"，无法在多个候选计划之间做客观比较，也无法量化排程算法的优化效果。

需要一个**计划评分模块**，对每个排出的辊期计划进行多维度量化评分，并将评分结果在结果分析工具中进行可视化展示。

## Solution

构建一个独立的评分模块 `src/evaluation/`，核心职责：

1. **接收**：一份辊期计划的物料明细数据（`completed_info`）及其计划元数据（`completed_plan`）
2. **计算**：按照 6 大类 23 项评分指标逐一计算原始值，换算为单项得分，聚合为总分
3. **输出**：结构化的评分结果（总分、分组得分、每项得分明细）

评分模块不直接连接数据库，所有数据由调用方传入。既可被结果分析工具（Streamlit）调用用于展示，也可被排程系统在计划生成后自动调用。

## User Stories

- **As a** 计划员（结果分析工具用户），**I want** 在查看计划时看到该计划的量化评分，**so that** 我可以快速判断计划质量，而不必逐条检查规则。
- **As a** 计划员，**I want** 看到评分按分组归类（物料类型/轧宽/轧厚/出钢标记/冷热坯/公里数），**so that** 我可以定位计划的薄弱维度。
- **As a** 排程算法开发人员，**I want** 对同一订单池用不同参数排出的多个计划进行评分对比，**so that** 我可以客观评估算法调优效果。
- **As a** 系统运维人员，**I want** 评分项的每单位分数和权重可配置，**so that** 我可以根据现场反馈调整评分倾向而不改代码。

## Implementation Decisions

### 模块结构

```
src/evaluation/
├── __init__.py              # 导出 PlanScorer
├── scorer.py                # PlanScorer 类：编排评分流程
├── config.py                # 数据类定义（ItemScore, CategoryScore, PlanScoreResult 等）
├── calculators/
│   ├── __init__.py           # 注册所有计算函数
│   ├── counters.py          # 计数类（主轧数、可利用材、热装数、主轧段过渡材数）
│   ├── violations.py        # B 类规则违规判定（轧宽/轧厚/出钢标记）
│   ├── trend.py             # 线性拟合 + 离散点检测（宽/厚 × 主轧段/过渡段）
│   ├── rebound.py           # 反跳累计（宽/厚 × 主轧段/过渡段）
│   ├── concentration.py     # 集中度/分段统计（同宽/同厚/同出钢标记）
│   ├── peaks.py             # 尖点检测（宽/厚）
│   └── kilometer.py         # 公里数合规
└── utils/
    ├── segmentation.py      # 分段逻辑：区分烫辊段/过渡段/主轧段
    ├── linear_fit.py        # 线性回归 + 标准差 + 离散点识别
    └── b_rule_check.py      # B 类规则判定工具
```

### 核心接口

```python
class PlanScorer:
    @classmethod
    def from_db(cls, connection) -> PlanScorer: ...
    
    def __init__(self, config_items: list[dict]): ...
    
    def score(self, plan_info: dict, materials: list[dict]) -> PlanScoreResult: ...
```

### 计算架构

每个评分项对应一个独立函数，签名统一为 `(ctx: CalcContext) -> float`：

```python
@dataclass
class CalcContext:
    plan_info: dict
    materials: list[dict]           # 原始全量物料列表
    segments: MaterialSegments      # 预计算的分段结果
    main_indices: list[int]         # 主轧段物料下标
    trans_indices: list[int]        # 过渡段物料下标
    rolled_widths: list[float]      # 宽度序列（按序）
    rolled_thicks: list[float]      # 厚度序列（按序）
```

预处理（分段、排序）在 `score()` 中一次性完成，所有计算函数共享上下文。

### 数据存储

- **评分配置**（`scoring_config`）：存储在本地 MySQL（127.0.0.1:3306）的 `sgjt_new` 库
- **评分结果**：当前阶段不持久化，展示时实时计算

### 配置项计算逻辑

| item_code | category | 计算逻辑 | 每单位分数 | 权重 |
|-----------|----------|----------|-----------|------|
| main_rolling_count | 物料类型 | 统计 zzc_sign=1 的物料数 | +1.0 | 1.0 |
| reusable_count | 物料类型 | 统计可利用材标记的物料数 | -1.0 | 1.0 |
| main_gdc_count | 物料类型 | 统计主轧段中 gdc_sign=1 的物料数 | -0.5 | 1.0 |
| width_violation | 轧宽 | 主轧段相邻物料违反 B 类轧宽规则的处数 | -5.0 | 1.0 |
| width_trend | 轧宽 | 主轧段轧宽线性拟合，2σ 外离散点数 | -2.0 | 1.0 |
| width_rebound | 轧宽 | 主轧段中当前物料之前轧宽小于当前值的物料数之和 | -1.0 | 1.0 |
| width_gdc_trend | 轧宽 | 过渡段轧宽线性拟合，2σ 外离散点数 | -2.0 | 1.0 |
| width_gdc_rebound | 轧宽 | 过渡段中当前物料之前轧宽大于当前值的物料数之和 | -1.0 | 1.0 |
| width_peak | 轧宽 | 轧宽值大于前后两卷的物料数 | -2.0 | 1.0 |
| width_concentration | 轧宽 | 同轧宽值的连续段数量 | -1.0 | 1.0 |
| thick_violation | 轧厚 | 主轧段相邻物料违反 B 类轧厚规则的处数 | -5.0 | 1.0 |
| thick_trend | 轧厚 | 主轧段轧厚线性拟合，2σ 外离散点数 | -2.0 | 1.0 |
| thick_rebound | 轧厚 | 主轧段中当前物料之前轧厚小于当前值的物料数之和 | -1.0 | 1.0 |
| thick_gdc_trend | 轧厚 | 过渡段轧厚线性拟合，2σ 外离散点数 | -2.0 | 1.0 |
| thick_gdc_rebound | 轧厚 | 过渡段中当前物料之前轧厚大于当前值的物料数之和 | -1.0 | 1.0 |
| thick_peak | 轧厚 | 轧厚值大于前后两卷的物料数 | -2.0 | 1.0 |
| thick_concentration | 轧厚 | 同轧厚值的连续段数量 | +0.5 | 1.0 |
| sg_violation | 出钢标记 | 相邻物料出钢标记违反 B 类规则的处数 | -5.0 | 1.0 |
| sg_concentration | 出钢标记 | 同出钢标记值的连续段数量 | +0.5 | 1.0 |
| hot_count | 冷热坯 | 冷热标记为 H 的物料数 | +2.0 | 1.0 |
| hot_cold_switch | 冷热坯 | 相邻物料 C/H 或 H/C 切换的次数 | -1.0 | 1.0 |
| roll_km_exceed | 公里数 | 辊期总公里数超过 C 类规则约束的数量 | -1.0 | 1.0 |
| tgc_km_exceed | 公里数 | 烫辊段公里数超过 C 类规则约束的数量 | -0.5 | 1.0 |

### 输出结构

```python
@dataclass
class PlanScoreResult:
    plan_id: str
    total_score: float                              # 总分
    category_scores: dict[str, CategoryScore]       # 按分组聚合
    item_details: list[ItemScore]                   # 23 项明细

@dataclass 
class CategoryScore:
    category: str
    score: float           # 该分组总分
    items: list[ItemScore]

@dataclass
class ItemScore:
    item_code: str
    name: str
    category: str
    raw_value: float        # 原始值（如主轧材 50 卷）
    unit_score: float       # 每单位分数
    weight: float           # 权重
    score: float            # = raw_value × unit_score × weight
```

### 结果分析工具集成

在 `数据仪表板/data_dashboard.py` 的"计划统计"分区中新增评分展示区域：

```
┌─────────────────────────────────────────┐
│  计划统计                                 │
│  ┌──────────┬──────────┬──────────┐      │
│  │ 库存统计  │ 人工计划  │ 算法计划  │      │
│  └──────────┴──────────┴──────────┘      │
│  ┌────────────────────────────────────┐  │
│  │ 计划评分                            │  │
│  │ 综合评分: 85.5                      │  │
│  │                                     │  │
│  │ ▼ 物料类型        45.0 分           │  │
│  │   主轧数: 50 × 1.0 = 50.0           │  │
│  │   可利用材: 3 × -1.0 = -3.0         │  │
│  │   主轧段过渡材: 4 × -0.5 = -2.0     │  │
│  │                                     │  │
│  │ ▼ 轧宽           -12.0 分           │  │
│  │   ...                               │  │
│  └────────────────────────────────────┘  │
└─────────────────────────────────────────┘
```

## Testing Decisions

| 测试层级 | 内容 | 方式 |
|----------|------|------|
| 单元测试 | 每个计算函数（23 项） | 构造已知输入的物料列表，验证输出值正确 |
| 单元测试 | 线性回归工具、离散点检测 | 已知序列输入，验证拟合参数和离散点识别 |
| 集成测试 | PlanScorer.score() | 用完整的计划数据 mock 输入，验证输出结构完整 |
| 配置测试 | scoring_config 表读写 | 本地 MySQL 验证建表和初始数据写入 |

不测试的内容：
- Streamlit 前端展示逻辑（手动验证）
- 结果分析工具的导出功能（已有测试覆盖）

## Out of Scope

- 评分结果持久化存储（后续按需添加）
- CSV/KPI 导出（后续按需添加）
- 多套评分方案的切换功能
- 评分历史趋势图表
- 评分权重的自动优化/学习
