# mark_by_line 文档入口（5分钟）

本文是项目文档总入口。目标是让首次接手同学在 5-10 分钟内找到：
- 主流程从哪里进
- 接口怎么联调
- 配置改哪里
- 问题怎么排查

## 1. 你现在在维护什么

- 服务形态：TCP Socket 服务，收包后分支路由到排程入口。
- 主链路：`src/main.py` -> `src/entry.py` -> `src/unit_process.py`。
- 粗排核心：`src/coarse_rolling_rule_schedule.py`。
- 评分模块：`src/evaluation/`。

## 2. 按场景快速跳转

- 新同事快速上手：[`01-SCENARIO-NAV.md`](./01-SCENARIO-NAV.md) -> [`02-CALL-CHAIN.md`](./02-CALL-CHAIN.md)
- 联调接口（报文/回包）：[`04-INTERFACE-CONTRACT.md`](./04-INTERFACE-CONTRACT.md)
- 改配置（开关/JSON）：[`03-CONFIG-QUICK-REF.md`](./03-CONFIG-QUICK-REF.md)
- 看数据库边界与结果字段：[`07-database-boundary.md`](./07-database-boundary.md) + [`08-input-tables-schema.md`](./08-input-tables-schema.md) + [`09-output-tables-schema.md`](./09-output-tables-schema.md)
- 线上排障：[`05-TROUBLESHOOTING.md`](./05-TROUBLESHOOTING.md) + [`06-DEBUG-CHECKLIST.md`](./06-DEBUG-CHECKLIST.md)

## 3. 推荐阅读顺序

1. [`02-CALL-CHAIN.md`](./02-CALL-CHAIN.md)：先建立全链路心智模型  
2. [`04-INTERFACE-CONTRACT.md`](./04-INTERFACE-CONTRACT.md)：确认请求/响应契约  
3. [`03-CONFIG-QUICK-REF.md`](./03-CONFIG-QUICK-REF.md)：再看配置影响面  
4. [`07-database-boundary.md`](./07-database-boundary.md)：最后看数据输入输出边界  

## 3.1 快速执行入口

- 10分钟联调脚本：[`06-DEBUG-CHECKLIST.md`](./06-DEBUG-CHECKLIST.md) 的“10分钟最小联调脚本”
- 故障分诊入口：[`05-TROUBLESHOOTING.md`](./05-TROUBLESHOOTING.md) 的“快速分诊”

## 4. 旧文档与深度文档

- 粗排实现总览：[`粗轧粗排设计说明书_实现对齐与旧版对照.md`](./粗轧粗排设计说明书_实现对齐与旧版对照.md)
- B类邻接规范：[`B类规则理解与邻接判定规范.md`](./B类规则理解与邻接判定规范.md)
- 入库与 exit_rate 口径：[`schedule_result_storage.md`](./schedule_result_storage.md)
- 领域术语：[`UBIQUITOUS_LANGUAGE.md`](./UBIQUITOUS_LANGUAGE.md)

## 5. 文档维护约定

- 改动 `main/entry/unit_process/setting/config` 中任一关键路径时，至少同步更新对应文档页。
- 接口口径优先以本目录 `03/04/07/08/09` 为准；算法细节以上述深度文档为准。
