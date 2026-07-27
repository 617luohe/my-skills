---
name: workflow-wrapup
layer: my-note
description: [内部] 收尾归档。将已处理文件从 raw/ 归档到 7-Sources/，更新项目状态，生成处理报告。由 noteall 路由器调度。
---

# workflow-wrapup — 收尾归档

4 阶段工作流「收尾阶段」：确认产出 → 归档原始文件 → 生成报告 → 建议后续。

## 一、处理流程

### Step 1 — 确认已完成工作
列出本次产出文件 + raw/ 中可归档的文件，让用户确认。

### Step 2 — 执行归档
- `raw/{subdir}/{file}` → `7-Sources/{project}/{subdir}/{file}`
- 目标目录不存在 → 询问是否创建
- 同名文件 → 询问覆盖/重命名
- 归档后 raw/ 变空 → 提示

### Step 3 — 收尾建议
输出报告（新建文件列表 + 归档文件列表 + 建议操作：更新 MOC/补充 wikilink/更新项目状态）

## 二、快捷模式

``/my-note/workflow-wrapup 归档 raw/xxx/ 到 7-Sources/xxx/`` → 直接执行不确认。

## 三、边界

- raw/ 为空 → 告知无需归档
- 文件被占用 → 建议手动处理
- 不确定归档位置 → 根据 domain 推断

## MUST 规则

1. **归档前必须确认产出清单。** 让用户确认哪些文件需要归档。
2. **同名文件冲突时必须询问。** 不静默覆盖。
3. **归档后 raw/ 为空时提示用户。**
