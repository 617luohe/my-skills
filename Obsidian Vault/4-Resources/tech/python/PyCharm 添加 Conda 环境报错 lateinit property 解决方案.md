---
title: "PyCharm 添加 Conda 环境报错 lateinit property 解决方案"
aliases: ["PyCharm Conda 报错", "lateinit property envs_dirs"]
tags:
  - type/resource
  - domain/tech/python
created: 2026-05-18
updated: 2026-05-18
status: published
confidence: seed
source: "https://blog.csdn.net/water_better/article/details/159434833"
---

# PyCharm 添加 Conda 环境报错 lateinit property 解决方案

> 一句话定义：解决 PyCharm 添加 Conda 虚拟环境时抛出 `lateinit property envs_dirs has not been initialized` 错误的完整方法汇总。

## 概述

在 PyCharm 中添加 Conda 环境时，报错：

```
lateinit property envs_dirs has not been initialized
```

这是 **PyCharm 与新版 Conda 之间的兼容性问题**（JetBrains 官方 Bug PY-85954）。Conda 本身功能正常，终端中可以正常使用，但 PyCharm 无法解析新版 Conda 的 JSON 输出结构。

## 问题原因

### 已知不兼容版本组合

| PyCharm 版本 | Conda 版本 | Python 版本 |
|-------------|-----------|------------|
| 2024.2 ~ 2025.2.x | 25.11.x | 3.13 |
| 2023.2.x | 25.x | 3.13 |

Conda 25.x 改变了内部数据结构的初始化方式，而 PyCharm 2025.2.x 及更早版本的解析器无法正确处理这些变化。

### 诊断方法

```bash
# 确认 conda 本身正常
conda info --json | grep envs_dirs

# 查看版本
conda --version
python --version

# 列出所有环境
conda env list
```

如果 `conda info --json` 能正常输出 `"envs_dirs"` 字段，说明 conda 本身没问题，是 PyCharm 的解析兼容性问题。

---

## 解决方案（按推荐程度排序）

### 方案一：升级 PyCharm（推荐）

官方已在 **PyCharm 2025.3+** 修复此问题。

```
Help → Check for Updates → 升级到最新版
```

或下载 Release Candidate (RC) 版本作为临时过渡。

---

### 方案二：降级 Conda（可靠方案）

macOS / Linux / Windows 均适用，保留 Python 3.12，使用 conda 24.x。

```bash
# 1. 下载并安装 Miniconda（Python 3.12 版本，非 3.13）
#    推荐 Miniconda3-py312_25.9.1 或更早的 py312 版本

# 2. 降级 conda 到 24.x + base python 到 3.12
conda install -n base python=3.12 conda=24.11.3 --solver=classic

# 3. 创建项目使用的环境
conda create -n myenv python=3.11 -y
```

在 PyCharm 中添加解释器时注意路径选择：

| 操作系统 | Conda executable 路径 |
|----------|----------------------|
| macOS/Linux | `/opt/miniconda3/bin/conda` |
| Windows | `D:\Miniconda3\Scripts\conda.exe` |

> [!warning]
> 不要选择 `condabin/conda`（macOS）或 `_conda.exe`（Windows），务必使用标准路径。

环境选择 **Existing environment**，直接指向 `.../envs/myenv/bin/python`（或 `python.exe`）。

---

### 方案三：使用 _conda.exe（Windows 特有）

在 Windows 上，选择 `_conda.exe` 而非 `Scripts\conda.exe` 可以绕过此问题：

```
D:\Miniforge3\_conda.exe         ← 选这个
D:\Miniforge3\Scripts\conda.exe  ← 不要选这个
```

---

### 方案四：使用 System Interpreter 绕过

完全绕过 PyCharm 的 Conda 环境扫描逻辑：

1. `File → Settings → Project → Python Interpreter`
2. 点击齿轮 → **Add Interpreter**
3. 选择 **System Interpreter**（而非 Conda Environment）
4. 直接浏览到 conda 环境中的 Python 可执行文件：

```
# macOS / Linux:
/opt/miniconda3/envs/myenv/bin/python

# Windows:
D:\Miniconda3\envs\myenv\python.exe
```

缺点：无法在 PyCharm 中管理 conda 包，需在终端手动操作。

---

### 方案五：使用 Virtualenv（放弃 Conda）

如果项目不强依赖 conda：

```
Add Interpreter → Virtualenv Environment → New environment
```

---

### 方案六：重新初始化 Conda

```bash
conda init --reverse
# 重启电脑
conda init
# 重启终端
```

---

### 方案七：清理多个 Conda 安装

同时存在 Anaconda + Miniconda 或 Miniforge + Miniconda 会导致环境冲突：

```bash
# macOS / Linux：检查所有 conda 安装
which -a conda

# Windows：检查所有 conda 安装
where conda

# 只保留一个，卸载其他的
```

---

## 方案选择决策树

```
PyCharm 是什么版本？
├── 2025.3+  → 已修复，直接使用
└── 2025.2 及以下 →
    ├── 能否升级 PyCharm？
    │   └── 是 → 升级到 2025.3+（方案一）
    └── 不能升级 →
        ├── 是 Windows 吗？
        │   └── 是 → 尝试 _conda.exe（方案三）
        ├── 能降级 Conda 吗？
        │   └── 是 → 降级到 conda 24.x + python 3.12（方案二）
        └── 都不想改 →
            └── 用 System Interpreter 绕过（方案四）
```

---

## 参考来源

- CSDN：PyCharm 添加 Conda 环境报错解决方案
- JetBrains Issue Tracker：PY-85954

## 延伸阅读

- [[Python 环境管理最佳实践]]
- [[Miniconda 安装与配置]]
- [[PyCharm 常用配置]]
