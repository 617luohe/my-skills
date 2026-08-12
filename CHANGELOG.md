# Changelog

All notable changes to this skills repository will be documented in this file.

## [Unreleased]

### 2026-08-12 - 体系优化报告落地（简洁收敛）

#### Changed

- **P0-1**: 路由加载措辞统一（复杂需求先加载 + 每会话首个复杂需求强制加载）
- **P0-2**: 1-规划 adr-format 引用指向 vocabulary 真源
- **P0-3**: README「部署方法」→「分发与部署」；治理文档锚点对齐
- **P1-1**: 2-开发/tdd 委托彻底化（MUST 与子流程去重，93→~80 行）
- **P1-2**: index-keeper / vault-publisher 改 `invocation: user`
- **P1-3**: CLAUDE.md 支撑层补 0--explore
- **P1-4**: CI 增加 pytest
- **P1-5**: 0-询问luohe 探索类三线分流脚注
- **P1-6**: CLAUDE 规模表 S/M/L/XL 映射
- **P2-1**: 5-版本管理 / 6-最后整理 / 0--neat-freak 示例与清单外迁 references
- **P2-2~4**: README 首行、0-询问luohe 主流程压缩、CONTEXT 部署术语引用 README
- **P2-5**: repository_version / 全技能 version → 1.1.0

### 2026-08-12 - 体系优化批次（skills-manager 分发 + 一致性收敛）

#### Added

- **governance**: `invocation-semantic` 校验（正文 user-only 声明须与 manifest/frontmatter 一致）
- **0--dialectic**: `references/style-patterns.md`（句式示例外迁）
- **dev**: `pyproject.toml`（pytest 本地开发依赖）

#### Changed

- **P0-1**: 删除 `--check-deployments` 与宿主部署层校验（分发由 skills-manager 负责）
- **P0-2/3**: multi-worker 晋升 stable + `invocation: user` 三方对齐
- **P0-4**: 路由加载模型措辞统一（README/USAGE/0-询问luohe/CLAUDE.md）
- **P1-1**: README/USAGE 补 `0--explore` 索引
- **P1-3**: 0-询问luohe 三表合并为规模表 + 场景快速查找（129→102 行）
- **P1-5**: 6-最后整理 ↔ neat-freak 记忆交接声明
- **P2-1**: vocabulary 暴露策略定稿（优先委托，模型可调用）
- **P2-2**: 0--dialectic 瘦身（108→63 行）
- **P2-5**: 主流程 1-5 description 补中文触发同义词
- **skill_manifest**: `status: experimental` 纳入 publication 校验

#### Removed

- **validate_skills**: `_validate_deployments`、`.my-skills-managed.json` 检查、部署 hash 对账

### 2026-08-08 - 知识库技能覆盖优化批次（noteall 场景补强）

#### Added

- **noteall**: maintain.md 新增「合规审计」模式（frontmatter 全库检视与批量补齐：缺块/缺字段/标签格式/命名/非法值）
- **noteall**: maintain.md 新增「断链与孤岛修复」模式（健康检查报告升级为可执行修复：改链接/移除/占位；归 MOC/合并/排除）
- **noteall**: profiles.yaml journal 新增 `extract` 提炼管道（日记→概念笔记，双链成对 + 级联更新）
- **noteall**: curate.md 新增 Confidence 晋升规则（seed→sapling→evergreen，更新时提示确认）
- **noteall**: SKILL.md 维护模式触发词扩充（合规审计/断链与孤岛修复）
- **noteall**: SKILL.md 新增「极轻量捕获」窄例外（§一·五：工作区脏时仅提交捕获文件，跳过流水线）
- **vault-publisher**: 新增 `scripts/vault_check.py` 确定性健康检查（frontmatter/断链/孤儿/重复/INDEX 统计，支持 --json），附 `tests/test_vault_check.py`（8 用例）

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
