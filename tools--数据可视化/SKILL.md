---
name: tools--数据可视化
description: 用 Python (matplotlib, seaborn, plotly) 创建有效的数据可视化。当用户说"画个图"、"做个数据图表"、"可视化这些数据"、"选什么图表类型"、"做出版级图表"、"这个数据怎么展示"时触发。涵盖图表选择、代码模板、设计原则和无障碍访问。
---

# 数据可视化工具

## 图表选择

| 想表达什么 | 最佳图表 | 备选 |
|-----------|----------|------|
| **时间趋势** | 折线图 | 面积图 |
| **类别对比** | 纵向柱状图 | 横向柱状图、棒棒糖图 |
| **排名** | 横向柱状图 | 点图、斜率图 |
| **构成占比** | 堆叠柱状图 | 树图、华夫饼图 |
| **分布** | 直方图 | 箱线图、小提琴图、散点分布图 |
| **相关性(2变量)** | 散点图 | 气泡图 |
| **相关性(多变量)** | 热力图 | 配对图 |
| **地理模式** | 等值线图 | 气泡地图 |
| **流程/过程** | 桑基图 | 漏斗图 |
| **关系网络** | 网络图 | 弦图 |
| **多KPI一览** | 小多组图 | 仪表板 |

## 避免使用的图表

- **饼图**：<6 个类别才考虑，人难以比较角度
- **3D 图表**：永远不用，扭曲感知
- **双轴图**：谨慎，可能误导暗示相关
- **堆叠柱状图(多类别)**：中间段难比较

## Python 代码模板

```python
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np

# 专业风格设置
plt.style.use('seaborn-v0_8-whitegrid')
plt.rcParams.update({
    'figure.figsize': (10, 6),
    'figure.dpi': 150,
    'font.size': 11,
    'axes.titlesize': 14,
    'axes.titleweight': 'bold',
})

# 色盲友好配色
COLORS = ['#4C72B0', '#DD8452', '#55A868', '#C44E52', '#8172B3', '#937860']
```

### 折线图（时序）
```python
fig, ax = plt.subplots(figsize=(10, 6))
for label, group in df.groupby('category'):
    ax.plot(group['date'], group['value'], label=label, linewidth=2)
ax.set_title('按类别趋势', fontweight='bold')
```

### 柱状图（类别对比）
```python
fig, ax = plt.subplots(figsize=(10, 6))
ax.bar(df['category'], df['value'], color=COLORS[0])
ax.set_title('各类别对比', fontweight='bold')
```

### 散点图（相关性）
```python
fig, ax = plt.subplots(figsize=(8, 8))
ax.scatter(df['x'], df['y'], alpha=0.6, c=COLORS[0])
ax.set_xlabel('X 变量')
ax.set_ylabel('Y 变量')
```

## 设计原则

- **减少非数据墨水**：去掉不传递信息的网格线、边框
- **直接标注优于图例**：让读者不用来回对照
- **排序**：柱状图按值排序，不是字母
- **无障碍**：色盲友好配色、足够对比度、图表标题清晰

## 参考原始 skill

基于 [anthropics/knowledge-work-plugins@data-visualization](https://github.com/anthropics/knowledge-work-plugins)，完整文件位于 `reference-skills/data-visualization/`。
