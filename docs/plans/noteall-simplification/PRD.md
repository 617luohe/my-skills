# PRD: Noteall 精简与固定知识库自动化

> 依据 `ai-vibe-coding-config/docs/analysis/my-note-simplification-handoff.md` 的 T001-T006 实施。

## Problem Statement

当前 noteall 是"多类型路由"：按意图/资料类型分派到 14 个子 skill，入口心智负担重；Vault 解析会探测当前目录并可能误写当前项目；收录后没有自动 Git 收尾。用户想要单一入口、固定 Vault、整理后自动发布。

## Solution

把 noteall 重构为**唯一入口的三阶段流水线**：

1. **Intake / 收录** — 解析输入（路径/URL/文本）与处理倾向，验证固定 Vault 与 Git 前置状态；本机文件复制到 `raw/`，URL/文本形成来源记录。
2. **Curate / 整理** — 判断目标笔记形态与目录，执行结构化、去重、wikilink、索引；归档 Vault 内原始副本。内容类型差异由 profile 承担。维护倾向（批量/索引/MOC/文件整理）走维护模式，跳过 Intake。
3. **Publish / 发布** — 校验改动范围，只暂存本次流水线 owned paths，commit，与远端同步并 push；失败保留本地提交并报告。

固定使用 `C:\Users\Administrator\Documents\Obsidian Vault`，校验失败即停止，不回退当前目录。

## User Stories

1. 用户只输入 PDF 路径 → 复制到 `raw/`，生成笔记，归档，提交并推送。
2. 用户输入 URL → 保存来源与整理笔记，不创建无意义文件副本。
3. 用户输入路径并带处理倾向（如"只提取行动项"）→ 按倾向处理，不走默认完整摘要。
4. 用户说"更新索引 / 整理知识库 / 批量整理 / MOC 审计" → 走维护模式，同样有 Git 收尾。
5. 同名来源重复收录 → 询问更新/另存/跳过，不静默覆盖。
6. Vault 开始时有未提交改动 → 停止，不处理资料，不执行 Git。
7. 远端可自动合并 → 同步后继续；远端冲突 → 停止，报告冲突文件。
8. push 因网络失败 → 保留本地提交并报告 hash；下次运行先补推遗留提交。

## Implementation Decisions

### 目录结构（my-skills 内）

```
my-note/noteall/                    # 唯一用户入口（invocation: user）
  SKILL.md                          # 输入识别 + 处理倾向解析 + 三阶段编排 + 维护模式
  references/
    config.yaml                     # 唯一固定 Vault 路径（单一配置值）
    profiles.yaml                   # meeting/reading/journal/article profile
    intake.md                       # Intake 阶段指令
    curate.md                       # Curate 阶段指令（compose/polish/atomic/索引/归档）
    maintain.md                     # 维护模式指令（批量/MOC/文件整理/索引审计）
    publish.md                      # Publish 阶段指令（调用 vault-publisher）
my-note/vault-publisher/            # 内部 Worker（invocation: model，不可独立触发）
  SKILL.md                          # Publish 阶段指令 + 脚本调用契约
  scripts/publish_vault.py          # 确定性 Git 状态机
tests/
  test_publish_vault.py             # 临时 git 仓库故障注入测试
  fixtures/prompts/                 # 测试提示（6 个场景）
```

### 接口要点

- `publish_vault.py` 状态机：`validate_vault → require_clean_worktree → fetch_remote → sync_remote → retry_pending_push → stage_owned_paths → commit → push`。
- 不变量：固定仓库之外不执行 Git；不用 `git add .`；不建空提交；冲突不自动解决；push 失败不回滚本地提交；commit 信息不含敏感正文。
- 提交信息：`notes(<type>): ingest <normalized-title>`；批量 `notes(batch): curate <count> sources`。
- `profiles.yaml` 只描述类型差异（提取字段、目标目录、模板）；文件复制、来源记录、链接、索引、Git 收尾由统一流水线承担。
- `config.yaml` 是 Vault 路径唯一来源；noteall 读取后传入 publisher 脚本，脚本不硬编码路径（便于测试）。
- `skills-manifest.yaml`：noteall 依赖改为仅 `[my-note/vault-publisher]`；14 个旧 skill 条目移除。

## Testing Decisions

- 用 pytest + `tmp_path` 临时 git 仓库测试 `publish_vault.py`，不在真实 Vault 上做故障注入。
- 覆盖场景：干净提交、脏工作区停止、远端 fast-forward、远端冲突停止、push 失败保留本地提交、无变更不建空提交、遗留提交补推。
- 测试提示集 `tests/fixtures/prompts/` 覆盖 6 个验收场景（路径/URL/文本/带倾向/脏工作区/push 失败）。
- 只测外部行为（退出码、提交存在、远端状态），不测内部实现细节。

## Out of Scope

- 不修改真实 Vault 现有改动，不处理 8 个未提交文件。
- 不做跨仓库镜像同步（handoff T007，延后）。
- 不做真实 Vault 小范围验收（handoff T008，需用户先清理 Vault 并另行授权）。
- 不创建新的 slash command。
- 不改变通用 `/5-版本管理` 的授权规则。

## Further Notes

- 14 个旧 skill 目录在 T006 删除，能力吸收进 references/profiles，git 历史可回溯。
- 与 CONTEXT.md 术语一致：Noteall、固定知识库、收录、整理、发布、处理倾向、处理 Profile、维护模式、内部 Worker、流水线拥有路径、遗留提交。
