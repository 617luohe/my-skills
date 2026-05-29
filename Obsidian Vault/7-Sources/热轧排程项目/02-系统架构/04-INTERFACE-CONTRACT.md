# 接口契约（Socket 请求/响应）

本文面向联调与集成同学，定义外部可见接口行为。

## 1. 传输层约定

- 协议：TCP
- 编码：UTF-8
- 服务入口：`src/main.py`
- 单次请求处理：`recv(4096)` 读取一包后分支处理并回包
- 连接保持：处理后每 5 秒尝试发送 `Test`，断连则关闭

## 2. 请求报文契约

### 2.1 分支A：辊期重算（ROLL）

格式：
- `ROLL<roll_id>`
- `ROLL<roll_id>|<unit>`
- `ROLL<roll_id>|<unit>|<config_type>`

示例：
- `ROLL2026012201`
- `ROLL2026012201|1580`
- `ROLL2026012201|1580|thin`

字段说明：
- `roll_id`：辊期号（字符串）
- `unit`：可选产线标识（如 `1580` / `2250`）
- `config_type`：可选配置类型（如 `standard` / `thin` / `thick`）

### 2.2 分支B：标准产线

`main.py` 先取 `message[:4]` 作为产线标识，再按 `_` 拆分字符串。

有效标识（当前实现）：
- `1580`
- `2250`
- `xlsx`
- `1580_all`
- `2250_all`

常见格式：
- 标准：`158020252000`
- 两段：`1580_all`
- 三段（manual）：`1580_<id>_<板坯号列表>`

> 注意：`xlsx` 为特殊分支，实际处理路径仍由 `entry -> UnitProcessor.entrance()` 控制。

### 2.3 报文样例表（建议直接复用）

| 场景 | 请求样例 | 预期分支 |
|---|---|---|
| 标准排程 | `158020252000` | `entry -> entrance` |
| 统计模式 | `1580_all` | `entry -> entrance_statistics` |
| 人工计划 | `1580_20250526005_252A01309H0600,252A01359G0200` | `entry -> entrance_manual` |
| 辊期重算 | `ROLL2026012201|1580|thin` | `entry_roll_replay -> entrance_roll_replay` |

## 3. 路由契约

- `main.unit_choice`：
  - `message_str.startswith("ROLL")` -> `entry_roll_replay`
  - 其他 -> `entry`
- `entry.entry`：
  - `len(id)==3 and id!='all'` -> `entrance_manual`
  - `len(id)==3 and id=='all'` -> `entrance_statistics`
  - 其他 -> `entrance`

## 4. 响应契约

响应为 JSON 字符串（`message.py`），标准字段：

```json
{
  "message_content": "程序执行成功！ ...",
  "message_type": "执行成功"
}
```

字段说明：
- `message_type`：状态类型（实现中存在英文常量与中文文案混用，联调请按“成功/失败/缺失”语义解析）
- `message_content`：可读文本；统计模式下可能是 JSON 字符串文本

额外约束：
- `entry._sanitize_response` 会对 `message_content` 中单引号进行 SQL 安全化替换（`'` -> `''`）

## 5. 错误与边界

- 产线标识不合法：直接回 `Error`（非 JSON）
- 运行时异常：通常回 JSON 失败消息
- 辊期冲突：可能返回“跳过写库”类失败/警告消息

### 5.1 响应判定建议（集成侧）

1. 先判断是否为合法 JSON。  
2. 不是 JSON 且内容为 `Error`：按“请求格式/产线路由错误”处理。  
3. 是 JSON 时，再基于 `message_type` 与 `message_content` 做业务判定。  

### 5.2 `message_type` 兼容建议

由于存在英文常量与中文文案混用，建议做兼容映射：
- 成功：`Success` / `SUCCESS` / `执行成功`
- 失败：`Failure` / `FAILURE` / `执行失败`
- 缺失：`Missing` / `MISSING` / `缺失`

## 6. 联调最小样例

1) 发送 `158020252000`  
2) 期望回 JSON，包含 `message_type` / `message_content`  
3) 再发 `ROLL2026012201|1580` 验证重算链路  

### 6.1 联调通过标准

- 标准请求与 ROLL 请求都能返回可解析响应。
- 至少一条成功响应可关联到数据库写入结果（若环境允许写库）。
- 异常请求（如非法产线）能稳定复现 `Error`。

建议同时配合：
- `06-DEBUG-CHECKLIST.md`（联调检查）
- `05-TROUBLESHOOTING.md`（异常定位）
