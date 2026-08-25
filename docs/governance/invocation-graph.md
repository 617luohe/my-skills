# Skill Invocation Graph

完整路由只见 `0-router/SKILL.md`；本图只描述依赖边。

## 内部依赖

以下为 manifest canonical dependencies，不是 slash 调用名：

```text
1-plan ──> vocabulary/grilling
2-implement ──> vocabulary/tdd
4-debug ──> vocabulary/tdd
my-note/noteall ──> my-note/index-keeper + my-note/vault-publisher
```

领域建模、正式 review 和诊断循环分别内聚在 `1-plan/references/`、`3-review/references/`、`4-debug/references/`，不再作为可发现 vocabulary。

运行时调用使用扁平 deployment name：`/grilling`、`/tdd`、`/noteall`、`/vault-publisher`、`/index-keeper`。

## 上下文边界

1. 规划会话把共识收敛为磁盘契约。
2. 开发切片优先使用 fresh context；宿主不支持时按 `/2-implement` 在主上下文顺序执行。
3. 正式 review 使用 fresh context，只接收 fixed point、spec、diff 与可选的已有验证证据。

## 调用策略

- `0-dialectic`：user-only。
- `issue-reporting`：仅在用户明确要求建单时触发；远程创建前展示完整内容并确认。
- `vocabulary/grilling` 与 `vocabulary/tdd`：`invocation: user`，仅由父工作流加载，不进入模型技能表。
