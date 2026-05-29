# 数据库边界（读写职责与失败语义）

本文定义“哪些代码负责读库/写库、何时写、失败时怎样表现”。

## 1. 边界总览

- DB 访问层：`src/communication.py`
- 编排层：`src/unit_process.py`
- 原则：`unit_process` 负责业务编排，`communication` 负责连接与 SQL 执行。

支持的 DB 分支（当前实现）：
- `tidb`（默认）
- `sqlserver`

## 2. 读库边界

入口：`UnitProcessor.get_total_data(self.c)` -> `Communication.read_data(...)`。

核心行为：
1) `unit_process` 传入 `unit_dict` 作为读表规范  
2) `communication.select_table` 根据 `database_column_name` 组装 `SELECT`  
3) 返回 `dict[table_name -> rows/None]`  
4) `unit_process` 负责转 `DataFrame`、列名映射、空表策略处理  

失败语义：
- 关键表（如 `inventory`）读取失败会抛错中止
- 非关键虚拟库存表允许按分支退化

### 2.1 读库最小时序

1. `UnitProcessor.get_unit_info()` 加载 `unit_dict`。  
2. `UnitProcessor.get_total_data(self.c)` 发起读库。  
3. `Communication.select_table(...)` 按表逐一执行 `SELECT`。  
4. 回到 `unit_process` 做 `DataFrame` 化与字段校验。  

## 3. 写库边界

入口：`UnitProcessor.build_and_write_all_schedule_results()`。

核心行为：
1) 构建结果数据（有粗排时：粗排 n + 主算法 n+1）  
2) `build_sql(...)` 生成 SQL 批次文件  
3) `Communication.write_data(sql_list)` 执行事务写入  
4) 写库成功后推进 `id_config["辊期号"]`  

写库目标表（当前主链）：
- `completed_info`
- `completed_plan`
- `plan_rate_kpi`

### 3.1 写库最小时序

1. 结果构建：`build_result_data`。  
2. 冲突检查：`_check_roll_no_conflict_before_store`。  
3. SQL 生成：`build_sql`。  
4. DB 执行：`Communication.write_data`。  
5. 成功后推进 `id_config["辊期号"]`。  

## 4. 防重与冲突策略

写库前执行 `_check_roll_no_conflict_before_store(...)`：
- 在三张目标表中检查 `FLAG_NO` 是否已存在
- 任一存在则整批跳过写库
- 返回消息中标记“冲突已跳过”，并推进 `id_config` 到本批最大号

> 注意：冲突场景“跳过写库但推进辊期号”是实现约定，用于避免后续重复占号。

## 5. SQL 生成与可追溯性

- SQL 文本由 `build_sql(...)` 统一构建
- 批次 SQL 落盘目录：`setting.SQL_BATCH_DIR`
- SQL 执行失败时，错误 SQL 追加到 `setting.SQL_LOG_PATH`

## 6. 与接口契约的关系

- 对外仍通过 `message_type` / `message_content` 返回执行结果
- DB 层异常通常映射为失败消息，不直接暴露 SQL 细节

## 7. 排查建议

1. 先看连接参数：`setting.SQL_FUNCTION` 与对应 `config/*_config.json`  
2. 再看读表映射：`unit_config.unit_dict` 中字段定义  
3. 再看写库冲突：`FLAG_NO` 是否已存在  
4. 最后看 SQL 批次文件与日志  

### 7.1 常见根因速查

| 现象 | 根因方向 | 优先动作 |
|---|---|---|
| 读库返回空 | 表无数据/过滤条件不匹配 | 先查源表与 `unit_dict` |
| SQL 执行失败 | 字段不匹配/值格式异常 | 查 `SQL_LOG_PATH` 对应 SQL |
| 写库被跳过 | 辊期冲突 | 先查三表是否已有同 `FLAG_NO` |

关联文档：
- `04-INTERFACE-CONTRACT.md`
- `08-input-tables-schema.md`
- `09-output-tables-schema.md`
