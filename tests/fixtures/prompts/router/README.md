# 路由意图 eval 基线

每个 prompt 以 frontmatter 声明 `expected`；不调用技能的直接路径另声明 `router_marker`。pytest 只校验 metadata 可解析、runtime skill 存在，以及 canonical router 包含目标或 marker，不实现第二份路由分类器。

语义路由是否正确仍需人工或模型 eval：读 prompt，判断预期是否合理。

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
