function predict_all()
    % Desensitized header
    data_path = 'path/to/data'; % set to your data directory
    file = fullfile(data_path, 'q2', 'pre1.xlsx');
    sheets = {'Sheet1', 'Sheet2', 'Sheet3', 'Sheet4'};
    window = 3;    % 滑动窗口
    T = 100;       % 扰动预测次数
    noise_ratio = 0.03;

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
        fprintf('\n【%s】联合建模预测销量 Sales：\n', sheet);
        predict_sales_combined(unitPrice, rodPrice, sales, window, T, noise_ratio, sheet);

        % ----------------- 2. 单变量预测 UnitPrice -----------------
        fprintf('\n【%s】单变量预测售价 UnitPrice：\n', sheet);
        predict_one_variable(unitPrice, window, T, noise_ratio, 'UnitPrice', sheet);

        % ----------------- 3. 单变量预测 RodPrice -----------------
        fprintf('\n【%s】单变量预测方棒价格 RodPrice：\n', sheet);
        predict_one_variable(rodPrice, window, T, noise_ratio, 'RodPrice', sheet);

        fprintf('==============================\n\n');
    end
end
function predict_sales_combined(unitPrice, rodPrice, sales, window, T, noise_ratio, tag)
    X = {};
    Y = [];

    for t = 1:(length(sales) - window)
        x_input = [unitPrice(t:t+window-1)'; rodPrice(t:t+window-1)'];  % 2 × window
        X{end+1} = x_input;
        Y(end+1, 1) = sales(t + window);
    end

    % 修改输入层为特征维度 2
    layers = [
        sequenceInputLayer(2)
        lstmLayer(32, 'OutputMode','last')
        fullyConnectedLayer(1)
        regressionLayer
    ];

    options = trainingOptions('adam', ...
        'MaxEpochs', 300, ...
        'MiniBatchSize', 1, ...
        'Shuffle','every-epoch', ...
        'Verbose', false);

    fprintf('训练网络中...\n');
    net = trainNetwork(X, Y, layers, options);

    % 构造最后输入
    x_last = [unitPrice(end-window+1:end)'; rodPrice(end-window+1:end)'];  % 2 × window

    preds = zeros(T,1);
    for t = 1:T
        noise = noise_ratio * x_last .* randn(size(x_last));
        x_noisy = x_last + noise;
        preds(t) = predict(net, {x_noisy});
    end

    show_prediction_result(preds, 'Sales', tag);
end
function predict_one_variable(series, window, T, noise_ratio, var_name, tag)
    X = {};
    Y = [];

    for t = 1:(length(series) - window)
        X{end+1} = series(t:t+window-1)';
        Y(end+1,1) = series(t+window);
    end

    layers = [
        sequenceInputLayer(1)
        lstmLayer(32, 'OutputMode','last')
        fullyConnectedLayer(1)
        regressionLayer
    ];

    options = trainingOptions('adam', ...
        'MaxEpochs', 300, ...
        'MiniBatchSize', 1, ...
        'Shuffle','every-epoch', ...
        'Verbose', false);

    net = trainNetwork(X, Y, layers, options);

    x_last = series(end-window+1:end)';
    preds = zeros(T,1);
    for t = 1:T
        noise = noise_ratio * x_last .* randn(size(x_last));
        x_noisy = x_last + noise;
        preds(t) = predict(net, {x_noisy});
    end

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