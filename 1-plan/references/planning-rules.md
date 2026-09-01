# Planning Rules

本文件只保留 1-plan 编排层独有的规则；具体纪律已下沉到 vocabulary 技能，此处只留指针，不重复正文。

## Pointer（切勿在本文重复纪律）

- **frontier 询问** → `vocabulary/grilling`（canonical `vocabulary/grilling`）
- **追问入口** → `vocabulary/grill-me`
- **领域建模与 ADR 门禁** → `vocabulary/domain-modeling`
- **throwaway prototype** → `vocabulary/prototype`
- **对话转 PRD** → `vocabulary/to-spec`
- **PRD 拆任务** → `vocabulary/to-tickets`

## Document Authority（编排层专属）

- `CONTEXT.md` 只保存领域 glossary：术语、关系、避免或有歧义的词及少量场景。
- 架构决策写入 `docs/adr/NNNN-title.md`，格式以核心层 `vocabulary/domain-modeling/ADR-FORMAT.md` 为准。
- 任务状态写入 `docs/plans/` 的任务清单、issue 或 `docs/handoff/`，不写入 `CONTEXT.md`。
