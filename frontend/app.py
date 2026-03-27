import streamlit as st
import requests
import pandas as pd
import time
from io import BytesIO

st.set_page_config(page_title="Auto Data Cleaning AI", layout="wide")

st.title("🚀 Auto Data Cleaning AI - Premium")
st.caption("Upload → Clean → Analyze → Download")

# ✅ API URL (single place)
API_URL = "https://data-cleaning-api-blsg.onrender.com/clean-data/"

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

            # 🔥 DEBUG: Show URL used
            st.write("🔗 API URL:", API_URL)

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

            # 🔥 DEBUG INFO
            st.write("Status:", response.status_code)
            st.write("Response Size:", len(response.content))

            # ❌ Handle 404 specifically
            if response.status_code == 404:
                st.error("❌ API Endpoint Not Found (404)")
                st.write("👉 Check if backend URL or route is correct")
                st.stop()

            # ❌ Handle other errors
            if response.status_code != 200:
                st.error("❌ Backend Error")
                st.text(response.text)
                st.stop()

            # ❌ If backend returned JSON error
            if "application/json" in response.headers.get("content-type", ""):
                st.error("❌ Backend returned error JSON")
                st.text(response.text)
                st.stop()

            # ✅ Read Excel safely
            try:
                df_clean = pd.read_excel(BytesIO(response.content), engine="openpyxl")
            except Exception:
                st.error("❌ Failed to read Excel file from backend")
                st.stop()

            quality_score = response.headers.get("X-Quality-Score", "N/A")

            st.success("✅ Cleaning Completed!")

            col1, col2, col3 = st.columns(3)
            col1.metric("Rows", df_clean.shape[0])
            col2.metric("Columns", df_clean.shape[1])
            col3.metric("Quality Score", f"{quality_score}%")

            st.subheader("✨ Cleaned Data")
            st.dataframe(df_clean.head(10))

            st.download_button(
                "📥 Download Cleaned Dataset",
                response.content,
                file_name="cleaned_data.xlsx"
            )

        except requests.exceptions.ConnectionError:
            st.error("❌ Cannot connect to backend API")
            st.write("👉 Check if backend is running or URL is correct")

        except Exception:
            import traceback
            st.error("❌ Failed to clean data")
            st.text(traceback.format_exc())

else:
    st.info("👆 Upload a dataset to begin")