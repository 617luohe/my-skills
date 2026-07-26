# Planning Rules

## Frontier Algorithm

规划任务时采用**前沿推进算法**（frontier expansion）：

1. **起点**：从用户需求明确的边界（需求文档、API 接口、数据模型）开始
2. **扩展**：识别下一层依赖——每个已定义的模块会暴露新的未定义边界
3. **优先级**：优先处理阻塞后续工作的模块（如数据层 schema、核心领域实体）
4. **停止条件**：所有模块的输入输出接口明确，实现细节可延后

### 示例

```
需求：用户登录功能
├─ 前沿 1：API 接口（POST /login）
│   └─ 暴露依赖：身份验证服务、会话管理
├─ 前沿 2：身份验证服务
│   └─ 暴露依赖：用户数据访问层、密码哈希算法
├─ 前沿 3：用户数据访问层
│   └─ 暴露依赖：User 表 schema
└─ 终止：所有模块接口明确
```

## Context Caching Rules

CONTEXT.md 设计遵循缓存友好原则（仅包含领域术语表）：

1. **不变部分**：领域术语定义（高缓存命中）
2. **更新策略**：
   - 新增领域术语 → 追加到术语表
   - 澄清歧义 → 在对应术语下补充辨析
   - 架构决策 → 独立记录到 `docs/adr/NNNN-title.md`

## ADR Format

架构决策记录在 `docs/adr/NNNN-title.md` 独立文件：

```markdown
# ADR NNNN: {Title}

**Status:** Accepted | Superseded by NNNN | Deprecated

**Context:** {The situation that led to this decision}

**Decision:** {What we decided to do}

**Consequences:** {Trade-offs we accepted}
```
