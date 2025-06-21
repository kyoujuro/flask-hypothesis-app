from sklearn.linear_model import LinearRegression, Lasso, LogisticRegression
from sklearn.svm import SVR
from sklearn.metrics import mean_squared_error, r2_score, accuracy_score
import numpy as np
import pandas as pd


def run_regression(df, model_type, target_col, feature_cols):
    X = df[feature_cols].select_dtypes(include=[np.number]).dropna()
    y = df[target_col].dropna()

    # 特徴量と目的変数の長さを揃える
    X, y = X.align(y, join='inner', axis=0)

    if model_type == 'linear':
        model = LinearRegression()
    elif model_type == 'lasso':
        model = Lasso(alpha=0.1)
    elif model_type == 'logistic':
        model = LogisticRegression(max_iter=1000)
    elif model_type == 'svm':
        model = SVR()
    else:
        return "未対応のモデルです"

    try:
        model.fit(X, y)
        y_pred = model.predict(X)

        result = {
            'model': model.__class__.__name__,
            'intercept': getattr(model, 'intercept_', None),
            'coefficients': dict(zip(feature_cols, model.coef_)) if hasattr(model, 'coef_') else 'なし',
        }

        if model_type == 'logistic':
            y_pred_label = (y_pred > 0.5).astype(int)
            result['accuracy'] = accuracy_score(y, y_pred_label)
        else:
            result['r2_score'] = r2_score(y, y_pred)
            result['rmse'] = np.sqrt(mean_squared_error(y, y_pred))

        return result
    except Exception as e:
        return {"error": str(e)}
