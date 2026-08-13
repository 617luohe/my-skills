# Changelog

All notable changes to this skills repository will be documented in this file.

## [Unreleased]

### Added

- **0--loop**：长时间自主迭代环；开场 grilling（含 mode/预算）一次确认后主环零 HITL；`min_rounds` 反早停；默认 max/min=8/3；产物 `docs/loop/`

### Changed

- **0--loop**：共识长跑定位与触发负例（vs Cursor `/loop`、Ralph）；何时用/不用决策树与市场三角；续跑示例；`completion_promise` 双安全阀；每轮必报一行进度；`slice-progress.md` 取代 `progress.md`；grilling 草拟 AC；hybrid 切换条件；触压信号与 blocker 优先级；术语表与 report 落地字段

### Changed

- **工作哲学**：三源重构（Caveman/Karpathy/Vercel）——Karpathy 四则独立保留，恢复语义完整性

## [1.3.0] - 2026-08-12

### Removed

- **multi-worker**：并行 worktree 编排；替代：主流程顺序开发或 Cursor 内置多 agent
- **leader**：外部 agent 任务书；替代：直接在对话中描述任务
- **0--explore**：预算驱动深潜探索；替代：只读调查 `docs/analysis/` 或 `/1-规划`
- **0--tokenless**：超压缩沟通；替代：CLAUDE.md「工作哲学·沟通」简洁表达

### Changed

- 路由表、USAGE、README、3-检查、0--dialectic 同步移除上述技能引用
- manifest：27 → 23 技能；repository_version → 1.3.0

## [1.2.0] - 2026-08-12

### Changed

- **README**: 去重技能表，索引统一指向 USAGE/CHANGELOG（189→~105 行）
- **5-版本管理 / 0-启动 / 0--laoyoutiao**: 命令与示例外迁 references，SKILL 瘦身
- **2-开发**: 编码准则改为纯引用 CLAUDE.md
- **manifest**: 全技能增加 `category` 字段；version → 1.2.0
- **validate_skills**: `category` 校验；`--check-claude-mirror` 可选镜像对账
- **tests**: 路由意图 eval fixture（`tests/fixtures/prompts/router/`）

## [1.1.0] - 2026-08-12

### Changed

- 路由加载措辞统一；1-规划 adr 引用修正；README「分发与部署」
- 2-开发/tdd 委托彻底化；Worker `invocation: user`
- CLAUDE 支撑层补 0--explore；CI 增加 pytest
- 0-询问luohe 探索分流；规模 S/M/L/XL 映射
- 5-版本管理 / 6-最后整理 / neat-freak 示例外迁

### Added

- `invocation-semantic` 校验；`pyproject.toml`；`status: experimental` 支持

### Removed

- `--check-deployments` 宿主部署层校验

## [1.0.0] - 2026-08-08

初始治理基线与 noteall 机制门禁批次。详见历史 commit。
