---
name: 0--laoyoutiao
description: >
  Python 项目交付节奏管理（面向甲方交付）：复用现有开关、逐步展示优化成果。
  触发：交付、优化成果展示、交付节奏、老油条、面向甲方。
disable-model-invocation: false
---

# 老油条 — Python 交付节奏管理

复用项目现有开关控制交付节奏；无现成机制时用 `branch_config.json`（见 [default-adapter.md](references/default-adapter.md)）。

## 核心原则

1. **现有框架优先** — 不引入第二套配置
2. **单一事实来源** — 冲突时停止写盘
3. **一条推荐** — 默认直接给最优建议
4. **统一写入门禁** — 预览配置+说明+历史，确认后写入并校验
5. **收益有依据** — 测试/基准/文档/提交记录；无则标「待验证」
6. **甲方语言** — 不暴露实现细节
7. **保持简洁** — 终端输出 ≤20 行
8. **不自动提交** — 除非用户明确要求

## 探查与适配

读 `CLAUDE.md`、`README*`、`docs/`、部署文档 → 搜 flag/配置/环境变量 → 沿入口确认影响。

**适配契约**：当前状态、候选状态、变更方法、校验方法、收益来源。无框架时用 [default-adapter.md](references/default-adapter.md)。

## 统一执行流程

读取 → 计算候选 → 推荐 2-4 项 → 完整预览 → 确认 → 写入 → 校验 → 结果。

意图路由与异常见 [references/routes.md](references/routes.md)。说明模板见 [delivery-note-template.md](references/delivery-note-template.md)。

## 完成检查

- 唯一有效配置来源；写入已预览确认；收益有依据；校验已跑；甲方语言
