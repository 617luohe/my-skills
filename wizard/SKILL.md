---
name: wizard
description: 生成交互式 bash 向导，带人走完只有人能做的步骤。触发：配置基础设施、设置凭据或 CI secrets、走陌生的第三方 dashboard、一次性迁移或切换（cutover）。不触发：agent 自己能做的步骤。
disable-model-invocation: false
---

# Wizard — 交互式向导

wizard 是 bash 脚本，一步步带人走完手动流程：自动开 URL、说清点什么、捕获值、写 `.env`、gh secret，每步确认、显示剩余步数。可能配置第三方服务、跑一次性迁移、把项目从 A 态搬到 B 态。

**核心**：[template.sh](template.sh) 已解决全部 UX（进度、确认门、跨平台开 URL 含 WSL、隐藏 secret 输入、幂等 `.env` upsert、`gh secret`/`gh variable` 写入、收尾摘要）。你只负责 **scope 流程 + 写 STAGES**。STAGES 标记以上是固定库，永不手改。

**生命周期**：默认 ephemeral——为单次运行而生，存 scratch 或 `scripts/`，用后即删。仅当用户想要可重复的 setup 路径时才 commit 进仓库。

## 流程

### 1. Scope 流程

先读仓库，不冷问：

- **setup**：`.env`、`.env.example`、`.env.*`、README、`docker-compose*`、框架配置、`.github/workflows/*`——每个 `secrets.*`/`vars.*` 引用都是一个 wizard 要产出的值
- **迁移/切换**：当前状态、目标状态、两者间的不可逆动作

然后给用户看有序阶段列表和各阶段产出的值，确认——可增、删、排序。

**完成条件**：每个阶段按序命名；每个捕获值都清楚 (a) 人从哪拿 (b) 写哪（`.env`、GH secret、both、nowhere——有些阶段是纯动作）(c) 是否 secret（隐藏输入）。

### 2. Map 每阶段路径

写清人走的精确路径：开哪个 URL、在那做什么、值在哪显示、填哪个变量。不确定当前 UI 或确切命令就明说并问用户或查文档——绝不发明可能不存在的步骤。

**完成条件**：每阶段可追踪到陌生人都能跟的明确指令。

### 3. Author

复制 [template.sh](template.sh) 到目标路径。用库函数（`stage`、`say`/`step`、`open_url`、`ask`/`ask_secret`、`write_env`、`set_secret`/`set_var`、`pause`/`confirm`）替换示例 stage，设 `TOTAL_STAGES` 与阶段数一致。守模板的规矩：**先开 URL 再要值**、secret 用 `ask_secret`、持久化值用 `write_env`、CI 真正需要的才 `set_secret`、不可逆动作前 `confirm`。每个 `stage` 清屏只留当前步——一步一个聚焦任务。STAGES 标记以上不动。

### 4. Verify + 交付

- `bash -n <script>`；有 shellcheck 就跑
- `chmod +x <script>`
- **不端到端自己跑**（会开浏览器 + 等人输入）——静态跟踪：每个值从步骤 1 捕获且落到步骤 1 说的位置；每个 `set_secret` 名与 CI 里 `secrets.*` 严格同名
- 告诉用户怎么跑。可重复的 setup 路径才 commit 并从 README 链接（下个人跑脚本，不问 AI）

## 触发分支（description 用）

1. 配置基础设施（provisioning）
2. 设置凭据或 CI secrets
3. 走陌生的第三方 dashboard
4. 一次性迁移或切换（cutover）

**不触发**：agent 自己做得完的步骤——能做就做。

## 与其它技能的关系

- **`0-启动`** — 脚手架后配 secrets 时可调
- **`2-开发`** — 执行中撞到仅人步骤时自动调起
- **`1-规划`** — 一次性迁移任务标 `[HITL]` 并注明用 wizard
- **`6-最后整理`** — 清理 ephemeral wizard 脚本
- **`5-版本管理`** — 用户要保留重复性 setup 路径时才 commit
