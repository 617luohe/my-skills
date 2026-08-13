# 场景：路径 + 处理倾向

输入：
```
/noteall 整理 C:\Users\Administrator\Downloads\meeting.docx，只提取决定和行动项
```

期望行为：
- 按处理倾向执行（meeting profile），只提取 decisions 和 action_items
- 不走默认完整摘要流程
- 倾向不能覆盖安全不变量（所选 Vault、干净工作区、受控暂存、冲突停止）
- 提交并推送
