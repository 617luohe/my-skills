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
1. **构建反馈回路** — 建立可比较的观测信号
2. **复现与最小化** — 缩小触发条件
3. **假设（3-5 条）** — 列出可能的根因
4. **工具验证** — 一次只改一个变量，形成根因证据
5. **修复 + 回归测试** — 用稳定或统计可信复现验收修复
6. **清理** — 删除调试代码

## 核心原则

### 1. 先建立可比较的观测信号
**在做任何假设之前**，先建立可比较的观测信号，而非等待一条命令稳定必现。可用信号包括 trace、metrics、安全采样、请求样本、profile、内存快照：
- **稳定 Bug** — 写最小失败测试
- **低频 Bug** — 收集 trace、metrics、安全采样或脱敏请求样本，并记录时间窗、样本量和环境
- **性能回归** — 写 benchmark，或记录 profile、内存快照的当前基线

稳定或统计可信的复现用于修复验收，不是进入调查的前置条件。无法自动测试时，说明 seam 缺失和风险，不能静默用手测替代。

**示例**：
```bash
# 稳定 Bug 信号
pytest tests/test_login.py::test_invalid_password  # 当前失败

# 性能信号：profile 基线
python -m cProfile -o login.prof app.py
```

低频故障的观测清单（按项目已有工具选择，不展示虚构可执行命令）：
- 按请求 ID 导出或查询关联 trace；记录 trace 来源和时间窗。
- 查询现有监控中的错误率、延迟等 metrics；记录指标名、筛选条件和时间窗。
- 需要时启用受控安全采样或保存脱敏请求样本，并记录样本量和环境。

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
只修复根因，不顺手重构。

## MUST 规则

1. **不建立可比较的观测信号不假设。** 稳定或统计可信的复现用于修复验收，不是进入调查的前置条件。
2. **不验证假设不修复。** 用工具形成根因证据，不靠猜；一次只改一个变量。
3. **修复必带回归测试。** 无法自动测试时说明 seam 缺失和风险，不能静默用手测替代。
4. **最小改动。** 只修复根因，不顺手重构。
5. **展示先脱敏。** 命令、输出与捕获物中的密钥一律写 `<REDACTED>`；凭据留在环境变量，不用明文展示。

## 详细流程

完整的六阶段流程、工具使用指南、非确定性 bug 处理见：
- `/vocabulary/diagnosing-bugs/SKILL.md` — 详细的六阶段流程

## 与其他技能的关系

- **输入** — Bug 现象描述、错误日志、性能指标
- **调用** — `/vocabulary/diagnosing-bugs`（核心诊断循环）
- **输出** — 修复代码 + 回归测试 → `/5-版本管理`（可选提交）
- **后续** — 如果发现架构问题（缺少测试接缝），需在后续迭代中重构
