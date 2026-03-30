import streamlit as st
import requests
import pandas as pd
import time
import traceback
from io import BytesIO

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="Auto Data Cleaning AI",
    layout="wide",
    page_icon="✨"
)

# ---------------- CUSTOM CSS ----------------
st.markdown("""
<style>
/* Background */
body {
    background: linear-gradient(135deg, #0f172a, #1e293b);
    color: white;
}

/* Cards */
.card {
    padding: 20px;
    border-radius: 15px;
    background: rgba(255,255,255,0.05);
    backdrop-filter: blur(10px);
    box-shadow: 0 4px 30px rgba(0,0,0,0.3);
}

/* Title */
.title {
    font-size: 40px;
    font-weight: bold;
    text-align: center;
}

/* Buttons */
.stButton>button {
    background: linear-gradient(90deg, #6366f1, #8b5cf6);
    color: white;
    border-radius: 10px;
    padding: 10px 20px;
}

/* Metrics */
[data-testid="stMetric"] {
    background: rgba(255,255,255,0.05);
    padding: 15px;
    border-radius: 10px;
}

/* File uploader */
[data-testid="stFileUploader"] {
    background: rgba(255,255,255,0.05);
    border-radius: 10px;
    padding: 10px;
}
</style>
""", unsafe_allow_html=True)

# ---------------- HEADER ----------------
st.markdown('<div class="title">✨ Auto Data Cleaning AI</div>', unsafe_allow_html=True)
st.caption("Upload → Clean → Analyze → Download")

# ---------------- SIDEBAR ----------------
with st.sidebar:
    st.header("⚙️ Settings")
    MAX_FILE_SIZE_MB = st.slider("Max File Size (MB)", 10, 100, 50)
    show_preview = st.toggle("Show Preview", True)
    show_insights = st.toggle("Show Insights", True)

# ---------------- API ----------------
API_URL = "https://automatic-data-cleaning.onrender.com/clean-data/"

# ---------------- FILE UPLOAD ----------------
uploaded_file = st.file_uploader("📂 Upload CSV File", type=["csv"])

if uploaded_file:
    file_size_mb = len(uploaded_file.getvalue()) / (1024 * 1024)

    if file_size_mb > MAX_FILE_SIZE_MB:
        st.error(f"❌ File too large ({file_size_mb:.1f}MB)")
        st.stop()

    df_original = pd.read_csv(uploaded_file)

    # ---------------- TABS ----------------
    tab1, tab2, tab3 = st.tabs(["📄 Preview", "📊 Insights", "⬇️ Download"])

    # -------- PREVIEW --------
    with tab1:
        if show_preview:
            st.subheader("Dataset Preview")
            st.dataframe(df_original.head(10), use_container_width=True)

            st.info(f"Rows: {df_original.shape[0]} | Columns: {df_original.shape[1]}")

    # -------- INSIGHTS --------
    with tab2:
        if show_insights:
            st.subheader("Quick Insights")

            col1, col2, col3 = st.columns(3)
            col1.metric("Missing Values", df_original.isnull().sum().sum())
            col2.metric("Duplicate Rows", df_original.duplicated().sum())
            col3.metric("Columns", df_original.shape[1])

            st.write("Column Data Types")
            st.dataframe(df_original.dtypes)

    # -------- CLEAN BUTTON --------
    if st.button("🚀 Run AI Cleaning"):
        progress = st.progress(0)
        status = st.empty()

        for i in range(100):
            time.sleep(0.01)
            progress.progress(i + 1)
            status.text(f"Processing... {i+1}%")

        try:
            uploaded_file.seek(0)

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
                st.error("❌ Backend Error")
                st.text(response.text)
                st.stop()

            df_clean = pd.read_excel(BytesIO(response.content), engine="openpyxl")

            quality_score = response.headers.get("X-Quality-Score", "0")
            score_val = int(quality_score) if quality_score.isdigit() else 0

            st.success("✅ Cleaning Completed!")

            # -------- METRICS --------
            col1, col2, col3 = st.columns(3)
            col1.metric("Rows", df_clean.shape[0])
            col2.metric("Columns", df_clean.shape[1])
            col3.metric("Quality Score", f"{score_val}%")

            # -------- CLEANED DATA --------
            with tab3:
                st.subheader("Cleaned Dataset")
                st.dataframe(df_clean.head(10), use_container_width=True)

                st.download_button(
                    "📥 Download Cleaned Dataset",
                    response.content,
                    file_name="cleaned_data.xlsx"
                )

        except requests.exceptions.ConnectionError:
            st.error("❌ Cannot connect to backend")

        except requests.exceptions.Timeout:
            st.error("❌ Request Timeout")

        except Exception:
            st.error("❌ Failed to clean data")
            st.text(traceback.format_exc())

else:
    st.info("👆 Upload a dataset to begin")