---
name: vision-skill
description: >
  通过 OpenCode Go 视觉 API 描述图片、截图和图片 URL。
  触发：用户附图、给图片路径或 URL、要求看图/读图，或消息中出现 [Image #N] / [Unsupported Image]。
allowed-tools: Bash(python *)
---

# Vision Skill — 图片描述（为纯文本模型补视觉）

当前后端是纯文本模型，本技能负责把图片交给视觉 API，再用返回描述作答。

## 强制规则

1. 以脚本输出为唯一事实源，图片理解一律走脚本。
2. 图片内容交给脚本解析，模型只转述脚本返回的描述。
3. 失败就如实报错。

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

截图或粘贴图没有明确路径时，先定位真实文件路径，再传给脚本。

## 配置

- **API key**：默认自动从 cc-switch 数据库读取（OpenCode Go 套餐）；也可设环境变量 `VISION_API_KEY` 覆盖
- **`VISION_MODEL`**：默认 `minimax-m3`（成本优先）
- **`VISION_API_URL`**：默认 `https://opencode.ai/zen/go/v1`

## 错误处理

- 无 key / 网络失败 / 图片过大：把 stderr 的错误信息原样报告用户。
- 输出为空：换 `--model qwen3.8-max` 重试一次，仍失败则如实报告。

## 完成标准

- 已定位真实图片路径或 URL 并调用脚本。
- 回答只基于脚本输出。
- 脚本失败时已原样报告错误。
