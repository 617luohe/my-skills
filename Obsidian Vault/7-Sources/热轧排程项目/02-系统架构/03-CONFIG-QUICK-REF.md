# 配置速查（setting + config）

本文只覆盖“关键且高频改动”的配置项，避免全量键表过重。

## 1. 全局开关（`src/setting.py`）

| 键 | 当前默认 | 作用 | 常见影响 |
|---|---:|---|---|
| `MODE` | `full` | 选择配置文件中的环境段 | 影响 socket、unit、db 等全部配置读取 |
| `MODE_ehcr` | `ehcr` | EHCR 相关模式标识 | 仅 EHCR 相关路径使用 |
| `DEBUG` | `True` | 过程数据备份开关 | 影响备份目录与调试证据 |
| `PER_DATA_SAVE` | `False` | 是否保存算法前过程数据 | 排障时常临时打开 |
| `EVALUATION` | `True` | 是否执行评分计算 | 影响评分 CSV 与日志 |
| `ALGORITHM` | `False` | 是否调用主算法 | `False` 时不走 HotRolling 主链 |
| `SQL_FUNCTION` | `tidb` | DB 驱动选择 | 影响 `communication.py` 连接分支 |

## 2. 路径类配置（`setting.py`）

- `SOCKET_CONFIG_PATH`: `../config/socket_connection_config.json`
- `UNIT_CONFIG_PATH`: `../config/unit_config.json`
- `ALGORITHM_CONFIG_PATH`: `../config/config.json`
- `SQLSERVER_CONFIG_PATH`: `../config/sqlserver_config.json`
- `TIDB_CONFIG_PATH`: `../config/tidb_config.json`
- `ID_CONFIG_PATH`: `../config/id_config.json`
- `BACKUP_PATH`: `../backup`
- `BACKUP_FTP`: `../backup_ftp`

> 约定：相对路径以项目根目录为基准；服务通常在 `src` 目录启动。

## 3. 配置文件职责

| 文件 | 作用 | 谁会读 |
|---|---|---|
| `config/socket_connection_config.json` | 监听地址/端口/并发参数 | `main.py` |
| `config/unit_config.json` | 产线路由、读表/写表结构、字段映射 | `main.py`, `unit_process.py` |
| `config/config.json` | 算法与粗排参数 | `unit_process.py`, 粗排/主算法 |
| `config/config_thin.json` / `config_thick.json` | 辊期重算时按类型切换配置 | `entrance_roll_replay` |
| `config/tidb_config.json` | TiDB 连接信息 | `communication.py` |
| `config/sqlserver_config.json` | SQL Server 连接信息 | `communication.py` |
| `config/id_config.json` | 辊期号推进状态 | `unit_process.py` |
| `config/logging_config.json` | 日志目录与文件策略 | `logging_paths.py` |
| `config/table_structure_config.json` | 表结构配置（占位） | 周边工具/兼容用途 |

## 4. 关键参数族（高频）

### 4.1 `coarse_rule_schedule.*`（粗排）

来源：`config/config*.json`，由 `CoarseRuleConfig` 覆盖默认值。

高频关注：
- `enabled`
- `max_run_seconds` / `timeout_seconds`
- `hot_segment_length`
- `min_transition_length`
- `max_bridge_nodes`
- `thickness_break_width_window`
- `enforce_executable_coarse_plan`
- `strict_when_rule_missing`

### 4.2 `unit_config`（产线）

高频关注：
- `prefix`（产线前缀拼接）
- `unit_dict`（读表配置：字段名、dtype）
- `unit_storage`（写表配置：字段映射）
- `mark_methods`（标注流程）

## 5. 常见改动场景与影响面

### 场景A：切数据库（`SQL_FUNCTION`）

- 必改：`setting.SQL_FUNCTION`
- 核查：对应连接配置文件段是否完整
- 风险：连接成功但字段类型/编码差异导致后续报错

### 场景B：修改粗排门禁策略

- 必改：`coarse_rule_schedule.enforce_executable_coarse_plan`
- 核查：`coarse_rule_schedule_result.csv` 行为、`failure_code` 语义
- 风险：放开门禁后输出语义与下游预期不一致

### 场景C：新增产线或改读写表

- 必改：`unit_config.json` 的 `unit_dict` / `unit_storage`
- 核查：`main.py` 路由可达性、`unit_process.get_total_data` 字段映射
- 风险：列名/dtype 不一致引发预处理失败

## 6. 建议变更流程

1. 先改配置，不改代码  
2. 用 `06-DEBUG-CHECKLIST.md` 执行最小回归  
3. 如影响接口/口径，同步更新：
   - `04-INTERFACE-CONTRACT.md`
   - `07/08/09` 数据契约页
