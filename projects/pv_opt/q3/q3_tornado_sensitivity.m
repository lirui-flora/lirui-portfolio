% 数据
models = {'N1', 'N2', 'N3', 'P'};
x = 1:length(models);
sales = [9358377.63, 4703201.23, 4974536.82, 8634348.44] / 1e6;  % 单位：百万片
unit_profit = [0.73, 0.39, 0.48, 0.19];  % 单位：元/片

% 双 y 轴绘图
figure;
yyaxis left
bar(x, sales, 0.4, 'FaceColor', [0.2 0.6 0.8]);  % 销量柱状图
ylabel('销量（百万片）');
ylim([0, max(sales)*1.2]);

yyaxis right
plot(x, unit_profit, '-o', 'LineWidth', 2, 'Color', [0.85 0.33 0.1], 'MarkerSize', 8);  % 单位利润折线图
ylabel('单位利润（元/片）');
ylim([0, max(unit_profit)*1.2]);

% 设置横轴
set(gca, 'xtick', x, 'xticklabel', models, 'FontSize', 12);
xlabel('型号');
title('各型号销量与单位利润对比图（双y轴）');
grid on;
legend({'销量（百万片）', '单位利润（元/片）'}, 'Location', 'northwest');