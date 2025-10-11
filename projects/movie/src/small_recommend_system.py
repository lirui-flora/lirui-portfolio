#用Jaccard相似系数结合机器学习特征权重（即逻辑回归和随机森林，文件路径为"../machine/feature_weights_lr.csv"和"../machine/feature_weights_rf.csv"），实现基于内容的电影推荐
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
import joblib
import os

# 读取数据
SRC_DIR = os.path.dirname(__file__)
df = pd.read_csv(os.path.join(SRC_DIR, 'douban_top250.csv'))
df_cluster = pd.read_csv("../cluster_movie_sentiment2.csv")

# 合并聚类信息
df = pd.merge(df, df_cluster[['movie', 'cluster']], on='movie', how='left')

# 预处理：将类型标签、导演、国家等按空格拆分为集合
df['genre_set'] = df['genre'].fillna('').apply(lambda x: set(x.split()))
df['director_set'] = df['director'].fillna('').apply(lambda x: set(x.replace('导演:', '').split()))
df['country_set'] = df['country'].fillna('').apply(lambda x: set(x.split()))
df['year'] = df['year'].fillna('').astype(str)

def jaccard(set1, set2):
	if not set1 or not set2:
		return 0.0
	return len(set1 & set2) / len(set1 | set2)

def year_sim(y1, y2):
	# 年份越接近分数越高，差距10年内线性衰减
	try:
		y1 = int(y1)
		y2 = int(y2)
		diff = abs(y1 - y2)
		return max(0, 1 - diff / 10)
	except:
		return 0

# 加载特征权重
def load_feature_weights():
    weights = {}
    # 加载逻辑回归权重
    lr_weights = pd.read_csv("../machine/feature_weights_lr.csv", index_col=0)
    weights['lr'] = lr_weights['weight'].to_dict()
    
    # 加载随机森林特征重要性
    rf_weights = pd.read_csv("../machine/feature_weights_rf.csv", index_col=0)
    weights['rf'] = rf_weights['importance'].to_dict()
    
    return weights

def get_feature_weight(feature_name, weights):
    # 综合两个模型的权重，可以调整两个模型的重要性
    lr_weight = weights['lr'].get(feature_name, 0)
    rf_weight = weights['rf'].get(feature_name, 0)
    return 0.6 * lr_weight + 0.4 * rf_weight  # 逻辑回归权重稍大，保证可解释性

def content_similarity(row, target, feature_weights):
    # 基础相似度计算
    genre_sim = jaccard(row['genre_set'], target['genre_set'])
    director_sim = jaccard(row['director_set'], target['director_set'])
    country_sim = jaccard(row['country_set'], target['country_set'])
    year_similarity = year_sim(row['year'], target['year'])
    
    # 获取特征权重
    genre_weight = get_feature_weight('genre', feature_weights)
    director_weight = get_feature_weight('director', feature_weights)
    country_weight = get_feature_weight('country', feature_weights)
    year_weight = get_feature_weight('year', feature_weights)
    
    # 簇的相似度（如果在同一个簇中，增加相似度）
    cluster_bonus = 0.2 if row['cluster'] == target['cluster'] else 0
    
    # 加权融合（权重归一化）
    total_weight = genre_weight + director_weight + country_weight + year_weight
    if total_weight == 0:
        weights = [0.5, 0.2, 0.2, 0.1]  # 默认权重
    else:
        weights = [
            genre_weight/total_weight,
            director_weight/total_weight,
            country_weight/total_weight,
            year_weight/total_weight
        ]
    
    similarity = (
        weights[0] * genre_sim +
        weights[1] * director_sim +
        weights[2] * country_sim +
        weights[3] * year_similarity +
        cluster_bonus
    )
    
    return similarity, weights

def recommend_by_content(movie_name, topn=3):
    target = df[df['movie'] == movie_name]
    if target.empty:
        print(f"未找到电影：{movie_name}")
        return
    
    # 加载特征权重
    feature_weights = load_feature_weights()
    
    target_row = target.iloc[0]
    # 计算综合相似度和获取权重
    similarities = []
    for _, row in df.iterrows():
        if row['movie'] != movie_name:
            sim, weights = content_similarity(row, target_row, feature_weights)
            similarities.append({
                'movie': row['movie'],
                'similarity': sim,
                'year': row['year'],
                'country': row['country'],
                'genre': row['genre'],
                'score': row['score'],
                'link': row['link'],
                'weights': weights
            })
    
    # 排序并获取推荐
    recs = pd.DataFrame(similarities).sort_values(by=['similarity','score'], ascending=[False,False]).head(topn)
    
    if recs.empty:
        print("没有找到合适的推荐。")
        return
        
    print(f"\n为你推荐与《{movie_name}》内容最相似的{topn}部电影：")
    print(f"目标电影信息：")
    print(f"年份:{target_row['year']}  国家:{target_row['country']}  类型:{target_row['genre']}  评分:{target_row['score']}")
    print("\n推荐电影：")
    
    for _, row in recs.iterrows():
        print(f"\n{row['movie']}")
        print(f"相似度: {row['similarity']:.3f}")
        print(f"年份:{row['year']}  国家:{row['country']}  类型:{row['genre']}  评分:{row['score']}")
        print(f"特征权重: 类型({row['weights'][0]:.2f}) 导演({row['weights'][1]:.2f}) "
              f"国家({row['weights'][2]:.2f}) 年份({row['weights'][3]:.2f})")
        print(f"链接:{row['link']}")

if __name__ == "__main__":
	name = input("请输入电影名称：")
	recommend_by_content(name)
