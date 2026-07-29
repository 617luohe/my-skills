# Windows 操作方案

> 本文件是 Windows 系统的完整操作方案。扫描前读取，分析时作为分级判定依据。
>
> **注意**：Windows 代码路径在 macOS 上无法验证，分析时对路径存在性保持谨慎。
> 扫描和删除代码已写但未在真实 Windows 上实测。

---

## 一、系统识别与信息收集

确认当前为 Windows 后，记录以下关键信息：

```bash
python -c "import platform; print(platform.system(), platform.release(), platform.version())"
python -c "import os; print(os.environ.get('USERPROFILE'), os.environ.get('SystemDrive'))"
python -c "import os; print(os.environ.get('PROCESSOR_ARCHITECTURE'))"
```

或通过系统命令：
```powershell
# 系统版本
systeminfo | findstr /B /C:"OS Name" /C:"OS Version"
# 磁盘列表
wmic logicaldisk get size,freespace,caption
```

**多盘符**：Windows 通常有多个盘（C:、D:…）。`scan.py` 的 `list_drives_windows()` 自动枚举所有盘符。**分析和清理聚焦系统盘 C:**——缓存、AppData、临时文件几乎都在 C:。其他盘（D: 等）一般是用户自存的资料/游戏，归 🟡 让用户自己判断，不要自动给删除按钮。

---

## 二、数据布局 —— 东西存哪

### 关键目录总览

| 目录（环境变量） | 装什么 | 典型分级 |
|---|---|---|
| `%LOCALAPPDATA%`（`C:\Users\<u>\AppData\Local`） | 浏览器缓存、应用数据、Temp，最大头 | 缓存 🟢 / 应用数据 🟡 |
| `%LOCALAPPDATA%\Temp`、`%TEMP%` | 临时文件 | 🟢 |
| `%APPDATA%`（Roaming） | 应用配置/数据（跨设备同步） | 🟡 |
| 浏览器缓存 `%LOCALAPPDATA%\Google\Chrome\User Data\*\Cache`、Edge 同构 | 浏览器缓存 | 🟢 |
| 浏览器 `User Data\<Profile>`（非 Cache 部分） | 书签/登录态/历史/扩展 | 🟡 |
| `%USERPROFILE%\.cache`、`.npm`、`.gradle`、`.m2`、`.cargo` | 开发缓存 | 🟢 |
| `%LOCALAPPDATA%\pip\Cache`、`npm-cache`、`Yarn\Cache` | 包管理缓存 | 🟢 |
| `%LOCALAPPDATA%\Microsoft\Windows\INetCache` | IE/WebView 缓存 | 🟢 |
| `%USERPROFILE%\.nuget\packages` | NuGet 包缓存 | 🟢 |
| `%LOCALAPPDATA%\uv`、`ms-playwright`、`go-build` | 开发工具缓存 | 🟢 |
| `C:\Program Files`、`Program Files (x86)` | 应用本体 | 🔴 仅重复/想卸时上灯，否则归蓝色 |
| `%USERPROFILE%\Downloads` | 下载文件 + 安装包残留 | 🟢（安装包）/ 🟡（用户文件） |
| `C:\$Recycle.Bin` | 回收站 | 🟡 提示用户清空 |
| `%USERPROFILE%\OneDrive` | OneDrive 文件（可能按需下载） | 🟡 |
| `%APPDATA%\Microsoft\Windows\Start Menu` | 开始菜单快捷方式 | 不入灯 |

### 浏览器缓存详解（Windows 上最常见的大头）

| 浏览器 | 缓存路径 | 分级 |
|---|---|---|
| **Chrome** | `%LOCALAPPDATA%\Google\Chrome\User Data\Default\Cache\Cache_Data` | 🟢 |
| **Edge** | `%LOCALAPPDATA%\Microsoft\Edge\User Data\Default\Cache\Cache_Data` | 🟢 |
| **Firefox** | `%APPDATA%\Mozilla\Firefox\Profiles\*\cache2` | 🟢 |
| **Brave** | `%LOCALAPPDATA%\BraveSoftware\Brave-Browser\User Data\Default\Cache` | 🟢 |

**注意**：只清 Cache 子目录，不动 User Data 根目录（含书签/登录态/密码）——后者归 🟡。

### 不在扫描范围内的占用源（需手动检查）

| 占用源 | 检查方式 | 处理方式 |
|---|---|---|
| Windows Update 缓存 | `DISM /Online /Cleanup-Image /AnalyzeComponentStore` | 磁盘清理 → 清理系统文件 |
| 休眠文件 `hiberfil.sys` | `powercfg /hibernate off` 可释放（等于关闭快速启动） | 🟡 需用户决定 |
| 虚拟内存 `pagefile.sys` | 系统属性 → 高级 → 性能设置 → 虚拟内存 | 🔴 不推荐手动改 |
| 系统还原点 | `vssadmin list shadows` | 磁盘清理 → 更多选项 → 清理还原点 |
| Windows.old | 看 C:\ 根目录 | 🟢 若已升级 Windows 且不打算回滚 |
| WSL 虚拟磁盘 | `%LOCALAPPDATA%\Packages\*\LocalState\ext4.vhdx` | 🟡 |
| Docker 镜像/容器 | `docker system df` | 🟢 用 Docker 自身清理 |

---

## 三、分级判定标准（结合 scan.py 输出）

### 🟢 可自动清理（纯缓存，可再生，不丢用户数据）

判定条件：**删了不丢数据、可再生、不影响 App 功能**。

