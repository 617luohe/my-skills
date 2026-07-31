# 场景：push 因网络失败

输入：
```
/noteall https://example.com/article
```

前置状态：远端不可达。

期望行为：
- 保留本地提交，不回滚
- 明确报告 commit hash 和失败原因
- 下一次运行先重试推送遗留提交，再开始新收录
