---
name: tdd
layer: vocabulary
description: Test-driven development with red-green-refactor loop using pytest. Use when building Python features or fixing bugs one vertical slice at a time.
disable-model-invocation: false
---

# TDD — 测试驱动开发

红-绿-重构循环，pytest 驱动，先写失败测试再写实现。

## 核心理念

测试应该**通过公共接口验证行为**，而不是验证实现细节。代码可以完全重写，测试不应该变。
优先写集成风格测试：走真实调用路径，验证用户可感知行为。

## 反模式：水平切片

```
错误（水平）:
  RED:   test1, test2, test3, test4, test5
  GREEN: impl1, impl2, impl3, impl4, impl5

正确（垂直）:
  RED→GREEN: test1→impl1
  RED→GREEN: test2→impl2
  RED→GREEN: test3→impl3
```

## TDD 循环

### 1. 规划

- 读术语与决策上下文（`CONTEXT.md` / ADR）
- 确认接口设计
- 列出要测试的行为（不是实现步骤）

**测试策略（按行为风险，而非任务规模或代码行数）**：

- 行为变化默认新增自动化回归测试；按用户可感知行为、边界和失败模式确定覆盖范围。
- 纯文档、格式或机械生成物可不新增测试；或能明确证明现有公共接口测试已覆盖该行为时可不新增测试。两种例外都必须记录验证证据（执行的检查、已有测试及其覆盖理由）。
- 无法测试时，必须说明 seam 缺失和风险，以及为何无法建立自动化验证；不能静默以手动验证替代。
- 保留垂直切片：一次选择一个高风险行为完成 RED→GREEN，再继续下一个；测试通过公共接口验证行为，不验证实现细节。

### 2. 示踪弹

写一个测试确认一件事 → 最少代码让它通过，证明路径可行。

### 3. 递增循环

对每个剩余行为：

- **RED**: 写下个测试 → 确认失败
- **GREEN**: 最少代码让它通过
- 一次一个测试，不提前写下一个，不超前实现

### 4. 重构（全绿后）

检查：

- 提取重复逻辑
- 浅模块深化（合并小接口、隐藏实现细节）
- 删除投机代码
- 每次重构后运行测试确认仍然全绿

## 编码准则

遵循项目 CLAUDE.md 的 **Karpathy 编码准则**（先想后写 / 简洁优先 / 外科手术式改动 / 目标驱动），此处不重复。本技能只补充 TDD 特有的纪律，见下方 MUST 规则。

## MUST 规则

1. **绝不在 RED 时重构。** 全部变绿后才检查提取重复/加深模块。
2. **测试通过公共接口验证行为，不验证实现细节。**
3. **一次一个测试。** 写一个测试 → 让它通过 → 再写下一个。
4. **最少代码通过测试。** 不提前实现未测试的功能。

## 测试原则

### 好的测试

- 通过公共接口验证行为
- 测试用户可感知的结果
- 独立、可重复、快速
- 失败时明确告诉你哪里出错

### 坏的测试

- 验证私有方法
- 验证实现细节（如"调用了 3 次 X 方法"）
- 测试之间有依赖
- 需要复杂的 setup/teardown

## 示例

**好的测试**：

```python
def test_user_can_login_with_valid_credentials():
    response = client.post('/login', json={
        'email': 'user@example.com',
        'password': 'password123'
    })
    assert response.status_code == 200
    assert 'token' in response.json()
```

**坏的测试**：

```python
def test_login_calls_validate_password():
    with patch('auth.validate_password') as mock:
        login('user', 'pass')
        assert mock.called  # 测试实现细节
```
