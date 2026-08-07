---
name: code-review
layer: vocabulary
description: Two-axis review of code changes - Standards (coding standards) and Spec (specification compliance). Use before merging or after feature completion.
disable-model-invocation: false
---

# Code Review — 代码审查

对代码变更进行双轴审查：**Standards**（编码规范）和 **Spec**（需求符合度）。

两个评估用并行子代理独立执行，避免互相污染上下文。

## 审查准备

### 1. 确定审查基点
从哪个点开始审查？main 分支、某个 commit、tag、还是当前改动？
- 统一记录基点：`git diff <fixed-point>...HEAD`（三点语法，基于 merge-base）；如存在未提交改动，再附加 `git diff` 和 `git diff --cached`
- 同时记录提交列表：`git log <fixed-point>..HEAD --oneline`；无提交时明确标注“无新增提交，审查未提交改动”
- **如果上游已显式提供 fixed-point**（如 `/2-开发` 传递），直接使用，跳过追问
- 如果没有给 fixed-point，先问清楚再继续

### 2. 定位需求来源
按顺序查找：
- **上游显式传递的需求来源**（如 `/2-开发` 传递的任务清单或 issue 路径）→ 优先使用
- commit 消息中的 issue 引用（`#123`、`Closes #45`）→ 仅作为上游未提供来源时的后备线索
- 传入的路径参数
- 项目中的 PRD/spec 文件
- 如果都没找到，询问需求在哪；若确认无 spec，Spec 轴标记为"无可用 spec"

### 3. 定位规范来源
收集：
- CLAUDE.md
- CONTRIBUTING.md
- CONTEXT.md / CONTEXT-MAP.md
- ADR
- linter/formatter/tsconfig 等工具配置

### 4. 识别门禁关注点
从上游 skill 提取门禁维度：

**代码质量门禁**（默认，始终检查）：
- 命名规范、类型注解、异常处理、import 组织、公共 API 文档字符串

**功能目标门禁**（按需，上游有明确目标时增加）：
- **性能指标**（如 PRD 要求"API 响应<100ms"）→ 运行性能测试或检查 benchmark 结果
- **可靠性指标**（如"复现率<1%"）→ 检查压力测试报告或重复运行测试
- **资源消耗**（如"内存<500MB"）→ 检查资源监控数据或 profiler 输出
- **覆盖率**（如"测试覆盖率>80%"）→ 检查覆盖率报告

如无法自动验证功能目标门禁 → 在审查报告中标注 `⚠️ 需手动验证：XXX 指标`

## 并行审查

**上下文管理**：
- **diff 较小**（<500 行变更）→ 并行运行两个子代理
- **diff 较大**（≥500 行变更）→ 串行运行，避免上下文超限：
  - 先运行 Standards 子代理（轻量，主要看规范）
  - Standards 完成后，再运行 Spec 子代理（重量，需理解需求）
  - 在最终汇总时标注："diff 较大，串行审查"

### Standards 子代理
读规范文件 + 读 diff，逐文件报告违反规范的地方（跳过已被工具自动强约束的事项）：
- 命名规范：snake_case 函数/变量、PascalCase 类
- 类型注解是否完整
- 异常处理是否捕获过于宽泛的 Exception
- import 组织：标准库 → 三方库 → 本地模块
- 公共 API 是否缺少文档字符串
- 是否使用 Python 惯用写法（上下文管理器、列表推导）

### Spec 子代理
读需求文档 + 读 diff，报告：
- 需求中要求但缺失或部分实现的功能
- 代码中出现但需求没要求的（范围蔓延）
- 实现方式有问题的地方

## 汇总报告

两个结果并排展示（`## Standards` + `## Spec` 标题），**不合并、不排序、不重排优先级**；只允许轻量清理表述。

末尾一行总结：每个轴各多少发现，最严重的问题是什么。

## 验收裁决

审查完成后，基于发现的问题严重程度输出 **PASS**、**PASS WITH WARNINGS** 或 **FAIL** 正式验收裁决。

