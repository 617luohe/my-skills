# Changelog

All notable changes to this skills repository will be documented in this file.

## [Unreleased]

### 2026-08-08 - 体系审视与优化批次执行

#### Added

- **P3-1**: validator 支持 `status: experimental`，允许实验性技能公开但不宣称稳定
- **P3-2**: 新增 CHANGELOG.md 轻量变更记录

#### Changed

- **P0-1**: multi-worker 状态统一为 stable，删除 frontmatter `experimental: true`
- **P0-2**: 0-询问luohe 调用模型统一为"强制网关：每次会话首个复杂需求先加载"
- **P0-3**: 测试策略单一事实源归 vocabulary/tdd，2-开发 改为引用
- **P0-4**: 1-规划 跨目录引用改为散文式调用 `/vocabulary/domain-modeling`
- **P0-5**: CONTEXT.md 同步目标统一为 README 部署链路 `~/.skills-manager/skills/`
- **P1-1**: 5-版本管理 补完成标准，删除自动推进段（路由逻辑交 6-最后整理）
- **P1-2**: 0--dialectic 六步表与散文合一，句式收敛为 6 种核心句式，补完成标准
- **P1-3**: 0--dialectic 删除"根因分析"触发词（与 4-调试 冲突），保留战略语义触发词
- **P1-4**: 6-最后整理 毕业信号检测瘦身为一句转交
- **P1-5**: multi-worker 补下游交接：completed 后提示授权 → /5-版本管理
- **P1-6**: 0-询问luohe 场景快速查找表合并，leader/multi-worker 边界判据补充
- **P1-7**: CLAUDE.md scale 命名漂移修正：拆为"中功能"/"大功能"两档
- **P1-8**: AGENTS.md 改为指向 CLAUDE.md 的指针（避免双文件同步成本）
- **P2-2**: vocabulary/domain-modeling 补完成标准
- **P2-3**: my-note/index-keeper 受保护区域标记统一说明，补充独立维护入口纪律
- **P2-5**: 0--claude ↔ 0--neat-freak 加减互斥声明（支撑层标题变体容忍）

#### Removed

- **P2-4**: vocabulary/code-review/.ruff_cache/ 未跟踪残留目录已清理

#### Fixed

- **P0-1**: multi-worker frontmatter/manifest/openai.yaml 状态冲突
- **P0-2**: 0-询问luohe USAGE/SKILL/CLAUDE 三处调用模型说法不一致
- **P0-3**: 2-开发 / vocabulary/tdd 测试策略逐字重复
- **P0-5**: CONTEXT.md:54 vs README:150 分发拓扑双说法
