import pandas as pd
import collections
import matplotlib.pyplot as plt
import matplotlib

# 设置matplotlib全局字体为simkai.ttf，防止中文乱码且为楷体
from matplotlib import font_manager
font_path = 'simkai.ttf'  # 请确保simkai.ttf在当前目录或指定路径
matplotlib.rcParams['font.sans-serif'] = ['simkai']
matplotlib.rcParams['font.family'] = 'sans-serif'
matplotlib.rcParams['axes.unicode_minus'] = False
font_manager.fontManager.addfont(font_path)

# 读取数据
df = pd.read_csv('姓名.csv')
name_col = df.columns[0]
names = df[name_col].dropna().astype(str)

# 统计所有长度为2及以上的词组频率
phrase_counter = collections.Counter()
for name in names:
	n = len(name)
	for l in range(2, n+1):  # 词组长度2到全名长度
		for i in range(n-l+1):
			phrase = name[i:i+l]
			phrase_counter[phrase] += 1

# 只保留出现次数大于1的词组
repeats = {k: v for k, v in phrase_counter.items() if v > 1}

# 取前20高频重复词组
top_n = 20
top_phrases = sorted(repeats.items(), key=lambda x: -x[1])[:top_n]

# 可视化
if top_phrases:
	from matplotlib import font_manager
	simkai_font = font_manager.FontProperties(fname='simkai.ttf')
	phrases, freqs = zip(*top_phrases)
	plt.figure(figsize=(12, 6))
	bars = plt.bar(range(len(phrases)), freqs, color='#00A7EB')
	plt.xticks(range(len(phrases)), phrases, fontproperties=simkai_font, fontsize=14, rotation=45, ha='right')
	plt.ylabel('出现次数', fontsize=14, fontproperties=simkai_font)
	plt.title('高频重复的姓名', fontsize=16, fontproperties=simkai_font)
	plt.tight_layout()
	plt.savefig('name_repeat_bar.png', dpi=200)
	plt.show()
else:
	print('没有重复词组（长度≥2，出现次数>1）')
