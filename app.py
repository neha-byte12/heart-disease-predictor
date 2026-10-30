import streamlit as st
import requests
import csv
from pathlib import Path
from datetime import datetime

# =====================================================
# CONFIGURATION
# =====================================================

API_URL = "https://heart-disease-api-4oke.onrender.com/predict"

BASE_DIR = Path(__file__).parent
HISTORY_FILE = BASE_DIR / "prediction_history.csv"

st.set_page_config(
    page_title="HealthAI | Heart Disease Predictor",
    page_icon="❤️",
    layout="wide",
    initial_sidebar_state="expanded"
)

LEVELS = {
    "Normal": 1,
    "Above normal": 2,
    "Well above normal": 3
}

PAGES = [
    "Home",
    "Predict",
    "Results",
    "Prediction History",
    "About"
]

# =====================================================
# SESSION STATE
# =====================================================

if "navigation" not in st.session_state:
    st.session_state.navigation = "Home"

if "next_page" in st.session_state:
    st.session_state.navigation = st.session_state.next_page
    del st.session_state.next_page

if "result" not in st.session_state:
    st.session_state.result = None

if "confirm_delete" not in st.session_state:
    st.session_state.confirm_delete = False

# =====================================================
# CUSTOM CSS
# =====================================================

st.markdown("""
<style>
.stApp {
    background-color: #111A20;
    color: #E5EAE6;
}

.block-container {
    max-width: 1150px;
    padding-top: 2rem;
    padding-bottom: 3rem;
}

[data-testid="stSidebar"] {
    background-color: #172329;
    border-right: 1px solid #293B3D;
}

[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p {
    color: #A5B4B0;
}

h1, h2, h3 {
    color: #E5EAE6 !important;
}

p {
    color: #A5B4B0;
}

.hero-label {
    color: #83B5A2;
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 2px;
}

.hero-description {
    color: #A5B4B0;
    font-size: 15px;
    line-height: 1.8;
}

.hero-title {
    color: #E5EAE6;
    font-size: 38px;
    font-weight: 750;
    margin-top: 10px;
}

[data-testid="stVerticalBlockBorderWrapper"] {
    background-color: #1C292D;
    border: 1px solid #304044;
    border-radius: 14px;
    padding: 12px;
}

[data-testid="stMetric"] {
    background-color: #1C292D;
    border: 1px solid #304044;
    border-radius: 12px;
    padding: 18px;
}

[data-testid="stMetricLabel"] {
    color: #A5B4B0;
}

[data-testid="stMetricValue"] {
    color: #E5EAE6;
}

[data-testid="stWidgetLabel"] p {
    color: #C4D0CA;
    font-weight: 550;
}

.stNumberInput input,
.stSelectbox div[data-baseweb="select"] > div {
    background-color: #26373A;
    color: #E5EAE6;
    border-color: #405355;
    border-radius: 8px;
}

.stButton button,
.stFormSubmitButton button {
    background-color: #527F70;
    color: white;
    border: 1px solid #527F70;
    border-radius: 9px;
    font-weight: 600;
    min-height: 42px;
    transition: 0.2s ease;
}

.stButton button:hover,
.stFormSubmitButton button:hover {
    background-color: #659783;
    color: white;
    border-color: #659783;
}

[data-testid="stRadio"] label {
    color: #D2DDD6;
}

.result-card {
    background-color: #1C292D;
    border: 1px solid #405355;
    border-radius: 16px;
    padding: 25px;
}

.result-number {
    color: #83B5A2;
    font-size: 48px;
    font-weight: 750;
    margin: 8px 0;
}

.result-label {
    color: #A5B4B0;
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 1.5px;
}

.feature-title {
    color: #E5EAE6;
    font-size: 17px;
    font-weight: 650;
}

.feature-description {
    color: #A5B4B0;
    font-size: 13px;
    line-height: 1.7;
}

.stProgress > div > div > div {
    background-color: #83B5A2;
}

.footer {
    text-align: center;
    color: #71827B;
    font-size: 12px;
    padding-top: 35px;
    line-height: 2;
}

hr {
    border-color: #304044;
}
</style>
""", unsafe_allow_html=True)

# =====================================================
# HELPER FUNCTIONS
# =====================================================

