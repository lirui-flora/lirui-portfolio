#pip install jieba -i https://pypi.tuna.tsinghua.edu.cn/simple
import string
import re
import jieba
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from collections import Counter  # 添加Counter的导入
import jieba.posseg as pseg  # 导入词性标注模块
from wordcloud import WordCloud

# 读取csv
df = pd.read_csv('douban_top250.csv', encoding='utf-8')

# 停用词表，增加“电影”“与”“一样”“佳作”“以为”
stopwords = set([
	'的','是','了','我','也','都','很','在','有','和','就','不','人','一','这','他','一个','上','说','你','到','要','看','还','为','但','对','好','得','没有','让','被','多','没','又','吧','着','还要','而是','而',
	'电影','与','一样','佳作','以为','评价','我们','就是','世界','不会','一部','能','会','想','知道','觉得'
])

# 去除所有中文符号和标点
def remove_punct(word):
	# 中文符号和英文标点
	zh_punct = '，。！？、；：“”‘’（）《》【】—…～·『』「」·—【】（）〔〕［］｛｝〈〉﹏﹋﹌﹉﹊﹍﹎﹏﹐﹑﹒﹔﹕﹖﹗﹙﹚﹛﹜﹝﹞！＂＃＄％＆＇（）＊＋，－．／：；＜＝＞＠［＼］＾＿｀｛｜｝～'
	all_punct = set(string.punctuation + zh_punct)
	return ''.join([c for c in word if c not in all_punct])

# 修改分词函数以仅保留名词、动词和形容词
def filter_by_pos(text):
    words = pseg.cut(text)
    allowed_pos = {'n', 'v', 'a'}  # 名词、动词、形容词
    filtered_words = [word for word, flag in words if flag in allowed_pos]
    return filtered_words

# 为每部电影单独提取热词
def extract_hot_words(text):
    words = filter_by_pos(text)
    words = [remove_punct(w) for w in words]
    words = [w for w in words if w.strip() and w not in stopwords]
    word_freq = Counter(words)
    return ' '.join([w for w, _ in word_freq.most_common(20)])  # 每部电影提取前20个热词

df['hot_word'] = df['hot_comments'].fillna('').apply(extract_hot_words)

# 为每部电影统计所有词的数量和最热的20个词
def extract_word_stats(text):
    words = filter_by_pos(text)
    words = [remove_punct(w) for w in words]
    words = [w for w in words if w.strip() and w not in stopwords]
    word_freq = Counter(words)
    total_count = sum(word_freq.values())
    top_20_words = word_freq.most_common(20)
    return {
        'total_count': total_count,
        'top_words': {w: freq for w, freq in top_20_words}
    }

df['word_stats'] = df['hot_comments'].fillna('').apply(lambda x: extract_word_stats(x))

# 保存每部电影的热词和统计到CSV
df.to_csv('douban_top250.csv', index=False, encoding='utf-8-sig')

# 提取整体热词并保存到文件
all_hot_comments = ' '.join(df['hot_comments'].fillna('').astype(str))
all_words = filter_by_pos(all_hot_comments)
all_words = [remove_punct(w) for w in all_words]
all_words = [w for w in all_words if w.strip() and w not in stopwords]
all_word_freq = Counter(all_words)

# 保存整体热词到文件
with open('../data/whole_hot_words.txt', 'w', encoding='utf-8') as f:
    for w, _ in all_word_freq.most_common(100):
        f.write(w + '\n')

# 生成整体热词的词云图
all_wordcloud = WordCloud(
    width=800, height=400,
    background_color='white',
    font_path='msyh.ttc'  # 确保字体路径正确
).generate_from_frequencies(all_word_freq)

# 保存词云图为图片
all_wordcloud.to_file('../data/whole_hot_words.png')

print('已更新逻辑，仅保留名词、动词和形容词，并保存结果。')
print('已生成整体热词的词云图，并保存到 ../data/whole_hot_words.png')
