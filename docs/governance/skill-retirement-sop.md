# Skill 退役标准操作流程（SOP）

> 本 SOP 确保技能退役时：①用户知道替代方案；②skills-manager 同步清除运行时副本；③历史可追溯。

## 退役触发条件

满足以下任一条件时，技能进入退役流程：

- 功能被新技能完全取代
- 维护成本 > 使用价值（使用频率极低且复杂度高）
- 设计失败，无法修复（架构性缺陷）

## 退役标准流程

### 1. manifest 标注（机器可检测）

在 `skills-manifest.yaml` 中：

```yaml
- name: old-skill-name
  status: deprecated # stable → deprecated
  deprecated_note: "Replaced by runtime deployment name NEW_NAME. Reason: clearer scope separation. Migration: rename calls to NEW_NAME with a leading slash."
  invocation: user # deprecated 技能禁止模型自动调用
```

**必填字段**：

- `deprecated_note`: 必须包含替代方案（如果有）和迁移指引
- `invocation: user`: deprecated 技能不可模型自动调用

Manifest 中的技能名与 dependencies 使用 canonical name；迁移说明里的 slash 调用使用替代技能的 runtime `deployment_name`。

### 2. SKILL.md 标注（人类可读）

在 SKILL.md 顶部 frontmatter 后立即加警告块：

```markdown
> **⚠️ DEPRECATED**: This skill has been retired. Use the replacement runtime deployment name with a leading slash.
> See [CHANGELOG.md](../../CHANGELOG.md#yyyy-mm-dd---skill-retirement) for details.
```

### 3. CHANGELOG 记录（历史追溯）

在 `CHANGELOG.md` 的 `[Unreleased]` 或日期段下：

```markdown
#### Deprecated

- **old-skill-name**: Replaced by the documented runtime deployment name. Reason: [简述原因]. Migration: [迁移步骤]
```

### 4. 同步与文档清理检查清单

**文档**（避免路由仍指向旧技能）：

- [ ] `README.md` 的技能清单：删除或标注 deprecated
- [ ] `USAGE.md` 的索引表：删除或移至 deprecated 段
- [ ] `CLAUDE.md`：保持 `/0-询问luohe` 指针，不加入技能级路由
- [ ] `0-询问luohe/SKILL.md`：删除旧技能条目或改指向替代者
- [ ] `CONTEXT.md`（如有）：删除对该技能的引用

### 5. 验证退役完整性

运行以下检查：

```bash
# 1. validator 通过（deprecated 状态 + deprecated_note + invocation user）
python scripts/validate_skills.py

# 2. 搜索遗留引用（排除 deprecated skill 自身的 SKILL.md 和 CHANGELOG）
grep -r "old-skill-name" --include="*.md" --exclude="SKILL.md" --exclude="CHANGELOG.md" .
# 预期：仅在 CHANGELOG/README deprecated 段出现，或无结果

# 3. 权威源 push 后，skills-manager 同步至运行时（用户环境自行 update）
```

### 6. 用户通知（可选）

如果该技能有已知用户，发送迁移通知：

- 替代方案
- 破坏性变更（如果有）
- 迁移时间窗口（建议至少 1 个月缓冲期）

---

## 退役后的文件处理

**保留在 my-skills/**：deprecated 技能的 `SKILL.md` 和目录保留，不删除。原因：

- 已部署到用户环境的技能可能仍在使用
- CHANGELOG 历史引用需要文件存在
- 用户需要时间迁移

**删除时机**：下次 major version bump 时，批量清理已 deprecated ≥6 个月的技能。

---

## 退役检查清单总结

```markdown
- [ ] manifest: status=deprecated, deprecated_note 已填, invocation=user
- [ ] SKILL.md: 顶部 DEPRECATED 警告块
- [ ] CHANGELOG: 记录退役原因和替代方案
- [ ] README: 删除或标注 deprecated
- [ ] USAGE: 删除或移至 deprecated 段
- [ ] CLAUDE.md: 仅保留路由指针，无技能级路由镜像
- [ ] 0-询问luohe: 快速判断表清理
- [ ] validator: 0 error/0 warning
- [ ] 遗留引用检查: grep 无意外引用
```

---

## 示例：cleanup skills 退役记录（参考）

2026-08-07，`cleanup` 和 `cleanupclaude` 技能退役：

- **原因**：职责被 `0--neat-freak` 完全覆盖，且边界更清晰
- **迁移**：所有旧 cleanup 调用改为 `/0--neat-freak`
- **执行**：manifest 标注 deprecated → SKILL.md 警告块 → CHANGELOG 记录 → 路由表清理 → validator 通过
- **结果**：技能目录保留但标注 deprecated，分发层遗留链接已清理

---

## 示例：v1.3.0 硬删除（2026-08-12）

与 deprecated 保留目录不同，以下 4 技能因低频/冗余**直接从 manifest 删除**（非 deprecated 过渡）：

| 技能 | 替代 |
|------|------|
| `multi-worker` | 主流程顺序开发；Cursor 内置多 agent |
| `leader` | 对话直接描述任务 |
| `0--explore` | 只读调查 `docs/analysis/` 或 `/1-规划` |
| `0--tokenless` | CLAUDE.md「工作哲学·沟通」 |

**执行**：manifest 删条目 → 删技能目录 → CHANGELOG [1.3.0] → 路由/CLAUDE/运行时/父仓库文档全量清理 → 父仓库 `docs/analysis/retired-skills-v1.3.0.md` 索引。

**与 deprecated 流程差异**：无 SKILL.md 警告块（目录已删）；历史证据保留在 CHANGELOG + 分析文档头注。

---

_本 SOP 遵循 mattpocock 的退役纪律：标注 → 记录 → 清理 → 保留目录，确保历史可追溯且用户有迁移路径。_
