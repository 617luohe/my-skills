# my-skills 体系优化复核（2026-08-13）

## 结论

当前体系应继续走“小而可组合的技能 + 单一路由 + 机器治理”，不再增加技能数量。相对 `master` 的既有简化已把受管技能收敛到 22 个；本轮优先修复发布契约、依赖可达性、知识库落点、审查入口和跨平台门禁，并为真实模型路由评测建立数据集。

当前结果：

- 22 个受管技能：21 stable、1 experimental；18 model、4 user-only。
- `validate_skills.py`：0 error、0 warning。
- `pytest`：90 passed。
- 破坏性移除三个已部署 vocabulary 名称，因此版本从原拟 1.4.0 校正为 2.0.0。

## 推荐顺序与落地状态

### S1｜把破坏性简化标成 major 版本 — 已完成

理由：`domain-modeling`、`code-review`、`diagnosing-bugs` 曾是可部署名称；即使内容正确内聚到父技能，删除名称仍会影响旧调用。minor 版本硬删除会让 runtime contract 和退役 SOP 失真。

动作：

- `skills-manifest.yaml` 与 `pyproject.toml` 统一为 2.0.0。
- CHANGELOG 将本批次标为 2.0.0。
- 退役 SOP 明确：minor 只 deprecate；major 才可删除；仅内部且无已知用户入口的名称允许在 major 直接删除。

### S2｜让依赖图可证明、可回归 — 已完成

理由：`noteall` 实际调度 `index-keeper`，manifest 却只声明 `vault-publisher`；调用图又漏掉 Worker 边。原 validator 只验证目标存在，无法发现循环、active → deprecated 或文档漏边。

动作：

- 补齐 `my-note/noteall` 的两条 canonical dependency。
- 调用图补齐两条 Worker 边。
- validator 新增依赖循环、active → deprecated、调用图完整性检查。

### S3｜把格式测试与语义 eval 分开 — 已完成基线

理由：旧 router fixture 只证明“目标名称存在”，不能证明模型会选对。真实模型 eval 有成本与波动，不适合伪装成确定性 CI。

动作：

- 新增 `tests/fixtures/prompts/router/trigger-evals.json`，含 24 个真实正例和近似负例。
- 覆盖规划/开发、建单/调试、memory/noteall、收尾/neat-freak、宿主定时 loop/共识 loop 等竞争边界。
- pytest 只校验数据集 schema、目标技能、禁选技能和近似负例存在。
- 发布前用固定宿主与模型多次运行并记录命中率；暂不设阻断式 CI。

### S4｜消除 Vault 落点冲突 — 已完成

理由：CLAUDE 模板允许当前目录 Vault，noteall 却声明绝不使用当前目录。同一句知识库请求可能落到不同位置，属于数据边界问题。

动作：

- `noteall/references/config.yaml` 成为解析策略唯一源。
- 当前目录含 `.obsidian/` 且策略允许时优先当前 Vault，否则使用默认 `vault_path`。
- 启动时只解析一次，整次 Intake → Curate → Publish 与 Worker 使用同一所选路径。

### S5｜降低错误阻塞与触发漂移 — 已完成

理由：

- 独立 review 不应因为上游没留下测试结果而无法开始；审查者本就会运行可自动验证门禁。
- `4-调试` 删除中文触发词后，中文请求更依赖模型猜测。
- loop references 要求逐轮一行进度，主文件却没有同一规则。

动作：

- `/3-检查` 只把 fixed point、spec、diff 设为必需；已有证据改为可选。
- `/4-调试` 恢复中文触发边界。
- `0--loop`（已删除）主文件明确每轮 checkpoint 后输出一行进度，但不索取新决策。

### S6｜让本机环境进入持续门禁 — 已完成

理由：实际开发环境是 Windows，仓库又包含中文路径、PowerShell 编码和路径分隔符风险；原 CI 只跑 Ubuntu/Python 3.12。

动作：

- CI 使用 Windows/Ubuntu × Python 3.11/3.12 矩阵。
- 默认验证加入 CLAUDE 模板小内核指针检查。
- validator 新增 manifest、pyproject、CHANGELOG 版本一致性与 USAGE 全量索引检查。

## 参考实践

以下 star 数由 GitHub API 于 2026-08-13 查询，只用于说明案例成熟度，不作为设计正确性的替代证据。

- [Agent Skills 规范](https://agentskills.io/specification)：metadata → SKILL.md → references/scripts 的三级渐进披露；description 同时说明“做什么、何时用”；环境要求放 compatibility。
- [anthropics/skills](https://github.com/anthropics/skills)（168,810 stars）：触发正例与近似负例、旧版/无技能基线、留出集和多次运行。本轮采用“真实 eval 数据集与静态 CI 分离”。
- [obra/superpowers](https://github.com/obra/superpowers)（271,582 stars）：小技能组合、fresh context 实现、规格与质量独立审查。现有 planning → fresh development slice → fresh review 契约应保留。
- [mattpocock/skills](https://github.com/mattpocock/skills)（215,985 stars）：用户编排技能与模型纪律分离，兜底路由不替代专用技能。本项目继续保留单一路由，但不再复制技能正文。
- [github/awesome-copilot](https://github.com/github/awesome-copilot)（37,782 stars）与 [Copilot 定制边界](https://docs.github.com/en/copilot/reference/customization-cheat-sheet)：instructions 管常驻规则，skill 管按需流程，subagent 管隔离任务，hook/script 管确定执行。`ai-vibe-coding-config` 的 hooks 继续留在宿主层，不搬进 my-skills。
- [openai/codex](https://github.com/openai/codex)（105,695 stars）：技能发现有上下文预算；数量和 description 总成本比继续拆短正文更值得关注。

本地参考 `E:\workplace\ai-vibe-coding-config` 已验证三项可迁移实践：Windows CI、模板源门禁、生成 contract；其 hooks、setup 部署器和已归档 agents/workflows 属于 Claude Code 宿主配置，不应复制到跨宿主技能库。

## 暂不实施

### A1｜manifest defaults / schema v2

收益是删掉约三分之一机械字段，但 raw manifest 可能仍被 skills-manager 或旧脚本消费。先确认所有下游只消费生成 contract，再做一次有迁移说明的 schema 升级；本轮不以“少几十行 YAML”换兼容风险。

### A2｜全面跨宿主行为认证

本轮只把 `hosts` 明确定义为分发目标，并增加 Windows/Ubuntu 源码门禁。Claude、Cursor、Codex 的真实触发与工具能力仍应分别评测，不能把“成功复制文件”等同于“行为兼容”。

### A3｜严格 Agent Skills 规范命名迁移

中文阶段名、`0--` 双连字符和 canonical 嵌套名不满足开放规范的最严格命名约束。迁移会破坏现有 slash 调用与个人心智模型；在目标宿主出现实际加载失败前，只记录风险，不立即重命名 22 个技能。

### A4｜把总路由改为 user-only

高星案例倾向让模型直接依 description 选技能、总路由只做显式兜底；但本项目明确把首个复杂需求经路由作为个人协作政策。先用新 eval 数据证明 descriptions 能独立稳定分流，再决定是否降低路由常驻权重。

## 明确不做

- 不恢复三个已内聚 vocabulary 的兼容壳；major 版本与迁移记录比长期保留僵尸技能更简洁。
- 不引入第二套路由正则或工作流 DSL。
- 不复制 `ai-vibe-coding-config` 的 hooks、commands、setup 部署器。
- 不继续按行数机械拆 SKILL.md；当前主文件均在既定上限内。
- 不扩成数百技能的市场式目录；个人体系优先可发现性与维护成本。
