%% 原始数据
unitProfit = [0.73, 0.39, 0.48, 0.19]; % 元/片
salesForecast = [9358377.63, 4703201.23, 4974536.82, 8634348.44];
lb = 0.8 * salesForecast;
ub = 1.2 * salesForecast;
fixedCost = mean([289170.53, 336101.54, 366864.11, 273491.93, ...
369345.34, 304606.05, 284814.53, 204793.12]);
laborCost = mean([613612, 474633, 359465, 225691, 546528, 552177, 538562, 494997]) + ...
mean([303383, 350157, 353277, 379963, 209677, 361594, 367446, 342713]) + ...
mean([503108, 411137, 411388, 545258, 508624, 366244, 314104, 596201]) + ...
mean([374897, 423073, 660870, 706088, 660171, 552985, 602888, 637089]);
salesCost = mean([98802, 94842, 96129, 91773, 96492, 95172, 97482, 104742]);
manageCost = mean([550498, 551191, 580891, 560068, 533536, 566701, 557428, 568351]);
financeCost = mean([649300.42, 646033.42, 677020.42, 651841.42, 630028.42, 661873.42, 654910.42, 673093.42]);
totalFixedCost = fixedCost + laborCost + salesCost + manageCost + financeCost;
nvars = 4;

options = optimoptions('particleswarm', ...
    'SwarmSize', 30, ...
    'MaxIterations', 50, ...
    'Display', 'off');

models = {'N1', 'N2', 'N3', 'P'};
baseFunc = @(x) - (sum(x .* unitProfit) - totalFixedCost);
[x_base, fval_base] = particleswarm(baseFunc, nvars, lb, ub, options);
base_profit = -fval_base;

%% 扰动分析 ±10%
delta = 0.10;
profit_down = zeros(1,4);
profit_up = zeros(1,4);

% 初始化一个 cell 数组来保存结果
results = cell(4, 4);  % 每行存储每个型号的扰动数据

for i = 1:4
    % 扰动下降
    unitProfit_down = unitProfit;
    unitProfit_down(i) = unitProfit(i) * (1 - delta);
    func_down = @(x) - (sum(x .* unitProfit_down) - totalFixedCost);
    [~, fval] = particleswarm(func_down, nvars, lb, ub, options);
    profit_down(i) = -fval;
    
    % 扰动上升
    unitProfit_up = unitProfit;
    unitProfit_up(i) = unitProfit(i) * (1 + delta);
    func_up = @(x) - (sum(x .* unitProfit_up) - totalFixedCost);
    [~, fval] = particleswarm(func_up, nvars, lb, ub, options);
    profit_up(i) = -fval;
    
    % 记录每个型号的结果
    results{i, 1} = models{i}; % 型号
    results{i, 2} = profit_down(i); % 下行利润
    results{i, 3} = profit_up(i); % 上行利润
    results{i, 4} = profit_up(i) - profit_down(i); % 利润差
end

%% 输出扰动分析结果
disp('==== 扰动分析结果 ====');
disp('型号    下行利润（元）  上行利润（元）  利润差（元）');
for i = 1:4
    disp([results{i, 1}, num2str(results{i, 2}), num2str(results{i, 3}), num2str(results{i, 4})]);
end

%% 构造 Tornado 图数据
profit_diff = [profit_down - base_profit; profit_up - base_profit];  % 每列为某一型号
colors = [repmat([0.6 0.6 0.9], 4, 1); repmat([0.9 0.6 0.6], 4, 1)];   % 蓝红条

% 合并上下扰动
tornado_data = [profit_down - base_profit; profit_up - base_profit]';
tornado_data = tornado_data(:, [2 1]);  % 顺序为 [负扰动, 正扰动]

%% 绘图
figure;
barh(tornado_data, 'stacked');
yticklabels(models);
xlabel('利润变化量（元）');
title('单位利润 ±10% 扰动的敏感性分析（Tornado图）');
legend({'-10% 扰动', '+10% 扰动'}, 'Location', 'best');
grid on;