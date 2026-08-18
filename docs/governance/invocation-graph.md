# Skill Invocation Graph

完整路由只见 `0-询问luohe/SKILL.md`；本图只描述依赖边。

## 内部依赖

以下为 manifest canonical dependencies，不是 slash 调用名：

```text
1-规划 ──> vocabulary/grilling
2-开发 ──> vocabulary/tdd
4-调试 ──> vocabulary/tdd
my-note/noteall ──> my-note/index-keeper + my-note/vault-publisher
```

领域建模、正式 review 和诊断循环分别内聚在 `1-规划/references/`、`3-检查/references/`、`4-调试/references/`，不再作为可发现 vocabulary。

运行时调用使用扁平 deployment name：`/grilling`、`/tdd`、`/noteall`、`/vault-publisher`、`/index-keeper`。

## 上下文边界

1. 规划会话把共识收敛为磁盘契约。
2. 每个开发切片使用 fresh context，只加载该切片契约与证据。
3. 正式 review 使用 fresh context，只接收 fixed point、spec、diff 与可选的已有验证证据。

## 调用策略

- `0--dialectic`：user-only。
- `issue-reporting`：仅在用户明确要求建单时触发；远程创建前展示完整内容并确认。
- `vocabulary/grilling` 与 `vocabulary/tdd`：`invocation: user`，仅由父工作流加载，不进入模型技能表。
