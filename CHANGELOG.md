# Changelog

All notable changes to this skills repository will be documented in this file.

## [Unreleased]

- **vocabulary/grilling、vocabulary/tdd**：`invocation: user` + `disable-model-invocation: true`，不再进入模型技能表；仍由 `/1-规划`、`/2-开发`、`/4-调试` 按需加载。

## [3.0.0] - 2026-08-18

> Major 版本：第一性原理精简。修复全部治理漂移（validator 9→0 错误），删除 1.3.0 残留技能 leader，fat 技能收敛为 grilling 式内核 + references 指针。

### Removed

- **leader**：删除残留目录与路由引用（1.3.0 已删除）；manifest 22 → 21 active skill。
- **已删除 vocabulary 的正文引用**：`1-规划`/`3-检查`/`4-调试` 对 `/vocabulary/domain-modeling`、`/vocabulary/code-review`、`/vocabulary/diagnosing-bugs` 的引用改为各自 `references/` 指针。

### Changed

- **0--neat-freak**：收敛为内核（身份、三层知识、毕业、五步流程骨架、MUST）；盘点细节/编辑原则/特殊情况迁入 `references/sync-matrix.md`。
- **vocabulary/tdd**：测试策略去重；好的/坏的测试与行为示例迁入 `references/test-principles.md`。
- **2-开发**：复评回环压缩为 `/3-检查` 契约指针；验证段改用项目原生 test/type/lint 命令；MUST 去重。
- **0-询问luohe**：三路判定与规模表合并为「规模路由」表。
- **引用规范**：`/vocabulary/grilling`、`/vocabulary/tdd` 统一为扁平 deployment name（`/grilling`、`/tdd`），canonical 名仅保留在 manifest 依赖与文档契约处。

## [2.0.0] - 2026-08-13

> Major 版本：三个曾部署的 vocabulary 名称已删除，其工作流内聚到对应阶段技能。

### Added

- **issue-reporting**：显式建单触发的独立技能；同 tracker 查重，远程创建前展示完整内容并确认。
- **skill_manifest contract**：输出 schema/repository 版本与 active skill 的 canonical name、deployment_name、hosts、invocation、status；publication/contract 支持 `--output` 直接写 UTF-8 JSON。
- **路由语义 eval 数据集**：24 个真实正例与近似负例，覆盖相邻技能和 user-only 边界；静态测试只校验数据结构。
- **治理门禁**：新增依赖循环、active→deprecated、调用图、USAGE 全量索引及 manifest/pyproject/CHANGELOG 版本一致性检查。

### Changed

- **0-询问luohe**：成为单一路由事实源，按歧义/影响/可逆性分三路，并定义 planning→fresh development slice→fresh review 的磁盘契约。
- **2-开发**：改为宿主与语言中立，发现并运行项目原生 test/type/lint/build；行为变更继续加载内部 TDD vocabulary；正式 review 交接覆盖 committed/staged/unstaged 与未跟踪文件内容。
- **3-检查**：收敛为正式 diff review，固定 fixed point/spec/workspace diff/证据输入和三态裁决；未跟踪文件不得静默漏审。
- **0--dialectic**：统一为 user-only，禁止模型隐式调用。
- **0--loop**：标记 experimental + user-only；移除最小轮次与耗尽轮次逻辑，AC 达标或连续两轮无高价值发现即停；新用户消息只写 superseded PROGRESS；执行前探测宿主隔离能力并支持顺序 fresh-context 降级。
- **0-启动**：明确只服务 Python + uv。
- **0--claude / 0--neat-freak**：统一 CLAUDE.md 小内核与路由指针职责；neat-freak 改用跨平台文件工具语义。
- **noteall**：统一 Vault 解析策略；当前目录是 Vault 时按配置优先使用，否则使用默认路径，整次流水线锁定同一路径。
- **3-检查**：已有验证证据改为可选；缺失时由审查者运行可自动验证门禁，不阻塞独立 review。
- **4-调试 / 0--loop**：恢复中文调试触发边界；loop 统一逐轮一行进度规则。
- **grilling / tdd**：description 限定为父工作流加载的内部 vocabulary；TDD 使用项目原生测试命令。
- **治理文档与索引**：更新调用图、唯一事实源路径和 2.0.0 技能清单；CLAUDE 校验改为小内核路由指针，导航只保留一句路由指针。
- **manifest**：24 → 22 个 active skill；补齐 noteall Worker 依赖，`repository_version` 升至 2.0.0。
- **跨宿主调用契约**：manifest dependencies 保持 canonical name；正文 slash 引用与 validator 统一使用扁平 deployment name。
- **validator / router fixtures**：显式 CLAUDE 指针检查要求目标存在；slash 校验覆盖导航与治理文档并识别反引号单段 typo；路由 fixture 增加 pytest 结构门禁，语义判断仍由人工或模型 eval。
- **CI**：扩展为 Windows/Ubuntu × Python 3.11/3.12，并校验 CLAUDE 模板小内核指针。

### Removed

- **vocabulary/domain-modeling**：内容迁入 `1-规划/references/`；旧 `/domain-modeling` 调用迁移到 `/1-规划`。
- **vocabulary/code-review**：内容迁入 `3-检查/references/`；旧 `/code-review` 调用迁移到 `/3-检查`。
- **vocabulary/diagnosing-bugs**：内容迁入 `4-调试/references/`；旧 `/diagnosing-bugs` 调用迁移到 `/4-调试`。

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
