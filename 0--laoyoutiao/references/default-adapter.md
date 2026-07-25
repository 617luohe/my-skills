# 默认适配器：branch_config.json + Python 注册表

仅当项目没有可复用的交付开关框架，或用户明确要求使用默认框架时读取本文件。

## 注册表发现

遍历项目 `.py` 文件，排除 `__pycache__`、`.git`、`venv`、`.venv` 和 `node_modules`。使用 Python `ast` 解析模块级 `dict`，命中任一条件即视为候选注册表：

- 上方有 `# registry` 或 `# branch-registry`；
- 变量名匹配 `*_REGISTRY`、`*_ENGINES`、`*_IMPLEMENTATIONS`、`*_PROVIDERS`、`*_BACKENDS`；
- key 为字符串、value 为类/函数引用，且至少有两个条目。

从变量名推断模块名，如 `SORT_ENGINES` → `sort`。叙事线按注释 `# storyline: xxx`、路径关键词、模块名关键词、兜底“功能”的顺序推断。

项目没有注册表时，只建议最小模板，不直接写入：

```python
# storyline: performance
SORT_ENGINES = {
    "basic": BasicSort,                 # branch: basic — 基础实现
    "optimized": OptimizedSort,         # branch: optimized — 待验证
}
```

## 初始化文件

确认预览后创建：

```text
项目根目录/
├── branch_config.json
├── .laoyoutiao/delivery-log.json
├── DELIVERY_ROADMAP.md
└── delivery-notes/
```

- `branch_config.json`：`{模块: 当前实现}`，初始值取每个注册表的第一个条目；
- `delivery-log.json`：空交付历史；
- `DELIVERY_ROADMAP.md`：按叙事线组织的交付路线图。

路线图同一叙事线内由简单到复杂，跨叙事线交替安排，每次 2–4 个模块。可选读取 git 历史标记已有原型，但不要把旧代码自动恢复到工作区。

## 读写与校验

- 当前状态来自 `branch_config.json`；
- 候选状态来自代码注册表；
- 写入时只修改目标模块的值；
- 校验目标值存在于对应注册表，并运行项目已有测试或配置检查；
- 配置漂移时先展示修复 diff，确认后再改为有效实现。
