"""Backend (FastAPI). Run:  uvicorn api:app --reload
Docs page: http://127.0.0.1:8000/docs
"""
import joblib
import pandas as pd
from fastapi import FastAPI
from pydantic import BaseModel, Field, model_validator

bundle = joblib.load("model.joblib")
model, FEATURES = bundle["model"], bundle["features"]

app = FastAPI(title="Heart Disease Prediction API")


class Patient(BaseModel):
    age_years: float = Field(ge=18, le=100)
    gender: int = Field(ge=1, le=2, description="1 = female, 2 = male")
    height: float = Field(ge=130, le=210, description="cm")
    weight: float = Field(ge=35, le=200, description="kg")
    ap_hi: int = Field(ge=70, le=250, description="systolic BP")
    ap_lo: int = Field(ge=40, le=200, description="diastolic BP")
    cholesterol: int = Field(ge=1, le=3)
    gluc: int = Field(ge=1, le=3)
    smoke: int = Field(ge=0, le=1)
    alco: int = Field(ge=0, le=1)
    active: int = Field(ge=0, le=1)

    @model_validator(mode="after")
    def systolic_above_diastolic(self):
        if self.ap_hi <= self.ap_lo:
            raise ValueError("Systolic BP must be higher than diastolic BP")
        return self


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/predict")
def predict(p: Patient):
    row = p.model_dump()
    row["BMI"] = row["weight"] / (row["height"] / 100) ** 2
    row["pulse_pressure"] = row["ap_hi"] - row["ap_lo"]
    X = pd.DataFrame([row])[FEATURES]
    prob = float(model.predict_proba(X)[0, 1])
    return {
        "disease_probability": round(prob, 4),
        "prediction": int(prob >= 0.5),
        "bmi": round(row["BMI"], 1),
    }