def save_history(probability, prediction, bmi):
    file_exists = HISTORY_FILE.exists()

    with open(HISTORY_FILE, "a", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)

        if not file_exists:
            writer.writerow([
                "Date",
                "Probability",
                "Prediction",
                "BMI"
            ])

        writer.writerow([
            datetime.now().strftime("%d-%m-%Y %H:%M"),
            f"{probability:.4f}",
            "Disease likely" if prediction == 1 else "Disease unlikely",
            bmi
        ])


def get_history():
    if not HISTORY_FILE.exists():
        return []

    with open(HISTORY_FILE, "r", newline="", encoding="utf-8") as file:
        return list(csv.DictReader(file))


def page_header(label, title, description):
    st.markdown(
        f"""
        <div style="padding: 20px 0 28px 0;">
            <div class="hero-label">{label}</div>
            <div class="hero-title">{title}</div>
            <p class="hero-description">{description}</p>
        </div>
        """,
        unsafe_allow_html=True
    )


def feature_card(icon, title, description):
    st.markdown(
        f"""
        <div style="
            background:#1C292D;
            border:1px solid #304044;
            border-radius:14px;
            padding:22px;
            min-height:145px;
        ">
            <div style="font-size:24px;">{icon}</div>
            <div class="feature-title">{title}</div>
            <div class="feature-description">{description}</div>
        </div>
        """,
        unsafe_allow_html=True
    )


# =====================================================
# SIDEBAR
# =====================================================

with st.sidebar:
    st.markdown(
        """
        <div style="padding:12px 0 18px 0;">
            <div style="font-size:25px;font-weight:750;color:#E5EAE6;">
                ♡ HealthAI
            </div>
            <div style="
                font-size:10px;
                color:#83B5A2;
                letter-spacing:2px;
            ">
                CARDIOVASCULAR HEALTH
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.divider()
    st.caption("MAIN MENU")

    selected_page = st.radio(
        "Navigation",
        PAGES,
        key="navigation",
        label_visibility="collapsed"
    )

    st.divider()
    st.markdown("### Project")
    st.caption("Heart Disease Prediction")
    st.caption("Machine Learning Application")
    st.divider()

    st.markdown(
        """
        <div style="font-size:11px;color:#71827B;">
            VERSION 1.0<br><br>
            Python · Streamlit · FastAPI
        </div>
        """,
        unsafe_allow_html=True
    )

# =====================================================
# PAGE 1: HOME
# =====================================================

if selected_page == "Home":
    page_header(
        "WELCOME TO HEALTHAI",
        "Your heart, our focus. ❤️",
        "An AI-assisted cardiovascular disease prediction application built using machine learning."
    )

    with st.container(border=True):
        st.markdown(
            """
            <div style="padding:10px 5px;">
                <div class="hero-label">HEALTH ASSESSMENT</div>
                <h2 style="margin-top:12px;">Understand your heart health.</h2>
                <p>
                    Enter medical and lifestyle parameters to receive
                    a machine learning based cardiovascular disease estimate.
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )

        if st.button("Start Prediction →", use_container_width=True):
            st.session_state.next_page = "Predict"
            st.rerun()

    st.markdown("## Explore HealthAI")

    c1, c2 = st.columns(2)

    with c1:
        feature_card(
            "♡",
            "Heart Prediction",
            "Estimate cardiovascular disease probability using patient health parameters."
        )

    with c2:
        feature_card(
            "◷",
            "Prediction History",
            "Review previously generated prediction records."
        )

    st.markdown("<br>", unsafe_allow_html=True)

    c1, c2 = st.columns(2)

    with c1:
        feature_card(
            "◈",
            "Results Analysis",
            "View probability estimates, BMI and model output."
        )

    with c2:
        feature_card(
            "ⓘ",
            "About the Project",
            "Explore the technologies, dataset and model information."
        )

    st.markdown("<br>", unsafe_allow_html=True)

    history = get_history()
    c1, c2 = st.columns(2)
    c1.metric("Total Predictions", len(history))
    c2.metric("Model Test Accuracy", "Approximately 74%")


# =====================================================
# PAGE 2: PREDICT
# =====================================================

