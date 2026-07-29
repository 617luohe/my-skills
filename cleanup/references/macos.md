# macOS 操作方案

> 本文件是 macOS 系统的完整操作方案。扫描前读取，分析时作为分级判定依据。

---

## 一、系统识别

确认当前为 macOS 后，记录以下关键信息用于后续分析：

```bash
sw_vers -productVersion     # macOS 版本号
uname -m                     # 架构（arm64 = Apple Silicon, x86_64 = Intel）
diskutil info /              # 主盘信息（文件系统、可清除空间等）
df -h /                      # 快速盘用量
```

**盘数**：macOS 一般只有一个物理盘（`Macintosh HD`），挂载在 `/`。`diskutil list` 可确认是否有外置盘、Time Machine 备份盘或多挂载点。

---

## 二、数据布局 —— 东西存哪

### 关键目录总览

| 目录 | 装什么 | 典型分级 |
|---|---|---|
| `~/Library/Caches/*` | 应用/工具缓存（浏览器、Homebrew、pip、playwright） | 🟢 可自动清 |
| `~/.cache/*`、`~/.npm`、`~/.cargo`、`~/.gradle`、`~/.m2` | 开发缓存（pip/uv/npm/Cargo/Gradle 等） | 🟢 |
| `~/Library/Developer/Xcode/DerivedData`、`CoreSimulator` | Xcode 构建产物 / 模拟器镜像 | 🟢 |
| `~/Downloads` 里的 `.dmg`/`.pkg` | 安装包残留 | 🟢 |
| `~/Library/Caches/Homebrew` | Homebrew 下载缓存 | 🟢 |
| `~/Library/Containers/<UUID 或 bundleid>` | 沙盒应用数据（聊天记录、离线视频、设置） | 🟡 多为用户数据 |
| `~/Library/Group Containers/*` | 应用组数据（微信文件、小组件共享） | 🟡 |
| `~/Library/Application Support/*` | 应用数据（Chrome Profile、Claude VM、VS Code 扩展） | 🟡 |
| `~/Library/Messages`、`~/Library/Mail` | 聊天记录 / 邮件 | 🟡 |
| `/Applications/*.app` | 应用本体 | 🔴 仅当重复/想卸时上灯，否则归蓝色 |
| `~/Library/` 其余系统文件 | macOS 系统/用户库 | 不上灯，归蓝色"系统及其他" |
| APFS 本地快照 / `/.DocumentRevisions-V100` | 系统快照 / 版本历史 | 不上灯，归蓝色 |

### 辨认"神秘 UUID 容器"

`~/Library/Containers/` 和 `~/Library/Group Containers/` 下 UUID 命名的大目录，要查清属于哪个 App：

```bash
# 方法一：ls 查 Data/Documents 找 bundle id
ls ~/Library/Containers/<UUID>/Data/Documents/
ls ~/Library/Containers/<UUID>/Data/Library/

# 方法二：用 mdfind 反查（若有索引）
mdfind "kMDItemFSName == '<UUID>'"
```

- Bundle id 如 `com.bilibili.bbad` → 哔哩哔哩
- 大头常藏在隐藏目录（如 `.Downloads/` 里的 `.bilitask` 离线视频）
- **关键提示**：App 托管容器内的文件在访达里是程序内部格式、文件名看不懂，想清理优先去对应 App 内删除（设置 → 存储管理 → 清除缓存）。
- 仍只读，别动文件。

### 不在扫描范围内的占用源（需手动检查）

| 占用源 | 检查命令 | 处理方式 |
|---|---|---|
| Time Machine 本地快照 | `tmutil listlocalsnapshots /` | 调整策略，不手删 |
| iOS 备份 | `ls ~/Library/Application\ Support/MobileSync/Backup/` | 🟡 让用户决定 |
| Docker 镜像/容器 | `docker system df` | 🟢 用 Docker 自身清理 |
| Steam/游戏 | `ls ~/Library/Application\ Support/Steam/steamapps/` | 🟡 让用户决定 |
| iTunes/Music 媒体库 | `ls ~/Music/iTunes/` 或 `~/Music/Music/` | 🟡 |

---

## 三、分级判定标准（结合 scan.py 输出）

### 🟢 可自动清理（纯缓存，可再生，不丢用户数据）

判定条件：**删了不丢数据、可再生、不影响 App 功能**。

