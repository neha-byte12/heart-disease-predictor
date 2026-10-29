# Heart Disease Predictor (Part C)

Backend: FastAPI (`api.py`). Frontend: Streamlit (`app.py`). Model: Gradient Boosting trained in `train_model.py`.

## Run
1. Put `cardio_train.csv` in this folder (extracted, not zipped).
2. `pip install -r requirements.txt`
3. `python train_model.py`  (creates model.joblib)
4. Terminal 1: `uvicorn api:app --reload`
5. Terminal 2: `streamlit run app.py`  (opens in browser)

API docs page: http://127.0.0.1:8000/docs
