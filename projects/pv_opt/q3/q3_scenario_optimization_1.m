%% 问题三总代码
% %光伏硅片利润优化模型（问题3-多约束版）
clear; clc;

% ================ 基础参数设置 ================
models = {'N1', 'N2', 'N3', 'P'};

% 核心预测值（9月预测）
Sales = [584.4560; 573.7360; 578.5380; 594.5680];       % 万片
UnitPrice = [1.7136; 1.6904; 1.6050; 1.3876];           % 元/片
RodPrice = [50.5137; 49.9642; 48.9516; 46.5492];        % 元/kg
UnitVarCost_pred = [9832.64; 13038.91; 11254.50; 11985.89]; % 9月预测单位变动成本（元/万片）

% 波动区间（销量、售价、硅棒价）
SalesRange = [584.4490 984.3038;
              392.0791 621.5000;
              440.6116 859.8333;
              452.6250 896.8663];

PriceRange = [1.1294 1.78;
              1.4456 1.7365;
              1.5733 1.8751;
              1.2850 1.4453];

RodPriceRange = [43.6839 79.57;
                 44.1734 71.50;
                 44.5086 80.67;
                 33.4751 69.67];

% 硅单耗（kg/片） - 合理值（估计）
SiliconUsage = [0.02; 0.022; 0.021; 0.018]; 

% ================ 多场景优化 ================
% 场景1：最不利情况（售价最低 + 成本最高）
unitVarCost_worst = (RodPriceRange(:,2) .* SiliconUsage + 0.5) * 10000;
price_worst = PriceRange(:,1);
c_worst = -(price_worst * 10000 - unitVarCost_worst);

% 场景2：基准情况（使用预测变动成本 + 售价中值）
price_mid = UnitPrice;
unitVarCost_mid = UnitVarCost_pred;
c_mid = -(price_mid * 10000 - unitVarCost_mid);

% 场景3：最有利情况（售价最高 + 成本最低）
unitVarCost_best = (RodPriceRange(:,1) .* SiliconUsage + 0.5) * 10000;
price_best = PriceRange(:,2);
c_best = -(price_best * 10000 - unitVarCost_best);

% ================ 固定成本与三费汇总 ================
% 来自8月数据
LaborCost = [494997; 342713; 596201; 637089];   % N1~P人工成本（元）
OtherCost = 204793.12 + 104742 + 568351 + 673093.42;  % 固定成本 + 销售、管理、财务费用（元）
const_cost = LaborCost + OtherCost / 4; % 平均分配三费

% ================ 优化约束 ================
% ================ 优化约束 ================

% 历史每月产能（单位：万片），可以按你需要填充真实数据（示例为 1~8 月）
past_monthly_output = [2100, 2250, 2180, 2300, 2400, 2350, 2280, 2420];  % 示例数据

% 动态设定最大产能上限为历史最大产能的 1.05 倍，避免太死板
b_total = max(past_monthly_output) * 1.05;

A_total = ones(1,4);        % 总产能限制（4 种型号总和）
lb = SalesRange(:,1);       % 各型号销量下限
ub = SalesRange(:,2);       % 各型号销量上限
% ================ 求解最优解 ================
options = optimoptions('linprog', 'Display', 'off');

[x_worst, fval_worst] = linprog(c_worst, A_total, b_total, [], [], lb, ub, options);
[x_mid, fval_mid] = linprog(c_mid, A_total, b_total, [], [], lb, ub, options);
[x_best, fval_best] = linprog(c_best, A_total, b_total, [], [], lb, ub, options);

% 计算利润
profit_worst = -fval_worst - sum(const_cost);
profit_mid   = -fval_mid - sum(const_cost);
profit_best  = -fval_best - sum(const_cost);

% ================ 输出结果 ================
fprintf('===== 问题3 多约束优化结果（单位：万片 / 万元）=====\n');
fprintf('场景\t\tN1\t\tN2\t\tN3\t\tP\t\t总利润\n');
fprintf('最不利\t%.1f\t%.1f\t%.1f\t%.1f\t%.2f\n', x_worst, profit_worst/1e4);
fprintf('基准\t%.1f\t%.1f\t%.1f\t%.1f\t%.2f\n', x_mid, profit_mid/1e4);
fprintf('最有利\t%.1f\t%.1f\t%.1f\t%.1f\t%.2f\n', x_best, profit_best/1e4);

% ================ 可视化分析 ================
figure('Position', [100, 100, 1200, 400]);

% 子图1：产量柱状图
subplot(1,3,1);
hold on;
bar(1:4, [x_worst, x_mid, x_best]);
set(gca, 'XTickLabel', models);
ylabel('产量（万片）');
legend({'最不利','基准','最有利'}, 'Location', 'northwest');
title('不同场景生产方案');
grid on;

% 子图2：利润柱状图
subplot(1,3,2);
bar([profit_worst, profit_mid, profit_best]/1e4);
set(gca, 'XTickLabel', {'最不利','基准','最有利'});
ylabel('利润（万元）');
title('利润场景对比');
grid on;

