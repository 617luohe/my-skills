---
name: 3-原型
description: Build throwaway prototypes to validate uncertain design decisions — data models, state machines, algorithm choices, API schemas — before committing to full TDD implementation. Use when planning reveals open questions, or before starting formal development.
---

# 3-原型 — 快速原型验证

**原型是用一次性代码回答一个设计问题。** 问题决定了原型的形式。

规划完成后（1-规划）→ 仍有不确定的决策 → 先快速原型验证 → 确认后进入正式开发（4-开发）。

## 第一步：确定问题

分析当前设计中最不确定的决策，决定原型要回答什么问题：

| 问题类型 | 原型形式 | 输出 |
|---|---|---|
| "这个数据模型/状态机感觉对吗？" | CLI 脚本 | 交互式终端程序，展示状态流转 |
| "这个算法/逻辑能跑通吗？" | CLI 脚本 | 输入样本，输出结果 |
| "这个 API 设计合理吗？" | CLI 脚本 | mock 客户端调用，展示请求/响应 |
| "这个 UI 交互方式对吗？" | Web 页面 | 多个 UI 变体（次要分支） |

**如果是 CLI 逻辑验证 → 走分支 A。如果是 UI/交互验证 → 走分支 B。** 如果两者都涉及且用户在线，先问用户聚焦哪个问题。

---

## 分支 A：逻辑/状态原型（CLI 脚本）

写一个可运行的 Python 脚本，推动状态机/数据模型通过难以在纸面上推理的路径。

### 规则

1. **标记为一次性代码** — 在文件头部加注释：
   ```python
   # PROTOTYPE — answer a question, then delete
   ```

2. **一条命令就能跑** — 脚本可直接 `python prototype_xxx.py` 运行，无需额外步骤

3. **无持久化** — 状态在内存中。持久化正是原型要验证的东西，不要依赖它

4. **跳过打磨** — 不写测试、不做错误处理（只要能跑）、不抽象。目标是快速学到东西然后删掉

5. **暴露状态** — 每次操作后打印完整状态，让用户看到发生了什么变化

6. **放到被测模块旁边** — 放在被验证模块的同级目录下，命名加上 `prototype_` 前缀，让人一眼看出这不是生产代码

### 工作流程

```
1. 理解要验证的设计决策
2. 写一个最小 CLI 原型（10-50 行 Python）
3. 运行给用户看，让用户操作/观察
4. 根据反馈决定：这个设计对吗？需要改吗？
5. 迭代原型 1-3 轮，直到问题被回答
```

### 示例

```
设计问题：订单状态机的"已支付→退款中→已退款"流程是否完整？

→ 原型：
   class OrderStateMachine:
       def __init__(self):
           self.state = "pending"
       def pay(self): ...
       def refund(self): ...
       def cancel(self): ...

→ 交互：
   State: pending
   操作: pay
   State: paid
   操作: refund
   State: refunding
   操作: complete_refund
   State: refunded
   操作: refund  ← 应该被拒绝
   Error: Cannot refund already refunded order
```

---

## 分支 B：UI/交互原型（Web）

如果问题涉及前端交互或界面布局：

- 生成 2-3 个截然不同的视觉方案
- 可在单一路由上通过参数切换
- 浮动的底部栏标识当前是哪个变体

> 注意：你的主要技术栈是 Python，UI 原型仅在你明确要求前端验证时使用。

---

## 原型完成后

**答案**是原型唯一值得保留的东西。

1. 如果用户在线：简短讨论，确定结论
2. 把结论记录到决策文档（commit message、ADR、或者就在当前对话中）
3. 删除原型代码，或者将验证通过的决策吸收到正式设计中
4. 进入 **4-开发**，用 TDD 实现正式代码

## 和上下游技能的关系

- **上游：1-规划 / 2-分析** — 规划完成后仍有不确定的设计决策
- **下游：4-开发** — 原型验证通过后，进入 TDD 正式实现
- **替代方案：** 如果设计没有不确定性，可以直接跳过原型进入 4-开发
