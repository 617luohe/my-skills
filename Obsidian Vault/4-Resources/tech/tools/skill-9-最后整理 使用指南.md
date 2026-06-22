---
title: "skill-9-最后整理 使用指南"
aliases: ["最后整理指南", "收尾交接指南"]
tags:
  - type/resource
  - domain/tech/tools
  - topic/skills-guide
created: 2026-06-18
status: published
confidence: sprout
source: "https://github.com/617luohe/my-skills"
skill: "9-最后整理"
---

# 9-最后整理 — 收尾与交接

> 一句话：阶段结束时做三件事——创建交接文档（让下个会话无缝继续）、同步知识（CLAUDE.md + docs/ + memory）、确认安全护栏。

## 什么时候用

| 场景 | 说明 |
|------|------|
| 完成一个功能/阶段 | 做完一个 milestone，需要整理上下文 |
| 结束一天的工作 | "今天做完了"——保存工作状态 |
| 把项目交接给别人 | 同事或另一个 agent 接手时 |
| 发现文档和代码不一致 | "这个 README 还是去年的接口" |
| 准备切换任务 | 当前项目要暂停，明天继续 |

**不适用**：中途临时离开（不需要交接文档），或者只是改了一行代码。

## 三步骤

```
步骤 1 — 会话交接
  创建 handoff-xxx.md → 引用已有产物不重复 → 建议下个会话用到的技能

步骤 2 — 知识整理
  同步三层知识：Agent Memory → CLAUDE.md → docs/ + README.md

步骤 3 — 安全确认
  检查 PreToolUse 钩子是否生效
```

## 三层知识定位

| 位置 | 受众 | 什么内容 |
|------|------|---------|
| **Agent Memory** (`memory/`) | 自己跨会话 | 个人偏好、非显而易见的事实、跨项目引用 |
| **CLAUDE.md** | 下次 AI 会话 | 项目约定、结构速查、红线、环境变量表 |
| **docs/ + README.md** | 其他人（同事/下游） | 接入指南、架构文档、运维手册、API 参考 |

> 核心原则：三层职责不重叠。CLAUDE.md 是**规则手册**，不是变更日志。
> 判断一条信息该不该进 CLAUDE.md：**下次 AI 写代码时如果没看到，会不会犯错？**

## 案例演示

### 案例 1：结束一天工作

```
用户：/9-最后整理 今天做完了，帮我收尾

Claude：luohe，开始收尾。

       === 步骤 1：会话交接 ===

       今天做的事：
       - 完成了订单取消功能（PRD → 5 个 issue 完成了前 3 个）
       - 未完成：issue #4（已支付取消退款）和 #5（取消日志）

       创建交接文档 → handoff-20260618-k3m7.md

       # Handoff: 订单取消功能开发

       ## 当前状态
       已完成 issue #1-3，issue #4-5 待做。
       相关 PRD：docs/prd/order-cancel.md

       ## 已做出的决策
       - 取消分两分支：未支付取消 vs 已支付取消（含退款）
       - 退款走异步流程（ADR-0003）

       ## 未决事项
       - issue #4 的退款超时策略：重试 3 次还是走人工？

       ## 下一步行动
       1. 继续 issue #4（已支付取消+退款）→ /4-开发
       2. 处理退款超时的决策 → /1-规划 或直接讨论
       3. 完成后 issue #5（取消日志）→ /4-开发

       ## 引用
       - PRD: docs/prd/order-cancel.md
       - ADR: docs/adr/0003-async-refund.md

       ✅ 交接文档已保存到 handoff-20260618-k3m7.md
       下次继续时先读这个文档。

       === 步骤 2：知识整理 ===

       枚举所有 .md 文件：
       - CLAUDE.md          → 需要更新（新增了 API 路由）
       - README.md           → 无需改动
       - docs/api.md         → 需要更新（新增取消接口）
       - docs/ADR/0003.md   → 已创建，无需改动

       本次变更：
       - 新增 API 路由：POST /orders/{id}/cancel
       - 新增 API 路由：GET /orders/{id}/cancel-eligibility

       → CLAUDE.md 路由表更新
       → docs/api.md 补充两个新端点

       [编辑 CLAUDE.md…]
       ✅ CLAUDE.md — 更新路由表（+2 行）
       ✅ docs/api.md — 补充取消接口文档

       尺寸检查：
       ✅ CLAUDE.md 当前 187 行（≤ 300）
       ✅ 单条 memory ≤ 100 行

       同步检查：
       ✅ 所有相对时间已转绝对日期（grep 清零）
       ✅ 所有路径/命令在代码中真实存在

       === 步骤 3：安全确认 ===

       检查 settings.json… PreToolUse 钩子已注册 ✅
       钩子脚本存在并可执行 ✅

       ── 收尾完成 ──

       ### 文档变更
       - CLAUDE.md — 新增取消接口路由
       - docs/api.md — 补充 POST /orders/{id}/cancel + GET .../cancel-eligibility

       ### 未处理
       - 无
```

