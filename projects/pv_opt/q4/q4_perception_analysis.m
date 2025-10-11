% Desensitized header
data_path = 'path/to/data'; % set to your data folder

% 感知评分表路径
filePath = fullfile(data_path, 'q4', 'perception_scores.csv');

% 读取评分表
scoreTable = readtable(filePath);

% 将评分转为 map 结构，便于查找
scoreMap = containers.Map(scoreTable.Model, scoreTable.TotalScore);

% 模拟四种晶硅片产品基本信息（来自之前数据）
models = {'N1', 'N2', 'N3', 'P'};  % 型号
sales = [120000, 100000, 95000, 110000];  % 第九个月预测销量
unitPrice = [2.7, 2.9, 2.85, 2.5];        % 单价（元）
unitCost = [1.5, 1.6, 1.55, 1.4];         % 单位成本（元）

% 计算基础利润
baseProfit = (unitPrice - unitCost) .* sales;

% 获取每种型号的感知评分
perceptionScores = zeros(size(models));
for i = 1:length(models)
    perceptionScores(i) = scoreMap(models{i});
end

% 感知加权利润
adjustedProfit = baseProfit .* perceptionScores;

% 合并结果为表格
resultTable = table(models', sales', unitPrice', unitCost', baseProfit', perceptionScores', adjustedProfit', ...
    'VariableNames', {'Model', 'Sales', 'UnitPrice', 'UnitCost', 'BaseProfit', 'PerceptionScore', 'AdjustedProfit'});

disp(resultTable);

% 可视化：原始利润 vs 感知加权利润
figure;
bar(categorical(models), [baseProfit; adjustedProfit]');
legend('原始利润', '感知加权利润');
ylabel('利润（元）');
title('晶硅片各型号利润对比（含感知加权）');
grid on;

figure;
Z = [baseProfit; adjustedProfit];
bar3(Z');
set(gca, 'XTickLabel', {'原始利润', '感知加权利润'});
set(gca, 'YTickLabel', models);
xlabel('利润类型'); ylabel('晶硅片型号'); zlabel('利润值（元）');
title('原始 vs 感知加权利润（三维柱状图）');

% 单项评分（假设从CSV读入）
policy = [0.88, 0.83, 0.80, 0.65];
market = [0.88, 0.87, 0.80, 0.65];
cost   = [0.73, 0.68, 0.68, 0.83];

% 合并
scoreMatrix = [policy; market; cost]';

% 雷达图
figure;
radarLabels = {'PolicySupport', 'MarketDemand', 'CostRisk'};
p = polarplot([scoreMatrix'; scoreMatrix(:,1)']', 'LineWidth', 2);
legend(models, 'Location', 'southoutside');
title('各型号感知评分雷达图');
set(gca, 'ThetaTickLabel', radarLabels);

figure;
heatData = [baseProfit; adjustedProfit; perceptionScores*100]; % 放大评分便于显示
imagesc(heatData);
colormap hot;
colorbar;
xticks(1:length(models)); xticklabels(models);
yticks([1 2 3]); yticklabels({'原始利润', '感知加权利润', '感知评分 ×100'});
title('晶硅片各型号感知与利润热力图');

figure;
stacked = [unitCost .* sales; (unitPrice - unitCost) .* sales];  % 成本 + 利润分层
bar(categorical(models), stacked', 'stacked');
legend('成本部分', '利润部分');
ylabel('销售总额（元）');
title('晶硅片利润结构堆叠图');