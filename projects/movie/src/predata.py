import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

# ==================== 创建保存图片目录 ====================
os.makedirs("../images", exist_ok=True)

# ==================== 中文显示 ====================
plt.rcParams['font.sans-serif'] = ['SimHei']   # 黑体
plt.rcParams['axes.unicode_minus'] = False     # 解决负号显示问题

# ==================== 读取数据 ====================
df = pd.read_csv("douban_top250.csv")

# -------------------- 数据清洗 --------------------
df = df.drop_duplicates()
df["score"] = pd.to_numeric(df["score"], errors="coerce")
df["comment"] = df["comment"].astype(str).str.replace("人评价", "", regex=False)
df["comment"] = pd.to_numeric(df["comment"], errors="coerce")
df["summary"] = df["summary"].fillna("")

# ==================== 绘制大图 ====================
fig, axes = plt.subplots(1, 3, figsize=(24, 6))  # 1行3列

# 1. 评分分布
sns.histplot(df["score"], bins=10, kde=True, ax=axes[0], color='skyblue')
axes[0].set_title("豆瓣Top250评分分布")
axes[0].set_xlabel("评分")
axes[0].set_ylabel("电影数量")

# 2. 评价人数分布
sns.histplot(df["comment"], bins=20, kde=True, ax=axes[1], color='lightgreen')
axes[1].set_title("豆瓣Top250评价人数分布")
axes[1].set_xlabel("评价人数")
axes[1].set_ylabel("电影数量")

# 3. 评分 vs 评价人数
sns.scatterplot(data=df, x="comment", y="score", alpha=0.6, ax=axes[2], color='orange')
axes[2].set_title("评分与评价人数关系")
axes[2].set_xlabel("评价人数")
axes[2].set_ylabel("评分")
axes[2].set_xscale("log")  # 对数刻度，更清晰

plt.tight_layout()
plt.savefig('../images/basic/basic_information.png', dpi=300, bbox_inches='tight')
print("📸 图表已保存到: ./images/basic/basic_information.png")

# ==================== 保存清洗后的数据 ====================
df.to_csv("douban_top250.csv", index=False)
print("✅ 清洗后的数据已保存到: douban_top250.csv")

# ==================== 拆分热评并保存 ====================
if 'hot_comments' in df.columns:
    long_comments = []
    for _, row in df.iterrows():
        movie = row['movie'] if 'movie' in row else None
        comments = str(row['hot_comments']).split('|')
        for c in comments:
            c = c.strip()
            if c:
                long_comments.append({'movie': movie, 'hot_comment': c})
    long_comments_df = pd.DataFrame(long_comments)
    long_comments_df.to_csv("douban_top250_long_comments.csv", index=False)
    print("✅ 热评已拆分并保存到: douban_top250_long_comments.csv")
else:
    print("⚠️ 未找到 'hot_comments' 列，未生成热评拆分文件。")