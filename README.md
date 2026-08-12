# My Skills Library

个人 skills 开发目录。每个 skill 独立文件夹；改完 commit + push，由 skills-manager 同步到运行时（见下方「分发与部署」）。

📖 **使用说明书**：[USAGE.md](USAGE.md) — 每个技能的场景描述 + 案例演示。
🧭 **路由器**：`/0-询问luohe` — 不知道用哪个技能？直接问路由器。

## 目录结构

```
my-skills/
├── README.md / USAGE.md         — 索引与调用示例
├── 0-询问luohe/                 — 技能路由器（唯一入口）
├── vocabulary/                   — 可复用核心循环（被其他技能调用）
│   ├── grilling/                — 询问循环
│   ├── domain-modeling/         — 领域建模
│   ├── tdd/                     — TDD 循环
│   ├── code-review/             — 代码审查
│   └── diagnosing-bugs/         — Bug 诊断
├── my-note/                      — 知识管理技能体系（类比 vocabulary 层）
│   ├── noteall/                 — 唯一入口（三阶段流水线编排）
│   ├── index-keeper/            — 内部 Worker（索引维护）
│   └── vault-publisher/         — 内部 Worker（固定 Vault 发布）
├── 0-启动/ ~ 6-最后整理/        — 阶段 0~6 开发流程
├── 0--*/                        — 阶段 0 扩展能力
└── scripts/                     — manifest 解析与受管技能部署脚本
```

## 命名规范

所有技能命名遵循以下约定：

| 类型              | 命名格式              | 示例                                         | 说明                               |
| ----------------- | --------------------- | -------------------------------------------- | ---------------------------------- |
| **阶段技能**      | `N-中文名称`          | `0-启动`、`1-规划`、`2-开发`                 | N 为阶段编号 0-6                   |
| **扩展能力**      | `0--英文名称`         | `0--claude`、`0--laoyoutiao`                 | 双连字符标识阶段 0 扩展            |
| **路由器**        | `0-询问luohe`         | `0-询问luohe`                                | 唯一入口，独立前缀                 |
| **vocabulary 层** | `vocabulary/英文名称` | `vocabulary/grilling`                        | 可复用核心，不直接调用             |
| **my-note 层**    | `my-note/英文名称`    | `my-note/noteall`、`my-note/vault-publisher` | 知识管理层，noteall 为唯一用户入口 |
| **独立方法论**    | `英文或中文名称`      | `writing-for-agents`                         | 不属于主流程的独立技能             |

**命名约束**：

- 阶段技能必须以 `N-` 开头（N=0-6），后接中文名称
- 扩展能力必须以 `0--` 开头，后接英文名称（双连字符区分单连字符阶段）
- vocabulary 层必须位于 `vocabulary/` 子目录下，使用英文名称
- 禁止在非阶段技能中使用 `N-` 格式（避免与阶段编号冲突）

## 调用分类

**路由加载**：复杂需求先加载 `/0-询问luohe` 选路径；每会话首个复杂需求强制加载。CLAUDE.md 常驻工作哲学，路由表不镜像。

**单技能 invocation**（manifest 字段）：`invocation: model` 允许模型按 description 自动调用；`invocation: user` 仅用户显式输入（如 my-note 内部 Worker）。默认 `disable-model-invocation: false` + `allow_implicit_invocation: true`。

按层级分组：

- **阶段技能**：`0-询问luohe`、`0-启动`、`1-规划`、`2-开发`、`3-检查`、`4-调试`、`5-版本管理`、`6-最后整理`
- **扩展能力**：`0--claude`、`0--dialectic`、`0--laoyoutiao`、`0--neat-freak`、`0--loop`
- **独立方法论**：`writing-for-agents`、`wizard`、`vision-skill`
- **vocabulary 层**：`grilling`、`domain-modeling`、`tdd`、`code-review`、`diagnosing-bugs`。优先被阶段技能委托；模型亦可按 description 调用，用户无需记路径。
- **my-note 层**：`noteall` 唯一入口；`vault-publisher`、`index-keeper` 内部 Worker（由 noteall 调度）

技能完整索引见 [USAGE.md](USAGE.md)；架构演进见 [CHANGELOG.md](CHANGELOG.md)。

## 分发与部署

技能单一事实源 + **skills-manager** 同步分发：

1. **权威源（唯一编辑处）**：本仓库（独立 git，`origin: 617luohe/my-skills`）——所有技能在此修改
2. **运行时生效**：改权威源 → commit + push → skills-manager 从远端拉取 → 符号链接生效到 `~/.claude/skills/` 及项目 `.claude/.cursor/.codex/skills/`（存在延迟窗口）
3. **治理验证**：`skills-manifest.yaml` 为清单事实源；`scripts/validate_skills.py` 校验源码治理（manifest ↔ 目录 ↔ frontmatter ↔ openai.yaml）

> 分发由 skills-manager 负责；本仓库治理脚本**不校验**宿主部署目录。

## 治理验证

治理脚本位于 `scripts/`，在仓库根目录执行：

```bash
python scripts/validate_skills.py
python scripts/validate_skills.py --json
python scripts/validate_skills.py --check-claude-mirror --claude-md ../CLAUDE.md
```

验证源码治理规则；治理错误返回非零退出码。CI 运行 `validate_skills.py` 与 `pytest`。

本地开发（含 pytest）：

```bash
pip install -e ".[dev]"
python -m pytest -q
```

## 技能生命周期

| 阶段     | 动作                                                                   | 校验                                                                     |
| -------- | ---------------------------------------------------------------------- | ------------------------------------------------------------------------ |
| **新建** | 写 `SKILL.md`（description 含触发词）→ manifest 登记（`status: stable`）→ 跑 validator | 命名规范 + frontmatter 三处一致 + 引用完整 + description 非空且 ≥12 字符 |
| **维护** | 直接改权威源，跑 validator 过闸                                        | 每次提交前 `python scripts/validate_skills.py`                           |
| **退役** | manifest `status` 改 `deprecated` + 写 `deprecated_note`（迁移指引）   | deprecated 必须带 `deprecated_note`                                      |
| **清理** | 从 manifest 删除条目 + 删除目录                                        | validator 报 manifest 与目录的 missing/extra 不一致                      |

- `status: deprecated` 表示技能已弃用但保留一版供迁移，validator 要求必须带 `deprecated_note`。
- 退役后由 skills-manager 同步清除；`deprecated_note` 写迁移指引，正文不应再引用旧技能名。
