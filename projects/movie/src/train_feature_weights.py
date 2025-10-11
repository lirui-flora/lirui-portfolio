# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
import os
import matplotlib.pyplot as plt
from math import pi

# 设置中文显示
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False

# 设置输出目录
output_dir = "../machine"
if not os.path.exists(output_dir):
    os.makedirs(output_dir)
# 设置图片保存目录
images_dir = os.path.join(output_dir, "images")
if not os.path.exists(images_dir):
    os.makedirs(images_dir)

# ==================== 1. 读取数据 ==========
df = pd.read_csv("../cluster_movie_sentiment2.csv")
# 脱敏：使用相对路径读取本地数据文件
SRC_DIR = os.path.dirname(__file__)
PROJECT_ROOT = os.path.abspath(os.path.join(SRC_DIR, '..'))

# douban_top250.csv 位于 src/ 下
df_features = pd.read_csv(os.path.join(SRC_DIR, 'douban_top250.csv'))

# 合并数据
df = pd.merge(
    df[['movie', 'cluster']],
    df_features[['movie', 'year', 'score', 'director', 'genre', 'country']],
    on='movie',
    how='left'
)

# ==================== 特征处理 ==========
features = pd.DataFrame()

# 数值特征
features['score'] = df['score']
# 提取年份数字
df['year'] = df['year'].astype(str).str.extract(r'(\d{4})').astype(float)
features['year'] = df['year']

# 类型独热编码（前10个类型）
genre_counts = df['genre'].str.split(' ').explode().value_counts()
top_genres = genre_counts.head(10).index.tolist()
def unique_other(lst, top_list, other_name):
    mapped = [g if g in top_list else other_name for g in lst]
    # 保证'其他'只出现一次
    result = []
    seen_other = False
    for item in mapped:
        if item == other_name:
            if not seen_other:
                result.append(item)
                seen_other = True
        else:
            result.append(item)
    return result

genre_filtered = df['genre'].str.split(' ').apply(lambda x: unique_other(x, top_genres, '其他类型'))
genre_ohe = pd.get_dummies(genre_filtered.explode()).groupby(level=0).sum()

# 国家独热编码（前10个国家）
country_counts = df['country'].str.split(' ').explode().value_counts()
top_countries = country_counts.head(10).index.tolist()
country_filtered = df['country'].str.split(' ').apply(lambda x: unique_other(x, top_countries, '其他国家'))
country_ohe = pd.get_dummies(country_filtered.explode()).groupby(level=0).sum()

# 导演独热编码（前20个导演）
director_counts = df['director'].str.split(' ').explode().value_counts()
top_directors = director_counts.head(20).index.tolist()
director_filtered = df['director'].str.split(' ').apply(lambda x: unique_other(x, top_directors, '其他导演'))
director_ohe = pd.get_dummies(director_filtered.explode()).groupby(level=0).sum()

# 合并所有特征
X = pd.concat([features, genre_ohe, country_ohe, director_ohe], axis=1)
y = df['cluster']

# 标准化数值特征
scaler = StandardScaler()
X_scaled = pd.DataFrame(scaler.fit_transform(X), columns=X.columns)

# 分割训练集和测试集
X_train, X_test, y_train, y_test = train_test_split(X_scaled, y, test_size=0.2, random_state=42, stratify=y)

# ==================== 训练逻辑回归模型 ==========
lr = LogisticRegression(multi_class='ovr', max_iter=1000)
lr.fit(X_train, y_train)

# 评估逻辑回归模型
y_pred_lr = lr.predict(X_test)
print("\n逻辑回归模型评估:")
print(classification_report(y_test, y_pred_lr))

# 获取特征权重（对每个类取绝对值的平均）
lr_weights = np.abs(lr.coef_).mean(axis=0)
lr_feature_weights = pd.DataFrame({
    'feature': X.columns,
    'weight': lr_weights
}).sort_values('weight', ascending=False)

# ==================== 训练随机森林模型 ==========
rf = RandomForestClassifier(n_estimators=200, random_state=42)
rf.fit(X_train, y_train)

# 评估随机森林模型
y_pred_rf = rf.predict(X_test)
print("\n随机森林模型评估:")
print(classification_report(y_test, y_pred_rf))

# 获取特征重要性
rf_feature_weights = pd.DataFrame({
    'feature': X.columns,
    'importance': rf.feature_importances_
}).sort_values('importance', ascending=False)

# 保存特征权重
lr_feature_weights.to_csv(os.path.join(output_dir, 'feature_weights_lr.csv'))
rf_feature_weights.to_csv(os.path.join(output_dir, 'feature_weights_rf.csv'))

# 打印前20个最重要特征
print("\n逻辑回归模型 - 前20个最重要特征:")
print(lr_feature_weights.head(20))
print("\n随机森林模型 - 前20个最重要特征:")
print(rf_feature_weights.head(20))

# ==================== 可视化：雷达图展示前10特征 ====================
def plot_radar(feature_df, value_col, title, save_path):
    # 取前10特征
    top10 = feature_df.head(10)
    labels = top10['feature'].tolist()
    values = top10[value_col].tolist()
    # 闭合雷达图
    values += values[:1]
    labels += labels[:1]
    angles = [n / float(len(labels)) * 2 * pi for n in range(len(labels))]
    fig, ax = plt.subplots(figsize=(8, 6), subplot_kw=dict(polar=True))
    ax.plot(angles, values, linewidth=2, linestyle='solid', marker='o')
    ax.fill(angles, values, alpha=0.25)
    ax.set_thetagrids([a * 180/pi for a in angles], labels, fontsize=10)
    ax.set_title(title, fontsize=14)
    ax.grid(True)
    plt.tight_layout()
    plt.savefig(save_path, dpi=300, bbox_inches="tight")
    plt.close()
    print(f"已保存雷达图: {save_path}")

plot_radar(lr_feature_weights, 'weight', '逻辑回归特征权重Top10(雷达图)', os.path.join(images_dir, 'lr_feature_weights_radar.png'))
plot_radar(rf_feature_weights, 'importance', '随机森林特征重要性Top10(雷达图)', os.path.join(images_dir, 'rf_feature_importance_radar.png'))