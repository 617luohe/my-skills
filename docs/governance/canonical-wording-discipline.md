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
| **技能调用名称**     | 各技能 `SKILL.md` frontmatter name | manifest、openai.yaml、README、USAGE、路由表 | 变量式引用（`/name`）    |
| **路由规则**         | `0-询问luohe/SKILL.md` description | CLAUDE.md、README、USAGE 路由加载行          | 镜像同步（声明来源）     |
| **技能触发关键词**   | 各技能 `SKILL.md` frontmatter desc | manifest、openai.yaml、README                | 变量式引用               |
| **完成标准模板**     | `writing-for-agents/SKILL.md`      | 各技能 SKILL.md 的"完成标准"段               | 按规范自行编写           |
| **ADR 模板**         | `vocabulary/domain-modeling/ref/`  | 各 `docs/adr/NNNN-*.md`                      | 模板复制，不变后续不同步 |
| **Git 操作命令示例** | `5-版本管理/SKILL.md`              | CLAUDE.md、USAGE.md                          | 链接引用                 |
| **测试策略**         | `vocabulary/tdd/SKILL.md`          | `2-开发/SKILL.md`                            | 文字引用（已落地 P0-3）  |

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

### 3. 镜像同步的特殊处理

某些场景需要完整镜像（如 CLAUDE.md 速查表是 0-询问luohe 的常驻版本）：

- **在镜像处声明来源**：`> 本表是 /0-询问luohe 的常驻镜像。改路由只改 0-询问luohe/SKILL.md，再同步此处。`
- **修改时先改唯一源，再镜像**：改 0-询问luohe → 提交 → 同步 CLAUDE.md → 提交
- **validator 可选检查**：未来可增加镜像一致性校验

---

## 常见违反场景与修复

| 违反场景                              | 问题                       | 修复                                                     |
| ------------------------------------- | -------------------------- | -------------------------------------------------------- |
| CONTEXT.md 和 README 各写一遍部署路径 | 双源，改一处另一处漂移     | 删除 CONTEXT 的详细路径，改为"见 README"                 |
| 2-开发 和 tdd 各写一遍测试策略        | 逐字重复（P0-3 已修）      | 测试策略归 tdd，2-开发 改为"按 /vocabulary/tdd 策略执行" |
| 三处写 0-询问luohe 的调用模型         | 三说法（P0-2 已修）        | 统一为 SKILL.md description，其他处引用                  |
| 安装命令散落 README/USAGE/各 SKILL    | 维护成本高，版本号易不同步 | 只在 README 写完整命令，其他处链接或简化引用             |

---

## 验证方法

### 手动检查

改动唯一编辑处后，搜索全库该措辞是否有遗留副本：

```bash
# 示例：改了部署路径后，检查是否有其他地方硬编码了旧路径
grep -r "~/.skills-manager/skills/" --include="*.md" .
# 预期：仅在 README 唯一源出现，或在引用处以链接形式出现
```

### 自动检查（未来）

可扩展 `validate_skills.py` 增加：

- 镜像一致性检查（CLAUDE.md 路由表 vs 0-询问luohe）
- 技能名称一致性（manifest.name vs frontmatter.name vs openai.yaml）

---

## 例外：模板不同步

某些内容是**模板复制后独立演化**，不属于镜像同步：

- ADR 文件：从 `vocabulary/domain-modeling/references/adr-format.md` 复制后，各 ADR 独立编辑
- 各技能的完成标准：从 `writing-for-agents` 规范生成后，各技能按自身场景定制

这些**不要求同步**，因为复制后是不同实例。

---

## 落地检查清单

改动唯一编辑处时，执行以下检查：

```markdown
- [ ] 确认当前文件是该措辞的唯一编辑处
- [ ] 搜索全库该措辞的其他出现，确认是引用而非副本
- [ ] 如果是镜像同步（如 CLAUDE.md），同步并提交
- [ ] 如果其他处有硬编码副本，改为引用或链接
- [ ] validator 通过
```

---

_本纪律吸收 mattpocock 的 install-block.md 模式：部署/触发措辞只写一处，防止三方漂移。_
