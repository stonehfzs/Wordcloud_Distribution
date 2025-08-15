import pandas as pd
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image, ImageDraw

# 读取数据
df = pd.read_csv('姓名.csv')

# 假设姓名在第一列，提取姓氏
name_col = df.columns[0]
surnames = df[name_col].dropna().astype(str).str[0]

# 统计姓氏频率
dict_freq = surnames.value_counts().to_dict()

# 生成反向mask，中央椭圆为空白，内容分布在外部
ellipse_width, ellipse_height = 1600, 800
# 椭圆尽可能铺满整个屏幕，只留极小边距
pad_x, pad_y = 30, 30
ellipse_img = Image.new('L', (ellipse_width, ellipse_height), 255)  # 先全白
draw = ImageDraw.Draw(ellipse_img)
draw.ellipse([(pad_x, pad_y), (ellipse_width-pad_x-1, ellipse_height-pad_y-1)], fill=0)  # 椭圆为黑
ellipse_mask = np.array(ellipse_img)

# 生成高分辨率椭圆词云，减小margin使内容更集中
mask_width, mask_height = 2000, 800
mask_img = Image.new('L', (mask_width, mask_height), 255)  # 白底
draw = ImageDraw.Draw(mask_img)
from PIL import ImageFont
try:
	font = ImageFont.truetype('arial.ttf', 600)
except:
	font = ImageFont.load_default()
# 居中绘制HAIDE，并整体右移
text = "HAIDE"
try:
	bbox = font.getbbox(text)
	text_width, text_height = bbox[2] - bbox[0], bbox[3] - bbox[1]
except AttributeError:
	text_width, text_height = font.getsize(text)
# 右移100像素
text_x = (mask_width - text_width) // 2 + 100
text_y = (mask_height - text_height) // 2
draw.text((text_x, text_y), text, font=font, fill=0)
haide_mask = np.array(mask_img)

wc = WordCloud(font_path='simkai.ttf', width=mask_width, height=mask_height, background_color='white', scale=2, mask=haide_mask, margin=2, collocations=False, prefer_horizontal=1.0)
wc.generate_from_frequencies(dict_freq)
# 生成HAIDE字母词云（更紧凑）
wc = WordCloud(
	font_path='simkai.ttf',
	width=mask_width,
	height=mask_height,
	background_color='white',
	scale=2,
	mask=haide_mask,
	margin=0,
	max_words=1000,
	relative_scaling=0.2,
	collocations=False,
	prefer_horizontal=1.0
)
wc.generate_from_frequencies(dict_freq)

# 显示并保存高分辨率词云
plt.figure(figsize=(16, 8), dpi=100)
plt.imshow(wc, interpolation='nearest')
plt.axis('off')
plt.tight_layout(pad=0)
plt.savefig('name_wordcloud.png', dpi=300, bbox_inches='tight', pad_inches=0.0)
plt.show()
