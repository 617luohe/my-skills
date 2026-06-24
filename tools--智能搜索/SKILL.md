---
name: tools--智能搜索
description: 基于 opencli 命令的智能搜索路由器。当用户想要搜索、查询、查找或研究信息时使用，尤其涉及指定网站、社交媒体、技术资料、新闻、购物、旅游、求职、金融或中文内容时务必触发。使用场景包括"搜一下X"、"查查Y"、"找找Z的资料"、"搜索XX平台"。
---

# 智能搜索路由器

根据话题和场景，将查询路由到最佳的 opencli 搜索源。

## 强制预检

每次使用前：
1. 运行 `opencli list -f yaml`
2. 用 live registry 确认候选站点存在，检查 strategy、browser、domain
3. 选定站点后运行 `opencli <site> -h` 查看子命令
4. 锁定子命令后运行 `opencli <site> <command> -h` 查看参数

**不要硬编码参数**，以 `-h` 实时输出为准。

## 路由规则

1. 用户明确指定网站 → 直接用
2. 用户未指定 → 优先选 1 个 AI 源：grok / doubao / gemini 三选一
3. AI 返回不足或需原始数据时 → 补充 1-2 个专用源

## 频率限制

- **AI 站点**：同一问题内每个最多 1 次
- **非 AI 站点**：默认最多 2 次
- 第 2 次必须加限定条件（时间/地区/类别/排序）
- 不进行第 3 次；信息仍不足则停止并说明缺口
- 报错/超时/反爬也算 1 次，不无限重试

## 查询结束汇报

每次回答末尾追加搜索摘要：
```
搜索摘要
- 网站：<site> | 查询词：<term> | 次数：<n>
- 已跳过：<site>，原因：达到频率上限
```

## 参考原始 skill

基于 [jackwener/opencli@smart-search](https://github.com/jackwener/opencli)，完整文件位于 `reference-skills/smart-search/`。
