---
name: cleanupclaude
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
disable-model-invocation: false
---

# Cleanup Claude（cleanupclaude）

安全梳理 Claude Code 本地状态，减轻多 session 使用后的膨胀与卡顿，不丢连续性。

## 铁律

1. **默认只读。** 第一轮永远只跑 report 模式，不写任何文件、不做任何移动。
2. **先备份后变更。** apply 前先备份 `history.jsonl`；备份目录含私有元数据，不外发。
3. **归档不删除。** 会话/telemetry/cache 一律移动到 `~/.claude/archived/`，写 manifest
   并生成恢复脚本，绝不永久删除。
4. **当前会话自动豁免。** 从 Claude Code 会话内调用时，脚本自动识别当前会话
   （父进程链匹配会话注册表，cwd 兜底）并跳过它，apply 可直接执行、无需关闭
   Claude Code；无法识别当前会话（如终端手动运行）时，运行中仍拒绝，
   `--force`/`--wait-for-claude-exit` 可覆盖。
5. **绝不触碰项目上下文。** 项目目录下的 `memory/`、`CLAUDE.md`、`todos/`、`tasks/`、
   `skills/` 不归档、不修改。
6. **重要会话先 handoff。** 自动清理只归档超期（默认 10 天未动）的旧会话；
   用户明确想保留的会话，先产出 handoff 文档（`docs/handoffs/YYYY-MM-DD-topic.md`
   或仓库内约定位置）再归档。
7. **不杀进程、不删数据、不自动定期执行。** 只报告重进程；定时任务若做，只做报告型提醒。

> 与 cleanup skill 的分工：cleanup 管整机磁盘空间（"磁盘满了/清理空间"）；
> 本 skill 管 `~/.claude` 会话状态（"Claude Code 卡顿/会话太多"）。

## 定位脚本

本 skill 的脚本位于 skill 目录下 `scripts/keep_claude_fast.py`。运行方式：

```bash
python "<本 skill 目录>/scripts/keep_claude_fast.py"
```

skill 目录即本 SKILL.md 所在目录。若不确定，用 `where`/`find` 定位
`keep_claude_fast.py`，或让用户告知安装位置（默认在 `~/.claude/skills/cleanupclaude/`）。

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

### Step 3 — 自动清理（默认，无需确认）

**从 Claude Code 会话内调用时，脚本自动识别并跳过当前会话，直接执行安全清理**
（备份 → 归档超期旧会话 → 裁剪 history → 归档 telemetry/cache → 出报告）。
活动会话（其他正在运行的 session）与被锁定文件同样自动跳过，不会中断用户其他工作。
本会话不归档、不裁剪，用户对话上下文不受影响。

```bash
python "<skill 目录>/scripts/keep_claude_fast.py" --apply --archive-older-than-days 10 --history-keep-last 500
```

默认阈值 10 天 / 500 行；可按用户习惯调整（如 30 天 / 1000 行）。

- 若没有超期旧会话 → 说明状态健康，报告后给出维持建议（weekly report 提醒），结束。
- 若有超期旧会话 → 自动清理并出报告（Step 6）。
- 若用户想先人工确认（或脚本无法识别当前会话而拒绝）→ 停在报告，让用户决定。

### Step 4 — handoff（仅当用户想保留的旧会话将被归档时）

对用户还想继续的重要旧会话，先产出 handoff 文档并给出 reactivation prompt
（让新会话读文档即可续上）。模板要点：repo/分支、当前目标、已完成、改动文件、
已跑命令、已知问题、未决决策、下一步 3-7 条、禁区、reactivation prompt。
若用户未提及、或归档对象都是不再需要的旧会话，无需强制 handoff。

### Step 5 — 处理结果报告

apply 结束后脚本自动生成**处理结果报告**：`<backup-root>/cleanup-report-<stamp>.md`
（默认 `<用户文档目录>/Documents/Claude/claude-backups/`），并打印报告路径。

报告内容（结论先行）：

- **处理摘要**：释放量（projects 前后对比）、归档会话数与大小、history 裁剪行数、
  telemetry/cache 归档量
- **归档明细**：按项目列出归档会话数与 MB
- **跳过项**：活动会话 / 锁定文件 / 未超期会话
- **恢复方法**：`restore-claude-fast.py` 与 manifest 路径

在对话里向用户汇报报告要点（一段话结论 + 恢复方法），完整报告路径一并给出。
可提议 weekly/biweekly 报告型提醒（只读，永不自动 apply）。

## Apply 做了什么（向用户说明）

1. 检测运行中 Claude Code 与活动会话（`~/.claude/sessions/*.json` 注册表），运行中默认拒绝
2. 备份 `history.jsonl` 到 `~/Documents/Claude/claude-backups/cleanupclaude-*`
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

- **斜杠命令**：将以下内容存为 `~/.claude/commands/cleanupclaude.md`，即可用
  `/cleanupclaude` 触发本 skill 的只读报告流程：
  ```markdown
  ---
  description: 只读检查 Claude Code 本地状态（会话膨胀/卡顿分析）
  ---

  使用 cleanupclaude skill 执行一次只读检查并汇报，不自动 apply。
  ```
- **hooks（可选）**：`hooks/session-end-report.example.json` 是 SessionEnd 报告型 hook
  模板（合并进 `~/.claude/settings.json` 的 hooks 段启用）。hook 输出会计入会话，
  默认不启用。

## Anti-Patterns

- 把归档当删除；删用户会话/日志
- 在 Claude Code 运行中 apply（未经用户同意）
- 归档前不产出 handoff
- 碰项目级 `memory/`/`CLAUDE.md`
- 自动定期 apply（只允许报告型提醒）
- 承诺"更快"为必然结果；只表述为本地状态维护结果
