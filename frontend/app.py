import streamlit as st
import requests
import pandas as pd
import time
from io import BytesIO

st.set_page_config(page_title="Auto Data Cleaning AI", layout="wide")

st.title("🚀 Auto Data Cleaning AI - Premium")
st.caption("Upload → Clean → Analyze → Download")

uploaded_file = st.file_uploader("📂 Upload CSV", type=["csv"])

if uploaded_file:

    df_original = pd.read_csv(uploaded_file)

    st.subheader("📄 Dataset Preview")
    st.dataframe(df_original.head(10))

    if st.button("🚀 Run AI Cleaning"):

        progress = st.progress(0)

        for i in range(100):
            time.sleep(0.01)
            progress.progress(i + 1)

        try:
            uploaded_file.seek(0)

            response = requests.post(
                "http://127.0.0.1:8000/clean-data/",
                files={
                    "file": (
                        uploaded_file.name,
                        uploaded_file.getvalue(),
                        "text/csv"
                    )
                }
            )

            st.write("Status:", response.status_code)
            st.write("Size:", len(response.content))

            # ❌ If backend error
            if response.status_code != 200:
                st.error("❌ Backend Error")
                st.text(response.text)
                st.stop()

            # ❌ If backend returned JSON instead of file
            if "application/json" in response.headers.get("content-type", ""):
                st.error("❌ Backend returned error JSON")
                st.text(response.text)
                st.stop()

            # ✅ Read Excel
            df_clean = pd.read_excel(BytesIO(response.content), engine="openpyxl")

            quality_score = response.headers.get("X-Quality-Score", "N/A")

            st.success("✅ Cleaning Completed!")

            # Metrics
            col1, col2, col3 = st.columns(3)
            col1.metric("Rows", df_clean.shape[0])
            col2.metric("Columns", df_clean.shape[1])
            col3.metric("Quality Score", f"{quality_score}%")

            st.subheader("✨ Cleaned Data")
            st.dataframe(df_clean.head(10))

            # Download
            st.download_button(
                "📥 Download Cleaned Dataset",
                response.content,
                file_name="cleaned_data.xlsx"
            )

        except Exception as e:
            import traceback
            st.error("❌ Failed to clean data")
            st.text(traceback.format_exc())

else:
    st.info("👆 Upload a dataset to begin")