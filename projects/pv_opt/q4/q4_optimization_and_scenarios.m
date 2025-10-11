% ===============================
% 问题四：智能感知模型敏感性分析
% ===============================

% 型号与基础数据
Model = {'N1'; 'N2'; 'N3'; 'P'};
Sales = [1.2e5; 1.0e5; 95000; 1.1e5];
UnitPrice = [2.7; 2.9; 2.85; 2.5];
UnitCost = [1.5; 1.6; 1.55; 1.4];

% 基础利润
BaseProfit = Sales .* (UnitPrice - UnitCost);

% 各项评分（Policy, Market, CostRisk）
Scores = [
    0.85 0.90 0.70;  % N1
    0.80 0.85 0.65;  % N2
    0.80 0.85 0.65;  % N3
    0.70 0.75 0.80   % P
];

% 权重组（w1, w2, w3）分别为 Policy、Market、CostRisk
WeightSet = [
    0.4 0.4 0.2;   % A 基准
    0.5 0.3 0.2;   % B 偏向政策
    0.3 0.5 0.2;   % C 偏向市场
    0.4 0.3 0.3;   % D 成本兼顾
    0.3 0.3 0.4    % E 偏向成本
];

WeightLabels = {'A:基准', 'B:偏政策', 'C:偏市场', 'D:成本兼顾', 'E:偏成本'};
numSchemes = size(WeightSet,1);

% 存储每组方案的修正利润
AdjustedProfits = zeros(length(Model), numSchemes);
TotalScores = zeros(length(Model), numSchemes);

for i = 1:numSchemes
    weights = WeightSet(i,:)';
    R = Scores * weights;                     % 综合评分
    AdjustedProfits(:,i) = BaseProfit .* R;   % 修正利润
    TotalScores(:,i) = R;                     % 保存评分
end

% 展示结果表格
disp('敏感性分析结果（评分与修正利润）：');
for i = 1:numSchemes
    fprintf('\n方案 %s 权重 = [%.1f %.1f %.1f]\n', WeightLabels{i}, WeightSet(i,:));
    T = table(Model, TotalScores(:,i), AdjustedProfits(:,i), ...
        'VariableNames', {'型号', '综合评分', '修正利润'});
    disp(T);
end

% --------------------
% 可视化（堆叠柱状图）
% --------------------

figure;
bar(AdjustedProfits', 'grouped');
title('不同权重组合下的修正利润对比');
xlabel('权重方案');
ylabel('修正利润（元）');
xticklabels(WeightLabels);
legend(Model, 'Location', 'northwest');
grid on;

% --------------------
% 可选：热力图展示评分变化
% --------------------

figure;
heatmap(WeightLabels, Model, round(TotalScores,2), ...
    'ColorbarVisible','on', 'Colormap', hot);
title('各型号产品在不同权重下的综合评分热力图');