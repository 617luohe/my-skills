# Changelog

All notable changes to this skills repository will be documented in this file.

## [Unreleased]

对照 mattpock/skills 参考体系（`main=6654f6b`）逐项优化，忠实其写作规范与第一性原理。

### 语言优化（P0 / P10 / P11 / P12）

- **description 措辞**：触发词按分支收敛（`noteall` 15 词 → 4 分支）；description 内否定式「非触发」改写为正向 scope（`0--dialectic`、`issue-reporting`、`0--neat-freak`）；`vision-skill` 删除冗余 `when_to_use` 字段与正文「触发」节，触发只留 description 一处。
- **正文否定句分级**：默认已遵守的 no-op 删除或改正向（`不编造根因`、`不猜图`、`不写进 CLAUDE.md`、`不主动推销` 等）；硬 guardrail（`git add .`、脱敏、冲突停止）保留。
- **摘要缓存消除**：`4-debug` 复述的 6 阶段纪律 4 条改为指向 `references/diagnosis-loop.md`。

### writing-for-agents 忠实同步（P1）

- 主文 = 参考 `SKILL.md` 全译，10 杠杆定位句同义（含 two loads、variance bug、co-location、negation、no-op、cache、sediment）。
- 新增 `SKILL-MECHANICS.md`（调用方式 / 拆分 / router 技能）。
- 我方定制（触发 / 写作流程 / 完成条件 / 关系）逐出为 `SKILL-WORKFLOW.md` disclosed reference。

### grilling 回收 sub-agent 不阻塞（P2）

- 事实派 sub-agent 查、不阻塞本轮，仅下游问题等待。
- 删除自创「逐步模式」节，由 rounds + frontier 天然覆盖逐轮需求。

### 路由重构（P3 / P5）

- `0-router` 叙述式重写：规模先行（S/M/L/XL）为入口，主干 idea→ship + on-ramps + 独立支线。
- `3-review` 收敛为纯 Review / 架构评估；「只建单 / 根因修复 / 架构评估」的判路由单点到 `0-router`，消除双路由。

### README / USAGE 按调用方式重组（P4）

- `USAGE.md` 索引按 User-invoked / Model-invoked 分两组，与 manifest `invocation` 一致；`README.md` 调用分类同步。
- 每个活跃技能保留唯一索引行且名链接 `SKILL.md`。

### vocabulary 改 model-invoked（P6）

- `vocabulary/grilling`、`vocabulary/tdd`：`invocation: user` → `model`，`disable-model-invocation: false`，`openai.yaml` 允许隐式调用（参考语义：model-invocation 只增加 agent 可达性）。
- description 去否定短语，改为正向「Use when」。

### 阶段技能瘦身（P7 / P8 / P9）

- `2-implement`、`4-debug` 收敛为「输入 → 调用纪律源 → 交接」薄编排壳。
- 纪律单源到 `/tdd` 与 `references/diagnosis-loop.md`；canonical 依赖显式引用。



## [3.0.0] - 2026-08-18

> Major 版本：第一性原理精简。修复全部治理漂移（validator 9→0 错误），删除 1.3.0 残留技能 leader，fat 技能收敛为 grilling 式内核 + references 指针。

### Removed

- **leader**：删除残留目录与路由引用（1.3.0 已删除）；manifest 22 → 21 active skill。
- **已删除 vocabulary 的正文引用**：`1-plan`/`3-review`/`4-debug` 对 `/vocabulary/domain-modeling`、`/vocabulary/code-review`、`/vocabulary/diagnosing-bugs` 的引用改为各自 `references/` 指针。

### Changed

- **0--neat-freak**：收敛为内核（身份、三层知识、毕业、五步流程骨架、MUST）；盘点细节/编辑原则/特殊情况迁入 `references/sync-matrix.md`。
- **vocabulary/tdd**：测试策略去重；好的/坏的测试与行为示例迁入 `references/test-principles.md`。
- **2-implement**：复评回环压缩为 `/3-review` 契约指针；验证段改用项目原生 test/type/lint 命令；MUST 去重。
- **0-router**：三路判定与规模表合并为「规模路由」表。
- **引用规范**：`/vocabulary/grilling`、`/vocabulary/tdd` 统一为扁平 deployment name（`/grilling`、`/tdd`），canonical 名仅保留在 manifest 依赖与文档契约处。

## [2.0.0] - 2026-08-13

> Major 版本：三个曾部署的 vocabulary 名称已删除，其工作流内聚到对应阶段技能。

### Added

- **issue-reporting**：显式建单触发的独立技能；同 tracker 查重，远程创建前展示完整内容并确认。
- **skill_manifest contract**：输出 schema/repository 版本与 active skill 的 canonical name、deployment_name、hosts、invocation、status；publication/contract 支持 `--output` 直接写 UTF-8 JSON。
- **路由语义 eval 数据集**：24 个真实正例与近似负例，覆盖相邻技能和 user-only 边界；静态测试只校验数据结构。
- **治理门禁**：新增依赖循环、active→deprecated、调用图、USAGE 全量索引及 manifest/pyproject/CHANGELOG 版本一致性检查。