| 目录/模式 | 清理命令 | 备注 |
|---|---|---|
| `~/Library/Caches/<app>/*` | `rm -rf ~/Library/Caches/<app>/*` | 关掉 App 再删 |
| `~/.cache/`、`~/.npm/_cacache/` | `rm -rf ~/.cache` 或仅子目 | 放 `trash_paths` |
| `~/.cargo/registry/cache/` | `rm -rf ~/.cargo/registry/cache/` | 仅缓存，非 registry |
| `~/.gradle/caches/` | `rm -rf ~/.gradle/caches/` | Android 开发者 |
| `~/Library/Developer/Xcode/DerivedData` | `rm -rf ~/Library/Developer/Xcode/DerivedData/*` | Xcode 自动重建 |
| `~/Library/Developer/CoreSimulator/Caches` | `xcrun simctl delete unavailable` | 用 xcrun 更安全 |
| `~/Library/Caches/Homebrew` | `brew cleanup --prune=all` | 用 brew 自身清理 |
| `~/Downloads/*.dmg`、`*.pkg` | 移到废纸篓 | 安装包残留 |
| `~/Library/Caches/pip` | `rm -rf ~/Library/Caches/pip` | pip 缓存 |
| Node 项目 `node_modules` | 放 🟡，"rm -rf 后 npm install 可恢复" | 有判断成本 |

### 🟡 需人工判断（含用户数据）

判定条件：**有用户数据、删了不可逆、或需要判断内容**。

处置路径：
1. **首选应用内清理**——如果该 App 自带存储管理（如微信 → 设置 → 通用 → 存储空间）
2. **其次访达审查**——在访达打开文件夹，让用户自己看内容决定删什么
3. **最后才建议终端 `rm`**——且只给安全子路径，不给 App 托管根目录

典型 🟡 项：

| 目录/App | 内容画像 | 处置路径 | 风险 |
|---|---|---|---|
| 微信 Containers | 聊天记录、文件、图片、视频 | 应用内清理 → 设置 → 通用 → 存储空间 | 误删丢聊天记录 |
| B站 Containers `.Downloads/` | bilitask 离线视频 | 访达打开 `.Downloads` 删视频；或 App 内清离线 | App 内清更安全 |
| Chrome User Data | 书签、密码、历史、扩展 | 不要把整个 Data 给 trash；给 Cache 子目录放 🟢 | 删 Data 丢所有登录态 |
| `~/Documents`、`~/Desktop` | 用户文档/工作文件 | 访达打开让用户自己审查 | 不可代删 |
| `node_modules`（项目级） | 项目依赖 | 可 `rm -rf` 后 `npm install` 恢复，但用户需确认项目是否还在 | 删错项目目录 |
| `~/Library/Messages/` | iMessage 聊天记录 + 附件 | 系统设置 → 信息 → 保留消息 | 删了不可逆 |

### 🔴 谨慎清理（不建议手删）

判定条件：**你可能想动，但手删有风险——走正规卸载/系统工具**。

| 项目 | 为什么不能手删 | 正规卸载步骤 |
|---|---|---|
| `/Applications/*.app` | 有残留（Library 里 Preference、Caches、Containers） | 启动台长按 → 点 × 卸载；或用 AppCleaner 清残留 |
| `~/Library/Application Support/<app>` | App 运行时核心数据 | 先卸载 App，再决定是否删残留 |
| `~/.Trash` | 回收站 | 提示用户手动清空废纸篓 |

---

## 四、清理方案 —— 五个层次

按安全性从高到低，分析时按此优先级推荐：

1. **系统自带存储管理** —  → 系统设置 → 通用 → 储存空间 → 系统会列出推荐（清废纸篓、优化储存、清信息大附件）
2. **App 内清理入口** — 微信/QQ/Chrome 等 App 自带清理（最安全，不丢数据）
3. **Homebrew cleanup** — `brew cleanup --prune=all` 清所有 formula/cask 旧版本
4. **开发缓存清扫** — Xcode、npm、pip、Cargo、Gradle 缓存目录
5. **访达手动清理** — 大文件查找 + 手动移废纸篓

### 删除机制

`server.py` 在 macOS 用 `osascript` 调访达将文件移入废纸篓；首次运行可能弹访达自动化授权，点允许。后端备用方案：若 osascript 失败，用 `shutil.move` 移到 `~/.Trash/`。

---

## 五、间接释放（不进红灯，写进 long_term）

这些不是具体要删的东西，而是可以帮用户长期省空间的技巧：

- 系统"可清除空间"（purgeable）：macOS 磁盘紧张时自动回收
- 重启 Mac 可释放部分 swap 和临时 APFS 快照
- `brew cleanup --prune=all` 定期清理
- 清 Xcode DerivedData：`rm -rf ~/Library/Developer/Xcode/DerivedData/*`
- 删除旧 iOS 模拟器：`xcrun simctl delete unavailable`
- 调整 Time Machine 本地快照保留策略：`tmutil disablelocal` / `tmutil enablelocal`
- 可视化工具推荐：DaisyDisk、GrandPerspective、OmniDiskSweeper
- macOS「系统设置 → 通用 → 储存空间」的优化建议
