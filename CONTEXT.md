# My Skills Library

个人技能库的领域语言：技能如何组织、命名、分发与校验。Vault 流水线（Noteall）的术语见 [`my-note/CONTEXT.md`](my-note/CONTEXT.md)，两个上下文的关系见 [`CONTEXT-MAP.md`](CONTEXT-MAP.md)。

## Language

**技能清单（Skills Manifest）**:
`skills-manifest.yaml`，声明每个技能的名称、路径、调用方式与分发属性（`sync: true`）的唯一权威文件。

**canonical name（权威名）**:
清单中的 `name`，如 `vocabulary/tdd`；用于源码路径、依赖边和文档互指。
_Avoid_: 显示名、目录昵称

**deployment name（运行时名）**:
扁平部署后生效的调用名，如 `/tdd`、`/noteall`；由 `skill_manifest.py` 从未段推导，清单里不重复声明。
_Avoid_: canonical 名当运行时名用

**contract（发布契约）**:
`skill_manifest.py contract` 输出的 active 技能集合及其 canonical name、deployment name、hosts、invocation、status；分发的唯一输入。
_Avoid_: 部署清单、目录扫描结果

**核心层（vocabulary）**:
`vocabulary/` 下的可复用纪律，只做一件事、说一种语言；由阶段技能加载或在适用时被模型取用。与上游参考实现对齐，改动前先问「上游改了吗」。
_Avoid_: 工具库、公共函数

**编排壳（阶段技能）**:
`1-plan` ~ `6-sum` 等阶段技能：只做路由、分支、串联与交接，不内嵌纪律。
_Avoid_: 主流程实现、大技能

**invocation（调用方式）**:
技能的可达性声明：`model` 表示模型可按 description 自动触发（人类仍可显式调用）；`user` 表示仅用户显式输入可达，机制为 `disable-model-invocation: true`。
_Avoid_: 权限级别、可见性

**hosts（分发目标）**:
`skills-manager` 把技能同步到的宿主集合；只表示分发，不等于各宿主已通过行为认证。
_Avoid_: 支持平台、兼容宿主

**镜像同步（Sync）**:
依据技能清单单向分发到同步目标。机制与路径见 [README §分发与部署](README.md#分发与部署)。

**退役（deprecated）**:
`status: deprecated` 的技能：保留源码与迁移说明（`deprecated_note`），必须 `sync: false`，不进入 contract、USAGE 与路由。
_Avoid_: 删除、下线

## Relationships

- 镜像同步依据技能清单执行，单向分发（详见 README §分发与部署）。
- contract 由清单推导，是分发的唯一输入；`status: deprecated` 的条目不进入 contract。
- 编排壳只加载核心层与自身 references，不复制核心纪律。
- 库级词汇只描述组织、命名与分发；Vault 流程词汇属于 My Note 上下文。
