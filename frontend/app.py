import streamlit as st
import requests
import pandas as pd
import time
from io import BytesIO
import plotly.express as px

# ---------------- PAGE CONFIG ----------------
st.set_page_config(page_title="Auto Data Cleaning AI", layout="wide")

# ---------------- CUSTOM CSS ----------------
st.markdown("""
<style>
.stApp {
    background: linear-gradient(135deg, #0f172a, #1e293b);
    color: white;
}
.hero {
    text-align: center;
    padding: 30px;
}
.hero h1 {
    font-size: 50px;
    font-weight: bold;
}
.hero p {
    font-size: 18px;
    color: #94a3b8;
}
.card {
    background: rgba(255,255,255,0.05);
    border-radius: 15px;
    padding: 20px;
    backdrop-filter: blur(12px);
    box-shadow: 0 4px 30px rgba(0,0,0,0.3);
}
.stButton>button {
    background: linear-gradient(90deg, #6366f1, #8b5cf6);
    color: white;
    border-radius: 12px;
    height: 50px;
    font-size: 18px;
}
[data-testid="stMetric"] {
    background: rgba(255,255,255,0.05);
    padding: 15px;
    border-radius: 12px;
}
</style>
""", unsafe_allow_html=True)

# ---------------- HERO ----------------
st.markdown("""
<div class="hero">
    <h1>✨ Auto Data Cleaning AI</h1>
    <p>Upload → Clean → Analyze → Download in Seconds 🚀</p>
</div>
""", unsafe_allow_html=True)

# ---------------- SIDEBAR ----------------
with st.sidebar:
    st.header("⚙️ Control Panel")
    MAX_FILE_SIZE_MB = st.slider("Max File Size (MB)", 10, 100, 50)
    show_charts = st.toggle("Enable Charts", True)

# ---------------- API ----------------
API_URL = "https://automatic-data-cleaning.onrender.com/clean-data/"

# ---------------- FILE UPLOAD ----------------
uploaded_file = st.file_uploader("📂 Upload CSV", type=["csv"])

if uploaded_file:

    # -------- FILE SIZE CHECK --------
    file_size_mb = len(uploaded_file.getvalue()) / (1024 * 1024)
    if file_size_mb > MAX_FILE_SIZE_MB:
        st.error(f"❌ File too large ({file_size_mb:.1f}MB)")
        st.stop()

    df = pd.read_csv(uploaded_file)

    # -------- METRICS --------
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Rows", df.shape[0])
    col2.metric("Columns", df.shape[1])
    col3.metric("Missing", df.isnull().sum().sum())
    col4.metric("Duplicates", df.duplicated().sum())

    # -------- TABS --------
    tab1, tab2, tab3 = st.tabs(["📄 Preview", "📊 Analytics", "⚡ Clean"])

    # -------- PREVIEW --------
    with tab1:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.dataframe(df.head(10), use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # -------- ANALYTICS --------
    with tab2:
        if show_charts:
            st.subheader("📊 Data Visualization")

            numeric_cols = df.select_dtypes(include=['number']).columns

            if len(numeric_cols) > 0:
                col = st.selectbox("Select Column", numeric_cols)
                fig = px.histogram(df, x=col)
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No numeric columns available")

    # -------- CLEAN --------
    with tab3:
        if st.button("🚀 Run AI Cleaning"):

            progress = st.progress(0)
            status = st.empty()

            for i in range(100):
                time.sleep(0.01)
                progress.progress(i + 1)
                status.text(f"Processing {i+1}%")

            try:
                uploaded_file.seek(0)

                # ✅ FIXED REQUEST
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

                # -------- DEBUG --------
                st.write("Status:", response.status_code)
                st.write("Content-Type:", response.headers.get("content-type"))

                # ❌ ERROR HANDLING
                if response.status_code != 200:
                    st.error("❌ Backend Error")
                    st.text(response.text)
                    st.stop()

                content_type = response.headers.get("content-type", "")

                if "application/json" in content_type:
                    st.error("❌ Backend returned JSON error")
                    st.text(response.text)
                    st.stop()

                if "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet" not in content_type:
                    st.error("❌ Invalid response (Not Excel)")
                    st.text(response.text[:300])
                    st.stop()

                # ✅ READ EXCEL
                df_clean = pd.read_excel(BytesIO(response.content), engine="openpyxl")

                st.success("✅ Cleaning Completed!")

                # -------- METRICS --------
                col1, col2, col3 = st.columns(3)
                col1.metric("Rows", df_clean.shape[0])
                col2.metric("Columns", df_clean.shape[1])
                col3.metric("Quality Score", response.headers.get("X-Quality-Score", "N/A"))

                # -------- CLEANED DATA --------
                st.dataframe(df_clean.head(10), use_container_width=True)

                st.download_button(
                    "📥 Download Cleaned Data",
                    response.content,
                    file_name="cleaned.xlsx"
                )

            except requests.exceptions.ConnectionError:
                st.error("❌ Cannot connect to backend")

            except requests.exceptions.Timeout:
                st.error("❌ Request Timeout")

            except Exception as e:
                st.error("❌ Unexpected Error")
                st.text(str(e))

else:
    st.info("👆 Upload your dataset to begin")