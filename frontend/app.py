import streamlit as st
import requests
import pandas as pd
from io import BytesIO
import plotly.express as px

# ---------------- CONFIG ----------------
st.set_page_config(page_title="Auto Data Cleaning AI", layout="wide")

# ---------------- CLEAN PROFESSIONAL CSS ----------------
st.markdown("""
<style>
.stApp {
    background-color: #0b1120;
    color: #e2e8f0;
}

/* Header */
h1 {
    text-align: center;
    font-weight: 700;
    letter-spacing: -1px;
}

/* Metrics */
[data-testid="stMetric"] {
    background-color: #111827;
    padding: 15px;
    border-radius: 10px;
}

/* Buttons */
.stButton>button {
    background-color: #6366f1;
    color: white;
    border-radius: 8px;
    height: 40px;
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background-color: #020617;
}
</style>
""", unsafe_allow_html=True)

# ---------------- HEADER ----------------
st.markdown("""
<h1>Auto Data Cleaning AI</h1>
<p style='text-align:center; color:#94a3b8;'>
Clean, Analyze & Prepare Data in Seconds
</p>
""", unsafe_allow_html=True)

# ---------------- SIDEBAR ----------------
with st.sidebar:
    st.markdown("### 📂 Upload Dataset")
    uploaded_file = st.file_uploader("Upload CSV", type=["csv"])
    run_clean = st.button("🚀 Clean Data", use_container_width=True)

API_URL = "https://automatic-data-cleaning.onrender.com/clean-data/"

# ---------------- MAIN ----------------
if uploaded_file:

    df = pd.read_csv(uploaded_file)

    # -------- KPI SECTION --------
    st.markdown("### 📊 Overview")

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Rows", df.shape[0])
    col2.metric("Columns", df.shape[1])
    col3.metric("Missing Values", df.isnull().sum().sum())
    col4.metric("Duplicates", df.duplicated().sum())

    st.divider()

    # -------- TABS --------
    tab1, tab2, tab3 = st.tabs(["📊 Dashboard", "📄 Data", "🤖 Insights"])

    # -------- DASHBOARD --------
    with tab1:
        st.markdown("### 📊 Data Analytics")

        num_cols = df.select_dtypes(include='number').columns

        if len(num_cols) > 0:
            col = st.selectbox("Select column", num_cols)

            fig = px.histogram(df, x=col)
            fig.update_layout(
                template="plotly_dark",
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)"
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No numeric columns available")

    # -------- DATA TAB --------
    with tab2:
        st.markdown("### 📄 Dataset Preview")
        st.dataframe(df.head(20), use_container_width=True)

    # -------- INSIGHTS TAB --------
    with tab3:
        st.markdown("### 🤖 AI Insights")

        missing = df.isnull().sum().sum()
        duplicates = df.duplicated().sum()

        if missing > 0:
            st.warning(f"Dataset contains {missing} missing values")

        if duplicates > 0:
            st.warning(f"Found {duplicates} duplicate rows")

        if missing == 0 and duplicates == 0:
            st.success("Dataset looks clean")

    st.divider()

    # -------- CLEAN SECTION --------
    st.markdown("### 🚀 Clean Dataset")

    if run_clean:
        try:
            with st.spinner("Processing dataset..."):

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
                    st.error("Backend error")
                    st.text(response.text)
                    st.stop()

                df_clean = pd.read_excel(BytesIO(response.content), engine="openpyxl")

                st.success("Cleaning completed successfully")

                # Metrics after cleaning
                c1, c2, c3 = st.columns(3)
                c1.metric("Rows", df_clean.shape[0])
                c2.metric("Columns", df_clean.shape[1])
                c3.metric("Quality Score", response.headers.get("X-Quality-Score", "N/A"))

                st.markdown("### ✨ Cleaned Dataset")
                st.dataframe(df_clean.head(10), use_container_width=True)

                st.download_button(
                    "⬇ Download Cleaned Data",
                    response.content,
                    file_name="cleaned.xlsx",
                    use_container_width=True
                )

        except Exception as e:
            st.error("Error occurred")
            st.text(str(e))

else:
    st.markdown("### 👈 Upload a dataset to begin")