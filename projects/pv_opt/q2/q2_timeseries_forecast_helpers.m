clc; clear; close all;

%% 1. 数据准备和读取
% 设置Excel文件路径（请根据实际路径修改）
data_path = 'path/to/data'; % set to your data folder
filename = fullfile(data_path, '附件2：2024.1-8生产系统数据 4.14.xlsx');

% 读取数据表，保留原始列名
opts = detectImportOptions(filename);
opts.VariableNamingRule = 'preserve';

% 读取销售收入数据
salesData = readtable(filename, opts, 'Sheet', '销售收入');

% 读取硅料单耗计算数据
siliconData = readtable(filename, opts, 'Sheet', '硅料单耗计算');

% 读取耗材价格数据
materialData = readtable(filename, opts, 'Sheet', '耗材价格');

% 提取四种硅片的销量数据（单位：万片）
sales182 = salesData{3:2:end, 5}; % N型182.2 * 183.75 * 130
sales210_210 = salesData{4:2:end, 5}; % N型210 * 210 * 130
sales210_182 = salesData{5:2:end, 5}; % N型210 * 182 * 130
salesP = salesData{6:2:end, 5}; % P型210 * 210 * 150

% 提取四种硅片的售价数据（单位：元/片）
price182 = salesData{3:2:end, 4};
price210_210 = salesData{4:2:end, 4};
price210_182 = salesData{5:2:end, 4};
priceP = salesData{6:2:end, 4};

% 提取单晶方棒价格数据（单位：元/kg）
siliconPrice182 = siliconData{2:5:end, 4};
siliconPrice210_210 = siliconData{3:5:end, 4};
siliconPrice210_182 = siliconData{4:5:end, 4};
siliconPriceP = siliconData{5:5:end, 4};

% 时间点（1-8月）
months = 1:8;

% 预测9月份数据
forecastMonth = 9;

%% 2. 主程序部分
% 预测销量
[forecast182, ci182] = forecastVariable(sales182, forecastMonth);
[forecast210_210, ci210_210] = forecastVariable(sales210_210, forecastMonth);
[forecast210_182, ci210_182] = forecastVariable(sales210_182, forecastMonth);
[forecastP, ciP] = forecastVariable(salesP, forecastMonth);

% 预测价格
[forecastPrice182, ciPrice182] = forecastVariable(price182, forecastMonth);
[forecastPrice210_210, ciPrice210_210] = forecastVariable(price210_210, forecastMonth);
[forecastPrice210_182, ciPrice210_182] = forecastVariable(price210_182, forecastMonth);
[forecastPriceP, ciPriceP] = forecastVariable(priceP, forecastMonth);

% 预测单晶方棒价格
[forecastSilicon182, ciSilicon182] = forecastVariable(siliconPrice182, forecastMonth);
[forecastSilicon210_210, ciSilicon210_210] = forecastVariable(siliconPrice210_210, forecastMonth);
[forecastSilicon210_182, ciSilicon210_182] = forecastVariable(siliconPrice210_182, forecastMonth);
[forecastSiliconP, ciSiliconP] = forecastVariable(siliconPriceP, forecastMonth);

%% 3. 显示预测结果
fprintf('\n===== 9月份预测结果 =====\n');
printResult('N型182.2 * 183.75 * 130', forecast182, ci182, forecastPrice182, ciPrice182, forecastSilicon182, ciSilicon182);
printResult('N型210 * 210 * 130', forecast210_210, ci210_210, forecastPrice210_210, ciPrice210_210, forecastSilicon210_210, ciSilicon210_210);
printResult('N型210 * 182 * 130', forecast210_182, ci210_182, forecastPrice210_182, ciPrice210_182, forecastSilicon210_182, ciSilicon210_182);
printResult('P型210 * 210 * 150', forecastP, ciP, forecastPriceP, ciPriceP, forecastSiliconP, ciSiliconP);

%% 4. 可视化预测结果
% 绘制销量预测图
figure('Name', '硅片销量预测', 'Position', [100 100 1200 800]);
plotForecast(months, sales182, forecast182, ci182, forecastMonth, 1, 'N型182.2 * 183.75 * 130销量预测');
plotForecast(months, sales210_210, forecast210_210, ci210_210, forecastMonth, 2, 'N型210 * 210 * 130销量预测');
plotForecast(months, sales210_182, forecast210_182, ci210_182, forecastMonth, 3, 'N型210 * 182 * 130销量预测');
plotForecast(months, salesP, forecastP, ciP, forecastMonth, 4, 'P型210 * 210 * 150销量预测');

