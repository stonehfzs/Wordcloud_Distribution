import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import rcParams

# ===== 0) 全局中文字体 =====
rcParams['font.sans-serif'] = ['PingFang SC', 'Songti SC', 'STHeiti', 'SimHei', 'Microsoft YaHei', 'Arial Unicode MS']
rcParams['axes.unicode_minus'] = False

# ===== 1) 数据（省份 + 数值）=====
data = pd.DataFrame({
    "province": [
        "山东省","河北省","广东省","河南省","安徽省","山西省","浙江省","湖南省","湖北省","江苏省",
        "江西省","天津市","北京市","福建省","四川省","广西壮族自治区","甘肃省","辽宁省",
        "内蒙古自治区","陕西省","重庆市","云南省","海南省","黑龙江省","上海市"
    ],
    "value": [
        112, 16, 15, 13, 13, 11, 10, 10, 10, 10,
        9, 9, 8, 8, 8, 7, 4, 4,
        4, 4, 4, 4, 3, 2, 2
    ]
})

# 统一省份名称
def norm_name(name: str) -> str:
    return (name.replace("省","").replace("市","")
            .replace("回族自治区","").replace("维吾尔自治区","")
            .replace("壮族自治区","").replace("自治区","")
            .replace("特别行政区","").strip())

data["province_norm"] = data["province"].apply(norm_name)

# ===== 2) 读取全国 GeoJSON（省级）=====
china_url = "https://geojson.cn/api/china/100000.json"
china_gdf = gpd.read_file(china_url)

# 找省份字段
name_col = "name" if "name" in china_gdf.columns else ("NAME" if "NAME" in china_gdf.columns else None)
if not name_col:
    raise ValueError(f"未找到省份名称列：{china_gdf.columns}")

# 标准化名称，筛省级
china_gdf["name_norm"] = china_gdf[name_col].apply(norm_name)
if "adcode" in china_gdf.columns:
    china_gdf = china_gdf[china_gdf["adcode"].astype(str).str.endswith("0000")]

# ===== 3) 合并数据 =====
merged = china_gdf.merge(data, left_on="name_norm", right_on="province_norm", how="left")

# ===== 4) 绘制（蓝色渐变 + 颜色范围收紧）=====
fig, ax = plt.subplots(1, 1, figsize=(12, 10))

# 底图边界
china_gdf.boundary.plot(ax=ax, color="0.7", linewidth=0.8, zorder=1)

# 手动收紧颜色范围，让非山东的整体更深一些（可按需调 vmax）
vmin = merged["value"].min(skipna=True)
vmax = 60  # 可试 50/60/70，越小整体越深
merged[merged["value"].notna()].plot(
    column="value",
    cmap="Blues",
    linewidth=0.6,
    ax=ax,
    edgecolor="0.6",
    legend=True,
    vmin=vmin, vmax=vmax,
    zorder=2
)

# ===== 5) 标注：重点区域做错位与引线，其它省份用面内代表点 =====
# 偏移表（单位约为度；根据你图面需要可微调）
offsets = {
    # 珠三角：避免广东/港澳重叠
    "香港": (1.4, -1.8),
    "澳门": (-1.0, -1.0),
    # 京津冀：避免渤海湾一带堆叠
    "北京": (1.2, 0.8),    # 往东北偏
    "天津": (1.6, -0.2)  # 往正东方向偏一点

}

# 值查表
val_map = dict(zip(merged["name_norm"], merged["value"]))

for _, row in china_gdf.iterrows():
    prov_std = row["name_norm"]
    pt = row.geometry.representative_point()  # 一定在面内

    val = val_map.get(prov_std, None)
    label = f"{prov_std}\n{int(val)}" if pd.notna(val) else prov_std

    if prov_std in offsets:
        dx, dy = offsets[prov_std]
        x_off, y_off = pt.x + dx, pt.y + dy
        # 引线（从省内代表点指向文字）
        ax.plot([pt.x, x_off], [pt.y, y_off], color="black", linewidth=0.6, zorder=3)
        ax.text(
            x_off, y_off, label,
            fontsize=8, ha="center", va="center", zorder=4, color="black",
            bbox=dict(facecolor="white", alpha=0.65, boxstyle="round,pad=0.25", lw=0)
        )
    else:
        ax.text(
            pt.x, pt.y, label,
            fontsize=8, ha="center", va="center", zorder=3, color="black",
            bbox=dict(facecolor="white", alpha=0.5, boxstyle="round,pad=0.2", lw=0)
        )

# 标题（如不需要可留空）
ax.set_title("中国海洋大学海德学院2025级新生生源地分布（单位：人）", fontsize=14)
ax.axis("off")
plt.tight_layout()

# 保存 + 显示
out_png = "china_heatmap_blue_labels_offset_bj_tj_he_prd.png"
plt.savefig(out_png, dpi=300, bbox_inches='tight')
print(f" 已保存图片：{out_png}")
plt.show(block=True)