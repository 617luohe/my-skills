# 输出表契约（写库视角）

本文定义排程结果写库的关键表、关键字段和口径差异。

## 1. 输出链路

- 结果构建：`UnitProcessor.build_result_data(...)`
- 统一写入：`UnitProcessor.build_and_write_all_schedule_results()`
- SQL 执行：`Communication.write_data(sql_list)`

## 1.1 输出契约边界

- 本文定义“写入什么”和“如何判定写入有效”。
- 具体算法如何得到结果，见 `02-CALL-CHAIN.md` 与粗排/评分文档。

## 2. 目标表与职责

| 表 | 层级 | 作用 |
|---|---|---|
| `completed_info` | 明细级 | 每块物料排程结果 |
| `completed_plan` | 计划级 | 每个辊期计划头信息与统计摘要 |
| `plan_rate_kpi` | KPI级 | 产线指标口径（含主轧材出场率等） |

## 3. 关键字段（契约级）

### 3.1 辊期相关
- `FLAG_NO`：辊期号主键语义
- `scheduling_type`：排程类型（粗排可带 `-粗排` 后缀）

### 3.2 结果统计
- `completed_plan.exit_rate`：按“排产结果与收池同类对齐”的分子/分母文本统计
- `plan_rate_kpi.exit_rate`（或主轧材出场率字段）：与上者口径不同，需区分使用

### 3.3 排程顺序
- `计划顺序号`：结果内排序位置，构建时生成

### 3.4 结果状态相关（建议关注）
- 粗排结果相关状态字段（如粗排状态、断点数、算法版本）主要来自粗排输出契约。
- 主计划状态以 `message_type/message_content` 和三表落库结果共同判定。

## 4. 粗排与主算法双写策略

有粗排时：
- 粗排使用辊期 `n`
- 主算法使用辊期 `n+1`
- 合并写入时顺序为“粗排在前，主算法在后”

无粗排时：
- 仅写主算法结果（单辊期）

## 5. 冲突与幂等

- 写库前检查三表辊期号冲突
- 任一表存在同辊期号则整批跳过
- 跳过场景会返回提示消息，并推进 `id_config` 到本批最大号

## 6. 写库成功判定（建议）

最小成功判定建议同时满足：
1. 响应为成功语义。  
2. `completed_info` / `completed_plan` / `plan_rate_kpi` 可查询到对应辊期号。  
3. `id_config["辊期号"]` 与本批最大占用号一致。  

## 7. 口径注意事项

最容易混淆：
- `completed_plan.exit_rate` 与 `plan_rate_kpi` 主轧出场率不是同一指标

详细口径与样例请看：
- `schedule_result_storage.md`

## 8. 验收建议

写库后建议至少核查：
1) 三表都有对应辊期号记录  
2) 有粗排时存在 `n` 与 `n+1` 两个辊期  
3) `scheduling_type` 能区分粗排/主算法  
4) `exit_rate` 字段可解析且口径符合预期  
5) 冲突重放请求时，系统表现为“跳过写库”而不是重复插入  

关联：
- `07-database-boundary.md`
- `schedule_result_storage.md`
