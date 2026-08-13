# 路由意图 eval 基线

每个 prompt 以 frontmatter 声明 `expected`；不调用技能的直接路径另声明 `router_marker`。pytest 只校验 metadata 可解析、runtime skill 存在，以及 canonical router 包含目标或 marker，不实现第二份路由分类器。

`trigger-evals.json` 保存真实正例与近似负例；pytest 校验其 schema、目标技能和边界覆盖。发布前应由固定宿主/模型多次运行该集合，记录命中率；模型结果有波动，不进入阻断式 CI。

| 文件 | 用户说法 | 预期技能 |
|------|----------|----------|
| plan.md | 规划这个新功能 | `/1-规划` |
| develop.md | 帮我实现这个模块 | `/2-开发` |
| review.md | 检查一下这次改动 | `/3-检查` |
| debug.md | 这个 bug 难复现，找根因 | `/4-调试` |
| issue.md | 明确只建单且创建前确认 | `/issue-reporting` |
| architecture.md | 架构评估但不落盘 | 只读聊天调查 |
| direct.md | 明确、低影响、可逆 | 直接做 + 验证 |
| noteall.md | 把这篇 PDF 收录进知识库 | `/noteall` |