### 阻断级别定义

- **❌ 阻断（Blocker）** — 必须修复才能合并：
  - Spec 轴：缺失核心功能、实现与需求严重不符、功能目标门禁未达标
  - Standards 轴：严重违反规范（如缺少类型注解、公共 API 无文档、裸露的宽泛异常捕获）
  
- **⚠️ 警告（Warning）** — 建议修复，但不阻断合并：
  - Spec 轴：部分实现、边缘场景未覆盖、范围蔓延（非核心）
  - Standards 轴：命名不规范、import 顺序混乱、缺少惯用写法
  
- **ℹ️ 建议（Suggestion）** — 可选优化：
  - 性能优化建议、代码简化建议、更好的抽象方式

### 裁决规则

1. **FAIL** — 存在至少 1 个 ❌ 阻断级别问题
   - 输出：`🚫 FAIL — 存在 {N} 个阻断问题，必须修复后才能合并`
   - 列出所有阻断问题清单

2. **PASS WITH WARNINGS** — 无阻断问题，但有 ⚠️ 警告
   - 输出：`⚠️ PASS WITH WARNINGS — {N} 个警告建议修复`
   - 列出所有警告问题清单

3. **PASS** — 无阻断、无警告（可以有建议）
   - 输出：`✅ PASS — 可以合并`

### 功能目标门禁处理

如果审查准备阶段识别出功能目标门禁（性能、可靠性、资源消耗、覆盖率等），必须在裁决前验证：

- **可自动验证** — 运行测试/benchmark，根据结果判定
- **需手动验证** — 在裁决中标注 `⚠️ 需手动验证：XXX 指标`，裁决降级为 PASS WITH WARNINGS

## 输出格式

```markdown
# Code Review Report

**审查基点**: <fixed-point>...HEAD
**提交列表**: 
- <commit1>
- <commit2>

**需求来源**: <PRD/issue 路径>
**规范来源**: CLAUDE.md, CONTRIBUTING.md, ...

---

## Standards

### 文件: path/to/file.py
- ❌ Line 42: 函数 `getUserName` 应改为 `get_user_name`（命名规范）
- ⚠️ Line 58: 捕获了过于宽泛的 `Exception`，建议捕获具体异常

### 文件: path/to/another.py
- ✅ 符合规范

---

## Spec

### 需求: "用户登录后显示欢迎消息"
- ❌ 缺失：登录成功后未返回欢迎消息
- ✅ 已实现：token 生成和返回

### 需求: "登录失败3次后锁定账户"
- ⚠️ 部分实现：计数器已加，但未实现锁定逻辑

---

## 总结

- **Standards**: 发现 3 个问题（1 个错误，2 个警告）
- **Spec**: 发现 2 个问题（1 个缺失功能，1 个部分实现）
- **最严重**: 缺失登录成功后的欢迎消息（Spec 要求）

---

## 验收裁决

🚫 **FAIL** — 存在 1 个阻断问题，必须修复后才能合并

**阻断问题清单**:
1. [Spec] 缺失登录成功后的欢迎消息（核心功能缺失）

**警告问题清单**:
1. [Standards] Line 42: 函数命名不规范
2. [Standards] Line 58: 捕获过于宽泛的异常
3. [Spec] 登录失败锁定功能部分实现
```

## MUST 规则

1. **审查基点和需求来源必须先确认再开始。** 不问清楚不审查。
2. **两个子代理必须并行运行（小 diff）或串行运行（大 diff）。** Standards 和 Spec 独立，不互相污染上下文。
3. **标准审查结果和需求审查结果不合并、不排序、不重排优先级。**
4. **必须输出验收裁决（PASS、PASS WITH WARNINGS 或 FAIL）。** 根据阻断级别问题判定，明确标注是否可合并。
5. **功能目标门禁必须验证。** 自动验证或标注需手动验证，未验证的门禁降级为警告。