% 子图3：敏感性分析（售价 vs 销量 vs 硅棒价格）
subplot(1,3,3);
scatter(UnitPrice, Sales, 500, RodPrice, 'filled');
colorbar;
xlabel('售价（元/片）');
ylabel('销量（万片）');
title('参数相关性分析（颜色表示硅棒价格）');
grid on;

fprintf('\n=== 各型号单位利润分析（元/片） ===\n');
fprintf('型号\t最不利\t基准\t最有利\n');
for i = 1:4
    prof_worst = price_worst(i)*10000 - unitVarCost_worst(i);
    prof_mid   = price_mid(i)*10000   - unitVarCost_mid(i);
    prof_best  = price_best(i)*10000  - unitVarCost_best(i);
    fprintf('%s\t%.2f\t%.2f\t%.2f\n', models{i}, prof_worst/1e4, prof_mid/1e4, prof_best/1e4);
end
% ================ 各型号利润贡献分析 ================
% 单位利润（元/片）
profitPerUnit_worst = -c_worst / 10000;
profitPerUnit_mid   = -c_mid   / 10000;
profitPerUnit_best  = -c_best  / 10000;

% 实际利润（万元） = 单位利润 × 产量 / 1e4
model_profit_worst = profitPerUnit_worst .* x_worst / 1e4;
model_profit_mid   = profitPerUnit_mid   .* x_mid   / 1e4;
model_profit_best  = profitPerUnit_best  .* x_best  / 1e4;

% 拼接为一个矩阵：每行一个场景，每列一个型号
profit_matrix = [model_profit_worst'; 
                 model_profit_mid'; 
                 model_profit_best'];

% ================ 堆叠柱状图展示 ================
figure('Position', [200, 150, 800, 400]);
bar(profit_matrix, 'stacked');
colormap(parula(4));
set(gca, 'XTickLabel', {'最不利','基准','最有利'});
ylabel('各型号利润贡献（万元）');
legend(models, 'Location', 'northeast');
title('各型号对总利润的构成');
grid on;

% ================ 单位利润热力图 ================
% 单位利润矩阵（元/片）
unit_profit_matrix = [
    -0.96,  0.73, 0.41;  % N1
    -0.63,  0.39, 0.26;  % N2
    -0.62,  0.48, 0.44;  % N3
    -0.47,  0.19, 0.34   % P
];

figure('Position', [100, 100, 600, 400]);
imagesc(unit_profit_matrix);
colormap(jet);  % 使用 jet 热度颜色
colorbar;
title('各型号单位利润热力图（元/片）');
xlabel('场景'); ylabel('型号');

set(gca, 'XTick', 1:3, 'XTickLabel', {'最不利','基准','最有利'});
set(gca, 'YTick', 1:4, 'YTickLabel', {'N1','N2','N3','P'});

for i = 1:4
    for j = 1:3
        text(j, i, sprintf('%.2f', unit_profit_matrix(i, j)), ...
            'HorizontalAlignment', 'center', 'Color', 'white', 'FontWeight', 'bold');
    end
end

% ================ 单位利润 3D柱状图 ================
figure('Position', [100, 100, 700, 500]);
bar3(unit_profit_matrix);
colormap(parula);
title('各型号单位利润3D柱状图（元/片）');
xlabel('场景'); ylabel('型号'); zlabel('单位利润');

set(gca, 'XTickLabel', {'最不利','基准','最有利'});
set(gca, 'YTickLabel', {'N1','N2','N3','P'});

% 添加数值标签
for k = 1:size(unit_profit_matrix, 1)
    for j = 1:size(unit_profit_matrix, 2)
        z = unit_profit_matrix(k, j);
        text(j, k, z + 0.02, sprintf('%.2f', z), ...
            'HorizontalAlignment', 'center', 'FontSize', 10, 'Color', 'k');
    end
end

% ================ 总利润 3D柱状图 ================
figure('Position', [100, 100, 600, 400]);
bar3([profit_worst, profit_mid, profit_best]/1e4);  % 万元为单位
colormap(summer);
title('不同场景下总利润（万元）');
xlabel('场景'); ylabel(' '); zlabel('利润（万元）');
set(gca, 'XTickLabel', {'最不利','基准','最有利'});
view(-45, 30);  % 设置视角

% 添加标签
for i = 1:3
    val = [profit_worst, profit_mid, profit_best]/1e4;
    text(i, 1, val(i) + 50, sprintf('%.2f', val(i)), ...
        'HorizontalAlignment', 'center', 'FontSize', 10, 'Color', 'k');
end

% ================ 各型号产量结构 3D柱状图 ================
figure('Position', [100, 100, 700, 500]);
X = [x_worst, x_mid, x_best]';  % 4x3 转置为 3x4
bar3(X);
colormap(cool);
title('不同场景下各型号产量分布（万片）');
xlabel('场景'); ylabel('型号'); zlabel('产量（万片）');

set(gca, 'XTickLabel', {'最不利','基准','最有利'});
set(gca, 'YTickLabel', {'N1','N2','N3','P'});
view(-45, 30);

% 添加数值标签
for i = 1:4
    for j = 1:3
        val = X(j,i);
        text(j, i, val + 30, sprintf('%.1f', val), ...
            'HorizontalAlignment', 'center', 'FontSize', 10, 'Color', 'k');
    end
end