elif selected_page == "Predict":
    page_header(
        "HEALTH ASSESSMENT",
        "Patient Information",
        "Provide the required examination details below."
    )

    with st.form("patient_form"):
        with st.container(border=True):
            st.markdown("### 01 · Personal Information")
            c1, c2 = st.columns(2)

            age = c1.number_input("Age (years)", 18, 100, 50)
            gender = c2.selectbox("Gender", ["Female", "Male"])
            height = c1.number_input("Height (cm)", 130, 210, 165)
            weight = c2.number_input("Weight (kg)", 35.0, 200.0, 70.0)

        with st.container(border=True):
            st.markdown("### 02 · Medical Measurements")
            c1, c2 = st.columns(2)

            ap_hi = c1.number_input(
                "Systolic Blood Pressure (ap_hi)", 70, 250, 120
            )
            ap_lo = c2.number_input(
                "Diastolic Blood Pressure (ap_lo)", 40, 200, 80
            )
            chol = c1.selectbox("Cholesterol", list(LEVELS.keys()))
            gluc = c2.selectbox("Glucose", list(LEVELS.keys()))

        with st.container(border=True):
            st.markdown("### 03 · Lifestyle Information")
            c1, c2, c3 = st.columns(3)

            smoke = c1.checkbox("Smoker")
            alco = c2.checkbox("Drinks alcohol")
            active = c3.checkbox("Physically active", value=True)

        st.markdown("<br>", unsafe_allow_html=True)

        go = st.form_submit_button(
            "♡  Generate Prediction",
            use_container_width=True
        )

    if go:
        payload = {
            "age_years": age,
            "gender": 1 if gender == "Female" else 2,
            "height": height,
            "weight": weight,
            "ap_hi": ap_hi,
            "ap_lo": ap_lo,
            "cholesterol": LEVELS[chol],
            "gluc": LEVELS[gluc],
            "smoke": int(smoke),
            "alco": int(alco),
            "active": int(active)
        }

        try:
            with st.spinner("Analyzing patient parameters..."):
                response = requests.post(
                    API_URL,
                    json=payload,
                    timeout=60
                )

                if response.status_code == 422:
                    errors = [
                        e["msg"] for e in response.json()["detail"]
                    ]
                    st.error("Invalid input: " + "; ".join(errors))
                else:
                    response.raise_for_status()
                    res = response.json()

                    prob = res["disease_probability"]
                    prediction = res["prediction"]
                    bmi = res["bmi"]

                    result_data = {
                        "probability": prob,
                        "prediction": prediction,
                        "bmi": bmi,
                        "date": datetime.now().strftime("%d-%m-%Y %H:%M")
                    }

                    st.session_state.result = result_data
                    save_history(prob, prediction, bmi)

                    st.session_state.next_page = "Results"
                    st.rerun()

        except requests.exceptions.ConnectionError:
            st.error(
                "Unable to connect to the prediction API. "
                "Check your internet connection and deployed backend."
            )

        except requests.exceptions.Timeout:
            st.error(
                "The prediction request timed out. Try again in a moment."
            )

        except requests.exceptions.RequestException as e:
            st.error(f"Request failed: {e}")


# =====================================================
# PAGE 3: RESULTS
# =====================================================

elif selected_page == "Results":
    page_header(
        "ANALYSIS SUMMARY",
        "Prediction Results",
        "Your latest machine learning prediction."
    )

    result = st.session_state.result

    if result is None:
        st.info(
            "No prediction is available yet. "
            "Visit the Predict page to generate your first result."
        )

        if st.button("Go to Prediction →"):
            st.session_state.next_page = "Predict"
            st.rerun()

    else:
        prob = float(result["probability"])
        prediction = result["prediction"]
        bmi = result["bmi"]

        with st.container(border=True):
            st.markdown(
                '<div class="result-label">ESTIMATED DISEASE PROBABILITY</div>',
                unsafe_allow_html=True
            )

            st.markdown(
                f'<div class="result-number">{prob:.1%}</div>',
                unsafe_allow_html=True
            )

            st.progress(min(max(float(prob), 0.0), 1.0))

            st.caption(
                "Probability estimated by the machine learning model."
            )

        st.markdown("<br>", unsafe_allow_html=True)

        c1, c2 = st.columns(2)

        with c1:
            st.metric("Body Mass Index (BMI)", bmi)

        with c2:
            st.metric(
                "Prediction Status",
                "Disease likely" if prediction == 1 else "Disease unlikely"
            )

        st.markdown("### Model Assessment")

        if prediction == 1:
            st.error(
                "The model predicts that cardiovascular disease is likely "
                "based on the submitted parameters."
            )
        else:
            st.success(
                "The model predicts that cardiovascular disease is unlikely "
                "based on the submitted parameters."
            )

        st.caption(f"Prediction generated: {result['date']}")

        st.info(
            "This result is an educational machine learning estimate, "
            "not a medical diagnosis. A low predicted probability does not "
            "rule out cardiovascular disease."
        )

        if st.button("Make Another Prediction →"):
            st.session_state.next_page = "Predict"
            st.rerun()


