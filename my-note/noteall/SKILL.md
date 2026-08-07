---
name: noteall
layer: my-note
description: >
  知识库唯一入口。接收本机路径、URL、自由文本或处理要求，整理进固定 Obsidian Vault 并自动提交推送，
  编排 Intake→Curate→Publish 三阶段。触发（知识库强信号词）：note、笔记、知识库、Obsidian、Vault、
  收录、归档、索引、MOC、会议纪要、日记、阅读、路径/URL 收录、批量整理、写文章。
disable-model-invocation: true
---

# noteall — 固定知识库唯一入口

主流程：**Intake（收录）→ Curate（整理）→ Publish（发布）**。所有产出写入固定 Vault。

## 〇、固定 Vault（每次启动首步）

1. 读取 `references/config.yaml` 的 `vault_path` —— 这是唯一允许操作的固定知识库。
2. 校验：路径存在，且含 `.obsidian/` 目录。
3. 校验失败 → 立即停止并提示；**绝不回退到当前工作目录**。

## 一、输入识别

识别用户输入与处理倾向：

| 输入 | 识别 | 处理 |
|------|------|------|
| 本机文件路径（pdf/docx/md 等） | 文件收录 | 复制原件到 `raw/`，走完整流水线 |
| URL/http/www | 来源收录 | 保存来源记录与整理笔记，不建无意义副本 |
| 自由文本 | 文本捕获 | 捕获到 `0-Inbox/` 并整理 |
| 处理倾向（整理/纪要/阅读/日记/写文章/批量/索引/MOC/文件整理…） | 覆盖自动推断 | 见 §二、§三 |

- 参数不足 → 一次一问分步盘问，不一次性抛出所有问题。
- 倾向优先于自动推断，但**不能覆盖 §四 安全不变量**。

## 二、三阶段流水线（默认收录）

### ① Intake — 收录
执行 `references/intake.md`：解析输入与倾向，验证固定 Vault 与 Git 前置状态，原件复制到 `raw/`，提取正文与元数据。

### ② Curate — 整理
执行 `references/curate.md`，并按需读取 `references/profiles.yaml`：判断目标笔记形态与目录，结构化、去重、建立 wikilink，更新必要 INDEX/MOC，归档 Vault 内原始副本到 `7-Sources/`。

### ③ Publish — 发布
执行 `references/publish.md`：校验改动范围与笔记完整性，只暂存本次 owned paths，commit，与远端同步并 push。失败时保留本地提交并报告。

## 三、维护模式

处理倾向为**批量整理 / 更新索引 / MOC 审计 / 文件整理 / 图谱健康检查**时，跳过 Intake，直接执行 `references/maintain.md` → 进入 Publish。同样有 Git 收尾。

## 四、安全不变量（倾向与自动推断均不可覆盖）

1. 固定 Vault 校验失败 → 停止。
2. Vault 工作区不干净 → 停止，不处理资料、不执行 Git 写操作。
3. 仅暂存本次流水线拥有的路径；**不用 `git add .`**。
4. 无实际变更 → 不创建空提交。
5. 远端冲突 → 停止并报告冲突文件，**不自动解决**。
6. push 失败 → 保留本地提交并报告 commit hash；下次运行先补推遗留提交。

## MUST 规则

1. **每次启动先校验固定 Vault（§〇）。** 失败即停止。
2. **先识别输入与倾向，再编排。** 倾向优先于自动推断，但不覆盖 §四。
3. **文件操作一律以固定 Vault 为根。** 不污染当前项目目录。
4. **中途取消（"算了"/"取消"）→ 退出，不继续。**
