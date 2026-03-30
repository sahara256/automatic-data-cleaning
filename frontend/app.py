import streamlit as st
import requests
import pandas as pd
import time
import traceback
from io import BytesIO

st.set_page_config(page_title="Auto Data Cleaning AI", layout="wide")

st.title("🚀 Auto Data Cleaning AI - Premium")
st.caption("Upload → Clean → Analyze → Download")

# ✅ API URL (single place)
API_URL = "https://automatic-data-cleaning.onrender.com/clean-data/"
MAX_FILE_SIZE_MB = 50

uploaded_file = st.file_uploader("📂 Upload CSV", type=["csv"])

if uploaded_file:
    # ✅ Validate file size
    file_size_mb = len(uploaded_file.getvalue()) / (1024 * 1024)
    if file_size_mb > MAX_FILE_SIZE_MB:
        st.error(f"❌ File too large ({file_size_mb:.1f}MB). Max: {MAX_FILE_SIZE_MB}MB")
        st.stop()

    df_original = pd.read_csv(uploaded_file)

    st.subheader("📄 Dataset Preview")
    st.dataframe(df_original.head(10))
    
    st.info(f"📊 Original: {df_original.shape[0]} rows × {df_original.shape[1]} columns")

    if st.button("🚀 Run AI Cleaning"):
        progress = st.progress(0)

        for i in range(100):
            time.sleep(0.01)
            progress.progress(i + 1)

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
                timeout=120,
                allow_redirects=True
            )

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
            except Exception as e:
                st.error("❌ Failed to read Excel file from backend")
                st.text(str(e))
                st.stop()

            # ✅ Parse quality score safely
            quality_score = response.headers.get("X-Quality-Score", "N/A")
            try:
                score_val = int(quality_score) if quality_score != "N/A" else 0
            except ValueError:
                score_val = 0

            st.success("✅ Cleaning Completed!")

            col1, col2, col3 = st.columns(3)
            col1.metric("Rows", df_clean.shape[0])
            col2.metric("Columns", df_clean.shape[1])
            col3.metric("Quality Score", f"{score_val}%")

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

        except requests.exceptions.Timeout:
            st.error("❌ Request Timeout - Backend took too long to respond")

        except Exception as e:
            st.error("❌ Failed to clean data")
            st.text(traceback.format_exc())

else:
    st.info("👆 Upload a dataset to begin")