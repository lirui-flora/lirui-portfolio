import pandas as pd
import matplotlib.pyplot as plt
import os

# ==================== 中文显示 ====================
plt.rcParams['font.sans-serif'] = ['SimHei']   # 黑体
plt.rcParams['axes.unicode_minus'] = False     # 解决负号显示问题

# ==================== 1. 读取簇-电影映射 ====================
# 先把簇的txt文件整理成 {cluster: [电影名,...]} 的结构
clusters = {
    0: ["辛德勒的名单", "当幸福来敲门", "末代皇帝", "活着", "乱世佳人", "摔跤吧！爸爸", "钢琴家", "绿皮书", "音乐之声", "西西里的美丽传说", "小鞋子", "断背山", "勇敢的心", "倩女幽魂", "喜宴", "模仿游戏", "射雕英雄传之东成西就", "血战钢锯岭", "达拉斯买家俱乐部", "卢旺达饭店", "东邪西毒", "波西米亚狂想曲", "奇迹男孩", "隐藏人物"],
    1: ["疯狂动物城", "机器人总动员", "寻梦环游记", "哈利·波特与魔法石", "龙猫", "哈尔的移动城堡", "天空之城", "狮子王", "哈利·波特与死亡圣器(下)", "哈利·波特与阿兹卡班的囚徒", "哈利·波特与密室", "加勒比海盗", "幽灵公主", "哈利·波特与火焰杯", "借东西的小人阿莉埃蒂", "头脑特工队", "驯龙高手", "玩具总动员3", "怪兽电力公司", "哪吒闹海", "神偷奶爸", "心灵奇旅", "疯狂原始人", "风之谷", "无敌破坏王", "冰川时代", "魔女宅急便", "哈利·波特与死亡圣器(上)", "崖上的波妞", "哈利·波特与凤凰社", "冰雪奇缘"],
    2: ["阿甘正传", "千与千寻", "忠犬八公的故事", "熔炉", "触不可及", "指环王3：王者无敌", "我不是药神", "飞屋环游记", "十二怒汉", "素媛", "鬼子来了", "少年派的奇幻漂流", "指环王2：双塔奇兵", "死亡诗社", "何以为家", "闻香识女人", "指环王1：护戒使者", "辩护人", "窃听风暴", "飞越疯人院", "布达佩斯大饭店", "心灵捕手", "超脱", "狩猎", "寄生虫", "入殓师", "菊次郎的夏天", "无人知晓", "小森林 夏秋篇", "一个叫欧维的男人决定去死", "小森林 冬春篇", "玛丽和麦克斯", "七武士", "阳光姐妹淘", "背靠背，脸对脸", "东京教父", "忠犬八公物语", "遗愿清单", "大佛普拉斯", "白日梦想家", "大红灯笼高高挂", "雨人"],
    3: ["怦然心动", "罗马假日", "天堂电影院", "本杰明·巴顿奇事", "情书", "喜剧之王", "摩登时代", "甜蜜蜜", "爱在黎明破晓前", "爱在日落黄昏时", "重庆森林", "剪刀手爱德华", "时空恋旅人", "花样年华", "阳光灿烂的日子", "傲慢与偏见", "天使爱美丽", "侧耳倾听", "色，戒", "请以你的名字呼唤我", "幸福终点站", "萤火之森", "大鱼", "你的名字。", "爱在午夜降临前", "芙蓉镇", "贫民窟的百万富翁", "花束般的恋爱", "城市之光", "青蛇", "爱乐之城", "初恋这件小事", "真爱至上", "恋恋笔记本", "千年女优", "魂断蓝桥"],
    4: ["搏击俱乐部", "看不见的客人", "蝴蝶效应", "禁闭岛", "致命魔术", "杀人回忆", "致命ID", "红辣椒", "七宗罪", "第六感", "未麻的部屋", "消失的爱人", "告白", "惊魂记", "电锯惊魂", "谍影重重3", "记忆碎片", "恐怖游轮", "源代码", "黑天鹅", "彗星来的那一夜", "谍影重重2", "血钻", "谍影重重"],
    5: ["黑客帝国", "阿凡达", "超能陆战队", "被解救的姜戈", "釜山行", "头号玩家", "黑客帝国3：矩阵革命", "2001太空漫游", "疯狂的麦克斯4：狂暴之路", "终结者2：审判日", "新龙门客栈", "火星救援", "黑客帝国2：重装上阵", "蜘蛛侠：平行宇宙", "攻壳机动队"],
    6: ["霸王别姬", "泰坦尼克号", "美丽人生", "星际穿越", "盗梦空间", "楚门的世界", "海上钢琴师", "三傻大闹宝莱坞", "放牛班的春天", "大话西游之大圣娶亲", "让子弹飞", "海蒂和爷爷", "大话西游之月光宝盒", "大闹天宫", "饮食男女", "美丽心灵", "穿条纹睡衣的男孩", "拯救大兵瑞恩", "一一", "还有明天", "春光乍泄", "海豚湾", "唐伯虎点秋香", "7号房的礼物", "天书奇谭", "被嫌弃的松子的一生", "茶馆", "九品芝麻官", "我是山姆", "海街日记", "雨中曲", "高山下的花环", "机器人之梦", "岁月神偷", "你看起来好像很好吃", "爆裂鼓手", "人工智能", "虎口脱险", "千钧一发", "海边的曼彻斯特", "萤火虫之墓", "步履不停", "房间"],
    7: ["肖申克的救赎", "这个杀手不太冷", "无间道", "控方证人", "教父", "蝙蝠侠：黑暗骑士", "猫鼠游戏", "教父2", "两杆大烟枪", "功夫", "沉默的羔羊", "低俗小说", "美国往事", "蝙蝠侠：黑暗骑士崛起", "完美的世界", "新世界", "教父3", "恐怖直播", "三块广告牌", "小丑", "无间道2", "绿里奇迹", "末路狂花", "疯狂的石头", "上帝之城", "英雄本色", "心迷宫", "纵横四海", "小偷家族", "牯岭街少年杀人事件", "荒蛮故事", "可可西里", "无耻混蛋", "罗生门", "战争之王"]
}

