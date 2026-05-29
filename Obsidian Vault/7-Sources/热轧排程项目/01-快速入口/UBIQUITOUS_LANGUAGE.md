# 统一语言 / Ubiquitous Language

> 热轧排程评价体系 — 领域术语表

## 规范术语

| 术语 | 英文对照 | 定义 |
|------|----------|------|
| 辊期 | Roll Cycle | 从更换轧辊开始到下一次更换轧辊为止的完整轧制处理单元，由 FLAG_NO 唯一标识 |
| 主轧材 | Main Rolling Material (ZZC) | 辊期中主要轧制的物料，希望尽可能多排入，对邻接规则要求严格 |
| 次轧材 | Secondary Material (CZC) | 用于填充辊期的物料，当主轧材数量不足时使用，防止辊期过短造成轧辊浪费 |
| 过渡材 | Transition Material (GDC) | 用于在规格差异大的物料之间进行过渡，保证轧机设备平稳过渡，防止安全事故 |
| 烫辊材 | Roll Warming Material (TGC) | 轧制难度低的物料，用于辊期开头预热轧辊，降低安全风险 |
| 可利用材 | Reusable Material (KLY) | 规格可变的物料，可通过切割改变规格，用于补充过渡材无法过渡的规格缺口 |
| 主轧段 | Main Rolling Section | 辊期中以主轧材为主的核心轧制阶段，邻接规则要求最严格 |
| 烫辊段 | Roll Warming Section | 辊期开头轧制烫辊材的阶段，用于预热新轧辊 |
| 过渡段 | Transition Section | 连接烫辊段与主轧段的中间阶段，实现规格的平滑过渡 |
| 物料邻接 | Material Adjacency | 相邻两块物料之间的衔接关系，需满足 B 类规则的约束 |
| B 类规则 | Type B Rule | 物料邻接的基本约束规则，定义相邻物料在宽度、厚度、硬度等属性上的允许跳变范围 |
| C 类规则 | Type C Rule | 辊期公里数的约束规则，定义不同规格组合下的允许公里数范围 |
| 出钢标记 | Tapping Mark (SG_SIGN) | 反映钢材内部成分和轧制工艺的编码，越相似的出钢标记物理性质越接近 |
| 冷热坯 / 冷热标记 | Hot/Cold Slab Flag (COLD_HOT_FLAG) | 标识物料是热装（H）还是冷装（C），影响加热炉能耗和轧制节奏 |
| 热装 | Hot Charging (H) | 物料在热状态下直接送入加热炉，节能降耗 |
| 轧宽 | Rolling Width (OUT_MAT_WIDTH) | 物料通过轧机达到的目标宽度 |
| 轧厚 | Rolling Thickness (OUT_MAT_THICK) | 物料通过轧机达到的目标厚度，厚度越小轧制难度越高 |
| 公里数 | Slab Kilometer | 辊期中所有物料长度累计的轧制总长度，受 C 类规则约束 |
| 宽窄印记 | Width Mark / Shadow Mark | 较窄物料在轧辊上留下的痕迹可能印在后续更宽物料表面，影响表面质量 |

## 评分体系专有术语

| 术语 | 定义 |
|------|------|
| 评分项 | Scoring Item | 一个具体的评分维度，如"主轧数"、"轧宽违规"等 |
| 评分分组 | Scoring Category | 评分项的逻辑分组，如"物料类型"、"轧宽"、"轧厚"等 |
| 原始值 | Raw Value | 评分逻辑计算出的未经换算的数值，如主轧材卷数 50 |
| 每单位分数 | Score Per Unit | 每单位原始值对应的分数，如"+1分/卷"、" -5分/处" |
| 权重 | Weight | 评分项的加权系数，默认为 1.0，用于调整不同评分项的相对重要性 |
| 单项得分 | Item Score | = 原始值 × 每单位分数 × 权重 |
| 总分 | Total Score | = Σ 所有单项得分 |
| 趋势拟合 | Trend Fitting | 将物料序号与规格值做线性回归，评估规格变化的均匀程度 |
| 离散点 | Outlier | 距离拟合直线超过 2 个标准差的物料点，反映规格突变 |
| 反跳 | Rebound / Back-jump | 在单调趋势中出现的反向跳变（如宽度本应收窄却变宽） |
| 尖点 | Peak Point | 当前物料规格值大于其前后相邻两卷的规格值 |
| 同规则集中 | Same-rule Concentration | 相同规格值的物料连续或独立排列形成的段的数量统计 |

