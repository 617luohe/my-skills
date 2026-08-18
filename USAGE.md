# Skills 使用说明书（索引）

> 本文件只做**导航索引**，每个技能的完整规则以其 `SKILL.md` 为唯一事实源，本文件不重复正文。
> **路由**：完整规则只见 `/0-询问luohe`。
> **名称**：文档链接使用 canonical source path；“触发”列使用 skills-manager 扁平部署后的 runtime slash name。

---

## Vocabulary 层（可复用核心，被其他技能调用）

| 技能       | 职责                                                               | 调用方                       | 文档                                     |
| ---------- | ------------------------------------------------------------------ | ---------------------------- | ---------------------------------------- |
| `grilling` | 内部询问循环，沿决策依赖图收敛共享理解                             | `/1-规划`、`/0--loop`        | [SKILL.md](vocabulary/grilling/SKILL.md) |
| `tdd`      | 内部 RED-GREEN-REFACTOR，使用项目原生测试命令保护行为变更          | `/2-开发`、`/4-调试`、`/0--loop` | [SKILL.md](vocabulary/tdd/SKILL.md)      |

---

## 独立方法论（不绑定开发阶段，跨场景通用）

| 技能                 | 职责                                                                                            | 触发                         | 文档                                    |
| -------------------- | ----------------------------------------------------------------------------------------------- | ---------------------------- | --------------------------------------- |
| `issue-reporting`    | 用户明确要求建单时查重、展示完整草稿并经确认后创建单个远程 issue                              | `/issue-reporting` 或明确建单 | [SKILL.md](issue-reporting/SKILL.md)    |
| `writing-for-agents` | 写给 agent 的文档写作规范（触发分支/完成标准/leading words/pruning），写/改技能时由模型自动调起 | `/writing-for-agents`        | [SKILL.md](writing-for-agents/SKILL.md) |
| `wizard`             | 生成交互式 bash 向导，带人走完只有人能做的步骤（配 CI secrets、第三方 dashboard、一次性迁移）   | `/wizard`                    | [SKILL.md](wizard/SKILL.md)             |
| `vision-skill`       | 图片描述：为纯文本模型（DeepSeek 等）经 OpenCode Go 视觉 API 描述图片/截图/URL                  | `/vision-skill`              | [SKILL.md](vision-skill/SKILL.md)       |

---

## 开发流程 Skills（按阶段 0~6 组织）

| 技能            | 职责                                                              | 触发                         | 文档                               |
| --------------- | ----------------------------------------------------------------- | ---------------------------- | ---------------------------------- |
| `0--claude`     | 初始化/修复 CLAUDE.md（称呼 + 工作哲学 + 路由入口 + 项目配置） | `/0--claude`                 | [SKILL.md](0--claude/SKILL.md)     |
| `0--dialectic`  | 战略问题的矛盾分析与阶段策略；仅用户显式调用                   | 用户显式 `/0--dialectic`     | [SKILL.md](0--dialectic/SKILL.md)  |
| `0--neat-freak` | 知识库洁癖审查：文档↔代码一致性、尺寸体检、记忆毕业               | `/0--neat-freak`             | [SKILL.md](0--neat-freak/SKILL.md) |
| `0--loop`       | experimental、user-only 共识长跑；AC 达标或连续两轮无高价值发现即停 | 用户显式 `/0--loop`          | [SKILL.md](0--loop/SKILL.md)       |
| `0-启动`        | 仅初始化 Python + uv：项目结构、本地 git、uv 环境                 | `/0-启动`                    | [SKILL.md](0-启动/SKILL.md)        |
| `0-询问luohe`   | **技能路由唯一事实源**                                            | `/0-询问luohe`               | [SKILL.md](0-询问luohe/SKILL.md)   |
| `1-规划`        | 方案追问 → 领域建模 → 接口设计 → PRD → 任务拆解                   | `/1-规划`                    | [SKILL.md](1-规划/SKILL.md)        |
| `2-开发`        | 宿主/语言中立实现；发现项目原生 test/type/lint/build              | `/2-开发`                    | [SKILL.md](2-开发/SKILL.md)        |
| `3-检查`        | 只做正式 diff review，输出 PASS / PASS WITH WARNINGS / FAIL       | `/3-检查`                    | [SKILL.md](3-检查/SKILL.md)        |
| `4-调试`        | 结构化调试（复现 → 假设 → 验证 → 修复 + 回归）                    | `/4-调试`                    | [SKILL.md](4-调试/SKILL.md)        |
| `5-版本管理`    | Git 版本控制（init/save/log/rollback/branch/remote/push）         | `/5-版本管理`                | [SKILL.md](5-版本管理/SKILL.md)    |
| `6-最后整理`    | 会话收尾沉淀：修改总结 + 经验入 memory + 结构整理 + 交接          | `/6-最后整理`                | [SKILL.md](6-最后整理/SKILL.md)    |

---

## My-Note 层（知识管理）

| 技能              | 职责                                                                         | 触发               | 文档                                         |
| ----------------- | ---------------------------------------------------------------------------- | ------------------ | -------------------------------------------- |
| `noteall`         | 受控知识库唯一入口，解析并锁定 Vault 后编排 Intake → Curate → Publish        | `/noteall` | [SKILL.md](my-note/noteall/SKILL.md)         |
| `vault-publisher` | 所选 Vault 受控发布 Worker（校验 → 同步 → 只暂存 owned paths → commit/push） | 被 `noteall` 调度  | [SKILL.md](my-note/vault-publisher/SKILL.md) |
| `index-keeper`    | 索引维护 Worker（增量更新 `_INDEX.md`、缺失补全、健康检查）                  | 被 `noteall` 调度  | [SKILL.md](my-note/index-keeper/SKILL.md)    |

---

> 说明：以上为分层索引。各技能详细规则、对话示例与 MUST 规则见对应 `SKILL.md`，不再于本文件重复。
