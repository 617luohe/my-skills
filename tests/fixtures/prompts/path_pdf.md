# 场景：仅输入本机 PDF 路径

输入：
```
/noteall C:\Users\Administrator\Downloads\report.pdf
```

期望行为：
- 复制原文件到 Vault `raw/`，外部原件不变
- 生成整理笔记
- Vault 内原始副本按规则归档到 `7-Sources/`
- 提交并推送，返回写入位置、处理摘要和 Git 结果
