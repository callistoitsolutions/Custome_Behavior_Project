import sys
import os
import streamlit as st
import pandas as pd
import plotly.express as px
from sqlalchemy import text
from datetime import datetime

# ---------------- PROJECT PATH ----------------
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
sys.path.append(PROJECT_ROOT)

from database.db_config import engine
from analytics.schema_mapper import map_columns
from analytics.data_cleaning import clean_data

# ---------------- PAGE CONFIG ----------------
st.set_page_config(page_title="Customer Analytics Dashboard", layout="wide")

# ---------------- CSS ----------------
st.markdown("""
<style>
[data-testid="stAppViewContainer"] {
    background: linear-gradient(135deg, #f5f7fa, #e4ecf7);
}
section[data-testid="stSidebar"] {
    background: #ffffff !important;
    border-right: 1px solid #e6e6e6;
}
section[data-testid="stSidebar"] * {
    color: #333333 !important;
}
.metric-card {
    background: white;
    padding: 25px;
    border-radius: 16px;
    box-shadow: 0 8px 20px rgba(0,0,0,0.08);
    text-align: center;
    transition: 0.3s ease;
}
.metric-card:hover {
    transform: translateY(-5px);
    box-shadow: 0 12px 25px rgba(0,0,0,0.12);
}
.metric-title { font-size: 14px; color: #666; }
.metric-value { font-size: 30px; font-weight: bold; color: #1f3c88; }
h1, h2, h3 { color: #1f3c88; }
hr { border: 1px solid rgba(0,0,0,0.08); }
</style>
""", unsafe_allow_html=True)

# ---------------- TITLE ----------------
st.title("📊 Customer Behavior Analytics Dashboard")

# =========================================================
# ---------------- ENSURE session_id COLUMN EXISTS ----------------
# =========================================================
with engine.connect() as conn:
    try:
        conn.execute(text("ALTER TABLE analytics_data ADD COLUMN session_id TEXT"))
        conn.commit()
    except Exception:
        pass  # Column already exists

# =========================================================
# ---------------- SIDEBAR UPLOAD ----------------
# =========================================================
st.sidebar.header("📂 Upload New Dataset")

uploaded_file = st.sidebar.file_uploader(
    "Upload Excel File",
    type=["xlsx"],
    key="upload_excel"
)

if uploaded_file:
    df_new = pd.read_excel(uploaded_file, engine="openpyxl")
    df_new = map_columns(df_new)
    df_new = clean_data(df_new)

    # ✅ Assign unique session ID based on filename + timestamp
    session_id = f"{uploaded_file.name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    df_new["session_id"] = session_id

    df_new.to_sql(
        name="analytics_data",
        con=engine,
        if_exists="append",
        index=False,
        chunksize=200
    )

    st.sidebar.success(f"✅ Dataset uploaded: `{session_id}`")

# =========================================================
# ---------------- LOAD ALL DATA ----------------
# =========================================================
query = text("SELECT * FROM analytics_data")
df_all = pd.read_sql(query, engine)

if df_all.empty:
    st.warning("No data available in database.")
    st.stop()

# =========================================================
# ---------------- DATASET SELECTOR ----------------
# =========================================================
st.sidebar.header("📁 Select Dataset")

if "session_id" not in df_all.columns or df_all["session_id"].isnull().all():
    st.warning("⚠️ Old data has no session tags. Please re-upload your datasets.")
    st.stop()

available_sessions = df_all["session_id"].dropna().unique().tolist()

selected_session = st.sidebar.selectbox(
    "Choose Uploaded Dataset",
    options=available_sessions,
    format_func=lambda x: x  # Shows full session label
)

# ✅ Filter to only the selected dataset
df = df_all[df_all["session_id"] == selected_session].copy()

st.info(f"📂 Showing results for: **{selected_session}**")

# =========================================================
# ---------------- TYPE CONVERSION ----------------
# =========================================================
df["date"]      = pd.to_datetime(df["date"])
df["revenue"]   = pd.to_numeric(df["revenue"],   errors="coerce").fillna(0)
df["cost"]      = pd.to_numeric(df["cost"],      errors="coerce").fillna(0)
df["clicks"]    = pd.to_numeric(df["clicks"],    errors="coerce").fillna(0)
df["converted"] = pd.to_numeric(df["converted"], errors="coerce").fillna(0)
df["roi"]       = pd.to_numeric(df["roi"],       errors="coerce").fillna(0)

# =========================================================
# ---------------- SIDEBAR FILTERS ----------------
# =========================================================
st.sidebar.header("🔎 Filters")

min_date = df["date"].min().date()
max_date = df["date"].max().date()

start_date = st.sidebar.date_input("Start Date", min_date)
end_date   = st.sidebar.date_input("End Date",   max_date)

selected_cities = st.sidebar.multiselect(
    "Select City",
    df["city"].unique(),
    default=df["city"].unique()
)

