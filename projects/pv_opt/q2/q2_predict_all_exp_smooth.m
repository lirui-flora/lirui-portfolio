function predict_all_es()
    % Desensitized header
    data_path = 'path/to/data'; % set to your data directory
    file = fullfile(data_path, 'q2', 'pre1.xlsx');
    sheets = {'Sheet1', 'Sheet2', 'Sheet3', 'Sheet4'};
    T = 100;          % 扰动预测次数
    noise_ratio = 0.03; % 噪声比例
    
    for i = 1:length(sheets)
        sheet = sheets{i};
        fprintf('====== 型号：%s ======\n', sheet);
        
        % 读取数据
        data = readtable(file, 'Sheet', sheet);
        if ~all(ismember({'UnitPrice', 'RodPrice', 'Sales'}, data.Properties.VariableNames))
            fprintf('缺失必要变量，跳过 %s\n\n', sheet);
            continue;
        end
        unitPrice = data.UnitPrice;
        rodPrice = data.RodPrice;
        sales = data.Sales;
        
        % ----------------- 1. 联合建模预测销量 -----------------
        fprintf('\n【%s】指数平滑预测销量 Sales：\n', sheet);
        predict_sales_combined_es(unitPrice, rodPrice, sales, T, noise_ratio, sheet);
        
        % ----------------- 2. 单变量预测 UnitPrice -----------------
        fprintf('\n【%s】指数平滑预测售价 UnitPrice：\n', sheet);
        predict_one_variable_es(unitPrice, T, noise_ratio, 'UnitPrice', sheet);
        
        % ----------------- 3. 单变量预测 RodPrice -----------------
        fprintf('\n【%s】指数平滑预测方棒价格 RodPrice：\n', sheet);
        predict_one_variable_es(rodPrice, T, noise_ratio, 'RodPrice', sheet);
        
        fprintf('==============================\n\n');
    end
end

function predict_sales_combined_es(unitPrice, rodPrice, sales, T, noise_ratio, tag)
    % 步骤1: 分别预测UnitPrice和RodPrice
    pred_unit = predict_one_variable_es(unitPrice, T, noise_ratio, 'UnitPrice', tag);
    pred_rod = predict_one_variable_es(rodPrice, T, noise_ratio, 'RodPrice', tag);
    
    % 步骤2: 使用预测的UnitPrice和RodPrice生成Sales预测
    X = [unitPrice, rodPrice];
    Y = sales;
    preds = zeros(T,1);
    for t = 1:T
        % 添加噪声生成扰动后的输入
        noisy_unit = pred_unit.mean + noise_ratio * pred_unit.mean * randn();
        noisy_rod = pred_rod.mean + noise_ratio * pred_rod.mean * randn();
        
        % 假设线性关系: Sales = a*UnitPrice + b*RodPrice + c
        mdl = fitlm(X, Y); % 使用历史数据拟合线性模型
        preds(t) = predict(mdl, [noisy_unit, noisy_rod]);
    end
    
    show_prediction_result(preds, 'Sales', tag);
end

function result = predict_one_variable_es(series, T, noise_ratio, var_name, tag)
    % Holt线性趋势指数平滑
    alpha = 0.3;  % 水平平滑系数
    beta = 0.1;   % 趋势平滑系数
    
    % 初始化
    level = series(1);
    trend = series(2) - series(1);
    n = length(series);
    
    % 拟合模型
    for i = 2:n
        new_level = alpha * series(i) + (1 - alpha) * (level + trend);
        new_trend = beta * (new_level - level) + (1 - beta) * trend;
        level = new_level;
        trend = new_trend;
    end
    
    % 基础预测
    base_forecast = level + trend;
    
    % 生成扰动预测
    preds = zeros(T,1);
    for t = 1:T
        noise = noise_ratio * base_forecast * randn();
        preds(t) = base_forecast + noise;
    end
    
    % 返回结果
    result.mean = base_forecast;
    result.preds = preds;
    
    % 显示结果
    show_prediction_result(preds, var_name, tag);
end

function show_prediction_result(preds, var_name, tag)
    y_mean = mean(preds);
    y_std = std(preds);
    lower = y_mean - 1.96*y_std;
    upper = y_mean + 1.96*y_std;
    
    fprintf('%s 第9个月预测均值：%.4f\n', var_name, y_mean);
    fprintf('95%%置信区间：%.4f - %.4f\n', lower, upper);
    
    figure;
    histogram(preds, 15);
    title([tag '：第9个月预测 ' var_name ' 分布']);
    xlabel([var_name ' 预测值']);
    ylabel('频数');
    xline(y_mean, '--r', '均值');
    xline(lower, '--g', '下界');
    xline(upper, '--g', '上界');
end