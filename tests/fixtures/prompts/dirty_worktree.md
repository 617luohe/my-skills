# 场景：Vault 工作区有未提交改动

输入：
```
/noteall C:\Users\Administrator\Downloads\report.pdf
```

前置状态：本次所选 Vault 工作区存在未提交改动。

期望行为：
- 立即停止，不处理资料
- 不执行任何 Git 写操作
- 明确提示用户先清理或提交 Vault 现有改动
