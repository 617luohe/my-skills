# 联调与调试检查清单

本文给出“最小可执行”的联调检查步骤，避免遗漏基础项。

## 1. 联调前（环境）

- [ ] 在 `src` 目录启动：`python main.py`
- [ ] `setting.MODE` 与目标环境一致（通常 `full`）
- [ ] `setting.SQL_FUNCTION` 与连接配置文件一致
- [ ] `config/socket_connection_config.json` 端口可用
- [ ] `config/unit_config.json` 中目标产线键存在

## 2. 联调前（数据）

- [ ] 关键输入表有数据（至少 `inventory`、`dynamic_rule`）
- [ ] `dynamic_rule` 至少一行 `是否使用=1`
- [ ] 字段映射 `database_column_name / pandas_column_name / dtype` 无明显冲突

## 3. 请求检查（协议）

- [ ] 标准请求示例：`158020252000`
- [ ] 统计请求示例：`1580_all`
- [ ] ROLL 请求示例：`ROLL2026012201|1580`
- [ ] 回包优先检查是否为 JSON（异常才会是 `Error`）

### 3.1 建议增加的反向用例

- [ ] 非法产线示例（预期 `Error`）
- [ ] 缺失参数的 ROLL 报文（预期失败语义回包）

## 4. 过程证据采集

- [ ] 原始报文文件（`RAW_MESSAGE_DIR`）
- [ ] 粗排结果文件（`coarse_rule_schedule_result.csv`）
- [ ] SQL 批次文件（`SQL_BATCH_DIR`）
- [ ] 错误 SQL 日志（`SQL_LOG_PATH`）
- [ ] 备份目录（`backup/<辊期_时间_产线_模型>/`）

建议记录：
- [ ] 本次请求唯一标识（辊期号或模型号）
- [ ] 关键日志时间窗口（开始/结束时间）

## 5. 写库后核查

- [ ] `completed_info` 有对应辊期
- [ ] `completed_plan` 有对应辊期
- [ ] `plan_rate_kpi` 有对应辊期
- [ ] 有粗排时确认 n / n+1 双辊期写入
- [ ] `exit_rate` 字段语义符合文档口径

如果是重放/重复请求：
- [ ] 验证系统是否触发“辊期冲突跳过”而非重复写入

## 6. 常见回归点（改配置后必查）

- [ ] 报文路由是否仍可达目标分支
- [ ] 过滤后收池是否异常缩小
- [ ] 粗排是否从“可执行”变为“不可执行”
- [ ] 评分开关变更后是否产出评分 CSV

## 7. 10分钟最小联调脚本

1. 启动服务：`cd src && python main.py`。  
2. 发标准请求：`158020252000`，确认响应可解析。  
3. 发 ROLL 请求：`ROLL2026012201|1580`，确认链路可达。  
4. 检查证据：原始报文、SQL 批次、备份目录三项齐全。  
5. 若环境允许写库，核查三张结果表是否有对应辊期。  

## 8. 失败时提交信息模板

建议在问题记录中附上：
- 请求报文
- 响应全文
- 关键日志片段时间点
- 备份目录路径
- SQL 批次文件路径
- 当前配置（至少 MODE/SQL_FUNCTION/EVALUATION/ALGORITHM）

## 9. 关联文档

- `04-INTERFACE-CONTRACT.md`
- `05-TROUBLESHOOTING.md`
- `03-CONFIG-QUICK-REF.md`
- `07-database-boundary.md`
