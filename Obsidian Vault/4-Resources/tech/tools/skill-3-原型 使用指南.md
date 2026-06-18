---
title: "skill-3-原型 使用指南"
aliases: ["原型技能指南", "快速原型指南"]
tags:
  - type/resource
  - domain/tech/tools
  - topic/skills-guide
created: 2026-06-18
status: published
confidence: sprout
source: "https://github.com/617luohe/my-skills"
skill: "3-原型"
---

# 3-原型 — 快速原型验证

> 一句话：用一次性代码回答一个设计问题。不确定的决策先试错再进入正式开发。

## 什么时候用

| 场景 | 说明 |
|------|------|
| 状态机设计不确定 | "PAID→REFUNDING→REFUNDED，还能退第二次吗？" |
| 数据模型感觉不对劲 | "这个嵌套结构查询起来会不会很别扭？" |
| 算法逻辑要验证 | "这个调度算法在边界情况下行为正确吗？" |
| API 设计合理性 | "这个接口签名调用方用起来方便吗？" |
| 规划完成后有不确定性 | 1-规划 走完了但有些决策还没底 |

**不适用**：你已经确定方案是对的（直接走 4-开发），或者不确定性可以通过读文档/代码解决（走 2-分析）。

## 两种原型模式

```
问题类型
  │
  ├── 逻辑/算法/状态机 ──→ 分支 A: CLI 脚本原型
  │
  └── UI/交互/布局    ──→ 分支 B: Web 原型
```

## 案例演示

### 案例 1：订单状态机验证（分支 A）

```
用户：/3-原型 帮我验证一下这个订单状态机设计：
       pending → paid → refunding → refunded
       我担心 refunded 之后还能被再次退款

Claude：luohe，先确认问题。

       正在验证：订单状态机 "refunded 之后不可再退款" 是否被正确约束。

       创建 prototype_order_state.py...

```python
# PROTOTYPE — answer a question, then delete
# 问题：订单状态机的 refunding→refunded→不可再退款 流程是否完整？

# --- 可移植逻辑模块（可 lift 到正式代码） ---
from enum import Enum, auto

class OrderState(Enum):
    PENDING = auto()
    PAID = auto()
    REFUNDING = auto()
    REFUNDED = auto()

class OrderStateMachine:
    """订单状态机 — 可在正式代码中复用"""
    
    def __init__(self):
        self.state = OrderState.PENDING
    
    def pay(self):
        if self.state == OrderState.PENDING:
            self.state = OrderState.PAID
        else:
            raise ValueError(f"无法支付：当前状态 {self.state}")
    
    def refund(self):
        if self.state == OrderState.PAID:
            self.state = OrderState.REFUNDING
        else:
            raise ValueError(f"无法退款：当前状态 {self.state}")
    
    def complete_refund(self):
        if self.state == OrderState.REFUNDING:
            self.state = OrderState.REFUNDED
        else:
            raise ValueError(f"无法完成退款：当前状态 {self.state}")

# --- 一次性 TUI 外壳 ---
import sys

def render(machine):
    print(f"当前状态: {machine.state.name}")
    print("可用操作:")
    if machine.state == OrderState.PENDING:
        print("  输入 'pay' → 支付")
    elif machine.state == OrderState.PAID:
        print("  输入 'refund' → 退款")
    elif machine.state == OrderState.REFUNDING:
        print("  输入 'complete' → 完成退款")
    print("  输入 'quit' → 退出")

if __name__ == "__main__":
    sm = OrderStateMachine()
    render(sm)
    while True:
        cmd = input("> ").strip()
        if cmd == "quit":
            break
        try:
            if cmd == "pay": sm.pay()
            elif cmd == "refund": sm.refund()
            elif cmd == "complete": sm.complete_refund()
            else: print(f"未知操作: {cmd}")
            render(sm)
        except ValueError as e:
            print(f"错误: {e}")
```

Claude：运行 `python prototype_order_state.py`：

       当前状态: PENDING
       可用操作: 输入 'pay' → 支付
       > pay
       当前状态: PAID
       可用操作: 输入 'refund' → 退款
       > refund
       当前状态: REFUNDING
       可用操作: 输入 'complete' → 完成退款
       > complete
       当前状态: REFUNDED
       > refund                          ← 尝试再次退款
       错误: 无法退款：当前状态 REFUNDED   ← 被正确拒绝！
       
       ✅ 验证通过：refunded 状态不可再次退款。
       
       状态机设计完整。可移植逻辑模块（OrderStateMachine）可 lift 到正式代码。
       原型文件 prototype_order_state.py 验证完成后可删除。
```

### 案例 2：缓存策略正确性验证

