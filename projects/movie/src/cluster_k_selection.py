import os
os.environ["OMP_NUM_THREADS"] = "1"
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
from sklearn.decomposition import TruncatedSVD
from sklearn.manifold import TSNE
import matplotlib.pyplot as plt
from wordcloud import WordCloud
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
from collections import Counter

# 设置中文显示
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False

# ========== 1. 读取数据 ==========
df = pd.read_csv("douban_top250.csv")

# ========== 特征处理 ==========
features = pd.DataFrame()
features['score'] = df['score']

# 标准化评分
scaler = StandardScaler()
features_num_scaled = pd.DataFrame(scaler.fit_transform(features[['score']]), columns=['score'])

# 年代独热编码
df['decade'] = (pd.to_numeric(df['year'], errors='coerce').fillna(0) // 10 * 10).astype(int)
decade_ohe = pd.get_dummies(df['decade'].astype(str)) * 0.5

# 类型独热编码（前10+其他）以空格为分隔符
genre_counts = df['genre'].str.split(' ').explode().value_counts()
top_genres = genre_counts.head(10).index.tolist()
def genre_with_other(genres):
    return [g if g in top_genres else '其他类型' for g in genres]
genre_filtered = df['genre'].str.split(' ').apply(genre_with_other)
genre_ohe = pd.get_dummies(genre_filtered.explode()).groupby(level=0).sum() * 2

# 国家独热编码（前10+其他）
country_counts = df['country'].str.split(' ').explode().value_counts()
top_countries = country_counts.head(10).index.tolist()
def country_with_other(countries):
    return [c if c in top_countries else '其他国家' for c in countries]
country_filtered = df['country'].str.split(' ').apply(country_with_other)
country_ohe = pd.get_dummies(country_filtered.explode()).groupby(level=0).sum() * 0.5

# 拼接所有类别特征
categorical_features = pd.concat([decade_ohe, genre_ohe, country_ohe], axis=1)

# 对类别特征做 TruncatedSVD 降维
svd = TruncatedSVD(n_components=10, random_state=42)
categorical_svd = pd.DataFrame(svd.fit_transform(categorical_features),
                               columns=[f'SVD{i+1}' for i in range(10)])

# 最终特征矩阵
X = pd.concat([features_num_scaled, categorical_svd], axis=1).values

# ========== 2. 聚类数选择 ==========
inertia_list, silhouette_list = [], []
K_range = range(3, 15)

for k in K_range:
    kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
    labels = kmeans.fit_predict(X)
    inertia_list.append(kmeans.inertia_)
    silhouette_list.append(silhouette_score(X, labels))

fig, axs = plt.subplots(1, 2, figsize=(14, 6))
axs[0].plot(K_range, inertia_list, '-o', color='C0')
axs[0].set_title("肘部法选择聚类数")
axs[0].set_xlabel("K")
axs[0].set_ylabel("SSE (Inertia)")
axs[1].plot(K_range, silhouette_list, '-o', color='orange')
axs[1].set_title("轮廓系数选择聚类数")
axs[1].set_xlabel("K")
axs[1].set_ylabel("Silhouette 系数")
plt.tight_layout()
os.makedirs("../images", exist_ok=True)
plt.savefig("../images/cluster_k_selection.png", dpi=300, bbox_inches='tight')
plt.close()

best_k = int(input("请查看 ../images/cluster_k_selection.png，然后输入最合适的 K 值: "))

# ========== 3. 最佳K下聚类 ==========
kmeans = KMeans(n_clusters=best_k, random_state=42, n_init=10)
labels = kmeans.fit_predict(X)
df[f'cluster_{best_k}'] = labels

# ========== 4. t-SNE 可视化 ==========
print("正在计算 t-SNE，请稍等...")
tsne = TSNE(n_components=2, random_state=42, perplexity=30, n_iter=1000)
X_tsne = tsne.fit_transform(X)

plt.figure(figsize=(8,6))
sc = plt.scatter(X_tsne[:,0], X_tsne[:,1], c=labels, cmap="rainbow", alpha=0.7)
plt.colorbar(sc, label="簇编号")
plt.title(f"t-SNE降维后聚类结果 (K={best_k})")
plt.savefig(f"../images/tsne_cluster_K{best_k}.png", dpi=300, bbox_inches='tight')
plt.show()

# ========== 5. 各簇类型/国家Top10 ==========
cluster_type_dist = pd.DataFrame()
cluster_country_dist = pd.DataFrame()
for i in range(best_k):
    vc_type = df[df[f'cluster_{best_k}']==i]['genre'].str.split(' ').explode().value_counts()
    vc_type_top = vc_type.loc[vc_type.index.isin(top_genres)].head(10)
    vc_type_top['其他类型'] = vc_type[~vc_type.index.isin(top_genres)].sum()
    
    vc_country = df[df[f'cluster_{best_k}']==i]['country'].str.split(' ').explode().value_counts()
    vc_country_top = vc_country.loc[vc_country.index.isin(top_countries)].head(10)
    vc_country_top['其他国家'] = vc_country[~vc_country.index.isin(top_countries)].sum()
    
    cluster_type_dist[f'簇{i}'] = vc_type_top.fillna(0)
    cluster_country_dist[f'簇{i}'] = vc_country_top.fillna(0)

# ========== 6. 簇详细信息统计 ==========
cluster_info = {}
for i in range(best_k):
    cluster_df = df[df[f'cluster_{best_k}'] == i]
    type_counts = cluster_df['genre'].str.split(' ').explode().value_counts()
    movie_examples = cluster_df['movie'].head(5).tolist()
    cluster_info[i] = {
        '类型统计': type_counts,
        '示例电影': movie_examples,
        '簇大小': len(cluster_df)
    }

for i, info in cluster_info.items():
    print(f"\n簇{i} (共{info['簇大小']}部电影)")
    print("类型统计（前10）：")
    print(info['类型统计'].head(10))
    print("示例电影（5部）：", info['示例电影'])

# ========== 7. 类型/国家分布可视化 ==========
fig, axs = plt.subplots(2, 2, figsize=(16, 12))
cluster_type_dist.plot(kind='bar', ax=axs[0,0], title=f'各簇类型Top10分布 (K={best_k})')
axs[0,0].tick_params(axis='x', labelrotation=45)

cluster_country_dist.plot(kind='bar', ax=axs[0,1], title=f'各簇国家Top10分布 (K={best_k})')
axs[0,1].tick_params(axis='x', labelrotation=45)

axs[1,0].axis('off')
text = "\n".join([f"簇{i}：共{info['簇大小']}部\n示例：{', '.join(info['示例电影'])}" 
                  for i, info in cluster_info.items()])
axs[1,0].text(0.05, 0.5, text, fontsize=12, va="center")

axs[1,1].axis('off')
axs[1,1].text(0.3, 0.5, "聚类统计完成 ✅", fontsize=16, va="center")

plt.tight_layout()
plt.savefig(f"../images/cluster_all_in_one_K{best_k}.png", dpi=300, bbox_inches='tight')
plt.show()

# ========== 8. 为每个簇生成词云并记录电影名称及词频 ==========
# 创建保存词云的目录
wordcloud_dir = f"../images/wordcloud_K{best_k}"
os.makedirs(wordcloud_dir, exist_ok=True)

# 打开文件记录每簇的电影名称及词频
with open('../data/wordcloud.txt', 'w', encoding='utf-8') as f:
    for i in range(best_k):
        # 提取当前簇的电影数据
        cluster_df = df[df[f'cluster_{best_k}'] == i]

        # 提取所有电影的 hot_word 并统计词频
        all_hot_words = ' '.join(cluster_df['hot_word'].dropna().astype(str))
        word_list = all_hot_words.split()
        word_freq = Counter(word_list)
        top_50_words = word_freq.most_common(50)

        # 生成词云
        wordcloud = WordCloud(
            width=800, height=400,
            background_color='white',
            font_path='msyh.ttc',  # 确保字体路径正确
            max_words=50
        ).generate_from_frequencies(dict(top_50_words))

        # 保存词云图片
        wordcloud_path = os.path.join(wordcloud_dir, f'cluster_{i}_wordcloud.png')
        wordcloud.to_file(wordcloud_path)

        # 写入文件记录电影名称及词频
        f.write(f'簇{i}：\n')
        f.write('电影名称：\n')
        f.write(', '.join(cluster_df['movie']) + '\n')
        f.write('词频：\n')
        f.write(', '.join([f'{word}: {freq}' for word, freq in top_50_words]) + '\n\n')

        print(f"簇{i}的词云已保存到 {wordcloud_path}")

print("所有簇的词云生成完成，并记录到 ../data/wordcloud.txt ✅")
