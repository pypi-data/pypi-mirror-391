from sklearn.ensemble import RandomForestClassifier
import joblib
import pandas as pd

def train_disease_model(data_path, label_col):
    """訓練疾病預測模型"""
    data = pd.read_csv(data_path)
    X = data.drop(columns=[label_col])
    y = data[label_col]
    model = RandomForestClassifier(n_estimators=200)
    model.fit(X, y)
    joblib.dump(model, "models/disease_predictor.pkl")
    return "✅ 模型訓練完成"

def predict_disease(sample):
    """使用訓練模型進行疾病風險預測"""
    model = joblib.load("models/disease_predictor.pkl")
    prob = model.predict_proba([sample])[0][1]
    return {"風險值": round(prob, 4), "建議": "進一步檢查" if prob > 0.7 else "正常"}
