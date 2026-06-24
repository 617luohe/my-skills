---
name: tools--网页测试
description: 使用 Playwright 测试本地 Web 应用。支持验证前端功能、调试 UI 行为、截取浏览器截图、查看浏览器日志。当用户说"测一下这个页面"、"截个浏览器图"、"调试前端"、"跑一下自动化测试"、"检查页面渲染"时触发。
---

# 网页测试工具

用 Python Playwright 脚本测试本地 Web 应用。

## 决策树

```
用户任务 → 是静态 HTML？
    ├─ 是 → 直接读 HTML 文件识别选择器
    │        ├─ 成功 → 用选择器写 Playwright 脚本
    │        └─ 失败/不完整 → 当作动态处理
    │
    └─ 否（动态 Web 应用）→ 服务器是否已在运行？
        ├─ 否 → 使用 with_server.py 启动
        │
        └─ 是 → 侦察后行动：
            1. 导航并等待 networkidle
            2. 截图或检查 DOM
            3. 从渲染状态识别选择器
            4. 用发现的选择器执行操作
```

## 启动服务器

```bash
# 单服务器
python scripts/with_server.py --server "npm run dev" --port 5173 -- python test.py

# 多服务器（如后端+前端）
python scripts/with_server.py \
  --server "cd backend && python server.py" --port 3000 \
  --server "cd frontend && npm run dev" --port 5173 \
  -- python test.py
```

## Playwright 脚本模板

```python
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    page.goto('http://localhost:5173')
    page.wait_for_load_state('networkidle')  # 关键：等 JS 执行完毕
    # ... 自动化逻辑 ...
    browser.close()
```

## 侦察后行动模式

1. **检查渲染后的 DOM**：
   ```python
   page.screenshot(path='/tmp/inspect.png', full_page=True)
   content = page.content()
   page.locator('button').all()
   ```
2. **识别选择器**
3. **执行操作**

## 常见陷阱

❌ 动态应用上，不要在等待 `networkidle` 之前检查 DOM

## 参考原始 skill

基于 [anthropics/skills@webapp-testing](https://github.com/anthropics/skills)，完整文件（含 scripts/）位于 `reference-skills/webapp-testing/`。
