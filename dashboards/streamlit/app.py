import sys
import os
import streamlit as st
import pandas as pd
import plotly.express as px
from sqlalchemy import text

# ---------------- PROJECT PATH ----------------
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
sys.path.append(PROJECT_ROOT)

from database.db_config import engine
from analytics.schema_mapper import map_columns
from analytics.data_cleaning import clean_data

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="Customer Analytics Dashboard",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------------- PROFESSIONAL CORPORATE UI ----------------
st.markdown("""
<style>

/* ── Google Fonts ── */
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600&family=DM+Mono:wght@400;500&display=swap');

/* ── Root Variables ── */
:root {
    --navy:       #0d1b3e;
    --blue-mid:   #1a4a8a;
    --blue:       #1e6fc5;
    --teal:       #19a8b8;
    --teal-light: #e0f7fa;
    --sky:        #e8f4fd;
    --white:      #ffffff;
    --surface:    #f4f7fc;
    --border:     #dce6f3;
    --text-main:  #0d1b3e;
    --text-muted: #5a6f8a;
    --text-light: #8fa3bb;
    --accent:     #19a8b8;
    --green:      #16a34a;
    --amber:      #d97706;
    --red:        #dc2626;
    --shadow-sm:  0 1px 4px rgba(13,27,62,0.07);
    --shadow-md:  0 4px 16px rgba(13,27,62,0.10);
    --radius:     10px;
    --radius-lg:  16px;
}

/* ── Base ── */
* { font-family: 'DM Sans', sans-serif; }

[data-testid="stAppViewContainer"] {
    background: var(--surface);
}

[data-testid="stHeader"] {
    background: var(--white);
    border-bottom: 1px solid var(--border);
}

/* ── Sidebar ── */
section[data-testid="stSidebar"] {
    background: var(--navy) !important;
    border-right: none;
}

section[data-testid="stSidebar"] * {
    color: #c8d8ef !important;
    font-family: 'DM Sans', sans-serif !important;
}

section[data-testid="stSidebar"] h1,
section[data-testid="stSidebar"] h2,
section[data-testid="stSidebar"] h3 {
    color: #ffffff !important;
    font-size: 13px !important;
    font-weight: 600 !important;
    letter-spacing: 0.06em;
    text-transform: uppercase;
    margin-top: 1.4rem !important;
    padding-bottom: 6px;
    border-bottom: 1px solid rgba(255,255,255,0.08);
}

section[data-testid="stSidebar"] .stFileUploader label,
section[data-testid="stSidebar"] .stDateInput label,
section[data-testid="stSidebar"] .stMultiSelect label {
    color: #a8c0dc !important;
    font-size: 12px !important;
    text-transform: uppercase;
    letter-spacing: 0.05em;
}

section[data-testid="stSidebar"] [data-testid="stFileUploaderDropzone"] {
    background: rgba(255,255,255,0.05) !important;
    border: 1px dashed rgba(255,255,255,0.2) !important;
    border-radius: var(--radius) !important;
}

section[data-testid="stSidebar"] [data-testid="stMultiSelect"] > div > div {
    background: rgba(255,255,255,0.07) !important;
    border: 1px solid rgba(255,255,255,0.15) !important;
    border-radius: var(--radius) !important;
}

/* ── Page Header / Title ── */
h1 {
    font-size: 22px !important;
    font-weight: 600 !important;
    color: var(--navy) !important;
    letter-spacing: -0.01em;
}

h2, h3 {
    color: var(--navy) !important;
    font-weight: 500 !important;
}

/* ── KPI Metric Cards ── */
.kpi-row {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 16px;
    margin-bottom: 24px;
}

.kpi-card {
    background: var(--white);
    border: 1px solid var(--border);
    border-radius: var(--radius-lg);
    padding: 20px 24px;
    position: relative;
    overflow: hidden;
    transition: box-shadow 0.2s;
}

.kpi-card:hover {
    box-shadow: var(--shadow-md);
}

.kpi-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 3px;
}

.kpi-card.revenue::before { background: linear-gradient(90deg, #1e6fc5, #19a8b8); }
.kpi-card.cost::before    { background: linear-gradient(90deg, #dc2626, #f59e0b); }
.kpi-card.conv::before    { background: linear-gradient(90deg, #16a34a, #19a8b8); }
.kpi-card.clicks::before  { background: linear-gradient(90deg, #7c3aed, #1e6fc5); }

.kpi-icon {
    width: 36px;
    height: 36px;
    border-radius: 8px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 16px;
    margin-bottom: 12px;
}

.kpi-icon.revenue { background: #e8f4fd; }
.kpi-icon.cost    { background: #fef2f2; }
.kpi-icon.conv    { background: #f0fdf4; }
.kpi-icon.clicks  { background: #f5f3ff; }

.kpi-label {
    font-size: 11px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.07em;
    color: var(--text-muted);
    margin-bottom: 4px;
}

.kpi-value {
    font-size: 26px;
    font-weight: 600;
    color: var(--navy);
    line-height: 1.1;
    font-variant-numeric: tabular-nums;
}

.kpi-sub {
    font-size: 11px;
    color: var(--text-light);
    margin-top: 4px;
}

/* ── Section Headers ── */
.section-header {
    display: flex;
    align-items: center;
    gap: 8px;
    margin: 24px 0 12px;
    padding-bottom: 10px;
    border-bottom: 1px solid var(--border);
}

.section-title {
    font-size: 13px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.07em;
    color: var(--text-muted);
}

.section-dot {
    width: 6px;
    height: 6px;
    border-radius: 50%;
    background: var(--teal);
    flex-shrink: 0;
}

/* ── Chart Containers ── */
.chart-card {
    background: var(--white);
    border: 1px solid var(--border);
    border-radius: var(--radius-lg);
    padding: 20px;
    margin-bottom: 16px;
}

.chart-title {
    font-size: 13px;
    font-weight: 600;
    color: var(--navy);
    margin-bottom: 4px;
}

.chart-sub {
    font-size: 11px;
    color: var(--text-light);
    margin-bottom: 16px;
}

/* ── Data Table ── */
[data-testid="stDataFrame"] {
    border: 1px solid var(--border) !important;
    border-radius: var(--radius-lg) !important;
    overflow: hidden;
}

[data-testid="stDataFrame"] thead th {
    background: var(--surface) !important;
    color: var(--text-muted) !important;
    font-size: 11px !important;
    font-weight: 600 !important;
    text-transform: uppercase;
    letter-spacing: 0.06em;
}

/* ── Plotly Charts Override ── */
.js-plotly-plot .plotly .main-svg {
    border-radius: var(--radius) !important;
}

/* ── Download Button ── */
.stDownloadButton > button {
    background: var(--navy) !important;
    color: white !important;
    border: none !important;
    border-radius: var(--radius) !important;
    font-size: 13px !important;
    font-weight: 500 !important;
    padding: 10px 20px !important;
    letter-spacing: 0.02em;
    transition: background 0.2s !important;
}

.stDownloadButton > button:hover {
    background: var(--blue-mid) !important;
}

/* ── Alert / Warning ── */
[data-testid="stAlert"] {
    border-radius: var(--radius) !important;
    border: 1px solid var(--border) !important;
    background: var(--sky) !important;
}

/* ── Success message ── */
.element-container .stAlert[data-baseweb="notification"] {
    border-radius: var(--radius) !important;
}

/* ── Divider ── */
hr {
    border: none !important;
    border-top: 1px solid var(--border) !important;
    margin: 24px 0 !important;
}

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: var(--border); border-radius: 3px; }

</style>
""", unsafe_allow_html=True)


