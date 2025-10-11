import pandas as pd
import matplotlib.pyplot as plt

# ========== 读取清洗后的数据 ==========
file_path = "./src/douban_top250.csv"   
df = pd.read_csv(file_path)

# 设置中文字体和负号正常显示
plt.rcParams['font.sans-serif'] = ['SimHei']  
plt.rcParams['axes.unicode_minus'] = False    


# ========== 合并4个分析为一个大图的4个子图 ==========
fig, axs = plt.subplots(2, 2, figsize=(14, 10))

# 1. 评分分布
df['score'].hist(bins=10, edgecolor='black', ax=axs[0,0])
axs[0,0].set_xlabel("评分")
axs[0,0].set_ylabel("电影数量")
axs[0,0].set_title("电影评分分布")

# 2. 国家分布（前10个，标签拆分）
from collections import Counter
country_counter = Counter()
df['country'].dropna().apply(lambda x: country_counter.update(x.split()))
pd.Series(country_counter).sort_values(ascending=False).head(10).plot(kind='bar', ax=axs[0,1])
axs[0,1].set_xlabel("国家")
axs[0,1].set_ylabel("电影数量")
axs[0,1].set_title("主要国家电影数量（前10）")

# 3. 类型分布（前10个，标签拆分）
genre_counter = Counter()
df['genre'].dropna().apply(lambda x: genre_counter.update(x.split()))
pd.Series(genre_counter).sort_values(ascending=False).head(10).plot(kind='bar', ax=axs[1,0])
axs[1,0].set_xlabel("类型")
axs[1,0].set_ylabel("电影数量")
axs[1,0].set_title("主要类型电影数量（前10）")

# 4. 年份趋势（按年份统计电影数量）
df['year'].value_counts().sort_index().plot(kind='line', marker='o', ax=axs[1,1])
axs[1,1].set_xlabel("年份")
axs[1,1].set_ylabel("电影数量")
axs[1,1].set_title("电影上映年份趋势")

plt.tight_layout()
plt.savefig("../images/basic_analysis.png", dpi=300)
plt.show()