```
用户：/3-原型 我的缓存失效策略是"写操作清空相关缓存"，
       担心并发下会有竞态——一个请求在读旧缓存，另一个在写新数据

Claude：luohe，这个问题用原型验证很合适——逻辑在纸上说不清。

       正在验证：读写并发场景下的缓存一致性。

```python
# PROTOTYPE — answer a question, then delete
# 问题：缓存失效与数据库写入的并发竞态是否有风险？

import threading
import time
from dataclasses import dataclass

@dataclass
class CacheEntry:
    key: str
    value: str
    version: int

# --- 可移植逻辑：Cache-Aside 模式 ---
class CacheStore:
    """模拟 Cache-Aside 模式的缓存层"""
    def __init__(self):
        self._store = {}
        self._lock = threading.Lock()
        self.stale_reads = 0
    
    def get(self, key):
        with self._lock:
            entry = self._store.get(key)
            return entry.value if entry else None
    
    def set(self, key, value, version):
        with self._lock:
            self._store[key] = CacheEntry(key, value, version)
    
    def invalidate(self, key):
        with self._lock:
            self._store.pop(key, None)

class Database:
    def __init__(self):
        self._data = {"order:1": "v1"}
        self._version = {"order:1": 1}
        self._lock = threading.Lock()
    
    def read(self, key):
        with self._lock:
            time.sleep(0.001)  # 模拟 DB 延迟
            return self._data.get(key), self._version.get(key)
    
    def write(self, key, value):
        with self._lock:
            self._version[key] = self._version.get(key, 0) + 1
            self._data[key] = value
            return self._version[key]

# --- 一次性测试 harness ---
def simulate_concurrent():
    db = Database()
    cache = CacheStore()
    errors = []
    
    def reader():
        # 模拟 cache-aside: 先读缓存，miss 则读 DB 并回填
        val = cache.get("order:1")
        if val is None:
            val, ver = db.read("order:1")
            cache.set("order:1", val, ver)
            time.sleep(0.002)  # 读-回填之间的窗口
        return val
    
    def writer():
        time.sleep(0.001)  # 让 reader 先开始
        new_ver = db.write("order:1", "v2")
        cache.invalidate("order:1")
        return new_ver
    
    threads = []
    results = []
    
    for _ in range(100):
        t1 = threading.Thread(target=lambda: results.append(reader()))
        t2 = threading.Thread(target=writer)
        t1.start(); threads.append(t1)
        t2.start(); threads.append(t2)
    
    for t in threads:
        t.join()
    
    # 检查：有没有 reader 读到了旧版本但缓存已经失效？
    stale = sum(1 for r in results if r == "v1")
    print(f"并发测试 100 次：旧值读到 {stale} 次")
    # 预期：可能有，因为缓存失效和 DB 写入不是原子的

if __name__ == "__main__":
    simulate_concurrent()
```

Claude：运行结果：

       并发测试 100 次：旧值读到 3 次

       ⚠️ 验证发现：确实存在竞态。3% 的 reader 在缓存失效后、DB 写入前读到了旧值。
       
       这不是 Cache-Aside 能彻底解决的。三种修复方向：
       A) 接受短暂不一致（最终一致性）— 3% 的概率，窗口 < 2ms
       B) 写时加分布式锁 — 增加复杂度
       C) 用版本号校验 — 读 DB 后检查缓存版本
       
       你倾向哪个？这个结论可以记录到 ADR。
```

### 案例 3：跳过原型——不需要的时候

```
用户：/3-原型 帮我验证一个简单的计算器 add 方法

Claude：luohe，add(a, b) 的逻辑是确定的——不需要原型验证。
       直接走 4-开发，用 TDD 实现即可。

       要我帮你切到 4-开发 吗？
```

## 五个铁律

1. **标记为一次性代码** — 文件头部加 `# PROTOTYPE — answer a question, then delete`
2. **一条命令就能跑** — `python prototype_xxx.py`
3. **不持久化** — 状态在内存中
4. **不写测试** — 测试需要维护，原型不需要
5. **不打磨** — 不抽象、不泛化、不做错误处理

## 反模式（千万别做的）

| ❌ | 为什么 |
|----|--------|
| 给原型写测试 | 需要测试的东西已经不是原型了 |
| 连真实数据库 | 内存 store 就够，原型是验证逻辑不是验证连接 |
| 泛化设计 | "以后还要支持 X"的想法不要有 |
| 逻辑和 TUI 混在一起 | reducer 里混了 print 就不可移植了 |
| TUI 外壳合入正式代码 | 外壳是为手操优化的，不是生产代码 |

## 原型完成后

1. 确定结论（验证通过/不通过/需要调整）
2. 记录结论（ADR 或 commit message）
3. 删除原型代码（或 lift 可移植模块到正式代码）
4. 进入 4-开发

## 相关技能

- [[skill-1-规划 使用指南]] — 上游：规划完成后仍有不确定性
- [[skill-4-开发 使用指南]] — 下游：验证通过后进入 TDD 实现
