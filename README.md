# My Skills Library

个人 skills 开发目录。每个 skill 独立文件夹；改完 commit + push，由 skills-manager 同步到运行时（见下方「分发与部署」）。

📖 **使用说明书**：[USAGE.md](USAGE.md) — 每个技能的场景描述 + 案例演示。
🧭 **路由器**：`/0-router` — 不知道用哪个技能？直接问路由器。

## 目录结构

```
my-skills/
├── README.md / USAGE.md         — 索引与调用示例
├── 0-router/                 — 技能路由器（唯一入口）
├── vocabulary/                   — 可复用核心循环（被其他技能调用）
│   ├── grilling/                — 询问循环
│   └── tdd/                     — TDD 循环
├── my-note/                      — 知识管理技能体系（类比 vocabulary 层）
│   ├── noteall/                 — 唯一入口（三阶段流水线编排）
│   ├── index-keeper/            — 内部 Worker（索引维护）
│   └── vault-publisher/         — 内部 Worker（所选 Vault 发布）
├── 0-init/ ~ 6-sum/        — 阶段 0~6 开发流程
├── 0--*/                        — 阶段 0 扩展能力
└── scripts/                     — manifest 解析与受管技能部署脚本
```

## 命名规范

所有技能命名遵循以下约定：

| 类型              | 命名格式              | 示例                                         | 说明                               |
| ----------------- | --------------------- | -------------------------------------------- | ---------------------------------- |
| **阶段技能**      | `N-中文名称`          | `0-init`、`1-plan`、`2-implement`                 | N 为阶段编号 0-6                   |
| **扩展能力**      | `0--英文名称`         | `0--claude`、`0--dialectic`                 | 双连字符标识阶段 0 扩展            |
| **路由器**        | `0-router`         | `0-router`                                | 唯一入口，独立前缀                 |
| **vocabulary 层** | `vocabulary/英文名称` | `vocabulary/grilling`                        | 可复用核心，不直接调用             |
| **my-note 层**    | `my-note/英文名称`    | `my-note/noteall`、`my-note/vault-publisher` | 知识管理层，noteall 为唯一用户入口 |
| **独立方法论**    | `英文或中文名称`      | `writing-for-agents`                         | 不属于主流程的独立技能             |

**命名约束**：

- 阶段技能必须以 `N-` 开头（N=0-6），后接中文名称
- 扩展能力必须以 `0--` 开头，后接英文名称（双连字符区分单连字符阶段）
- vocabulary 层必须位于 `vocabulary/` 子目录下，使用英文名称
- 禁止在非阶段技能中使用 `N-` 格式（避免与阶段编号冲突）

## 调用分类

**单技能 invocation**（manifest 字段）：`invocation: model` 允许模型按 description 自动调用；`invocation: user` 仅用户显式输入（如 my-note 内部 Worker）。默认 `disable-model-invocation: false` + `allow_implicit_invocation: true`。

**hosts 语义**：`hosts` 表示 skills-manager 的分发目标，不等于各宿主已通过完整行为认证；技能应在正文声明环境要求，并在执行前探测所需能力。

**名称契约**：manifest 的 `name`、`path`、`dependencies` 使用 canonical name（如 `vocabulary/tdd`）；skills-manager 按末段扁平部署，运行时 slash 调用必须使用 contract 的 `deployment_name`（如 `/tdd`、`/noteall`）。

按调用方式分两组（与 manifest `invocation` 字段一致，详见 [USAGE.md](USAGE.md)）：

**User-invoked**（仅用户显式输入可及，不进入模型技能表）：`0--dialectic`、`vocabulary/grilling`、`vocabulary/tdd`、`my-note/index-keeper`、`my-note/vault-publisher`

**Model-invoked**（模型按 description 自动触发，用户亦可显式输入）：

- 阶段技能：`0-router`、`0-init`、`1-plan`、`2-implement`、`3-review`、`4-debug`、`5-git`、`6-sum`
- 扩展能力：`0--claude`、`0--neat-freak`
- 独立方法论：`issue-reporting`、`writing-for-agents`、`wizard`、`vision-skill`
- my-note 层：`noteall` 唯一入口

`grilling`、`tdd` 由父工作流加载；`vault-publisher`、`index-keeper` 由 `noteall` 调度。

技能完整索引见 [USAGE.md](USAGE.md)；调用依赖见 [invocation-graph.md](docs/governance/invocation-graph.md)；架构演进见 [CHANGELOG.md](CHANGELOG.md)。

## 分发与部署

技能单一事实源 + **skills-manager** 同步分发：

1. **权威源（唯一编辑处）**：本仓库（独立 git，`origin: 617luohe/my-skills`）——所有技能在此修改
2. **运行时生效**：改权威源 → commit + push → skills-manager 从远端拉取 → 符号链接生效到 `~/.claude/skills/` 及项目 `.claude/.cursor/.codex/skills/`（存在延迟窗口）
3. **治理验证**：`skills-manifest.yaml` 为清单事实源；`scripts/validate_skills.py` 按运行时 deployment name 校验 slash 引用；`scripts/skill_manifest.py contract` 输出 active skill 的 canonical name、deployment_name、hosts、invocation 与 status

> 分发由 skills-manager 负责；本仓库治理脚本**不校验**宿主部署目录。

## 治理验证

治理脚本位于 `scripts/`，在仓库根目录执行：

```bash
python scripts/validate_skills.py
python scripts/validate_skills.py --json
python scripts/validate_skills.py --check-claude-pointer --claude-md <project>/CLAUDE.md
python scripts/skill_manifest.py contract
python scripts/skill_manifest.py contract --output skills-contract.json
```

验证源码治理规则；治理错误返回非零退出码。显式 CLAUDE 指针检查必须传入实际项目文件，不能假设父目录布局。`--output` 直接写 UTF-8 JSON（含末尾换行），避免依赖 shell 重定向编码。CI 在 Windows/Ubuntu 与 Python 3.11/3.12 运行 CLAUDE 模板指针校验、`validate_skills.py` 与 `pytest`。

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
