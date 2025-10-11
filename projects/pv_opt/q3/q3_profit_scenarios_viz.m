% 型号与数据
models = {'N1', 'N2', 'N3', 'P'};
production_plan = [11230000, 5644000, 5969000, 10361000];  % 生产计划（片）

% 多行注释内容（cell数组）
comments = {
    {'主打利润型号', '重点抢占市场份额', '配套营销支持'};
    {'稳定投放', '适当审慎扩大', '关注产能与政策联动'};
    {'控制产量', '保障基础利润贡献', '适当压缩'};
    {'成本可控', '扩大产能', '利润托底产品'};
};

% 创建图形窗口
figure;
bar(production_plan / 1e6, 0.5);  % 单位换算为百万片，柱宽0.5
xticks(1:4);
xticklabels(models);
ylabel('生产计划（百万片）');
title('各型号九月份生产计划与销售策略');

% 添加多行注释文本
for i = 1:4
    text(i, production_plan(i)/1e6 + 0.8, comments{i}, ...
        'HorizontalAlignment', 'center', ...
        'FontSize', 9, 'Color', 'k');
end

grid on;