# 转成 DataFrame
cluster_rows = []
for cid, movies in clusters.items():
    for m in movies:
        cluster_rows.append((cid, m))
df_clusters = pd.DataFrame(cluster_rows, columns=["cluster", "movie"])

# ==================== 2. 读取电影最终情感标签 ====================
# 使用相对路径以避免泄露本地绝对路径
SRC_DIR = os.path.dirname(__file__)
PROJECT_ROOT = os.path.abspath(os.path.join(SRC_DIR, '..'))

# 修复列名错位问题
final_sentiment_file = os.path.join(PROJECT_ROOT, 'final_movie_sentiment2.csv')
df_sentiment = pd.read_csv(final_sentiment_file, index_col=0)

# 将索引重命名为 movie
df_sentiment.index.name = "movie"
df_sentiment = df_sentiment.reset_index()

# 调试：打印列名
print("df_sentiment 列名:", df_sentiment.columns)

# 保证列名对应，去除空格
# 去除电影名中的前后空格，避免匹配失败
df_sentiment["movie"] = df_sentiment["movie"].str.strip()

# 只保留电影名和最终标签
df_sentiment = df_sentiment[["movie", "Final_Sentiment"]]

# ==================== 3. 合并两个文件 ====================
df_clusters["movie"] = df_clusters["movie"].astype(str).str.strip()
df_sentiment["movie"] = df_sentiment["movie"].astype(str)

df_merge = pd.merge(df_clusters, df_sentiment, on="movie", how="left")

# 填充缺失值
df_merge["Final_Sentiment"] = df_merge["Final_Sentiment"].fillna("Unknown")

# 保存合并结果（写入项目根或 machine 子目录）
output_file = os.path.join(PROJECT_ROOT, 'cluster_movie_sentiment2.csv')
df_merge.to_csv(output_file, index=False, encoding="utf-8-sig")
print(f"簇-电影-情感标签文件已保存到 {output_file}")

# ==================== 4. 统计每个簇内正负数量 ====================
stats = df_merge.groupby(["cluster", "Final_Sentiment"]).size().unstack(fill_value=0)

# 确保 stats 包含数值数据
stats = stats.apply(pd.to_numeric, errors="coerce", axis=1)

# 保存统计结果
stats_file = os.path.join(PROJECT_ROOT, 'cluster_sentiment_stats2.csv')
stats.to_csv(stats_file, encoding="utf-8-sig")
print(f"簇情感统计结果已保存到 {stats_file}")

# ==================== 5. 可视化 ====================
os.makedirs("./images", exist_ok=True)

stats.plot(kind="bar", stacked=True, figsize=(10,6), color=["#4CAF50", "#F44336", "#9E9E9E"])
plt.title("各簇电影情感分布")
plt.xlabel("簇编号")
plt.ylabel("电影数量")
plt.xticks(rotation=0)
plt.legend(title="情感标签")
plt.tight_layout()
images_dir = os.path.join(PROJECT_ROOT, 'images')
os.makedirs(images_dir, exist_ok=True)
plt.savefig(os.path.join(images_dir, 'cluster_sentiment_distribution2.png'))
plt.close()

print(f"可视化已保存到 {os.path.join(images_dir, 'cluster_sentiment_distribution2.png')}")
