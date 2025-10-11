%% 基准数据
unitProfit_base = [0.73, 0.39, 0.48, 0.19]; % 元/片
salesForecast = [9358377.63, 4703201.23, 4974536.82, 8634348.44];
lb = 0.8 * salesForecast;
ub = 1.2 * salesForecast;
nvars = 4;

% 固定成本和三费总额
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

%% 扰动设置（售价 ±10%, ±5%, 基准）
delta = [-0.1, -0.05, 0, 0.05, 0.1];
sensitivity_profit = zeros(length(delta), 1);
sensitivity_ratio = zeros(length(delta), 1);  % 利润变化率 / 售价变化率

%% 基准利润（用于灵敏度计算）
unitProfit = unitProfit_base;
profitFunc = @(x) - (sum(x .* unitProfit) - totalFixedCost);
[x_base, fval_base] = particleswarm(profitFunc, nvars, lb, ub);
baseProfit = -fval_base;

%% 敏感性分析循环
for i = 1:length(delta)
    % 售价扰动（通过单位利润模拟）
    unitProfit = unitProfit_base * (1 + delta(i));
    profitFunc = @(x) - (sum(x .* unitProfit) - totalFixedCost);
    
    [x_opt, fval] = particleswarm(profitFunc, nvars, lb, ub);
    currentProfit = -fval;
    sensitivity_profit(i) = currentProfit;

    if delta(i) ~= 0
        sensitivity_ratio(i) = ((currentProfit - baseProfit) / baseProfit) / delta(i);
    else
        sensitivity_ratio(i) = NaN;
    end
end

%% 输出表格
T = table(delta'*100, sensitivity_profit, sensitivity_ratio, ...
    'VariableNames', {'售价变动率_%', '最优利润_元', '利润对售价灵敏度'});
disp(T);

%% 可视化
figure;
yyaxis left;
plot(delta*100, sensitivity_profit/1e6, '-o', 'LineWidth', 2);
ylabel('最大利润（百万元）');
yyaxis right;
plot(delta*100, sensitivity_ratio, '-s', 'LineWidth', 2);
ylabel('利润灵敏度');
xlabel('售价扰动率 (%)');
title('售价敏感性分析');
legend('最大利润', '利润灵敏度', 'Location', 'best');
grid on;