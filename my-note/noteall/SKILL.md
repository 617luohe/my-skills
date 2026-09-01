---
name: noteall
layer: my-note
description: >
  知识库唯一入口。接收本机路径、URL、自由文本或处理要求，整理进选定的 Obsidian Vault 并自动提交推送，
  编排 Intake→Curate→Publish 三阶段。触发：收录内容（路径/URL/文本）、记一笔、整理或维护既有笔记、
  把会议/日记/文章定型。
---

# noteall — 受控知识库唯一入口

主流程：**Intake（收录）→ Curate（整理）→ Publish（发布）**。启动时解析一次 Vault，整次运行保持不变。Manifest dependencies 为 `my-note/index-keeper`、`my-note/vault-publisher`。

## 〇、Vault 解析（每次启动首步）

1. 读取 `references/config.yaml` 的 `prefer_current_vault` 与 `vault_path`。
2. 若 `prefer_current_vault: true` 且当前目录含 `.obsidian/`，选当前目录；否则选 `vault_path`。
3. 校验所选路径存在且含 `.obsidian/`；失败即停止，不尝试其它目录。
4. 记录为 `{selected_vault}`；后续阶段与 Worker 只使用该路径。

## 一、输入识别

识别用户输入与处理倾向：

| 输入                                                           | 识别         | 处理                                   |
| -------------------------------------------------------------- | ------------ | -------------------------------------- |
| 本机文件路径（pdf/docx/md 等）                                 | 文件收录     | 复制原件到 `raw/`，走完整流水线        |
| URL/http/www                                                   | 来源收录     | 保存来源记录与整理笔记，不建无意义副本 |
| 自由文本                                                       | 文本捕获     | 捕获到 `0-Inbox/` 并整理               |
| 自由文本 + 「先记一下 / 极简捕获 / 快速记一笔」                | 极轻量捕获   | 见 §一·五（唯一窄例外，跳过流水线）    |
| 处理倾向（整理/纪要/阅读/日记/写文章/批量/索引/MOC/文件整理…） | 覆盖自动推断 | 见 §二、§三                            |

- 参数不足 → 一次一问分步盘问，不一次性抛出所有问题。
- 倾向优先于自动推断，但**不能覆盖 §四 安全不变量**（极轻量捕获的窄例外见 §一·五）。

## 一·五、极轻量捕获（唯一窄例外）

**触发**：自由文本 + 明确倾向「先记一下 / 极简捕获 / 快速记一笔 / 回头再整理」；用户只要记下想法，不要完整流水线。

**行为**：

1. 写入 `0-Inbox/YYYYMMDD-HHMM-主题.md`（frontmatter：`title`、`tags`（`type/idea`、`status/inbox`）、`created`、`source` 可选）。
2. Git 收尾：**只暂存并提交该捕获文件**（`git add <该文件>` + `git commit`），不 push；不用 `git add .`，不触碰其他未提交改动。
3. 不运行 Curate / Publish 全流程；捕获留待下一次 noteall 维护（批量整理 / 文件整理）处理。

**边界**：这是 §四 不变量 2（工作区不干净即停止）的唯一放宽 —— 仅针对本次捕获文件做最小提交，其余未提交改动保持原样。其余不变量不受影响。

## 二、三阶段流水线（默认收录）

### ① Intake — 收录

执行 `references/intake.md`：解析输入与倾向，验证所选 Vault 与 Git 前置状态，原件复制到 `raw/`，提取正文与元数据。

### ② Curate — 整理

执行 `references/curate.md`，并按需读取 `references/profiles.yaml`：判断目标笔记形态与目录，结构化、去重、建立 wikilink，更新必要 INDEX/MOC，归档 Vault 内原始副本到 `7-Sources/`。

### ③ Publish — 发布

执行 `references/publish.md`：校验改动范围与笔记完整性，只暂存本次 owned paths，commit，与远端同步并 push。失败时保留本地提交并报告。

## 三、维护模式

处理倾向为**批量整理 / 更新索引 / MOC 审计 / 文件整理 / 图谱健康检查 / 合规审计 / 断链与孤岛修复**时，跳过 Intake，直接执行 `references/maintain.md` → 进入 Publish。同样有 Git 收尾。

## 四、安全不变量（倾向与自动推断均不可覆盖）

1. Vault 解析或校验失败 → 停止。
2. Vault 工作区不干净 → 停止，不处理资料、不执行 Git 写操作。
3. 仅暂存本次流水线拥有的路径；**不用 `git add .`**。
4. 无实际变更 → 不创建空提交。
5. 远端冲突 → 停止并报告冲突文件，**不自动解决**。
6. push 失败 → 保留本地提交并报告 commit hash；下次运行先补推遗留提交。

## MUST 规则

1. **每次启动先解析并校验 Vault（§〇）。** 失败即停止。
2. **先识别输入与倾向，再编排。** 倾向优先于自动推断，但不覆盖 §四。
3. **文件操作一律以所选 Vault 为根。** 不向其它目录写入。
4. **中途取消（"算了"/"取消"）→ 退出，不继续。**
