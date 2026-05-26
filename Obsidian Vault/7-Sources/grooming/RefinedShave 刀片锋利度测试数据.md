---
title: "RefinedShave 刀片锋利度测试数据"
aliases: ["refinedshave blade data", "刀片切割力测试"]
tags:
  - type/source
  - domain/life/grooming
  - source/web
created: 2026-05-26
updated: 2026-05-26
status: published
confidence: sprout
source: "https://www.refinedshave.com/razor-blade-sharpness-testing/"
archive: "https://web.archive.org/web/20230603150437/https://www.refinedshave.com/razor-blade-sharpness-testing/"
---

# RefinedShave 刀片锋利度测试数据

> 数据来源：RefinedShave.com（工程师运营的独立测试项目），原网站已下线，数据来自 Wayback Machine 存档及各论坛引用。

## 测试方法

- **测试原理**：用专用设备测量刀片切穿标准测试介质所需的力
- **计量单位**：克力（gram-force），数值越低 = 越锋利
- **测试刀架**：Merkur 34C（固定变量）
- **测试周期**：全新 → 第 1 次剃须后 → 第 2 次剃须后
- **测试者**：每次剃须为全头+全脸，约等于普通人的 2 次面部剃须
- **数据性质**：实验室测量值，非主观感受

### 测量标尺

| 切割力范围 | 主观体验 |
|-----------|---------|
| ~30-35g | 极锋利——可能引起刺激、割伤，敏感肤质需谨慎 |
| ~40g | 甜点区——锋利度与舒适度的最佳平衡 |
| ~50g+ | 偏钝——拉扯感，需多次 passes |

## 原始数据表

### 按初始锋利度排序

| 排名 | 品牌 | 型号 | 产地 | 全新 (g) | 第 1 次后 (g) | 第 2 次后 (g) | 平均 (g) |
|------|------|------|------|---------|-------------|-------------|---------|
| 1 | Feather | Hi-Stainless | 日本 | 32 | — | — | ~37 |
| 2 | BIC | Chrome Platinum | 希腊 | 40 | — | — | ~35 |
| 3 | Perma-Sharp | Super | 俄罗斯 | 41 | 30 | 37 | 36 |
| 4 | Voskhod | Teflon Coated | 俄罗斯 | 42 | — | — | — |
| 5 | Astra | Superior Stainless (蓝) | 俄罗斯 | 43 | 38 | 40 | 40 |
| 6 | Gillette | Nacet Stainless | 俄罗斯 | 39 | — | — | ~37 |
| 7 | Gillette | 7 O'Clock Super Platinum (黑) | 俄罗斯 | 45 | 32 | 36 | 38 |
| 8 | Gillette | Platinum | 俄罗斯 | 45 | — | — | — |
| 9 | Gillette | 7 O'Clock Permasharp Stainless (绿·印) | 印度 | 45 | 35 | 42 | 41 |
| 10 | Gillette | 7 O'Clock Super Stainless (绿·俄) | 俄罗斯 | 45 | 38 | 40 | 41 |
| 11 | Shark | Super Stainless | 埃及 | 47 | — | — | — |
| 12 | Astra | Superior Platinum (绿) | 俄罗斯 | 49 | 46 | 44 | 46 |
| 13 | Derby | Premium | 土耳其 | 51 | 46 | 46 | 48 |
| 14 | Derby | Extra (绿) | 土耳其 | 53 | 44 | 51 | 49 |
| 15 | Merkur | Super Platinum | 德国 | 53 | — | — | — |
| 16 | Kai | Stainless Steel | 日本 | 53 | ~43 | — | — |

> 注：部分刀片缺少多轮数据（"—"），原始页面尚未补全所有刀片的完整追踪。

### 按平均锋利度排序

| 排名 | 品牌 | 型号 | 平均 (g) |
|------|------|------|---------|
| 1 | BIC Chrome Platinum | | ~35 |
| 2 | Perma-Sharp Super | | 36 |
| 3 | Feather Hi-Stainless | | ~37 |
| 4 | Gillette Nacet | | ~37 |
| 5 | Gillette 7 O'Clock Super Platinum (黑) | 38 |
| 6 | Astra Superior Stainless (蓝) | 40 |
| 7 | Gillette 7 O'Clock Permasharp Stainless (绿·印) | 41 |
| 8 | Gillette 7 O'Clock Super Stainless (绿·俄) | 41 |
| 9 | Astra Superior Platinum (绿) | 46 |
| 10 | Derby Premium | 48 |
| 11 | Derby Extra (绿) | 49 |
| 12 | Kai Stainless Steel | ~48 |
| 13 | Merkur Super Platinum | ~53 |
| 14 | Shark Super Stainless | ~47 |

> BIC 的平均值最低（~35g），因其第 2、3 次使用后锋利度反而上升，拉低了均值。
> Feather 虽然全新时最锋利（32g），但因单调递减，平均被 BIC 和 Perma-Sharp 反超。

## 锋利度生命周期特征

### U 型曲线现象

多数涂层刀片的锋利度并非线性递减，而是呈现 U 型曲线：

```
锋
利    全新   第1次后   第2次后   第3次后   第4次后
度    │       │        │        │        │
▲    32      │        │        │        │
│    ·Feather│        │        │        │
│    41     ·30      ·37      ·        ·
│    ·Perma-│ Sharp  │        │        │
│    45     ·32      ·36      ·        ·
│    ·7O'Black       │        │        │
│    43     ·38      ·40      ·        ·
│    ·Astra Blue     │        │        │
│           │        │        │        │
└──────────────────────────────────────────▶ 使用次数
```

关键发现：
- **涂层刀片**（如 Perma-Sharp、7 O'Clock）：第 2 次使用时锋利度达到峰值（涂层磨掉后露出更薄边缘）
- **无涂层刀片**（如 Kai）：初始偏钝，使用后显著变锋
- **单调递减型**（如 Feather）：出厂即巅峰，之后持续下滑

### 耐用性分层

| 等级 | 代表刀片 | 可用次数 | 特点 |
|------|---------|---------|------|
| 优秀 | BIC, Kai, 7 O'Clock Black | 7-10 次 | 峰值出现晚，衰减平缓 |
| 良好 | Nacet, Perma-Sharp, Astra Blue | 5-7 次 | 稳定输出，均衡型 |
| 一般 | Feather, Derby Premium | 3-5 次 | 初始不错但衰减快 |
| 偏弱 | Merkur, Derby Extra | 3-4 次 | 初始已偏钝 |

## 数据可靠性说明

- **客观性**：机器测量，非主观感受，排除了安慰剂效应
- **局限性**：
  - 仅代表一把 Merkur 34C 中的数据
  - 仅反映切割力，不反映顺滑度、涂层感受、肤质适配
  - 样本量可能有限
- **社区共识**：Badger & Blade、Sharpologist 等论坛普遍认可该数据的参考价值，但强调个体差异（YMMV）

## 引用来源

- RefinedShave.com — Razor Blade Sharpness Testing（原始页面，已下线）
- Wayback Machine 存档 — 2023-06-03 快照
- Badger & Blade 论坛 — 多线程引用与讨论
- Sharpologist — The Science of Blade Sharpness（Charles Smith）
- AR15.com 论坛 — 数据汇总转贴

## 延伸阅读

- [[双面安全剃须刀刀片数据横评]] — 知识库内的综合横评笔记
- [[刀片锋利度多维度分析]] — 多角度深度分析
