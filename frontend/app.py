import streamlit as st
import requests
import pandas as pd
from io import BytesIO
import plotly.express as px

# ---------------- CONFIG ----------------
st.set_page_config(page_title="Auto Data Cleaning AI", layout="wide")

API_URL = "https://automatic-data-cleaning.onrender.com/clean-data/"

# ---------------- UTILITY FUNCTIONS ----------------
def safe_read_csv(file):
    try:
        return pd.read_csv(file)
    except Exception as e:
        st.error("❌ Failed to read CSV file")
        st.text(str(e))
        return None


def compute_metrics(df):
    return {
        "rows": df.shape[0],
        "cols": df.shape[1],
        "missing": int(df.isnull().sum().sum()),
        "duplicates": int(df.duplicated().sum())
    }


def call_backend(file):
    try:
        file.seek(0)
        response = requests.post(
            API_URL,
            files={
                "file": (
                    file.name,
                    file.getvalue(),
                    "text/csv"
                )
            },
            timeout=120
        )
        return response
    except requests.exceptions.ConnectionError:
        st.error("❌ Cannot connect to backend")
    except requests.exceptions.Timeout:
        st.error("❌ Backend timeout")
    return None


def parse_cleaned_data(response):
    try:
        return pd.read_excel(BytesIO(response.content), engine="openpyxl")
    except Exception:
        st.error("❌ Invalid Excel response from backend")
        return None


# ---------------- CSS (UNCHANGED FROM YOUR DESIGN) ----------------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
* { font-family: 'Inter', sans-serif; }

.stApp {
    background: linear-gradient(180deg, #0a0f1f, #0d1526);
    color: #e2e8f0;
}

section[data-testid="stSidebar"] {
    background-color: #0a1020 !important;
    border-right: 1px solid #1e2d4a;
}

.main-header {
    text-align: center;
    padding: 40px 0 30px;
}
.main-header h1 {
    font-size: 40px;
    font-weight: 800;
}
.main-header p {
    color: #64748b;
    font-size: 16px;
}

.kpi-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 18px;
    margin-bottom: 32px;
}
.kpi-card {
    background: linear-gradient(180deg, #111e35, #0f1a2e);
    border: 1px solid #1e2d4a;
    border-radius: 14px;
    padding: 20px;
    display: flex;
    gap: 12px;
}
.kpi-card:hover {
    transform: translateY(-3px);
    box-shadow: 0 8px 30px rgba(0,0,0,0.4);
}

.clean-card {
    background: #111e35;
    border: 1px solid #1e2d4a;
    border-radius: 16px;
    padding: 28px;
    margin-top: 16px;
}
</style>
""", unsafe_allow_html=True)

# ---------------- SIDEBAR ----------------
with st.sidebar:
    st.header("📂 Upload Dataset")
    uploaded_file = st.file_uploader("Upload CSV", type=["csv"])
    run_clean = st.button("🚀 Clean Data", use_container_width=True)

# ---------------- HEADER ----------------
st.markdown("""
<div class="main-header">
<h1>Auto Data Cleaning AI</h1>
<p>Clean, Analyze & Prepare Data in Seconds</p>
</div>
""", unsafe_allow_html=True)

# ---------------- MAIN ----------------
if uploaded_file:

    df = safe_read_csv(uploaded_file)
    if df is None:
        st.stop()

    metrics = compute_metrics(df)

    # -------- KPI --------
    st.markdown("### 📊 Overview")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Rows", f"{metrics['rows']:,}")
    col2.metric("Columns", metrics["cols"])
    col3.metric("Missing", f"{metrics['missing']:,}")
    col4.metric("Duplicates", metrics["duplicates"])

    st.divider()

    # -------- TABS --------
    tab1, tab2, tab3 = st.tabs(["📊 Dashboard", "📄 Data", "🤖 Insights"])

    # DASHBOARD
    with tab1:
        st.markdown("### 📊 Analytics")

        num_cols = df.select_dtypes(include="number").columns.tolist()

        if num_cols:
            col = st.selectbox("Select column", num_cols)
            fig = px.histogram(df, x=col)
            fig.update_layout(template="plotly_dark")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("No numeric columns available")

    # DATA
    with tab2:
        st.dataframe(df.head(20), use_container_width=True)

    # INSIGHTS
    with tab3:
        if metrics["missing"] > 0:
            st.warning(f"{metrics['missing']} missing values detected")
        if metrics["duplicates"] > 0:
            st.warning(f"{metrics['duplicates']} duplicate rows found")
        if metrics["missing"] == 0 and metrics["duplicates"] == 0:
            st.success("Dataset looks clean")

    st.divider()

    # -------- CLEAN --------
    st.markdown('<div class="clean-card">', unsafe_allow_html=True)
    st.markdown("### 🚀 Clean Dataset")

    if run_clean:
        try:
            with st.spinner("Processing..."):

                response = call_backend(uploaded_file)

                if response is None:
                    st.stop()

                if response.status_code != 200:
                    st.error("Backend error")
                    st.text(response.text)
                    st.stop()

                df_clean = parse_cleaned_data(response)
                if df_clean is None:
                    st.stop()

                st.success("Cleaning completed")

                clean_metrics = compute_metrics(df_clean)

                c1, c2, c3 = st.columns(3)
                c1.metric("Rows", f"{clean_metrics['rows']:,}")
                c2.metric("Columns", clean_metrics["cols"])
                c3.metric("Quality Score", response.headers.get("X-Quality-Score", "N/A"))

                st.dataframe(df_clean.head(10), use_container_width=True)

                st.download_button(
                    "Download Cleaned Data",
                    response.content,
                    file_name="cleaned.xlsx",
                    use_container_width=True
                )

        except Exception as e:
            st.error("Unexpected error")
            st.text(str(e))

    st.markdown("</div>", unsafe_allow_html=True)

else:
    st.info("Upload a dataset to begin")
    