| 目录/模式 | 清理方法 | 备注 |
|---|---|---|
| `%TEMP%` 和 `%LOCALAPPDATA%\Temp` | 资源管理器地址栏输入 `%TEMP%` → Ctrl+A → Del | 系统临时文件 |
| 浏览器 Cache 目录 | 见上方浏览器缓存表 | 仅删 Cache 子目录 |
| `%USERPROFILE%\.cache`、`.npm\_cacache`、`.gradle\caches` | 移回收站 | 开发缓存 |
| `%LOCALAPPDATA%\pip\Cache` | 移回收站 | pip 下载缓存 |
| `%USERPROFILE%\Downloads\*.exe`、`*.msi` | 移回收站 | 安装包残留 |
| NuGet 缓存 `%USERPROFILE%\.nuget\packages` | 移回收站 | 可重建 |
| `%LOCALAPPDATA%\Microsoft\Windows\INetCache` | 磁盘清理工具 | IE 缓存 |
| `%LOCALAPPDATA%\Yarn\Cache` | 移回收站 | Yarn 缓存 |

### 🟡 需人工判断（含用户数据）

判定条件：**有用户数据、删了不可逆、或需要判断内容**。

处置路径：
1. **首选应用内清理**——微信/QQ/Chrome 等 App 自带清理入口
2. **其次资源管理器审查**——在资源管理器打开文件夹，让用户自己看内容
3. **最后才建议终端删除**——且只给安全子路径

典型 🟡 项：

| 目录/App | 内容画像 | 处置路径 | 风险 |
|---|---|---|---|
| 微信 `%USERPROFILE%\Documents\WeChat Files\` | 聊天记录、文件、图片、视频 | 微信 → 设置 → 文件管理 → 清理 | 误删丢聊天记录 |
| Chrome/Edge User Data（非 Cache） | 书签、密码、历史 | 浏览器内清理历史记录，不手删文件 | 删 Data 丢所有登录态 |
| `%USERPROFILE%\Documents`、`Desktop` | 用户文档/工作文件 | 资源管理器打开让用户自己审查 | 不可代删 |
| `%USERPROFILE%\Downloads`（非安装包） | 下载文件 | 资源管理器打开审查 | 🟢 仅安装包，其他 🟡 |
| QQ `%USERPROFILE%\Documents\Tencent Files\` | 聊天图片/文件/语音 | QQ → 设置 → 文件管理 → 清理 | 误删丢文件 |
| `%USERPROFILE%\OneDrive` | 云端同步文件 | 检查文件是否按需下载（占位符不占本地空间） | 注意同步状态 |

### 🔴 谨慎清理（不建议手删）

判定条件：**你可能想动，但手删有风险——走正规卸载/系统工具**。

| 项目 | 为什么不能手删 | 正规操作 |
|---|---|---|
| `C:\Program Files\*.exe` | 有注册表残留和 AppData 残留 | 设置 → 应用 → 卸载；或用卸载工具（Geek Uninstaller）清残留 |
| `C:\Windows\WinSxS` | 组件存储，系统依赖 | 用 `DISM /Online /Cleanup-Image /StartComponentCleanup` |
| `hiberfil.sys` / `pagefile.sys` | 系统管理的文件 | 通过系统设置调整，不手删 |
| `C:\Windows` 内任何目录 | 操作系统核心 | 用磁盘清理工具处理系统垃圾 |

---

## 四、清理方案 —— 六个层次

按安全性从高到低，分析时按此优先级推荐：

1. **存储感知（Storage Sense）** — 设置 → 系统 → 存储 → 打开存储感知 → 配置自动清理规则（最推荐，全自动）
2. **磁盘清理（cleanmgr）** — 运行 `cleanmgr`，点"清理系统文件"可清 Windows Update 缓存、临时文件、回收站
3. **App 内清理入口** — 微信/QQ/Chrome/Edge 等 App 自带清理（最安全，不丢数据）
4. **设置 → 应用 → 卸载** — 正规卸载不用的应用，比直接删文件夹干净（不残留注册表）
5. **开发缓存清扫** — pip/npm/Yarn/NuGet/Go/Cargo 缓存目录，删了可再生
6. **资源管理器手动清理** — 大文件查找 + 手动移回收站

### Windows 系统工具速查

| 工具 | 启动方式 | 功能 |
|---|---|---|
| **存储感知** | 设置 → 系统 → 存储 | 自动清理临时文件、回收站、下载文件夹 |
| **磁盘清理** | `cleanmgr` | 清临时文件、缩略图、Windows Update 缓存 |
| **DISM 组件清理** | `DISM /Online /Cleanup-Image /StartComponentCleanup`（管理员终端） | 清 WinSxS 组件存储 |
| **程序卸载** | 设置 → 应用 → 已安装的应用 | 正规卸载大应用 |

### 删除机制

`server.py` 在 Windows 用 `ctypes` 调 `SHFileOperationW`（`FOF_ALLOWUNDO`）将文件送入回收站，可逆。纯标准库，无需第三方依赖。🟢 项的 `trash_paths` 应在用户配置文件（`%USERPROFILE%`）目录内，便于白名单与 HOME 越界校验通过。

---

## 五、间接释放（不进红灯，写进 long_term）

这些都是系统层面的空间优化技巧，不属于"清理决策"，写入长期建议：

- 打开**存储感知**：设置 → 系统 → 存储 → 配置清理计划
- 定期运行 `cleanmgr`（磁盘清理），勾选"Windows 更新清理"
- `DISM /Online /Cleanup-Image /StartComponentCleanup` 清理 WinSxS（管理员终端）
- 关闭休眠释放 `hiberfil.sys`（会失去快速启动）：`powercfg /hibernate off`
- 调整回收站大小：右键回收站 → 属性 → 设置各盘最大容量
- 移动文档/下载到 D: 盘（若有多盘）
- 用 **WizTree** / **SpaceSniffer** / **TreeSize Free** 可视化大文件分布
