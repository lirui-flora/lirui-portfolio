% 各策略下的销量数据（单位：万片）
data = [
    584.4,  392.1,  440.6,  452.6;   % 最不利
    984.3,  392.1,  712.0,  452.6;   % 基准
    836.5,  392.1,  859.8,  452.6;   % 最有利
   1123.0,  564.4,  596.9, 1036.1    % 最优策略
];

labels = {'N1', 'N2', 'N3', 'P'};

% 用 Radar chart（极坐标雷达图）绘制
data = [data, data(:,1)]; % 闭合
theta = linspace(0, 2*pi, size(data,2));

figure;
pax = polaraxes;
hold on;

% 颜色
colors = lines(4);

% 绘图
for i = 1:size(data,1)
    polarplot(pax, theta, data(i,:), '-o', 'LineWidth', 2, 'Color', colors(i,:));
end

% 设置角度标签
pax.ThetaTick = rad2deg(theta(1:end-1));
pax.ThetaTickLabel = labels;
pax.RLim = [0 1200];

% 图例与标题
legend('最不利', '基准', '最有利', '最优策略', 'Location', 'southoutside');
title('多策略下晶硅片销量结构雷达图（单位：万片）');