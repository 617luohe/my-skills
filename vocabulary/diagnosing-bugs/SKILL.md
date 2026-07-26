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

#### 2.1 非确定性 Bug 处理

对于**偶发性、时序相关、并发竞态**等非确定性 bug，需要特殊策略。

**统计复现率**：
```bash
# 运行 100 次，统计失败率
for i in {1..100}; do
    pytest tests/test_flaky.py -q && echo "PASS" || echo "FAIL"
done | sort | uniq -c

# 输出示例：
#  73 PASS
#  27 FAIL  # 复现率 27%
```

**pytest-repeat 工具**：
```bash
# 安装
pip install pytest-repeat

# 重复运行 100 次，第一次失败即停止
pytest tests/test_flaky.py --count=100 -x

# 统计模式（显示失败率）
pytest tests/test_flaky.py --count=100 --count-report
```

**并发竞态检测**：
```bash
# Go: race detector
go test -race ./...

# C/C++: ThreadSanitizer
clang -fsanitize=thread -g program.c
./a.out

# Python: 并发压测
pytest tests/test_concurrent.py -n 8 --count=50  # 8 个进程，每个跑 50 次
```

**日志采样指引**：
对于高频操作，用采样避免日志淹没：
```python
import random

# 1% 采样率
if random.random() < 0.01:
    logger.debug(f"[SAMPLE] request_id={req_id}, state={state}")

# 或：每 100 次记录一次
if counter % 100 == 0:
    logger.debug(f"[SAMPLE-{counter}] processed {counter} requests")
```

**退出门禁**：
- 复现率 > 50%，或
- 有工具能稳定触发（如 race detector 报告），或
- 采样日志捕获到异常模式

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

**非确定性 Bug 假设**：
- 时序问题（异步回调顺序）
- 竞态条件（共享状态无锁保护）
- 环境差异（时区、locale、随机种子）
- 资源竞争（连接池、文件句柄耗尽）

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
- **清除调试标签** — 如果插桩时用了 `[DEBUG-xxxx]` 标记，用 grep 清除：
  ```bash
  # 查找所有调试标签
  grep -rn "\[DEBUG-" . --include="*.py" --include="*.js" --include="*.go"
  
  # 清除（手动确认后删除对应行）
  ```
- 提交修复 + 回归测试

**退出门禁**：代码库无临时调试代码，回归测试已提交。

---

## MUST 规则

1. **不构建反馈回路不假设。** 先有可重复的失败信号，再做假设。
2. **不验证假设不修复。** 用工具验证，不靠猜。
3. **修复必带回归测试。** 防止问题再次出现。
4. **最小改动。** 只修复根因，不顺手重构。

## 何时使用

- Bug 难复现、偶发
- 性能突然下降
- 回归：之前正常，现在失败
- 多次尝试修复仍未解决

## 工具速查

### Python（主要语言）

| 场景 | 工具 | 用法 |
|------|------|------|
| 检查变量值 | `breakpoint()` | 交互式调试 |
| 追踪执行路径 | `logging.debug()` | 插桩日志 |
| CPU 性能瓶颈 | `cProfile`, `py-spy` | `python -m cProfile script.py` |
| 内存泄漏 | `tracemalloc` | 追踪内存分配 |
| 测试覆盖率 | `pytest --cov` | 查看未覆盖代码路径 |
| 非确定性 bug | `pytest-repeat` | `pytest --count=100 -x` |
| 并发压测 | `pytest-xdist` | `pytest -n 8 --count=50` |

### JavaScript/TypeScript

| 场景 | 工具 | 用法 |
|------|------|------|
| 检查变量值 | `debugger` | 断点调试 |
| 追踪执行路径 | `console.debug()` | 插桩日志 |
| CPU 性能瓶颈 | `node --prof`, `clinic.js` | `node --prof app.js` |
| 内存泄漏 | Chrome DevTools, `heapdump` | 堆快照分析 |
| 测试覆盖率 | `jest --coverage`, `c8` | 查看未覆盖代码路径 |

### Go

| 场景 | 工具 | 用法 |
|------|------|------|
| 检查变量值 | `delve` | `dlv debug` |
| 追踪执行路径 | `log.Printf()` | 插桩日志 |
| CPU 性能瓶颈 | `pprof` | `go test -cpuprofile=cpu.prof` |
| 内存泄漏 | `pprof` | `go test -memprofile=mem.prof` |
| 竞态检测 | `go test -race` | 检测数据竞争 |

### C/C++

| 场景 | 工具 | 用法 |
|------|------|------|
| 检查变量值 | `gdb`, `lldb` | `gdb ./program` |
| 内存泄漏 | `valgrind` | `valgrind --leak-check=full ./program` |
| 竞态检测 | ThreadSanitizer | `clang -fsanitize=thread` |
| 未定义行为 | UBSan | `clang -fsanitize=undefined` |

### Rust

| 场景 | 工具 | 用法 |
|------|------|------|
| 检查变量值 | `lldb`, `rust-gdb` | `rust-gdb ./target/debug/app` |
| 追踪执行路径 | `dbg!()` | 插桩宏 |
| CPU 性能瓶颈 | `cargo flamegraph` | 生成火焰图 |
| 测试覆盖率 | `cargo tarpaulin` | `cargo tarpaulin --out Html` |