## 系统概念

| 术语 | 定义 |
|------|------|
| `completed_plan` | 计划级数据表，存储每个辊期的元数据（FLAG_NO、产线、模型等） |
| `completed_info` | 物料级明细表，存储每个辊期中每块物料的完整属性 |
| `scoring_config` | 评分配置表，存储评分项定义（本地 MySQL `sgjt_new` 库） |
| 结果分析工具 | 基于 Streamlit 的仪表板，用于对比分析人工计划与系统计划 |
| 计划统计 | 结果分析工具中的一个展示分区，当前显示库存统计和物料分类统计，后续扩展评分展示 |
| 粗排结果 | Coarse Rolling Result | 粗轧规则排程器输出的排程结果，保存为 `coarse_rule_schedule_result.csv`，排程类型标记为"-粗排" |
| 蚁群结果 / 主算法结果 | Ant Colony Result / Main Algorithm Result | 蚁群优化算法（`HotRollingSchedule`）输出的排程结果，是系统的核心排程输出，排程类型默认不加后缀 |
| 评分 CSV | Scoring CSV | 保存评分结果的 CSV 文件，粗排对应 `coarse_evaluation_score.csv`，蚁群对应 `main_evaluation_score.csv`，输出到备份目录 |
| 排程类型 | Schedule Type | 区分粗排和蚁群排程的标记，在写入 `completed_plan` 时通过 `scheduling_type_suffix` 参数控制 |
| 备份目录 | Backup Directory | 排程过程数据的存储目录，路径模式：`{BACKUP_PATH}/{辊期号}_{开始时间}_{产线}_{模型列表}/` |
| 评价方法 | `evaluation()` | `UnitProcess` 类的方法，计算基础评价指标（总长、块数、耗时）并调用 PlanScorer 进行评分 |

## 术语关系

```
辊期 (FLAG_NO)
 ├── 烫辊段 → 含烫辊材 (TGC)
 ├── 过渡段 → 含过渡材 (GDC) + 可利用材 (KLY)
 └── 主轧段 → 含主轧材 (ZZC) + 次轧材 (CZC) + 少量过渡材 (GDC)

评分体系
 ├── 评分分组 (Category)
 │    ├── 物料类型
 │    ├── 轧宽
 │    ├── 轧厚
 │    ├── 出钢标记
 │    ├── 冷热坯
 │    └── 公里数
 └── 评分项 (Item) → 从属于某个分组
      └── 每项产出: 原始值 → 单项得分 → 汇总为总分
```

## 库区调序专有术语

| 术语 | 英文对照 | 定义 |
|------|----------|------|
| 层号 | Layer Number | 物料在仓库库位中的叠放层号，反映物料在库区中的物理位置和取用顺序 |
| 材料库位号 | Warehouse Location Code | 物料在仓库中存放的具体库位编号，用于标识物料所在的物理区域 |
| 相同规格物料 | Same-specification Materials | 在出钢标记、宽度、厚度、材料库位号上完全一致的物料集合 |
| 层号排序 | Layer Number Reordering | 将相同规格的物料组内按层号从大到小（上层优先）重新排列的过程，使取用顺序更合理 |
| 调序函数 | Reorder Function | 对排程结果按规格分组+层号排序的独立函数，可作用于粗排结果和蚁群结果 |

## 歧义标记

| 词条 | 歧义说明 |
|------|----------|
| 可利用材 | CSV 中称"可利用材"，排程背景中也可写作"次轧材"的一种补充。需确认：可利用材在评分中单独计 -1 分/卷，与次轧材是否为同一概念 |
| 过渡材 / 主轧段过渡材 | CSV 中"主轧段过渡材"特指主轧段内出现的过渡材，而非过渡段中的过渡材。两者计分标准不同 |
