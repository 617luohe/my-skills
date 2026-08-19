# Canonical 单源措辞纪律

> 防止文档漂移：关键措辞只在一处编辑，其他位置引用或链接。

## 核心原则

**单一编辑处**（Single Source of Truth）：对于会在多处出现的措辞（部署路径、触发关键词、技能调用名称），指定唯一编辑处，其他位置只引用或链接。

**目标**：避免改一处忘另一处，导致文档三方不一致。

---

## 措辞类型与唯一编辑处

| 措辞类型             | 唯一编辑处                         | 引用位置                                     | 传播方式                 |
| -------------------- | ---------------------------------- | -------------------------------------------- | ------------------------ |
| **部署路径**         | `README.md` 「分发与部署」段       | CONTEXT.md、USAGE.md、各 SKILL.md            | 文字引用或链接           |
| **技能 canonical name** | `skills-manifest.yaml` 的 name/path | 源码目录、manifest dependencies、结构说明 | 无 slash 的完整路径名 |
| **运行时调用名称**   | `skill_manifest.py` 的 deployment_name 规则与 contract | 各 SKILL.md 正文、README、USAGE、路由表 | slash + `deployment_name` |
| **路由规则**         | `0-router/SKILL.md`             | CLAUDE.md、README、USAGE 路由加载行          | 仅指针，不镜像路由表     |
| **技能触发关键词**   | 各技能 `SKILL.md` frontmatter desc | manifest、openai.yaml、README                | 变量式引用               |
| **完成标准模板**     | `writing-for-agents/SKILL.md`      | 各技能 SKILL.md 的"完成标准"段               | 按规范自行编写           |
| **ADR 模板**         | `1-plan/references/adr-format.md`  | 各 `docs/adr/NNNN-*.md`                      | 模板复制，不变后续不同步 |
| **Git 操作命令示例** | `5-git/SKILL.md`              | CLAUDE.md、USAGE.md                          | 链接引用                 |
| **测试策略**         | `vocabulary/tdd/SKILL.md`          | `2-implement/SKILL.md`                            | 文字引用（已落地 P0-3）  |

---

## 编写规范

### 1. 唯一编辑处的措辞模板

在唯一编辑处，用**清晰的标题或注释**标记"本段为唯一事实源"：

```markdown
## 分发与部署（唯一事实源）

my-skills 仓库通过 skills-manager 同步到 `~/.skills-manager/skills/`，
再通过 junction 部署至 `~/.claude/skills/` 和项目 `.claude/skills/`。
```

### 2. 引用处的写法

**禁止**：复制粘贴完整措辞（一旦原文改，引用处成僵尸）

```markdown
<!-- ❌ 错误示例 -->

部署路径是 ~/.skills-manager/skills/ → ~/.claude/skills/
```

**推荐**：引用或链接

```markdown
<!-- ✅ 正确示例 -->

部署路径见 [README 分发与部署段](../../README.md#分发与部署)。
```

或简化为：

```markdown
<!-- ✅ 简化引用 -->

部署通过 skills-manager 同步（详见 README）。
```

### 3. 路由只使用指针

CLAUDE.md 常驻内容必须小而稳定：

- 不含路由表；模板只保留工作哲学、记忆约定两个 H2。
- 若保留 `## 路由入口` 指针，只指向 `/0-router`。
- 不在 CLAUDE.md、README 或 USAGE 复制三路判定和场景路由表。
- 修改路由只编辑 `0-router/SKILL.md`；导航文档只更新技能存在性与一句职责。

---

## 常见违反场景与修复

| 违反场景                              | 问题                       | 修复                                                     |
| ------------------------------------- | -------------------------- | -------------------------------------------------------- |
| CONTEXT.md 和 README 各写一遍部署路径 | 双源，改一处另一处漂移     | 删除 CONTEXT 的详细路径，改为"见 README"                 |
| 2-implement 和 tdd 各写一遍测试策略        | 逐字重复（P0-3 已修）      | 测试策略归 tdd，2-implement 只定义命令发现与交接 |
| 三处写 0-router 的调用模型         | 三说法（P0-2 已修）        | 统一为 SKILL.md description，其他处引用                  |
| 正文把 canonical `vocabulary/tdd` 当 slash 调用 | canonical name 被误当运行时名称 | manifest dependency 保留 canonical，正文使用 `/tdd` |
| 安装命令散落 README/USAGE/各 SKILL    | 维护成本高，版本号易不同步 | 只在 README 写完整命令，其他处链接或简化引用             |

---

## 验证方法

### 手动检查

改动唯一编辑处后，用宿主内容搜索能力检查全库是否有遗留副本。例如：

```bash
# 示例：改了部署路径后，检查是否有其他地方硬编码了旧路径
rg "~/.skills-manager/skills/" -g "*.md" .
# 预期：仅在 README 唯一源出现，或在引用处以链接形式出现
```

### 自动检查

- `python scripts/validate_skills.py --check-claude-pointer --claude-md <path>`：目标不存在即失败；存在时要求 CLAUDE.md 只含路由指针且无 Fat 路由镜像。
- `python scripts/validate_skills.py`：manifest dependencies 按 canonical name 校验；技能目录、README、USAGE 与 `docs/governance/**/*.md` 的 slash 引用按 runtime deployment name 校验。反引号中的未知单段调用也会报错，已知宿主命令与系统路径走显式 allowlist。

后续可扩展技能名称一致性（manifest.name vs frontmatter.name vs openai.yaml）。

---

## 例外：模板不同步

某些内容是**模板复制后独立演化**，不属于镜像同步：

- ADR 文件：从 `1-plan/references/adr-format.md` 复制后，各 ADR 独立编辑
- 各技能的完成标准：从 `writing-for-agents` 规范生成后，各技能按自身场景定制

这些**不要求同步**，因为复制后是不同实例。

---

## 落地检查清单

改动唯一编辑处时，执行以下检查：

```markdown
- [ ] 确认当前文件是该措辞的唯一编辑处
- [ ] 搜索全库该措辞的其他出现，确认是引用而非副本
- [ ] 路由引用处只保留指针，不复制路由表
- [ ] 如果其他处有硬编码副本，改为引用或链接
- [ ] validator 通过
```

---

_本纪律吸收 mattpocock 的 install-block.md 模式：部署/触发措辞只写一处，防止三方漂移。_
