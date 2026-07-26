---
name: 2-开发
description: Implement features and bug fixes with a pytest-driven red-green-refactor loop and coding guardrails. Use when the user asks to develop, implement, code, or test-drive a change, especially after a plan or validated prototype exists.
disable-model-invocation: false
---

# 2-开发 — TDD 编码实现

使用 `/vocabulary/tdd` 技能进行红-绿-重构循环开发。

## 编码准则（贯穿全程）

### 1. 先想后写
编码之前说出你的假设、列出多种解读、如果有更简单的方案就说出来。

### 2. 简单第一
最少代码解决问题。没有要求的功能不加，只用一次的逻辑不抽象，没人要求的灵活性不做。

### 3. 手术刀式改动
只碰必须碰的，只清理自己制造的垃圾，不顺手改进旁边的代码。

### 4. 目标驱动执行
把模糊任务转成可验证的目标。多步骤时给出简短计划和验证项。

## 开发流程

### 1. 理解任务
- 从任务清单（`/1-规划` 产出）或 issue 中提取：
  - 要实现的功能切片
  - 验收标准
  - AFK/HITL 标记
  - 前置依赖
- 如果标记为 `[HITL]`，执行到需要用户决策的点时暂停并询问

### 2. TDD 开发
使用 `/vocabulary/tdd` 技能：
- **规划** — 读 CONTEXT.md/ADR，确认接口，列出要测试的行为
- **示踪弹** — 写一个测试确认路径可行
- **递增循环** — RED→GREEN，一次一个测试
- **重构** — 全绿后提取重复、深化浅模块

**测试策略**：
- **简单任务**（<50行）→ 至少 1 个关键路径测试
- **中大任务**（新功能、重构）→ 3-5 个核心行为测试，聚焦复杂逻辑和边界

### 3. 验证
- 运行完整测试套件：`pytest`
- 运行类型检查：`mypy` 或 `pyright`（如果项目有配置）
- 运行 linter：`ruff` 或 `flake8`（如果项目有配置）
- 所有检查通过后进入下一步

### 4. 代码审查
开发完成后，自动调用 `/vocabulary/code-review`：
- **审查基点** — 通常是当前分支相对 main 的变更
- **Standards 审查** — 编码规范
- **Spec 审查** — 需求符合度
- 如果发现问题，修复后重新验证

### 5. 提交
审查通过后，提交代码：
```bash
git add <changed-files>
git commit -m "feat: <简短描述>"
```

commit 消息格式：
- `feat:` — 新功能
- `fix:` — Bug 修复
- `refactor:` — 重构
- `test:` — 测试相关
- `docs:` — 文档更新

## MUST 规则

1. **先想后写。** 编码前说出假设，不确定就问。
2. **简单第一。** 最少代码解决问题，不做投机功能。
3. **手术刀式改动。** 只碰必须碰的，不顺手改旁边的。
4. **目标驱动。** 模糊任务转可验证目标，多步骤先列计划。
5. **绝不在 RED 时重构。** 全部变绿后才检查提取重复/加深模块。
6. **测试通过公共接口验证行为，不验证实现细节。**
7. **遇 HITL 任务时暂停决策。** 展示当前进度和待决策项，等待用户输入后继续。
8. **开发完成后必须运行代码审查。** 不跳过审查直接提交。

## 何时使用

- `/1-规划` 产出任务清单后，逐个任务执行
- 用户明确要求"开发"、"实现"、"TDD"
- 方案已明确，直接进入编码阶段

## 与其他技能的关系

- **输入** — `/1-规划` 产出的任务清单、PRD、CONTEXT.md
- **调用** — `/vocabulary/tdd`（核心循环）→ `/vocabulary/code-review`（质量门禁）
- **输出** — 通过测试的代码 + 审查报告 → `/8-版本管理`（可选提交）
