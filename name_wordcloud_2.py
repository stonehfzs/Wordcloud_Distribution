import pandas as pd
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image, ImageDraw, ImageFont

# 读取数据
df = pd.read_csv('姓名.csv')

# 假设姓名在第一列，提取所有单字
name_col = df.columns[0]
names = df[name_col].dropna().astype(str)
all_chars = list(''.join(names))

# 统计所有单字频率
import collections
dict_freq = dict(collections.Counter(all_chars))

# 生成HAIDE字母mask（反转，内容只在字母外部）
mask_width, mask_height = 2000, 800
mask_img = Image.new('L', (mask_width, mask_height), 0)  # 先全黑

draw = ImageDraw.Draw(mask_img)
try:
    font = ImageFont.truetype('arial.ttf', 600)
except:
    font = ImageFont.load_default()
text = "HAIDE"
try:
    bbox = font.getbbox(text)
    text_width, text_height = bbox[2] - bbox[0], bbox[3] - bbox[1]
except AttributeError:
    text_width, text_height = font.getsize(text)
# 居中绘制HAIDE字母
text_x = (mask_width - text_width) // 2
text_y = (mask_height - text_height) // 2
draw.text((text_x, text_y), text, font=font, fill=255)  # 字母区域为白
haide_mask_inv = np.array(mask_img)

# 生成HAIDE字母反向词云（内容在字母外部）

# 自定义颜色函数，主色调为00A7EB，增强对比度
from wordcloud import get_single_color_func
class BlueColorFunc(object):
    def __init__(self, base_color='#00A7EB'):
        self.base_color = base_color
        # 增加更深和更亮的蓝色，增强对比
        self.variations = [
            '#00A7EB',  # 主色
            '#0070A8',  # 深蓝
            '#33B8E8',  # 浅蓝
            '#005077',  # 极深蓝
            '#66CFF2',  # 亮蓝
            '#00334D',  # 最深蓝
            '#40CFFF',  # 高亮蓝
            '#0090C7',  # 中蓝
        ]
    def __call__(self, word, font_size, position, orientation, random_state=None, **kwargs):
        import random
        return random.choice(self.variations)

wc = WordCloud(
    font_path='simkai.ttf',
    width=mask_width,
    height=mask_height,
    background_color='white',
    scale=2,
    mask=haide_mask_inv,
    margin=0,
    max_words=1000,
    relative_scaling=0.2,
    collocations=False,
    prefer_horizontal=1.0
)
wc.generate_from_frequencies(dict_freq)
wc.recolor(color_func=BlueColorFunc())

# 显示并保存高分辨率词云
plt.figure(figsize=(16, 8), dpi=100)
plt.imshow(wc, interpolation='nearest')
plt.axis('off')
plt.tight_layout(pad=0)
plt.savefig('name_wordcloud_2.png', dpi=300, bbox_inches='tight', pad_inches=0.0)
plt.show()
