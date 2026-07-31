# Handoff: noteall 三阶段流水线重构

## 当前状态

my-skills 的 my-note 体系重构 **T001-T006 完成并提交**：
- `f9a9db5` — noteall 精简为三阶段流水线 + vault-publisher + 8 测试
- `6038975` — validator 治理修复（13 预存在错误清零）

`scripts/validate_skills.py` 全绿（0 错误 0 警告），pytest 10 passed。两个 commit 尚未 push。

## 已做出的决策

- noteall 唯一入口，内部 Intake → Curate → Publish 三阶段 + 维护模式
- 14 个旧 skill 删除，能力吸收进 `noteall/references/`（intake/curate/maintain/publish/profiles）
- `vault-publisher` 内部 Worker：确定性脚本 `scripts/publish_vault.py` 负责 Git 收尾，授权仅限固定 Vault
- 固定 Vault 单一配置 `references/config.yaml`，校验失败即停止
- validator parity 改为以 `disable-model-invocation` 为唯一权威（支持"AI 可自动调用"意图）

## 未决事项

- **T007** 镜像同步：把 my-note 加入 sync-map，生成 ai-vibe-coding-config 仓库副本与工具镜像
- **T008** 真实 Vault 小范围验收：Vault 当前有 8 个未提交改动需先清理，再做一次真实收录验收
- 是否 push 到 GitHub（`origin` = github.com/617luohe/my-skills.git）

## 下一步行动

1. 确认推送两个 commit → `/5-版本管理`
2. 安排 T007 镜像同步 → 先 `/1-规划`
3. T008 真实 Vault 验收 → 需 luohe 先清理 Vault 未提交改动

## 引用

- PRD: [docs/plans/noteall-simplification/PRD.md](../../docs/plans/noteall-simplification/PRD.md)
- 任务: [docs/plans/noteall-simplification/tasks.md](../../docs/plans/noteall-simplification/tasks.md)
- ADR: [docs/adr/0001-fixed-vault-auto-publish.md](../../docs/adr/0001-fixed-vault-auto-publish.md)
- 上游分析: `E:\workplace\ai-vibe-coding-config\docs\analysis\my-note-simplification-handoff.md`
