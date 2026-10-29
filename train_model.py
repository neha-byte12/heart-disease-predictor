"""Trains the final model (Gradient Boosting) and saves it to model.joblib.
Run once:  python train_model.py   (needs cardio_train.csv in the same folder)
"""
import joblib
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.metrics import accuracy_score, f1_score

FEATURES = ["age_years", "gender", "height", "weight", "ap_hi", "ap_lo", "cholesterol",
            "gluc", "smoke", "alco", "active", "BMI", "pulse_pressure"]

df = pd.read_csv("cardio_train.csv", sep=";")
data = df.drop(columns="id").drop_duplicates().copy()
data = data[
    data["ap_hi"].between(70, 250) & data["ap_lo"].between(40, 200)
    & (data["ap_hi"] > data["ap_lo"])
    & data["height"].between(130, 210) & data["weight"].between(35, 200)
].copy()
data["age_years"] = data["age"] / 365.25
data["BMI"] = data["weight"] / (data["height"] / 100) ** 2
data["pulse_pressure"] = data["ap_hi"] - data["ap_lo"]

X, y = data[FEATURES], data["cardio"]
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, stratify=y, random_state=42)

model = HistGradientBoostingClassifier(
    learning_rate=0.05, max_depth=5, max_iter=150, random_state=42)
model.fit(X_train, y_train)

pred = model.predict(X_test)
print("Test accuracy: %.4f | F1: %.4f" % (accuracy_score(y_test, pred), f1_score(y_test, pred)))
joblib.dump({"model": model, "features": FEATURES}, "model.joblib")
print("Saved model.joblib")
