---
name: vision-skill
description: >
  通过 OpenCode Go 视觉 API 为纯文本模型（DeepSeek 等）描述图片/截图/图片 URL。
  MUST trigger when user attaches an image (png/jpg/gif/webp/bmp), pastes an image path or image URL,
  asks to describe/read/see a screenshot or photo, or when [Image #N] / [Unsupported Image] appears in chat.
  Do NOT guess image contents — run the vision script instead.
when_to_use: 用户附带图片(png/jpg/gif/webp/bmp)、图片路径或 URL、要求描述/看懂截图/照片、消息中出现 [Image #N] 或 [Unsupported Image]
allowed-tools: Bash(python *)
---

# Vision Skill — 图片描述（为纯文本模型补视觉）

当前后端是纯文本模型（DeepSeek v4 flash），**没有视觉能力**。本技能是唯一视觉入口：把图片交给视觉 API 模型（OpenCode Go 套餐），返回结构化中文描述，模型只读描述作答。

## 强制规则

1. **绝不猜图**：面对图片输入，禁止凭文件名、上下文或经验推测图片内容。
2. **禁止直接读图**：不要用 Read 或其他工具读取二进制图片文件——你无法解析二进制数据。
3. **脚本是唯一入口**：任何图片理解需求一律运行脚本，以脚本输出的 description 为唯一依据。脚本报错就把错误原样转告用户，**禁止伪装成功**。

## 执行

用户提供图片时，定位真实文件路径或 URL，然后运行：

```bash
python "${CLAUDE_SKILL_DIR}/scripts/vision_describe.py" <图片路径或URL>
```

常用参数：

| 参数                  | 作用                             |
| --------------------- | -------------------------------- |
| `--model qwen3.8-max` | 换更强的视觉模型（更准、更贵）   |
| `--thinking`          | 开启模型推理（更准、更贵、更慢） |
| 多个路径              | 一次传多张图，逐张描述           |
| `--list-models`       | 列出 OpenCode Go 可用模型        |

截图/粘贴图没有明确路径时：先从剪贴板或临时目录定位真实文件路径，再传路径给脚本。

## 配置

- **API key**：默认自动从 cc-switch 数据库读取（OpenCode Go 套餐）；也可设环境变量 `VISION_API_KEY` 覆盖
- **`VISION_MODEL`**：默认 `minimax-m3`（成本优先）
- **`VISION_API_URL`**：默认 `https://opencode.ai/zen/go/v1`

## 触发分支

1. 用户附带图片文件、图片路径或图片 URL
2. 消息中出现 `[Image #N]` / `[Unsupported Image]` 占位符
3. 用户要求"描述 / 看懂 / 读取 / 看看这张图、截图、照片"

**不触发**：纯文本、代码、文档内容——那是模型本职，不需要视觉。

## 错误处理

- 无 key / 网络失败 / 图片过大：把 stderr 的错误信息原样报告用户。
- 输出为空：换 `--model qwen3.8-max` 重试一次，仍失败则如实报告。

## 与其它技能的关系

- `/2-开发` — 写代码时遇到截图/UI 图需求可调
- `/4-调试` — 分析报错截图
