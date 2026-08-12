# Changelog

All notable changes to this skills repository will be documented in this file.

## [Unreleased]

## [1.2.0] - 2026-08-12

### Changed

- **README**: 去重技能表，索引统一指向 USAGE/CHANGELOG（189→~105 行）
- **5-版本管理 / 0-启动 / 0--laoyoutiao**: 命令与示例外迁 references，SKILL 瘦身
- **2-开发**: 编码准则改为纯引用 CLAUDE.md
- **manifest**: 全技能增加 `category` 字段；version → 1.2.0
- **validate_skills**: `category` 校验；`--check-claude-mirror` 可选镜像对账
- **tests**: 路由意图 eval fixture（`tests/fixtures/prompts/router/`）

## [1.1.0] - 2026-08-12

### Changed

- 路由加载措辞统一；1-规划 adr 引用修正；README「分发与部署」
- 2-开发/tdd 委托彻底化；Worker `invocation: user`
- CLAUDE 支撑层补 0--explore；CI 增加 pytest
- 0-询问luohe 探索分流；规模 S/M/L/XL 映射
- 5-版本管理 / 6-最后整理 / neat-freak 示例外迁

### Added

- `invocation-semantic` 校验；`pyproject.toml`；`status: experimental` 支持

### Removed

- `--check-deployments` 宿主部署层校验

## [1.0.0] - 2026-08-08

初始治理基线与 noteall 机制门禁批次。详见历史 commit。
