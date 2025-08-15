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


# 生成反向椭圆mask，中央椭圆留白，内容分布在外部
ellipse_width, ellipse_height = 1600, 800
# 椭圆尽可能铺满整个屏幕，只留极小边距
pad_x, pad_y = 30, 30
ellipse_img = Image.new('L', (ellipse_width, ellipse_height), 255)  # 先全白
draw = ImageDraw.Draw(ellipse_img)
draw.ellipse([(pad_x, pad_y), (ellipse_width-pad_x-1, ellipse_height-pad_y-1)], fill=0)  # 椭圆为黑
ellipse_mask = np.array(ellipse_img)

# 生成高分辨率椭圆词云，减小margin使内容更集中
wc = WordCloud(
	font_path='simkai.ttf',
	width=ellipse_width,
	height=ellipse_height,
	background_color='white',
	scale=2,
	mask=ellipse_mask,
	margin=0,
	max_words=1000,
	relative_scaling=0.2,
	collocations=False,
	prefer_horizontal=1.0
)
wc.generate_from_frequencies(dict_freq)

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

wc.recolor(color_func=BlueColorFunc())

# 显示并保存高分辨率词云
plt.figure(figsize=(16, 8), dpi=100)
plt.imshow(wc, interpolation='nearest')
plt.axis('off')
plt.tight_layout(pad=0)
plt.savefig('name_wordcloud.png', dpi=300, bbox_inches='tight', pad_inches=0.0)
plt.show()