### Changed

- **0-router**：成为单一路由事实源，按歧义/影响/可逆性分三路，并定义 planning→fresh development slice→fresh review 的磁盘契约。
- **2-implement**：改为宿主与语言中立，发现并运行项目原生 test/type/lint/build；行为变更继续加载内部 TDD vocabulary；正式 review 交接覆盖 committed/staged/unstaged 与未跟踪文件内容。
- **3-review**：收敛为正式 diff review，固定 fixed point/spec/workspace diff/证据输入和三态裁决；未跟踪文件不得静默漏审。
- **0--dialectic**：统一为 user-only，禁止模型隐式调用。
- **0--loop**：标记 experimental + user-only；移除最小轮次与耗尽轮次逻辑，AC 达标或连续两轮无高价值发现即停；新用户消息只写 superseded PROGRESS；执行前探测宿主隔离能力并支持顺序 fresh-context 降级。
- **0-init**：明确只服务 Python + uv。
- **0--claude / 0--neat-freak**：统一 CLAUDE.md 小内核与路由指针职责；neat-freak 改用跨平台文件工具语义。
- **noteall**：统一 Vault 解析策略；当前目录是 Vault 时按配置优先使用，否则使用默认路径，整次流水线锁定同一路径。
- **3-review**：已有验证证据改为可选；缺失时由审查者运行可自动验证门禁，不阻塞独立 review。
- **4-debug / 0--loop**：恢复中文调试触发边界；loop 统一逐轮一行进度规则。
- **grilling / tdd**：description 限定为父工作流加载的内部 vocabulary；TDD 使用项目原生测试命令。
- **治理文档与索引**：更新调用图、唯一事实源路径和 2.0.0 技能清单；CLAUDE 校验改为小内核路由指针，导航只保留一句路由指针。
- **manifest**：24 → 22 个 active skill；补齐 noteall Worker 依赖，`repository_version` 升至 2.0.0。
- **跨宿主调用契约**：manifest dependencies 保持 canonical name；正文 slash 引用与 validator 统一使用扁平 deployment name。
- **validator / router fixtures**：显式 CLAUDE 指针检查要求目标存在；slash 校验覆盖导航与治理文档并识别反引号单段 typo；路由 fixture 增加 pytest 结构门禁，语义判断仍由人工或模型 eval。
- **CI**：扩展为 Windows/Ubuntu × Python 3.11/3.12，并校验 CLAUDE 模板小内核指针。

### Removed

- **vocabulary/domain-modeling**：内容迁入 `1-plan/references/`；旧 `/domain-modeling` 调用迁移到 `/1-plan`。
- **vocabulary/code-review**：内容迁入 `3-review/references/`；旧 `/code-review` 调用迁移到 `/3-review`。
- **vocabulary/diagnosing-bugs**：内容迁入 `4-debug/references/`；旧 `/diagnosing-bugs` 调用迁移到 `/4-debug`。

## [1.3.0] - 2026-08-12

### Removed

- **multi-worker**：并行 worktree 编排；替代：主流程顺序开发或 Cursor 内置多 agent
- **leader**：外部 agent 任务书；替代：直接在对话中描述任务
- **0--explore**：预算驱动深潜探索；替代：只读调查 `docs/analysis/` 或 `/1-plan`
- **0--tokenless**：超压缩沟通；替代：CLAUDE.md「工作哲学·沟通」简洁表达

### Changed

- 路由表、USAGE、README、3-review、0--dialectic 同步移除上述技能引用
- manifest：27 → 23 技能；repository_version → 1.3.0

## [1.2.0] - 2026-08-12

### Changed

- **README**: 去重技能表，索引统一指向 USAGE/CHANGELOG（189→~105 行）
- **5-git / 0-init / 0--laoyoutiao**: 命令与示例外迁 references，SKILL 瘦身
- **2-implement**: 编码准则改为纯引用 CLAUDE.md
- **manifest**: 全技能增加 `category` 字段；version → 1.2.0
- **validate_skills**: `category` 校验；`--check-claude-mirror` 可选镜像对账
- **tests**: 路由意图 eval fixture（`tests/fixtures/prompts/router/`）

## [1.1.0] - 2026-08-12

### Changed

- 路由加载措辞统一；1-plan adr 引用修正；README「分发与部署」
- 2-implement/tdd 委托彻底化；Worker `invocation: user`
- CLAUDE 支撑层补 0--explore；CI 增加 pytest
- 0-router 探索分流；规模 S/M/L/XL 映射
- 5-git / 6-sum / neat-freak 示例外迁

### Added

- `invocation-semantic` 校验；`pyproject.toml`；`status: experimental` 支持

### Removed

- `--check-deployments` 宿主部署层校验

## [1.0.0] - 2026-08-08

初始治理基线与 noteall 机制门禁批次。详见历史 commit。