# =====================================================
# PAGE 4: PREDICTION HISTORY
# =====================================================

elif selected_page == "Prediction History":
    page_header(
        "RECORD MANAGEMENT",
        "Prediction History",
        "Review your previously generated prediction records."
    )

    history = get_history()

    if history:
        total = len(history)

        likely = sum(
            1 for row in history
            if row["Prediction"] == "Disease likely"
        )

        c1, c2, c3 = st.columns(3)

        c1.metric("Total Predictions", total)
        c2.metric("Disease Likely", likely)
        c3.metric("Disease Unlikely", total - likely)

        st.markdown("## Previous Records")

        st.dataframe(
            history[::-1],
            use_container_width=True,
            hide_index=True
        )

        c1, c2 = st.columns(2)

        with c1:
            with open(HISTORY_FILE, "rb") as file:
                st.download_button(
                    "↓ Download History CSV",
                    data=file,
                    file_name="prediction_history.csv",
                    mime="text/csv",
                    use_container_width=True
                )

        with c2:
            if st.button("Delete History", use_container_width=True):
                st.session_state.confirm_delete = True

        if st.session_state.confirm_delete:
            st.warning(
                "Are you sure? This will permanently delete all records."
            )

            c1, c2 = st.columns(2)

            with c1:
                if st.button("Yes, Delete All", type="primary"):
                    HISTORY_FILE.unlink(missing_ok=True)
                    st.session_state.confirm_delete = False
                    st.rerun()

            with c2:
                if st.button("Cancel"):
                    st.session_state.confirm_delete = False
                    st.rerun()

    else:
        st.session_state.confirm_delete = False

        with st.container(border=True):
            st.markdown("### No records yet")

            st.write(
                "Your prediction history will appear here "
                "after your first assessment."
            )

            if st.button("Create First Prediction →"):
                st.session_state.next_page = "Predict"
                st.rerun()


# =====================================================
# PAGE 5: ABOUT
# =====================================================

elif selected_page == "About":
    page_header(
        "PROJECT INFORMATION",
        "About HealthAI",
        "A machine learning project focused on cardiovascular "
        "disease probability estimation."
    )

    with st.container(border=True):
        st.markdown("## ♡ Project Overview")

        st.write(
            "Heart Disease Predictor is a machine learning application "
            "that estimates the probability of cardiovascular disease "
            "using patient health and lifestyle parameters."
        )

        st.write(
            "The application accepts information such as age, gender, "
            "height, weight, blood pressure, cholesterol, glucose "
            "and lifestyle habits."
        )

    st.markdown("## Technology Stack")

    c1, c2 = st.columns(2)

    with c1:
        with st.container(border=True):
            st.markdown("### Python")
            st.caption("Core programming language")

            st.markdown("### Streamlit")
            st.caption("Frontend framework")

            st.markdown("### Machine Learning")
            st.caption("Prediction model")

    with c2:
        with st.container(border=True):
            st.markdown("### FastAPI")
            st.caption("Backend API")

            st.markdown("### Render")
            st.caption("Backend deployment")

            st.markdown("### Kaggle")
            st.caption("Cardiovascular dataset source")

    st.markdown("## Model Information")

    with st.container(border=True):
        st.metric("Reported Test Accuracy", "~74%")

        st.write(
            "The model was trained using a public Kaggle "
            "cardiovascular disease dataset."
        )

        st.write(
            "Smoking and alcohol are self-reported in this dataset "
            "and carry almost no signal, so the model is constrained "
            "to never lower risk because of them. Blood pressure, "
            "age and cholesterol drive the result."
        )

    st.warning(
        "This project is intended for educational purposes. "
        "It is not a substitute for professional medical advice, "
        "diagnosis or treatment."
    )


# =====================================================
# FOOTER
# =====================================================

st.markdown(
    """
    <div class="footer">
        ♡ HEALTHAI<br>
        HEART DISEASE PREDICTION SYSTEM<br><br>
        Built with Python · Streamlit · FastAPI<br>
        Educational Machine Learning Project
    </div>
    """,
    unsafe_allow_html=True
)
