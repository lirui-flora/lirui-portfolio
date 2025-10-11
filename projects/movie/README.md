## 项目简介

本项目对豆瓣电影进行了完整的数据采集、预处理、聚类分析、词云与情感分析，并在聚类结果的基础上实现了一个简单的推荐系统。

主要工作流：
- 爬取电影及热评数据（爬虫、HTML 解析）
- 数据清洗与基础统计（缺失值、异常值处理、格式化）
- 文本处理与词云生成（jieba 分词、wordcloud）
- 聚类分析（特征工程、K 值选择：轮廓系数 / 肘部法、t-SNE 可视化）
- 聚类下的情感分析（Hugging Face 预训练模型 + transformers pipeline）
- 基于聚类与多特征的简单推荐（Jaccard + 随机森林 / 逻辑回归）

## 仓库结构（基于当前文件）

项目根目录结构（以文件/目录 -> 简要说明）：

- `.idea/`                          - IDE 配置（PyCharm 配置文件，可忽略或加入 .gitignore）
	- `misc.xml`
	- `csv-editor.xml`
	- `inspectionProfiles/profiles_settings.xml`

	- `basic_analysis.py`             - 基础统计与可视化脚本
	- `catogary_sentiment.py`         - 汇总每部电影的评论情感并给出标签
	- `cluster_k_selection.py`        - 聚类流程、K 值选择、t-SNE 可视化与词云生成
	- `data.py`                       - 爬取豆瓣电影与热评的脚本（requests + lxml）
		python .\\src\\data.py
	- `predata.py`                    - 数据预处理与基础信息分析
	- `sentiment.py`                  - 使用 Hugging Face 模型做情感预测的脚本
	- `small_recommend_system.py`     - 基于特征的简单推荐系统实现
		python .\\src\\word_cloud.py
	- `word_cloud.py`                 - 处理热评并生成词云与热词统计
		python .\\src\\cluster_k_selection.py

- `output/`                           - 项目运行生成的结果（示例输出）
	- `machine/`                        - 示例模型、权重与示例输出
		- `example_feature_weights_lr.csv`
		- `example_feature_weights_rf.csv`
		- `sample_movie_sentiment.csv`
		python .\\src\\word_cloud.py
		- `images/`                        - 模型/权重可视化图片
			- `lr_feature_weights_radar.png`
	- `images/`                          - 运行生成的可视化图片（聚类、基础分析）
		- `basic/`
		python .\\src\\cluster_k_selection.py
			- `basic_analysis2.png`
			- `basic_analysis.png`
			- `cluster_all_in_one_K8.png`
			- `cluster_k_selection.png`
		# conda activate sentiment; python .\\src\\small_recommend_system.py
        - `wordcloud_K8/`
		    - `cluster_sentiment/`

	- `wordcloud/`                       - 词云与热词输出
		- `whole_hot_words.txt`
		# conda activate sentiment; python .\\src\\sentiment.py
		- `wordcloud_K8/`
			- `cluster_sentiment/`
				- `whole_hot_words.png`
				- `cluster_sentiment_distribution2.png`

	注意：README 中列出的路径均为示例输出路径。请在实际使用时把这些路径替换为你本地或运行环境中的对应路径（例如替换为你的 Python/conda 环境的绝对路径或相对路径）。

- 项目根文件
	- `README.md`                       - 项目说明（本文件）
	- `flow.md`, `flow.png`             - 流程图与源文件
	- `requirements.txt`                - 建议依赖列表（已生成）


## 环境与依赖

建议使用 Anaconda 创建虚拟环境，分为两个环境以便隔离（可选）：

- 基础数据处理环境（如：`base`）
- 情感分析环境（`sentiment`）：用于安装 transformer、torch 等模型依赖

示例（在 Windows PowerShell 中运行）：

```powershell
# 创建并激活环境（示例）
conda create -n sentiment python=3.10 -y; conda activate sentiment
# 安装常用依赖
pip install -r requirements.txt
```