selected_sources = st.sidebar.multiselect(
    "Select Traffic Source",
    df["traffic_source"].unique(),
    default=df["traffic_source"].unique()
)

# =========================================================
# ---------------- APPLY FILTERS ----------------
# =========================================================
df_filtered = df[
    (df["date"].dt.date >= start_date) &
    (df["date"].dt.date <= end_date) &
    (df["city"].isin(selected_cities)) &
    (df["traffic_source"].isin(selected_sources))
]

# =========================================================
# ---------------- KPI CALCULATIONS ----------------
# =========================================================
total_revenue   = df_filtered["revenue"].sum()
total_cost      = df_filtered["cost"].sum()
total_clicks    = int(df_filtered["clicks"].sum())
conversion_rate = (
    df_filtered["converted"].sum() / total_clicks * 100
    if total_clicks > 0 else 0
)

# =========================================================
# ---------------- KPI CARDS ----------------
# =========================================================
k1, k2, k3, k4 = st.columns(4)

k1.markdown(f"""
<div class="metric-card">
    <div class="metric-title">Total Revenue</div>
    <div class="metric-value">₹{total_revenue:,.0f}</div>
</div>""", unsafe_allow_html=True)

k2.markdown(f"""
<div class="metric-card">
    <div class="metric-title">Total Cost</div>
    <div class="metric-value">₹{total_cost:,.0f}</div>
</div>""", unsafe_allow_html=True)

k3.markdown(f"""
<div class="metric-card">
    <div class="metric-title">Conversion Rate</div>
    <div class="metric-value">{conversion_rate:.2f}%</div>
</div>""", unsafe_allow_html=True)

k4.markdown(f"""
<div class="metric-card">
    <div class="metric-title">Total Clicks</div>
    <div class="metric-value">{total_clicks:,}</div>
</div>""", unsafe_allow_html=True)

st.markdown("---")

# =========================================================
# ---------------- REVENUE TREND ----------------
# =========================================================
trend = df_filtered.groupby(df_filtered["date"].dt.date)["revenue"].sum().reset_index()
fig_trend = px.line(trend, x="date", y="revenue",
                    title="Revenue Trend Over Time", template="plotly_white")
st.plotly_chart(fig_trend, use_container_width=True)

# =========================================================
# ---------------- ROW 2 ----------------
# =========================================================
col1, col2 = st.columns(2)

rev_city = df_filtered.groupby("city")["revenue"].sum().reset_index()
fig_city = px.bar(rev_city, x="revenue", y="city", orientation="h",
                  title="Total Revenue by City", template="plotly_white",
                  color="revenue", color_continuous_scale="Blues")
col1.plotly_chart(fig_city, use_container_width=True)

source_data = df_filtered.groupby("traffic_source")["clicks"].sum().reset_index()
fig_source = px.pie(source_data, names="traffic_source", values="clicks",
                    hole=0.5, title="Traffic Source Distribution",
                    template="plotly_white")
col2.plotly_chart(fig_source, use_container_width=True)

# =========================================================
# ---------------- ROW 3 ----------------
# =========================================================
col3, col4 = st.columns(2)

conv_campaign = df_filtered.groupby("campaign")["converted"].sum().reset_index()
fig_campaign = px.bar(conv_campaign, x="campaign", y="converted",
                      title="Total Conversions by Campaign",
                      template="plotly_white", color="converted",
                      color_continuous_scale="Greens")
col3.plotly_chart(fig_campaign, use_container_width=True)

roi_campaign = df_filtered.groupby("campaign")["roi"].mean().reset_index()
fig_roi = px.bar(roi_campaign, x="campaign", y="roi",
                 title="ROI by Campaign", template="plotly_white",
                 color="roi", color_continuous_scale="Purples")
col4.plotly_chart(fig_roi, use_container_width=True)

# =========================================================
# ---------------- DEVICE TYPE PIE ----------------
# =========================================================
device_data = df_filtered.groupby("device_type")["revenue"].sum().reset_index()
fig_device = px.pie(device_data, names="device_type", values="revenue",
                    title="Revenue by Device Type", template="plotly_white")
st.plotly_chart(fig_device, use_container_width=True)

st.markdown("---")

# =========================================================
# ---------------- RAW DATA ----------------
# =========================================================
st.subheader("📄 Raw Data")
st.dataframe(df_filtered.drop(columns=["session_id"], errors="ignore"),
             use_container_width=True)

# =========================================================
# ---------------- DOWNLOAD ----------------
# =========================================================
csv = df_filtered.drop(columns=["session_id"], errors="ignore")\
                 .to_csv(index=False).encode("utf-8")

st.download_button(
    label="⬇ Download Filtered Data (CSV)",
    data=csv,
    file_name=f"filtered_{selected_session}.csv",
    mime="text/csv"
)