% 绘制价格预测图
figure('Name', '硅片价格预测', 'Position', [100 100 1200 800]);
plotForecast(months, price182, forecastPrice182, ciPrice182, forecastMonth, 1, 'N型182.2 * 183.75 * 130售价预测');
plotForecast(months, price210_210, forecastPrice210_210, ciPrice210_210, forecastMonth, 2, 'N型210 * 210 * 130售价预测');
plotForecast(months, price210_182, forecastPrice210_182, ciPrice210_182, forecastMonth, 3, 'N型210 * 182 * 130售价预测');
plotForecast(months, priceP, forecastPriceP, ciPriceP, forecastMonth, 4, 'P型210 * 210 * 150售价预测');

%% 5. 辅助函数定义
function [forecast, ci] = forecastVariable(data, forecastMonth)
    % 数据预处理：去除NaN值
    data = data(~isnan(data));
    if isempty(data) || length(data) < 5  % 样本量不足时使用简单移动平均
        forecast = mean(data);
        ci = [forecast*0.9, forecast*1.1];
        return;
    end
    
    % 平稳性检验（仅当样本量足够时）
    try
        [h, ~] = adftest(data);
        d = h == 0; % 如果不平稳则进行差分
    catch
        d = 0; % 默认不差分
    end
    
    % 自动选择ARIMA模型参数
    maxP = min(2, length(data)-1);
    maxQ = min(2, length(data)-1);
    
    % 尝试多种ARIMA模型组合
    bestAIC = Inf;
    bestModel = [];
    
    for p = 0:maxP
        for q = 0:maxQ
            try
                model = arima(p,d,q);
                [fit, ~, logL] = estimate(model, data, 'Display', 'off');
                currentAIC = aicbic(logL, p+q+1, length(data));
                
                if currentAIC < bestAIC
                    bestAIC = currentAIC;
                    bestModel = fit;
                end
            catch
                continue;
            end
        end
    end
    
    % 进行预测
    if ~isempty(bestModel)
        try
            [forecast, ymse] = forecast(bestModel, 1, 'Y0', data);
            ci = [forecast - 1.96*sqrt(ymse), forecast + 1.96*sqrt(ymse)];
            % 确保预测值和置信区间是标量
            if length(forecast) > 1
                forecast = forecast(1);
            end
            if length(ci) > 2
                ci = ci(1:2);
            end
        catch
            forecast = mean(data(end-min(2,end):end));
            ci = [forecast*0.9, forecast*1.1];
        end
    else
        forecast = mean(data(end-min(2,end):end));
        ci = [forecast*0.9, forecast*1.1];
    end
end

function printResult(type, sales, salesCI, price, priceCI, silicon, siliconCI)
    fprintf('%s硅片 - 销量: %.1f (%.1f-%.1f)万片, 售价: %.2f (%.2f-%.2f)元/片, 单晶方棒价格: %.2f (%.2f-%.2f)元/kg\n', ...
        type, sales, salesCI(1), salesCI(2), price, priceCI(1), priceCI(2), silicon, siliconCI(1), siliconCI(2));
end

function plotForecast(months, data, forecast, ci, forecastMonth, subplotIdx, titleText)
    % 确保 data 和 months 长度一致
    if length(data) ~= length(months)
        % 如果 data 长度大于 months，截取 data
        if length(data) > length(months)
            data = data(1:length(months));
        % 如果 data 长度小于 months，用 NaN 填充 data
        else
            data = [data; NaN(length(months) - length(data), 1)];
        end
    end
    subplot(2,2,subplotIdx);
    plot(months, data, 'b-o', 'LineWidth', 1.5, 'MarkerSize', 8);
    hold on;
    plot(forecastMonth, forecast, 'r*', 'MarkerSize', 12, 'LineWidth', 2);
    plot([forecastMonth, forecastMonth], ci, 'r--', 'LineWidth', 1.5);
    title(titleText, 'FontSize', 12);
    xlabel('月份', 'FontSize', 10);
    
    if contains(titleText,'销量')
        ylabel('销量(万片)', 'FontSize', 10);
    else
        ylabel('价格(元)', 'FontSize', 10);
    end
    
    legend('实际值', '预测值', '95%置信区间', 'Location', 'best');
    grid on;
    xlim([1, forecastMonth]);
    xticks(1:forecastMonth);
    set(gca, 'FontSize', 10);
end