### 案例 2：发现文档过期

```
用户：/9-最后整理 项目文档好像很久没更新了，帮我同步一下

Claude：luohe，先枚举所有文档检查…

       发现以下不一致：

       ❌ README.md 写的启动命令是 `python main.py`
          实际是 `uv run uvicorn src.main:app`

       ❌ CLAUDE.md 路由表缺少 /payments/refund 端点
          （代码中已实现但文档未记录）

       ❌ docs/setup.md 写的 Python 版本是 3.8
          实际 pyproject.toml 要求 ≥ 3.12

       修复以上 3 处…

       ✅ README.md — 启动命令已更正
       ✅ CLAUDE.md — 路由表已补全
       ✅ docs/setup.md — Python 版本已更新

       尺寸检查通过。无过期 memory。
```

### 案例 3：交接给别人

```
用户：/9-最后整理 这个项目要交接给另一位同事，帮我整理清楚

Claude：luohe，面向新人的交接。

       前两个步骤（交接文档 + 知识整理）按标准流程走。
       
       额外做：新人读得懂的 README。

       当前 README.md 缺少：
       - 这个项目解决什么问题（Problem Statement）
       - 本地启动的完整步骤（而非只写命令）
       - 项目目录结构说明
       - 常见问题

       补充以上内容…

       === 交接材料 ===
       1. handoff-20260618-m2n8.md — 当前状态 + 下一步行动
       2. README.md — 已补充新手引导
       3. CLAUDE.md — 同步后路由表完整
       4. docs/ — 架构文档 + API 文档已同步

       新同事上手路径：
       1. 读 README.md → 理解项目 + 本地跑起来
       2. 读 ./handoff-20260618-m2n8.md → 知道做到哪了
       3. 读 docs/architecture.md → 理解系统设计
       4. 运行 pytest → 确认所有测试通过
```

## CLAUDE.md 判断速查表

| 内容 | 进 CLAUDE.md? | 理由 |
|------|:---:|------|
| 硬边界规则、禁用事项 | ✅ | 必须遵守 |
| 命令速查 | ✅ | 频繁使用 |
| 环境变量表 | ✅ | 缺少会运行不了 |
| 最新路由表 | ✅ | 缺少会走错 |
| "2026-03-15 X 功能上线" | ❌ | 历史叙事，属于 git log |
| 单次 bug 复盘细节 | ❌ | 已有 memory 系统 |
| 测试覆盖率 85% | ❌ | 应该写进 CI/CD |
| "张三负责订单模块" | ❌ | 会过期，属于团队 Wiki |

## 注意事项

- CLAUDE.md **净增不超过 30 行**——减优于加，合并优于追加，删除优于保留
- 交接文档**不复制已有产物的内容**——引用路径或 URL 即可
- 所有相对时间（"昨天""上周""today"）必须转为绝对日期
- memory 中不能有过期事实——做过的事情、已推翻的决策直接删

## 相关技能

- [[skill-0-初始化CLAUDE 使用指南]] — CLAUDE.md 的初始化和后期同步
- [[skill-8-版本管理 使用指南]] — 最后确认 git 状态
- [[skill-5-检查 使用指南]] — 收尾前做最后一次审查
