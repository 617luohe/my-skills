---
name: 9-最后整理
description: End-of-session cleanup — create handoff document, sync project docs with code, verify git safety guardrails. Use when finishing a milestone, ending a work session, or before handing off to another agent.
---

# 9-最后整理 — 收尾与交接

三件事：**交接**（为下个会话留上下文）、**知识整理**（同步文档和记忆）、**安全确认**（检查护栏）。

---

## 步骤

### 1. 会话交接

创建交接文档，让下个会话能无缝继续。

**规则**：
- 保存到临时文件，返回路径给你
- 不重复已在其他产物（PRD、commit、diff）中的内容，引用路径或 URL 即可
- 建议下个会话要用到的技能

模板：

```md
# Handoff: <会话主题>

## 当前状态
做到了哪一步、什么还没做。

## 已做出的决策
- [决策 1] — 为什么

## 未决事项
- [待定事项]

## 下一步行动
1. [行动] → 建议使用的技能

## 引用
- PRD: [路径]
- 相关文件: [路径]
```

---

### 2. 知识整理

同步项目文档和记忆，避免信息过期。

**执行顺序**：先精简（破除膨胀）→ 再做增量同步。

**检查清单**：

**尺寸检查**：
- [ ] CLAUDE.md ≤ 300 行（超标则精简：删历史叙事段，只留规则）
- [ ] 单条 memory ≤ 100 行（超标则拆分或删）

**同步检查**：
- [ ] 本次变更波及的文档已更新
- [ ] 新增 API/路由 → CLAUDE.md + 对应文档
- [ ] 新增环境变量 → CLAUDE.md
- [ ] 所有相对时间已转绝对日期
- [ ] memory 中没有过期事实

**编辑原则**：
- 减优于加 — CLAUDE.md 净增 > 30 行 = 超标
- 合并优于追加 — 新信息是对旧信息的更新，改旧条目
- 删除优于保留 — 完成的计划、推翻的决策、过期记忆直接删
- 面向读者 — 文档是写给第一次接触的人看的

---

### 3. 安全护栏确认

检查 `0-安全护栏` 是否已配置并生效。

- [ ] `settings.json` 中 PreToolUse 钩子已注册
- [ ] 钩子脚本存在并可执行

如果尚未配置，询问是否需要安装。

---

## 什么时候用

- 完成一个阶段/功能后收尾
- 结束一天的工作前
- 需要把项目交给另一个人或 agent
- 发现文档和代码不一致

## 案例

```
你：今天做完了，帮我整理一下
Claude：1. 创建交接文档 → handoff-a7k3.md
        2. 同步知识 → CLAUDE.md 精简 40 行历史叙事，新增本次 API 路由表
        3. 安全护栏 → 已配置，脚本正常

        交接文档已保存到 handoff-a7k3.md。
        明天继续时先读交接文档，然后继续开发。

        本次变更摘要：
        - CLAUDE.md — 精简 + 更新路由表
        - memory: payment-module — 更新已完成事项
        - docs/integration-guide.md — 新增 API 示例
```
