import geopandas as gpd
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import rcParams

# ===== 0) 全局中文字体（自动匹配可用中文字体）=====
rcParams['font.sans-serif'] = ['PingFang SC', 'Songti SC', 'STHeiti', 'SimHei', 'Microsoft YaHei', 'Arial Unicode MS']
rcParams['axes.unicode_minus'] = False

# ===== 1) 你的数据（按你提供的顺序与数值）=====
data = pd.DataFrame({
    "city": ["淄博","枣庄","烟台","潍坊","威海","泰安","日照","青岛","临沂","聊城","济宁","济南","菏泽","东营","德州","滨州"],
    "value": [  1,    4,    9,    4,    3,    9,    5,   25,    2,    2,    6,   32,    1,    5,    1,    3]
})
# 与底图匹配：底图是“XX市”，我们统一加上“市”
data["city_full"] = data["city"].astype(str) + "市"
data["city_norm"] = data["city"]  # 不带“市”的标准名

# ===== 2) 读取山东省地市级 GeoJSON =====
shandong_url = "https://geojson.cn/api/china/370000.json"
gdf = gpd.read_file(shandong_url)

# 只保留面要素（排除线等）
gdf = gdf[gdf.geometry.geom_type.isin(["Polygon", "MultiPolygon"])].copy()
gdf["name_norm"] = gdf["name"].str.replace("市","", regex=False)

# ===== 3) 修复几何，避免 dissolve 报错 =====
try:
    from shapely.make_valid import make_valid
    gdf["geometry"] = gdf["geometry"].apply(make_valid)
except Exception:
    gdf["geometry"] = gdf["geometry"].buffer(0)

# ===== 4) 合并数据 =====
merged = gdf.merge(data, left_on="name_norm", right_on="city_norm", how="left")

# ===== 5) 颜色范围：收紧上限让整体更“深”（不被济南=32、青岛=25拉浅）=====
vals = merged["value"].dropna().to_numpy()
if len(vals):
    vmin = float(np.nanmin(vals))
    # 用 95 分位数做 vmax，再略微收紧（乘 0.9），你也可手动设比如 vmax=15/18/20
    vmax_auto = float(np.quantile(vals, 0.95))
    vmag = max(1.0, vmax_auto * 0.9)
else:
    vmin, vmag = 0.0, 1.0

# ===== 6) 绘制 =====
fig, ax = plt.subplots(1, 1, figsize=(9, 9))

# 6.1 市级填充：蓝色渐变（人数越多越深）
merged.plot(
    column="value",
    cmap="Blues",
    linewidth=0.6,
    ax=ax,
    edgecolor="0.6",   # 市级外轮廓
    legend=True,
    vmin=vmin, vmax=vmag,
    zorder=1
)

# 6.2 省整体外轮廓（更粗更深）
gdf.dissolve().boundary.plot(ax=ax, color="black", linewidth=0.5, zorder=2)

# 6.3 标注：市名 + 数值（代表点在多边形内部）
for _, row in merged.iterrows():
    pt = row.geometry.representative_point()
    if pd.notna(row.get("value", np.nan)):
        label = f"{row['name']}\n{int(row['value'])}"
    else:
        label = row["name"]
    ax.text(
        pt.x, pt.y, label,
        fontsize=8, ha="center", va="center", zorder=3, color="black",
        bbox=dict(facecolor="white", alpha=0.55, boxstyle="round,pad=0.2", lw=0)
    )

ax.set_title("中国海洋大学海德学院2025级新生山东省内生源地分布（单位：人）", fontsize=14)
ax.axis("off")
plt.tight_layout()

# 保存 + 显示
out_png = "shandong_city_heatmap_yourdata.png"
plt.savefig(out_png, dpi=300, bbox_inches='tight')
print(f" 已保存图片：{out_png}")
plt.show(block=True)