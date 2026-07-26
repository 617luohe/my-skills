---
name: code-review
layer: vocabulary
description: Two-axis review of code changes - Standards (coding standards) and Spec (specification compliance). Use before merging or after feature completion.
---

# Code Review — 代码审查

对代码变更进行双轴审查：**Standards**（编码规范）和 **Spec**（需求符合度）。

两个评估用并行子代理独立执行，避免互相污染上下文。

## 审查准备

### 1. 确定审查基点
从哪个点开始审查？main 分支、某个 commit、tag、还是当前改动？
- 统一记录：`git diff <fixed-point>...HEAD`（三点语法，基于 merge-base）
- 同时记录提交列表：`git log <fixed-point>..HEAD --oneline`
- 如果没有给 fixed-point，先问清楚再继续

### 2. 定位需求来源
按顺序查找：
- commit 消息中的 issue 引用（`#123`、`Closes #45`）→ 取对应 issue
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
```

## MUST 规则

1. **审查基点和需求来源必须先确认再开始。** 不问清楚不审查。
2. **两个子代理必须并行运行（小 diff）或串行运行（大 diff）。** Standards 和 Spec 独立，不互相污染上下文。
3. **标准审查结果和需求审查结果不合并、不排序、不重排优先级。**
