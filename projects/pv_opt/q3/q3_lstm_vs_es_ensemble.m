
% LSTM 和指数平滑模型预测结果
LSTM_predictions = [8611.53, 11421.77, 9857.74, 10329.04];  % LSTM预测值
ES_predictions = [11053.74, 14656.04, 12651.26, 13642.73];  % 指数平滑预测值

% 均匀加权
w_LSTM = 0.5;  % LSTM权重
w_ES = 0.5;    % 指数平滑法权重

% 计算加权平均
final_predictions_weighted = w_LSTM * LSTM_predictions + w_ES * ES_predictions;

% 输出加权平均结果
fprintf('N1 型号第九月单位变动成，本预测（加权平均）：%.2f 元\n', final_predictions_weighted(1));
fprintf('N2 型号第九月单位变动成本预测（加权平均）：%.2f 元\n', final_predictions_weighted(2));
fprintf('N3 型号第九月单位变动成本预测（加权平均）：%.2f 元\n', final_predictions_weighted(3));
fprintf('P 型号第九月单位变动成本预测（加权平均）：%.2f 元\n', final_predictions_weighted(4));