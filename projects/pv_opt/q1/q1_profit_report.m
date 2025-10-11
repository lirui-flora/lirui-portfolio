% 清空环境
clear;
clc;

% --- Desensitized header: set your data folder here ---
data_path = 'path/to/data'; % <-- change this to your data folder (absolute or relative)

% 1. 加载数据
filepath = fullfile(data_path, 'data2.xlsx');
sheets = {'汇总', '销售收入'};
df_summary = readtable(filepath, 'Sheet', sheets{1}, 'ReadRowNames', true);
df_sales = readtable(filepath, 'Sheet', sheets{2}, 'ReadRowNames', true);

% 2. 提取月份列（包含1月）
all_columns = df_summary.Properties.VariableNames;
valid_months = all_columns(startsWith(all_columns, {'x','1','2','3','4','5','6','7','8','9','10','11','12'}));  % 包含 x1_, 1月 等
months = string(valid_months);  % 强制转成 string 数组用于后续操作

% 3. 利润计算
results = table();
for i = 1:length(months)
    month = months(i);
    col = char(month);

    sales          = get_value(df_summary, '一、销售收入', col);
    variable_cost  = get_value(df_summary, '减：生产变动成本', col);
    public_cost    = get_value(df_summary, '生产公共成本', col);
    labor_cost     = get_value(df_summary, '人工成本', col);
    depreciation   = get_value(df_summary, '折旧', col);
    business_tax   = get_value(df_summary, '营业税费', col);
    sales_fee      = get_value(df_summary, '销售费用', col);
    management_fee = get_value(df_summary, '管理费用', col);
    financial_fee  = get_value(df_summary, '财务费用', col);
    other_income   = get_value(df_summary, '其他收益', col);

    % 计算利润
    profit_before_tax = sales - variable_cost - public_cost - labor_cost - depreciation - ...
                        business_tax - sales_fee - management_fee - financial_fee + other_income;
    income_tax = 0.15 * profit_before_tax;
    net_profit = profit_before_tax - income_tax;

    new_row = table(month, sales, variable_cost, public_cost, labor_cost, depreciation, ...
        business_tax, sales_fee, management_fee, financial_fee, other_income, ...
        profit_before_tax, income_tax, net_profit, ...
        'VariableNames', {'Month', 'Sales', 'VariableCost', 'PublicCost', 'LaborCost', ...
        'Depreciation', 'BusinessTax', 'SalesFee', 'ManagementFee', 'FinancialFee', ...
        'OtherIncome', 'ProfitBeforeTax', 'IncomeTax', 'NetProfit'});

    results = [results; new_row];
end

% 4. 输出
disp(repmat('=', 1, 60));
disp('Monthly Profit Report (Jan–Aug 2024):');
disp(repmat('=', 1, 60));
disp(results);

% 5. 可视化
figure('Position', [100, 100, 1200, 800]);

x_labels = categorical(results.Month);
x_labels = reordercats(x_labels, results.Month);

% 子图1：净利润趋势
subplot(2,2,1);
plot(x_labels, results.NetProfit / 1e6, 'o-', 'LineWidth', 1.5);
title('Net Profit Trend (Million CNY)');
xlabel('Month'); ylabel('Net Profit (Million)');
grid on;

% 子图2：成本结构
subplot(2,2,2);
cost_columns = {'VariableCost', 'PublicCost', 'LaborCost', 'SalesFee', 'ManagementFee', 'FinancialFee'};
cost_data = table2array(results(:, cost_columns))';
hold on;
colors = lines(length(cost_columns));
for j = 1:length(cost_columns)
    bar(x_labels, cost_data(j, :) / 1e6, 'FaceColor', colors(j,:), 'BarWidth', 0.6, 'EdgeColor', 'none');
end
legend(cost_columns, 'Location', 'northwest');
title('Cost Breakdown (Million CNY)');
xlabel('Month'); ylabel('Cost (Million)');
grid on;

% 子图3：利润率
subplot(2,2,3);
profit_rate = results.NetProfit ./ results.Sales * 100;
plot(x_labels, profit_rate, 's-', 'LineWidth', 1.5);
title('Net Profit Margin (%)');
xlabel('Month'); ylabel('Profit Margin (%)');
grid on;

% 6. 保存
writetable(results, fullfile(data_path, 'ProfitResults.xlsx'), 'WriteRowNames', false);
fprintf('\nResults saved to file.\n');

% 7. 辅助函数：安全读取
function val = get_value(table, row_name, col_name)
    try
        val = table.(col_name)(strcmp(table.Properties.RowNames, row_name));
        if isempty(val)
            val = 0;
        end
    catch
        val = 0;
    end
end