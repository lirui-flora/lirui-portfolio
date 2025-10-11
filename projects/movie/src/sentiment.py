
import os
import pandas as pd
from transformers import pipeline
import matplotlib.pyplot as plt
import seaborn as sns

# ==================== 中文显示 ====================
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False

# ----------------------------
# 0. 配置 Hugging Face 缓存路径（脱敏）
# 优先使用已设置的环境变量；若未设置，则在项目中建立 `.cache/huggingface`
# ----------------------------
SRC_DIR = os.path.dirname(__file__)
PROJECT_ROOT = os.path.abspath(os.path.join(SRC_DIR, '..'))

default_hf_cache = os.path.join(PROJECT_ROOT, '.cache', 'huggingface')
os.environ.setdefault("TRANSFORMERS_CACHE", os.environ.get("TRANSFORMERS_CACHE", default_hf_cache))
os.environ.setdefault("HF_HOME", os.environ.get("HF_HOME", default_hf_cache))

# ----------------------------
# 1. 读取 CSV 文件
# ----------------------------
csv_file = os.path.join(SRC_DIR, 'douban_top250.csv')
df = pd.read_csv(csv_file)
print(f"总电影条目数: {len(df)}")

# ----------------------------
# 1.1 拆分 hot_comments 多条评论
# ----------------------------
df["hot_comments"] = df["hot_comments"].fillna("")
df_expanded = df.assign(hot_comments=df["hot_comments"].str.split('|')).explode("hot_comments")
df_expanded["hot_comments"] = df_expanded["hot_comments"].str.strip()
print(f"拆分后评论总条数: {len(df_expanded)}")

# ----------------------------
# 2. 加载中文情感分析模型
# ----------------------------
print("加载模型中...")
classifier = pipeline(
    "sentiment-analysis",
    model="IDEA-CCNL/Erlangshen-Roberta-110M-Sentiment",
    tokenizer="IDEA-CCNL/Erlangshen-Roberta-110M-Sentiment",
    device=-1
)# 这个模型2更合适，适合影片类评论
# classifier = pipeline(
#     "sentiment-analysis",
#     model="uer/roberta-base-finetuned-dianping-chinese",
#     tokenizer="uer/roberta-base-finetuned-dianping-chinese",
#     device=-1
# )#这个是模型1，基于大众点评服务类评论的，可能不太适合电影评论

# ----------------------------
# 3. 批量分析评论
# ----------------------------
results = classifier(df_expanded["hot_comments"].tolist(),
                     truncation=True, max_length=512, batch_size=16)
df_expanded["sentiment"] = [r["label"] for r in results]
df_expanded["confidence"] = [r["score"] for r in results]

# ----------------------------
# 4. 保存每条评论分析结果
# ----------------------------
output_file = os.path.join(PROJECT_ROOT, 'comments_sentiment1.csv')
df_expanded.to_csv(output_file, index=False)
print(f"每条评论分析结果已保存到 {output_file}")

# ----------------------------
# 5. 按电影汇总正负情感和置信度区间
# ----------------------------
bins = [0.0, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
labels = ["0.0-0.5","0.5-0.6","0.6-0.7","0.7-0.8","0.8-0.9","0.9-1.0"]
df_expanded["conf_interval"] = pd.cut(df_expanded["confidence"], bins=bins, labels=labels, include_lowest=True)

# 按电影、情感、置信度区间统计数量和平均置信度
df_summary = df_expanded.groupby(["movie","conf_interval","sentiment"]).agg(
    count=("hot_comments","count"),
    avg_confidence=("confidence","mean")
).reset_index()

summary_file = os.path.join(PROJECT_ROOT, 'confidence_movies_summary1.csv')
df_summary.to_csv(summary_file, index=False)
print(f"按电影和置信度区间汇总的电影信息已保存到 {summary_file}")

# ----------------------------
# 6. 可视化总体评论情感分布
# ----------------------------
images_dir = "./images"
os.makedirs(images_dir, exist_ok=True)

plt.figure(figsize=(6,4))
sns.countplot(x="sentiment", data=df_expanded)
plt.title("评论情感分布")
plt.xlabel("情感")
plt.ylabel("数量")
plt.tight_layout()
plt.savefig(os.path.join(images_dir, "overall_sentiment.png"))
plt.close()

# ----------------------------
# 7. 查询功能：输出电影正负情感和置信度区间
# ----------------------------
while True:
    movie_name = input("请输入电影名查询正负情感统计（输入'q'退出）：")
    if movie_name.lower() == 'q':
        break
    subset = df_summary[df_summary["movie"].str.contains(movie_name, case=False, na=False)]
    if subset.empty:
        print("未找到该电影。")
    else:
        print(f"{movie_name} 各置信度区间的情感统计：")
        print(subset.pivot(index="conf_interval", columns="sentiment", values=["count","avg_confidence"]).fillna(0))
