---
name: diagnosing-bugs
layer: vocabulary
description: Disciplined diagnosis loop for hard bugs and performance regressions - reproduce → minimize → hypothesize → instrument → fix → regression-test.
---

# Diagnosing Bugs — Bug 诊断循环

结构化调试流程，用于难复现的 bug 或性能突然下降。

## 六阶段流程

### 1. 构建反馈回路
在做任何假设之前，先建立一个**可重复的失败信号**。

**目标**：一条命令，现在运行就失败（或慢）。

**方法**：
- **Bug** — 写一个最小测试用例，当前失败
- **性能回归** — 写一个 benchmark，记录当前基线

**示例**：
```bash
# Bug 反馈回路
pytest tests/test_login.py::test_invalid_password  # 当前失败

# 性能反馈回路
pytest tests/bench_login.py --benchmark-only  # 当前 500ms（基线 100ms）
```

**退出门禁**：有一条命令，运行必现问题。

---

### 2. 复现与最小化
缩小触发条件，找到**最小复现路径**。

**方法**：
- 去掉不相关的步骤
- 简化输入数据
- 隔离单个模块

**示例**：
```python
# 原始（复杂）
user = create_user(email="test@example.com", name="Test", age=25, ...)
login(user, password="wrong")  # 失败

# 最小化后
login(user_id=1, password="wrong")  # 仍然失败
```

**退出门禁**：最小输入 + 最短路径，仍能复现。

---

### 3. 假设（3-5 条）
基于最小复现路径，列出 3-5 个可能的根因假设。

**格式**：
```
假设 1: 密码验证逻辑使用了错误的比较运算符（< 而非 <=）
假设 2: 缓存层返回了过期的用户数据
假设 3: 数据库连接池耗尽导致查询超时
假设 4: ...
```

**优先级**：
- 最近改动的代码
- 复杂度高的模块
- 已知的历史问题区域

**退出门禁**：至少 3 个具体假设，不是"可能是哪里的问题"。

---

### 4. 工具验证
逐个验证假设，使用工具而非猜测。

**Python 工具**：
- **断点调试** — `breakpoint()`，检查变量值
- **日志插桩** — 在关键路径插入 `print()` 或 `logging.debug()`
- **性能分析** — `cProfile`、`py-spy`、`tracemalloc`
- **测试覆盖率** — `pytest --cov` 查看未覆盖路径

**示例**：
```python
# 验证假设 1：密码验证逻辑
def validate_password(stored_hash, input_password):
    breakpoint()  # 检查比较逻辑
    return bcrypt.checkpw(input_password, stored_hash)
```

**退出门禁**：找到根因，或排除所有假设（回到步骤 3 补充假设）。

---

### 5. 修复 + 回归测试
修复根因，并添加回归测试防止再次出现。

**修复原则**：
- **最小改动** — 只修复根因，不顺手重构
- **保持行为** — 其他功能不受影响

**回归测试**：
```python
def test_password_validation_boundary():
    """回归测试：密码验证边界条件"""
    # 这个测试在修复前失败，修复后通过
    assert validate_password(hash, "wrong") == False
    assert validate_password(hash, "correct") == True
```

**验证**：
- 回归测试通过
- 原有测试套件全部通过
- 步骤 1 的反馈回路变绿

**退出门禁**：问题修复，回归测试覆盖根因。

---

### 6. 清理
删除调试代码，整理临时文件。

**清理项**：
- 删除 `breakpoint()`、`print()`、临时日志
- 删除临时测试文件
- 提交修复 + 回归测试

---

## MUST 规则

1. **不构建反馈回路不假设。** 先有可重复的失败信号，再做假设。
2. **不验证假设不修复。** 用工具验证，不靠猜。
3. **修复必带回归测试。** 防止问题再次出现。
4. **最小改动。** 只修复根因，不顺手重构（重构留给 `/6-优化`）。

## 何时使用

- Bug 难复现、偶发
- 性能突然下降
- 回归：之前正常，现在失败
- 多次尝试修复仍未解决

## 工具速查

| 场景 | 工具 | 用法 |
|------|------|------|
| 检查变量值 | `breakpoint()` | 交互式调试 |
| 追踪执行路径 | `logging.debug()` | 插桩日志 |
| CPU 性能瓶颈 | `cProfile`, `py-spy` | `python -m cProfile script.py` |
| 内存泄漏 | `tracemalloc` | 追踪内存分配 |
| 测试覆盖率 | `pytest --cov` | 查看未覆盖代码路径 |
