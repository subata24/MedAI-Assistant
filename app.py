import html
import os

import requests
import streamlit as st
from dotenv import load_dotenv
from core.memory import get_memory_context, update_memory


st.set_page_config(
    page_title="MedAI Assistant",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded",
)

load_dotenv()

API_URL = os.getenv("API_URL", "http://127.0.0.1:8000").rstrip("/")
try:
    API_URL = st.secrets.get("API_URL", API_URL).rstrip("/")
except Exception:
    pass

REQUEST_TIMEOUT = 30


if "current_patient" not in st.session_state:
    st.session_state.current_patient = None

if "current_patient_id" not in st.session_state:
    st.session_state.current_patient_id = None

if "chat_memory" not in st.session_state:
    st.session_state.chat_memory = {}

if "ai_output" not in st.session_state:
    st.session_state.ai_output = {}


st.markdown(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

body,
.stApp {
    background:
        radial-gradient(circle at top left, rgba(37,99,235,0.10), transparent 30%),
        linear-gradient(180deg, #F8FAFC 0%, #EEF2F7 100%);
}

#MainMenu, footer {
    visibility: hidden;
}

.block-container {
    padding-top: 1.5rem;
    padding-bottom: 2rem;
    max-width: 1450px;
}

section[data-testid="stSidebar"] {
    background:
        linear-gradient(180deg, rgba(14,165,233,0.08), transparent 22%),
        linear-gradient(180deg, #06111F 0%, #101827 100%);
    border-right: 1px solid #1E293B;
    min-width: 320px !important;
    max-width: 320px !important;
}

section[data-testid="stSidebar"] > div {
    width: 320px !important;
}

[data-testid="stSidebar"] * {
    color: #E2E8F0;
}

.hero {
    background:
        linear-gradient(135deg, rgba(15,23,42,0.96), rgba(12,74,110,0.92)),
        linear-gradient(90deg, #0F172A, #134E4A);
    padding: 30px 32px;
    border-radius: 16px;
    margin-bottom: 24px;
    border: 1px solid rgba(226,232,240,0.18);
    box-shadow: 0 24px 60px rgba(15,23,42,0.18);
    position: relative;
    overflow: hidden;
}

.hero::after {
    content: "";
    position: absolute;
    inset: auto -8% -45% 58%;
    height: 220px;
    background: radial-gradient(circle, rgba(45,212,191,0.28), transparent 62%);
    pointer-events: none;
}

.hero-row {
    position: relative;
    z-index: 1;
    display: flex;
    align-items: flex-end;
    justify-content: space-between;
    gap: 24px;
}

.hero-kicker {
    color: #67E8F9;
    font-size: 12px;
    font-weight: 700;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    margin-bottom: 8px;
}

.hero-title {
    font-size: 36px;
    font-weight: 700;
    color: white;
    line-height: 1.15;
}

.hero-sub {
    color: #CBD5E1;
    margin-top: 8px;
    font-size: 15px;
}

.hero-stats {
    display: grid;
    grid-template-columns: repeat(2, minmax(120px, 1fr));
    gap: 12px;
    min-width: 280px;
}

.stat-card {
    background: rgba(255,255,255,0.10);
    border: 1px solid rgba(255,255,255,0.16);
    border-radius: 12px;
    padding: 14px;
}

.stat-value {
    color: #FFFFFF;
    font-size: 24px;
    font-weight: 700;
}

.stat-label {
    color: #BAE6FD;
    font-size: 12px;
    margin-top: 2px;
}

.live-badge {
    margin-top: 18px;
    display: inline-block;
    background: rgba(16,185,129,0.15);
    color: #6EE7B7;
    padding: 8px 14px;
    border-radius: 999px;
    font-size: 12px;
    font-weight: 600;
}

.live-badge.offline {
    background: rgba(239,68,68,0.15);
    color: #FCA5A5;
}

.card-title {
    font-size: 16px;
    font-weight: 700;
    margin-bottom: 18px;
    color: #0F172A;
}

.section-panel {
    background: rgba(255,255,255,0.88);
    border: 1px solid #E2E8F0;
    border-radius: 16px;
    padding: 20px;
    box-shadow: 0 16px 36px rgba(15,23,42,0.08);
}

.patient-header {
    background: white;
    border: 1px solid #E2E8F0;
    border-radius: 16px;
    padding: 18px 20px;
    margin-bottom: 18px;
    box-shadow: 0 12px 28px rgba(15,23,42,0.06);
}

.patient-name {
    font-size: 24px;
    font-weight: 700;
    color: #0F172A;
}

.patient-meta {
    color: #64748B;
    font-size: 13px;
    margin-top: 4px;
}

.risk-pill {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    min-width: 96px;
    border-radius: 999px;
    padding: 10px 14px;
    font-size: 13px;
    font-weight: 700;
}

.risk-low {
    color: #047857;
    background: #D1FAE5;
}

.risk-medium {
    color: #B45309;
    background: #FEF3C7;
}

.risk-high {
    color: #B91C1C;
    background: #FEE2E2;
}

.stButton > button {
    width: 100%;
    border-radius: 12px;
    border: none;
    background: linear-gradient(135deg,#2563EB,#06B6D4);
    color: white;
    font-weight: 600;
    padding: 12px 18px;
    box-shadow: 0 12px 22px rgba(37,99,235,0.22);
    transition: transform 120ms ease, box-shadow 120ms ease;
}

.stButton > button:hover {
    transform: translateY(-1px);
    box-shadow: 0 16px 28px rgba(37,99,235,0.28);
}

.ai-box {
    background: linear-gradient(180deg, #F8FAFC 0%, #EFF6FF 100%);
    border: 1px solid #BFDBFE;
    border-radius: 14px;
    padding: 18px;
    line-height: 1.8;
    color: #334155;
}

.empty-box {
    background: linear-gradient(180deg, rgba(255,255,255,0.94), rgba(248,250,252,0.94));
    border: 1px dashed #94A3B8;
    border-radius: 16px;
    padding: 90px 20px;
    text-align: center;
    box-shadow: 0 18px 42px rgba(15,23,42,0.08);
}

.empty-title {
    font-size: 24px;
    font-weight: 700;
    margin-top: 14px;
}

.empty-sub {
    margin-top: 8px;
    color: #64748B;
}

[data-testid="stChatMessage"] {
    border-radius: 14px;
    border: 1px solid #E2E8F0;
    padding: 10px;
}

/* Sidebar Inputs */
.stTextInput input,
.stNumberInput input,
.stTextArea textarea {
    background-color: #0F172A !important;
    color: #FFFFFF !important;
    -webkit-text-fill-color: #FFFFFF !important;
    border: 1px solid #334155 !important;
    border-radius: 10px !important;
    font-size: 15px !important;
    opacity: 1 !important;
}

.stNumberInput button {
    background: #111827 !important;
    border-color: #334155 !important;
    color: #E2E8F0 !important;
}

/* BIGGER & CLEARER TEXTAREA */
.stTextArea textarea {
    min-height: 220px !important;
    line-height: 1.7 !important;
    padding: 14px !important;
    font-size: 15px !important;
}

/* Disabled/read-only textarea text */
.stTextArea textarea:disabled,
.stTextArea textarea[disabled] {
    background-color: #0F172A !important;
    color: #E5E7EB !important;
    -webkit-text-fill-color: #E5E7EB !important;
    opacity: 1 !important;
}

/* Placeholder */
.stTextInput input::placeholder,
.stTextArea textarea::placeholder {
    color: #94A3B8 !important;
    -webkit-text-fill-color: #94A3B8 !important;
    opacity: 1 !important;
}

/* Focus effect */
.stTextInput input:focus,
.stNumberInput input:focus,
.stTextArea textarea:focus {
    border: 1px solid #3B82F6 !important;
    box-shadow: 0 0 0 1px #3B82F6 !important;
}

label {
    color: #E2E8F0 !important;
    font-weight: 500 !important;
}

div[data-baseweb="select"] > div {
    background: #111827 !important;
    color: white !important;
    border: 1px solid #334155 !important;
}

[data-testid="stForm"] {
    background: rgba(15,23,42,0.4);
    padding: 16px;
    border-radius: 14px;
    border: 1px solid #1E293B;
}

@media (max-width: 900px) {
    .hero-row {
        align-items: flex-start;
        flex-direction: column;
    }

    .hero-stats {
        width: 100%;
        min-width: 0;
    }
}
</style>
""",
    unsafe_allow_html=True,
)


def fetch_patients():
    try:
        response = requests.get(f"{API_URL}/patients", timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        return response.json(), None
    except requests.RequestException:
        return [], "Backend is not reachable. Check API_URL and confirm the FastAPI service is running."


def fetch_api_status():
    try:
        response = requests.get(f"{API_URL}/health", timeout=10)
        response.raise_for_status()
        return True
    except requests.RequestException:
        return False


patients, api_error = fetch_patients()
api_online = api_error is None and fetch_api_status()


with st.sidebar:
    st.markdown(
        """
    <h1 style='font-size:28px;color:white;margin-bottom:0'>
    🏥 MedAI Assistant
    </h1>
    <p style='color:#94A3B8;margin-top:4px'>
    AI Clinical Intelligence Platform
    </p>
    <hr style='border-color:#1E293B'>
    """,
        unsafe_allow_html=True,
    )

    st.subheader("Add Patient")

    with st.form("add_patient_form", clear_on_submit=True):
        patient_name = st.text_input("Patient Name")
        patient_age = st.number_input(
            "Age",
            min_value=0,
            max_value=120,
            value=None,
            placeholder="Enter age",
        )
        patient_condition = st.text_input("Condition")
        patient_report = st.text_area("Discharge Summary", height=150)
        submitted = st.form_submit_button("Add Patient")

    if submitted and patient_name:
        age_text = patient_age if patient_age is not None else "Not provided"
        report_text = f"""
Age: {age_text}

Condition:
{patient_condition}

Discharge Summary:
{patient_report}
"""

        try:
            response = requests.post(
                f"{API_URL}/patients",
                json={"name": patient_name, "report": report_text},
                timeout=REQUEST_TIMEOUT,
            )
            response.raise_for_status()
            created_patient = response.json()

            st.session_state.current_patient = patient_name
            st.session_state.current_patient_id = created_patient.get("patient_id")
            st.success("Patient added")
            st.rerun()

        except requests.RequestException as e:
            st.error(f"API Error: {e}")

    st.divider()

    if st.button("Load Demo Patient"):
        demo = """
Patient diagnosed with severe hypertension.

Symptoms:
- Chest pain
- Dizziness

Medication:
- Amlodipine
- Losartan
"""

        try:
            response = requests.post(
                f"{API_URL}/patients",
                json={"name": "Muhammad Ali", "report": demo},
                timeout=REQUEST_TIMEOUT,
            )
            response.raise_for_status()
            created_patient = response.json()

            st.session_state.current_patient = "Muhammad Ali"
            st.session_state.current_patient_id = created_patient.get("patient_id")
            st.rerun()

        except requests.RequestException as e:
            st.error(f"API Error: {e}")

    st.divider()
    st.subheader("Patients")

    if patients:
        patient_ids = [p["id"] for p in patients]
        patient_labels = {p["id"]: f"{p['name']} (ID: {p['id']})" for p in patients}

        patient_options = [None] + patient_ids
        selected_index = 0
        if st.session_state.current_patient_id in patient_ids:
            selected_index = patient_options.index(st.session_state.current_patient_id)

        selected_patient_id = st.selectbox(
            "Select Patient",
            patient_options,
            index=selected_index,
            format_func=lambda patient_id: (
                "Select a patient" if patient_id is None else patient_labels[patient_id]
            ),
        )

        if selected_patient_id is None:
            st.session_state.current_patient_id = None
            st.session_state.current_patient = None
        else:
            st.session_state.current_patient_id = selected_patient_id
            st.session_state.current_patient = patient_labels[selected_patient_id]


badge_class = "live-badge" if api_online else "live-badge offline"
badge_text = "System Online" if api_online else "Backend Offline"
high_risk_count = sum(
    1 for patient in patients if patient.get("risk_level", "").upper() == "HIGH"
)
status_label = "Online" if api_online else "Offline"

st.markdown(
    f"""
<div class="hero">
    <div class="hero-row">
        <div>
            <div class="hero-kicker">Clinical command center</div>
            <div class="hero-title">MedAI Assistant</div>
            <div class="hero-sub">AI-powered discharge intelligence for faster patient review</div>
            <div class="{badge_class}">&bull; {badge_text}</div>
        </div>
        <div class="hero-stats">
            <div class="stat-card">
                <div class="stat-value">{len(patients)}</div>
                <div class="stat-label">Patient records</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{high_risk_count}</div>
                <div class="stat-label">High-risk cases</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{status_label}</div>
                <div class="stat-label">API status</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{REQUEST_TIMEOUT}s</div>
                <div class="stat-label">Request timeout</div>
            </div>
        </div>
    </div>
</div>
""",
    unsafe_allow_html=True,
)

if api_error:
    st.warning(api_error)

active_patient = next(
    (p for p in patients if p["id"] == st.session_state.current_patient_id),
    None,
)


if not active_patient:
    st.markdown(
        """
    <div class="empty-box">
    <div style="font-size:64px">🩺</div>
    <div class="empty-title">No Patient Selected</div>
    <div class="empty-sub">Add a patient from the sidebar or load the demo patient.</div>
    </div>
    """,
        unsafe_allow_html=True,
    )

else:
    risk = active_patient.get("risk_level") or "LOW"
    risk_key = risk.lower()
    risk_class = (
        "risk-high"
        if risk_key == "high"
        else "risk-medium"
        if risk_key == "medium"
        else "risk-low"
    )
    safe_patient_name = html.escape(active_patient["name"])

    st.markdown(
        f"""
    <div class="patient-header">
        <div style="display:flex;align-items:center;justify-content:space-between;gap:16px;flex-wrap:wrap">
            <div>
                <div class="patient-name">{safe_patient_name}</div>
                <div class="patient-meta">Patient ID: {active_patient['id']}</div>
            </div>
            <div class="risk-pill {risk_class}">{html.escape(risk.upper())} RISK</div>
        </div>
    </div>
    """,
        unsafe_allow_html=True,
    )

    left, right = st.columns([1.15, 1])

    with left:
        st.markdown(
            """
        <div class="card-title">📄 Discharge Summary</div>
        """,
            unsafe_allow_html=True,
        )

        st.text_area(
            "summary",
            value=active_patient.get("discharge_summary", ""),
            height=420,
            label_visibility="collapsed",
            disabled=True,
        )

    with right:
        st.markdown(
            """
        <div class="card-title">🤖 AI Clinical Instructions</div>
        """,
            unsafe_allow_html=True,
        )

        patient_id = active_patient["id"]

        if st.button("Generate AI Instructions"):
            with st.spinner("Analyzing..."):
                try:
                    response = requests.post(
                        f"{API_URL}/analyze",
                        json={"report": active_patient["discharge_summary"]},
                        timeout=REQUEST_TIMEOUT,
                    )
                    response.raise_for_status()
                    output = response.json().get("ai_output", "No output generated.")
                    st.session_state.ai_output[patient_id] = output

                except requests.RequestException as e:
                    st.error(f"API Error: {e}")

        if patient_id in st.session_state.ai_output:
            safe_output = html.escape(st.session_state.ai_output[patient_id]).replace(
                "\n", "<br>"
            )

            st.markdown(
                f"""
            <div class="ai-box">
            {safe_output}
            </div>
            """,
                unsafe_allow_html=True,
            )

    st.divider()
    st.subheader("💬 AI Medical Assistant")

    patient_id = active_patient["id"]
    chat_key = str(patient_id)

    if chat_key not in st.session_state.chat_memory:
        st.session_state.chat_memory[chat_key] = []

    for turn in st.session_state.chat_memory[chat_key]:
        with st.chat_message("user"):
            st.write(turn["user"])

        with st.chat_message("assistant"):
            st.write(turn["assistant"])

    user_message = st.chat_input("Ask about this patient...")

    if user_message:
        memory_context = get_memory_context(st.session_state.chat_memory[chat_key])

        with st.spinner("Thinking..."):
            try:
                response = requests.post(
                    f"{API_URL}/chat",
                    json={
                        "patient_id": patient_id,
                        "question": user_message,
                        "memory": memory_context,
                    },
                    timeout=REQUEST_TIMEOUT,
                )
                response.raise_for_status()
                answer = response.json().get("answer", "No response generated.")

            except requests.RequestException as e:
                answer = f"API Error: {e}"

        with st.chat_message("user"):
            st.write(user_message)

        with st.chat_message("assistant"):
            st.write(answer)

        update_memory(
            st.session_state.chat_memory[chat_key],
            user_message,
            answer,
        )
