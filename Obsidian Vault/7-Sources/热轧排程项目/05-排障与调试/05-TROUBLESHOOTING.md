# 故障排查手册（症状 -> 定位 -> 处理）

本文用于线上/联调快速定位，不替代深度算法文档。

## 1. 排查总原则

1. 先确认请求是否走到正确分支（`main.py`）  
2. 再确认入口是否返回可解析 JSON（`entry.py`）  
3. 再确认数据与配置是否完整（`unit_process.py` + `setting/config`）  
4. 最后看算法与写库细节（粗排/评分/SQL）  

## 2. 常见症状与处理

| 症状 | 优先检查 | 常见根因 | 处理建议 |
|---|---|---|---|
| 回包是 `Error`（非 JSON） | `main.py` 产线校验 | 报文前缀无效/产线不在 `unit_dict` | 修正产线标识与配置映射 |
| 回包 JSON 失败消息：数据获取失败 | `get_total_data` | 关键表空、列映射错误 | 检查 `unit_config.unit_dict` 与库表一致性 |
| 算法结果为空 | `schedule_new` / `schedule` | 粗排不可执行、主算法异常、输入过滤过严 | 先看粗排输出 CSV 和日志，再看 dynamic_rule |
| 写库被跳过（辊期冲突） | `_check_roll_no_conflict_before_store` | 三表已有相同辊期号 | 确认是否重复请求，必要时人工核对辊期推进 |
| 评分未产出 | `setting.EVALUATION` | 开关关闭或评分阶段异常 | 打开开关并检查评分模块日志 |
| ROLL 重算找不到数据 | `entrance_roll_replay` | 备份目录缺失或辊期不存在 | 校验 `backup/` 目录与辊期号匹配 |

### 2.1 快速分诊（先判哪一层出错）

- 非 JSON 且 `Error`：优先看协议层与路由层。  
- JSON 失败且含“数据获取/预处理”字样：优先看输入数据层。  
- JSON 失败且含“算法/粗排”字样：优先看算法与规则层。  
- JSON 警告且含“冲突跳过”：优先看写库与辊期冲突层。  

## 3. 粗排相关专项

当粗排结果为 0 行或不可执行：
1) 检查 `coarse_rule_schedule_result.csv` 是否落盘  
2) 检查返回 `status` / `failure_code`  
3) 检查 `coarse_rule_schedule.enforce_executable_coarse_plan`  
4) 若是邻接问题，转 `B类规则理解与邻接判定规范.md`

建议附带核查：
- 同批次 `coarse_rule_process` 目录是否存在
- 配置中 `strict_when_rule_missing` 是否改变了判定行为

## 4. SQL 与写库专项

1) 看 `SQL_FUNCTION` 与连接配置  
2) 看 `SQL_BATCH_DIR` 下本批 SQL 文件  
3) 看 `SQL_LOG_PATH` 是否有失败 SQL  
4) 确认 `id_config["辊期号"]` 推进是否与实际一致  

### 4.1 最小 SQL 证据链

至少保留三类证据：
1. 请求报文与时间戳  
2. `SQL_BATCH_DIR` 中对应批次 SQL  
3. `SQL_LOG_PATH` 中失败记录（若有）  

## 5. 排查输出模板（建议）

- 请求样例：`<原始报文>`
- 产线/辊期：`<unit>/<roll_no>`
- 触发分支：`normal/manual/statistics/roll_replay`
- 关键日志时间段：`<start-end>`
- 粗排文件：`<path>`
- SQL批次文件：`<path>`
- 结论：`<根因>`
- 处理动作：`<动作>`

## 6. 常见误判提醒

- 看到 `coarse_rule_schedule_result.csv` 存在不代表粗排可执行，需看行数与状态字段。  
- `message_type` 文案并非唯一标准，必须结合 `message_content` 与落库结果。  
- `completed_plan.exit_rate` 与 `plan_rate_kpi` 主轧出场率不是同一口径。  

## 7. 关联文档

- `06-DEBUG-CHECKLIST.md`
- `04-INTERFACE-CONTRACT.md`
- `07-database-boundary.md`
- `粗轧粗排设计说明书_实现对齐与旧版对照.md`
