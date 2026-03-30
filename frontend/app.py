import streamlit as st
import requests
import pandas as pd
from io import BytesIO
import plotly.express as px

# ---------------- CONFIG ----------------
st.set_page_config(page_title="Auto Data Cleaning AI", layout="wide")

# ---------------- CSS MATCHING THE IMAGE ----------------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

* { font-family: 'Inter', sans-serif; }

/* ── App background ── */
.stApp {
    background-color: #0d1526;
    color: #e2e8f0;
}

/* ── Sidebar ── */
section[data-testid="stSidebar"] {
    background-color: #0a1020 !important;
    border-right: 1px solid #1e2d4a;
    padding-top: 0 !important;
}
section[data-testid="stSidebar"] > div { padding: 0 !important; }

/* Sidebar inner wrapper */
.sidebar-inner {
    padding: 24px 16px;
}

/* Sidebar section headers */
.sidebar-label {
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 0.12em;
    color: #64748b;
    text-transform: uppercase;
    margin-bottom: 12px;
    margin-top: 24px;
}

/* Upload box */
.upload-box {
    border: 1.5px dashed #2a3f6a;
    border-radius: 12px;
    padding: 20px 16px;
    text-align: center;
    background-color: #0f1e36;
    margin-bottom: 16px;
}
.upload-box .upload-title {
    font-weight: 600;
    font-size: 13px;
    color: #cbd5e1;
    margin-bottom: 4px;
}
.upload-box .upload-sub {
    font-size: 11px;
    color: #475569;
    margin-bottom: 12px;
}
.browse-btn {
    background: #1e2d4a;
    color: #94a3b8;
    border: 1px solid #2a3f6a;
    border-radius: 6px;
    padding: 6px 16px;
    font-size: 12px;
    cursor: pointer;
}