（如果仓库中没有 `requirements.txt`，请按需安装：pandas, numpy, requests, lxml, jieba, wordcloud, scikit-learn, matplotlib, seaborn, transformers, torch 等。）

> 注意：情感模型会从 Hugging Face 下载权重，缓存位置通常在用户目录下的 `.cache/huggingface`，下载过程需要网络且可能占用较多磁盘空间。

## 快速开始（运行脚本说明）

下面给出每个关键脚本的运行说明，假设在项目根目录下运行并将 Python 可执行路径替换为你的环境路径：

- 爬取数据

	```powershell
	# 使用你的 Python 解释器运行
	# 使用当前环境中的 Python 解释器运行脚本，例如：
	python .\\src\\data.py

	python .\\src\\predata.py

	python .\\src\\word_cloud.py

	python .\\src\\cluster_k_selection.py

	# 如果使用专门的 conda 环境（例如 sentiment），在激活该环境后使用 python 运行：
	# conda activate sentiment; python .\\src\\small_recommend_system.py

	# conda activate sentiment; python .\\src\\sentiment.py
	```powershell
	# 使用当前环境中的 python 运行脚本，例如：
	python .\\src\\word_cloud.py
	```

- 聚类分析与 K 值选择

	```powershell
	# 使用当前环境中的 python 运行脚本，例如：
	python .\\src\\cluster_k_selection.py
	```

- 小推荐系统（注意：示例使用 `sentiment` 环境运行）

	```powershell
	# 如果使用专门的 conda 环境（例如 sentiment），激活后运行：
	# conda activate sentiment; python .\\src\\small_recommend_system.py
	```

- 情感判别（单条评论/批量）

	```powershell
	# sentiment 环境中运行（示例）
	# conda activate sentiment; python .\\src\\sentiment.py
	```

## 模型说明

- `machine/` 目录包含示例模型与权重：
	- 后缀 `1` 的文件对应模型 1：`uer/roberta-base-finetuned-dianping-chinese`
	- 后缀 `2` 的文件对应模型 2：`IDEA-CCNL/Erlangshen-Roberta-110M-Sentiment`

情感预测脚本会使用 `transformers` 的 pipeline 或自定义推理逻辑来加载这些模型并进行预测。

## 输出与结果

- 词云图片（存放在 `images/wordcloud_*` 或 `data/` 中）
- 聚类可视化（t-SNE 散点图等，位于 `images/cluster/`）
- 聚类情感统计：`cluster_movie_sentiment2.csv`, `cluster_sentiment_stats2.csv`
- 小推荐系统结果：交互式命令行或保存为 CSV（视脚本实现）

## 注意事项

- > 原始 CSV 数据因合规与隐私考虑已删除，仅保留分析逻辑与示例输出。  
- > 如需复现，可使用公开电影数据替代。
- 仓库中已删除部分中间过程文件，只保留主要结果。若要重跑某些步骤，可能需要调整脚本中的路径或重新生成中间文件。
- Hugging Face 模型会占用缓存空间，默认缓存位置通常在用户主目录下的 `~/.cache/huggingface`（或 Windows 上 `%USERPROFILE%\\.cache\\huggingface`）。
	如果你希望把缓存放在项目内以便可复现或避免使用全局缓存，可以在运行前设置环境变量：
	- TRANSFORMERS_CACHE 或 HF_HOME 指向你想要的缓存目录（例如 `./.cache/huggingface`）。


## 参考与致谢

- 使用了 Hugging Face 的开源模型与 Transformers 库
- 部分实现参考了 scikit-learn、jieba、wordcloud 等社区工具

## 联系

如需帮助或复现结果，请在 Issue 中说明运行环境与遇到的问题，或直接联系作者（在仓库中保留的联系方式）。

- 小推荐系统结果：交互式命令行或保存为 CSV（视脚本实现）

本项目旨在展示作者在数据分析、文本挖掘与推荐系统建模方面的能力。

