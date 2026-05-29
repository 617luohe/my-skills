# 场景导航（开发 / 联调 / 排障）

本文按高频工作场景组织，不按代码文件平铺。

## 1. 场景总表

| 场景 | 先看 | 再看 | 验证结果 |
|---|---|---|---|
| 新同事上手 | `00-START-HERE.md` | `02-CALL-CHAIN.md` | 能说清主流程与关键模块职责 |
| 定位调用链 | `02-CALL-CHAIN.md` | `src/main.py` / `src/entry.py` | 能判断一次请求走到哪个分支 |
| 联调接口 | `04-INTERFACE-CONTRACT.md` | `06-DEBUG-CHECKLIST.md` | 能构造报文并解释响应 |
| 改配置 | `03-CONFIG-QUICK-REF.md` | `config/*.json` | 能说明改动影响范围与回滚方式 |
| 看入库口径 | `09-output-tables-schema.md` | `schedule_result_storage.md` | 能区分各字段统计口径 |
| DB边界排查 | `07-database-boundary.md` | `08-input-tables-schema.md` | 能判断读写在哪一层失败 |
| 粗排/B类排查 | `粗轧粗排设计说明书_实现对齐与旧版对照.md` | `B类规则理解与邻接判定规范.md` | 能解释 not_executable 或邻接失败原因 |
| 线上故障排查 | `05-TROUBLESHOOTING.md` | `06-DEBUG-CHECKLIST.md` | 能按步骤快速定位并回收现场证据 |

## 2. 典型任务走法

### 2.1 “我要改协议”
1) 看 `04-INTERFACE-CONTRACT.md` 的请求/响应契约  
2) 对照 `src/main.py` / `src/entry.py` 实现  
3) 回归 `06-DEBUG-CHECKLIST.md` 的联调清单  

### 2.2 “我要改排程行为”
1) 看 `02-CALL-CHAIN.md` 中 `entrance` 主链  
2) 下钻 `src/unit_process.py` 的 `data_processor`/`schedule_new`/`build_and_write_all_schedule_results`  
3) 若涉及粗排邻接，继续看 `粗轧粗排设计说明书_实现对齐与旧版对照.md` 与 `B类规则理解与邻接判定规范.md`  

### 2.3 “我收到辊期冲突或写库失败”
1) 看 `05-TROUBLESHOOTING.md` 对应症状  
2) 看 `07-database-boundary.md` 的写库流程与冲突检查  
3) 用 `06-DEBUG-CHECKLIST.md` 收集证据后再处理  

## 3. 模块索引（从场景回到代码）

| 模块 | 代码路径 | 文档页 |
|---|---|---|
| 主服务与报文路由 | `src/main.py` | `02-CALL-CHAIN.md`, `04-INTERFACE-CONTRACT.md` |
| 入口与响应安全化 | `src/entry.py` | `02-CALL-CHAIN.md`, `04-INTERFACE-CONTRACT.md` |
| 编排主链 | `src/unit_process.py` | `02-CALL-CHAIN.md`, `07/08/09` |
| 数据筛选与构建 | `src/data_filter.py` | `02-CALL-CHAIN.md`, `08-input-tables-schema.md` |
| 粗轧规则排程 | `src/coarse_rolling_rule_schedule.py` | `粗轧粗排设计说明书_实现对齐与旧版对照.md` |
| 评分 | `src/evaluation/` | `02-CALL-CHAIN.md`, `PRD_计划评分模块.md` |
| 配置 | `src/setting.py`, `config/*.json` | `03-CONFIG-QUICK-REF.md` |
| DB边界 | `src/communication.py` | `07-database-boundary.md` |
