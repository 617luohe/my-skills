# Skills 使用说明书（索引）

> 本文件只做**导航索引**，每个技能的完整规则以其 `SKILL.md` 为唯一事实源，本文件不重复正文。
> 调用分类：仅用户调用的 skill 必须显式输入 canonical 名称；允许模型调用的 skill 可由模型按场景自动选择，也可显式调用。完整分类见 [README.md](README.md)。

---

## Vocabulary 层（可复用核心，被其他技能调用）

| 技能 | 职责 | 调用方 | 文档 |
| --- | --- | --- | --- |
| `grilling` | 询问循环（默认批量 / 用户说"逐步"时一次一问），沿决策树逐个决议 | `/1-规划` | [SKILL.md](vocabulary/grilling/SKILL.md) |
| `domain-modeling` | 维护领域术语 `CONTEXT.md`，把架构决策记为独立 ADR | `/1-规划` | [SKILL.md](vocabulary/domain-modeling/SKILL.md) |
| `tdd` | 红-绿-重构循环，pytest 驱动，按行为风险补回归测试 | `/2-开发`、`/multi-worker` | [SKILL.md](vocabulary/tdd/SKILL.md) |
| `code-review` | 双轴审查（Standards + Spec），并行子代理 | `/2-开发`、`/3-检查`、`/multi-worker` | [SKILL.md](vocabulary/code-review/SKILL.md) |
| `diagnosing-bugs` | 六阶段 bug 诊断（观测信号 → 复现 → 假设 → 验证 → 修复 + 回归 → 清理） | `/4-调试` | [SKILL.md](vocabulary/diagnosing-bugs/SKILL.md) |

---

## 独立方法论（不绑定开发阶段，跨场景通用）

| 技能 | 职责 | 触发 | 文档 |
| --- | --- | --- | --- |
| `0--dialectic` | 辩证矛盾分析六步法（调查研究 → 定性 → 矛盾分析 → 阶段划分 → 策略 → 复盘） | `/0--dialectic` | [SKILL.md](0--dialectic/SKILL.md) |
| `0--laoyoutiao` | Python 交付节奏管理（复用现有开关、逐步展示优化成果、面向甲方交付） | `/0--laoyoutiao` | [SKILL.md](0--laoyoutiao/SKILL.md) |
| `leader` | 一句话想法 → 给另一 agent 独立跑的自包含任务书（≤4000 字，五步流程） | `/leader` | [SKILL.md](leader/SKILL.md) |
| `multi-worker` | 内置多 Agent 并行开发（消费已确认 tasks.md，管理配置检查、worktree 隔离、验收） | `/multi-worker` | [SKILL.md](multi-worker/SKILL.md) |

---

## 开发流程 Skills（按阶段 0~6 组织）

| 技能 | 职责 | 触发 | 文档 |
| --- | --- | --- | --- |
| `0--claude` | 初始化/修复 CLAUDE.md（称呼规则 + Caveman + Karpathy + 工作流路由） | `/0--claude` | [SKILL.md](0--claude/SKILL.md) |
| `0--neat-freak` | 知识库洁癖审查：文档↔代码一致性、尺寸体检、记忆毕业 | `/0--neat-freak` | [SKILL.md](0--neat-freak/SKILL.md) |
| `0--tokenless` | 超压缩沟通模式（caveman / less tokens / be brief） | `/0--tokenless` | [SKILL.md](0--tokenless/SKILL.md) |
| `0-启动` | Python 项目最小初始化：项目结构 + 本地 git + uv 环境 | `/0-启动` | [SKILL.md](0-启动/SKILL.md) |
| `0-询问luohe` | **技能路由器**（唯一事实源：主流程 / 上游 / 支撑层 / 快速判断） | 强制网关，每请求先加载 | [SKILL.md](0-询问luohe/SKILL.md) |
| `1-规划` | 方案追问 → 领域建模 → 接口设计 → PRD → 任务拆解 | `/1-规划` | [SKILL.md](1-规划/SKILL.md) |
| `2-开发` | TDD 红-绿-重构实现，pytest 驱动 | `/2-开发` | [SKILL.md](2-开发/SKILL.md) |
| `3-检查` | 代码审查与验收（Review / 只建单 / 架构评估自动路由） | `/3-检查` | [SKILL.md](3-检查/SKILL.md) |
| `4-调试` | 结构化调试（复现 → 假设 → 验证 → 修复 + 回归） | `/4-调试` | [SKILL.md](4-调试/SKILL.md) |
| `5-版本管理` | Git 版本控制（init/save/log/rollback/branch/remote/push） | `/5-版本管理` | [SKILL.md](5-版本管理/SKILL.md) |
| `6-最后整理` | 会话收尾沉淀：修改总结 + 经验入 memory + 结构整理 + 交接 | `/6-最后整理` | [SKILL.md](6-最后整理/SKILL.md) |
| `cleanup` | 磁盘/存储空间清理（自动识别 OS，生成 HTML 报告） | `/cleanup` | [SKILL.md](cleanup/SKILL.md) |
| `cleanupclaude` | `~/.claude` 本地状态梳理（会话/历史/缓存膨胀治理，可回滚） | `/cleanupclaude` | [SKILL.md](cleanupclaude/SKILL.md) |

---

## My-Note 层（知识管理）

| 技能 | 职责 | 触发 | 文档 |
| --- | --- | --- | --- |
| `noteall` | 固定知识库唯一入口，编排 Intake → Curate → Publish 三阶段流水线 | `/my-note/noteall` | [SKILL.md](my-note/noteall/SKILL.md) |
| `vault-publisher` | 固定 Vault 受控发布 Worker（校验 → 同步 → 只暂存 owned paths → commit/push） | 被 `noteall` 调度 | [SKILL.md](my-note/vault-publisher/SKILL.md) |
| `index-keeper` | 索引维护 Worker（增量更新 `_INDEX.md`、缺失补全、健康检查） | 被 `noteall` 调度 | [SKILL.md](my-note/index-keeper/SKILL.md) |

---

> 说明：以上为分层索引。各技能详细规则、对话示例与 MUST 规则见对应 `SKILL.md`，不再于本文件重复。
