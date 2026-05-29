# 输入表契约（读库视角）

本文描述排程主链读取的关键输入表与用途。完整字段以 `config/unit_config.json` 为准。

## 1. 输入来源

- 配置源：`config/unit_config.json` 的 `unit_dict`
- 读取执行：`UnitProcessor.get_total_data()` -> `Communication.read_data()`
- 转换逻辑：`database_column_name` -> `pandas_column_name` -> `dtype`

## 1.1 输入契约的最小完整性

`unit_dict` 中每张输入表至少需要：
- `database_column_name`
- `pandas_column_name`
- `dtype`

三者任一与真实数据不一致，都可能在 `get_total_data` 或 `data_preprocess` 阶段失败。

## 2. 1580 / 2250 常见输入表

以下为主链高频使用表（按功能分组）：

### 2.1 库存与收池基础
- `inventory`
- `inventory_virtual`
- `inventory_virtual_ehcr`

### 2.2 B类规则
- `rule_b_thk`
- `rule_b_w`
- `rule_b_hard`
- `rule_b_gdc`
- `rule_b_cgbj`

### 2.3 其他规则/约束
- `rule_a`
- `rule_c_spelcust`
- `rule_d_model`
- `rule_d_roasting`
- `rule_d_series`
- `rule_d_hotflag`
- `same_width_limit`
- `surf_index`
- `dynamic_rule`
- `cast_speed`
- `plan_prod_time`

## 3. 特殊输入分支

### 3.1 xlsx 分支

使用 `excel_input` 提供手工文件地址及元信息，进入 `UnitProcessor.manual_plan` 处理。

### 3.2 ren（人工计划）

由手工板坯号列表拼接数据，部分库表字段映射可为空，依赖流程内二次拼接。

## 4. 高频关键字段（按用途）

| 用途 | 关键字段（示例） |
|---|---|
| 主键定位 | `板坯号` / `材料号` / `入口材料号` |
| 规格邻接 | `轧宽`、`轧厚`、`硬度组` |
| 业务规则 | `出钢标记`、冷热标记、模型相关字段 |
| 时序筛选 | `生产时刻`、`交货日期` |

## 5. 字段契约层级

为了控制文档复杂度，当前只固定“关键字段级”：

- 标识字段：板坯号/材料号/入口材料号
- 规格字段：轧宽、轧厚、硬度组、出钢标记
- 时间字段：生产时刻、交货日期
- 规则匹配字段：模型、钢系、冷热标识

如需字段级全字典，请直接查 `unit_config.json` 对应产线段。

## 6. 输入质量要求（实现口径）

`data_preprocess` 阶段会做：
- 去重
- 关键字段空值剔除
- 类型转换（按 `dtype`）
- 硬度组/表面指数代码清洗

关键表（尤其 `inventory`）为空会导致主链失败并返回失败消息。

## 7. 读库失败定位

1. 确认表是否存在且有数据  
2. 确认 `database_column_name` 与实际库字段一致  
3. 确认 `pandas_column_name` 数量与查询列一致  
4. 确认 `dtype` 可转换  

### 7.1 最小自检建议

对目标产线，先验证三件事：
1. `inventory` 能读到非空数据。  
2. `dynamic_rule` 至少有一行 `是否使用=1`。  
3. 规格字段（`轧宽`/`轧厚`）没有大面积空值或非数值。  

关联：
- `03-CONFIG-QUICK-REF.md`
- `07-database-boundary.md`
- `02-CALL-CHAIN.md`
