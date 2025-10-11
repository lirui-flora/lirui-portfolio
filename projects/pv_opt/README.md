
# 光伏发电优化与预测（PV Optimization Project）

本目录包含与光伏（PV）发电优化、预测与情景分析有关的 MATLAB 脚本与示例，按题目（q1-q4）组织。

本 README 旨在：
- 概述项目目的与结构
- 说明每个子目录/脚本的功能
- 给出运行与复现的最小依赖与步骤
- 列出注意事项与可拓展方向

本项目聚焦于光伏发电的收益预测与优化建模，使用 MATLAB 构建了从时间序列预测到多情景优化的一体化实验框架。

主要特征：
- 多模型时间序列预测（指数平滑、LSTM、集成方法）
- 情景驱动的产量优化与利润可视化
- 敏感性分析与感知度研究（Tornado 图）
- 适用于教学演示与科研验证的原型框架


## 项目简介

该工程集合了一组用于光伏发电预测、优化与情景分析的 MATLAB 脚本，覆盖：

- 第1题（q1）：利润/收益汇报与基础分析
- 第2题（q2）：时间序列预测（指数平滑、LSTM 与混合方法）
- 第3题（q3）：产量预测、优化与不确定性/情景可视化
- 第4题（q4）：优化与情景求解、感知/感受度分析

这些脚本可用于教学演示、项目原型或作为研究的起点。

## 目录结构

（只列出与本项目相关的主要文件/文件夹）

- q1/
	- `q1_profit_report.m` —— 第1题主脚本：生成利润/收益相关的表格和可视化。
- q2/
	- `q2_predict_all_exp_smooth.m` —— 使用指数平滑方法进行时间序列预测的示例。
	- `q2_predict_all_lstm_and_univariate.m` —— 使用 LSTM 与单变量模型进行预测的尝试/比较。
	- `q2_timeseries_forecast_helpers.m` —— 辅助函数，包含常用的时间序列处理与评估方法。
- q3/
	- `q3_forecast_main.m` —— 第3题主脚本：进行产量预测并与后续优化或可视化连接。
	- `q3_lstm_vs_es_ensemble.m` —— 比较 LSTM 与指数平滑（ES）模型并做集成。
	- `q3_production_plan_viz.m` —— 产量/计划的可视化脚本。
	- `q3_profit_scenarios_viz.m` —— 利润在不同情景下的可视化。
	- `q3_scenario_optimization_1.m` —— 以情景为基础的优化示例。
	- `q3_simple_es_models.m` —— 简单的指数平滑模型实现与示例。
	- `q3_tornado_sensitivity.m` —— Tornado 图（敏感性分析）示例脚本。
	- `q3_unit_cost_regression.m` —— 单位成本回归分析脚本。
	- `q3_weighted_predictions_combine.m` —— 权重融合/加权组合预测的实现。
- q4/
	- `q4_optimization_and_scenarios.m` —— 第4题主脚本：优化与情景求解主流程。
	- `q4_perception_analysis.m` —— 感知/感受度分析脚本。
- README.md —— 本文件。

此外，目录根下可能包含用于数据或可视化的其他资源（例如 `workspace_data.txt`、`workspace_pointcloud.pkl`、`motorevo.txt` 等），但这些文件看起来与本题目的 MATLAB 实验无直接强耦合。

## 依赖与环境

- MATLAB（建议 R2019a 及以上以支持深度学习工具箱与时间序列工具箱）
- 若需运行 LSTM 脚本：MATLAB Deep Learning Toolbox
- 若需绘图或导出图形：常规 MATLAB 绘图库

请根据您的 MATLAB 版本在脚本开头检查 `addpath` 或路径依赖，并在必要时调整路径以指向数据文件或辅助函数。

## 快速复现（运行示例）

1. 在 MATLAB 中将当前目录切换到 `pv_opt` 文件夹（例如：`cd('d:/E/实习海投/作品集/pv_opt')`）。
2. 打开并检查各题目脚本，确认数据文件路径（例如 `workspace_data.txt` 或其它 CSV/ MAT 文件）是否正确。
3. 依次运行：
	 - 第1题（报告）: 打开并运行 `q1/q1_profit_report.m`。
	 - 第2题（预测）: 运行 `q2/q2_predict_all_exp_smooth.m` 和 `q2/q2_predict_all_lstm_and_univariate.m`（如果有 Deep Learning Toolbox）。
	 - 第3题（情景与优化）: 运行 `q3/q3_forecast_main.m`，或根据目的运行其他 q3 脚本进行可视化/优化。
	 - 第4题（优化与感知分析）: 运行 `q4/q4_optimization_and_scenarios.m` 或 `q4/q4_perception_analysis.m`。

示例（在 MATLAB 命令窗口中执行）：

```matlab
cd('d:/E/实习海投/作品集/pv_opt')
run('q1/q1_profit_report.m')
run('q2/q2_predict_all_exp_smooth.m')
run('q3/q3_forecast_main.m')
``` 

注意：如果脚本使用相对路径读取 `data` 或 `inputs`，请确保将 MATLAB 的当前工作目录设为 `pv_opt` 或在脚本中修正路径。

## 脚本说明（要点）

- q1_profit_report.m：生成利润/收益相关的统计与图表，用于答题或报告展示；请检查其中的数据读取部分，确保数据文件路径存在。
- q2_predict_all_exp_smooth.m：实现并对比多个指数平滑配置，输出预测结果与评价指标（如 MAPE、RMSE 等）。
- q2_predict_all_lstm_and_univariate.m：训练并评估 LSTM 模型（若工具箱可用），同时与单变量模型做对比或融合。
- q3_forecast_main.m：作为 q3 的主流程脚本，包含数据准备、模型预测、以及后续优化/可视化调用。
- q3_* 脚本族：包含一系列的可视化（生产计划、利润情景、敏感性分析）与模型融合/回归分析工具。
- q4_* 脚本族：侧重于情景驱动的优化求解，并包含感知度/敏感性分析的实现。

## 常见问题与调试提示

- 路径错误：请在 MATLAB 中使用绝对路径或在脚本顶部添加 `addpath(genpath(pwd))` 来引入子目录。
- 工具箱缺失：若运行 LSTM 相关脚本报错，请在 MATLAB 中检查是否安装 Deep Learning Toolbox。
- 数据格式：脚本可能假定输入为特定格式（CSV、MAT 或纯数值矩阵）。请打开脚本顶部注释查看数据格式要求并预处理数据。

## 扩展建议

- 把常用的数据加载与预处理步骤抽象到一个共享函数，减少每个脚本里重复代码。
- 使用 Git 管理版本，并把数据（如大文件）放到单独的数据目录或使用下载脚本。
- 若希望可重复的实验环境，可把 MATLAB 脚本转换为 Python（使用 scikit-learn/prophet/keras）或编写 Docker 镜像（需要 MATLAB Runtime 或开源替代）。

## 联系与许可

此仓库为个人/学术用途示例。如要在生产环境使用，请根据需要清理、重构并添加单元测试与数据验证步骤。

---