import streamlit as st
import requests
import pandas as pd
from io import BytesIO
import plotly.express as px
from streamlit_lottie import st_lottie

# ---------------- CONFIG ----------------
st.set_page_config(page_title="Auto Data Cleaning AI", layout="wide")

# ---------------- LOTTIE ----------------
def load_lottie(url):
    return requests.get(url).json()

lottie_loading = load_lottie("https://assets10.lottiefiles.com/packages/lf20_usmfx6bp.json")
lottie_empty = load_lottie("https://assets2.lottiefiles.com/packages/lf20_qp1q7mct.json")

# ---------------- PREMIUM CSS ----------------
st.markdown("""
<style>

/* BACKGROUND */
.stApp {
    background: radial-gradient(circle at top, #0f172a, #020617);
    color: #e2e8f0;
    font-family: 'Inter', sans-serif;
}

/* HERO */
.hero {
    text-align: center;
    padding: 40px 20px;
}
.hero h1 {
    font-size: 52px;
    font-weight: 800;
    background: linear-gradient(90deg, #00f5ff, #6366f1, #a855f7);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}
.hero p {
    color: #94a3b8;
    font-size: 18px;
}

/* CARD */
.card {
    background: linear-gradient(145deg, rgba(255,255,255,0.05), rgba(255,255,255,0.02));
    border-radius: 18px;
    padding: 20px;
    backdrop-filter: blur(16px);
    border: 1px solid rgba(255,255,255,0.08);
    box-shadow: 0 10px 40px rgba(0,0,0,0.5);
    transition: 0.3s ease;
}
.card:hover {
    transform: translateY(-6px);
    box-shadow: 0 20px 60px rgba(99,102,241,0.3);
}

/* METRICS */
[data-testid="stMetric"] {
    background: linear-gradient(145deg, rgba(99,102,241,0.15), rgba(168,85,247,0.08));
    padding: 15px;
    border-radius: 14px;
}

/* BUTTON */
.stButton>button {
    background: linear-gradient(90deg, #00f5ff, #6366f1, #a855f7);
    color: white;
    border-radius: 12px;
    height: 48px;
    font-size: 16px;
    border: none;
}
.stButton>button:hover {
    transform: scale(1.05);
    box-shadow: 0 0 20px rgba(99,102,241,0.6);
}

/* DOWNLOAD BUTTON */
.stDownloadButton>button {
    background: linear-gradient(90deg, #22c55e, #10b981);
    border-radius: 12px;
}

/* FILE UPLOADER */
[data-testid="stFileUploader"] {
    border: 2px dashed #6366f1;
    border-radius: 14px;
    padding: 15px;
    background: rgba(255,255,255,0.02);
}

/* TABS */
.stTabs [data-baseweb="tab"] {
    font-size: 16px;
    font-weight: 600;
    color: #94a3b8;
}
.stTabs [aria-selected="true"] {
    color: #00f5ff !important;
    border-bottom: 3px solid #6366f1;
}

/* SIDEBAR */
section[data-testid="stSidebar"] {
    background: #020617;
}

/* CHAT STYLE */
[data-testid="stChatMessage"] {
    background: rgba(99,102,241,0.08);
    border-radius: 12px;
    padding: 10px;
    margin-bottom: 8px;
}

</style>
""", unsafe_allow_html=True)

# ---------------- HEADER ----------------
st.markdown("""
<div class="hero">
<h1>✨ Auto Data Cleaning AI</h1>
<p>Upload → Analyze → Clean → Download</p>
</div>
""", unsafe_allow_html=True)

# ---------------- SIDEBAR ----------------
with st.sidebar:
    st.header("⚙️ Controls")
    uploaded_file = st.file_uploader("Upload CSV", type=["csv"])
    run_clean = st.button("🚀 Run Cleaning")

API_URL = "https://automatic-data-cleaning.onrender.com/clean-data/"

# ---------------- EMPTY STATE ----------------
if not uploaded_file:
    st_lottie(lottie_empty, height=250)
    st.info("Upload a dataset to begin")
    st.stop()

# ---------------- LOAD DATA ----------------
df = pd.read_csv(uploaded_file)

# ---------------- METRICS ----------------
st.subheader("📊 Dataset Overview")
c1, c2, c3, c4 = st.columns(4)
c1.metric("Rows", df.shape[0])
c2.metric("Columns", df.shape[1])
c3.metric("Missing", df.isnull().sum().sum())
c4.metric("Duplicates", df.duplicated().sum())

# ---------------- PREVIEW ----------------
st.subheader("📄 Preview")
st.dataframe(df.head(10), use_container_width=True)

# ---------------- DASHBOARD ----------------
st.subheader("📊 Analytics Dashboard")

numeric_cols = df.select_dtypes(include='number').columns

col1, col2 = st.columns(2)

with col1:
    if len(numeric_cols) > 0:
        fig = px.histogram(df, x=numeric_cols[0], title="Distribution")
        fig.update_layout(template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig, use_container_width=True)

with col2:
    missing = df.isnull().sum()
    fig2 = px.bar(x=missing.index, y=missing.values, title="Missing Values")
    fig2.update_layout(template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)")
    st.plotly_chart(fig2, use_container_width=True)

if len(numeric_cols) > 1:
    corr = df[numeric_cols].corr()
    fig3 = px.imshow(corr, text_auto=True, title="Correlation Heatmap")
    fig3.update_layout(template="plotly_dark")
    st.plotly_chart(fig3, use_container_width=True)

# ---------------- AI INSIGHTS ----------------
st.subheader("🤖 AI Insights")

insights = []
missing_total = df.isnull().sum().sum()
duplicates = df.duplicated().sum()

if missing_total > 0:
    insights.append(f"⚠️ Dataset contains {missing_total} missing values")

if duplicates > 0:
    insights.append(f"⚠️ Found {duplicates} duplicate rows")

if len(df.columns) > 10:
    insights.append("📊 Large dataset — consider feature selection")

if insights:
    for msg in insights:
        st.chat_message("assistant").write(msg)
else:
    st.chat_message("assistant").write("✅ Dataset looks clean!")

# ---------------- CLEAN ----------------
if run_clean:
    try:
        uploaded_file.seek(0)

        st_lottie(lottie_loading, height=200)
        st.info("AI is cleaning your data...")

        response = requests.post(
            API_URL,
            files={
                "file": (
                    uploaded_file.name,
                    uploaded_file.getvalue(),
                    "text/csv"
                )
            },
            timeout=120
        )

        if response.status_code != 200:
            st.error("Backend error")
            st.text(response.text)
            st.stop()

        df_clean = pd.read_excel(BytesIO(response.content), engine="openpyxl")

        st.success("✅ Cleaning Completed")

        c1, c2, c3 = st.columns(3)
        c1.metric("Rows", df_clean.shape[0])
        c2.metric("Columns", df_clean.shape[1])
        c3.metric("Quality Score", response.headers.get("X-Quality-Score", "N/A"))

        st.subheader("✨ Cleaned Data")
        st.dataframe(df_clean.head(10), use_container_width=True)

        st.download_button(
            "📥 Download Cleaned File",
            response.content,
            file_name="cleaned.xlsx"
        )

    except Exception as e:
        st.error("Error occurred")
        st.text(str(e))