# =========================================================
# ---------------- HEADER ----------------
# =========================================================
col_title, col_badge = st.columns([5, 1])
with col_title:
    st.markdown("""
    <div style="display:flex; align-items:center; gap:12px; padding: 8px 0 4px;">
        <div style="width:38px;height:38px;border-radius:10px;background:linear-gradient(135deg,#1e6fc5,#19a8b8);
                    display:flex;align-items:center;justify-content:center;font-size:18px;">📊</div>
        <div>
            <div style="font-size:20px;font-weight:600;color:#0d1b3e;line-height:1.1;">Customer Behavior Analytics</div>
            <div style="font-size:12px;color:#8fa3bb;margin-top:1px;">Real-time marketing intelligence dashboard</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# =========================================================
# ---------------- SIDEBAR ----------------
# =========================================================
st.sidebar.markdown("""
<div style="padding: 8px 0 16px;">
    <div style="font-size:18px;font-weight:700;color:white;letter-spacing:-0.01em;">Analytics</div>
    <div style="font-size:11px;color:#7a9abf;text-transform:uppercase;letter-spacing:0.08em;">Control Panel</div>
</div>
""", unsafe_allow_html=True)

st.sidebar.header("Upload Dataset")
uploaded_file = st.sidebar.file_uploader(
    "Upload Excel File",
    type=["xlsx"],
    key="upload_excel"
)

if uploaded_file:
    df_new = pd.read_excel(uploaded_file, engine="openpyxl")
    df_new = map_columns(df_new)
    df_new = clean_data(df_new)
    df_new.to_sql(
        name="analytics_data",
        con=engine,
        if_exists="append",
        index=False,
        chunksize=200
    )
    st.sidebar.success("✅ Data inserted successfully!")

# =========================================================
# ---------------- LOAD DATA ----------------
# =========================================================
query = text("SELECT * FROM analytics_data")
df = pd.read_sql(query, engine)

if df.empty:
    st.warning("No data available in database.")
    st.stop()

df["date"] = pd.to_datetime(df["date"])

# =========================================================
# ---------------- SIDEBAR FILTERS ----------------
# =========================================================
st.sidebar.header("Filters")

min_date = df["date"].min().date()
max_date = df["date"].max().date()

start_date = st.sidebar.date_input("Start Date", min_date)
end_date = st.sidebar.date_input("End Date", max_date)

selected_cities = st.sidebar.multiselect(
    "City",
    df["city"].unique(),
    default=df["city"].unique()
)

selected_sources = st.sidebar.multiselect(
    "Traffic Source",
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
total_clicks    = df_filtered["clicks"].sum()
conversion_rate = (
    df_filtered["converted"].sum() / total_clicks * 100
    if total_clicks > 0 else 0
)

# =========================================================
# ---------------- KPI CARDS ----------------
# =========================================================
k1, k2, k3, k4 = st.columns(4)

k1.markdown(f"""
<div class="kpi-card revenue">
  <div class="kpi-icon revenue">💰</div>
  <div class="kpi-label">Total Revenue</div>
  <div class="kpi-value">₹{total_revenue:,.0f}</div>
  <div class="kpi-sub">All filtered periods</div>
</div>
""", unsafe_allow_html=True)

k2.markdown(f"""
<div class="kpi-card cost">
  <div class="kpi-icon cost">📉</div>
  <div class="kpi-label">Total Cost</div>
  <div class="kpi-value">₹{total_cost:,.0f}</div>
  <div class="kpi-sub">Operational spend</div>
</div>
""", unsafe_allow_html=True)

k3.markdown(f"""
<div class="kpi-card conv">
  <div class="kpi-icon conv">🎯</div>
  <div class="kpi-label">Conversion Rate</div>
  <div class="kpi-value">{conversion_rate:.2f}%</div>
  <div class="kpi-sub">Clicks → Converted</div>
</div>
""", unsafe_allow_html=True)

k4.markdown(f"""
<div class="kpi-card clicks">
  <div class="kpi-icon clicks">🖱️</div>
  <div class="kpi-label">Total Clicks</div>
  <div class="kpi-value">{total_clicks:,}</div>
  <div class="kpi-sub">Across all sources</div>
</div>
""", unsafe_allow_html=True)

# =========================================================
# ---------------- PLOTLY THEME HELPER ----------------
# =========================================================
CHART_COLORS = ["#1e6fc5", "#19a8b8", "#7c3aed", "#16a34a", "#d97706", "#dc2626", "#0d1b3e"]

def base_layout(title=""):
    return dict(
        template="plotly_white",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="DM Sans, sans-serif", color="#0d1b3e", size=12),
        title=dict(text=title, font=dict(size=14, color="#0d1b3e", family="DM Sans"), x=0, pad=dict(l=0)),
        margin=dict(l=0, r=0, t=36, b=0),
        colorway=CHART_COLORS,
        xaxis=dict(gridcolor="#f0f4f9", linecolor="#dce6f3", tickcolor="#dce6f3"),
        yaxis=dict(gridcolor="#f0f4f9", linecolor="#dce6f3", tickcolor="#dce6f3"),
    )

# =========================================================
# ---------------- SECTION: REVENUE TREND ----------------
# =========================================================
st.markdown("""
<div class="section-header">
  <div class="section-dot"></div>
  <div class="section-title">Revenue Overview</div>
</div>
""", unsafe_allow_html=True)

trend = df_filtered.groupby(df_filtered["date"].dt.date)["revenue"].sum().reset_index()

fig_trend = px.area(
    trend,
    x="date",
    y="revenue",
    title="Revenue Trend Over Time",
)
fig_trend.update_traces(
    line=dict(color="#1e6fc5", width=2.5),
    fillcolor="rgba(30,111,197,0.08)"
)
fig_trend.update_layout(**base_layout("Revenue Trend Over Time"))
st.plotly_chart(fig_trend, use_container_width=True)

# =========================================================
# ---------------- ROW 2: City + Traffic Source ----------------
# =========================================================
st.markdown("""
<div class="section-header">
  <div class="section-dot"></div>
  <div class="section-title">Geographic & Channel Breakdown</div>
</div>
""", unsafe_allow_html=True)

col1, col2 = st.columns(2)

rev_city = df_filtered.groupby("city")["revenue"].sum().reset_index().sort_values("revenue", ascending=True)
fig_city = px.bar(
    rev_city,
    x="revenue",
    y="city",
    orientation="h",
    title="Revenue by City",
    color="revenue",
    color_continuous_scale=["#e8f4fd", "#1e6fc5"],
)
fig_city.update_layout(**base_layout("Revenue by City"))
fig_city.update_coloraxes(showscale=False)
col1.plotly_chart(fig_city, use_container_width=True)

source_data = df_filtered.groupby("traffic_source")["clicks"].sum().reset_index()
fig_source = px.pie(
    source_data,
    names="traffic_source",
    values="clicks",
    hole=0.55,
    title="Traffic Source Distribution",
    color_discrete_sequence=CHART_COLORS,
)
fig_source.update_layout(**base_layout("Traffic Source Distribution"))
fig_source.update_traces(textinfo="percent+label", textfont_size=11)
col2.plotly_chart(fig_source, use_container_width=True)

# =========================================================
# ---------------- ROW 3: Campaign ----------------
# =========================================================
st.markdown("""
<div class="section-header">
  <div class="section-dot"></div>
  <div class="section-title">Campaign Performance</div>
</div>
""", unsafe_allow_html=True)

col3, col4 = st.columns(2)

conv_campaign = df_filtered.groupby("campaign")["converted"].sum().reset_index()
fig_campaign = px.bar(
    conv_campaign,
    x="campaign",
    y="converted",
    title="Conversions by Campaign",
    color="converted",
    color_continuous_scale=["#f0fdf4", "#16a34a"],
)
fig_campaign.update_layout(**base_layout("Conversions by Campaign"))
fig_campaign.update_coloraxes(showscale=False)
col3.plotly_chart(fig_campaign, use_container_width=True)

roi_campaign = df_filtered.groupby("campaign")["roi"].mean().reset_index()
fig_roi = px.bar(
    roi_campaign,
    x="campaign",
    y="roi",
    title="Average ROI by Campaign",
    color="roi",
    color_continuous_scale=["#f5f3ff", "#7c3aed"],
)
fig_roi.update_layout(**base_layout("Average ROI by Campaign"))
fig_roi.update_coloraxes(showscale=False)
col4.plotly_chart(fig_roi, use_container_width=True)

# =========================================================
# ---------------- DEVICE TYPE ----------------
# =========================================================
st.markdown("""
<div class="section-header">
  <div class="section-dot"></div>
  <div class="section-title">Device Insights</div>
</div>
""", unsafe_allow_html=True)

device_data = df_filtered.groupby("device_type")["revenue"].sum().reset_index()
fig_device = px.pie(
    device_data,
    names="device_type",
    values="revenue",
    hole=0.55,
    title="Revenue by Device Type",
    color_discrete_sequence=["#1e6fc5", "#19a8b8", "#7c3aed", "#16a34a"],
)
fig_device.update_layout(**base_layout("Revenue by Device Type"))
fig_device.update_traces(textinfo="percent+label", textfont_size=12)
st.plotly_chart(fig_device, use_container_width=True)

# =========================================================
# ---------------- RAW DATA ----------------
# =========================================================
st.markdown("""
<div class="section-header">
  <div class="section-dot"></div>
  <div class="section-title">Raw Data</div>
</div>
""", unsafe_allow_html=True)

st.dataframe(df_filtered, use_container_width=True, height=320)

# =========================================================
# ---------------- DOWNLOAD ----------------
# =========================================================
csv = df_filtered.to_csv(index=False).encode("utf-8")

col_dl, _ = st.columns([1, 3])
with col_dl:
    st.download_button(
        label="⬇  Export Filtered Data (CSV)",
        data=csv,
        file_name="filtered_analytics_data.csv",
        mime="text/csv"
    )

st.markdown("<div style='height:32px'></div>", unsafe_allow_html=True)
