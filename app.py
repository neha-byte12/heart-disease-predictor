"""Frontend (Streamlit). Run:  streamlit run app.py
The backend (api.py) must be running first.
"""
import requests
import streamlit as st

API_URL = "http://127.0.0.1:8000/predict"

st.set_page_config(page_title="Heart Disease Predictor", page_icon="❤️")
st.title("❤️ Heart Disease Predictor")
st.caption("Enter the examination details and the model estimates the chance of cardiovascular disease.")

LEVELS = {"Normal": 1, "Above normal": 2, "Well above normal": 3}

with st.form("patient_form"):
    c1, c2 = st.columns(2)
    age = c1.number_input("Age (years)", 18, 100, 50)
    gender = c2.selectbox("Gender", ["Female", "Male"])
    height = c1.number_input("Height (cm)", 130, 210, 165)
    weight = c2.number_input("Weight (kg)", 35.0, 200.0, 70.0)
    ap_hi = c1.number_input("Systolic BP (ap_hi)", 70, 250, 120)
    ap_lo = c2.number_input("Diastolic BP (ap_lo)", 40, 200, 80)
    chol = c1.selectbox("Cholesterol", list(LEVELS))
    gluc = c2.selectbox("Glucose", list(LEVELS))
    smoke = c1.checkbox("Smoker")
    alco = c2.checkbox("Drinks alcohol")
    active = st.checkbox("Physically active", value=True)
    go = st.form_submit_button("Predict")

st.caption("Note: smoking and alcohol are self-reported in this dataset and carry almost no signal, "
           "so the model is constrained to never lower risk because of them. "
           "Blood pressure, age and cholesterol drive the result.")

if go:
    payload = {
        "age_years": age, "gender": 1 if gender == "Female" else 2,
        "height": height, "weight": weight, "ap_hi": ap_hi, "ap_lo": ap_lo,
        "cholesterol": LEVELS[chol], "gluc": LEVELS[gluc],
        "smoke": int(smoke), "alco": int(alco), "active": int(active),
    }
    try:
        r = requests.post(API_URL, json=payload, timeout=60)
        if r.status_code == 422:
            msgs = [e["msg"] for e in r.json()["detail"]]
            st.error("Invalid input: " + "; ".join(msgs))
        else:
            r.raise_for_status()
            res = r.json()
            prob = res["disease_probability"]
            st.metric("Estimated probability of disease", f"{prob:.1%}")
            st.progress(min(prob, 1.0))
            st.caption(f"BMI: {res['bmi']}")
            if res["prediction"] == 1:
                st.error("Model prediction: disease likely")
            else:
                st.success("Model prediction: disease unlikely")
    except requests.exceptions.ConnectionError:
        st.error("Backend is not running. Start it with:  uvicorn api:app --reload")

st.divider()
st.caption("Learning project on the public Kaggle cardiovascular dataset. "
           "Not a medical diagnosis tool. Test accuracy is about 74%.")
