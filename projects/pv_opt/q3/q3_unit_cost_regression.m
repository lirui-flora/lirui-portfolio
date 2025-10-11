% 自定义指数平滑预测函数
function forecastVal = simpleExpSmoothing(y, alpha)
    % y: 数据序列，列向量
    % alpha: 平滑因子，通常取 0.2 ~ 0.5
    s = y(1); % 初始平滑值
    for t = 2:length(y)
        s = alpha * y(t) + (1 - alpha) * s;
    end
    forecastVal = s; % 最终平滑值作为下一期预测
end
% 数据输入
data_map = struct( ...
    'N1', [17037.20; 15456.88; 13886.58; 13187.85; 13154.84; 11634.71; 10862.48; 9384.46], ...
    'N2', [22579.22; 20482.13; 18409.65; 17478.06; 17430.43; 15422.39; 14402.71; 12448.94], ...
    'N3', [19496.70; 17682.19; 15893.61; 15090.05; 15052.00; 13313.52; 12432.69; 10743.43], ...
    'P',  [21738.23; 19419.40; 17312.99; 16516.10; 16473.22; 13703.19; 13664.81; 11502.47]);

fprintf("===== 指数平滑预测（自定义）=====\n");

alpha = 0.4; % 平滑因子（可调）

models = fields(data_map);
for i = 1:length(models)
    name = models{i};
    y = data_map.(name);

    forecastVal = simpleExpSmoothing(y, alpha);
    fprintf("%s 型号第9月单位变动成本预测（指数平滑）：%.2f 元\n", name, forecastVal);
end