# Skill mechanics — 当文档是 skill 时

skill 专属分支：frontmatter、调用选择、路由器。其余写作规则见 [SKILL.md](SKILL.md)。

## 调用选择

两个选择，权衡两种 load：

- **model-invoked** — 保留 description，agent 可自主触发，其他技能可引用。description 是常驻指针：付常驻 context load 换自动发现。写法：`disable-model-invocation: false`（或省略），description 面向模型、带触发分支（指针规则完整适用）。
- **user-invoked** — 从 agent 可及范围剥离 description：只有人手输入名字可调，其他技能调不动。零 context load，但付 cognitive load——你是索引。写法：`disable-model-invocation: true`，description 变 human-facing 一行摘要，触发词剥掉。

**规则**：只有 agent 需要自己触达、或别的技能必须引用时才选 model-invoked；只由人手触发就 user-invoked，不付常驻成本。

两个 user-invoked 技能都要用的共享 reference：放不进任何一个（无 description 互相调不动）→ 放到技能系统外的普通文件，任何技能都能指。

## 按调用切分

有独立触发词（你真会用的词）、或别的技能必须触达时才切出 model-invoked 技能。常驻 description 是成本，独立触达要值回票价。

## 路由器

user-invoked 技能多到你记不住时，用一个路由技能化解：一个 user-invoked 技能列出其他技能和各自何时用，人只需记一个。它只能提示，不能触发它们——user-invoked 无 description，只有人能触达。
