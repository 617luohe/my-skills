## Task List

### T001: 建立 pytest 设施与基线测试提示
**Description:** my-skills 目前无 pytest 配置。新增 `pyproject.toml`（pytest 配置）与 `tests/` 目录；建立测试提示集 `tests/fixtures/prompts/`（path_pdf / url / free_text / with_intent / dirty_worktree / push_fail 六个场景），作为 T003-T005 的输入基线。为当前 noteall 建基线快照（git tag `pre-noteall-simplify`），保留新旧输出对照。
**Acceptance Criteria:**
- [ ] `pytest` 可在 my-skills 根目录运行且无收集错误
- [ ] `tests/fixtures/prompts/` 含 6 个场景提示文件
- [ ] git tag `pre-noteall-simplify` 已打在当前 HEAD
**AFK/HITL:** AFK
**Depends On:** None

### T002: 固定 Vault 配置
**Description:** 创建 `my-note/noteall/references/config.yaml`，定义唯一 Vault 路径 `C:\Users\Administrator\Documents\Obsidian Vault`。定义校验规则：路径存在且含 `.obsidian/` 才继续；校验失败即停止，不回退到当前工作目录。
**Acceptance Criteria:**
- [ ] config.yaml 中 Vault 路径为单一配置值，全流水线只引用它
- [ ] noteall 启动时校验 Vault；路径缺失/非 Vault 时停止并提示，绝不回退当前目录
- [ ] 该规则写入 noteall SKILL.md 的 MUST 规则
**AFK/HITL:** AFK
**Depends On:** None

### T003: 重写 noteall 入口
**Description:** 重写 `my-note/noteall/SKILL.md`：输入识别（路径/URL/文本）→ 处理倾向解析 → 三阶段编排（Intake→Curate→Publish）或维护模式。删除面向用户的复杂路由表与 14 个子 skill 引用。处理倾向覆盖自动推断，但不能覆盖安全不变量（固定 Vault、干净工作区、受控暂存、冲突停止）。`references/` 下的阶段指令文件作为编排正文。
**Acceptance Criteria:**
- [ ] SKILL.md 只含输入识别、倾向解析、三阶段/维护模式编排，无旧路由表
- [ ] 触发词覆盖：路径、URL、自由文本、整理、记录、会议、阅读、日记、写文章、批量、索引、MOC、文件整理
- [ ] 参数不足时一次一问分步盘问
- [ ] 倾向不能覆盖安全不变量（有测试提示验证）
**AFK/HITL:** AFK
**Depends On:** T002

### T004: 合并 Intake 与 Curate 公共能力 + profiles
**Description:** 编写 `references/intake.md`（输入解析、原件复制到 raw/、URL/文本来源记录、元数据提取）、`references/curate.md`（笔记形态判断、摘要/结构化/去重/链接、索引更新、原始副本归档，含 compose/polish/atomic 模式）、`references/maintain.md`（维护模式：批量、MOC/审计、文件整理、索引健康检查）。创建 `references/profiles.yaml`，将 meeting/reading/journal/article 定义为 profile（提取字段、目标目录、模板），从旧 skill 吸收模板细节。保留重复收录检测（询问更新/另存/跳过，不静默覆盖）。
**Acceptance Criteria:**
- [ ] 四个 references 文件与 profiles.yaml 就位，公共步骤只写一次
- [ ] meeting/reading/journal/article 六类输入走同一流水线，仅 profile 差异
- [ ] 维护模式跳过 Intake 直接 Curate+Publish
- [ ] 同名来源重复收录必询问，不静默覆盖
**AFK/HITL:** AFK
**Depends On:** T003

### T005: 实现 vault-publisher（内部 Worker）
**Description:** 创建 `my-note/vault-publisher/SKILL.md` + `scripts/publish_vault.py`。Python 状态机：validate_vault → require_clean_worktree → fetch_remote → sync_remote（up_to_date / fast_forward / clean_auto_merge / conflict:STOP）→ retry_pending_push → stage_owned_paths（仅本次 owned paths，不用 git add .）→ commit（无变更不建空提交）→ push（失败保留本地提交并报告）。提交信息格式 `notes(<type>): ...`。编写 `tests/test_publish_vault.py`，用 tmp_path 临时 git 仓库覆盖：干净提交、脏工作区停止、远端 fast-forward、远端冲突停止、push 失败保留本地、无变更不建空提交、遗留提交补推。
**Acceptance Criteria:**
- [ ] pytest 全绿（覆盖上述 7 场景）
- [ ] 脚本不硬编码 Vault 路径，`--vault` 由 noteall 传入
- [ ] 冲突/脏工作区返回非零退出码并输出明确报告，不做任何自动解决
- [ ] 不调用 `git add .`
**AFK/HITL:** AFK
**Depends On:** T002

### T006: 精简旧 skills 与元数据
**Description:** 删除 14 个旧 skill 目录（meeting-minutes、reading-digester、daily-concierge、article-writer、note-composer、note-polisher、concept-atomizer、index-keeper、vault-cartographer、file-organizer、batch-curator、workflow-wrapup、raw-ingester、info-digester）。更新 `skills-manifest.yaml`：noteall 依赖改为仅 `[my-note/vault-publisher]`，移除旧条目。运行 `scripts/validate_skills.py` 校验。更新 CONTEXT.md（维护模式术语已在规划阶段补充）、README.md/USAGE.md 中 my-note 部分。git commit 记录删除（可回溯）。
**Acceptance Criteria:**
- [ ] 14 个旧目录已删除，git 历史可回溯
- [ ] manifest 只含 noteall + vault-publisher（my-note 层）
- [ ] `scripts/validate_skills.py` 通过
- [ ] README/USAGE 的 my-note 章节反映新结构
**AFK/HITL:** AFK
**Depends On:** T003, T004, T005
