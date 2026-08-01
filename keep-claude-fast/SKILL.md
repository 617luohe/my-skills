---
name: keep-claude-fast
description: >
  Claude Code 本地状态安全梳理（卡顿/膨胀治理）。在以下场景使用：用户说"Claude Code
  卡顿/变慢/打开多个会话很卡""会话太多/历史太长""~/.claude 太大了""清理 Claude 会话/
  历史/缓存""resume 列表太长""多 agent 占用资源高"；或 Claude Code 多 session 并行后
  明显变慢、磁盘占用膨胀、启动/搜索变慢时。提供默认只读的 report，backup 先行，
  apply 时归档旧会话而非删除、裁剪 history.jsonl 死条目、归档 telemetry/cache，
  全程 manifest + 恢复脚本可回滚。绝不触碰项目级 memory/ 与 CLAUDE.md。
  注意：整机磁盘满/空间不足请走 cleanup skill；本 skill 只管 ~/.claude。
metadata:
  short-description: "Claude Code 会话状态安全梳理（报告/备份/归档）"
---

# Keep Claude Fast

安全梳理 Claude Code 本地状态，减轻多 session 使用后的膨胀与卡顿，不丢连续性。

## 铁律

1. **默认只读。** 第一轮永远只跑 report 模式，不写任何文件、不做任何移动。
2. **先备份后变更。** apply 前先备份 `history.jsonl`；备份目录含私有元数据，不外发。
3. **归档不删除。** 会话/telemetry/cache 一律移动到 `~/.claude/archived/`，写 manifest
   并生成恢复脚本，绝不永久删除。
4. **运行中禁止变更。** 检测到 Claude Code 进程/活动会话时，apply 默认拒绝；
   除非用户明确同意 `--force` 或 `--wait-for-claude-exit`。
5. **绝不触碰项目上下文。** 项目目录下的 `memory/`、`CLAUDE.md`、`todos/`、`tasks/`、
   `skills/` 不归档、不修改。
6. **apply 前先 handoff。** 对用户还想继续的重要会话，先产出 handoff 文档
   （`docs/handoffs/YYYY-MM-DD-topic.md` 或仓库内约定位置），再归档。
7. **不杀进程、不删数据、不自动定期执行。** 只报告重进程；定时任务若做，只做报告型提醒。

> 与 cleanup skill 的分工：cleanup 管整机磁盘空间（"磁盘满了/清理空间"）；
> 本 skill 管 `~/.claude` 会话状态（"Claude Code 卡顿/会话太多"）。

## 定位脚本

本 skill 的脚本位于 skill 目录下 `scripts/keep_claude_fast.py`。运行方式：

```bash
python "<本 skill 目录>/scripts/keep_claude_fast.py"
```

skill 目录即本 SKILL.md 所在目录。若不确定，用 `where`/`find` 定位
`keep_claude_fast.py`，或让用户告知安装位置（默认在 `~/.claude/skills/keep-claude-fast/`）。

## 工作流

### Step 1 — 只读报告（必须第一步）

```bash
python "<skill 目录>/scripts/keep_claude_fast.py"
```

如用户要求细节（UUID/路径/进程详情），加 `--details`。若用户只想要摘要，不加。

### Step 2 — 汇报（结论先行）

按以下要点给摘要：
- 项目会话占用：哪个项目最大、会话文件数
- 最大的几个会话、超过保留期（默认 10 天）的旧会话候选数
- `history.jsonl` 行数；telemetry/cache/file-history/shell-snapshots 大小
- 当前运行的 Claude Code 进程数与活动会话数（= 卡顿的运行时成本）

### Step 3 — 判断是否需要 apply

- 若没有超期旧会话、没有明显膨胀 → 说明状态健康，给出维持建议（weekly report 提醒），结束。
- 若有超期旧会话 → 建议 apply，但先处理 handoff（铁律 6）。

### Step 4 — handoff（apply 前）

对用户还想继续的重要会话，产出 handoff 文档并给出 reactivation prompt（让新会话
读文档即可续上）。模板要点：repo/分支、当前目标、已完成、改动文件、已跑命令、
已知问题、未决决策、下一步 3-7 条、禁区、reactivation prompt。

### Step 5 — apply（用户明确要求后）

提醒用户：**关闭 Claude Code（或接受等待/`--force`）**，然后执行：

```bash
python "<skill 目录>/scripts/keep_claude_fast.py" --apply --archive-older-than-days 10 --history-keep-last 500
```

默认阈值 10 天 / 500 行；可按用户习惯调整（如 30 天 / 1000 行）。

### Step 6 — 验证与收尾

```bash
python "<skill 目录>/scripts/keep_claude_fast.py"
```

对比前后 `projects_size_mb` / `history_rows`；确认 `archived/` 大小；告知用户
恢复方法：备份目录下 `restore-claude-fast.py` 一键回滚。
可提议 weekly/biweekly 报告型提醒（只读，永不自动 apply）。

## Apply 做了什么（向用户说明）

1. 检测运行中 Claude Code 与活动会话（`~/.claude/sessions/*.json` 注册表），运行中默认拒绝
2. 备份 `history.jsonl` 到 `~/Documents/Claude/claude-backups/keep-claude-fast-*`
3. 归档超期会话：`<uuid>.jsonl` + 同名会话目录 → `~/.claude/archived/<项目>/<stamp>/`
4. 写 `moved-items.jsonl` manifest + `restore-claude-fast.py` 恢复脚本
5. 从 `history.jsonl` 移除已归档会话条目并裁剪到最近 N 行（resume 列表不再有死条目）
6. 归档 `telemetry/` 与 `cache/`

**不处理**（只报告）：`plugins/`、`hooks/`、`file-history/`、`shell-snapshots/`。

## 安全边界（编程约束）

- report/backup-only 之外的所有写操作只发生在 `--apply` 分支。
- 会话识别仅匹配 `<uuid>.jsonl` 及其同名目录；其余文件一律不动。
- 被系统锁定（文件占用）的会话自动跳过并报告，不重试强移。
- 活动会话（注册表 pid 存活）跳过；死 pid 的注册条目不构成保护。
- 输出默认伪匿名；`--details` 才显示 UUID/路径。

## 可选集成

- **斜杠命令**：将以下内容存为 `~/.claude/commands/keep-claude-fast.md`，即可用
  `/keep-claude-fast` 触发本 skill 的只读报告流程：
  ```markdown
  ---
  description: 只读检查 Claude Code 本地状态（会话膨胀/卡顿分析）
  ---
  使用 keep-claude-fast skill 执行一次只读检查并汇报，不自动 apply。
  ```
- **hooks（可选）**：`hooks/session-end-report.example.json` 是 SessionEnd 报告型 hook
  模板（合并进 `~/.claude/settings.json` 的 hooks 段启用）。hook 输出会计入会话，
  默认不启用。

## 测试

```bash
python "<skill 目录>/tests/smoke_test.py"   # 黑盒全链路断言，约 30 秒
```

## Anti-Patterns

- 把归档当删除；删用户会话/日志
- 在 Claude Code 运行中 apply（未经用户同意）
- 归档前不产出 handoff
- 碰项目级 `memory/`/`CLAUDE.md`
- 自动定期 apply（只允许报告型提醒）
- 承诺"更快"为必然结果；只表述为本地状态维护结果
