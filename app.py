"""Streamlit frontend. Start api.py first: uvicorn api:app --reload."""
import csv
import jsonfrom datetime import datetime
from io import StringIO
from pathlib import Path

import requests
import streamlit as st

API_URL = "https://heart-disease-api-4oke.onrender.com/predict"
LEVELS = {"Normal": 1, "Above normal": 2, "Well above normal": 3}
HISTORY_FILE = Path(__file__).with_name("prediction_history.json")

st.set_page_config(page_title="Heart Disease Predictor", page_icon="♥", layout="centered")
st.markdown("""<style>
.stApp {background:#0b1020;color:#e7edf8} [data-testid="stSidebar"]{background:#10182c}
[data-testid="stSidebar"] *{color:#e7edf8} h1,h2,h3{color:#f7f9ff}
.eyebrow{color:#78a6ff;font-size:.8rem;font-weight:700;letter-spacing:.1em;text-transform:uppercase}
.subtle{color:#aebbd0} [data-testid="stMetric"]{background:#131e35;border:1px solid #263653;padding:1rem;border-radius:.75rem}
.stButton>button,.stDownloadButton>button{background:#4f7cff;color:white;border:0;border-radius:.55rem;font-weight:650}
</style>""", unsafe_allow_html=True)


def init_history():
    if "prediction_history" not in st.session_state:
        try:
            st.session_state.prediction_history = json.loads(HISTORY_FILE.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            st.session_state.prediction_history = []


def save_history():
    HISTORY_FILE.write_text(json.dumps(st.session_state.prediction_history, indent=2), encoding="utf-8")


def heading(eyebrow, title, description):
    st.markdown(f'<p class="eyebrow">{eyebrow}</p>', unsafe_allow_html=True)
    st.title(title)
    st.markdown(f'<p class="subtle">{description}</p>', unsafe_allow_html=True)


def predict_page():
    heading("Local learning project", "Heart Disease Predictor", "Enter examination details to receive a model estimate—not a diagnosis.")
    with st.form("patient_form"):
        c1, c2 = st.columns(2)
        age = c1.number_input("Age (years)", 18, 100, 50)
        gender = c2.selectbox("Gender", ["Female", "Male"])
        height = c1.number_input("Height (cm)", 130, 210, 165)
        weight = c2.number_input("Weight (kg)", 35.0, 200.0, 70.0)
        ap_hi = c1.number_input("Systolic BP", 70, 250, 120)
        ap_lo = c2.number_input("Diastolic BP", 40, 200, 80)
        chol = c1.selectbox("Cholesterol", list(LEVELS))
        gluc = c2.selectbox("Glucose", list(LEVELS))
        smoke = c1.checkbox("Smoker")
        alco = c2.checkbox("Drinks alcohol")
        active = st.checkbox("Physically active", value=True)
        submitted = st.form_submit_button("Estimate with model", use_container_width=True)
    if not submitted:
        return

    payload = {"age_years": age, "gender": 1 if gender == "Female" else 2,
               "height": height, "weight": weight, "ap_hi": ap_hi, "ap_lo": ap_lo,
               "cholesterol": LEVELS[chol], "gluc": LEVELS[gluc], "smoke": int(smoke),
               "alco": int(alco), "active": int(active)}
    try:
        response = requests.post(API_URL, json=payload, timeout=10)
        if response.status_code == 422:
            st.error("Please correct the following: " + "; ".join(e["msg"] for e in response.json()["detail"]))
            return
        response.raise_for_status()
        result = response.json()
    except requests.exceptions.ConnectionError:
        st.error("The local backend is not running. Start it with: uvicorn api:app --reload")
        return
    except requests.RequestException as error:
        st.error(f"The prediction service could not respond: {error}")
        return

    probability = result["disease_probability"]
    label = "Higher model estimate" if result["prediction"] else "Lower model estimate"
    st.divider()
    left, right = st.columns(2)
    left.metric("Estimated probability", f"{probability:.1%}")
    right.metric("Calculated BMI", result["bmi"])
    st.progress(min(probability, 1.0))
    if result["prediction"]:
        st.warning(f"{label}. This is a statistical model output, not confirmation of disease.")
    else:
        st.success(f"{label}. A lower estimate does not rule out a health condition.")
    st.caption("Discuss concerning results or symptoms with a qualified healthcare professional.")
    st.session_state.prediction_history.insert(0, {"Time": datetime.now().strftime("%d %b %Y, %H:%M"), "Estimate": f"{probability:.1%}", "Model result": label, "BMI": result["bmi"], "Age": age, "BP": f"{ap_hi}/{ap_lo}", "Cholesterol": chol, "Glucose": gluc})
    save_history()


def history_page():
    heading("Saved locally", "Prediction history", "Estimates are saved beside this app and remain after refresh. Clear removes them.")
    rows = st.session_state.prediction_history
    if not rows:
        st.info("No estimates yet. Use Predict to add the first entry.")
        return
    st.dataframe(rows, use_container_width=True, hide_index=True)
    output = StringIO()
    writer = csv.DictWriter(output, fieldnames=rows[0].keys())
    writer.writeheader(); writer.writerows(rows)
    st.download_button("Download saved history as CSV", output.getvalue(), "heart-predictor-history.csv", "text/csv")
    if st.button("Clear saved history", type="secondary"):
        st.session_state.prediction_history = []
        try:
            HISTORY_FILE.unlink(missing_ok=True)
        except OSError:
            st.warning("The page was cleared, but the saved history file could not be removed.")
        st.rerun()


def model_page():
    heading("Verified from this project", "About the model", "Only implementation details found in the project source are shown here.")
    st.subheader("Training setup")
    st.markdown("""
- **Data:** the local `cardio_train.csv` file, described in this project as the public Kaggle cardiovascular dataset.
- **Preparation:** removes the `id` column and duplicate rows; applies the ranges in `train_model.py`; derives age in years, BMI, and pulse pressure.
- **Algorithm:** scikit-learn `HistGradientBoostingClassifier`, with a stratified 80/20 train/test split and random seed 42.
- **Output:** the API returns the positive-class probability and uses a 0.5 threshold for its label.
""")
    st.subheader("Inputs used")
    st.caption("Age, encoded gender, height, weight, systolic and diastolic BP, cholesterol, glucose, smoking, alcohol use, physical activity, BMI, and pulse pressure.")
    st.info("No evaluation score is shown because the saved model bundle does not store one. Rerun `train_model.py` to calculate metrics for a newly trained model.")


def health_page():
    heading("Education, not medical advice", "Heart health & limitations", "Use this project for learning—not for screening, treatment, or urgent decisions.")
    st.subheader("What this estimate cannot do")
    st.markdown("""
- It cannot diagnose cardiovascular disease or determine the cause of symptoms.
- It does not include clinical examination, medical history, medications, family history, ECG, laboratory testing, or many other relevant factors.
- The training data and model-building choices may not represent every person or setting.
- A probability is not a personal prognosis and can be wrong in either direction.
""")
    st.subheader("General prevention information")
    st.write("Public-health guidance highlights avoiding tobacco, being physically active, choosing a balanced diet, limiting harmful alcohol use, and working with a clinician to manage raised blood pressure, blood glucose, and blood lipids.")
    st.markdown("Source: [World Health Organization—cardiovascular diseases](https://www.who.int/news-room/fact-sheets/detail/cardiovascular-diseases-%28cvds%29).")
    st.error("Emergency: if you have chest discomfort, shortness of breath, fainting, or other possible emergency symptoms, contact local emergency services now. Do not wait for this app's result.")
    st.markdown("Warning signs: [American Heart Association](https://www.heart.org/health-topics/heart-attack/warning-signs-of-a-heart-attack).")


init_history()
page = st.sidebar.radio("Navigate", ["Predict", "Prediction history", "About the model", "Heart health & limitations"])
st.sidebar.divider()
st.sidebar.caption("Educational project · Local API · History is saved locally on this computer")
if page == "Predict":
    predict_page()
elif page == "Prediction history":
    history_page()
elif page == "About the model":
    model_page()
else:
    health_page()