/* Clean Data button */
.stButton > button {
    background: linear-gradient(135deg, #2563eb, #3b82f6) !important;
    color: white !important;
    border: none !important;
    border-radius: 10px !important;
    font-weight: 600 !important;
    font-size: 14px !important;
    height: 44px !important;
    width: 100% !important;
    letter-spacing: 0.02em !important;
    transition: opacity 0.2s !important;
}
.stButton > button:hover { opacity: 0.88 !important; }

/* ── Main header ── */
.main-header {
    text-align: center;
    padding: 32px 0 24px;
}
.main-header .sparkle {
    font-size: 36px;
    margin-bottom: 4px;
}
.main-header h1 {
    font-size: 36px;
    font-weight: 800;
    color: #f1f5f9;
    margin: 0;
    letter-spacing: -0.5px;
}
.main-header h1 span {
    color: #60a5fa;
}
.main-header p {
    color: #64748b;
    font-size: 15px;
    margin-top: 6px;
}

/* ── KPI cards ── */
.kpi-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 14px;
    margin-bottom: 28px;
}
.kpi-card {
    background: #111e35;
    border: 1px solid #1e2d4a;
    border-radius: 14px;
    padding: 20px 22px;
    display: flex;
    align-items: center;
    gap: 14px;
}
.kpi-icon {
    width: 40px;
    height: 40px;
    border-radius: 10px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 18px;
    flex-shrink: 0;
}
.kpi-icon.blue  { background: #1e3a5f; }
.kpi-icon.grid  { background: #1a3050; }
.kpi-icon.warn  { background: #2d2010; }
.kpi-icon.purple{ background: #1e1a40; }
.kpi-label {
    font-size: 12px;
    color: #64748b;
    font-weight: 500;
    margin-bottom: 2px;
}
.kpi-value {
    font-size: 26px;
    font-weight: 800;
    color: #f1f5f9;
    line-height: 1;
}

/* ── Tabs ── */
.stTabs [data-baseweb="tab-list"] {
    background: transparent;
    border-bottom: 1px solid #1e2d4a;
    gap: 8px;
}
.stTabs [data-baseweb="tab"] {
    background: transparent;
    color: #64748b;
    font-weight: 500;
    font-size: 14px;
    border-radius: 0;
    padding: 8px 20px;
}
.stTabs [aria-selected="true"] {
    color: #f1f5f9 !important;
    border-bottom: 2px solid #3b82f6 !important;
    background: transparent !important;
}

/* ── Section titles ── */
.section-title {
    font-size: 16px;
    font-weight: 700;
    color: #e2e8f0;
    margin-bottom: 16px;
    margin-top: 8px;
}

/* ── Selectbox ── */
.stSelectbox > div > div {
    background-color: #111e35 !important;
    border: 1px solid #1e2d4a !important;
    border-radius: 8px !important;
    color: #94a3b8 !important;
}

/* ── Dataframe ── */
.stDataFrame { border-radius: 10px; overflow: hidden; }

/* ── Download button ── */
.stDownloadButton > button {
    background: linear-gradient(135deg, #1d4ed8, #2563eb) !important;
    color: white !important;
    border: none !important;
    border-radius: 10px !important;
    font-weight: 600 !important;
    font-size: 14px !important;
    height: 44px !important;
    width: 100% !important;
}

/* ── Divider ── */
hr { border-color: #1e2d4a !important; }

/* ── Metrics override ── */
[data-testid="stMetric"] {
    background: #111e35;
    border: 1px solid #1e2d4a;
    border-radius: 12px;
    padding: 16px !important;
}
[data-testid="stMetricLabel"] { color: #64748b !important; font-size: 12px !important; }
[data-testid="stMetricValue"] { color: #f1f5f9 !important; font-weight: 800 !important; }

/* File uploader */
[data-testid="stFileUploader"] {
    background: #0f1e36;
    border: 1.5px dashed #2a3f6a;
    border-radius: 12px;
    padding: 8px;
}

/* Checkbox */
.stCheckbox span { color: #94a3b8 !important; font-size: 14px !important; }

/* Warning / success */
.stAlert { border-radius: 10px !important; }

/* Clean section card */
.clean-card {
    background: #111e35;
    border: 1px solid #1e2d4a;
    border-radius: 16px;
    padding: 24px;
    margin-top: 8px;
}
.clean-card-title {
    font-size: 18px;
    font-weight: 700;
    color: #e2e8f0;
    margin-bottom: 16px;
    display: flex;
    align-items: center;
    gap: 8px;
}
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown('<div class="sidebar-inner">', unsafe_allow_html=True)

    st.markdown('<div class="sidebar-label">📂 Upload Dataset</div>', unsafe_allow_html=True)
    uploaded_file = st.file_uploader("Upload CSV", type=["csv"], label_visibility="collapsed")

    run_clean = st.button("🚀  Clean Data", use_container_width=True)

    st.markdown('<div class="sidebar-label">⚙️ Controls</div>', unsafe_allow_html=True)

    remove_dups  = st.checkbox("Remove Duplicates", value=True)
    fill_missing = st.checkbox("Fill Missing Values", value=False)

    filter_option = st.selectbox("Filter", ["None", "Top 100 rows", "Non-null only", "Numeric only"],
                                 label_visibility="collapsed")

    st.markdown('</div>', unsafe_allow_html=True)

API_URL = "https://automatic-data-cleaning.onrender.com/clean-data/"

# ─────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────

# Header
st.markdown("""
<div class="main-header">
    <div class="sparkle">✦</div>
    <h1>Auto Data <span>Cleaning AI</span></h1>
    <p>Clean, Analyze &amp; Prepare Data in Seconds</p>
</div>
""", unsafe_allow_html=True)

if uploaded_file:
    df = pd.read_csv(uploaded_file)

    rows      = df.shape[0]
    cols      = df.shape[1]
    missing   = int(df.isnull().sum().sum())
    dups      = int(df.duplicated().sum())

    # ── KPI Cards ──
    st.markdown(f"""
    <div class="kpi-grid">
        <div class="kpi-card">
            <div class="kpi-icon blue">≡</div>
            <div>
                <div class="kpi-label">Rows</div>
                <div class="kpi-value">{rows:,}</div>
            </div>
        </div>
        <div class="kpi-card">
            <div class="kpi-icon grid">⊞</div>
            <div>
                <div class="kpi-label">Columns</div>
                <div class="kpi-value">{cols}</div>
            </div>
        </div>
        <div class="kpi-card">
            <div class="kpi-icon warn">⚠</div>
            <div>
                <div class="kpi-label">Missing Values</div>
                <div class="kpi-value">{missing:,}</div>
            </div>
        </div>
        <div class="kpi-card">
            <div class="kpi-icon purple">⊞</div>
            <div>
                <div class="kpi-label">Duplicates</div>
                <div class="kpi-value">{dups:,}</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Tabs ──
    tab1, tab2, tab3 = st.tabs(["📊 Dashboard", "📄 Data", "🤖 Insights"])

    # ── DASHBOARD TAB ──
    with tab1:
        st.markdown('<div class="section-title">Data Analytics</div>', unsafe_allow_html=True)

        num_cols = df.select_dtypes(include="number").columns.tolist()

        if num_cols:
            left_col, right_col = st.columns([1, 1.4])

            with left_col:
                selected_col = st.selectbox("Select column", num_cols, key="col_select")
                st.dataframe(
                    df[[selected_col] + [c for c in df.columns if c != selected_col][:3]].head(8),
                    use_container_width=True,
                    height=260
                )

            with right_col:
                fig = px.histogram(
                    df, x=selected_col,
                    title=f"{selected_col} Distribution",
                    color_discrete_sequence=["#3b82f6"]
                )
                fig.update_layout(
                    template="plotly_dark",
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",
                    title_font=dict(size=14, color="#94a3b8"),
                    margin=dict(l=10, r=10, t=40, b=10),
                    font_color="#94a3b8",
                    bargap=0.05,
                )
                fig.update_traces(marker_line_width=0)
                st.plotly_chart(fig, use_container_width=True)

                st.download_button(
                    "⬇ Download Cleaned Data",
                    data=df.to_csv(index=False).encode(),
                    file_name="preview_data.csv",
                    use_container_width=True,
                )
        else:
            st.info("No numeric columns available for visualization.")

    # ── DATA TAB ──
    with tab2:
        st.markdown('<div class="section-title">Dataset Preview</div>', unsafe_allow_html=True)
        st.dataframe(df.head(20), use_container_width=True)

    # ── INSIGHTS TAB ──
    with tab3:
        st.markdown('<div class="section-title">AI Insights</div>', unsafe_allow_html=True)

        if missing > 0:
            st.warning(f"⚠️ Dataset contains **{missing:,}** missing values across columns.")
        if dups > 0:
            st.warning(f"⚠️ Found **{dups}** duplicate rows that may affect analysis quality.")
        if missing == 0 and dups == 0:
            st.success("✅ Dataset looks clean — no missing values or duplicates detected.")

        # Column-level breakdown
        st.markdown('<div class="section-title" style="margin-top:20px">Column Summary</div>',
                    unsafe_allow_html=True)
        summary = pd.DataFrame({
            "Column": df.columns,
            "Type": df.dtypes.astype(str).values,
            "Missing": df.isnull().sum().values,
            "Unique": df.nunique().values,
        })
        st.dataframe(summary, use_container_width=True, hide_index=True)

    st.divider()

    # ── CLEAN DATASET SECTION ──
    st.markdown("""
    <div class="clean-card">
        <div class="clean-card-title">🚀 Clean Dataset</div>
    """, unsafe_allow_html=True)

    if run_clean:
        try:
            with st.spinner("Processing dataset with AI cleaning engine..."):
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
                    st.error(f"Backend returned error {response.status_code}")
                    st.text(response.text)
                    st.stop()

                df_clean = pd.read_excel(BytesIO(response.content), engine="openpyxl")
                st.success("✅ Cleaning completed successfully!")

                c1, c2, c3 = st.columns(3)
                c1.metric("Rows", f"{df_clean.shape[0]:,}")
                c2.metric("Columns", df_clean.shape[1])
                c3.metric("Quality Score", response.headers.get("X-Quality-Score", "N/A"))

                st.markdown('<div class="section-title" style="margin-top:16px">✨ Cleaned Dataset</div>',
                            unsafe_allow_html=True)
                st.dataframe(df_clean.head(10), use_container_width=True)

                st.download_button(
                    "⬇ Download Cleaned Data",
                    data=response.content,
                    file_name="cleaned.xlsx",
                    use_container_width=True,
                )
        except Exception as e:
            st.error("An error occurred during cleaning.")
            st.text(str(e))
    else:
        st.markdown("""
        <p style="color:#475569; font-size:14px; margin-bottom:16px;">
            Click <strong style="color:#60a5fa">Clean Data</strong> in the sidebar to process your dataset.
        </p>
        """, unsafe_allow_html=True)

        st.download_button(
            "⬇ Download Current Data",
            data=df.to_csv(index=False).encode(),
            file_name="data.csv",
            use_container_width=True,
        )

    st.markdown("</div>", unsafe_allow_html=True)

else:
    st.markdown("""
    <div style="text-align:center; padding: 80px 0; color:#475569;">
        <div style="font-size:48px; margin-bottom:16px;">📁</div>
        <div style="font-size:20px; font-weight:600; color:#64748b; margin-bottom:8px;">
            No dataset uploaded
        </div>
        <div style="font-size:14px;">
            Use the sidebar to upload a CSV file and begin cleaning
        </div>
    </div>
    """, unsafe_allow_html=True)