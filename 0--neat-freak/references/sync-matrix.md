# 变更影响矩阵

遇到不确定"这次改动要同步哪些文件"时查这张表。**两个方向都要查**：补漏（加到哪些文件）+ 防膨胀（应该从哪些文件删）。

## 反向：哪些信息该从 CLAUDE.md / 记忆里删除

CLAUDE.md / AGENTS.md 不是变更日志。下面这些反模式发现了就删 / 迁：

| 反模式 | 处理 |
|---|---|
| "X 时刻起 Y 功能上线，详见 docs/Z.md" 形式的 blockquote | 删除——指针角色已经被「深入文档」指针表占掉，叙事归 git log / `/changelog` / `docs/CHANGES.md` |
| 在 CLAUDE.md 里抄 docs/ 已有的详细机制 / 数据流 / 评分公式 | 删除——AI 改到这块自然会读 docs，CLAUDE.md 只留"边界规则" |
| 已经稳定 ≥ 7 天的"新功能上线"叙事 | 该融入项目概览的融入；纯历史的删 |
| 一次性事故的复盘细节（"X 时 Y 服务挂了 30min 因为 Z"） | 留 1 行红线规则（"不要再裸跑 systemctl stop X"），事故详情归 docs/PLAYBOOK.md 或删 |
| 已被新版本取代的"中间态"叙事（"5/6 改了 X，5/8 又改成 Y"） | 只留最终态规则；中间历史删 |
| 单条 memory > 100 行 + 全是事故复盘 | 提炼成一条 ≤ 30 行的"规则 + Why + How to apply"；多余的删 |
| 记忆条目里"已被 X 取代" / "已废弃" / "保留作历史" 字样 | 99% 真的可以删，docs 已经是权威 |

判断标准：**这条信息在下次 AI 写代码时如果没看到，会犯错吗？** 不会就删 / 迁。

## 代码层变更 → 文档层变更

| 本次对话发生的事 | 要改的文件(按受众) |
|---|---|
| 新增 API / 路由 | `CLAUDE.md`（仅当 AI 需要路由红线）· README（用户入口变化时）· `docs/integration-guide.md` API 速查表 · `docs/architecture.md` Routes 小节 |
| 新增 / 改名 环境变量 | `CLAUDE.md`（仅放配置红线）· `docs/operator-runbook.md` 环境变量章节 · `docs/integration-guide.md`（下游要配置时） |
| 新增数据库表 / 列 | `CLAUDE.md`（仅放操作红线）· `docs/architecture.md` Data Model |
| 新增 / 改动用户流程 | README 相关命令行示例 · `docs/integration-guide.md`（外部用法变化时）· `docs/handoff.md`（确有交接需求时） |
| 新增大特性（能跨多文件） | 按实际影响更新 integration guide、architecture、runbook；确有交接需求时再更新 handoff |
| 新增术语 / 改命名 | `docs/integration-guide.md` 术语表(如果有)+ 全局搜索旧术语替换 |
| 部署参数 / 基础设施变化 | `docs/operator-runbook.md` · `CLAUDE.md`（仅配置红线）· README（用户部署步骤变化时） |
| 下游项目接入方式变化 | 下游项目的 `docs/<integration>.md` · 上游项目的 `integration-guide.md` |

## 记忆层变更

| 情况 | 处理方式 |
|---|---|
| 过期事实 | 改记忆文件,同时更新索引(如 MEMORY.md)的 description |
| 相对日期事实 | 转成绝对日期（如 `2026-04-29`）；检测规则和用户话术示例可保留相对日期词 |
| 重复记录(多条说同一件事) | 合并为一条,改索引 |
| 已完成的待办 | 删除——知识库不是历史档案 |
| 推翻的决策 | 删除旧条目,留新决策 |
| 跨会话只用一次的临时上下文 | 删除 |

## 跨项目影响检查

最容易漏改的场景:

- **上游 API 变了 → 下游 SDK 文档**:协议变化必须两边对齐
- **共享子域 / 路由 / 环境变量改了 → 所有 consumer 项目的 setup 文档**
- **认证中台变更 → 所有接入应用的 integration guide**
- **公共组件 / 基础设施 升级 → 各项目的 operator-runbook 提及版本号的地方**

判断方法:这次改的东西有没有 SDK、子域、共享配置、跨进程协议?有就要在所有依赖项目里搜一遍提到这件事的文档。

## 文档结构通用约定

按影响更新，不为凑齐模板而创建空文档：

1. **integration guide / 外部视角文档**：外部调用方式、SDK 示例或错误码变化时更新
2. **architecture**：内部数据流、状态机或设计取舍变化时更新
3. **runbook**：部署、监控、环境变量或故障排查变化时更新
4. **handoff**：大特性完成且确有跨人员交接需求时更新；纯历史归 git log / CHANGELOG

API 速查表、环境变量表、术语表一旦存在，必须保持「所见即最新」。
