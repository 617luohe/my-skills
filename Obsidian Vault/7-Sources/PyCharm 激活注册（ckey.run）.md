---
title: "PyCharm 激活注册（ckey.run）"
aliases: ["ckey.run", "JetBrains 激活工具", "PyCharm 激活"]
tags:
  - type/resource
  - domain/tech/python
created: 2026-05-29
updated: 2026-05-29
status: published
confidence: sprout
source: "https://ckey.run/"
---

# PyCharm 激活注册（ckey.run）

> 通过 ckey.run 提供的自动化脚本，一键激活 PyCharm 及 JetBrains 全家桶，支持 Windows/Linux/macOS 全平台。

## 概述

ckey.run（CodeKey Run）是一个第三方 JetBrains 产品激活工具网站，通过自动化脚本为 PyCharm、IntelliJ IDEA、WebStorm、GoLand 等数十款 JetBrains IDE 提供激活服务。其底层基于 `ja-netfilter` 激活代理实现。

## 激活特点

| 特性 | 说明 |
|------|------|
| **支持产品** | PyCharm、IDEA、WebStorm、GoLand、CLion、DataGrip 等全部 JetBrains 产品 |
| **激活有效期** | 默认至 **2099 年 12 月 31 日** |
| **自定义信息** | 运行脚本后可自定义授权名称和到期日期 |
| **批量激活** | 自动检测本地所有 JetBrains 产品，一键批量激活 |
| **底层原理** | 基于 `ja-netfilter`，自动注入 `-javaagent` 启动参数 |

## 各平台激活步骤

### Windows

以 **管理员身份** 打开 PowerShell，执行以下命令：

```powershell
irm ckey.run|iex
```

**调试模式**（查看详细执行日志）：

```powershell
irm ckey.run/debug|iex
```

**查看脚本源码**（不执行，仅查看）：

```powershell
irm ckey.run
```

### Linux

打开终端，执行：

```bash
wget --no-check-certificate ckey.run -O ckey.run && bash ckey.run
```

### macOS

打开终端，建议先运行以下命令安装基础依赖：

```bash
xcode-select --install
```

然后执行：

```bash
curl -L -o ckey.run ckey.run && bash ckey.run
```

## 激活后的自定义设置

脚本运行过程中会依次提示：

1. **自定义授权名称** — 默认 `ckey.run`，可直接回车跳过
2. **自定义到期日期** — 默认 `2099-12-31`，格式 `yyyy-MM-dd`

## 注意事项

- **激活前关闭所有 JetBrains 软件**，避免文件占用导致失败
- **Windows 必须使用管理员权限**运行 PowerShell
- 如之前使用过其他激活工具，可能需要清理缓存文件（macOS 路径：`~/Library/Application Support/JetBrains`）
- 可通过 `irm ckey.run` 查看脚本源码，建议执行前确认代码安全性

## 技术原理

ckey.run 基于 `ja-netfilter` 项目实现激活：

1. 自动下载 `ja-netfilter.jar` 及 `privacy.jar` 到 `~/.jb_run/`
2. 为每个 JetBrains 产品生成 `.vmoptions` 配置文件，注入 `-javaagent` 参数
3. 向 `https://ckey.run/generateLicense/file` 请求激活密钥
4. 将密钥写入产品配置目录，完成激活

## 免责声明

ckey.run 属于**第三方非官方激活工具**，通过自动化脚本绕过正版授权验证。请根据个人需求和法律风险自行评估使用。建议在经济条件允许的情况下支持 JetBrains 官方正版授权（提供教育免费、社区版及付费订阅等多种方案）。

## 参考链接

- ckey.run 官方网站：https://ckey.run/
- ja-netfilter 源项目：https://gitee.com/ja-netfilter/ja-netfilter/releases/tag/2025.3.0
- privacy.jar 源项目：https://gitea.998043.xyz/novice/plugin-privacy/releases/tag/release
