# Skills 使用说明书（索引）

> 本文件只做**导航索引**，每个技能的完整规则以其 `SKILL.md` 为唯一事实源，本文件不重复正文。
> **路由**：完整规则只见 `/0-router`。
> **名称**：文档链接使用 canonical source path；“触发”列使用 skills-manager 扁平部署后的 runtime slash name。
> **分组**：按调用方式分两组——**User-invoked**（仅用户显式输入可及）与 **Model-invoked**（模型可按 description 自动触发，用户也能显式输入）。分组与 `skills-manifest.yaml` 的 `invocation` 字段一致。

---

## User-invoked（仅用户显式调用）

| 技能               | 职责                                                              | 触发                        | 文档                                        |
| ------------------ | ----------------------------------------------------------------- | --------------------------- | ------------------------------------------- |
| `0-dialectic`     | 战略问题的矛盾分析与阶段策略；仅用户显式调用                      | 用户显式 `/0-dialectic`    | [SKILL.md](0-dialectic/SKILL.md)           |
| `vault-publisher`  | 所选 Vault 受控发布 Worker（校验 → 同步 → 只暂存 owned paths → commit/push） | 被 `noteall` 调度     | [SKILL.md](my-note/vault-publisher/SKILL.md) |
| `index-keeper`     | 索引维护 Worker（增量更新 `_INDEX.md`、缺失补全、健康检查）       | 被 `noteall` 调度           | [SKILL.md](my-note/index-keeper/SKILL.md)   |

---

## Model-invoked（模型可自动触发，用户亦可显式调用）

### 主流程（阶段 0~6 + 路由）

| 技能            | 职责                                                              | 触发                    | 文档                             |
| --------------- | ----------------------------------------------------------------- | ----------------------- | -------------------------------- |
| `0-router`      | **技能路由唯一事实源**                                            | `/0-router`             | [SKILL.md](0-router/SKILL.md)    |
| `0-init`        | 仅初始化 Python + uv：项目结构、本地 git、uv 环境                 | `/0-init`               | [SKILL.md](0-init/SKILL.md)      |
| `0-claude`     | 初始化/修复 CLAUDE.md（工作哲学 + 记忆约定）                      | `/0-claude`            | [SKILL.md](0-claude/SKILL.md)   |
| `1-plan`        | 方案追问 → 领域建模 → 接口设计 → PRD → 任务拆解                   | `/1-plan`               | [SKILL.md](1-plan/SKILL.md)      |
| `2-implement`   | 宿主/语言中立实现；发现项目原生 test/type/lint/build              | `/2-implement`          | [SKILL.md](2-implement/SKILL.md) |
| `3-review`      | 只做正式 diff review，输出 PASS / PASS WITH WARNINGS / FAIL       | `/3-review`             | [SKILL.md](3-review/SKILL.md)    |
| `4-debug`       | 结构化调试（复现 → 假设 → 验证 → 修复 + 回归）                    | `/4-debug`              | [SKILL.md](4-debug/SKILL.md)     |
| `5-git`         | Git 版本控制（init/save/log/rollback/branch/remote/push）         | `/5-git`                | [SKILL.md](5-git/SKILL.md)       |
| `6-sum`         | 会话收尾沉淀：修改总结 + 经验入 memory + 结构整理 + 交接          | `/6-sum`                | [SKILL.md](6-sum/SKILL.md)       |

### Vocabulary 层（可复用纪律，模型可自动取用）

| 技能       | 职责                                                              | 触发                                    | 文档                                     |
| ---------- | ----------------------------------------------------------------- | --------------------------------------- | ---------------------------------------- |
| `grilling` | 对计划、决策或想法穷尽追问，沿决策依赖图收敛共享理解              | `/grilling` 或"追问/grill"意图；`/1-plan` 也加载 | [SKILL.md](vocabulary/grilling/SKILL.md) |
| `tdd`      | RED-GREEN-REFACTOR：先写失败测试再写最少实现                      | `/tdd` 或 test-first 意图；`/2-implement`、`/4-debug` 也加载 | [SKILL.md](vocabulary/tdd/SKILL.md) |

### 独立方法论（不绑定开发阶段，跨场景通用）

| 技能                 | 职责                                                                                            | 触发                  | 文档                                    |
| -------------------- | ----------------------------------------------------------------------------------------------- | --------------------- | --------------------------------------- |
| `issue-reporting`    | 用户明确要求建单时查重、展示完整草稿并经确认后创建单个远程 issue                              | `/issue-reporting`    | [SKILL.md](issue-reporting/SKILL.md)    |
| `writing-for-agents` | 写给 agent 的文档写作规范，写/改技能时由模型自动调起                                          | `/writing-for-agents` | [SKILL.md](writing-for-agents/SKILL.md) |
| `wizard`             | 生成交互式 bash 向导，带人走完只有人能做的步骤（配 CI secrets、第三方 dashboard、一次性迁移）   | `/wizard`             | [SKILL.md](wizard/SKILL.md)             |
| `vision-skill`       | 图片描述：为纯文本模型经 OpenCode Go 视觉 API 描述图片/截图/URL                                  | `/vision-skill`       | [SKILL.md](vision-skill/SKILL.md)       |
| `0-neat-freak`      | 知识库洁癖审查：文档↔代码一致性、尺寸体检、记忆毕业               | `/0-neat-freak`      | [SKILL.md](0-neat-freak/SKILL.md)      |

### My-Note 层（知识管理）

| 技能       | 职责                                                                  | 触发       | 文档                                 |
| ---------- | --------------------------------------------------------------------- | ---------- | ------------------------------------ |
| `noteall`  | 受控知识库唯一入口，解析并锁定 Vault 后编排 Intake → Curate → Publish | `/noteall` | [SKILL.md](my-note/noteall/SKILL.md) |

---

> 说明：以上为按调用方式分组的索引。各技能详细规则、对话示例与 MUST 规则见对应 `SKILL.md`，不再于本文件重复。
