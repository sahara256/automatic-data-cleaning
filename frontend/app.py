import streamlit as st
import requests
import pandas as pd
from io import BytesIO
import time

# ---------------- CONFIG ----------------
st.set_page_config(page_title="Auto Data Cleaning AI", layout="centered")

API_URL = "https://automatic-data-cleaning.onrender.com/clean-data/"

# ---------------- FUNCTIONS ----------------
def call_backend(file):
    file.seek(0)
    return requests.post(
        API_URL,
        files={"file": (file.name, file.getvalue(), "text/csv")},
        timeout=120
    )

def parse_cleaned_data(response):
    return pd.read_excel(BytesIO(response.content), engine="openpyxl")


# ---------------- STYLE + ANIMATIONS ----------------
st.markdown("""
<style>

/* BACKGROUND */
.stApp {
    background: radial-gradient(circle at top, #0f172a, #020617);
    color: white;
    text-align: center;
}

/* TITLE */
.title {
    font-size: 48px;
    font-weight: 800;
    background: linear-gradient(90deg, #38bdf8, #6366f1);
    -webkit-background-clip: text;
    color: transparent;
}

/* SUBTITLE */
.subtitle {
    color: #94a3b8;
    margin-bottom: 25px;
}

/* ANIMATION ICON */
.clean-animation {
    font-size: 70px;
    animation: bounce 2s infinite;
}

/* CLEANING DOTS */
.loading-dots::after {
    content: '';
    animation: dots 1.5s steps(4, end) infinite;
}
@keyframes dots {
    0% {content: '';}
    25% {content: '.';}
    50% {content: '..';}
    75% {content: '...';}
}

/* BOUNCE */
@keyframes bounce {
    0%,100% {transform: translateY(0);}
    50% {transform: translateY(-15px);}
}

/* CARD */
.card {
    padding: 20px;
    border-radius: 15px;
    background: rgba(255,255,255,0.05);
    border: 1px solid rgba(255,255,255,0.1);
    margin-top: 15px;
}

/* BUTTON */
.stButton>button {
    width: 100%;
    background: linear-gradient(90deg, #6366f1, #3b82f6);
    color: white;
    border-radius: 10px;
    height: 45px;
}

/* PROGRESS BAR */
.progress-bar {
    height: 10px;
    border-radius: 10px;
    background: linear-gradient(90deg, #6366f1, #3b82f6);
    animation: progressAnim 3s linear forwards;
}

@keyframes progressAnim {
    from {width: 0%;}
    to {width: 100%;}
}

</style>
""", unsafe_allow_html=True)

# ---------------- UI ----------------

# TITLE
st.markdown('<div class="title">🚀 Auto Data Cleaning AI</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Clean • Analyze • Transform instantly</div>', unsafe_allow_html=True)

# 🎬 ANIMATION (PURE CSS)
st.markdown('<div class="clean-animation">🧹</div>', unsafe_allow_html=True)

# UPLOAD
st.markdown("### 📂 Upload CSV")
uploaded_file = st.file_uploader("Choose CSV file", type=["csv"])

# BUTTON
run_clean = st.button("🚀 Clean Data")

# ---------------- PROCESS ----------------
if uploaded_file and run_clean:

    # 🔄 FAKE PROGRESS UI
    st.markdown("### ⚡ Processing")
    st.markdown('<div class="progress-bar"></div>', unsafe_allow_html=True)

    status = st.empty()

    steps = [
        "Uploading file",
        "Analyzing data",
        "Cleaning missing values",
        "Removing duplicates",
        "Finalizing"
    ]

    for step in steps:
        status.markdown(f"**{step}** <span class='loading-dots'></span>", unsafe_allow_html=True)
        time.sleep(0.7)

    # CALL BACKEND
    response = call_backend(uploaded_file)

    if response and response.status_code == 200:

        df_clean = parse_cleaned_data(response)

        if df_clean is not None:

            st.success("✅ Cleaning Completed")

            # 🔥 BEFORE vs AFTER
            st.markdown("## 🔄 Before vs After")

            col1, col2 = st.columns(2)

            with col1:
                st.markdown("### 📄 Original")
                df_original = pd.read_csv(uploaded_file)
                st.dataframe(df_original.head(10), use_container_width=True)

            with col2:
                st.markdown("### ✨ Cleaned")
                st.dataframe(df_clean.head(10), use_container_width=True)

            st.divider()

            # FINAL DATA
            st.markdown("## 📊 Cleaned Dataset")
            st.dataframe(df_clean, use_container_width=True)

            # DOWNLOAD
            st.download_button(
                "⬇ Download Cleaned Data",
                response.content,
                file_name="cleaned.xlsx"
            )

        else:
            st.error("Invalid response")

    else:
        st.error("Backend failed")