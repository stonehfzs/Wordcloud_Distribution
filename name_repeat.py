import pandas as pd
import collections
import matplotlib.pyplot as plt
import matplotlib

# 设置matplotlib负号正常显示
import matplotlib
matplotlib.rcParams['axes.unicode_minus'] = False

# 读取数据
df = pd.read_csv('姓名+专业.csv')


# 只统计名字最后两个字的重复情况
from collections import defaultdict
name_major = df[['姓名', '专业']].dropna()
last2_major_dict = defaultdict(set)
for _, row in name_major.iterrows():
	name = str(row['姓名'])
	major = str(row['专业'])
	if len(name) >= 2:
		last2 = name[-2:]
		last2_major_dict[last2].add(major)

# 只保留出现在多个专业中的重复后两字
repeats = {k: v for k, v in last2_major_dict.items() if len(v) > 1}

if repeats:
	# 统计每个重复后两字在各专业的出现次数
	from collections import Counter
	last2_major_count = {k: Counter() for k in repeats}
	for _, row in name_major.iterrows():
		name = str(row['姓名'])
		major = str(row['专业'])
		if len(name) >= 2:
			last2 = name[-2:]
			if last2 in repeats:
				last2_major_count[last2][major] += 1

	# 显示所有重复的后两字
	top_phrases = sorted(last2_major_count.items(), key=lambda x: -sum(x[1].values()))
	# 专业列表
	all_majors = sorted({m for c in last2_major_count.values() for m in c})
	# 颜色映射
	import matplotlib.pyplot as plt
	import matplotlib
	from matplotlib import font_manager
	import numpy as np
	simkai_font = font_manager.FontProperties(fname='simkai.ttf')
	color_map = plt.get_cmap('tab10')
	major_colors = {m: color_map(i % 10) for i, m in enumerate(all_majors)}

	# 构造堆叠条形图数据
	ind = np.arange(len(top_phrases))
	bottom = np.zeros(len(top_phrases))
	plt.figure(figsize=(14, 7))
	for major in all_majors:
		values = [c[1][major] if major in c[1] else 0 for c in top_phrases]
		plt.bar(ind, values, bottom=bottom, color=major_colors[major], label=major)
		bottom += values
	# 横坐标横放
	plt.xticks(ind, [c[0] for c in top_phrases], fontproperties=simkai_font, fontsize=18, rotation=0, ha='center')
	# 纵坐标整数刻度，字体统一
	from matplotlib.ticker import MaxNLocator
	ax = plt.gca()
	ax.yaxis.set_major_locator(MaxNLocator(integer=True))
	for label in ax.get_yticklabels():
		label.set_fontproperties(simkai_font)
		label.set_fontsize(14)
	plt.ylabel('出现次数', fontsize=18, fontproperties=simkai_font)
	# 标题更大
	# 用suptitle设置大标题，确保字体大小生效
	plt.suptitle('后两字重复的名字', fontsize=28, fontproperties=simkai_font, y=0.98)
	plt.tight_layout(rect=[0, 0, 1, 0.95])
	plt.legend(fontsize=12, prop=simkai_font)
	plt.tight_layout()
	plt.savefig('name_repeat_major_bar.png', dpi=200, transparent=True)
	plt.show()
else:
	print('没有重复姓名后两字分布于不同专业的情况')
