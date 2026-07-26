---
name: 4-调试
description: Diagnose bugs and performance regressions through reproduce → hypothesize → instrument → fix → regression test. Use when errors, crashes, intermittent failures, unexplained behavior, or performance problems need systematic investigation.
disable-model-invocation: false
---

# 4-调试 — 结构化调试

使用 `/vocabulary/diagnosing-bugs` 技能进行六阶段调试流程。

## 何时使用

- Bug 难复现、偶发
- 性能突然下降
- 回归：之前正常，现在失败
- 多次尝试修复仍未解决

## 快速调用

```
luohe，订单支付接口偶尔返回 500，帮我调试
```

会自动执行六阶段流程：
1. **构建反馈回路** — 建立可重复的失败信号
2. **复现与最小化** — 缩小触发条件
3. **假设（3-5 条）** — 列出可能的根因
4. **工具验证** — 逐个验证假设
5. **修复 + 回归测试** — 修复根因并添加回归测试
6. **清理** — 删除调试代码

## 核心原则

### 1. 先构建反馈回路
**在做任何假设之前**，先建立一个可重复的失败信号：
- **Bug** — 写一个最小测试用例，当前失败
- **性能回归** — 写一个 benchmark，记录当前基线

**示例**：
```bash
# Bug 反馈回路
pytest tests/test_login.py::test_invalid_password  # 当前失败

# 性能反馈回路
pytest tests/bench_login.py --benchmark-only  # 当前 500ms（基线 100ms）
```

### 2. 用工具验证，不靠猜
列出 3-5 个假设后，逐个用工具验证：
- `breakpoint()` — 检查变量值
- `logging.debug()` — 追踪执行路径
- `cProfile`, `py-spy` — CPU 性能瓶颈
- `tracemalloc` — 内存泄漏
- `pytest --cov` — 测试覆盖率

### 3. 修复必带回归测试
防止问题再次出现：
```python
def test_password_validation_boundary():
    """回归测试：密码验证边界条件"""
    # 这个测试在修复前失败，修复后通过
    assert validate_password(hash, "wrong") == False
    assert validate_password(hash, "correct") == True
```

### 4. 最小改动
只修复根因，不顺手重构（重构留给 `/6-优化`）。

## MUST 规则

1. **不构建反馈回路不假设。** 先有可重复的失败信号，再做假设。
2. **假设阶段至少列 3 条可证伪假设。** 不能只有一条（锚定偏见）。
3. **一次只改一个变量验证。** 不并行修改。
4. **所有调试标签用唯一 ID 标记。** 格式 `[DEBUG-xxxx]`，最后 grep 清除。
5. **修复必带回归测试。** 防止问题再次出现。

## 详细流程

完整的六阶段流程、工具使用指南、非确定性 bug 处理见：
- `/vocabulary/diagnosing-bugs/SKILL.md` — 详细的六阶段流程

## 与其他技能的关系

- **输入** — Bug 现象描述、错误日志、性能指标
- **调用** — `/vocabulary/diagnosing-bugs`（核心诊断循环）
- **输出** — 修复代码 + 回归测试 → `/8-版本管理`（可选提交）
- **后续** — 如果发现架构问题（缺少测试接缝），移交给 `/6-优化`
