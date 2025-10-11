import pandas as pd
import matplotlib.pyplot as plt
import os

# ==================== 中文显示 ====================
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False

SRC_DIR = os.path.dirname(__file__)
PROJECT_ROOT = os.path.abspath(os.path.join(SRC_DIR, '..'))

# ==================== 1. 读取数据 ====================
summary_file = os.path.join(PROJECT_ROOT, 'processed_files', 'confidence_movies_summary1.csv')
df_summary = pd.read_csv(summary_file)

# ==================== 2. 按电影聚合 ====================
df_final = df_summary.groupby(["movie", "sentiment"]).agg(
    total_count=("count", "sum"),
    weighted_confidence=("avg_confidence", 
                         lambda x: (x * df_summary.loc[x.index, "count"]).sum())
).reset_index()

# 避免除以 0
df_final["avg_confidence"] = df_final.apply(
    lambda row: row["weighted_confidence"] / row["total_count"] if row["total_count"] > 0 else 0,
    axis=1
)

# 转为透视表
pivot = df_final.pivot(index="movie", columns="sentiment", values=["total_count", "avg_confidence"]).fillna(0)

# ==================== 3. 判定最终情感标签 ====================
def decide_final(row):
    pos_count = row[("total_count", "positive (stars 4 and 5)")]
    neg_count = row[("total_count", "negative (stars 1, 2 and 3)")]
    if pos_count > neg_count:
        return "Positive"
    elif neg_count > pos_count:
        return "Negative"
    else:
        return "Positive" if row[("avg_confidence", "positive (stars 4 and 5)")] >= row[("avg_confidence", "negative (stars 1, 2 and 3)")] else "Negative"

pivot["Final_Sentiment"] = pivot.apply(decide_final, axis=1)

# ==================== 4. 保存结果 ====================
output_file = os.path.join(PROJECT_ROOT, 'final_movie_sentiment1.csv')
pivot.to_csv(output_file, encoding="utf-8-sig")
print(f"✅ 最终电影情感标签已保存到 {output_file}")

# ==================== 5. 可视化最终标签分布 ====================
images_dir = os.path.join(PROJECT_ROOT, 'machine', 'images')
os.makedirs(images_dir, exist_ok=True)

final_counts = pivot["Final_Sentiment"].value_counts()

plt.figure(figsize=(6,4))
final_counts.plot(kind="bar", color=["#4CAF50", "#F44336"])  # 绿色=正向，红色=负向
plt.title("电影最终情感标签分布")
plt.xlabel("情感标签")
plt.ylabel("电影数量")
plt.xticks(rotation=0)
plt.tight_layout()
plt.savefig(os.path.join(images_dir, "final_movie_sentiment1.png"))
plt.close()

print(f"✅ 最终情感标签分布图已保存到 {os.path.join(images_dir, 'final_movie_sentiment1.png')}")
