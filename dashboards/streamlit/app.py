import sys
import os
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from sqlalchemy import text

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
sys.path.append(PROJECT_ROOT)

from database.db_config import engine
from analytics.schema_mapper import map_columns
from analytics.data_cleaning import clean_data

st.set_page_config(page_title="Customer Analytics Dashboard", layout="wide")

# ── CSS: exact match to reference image ──────────────────────────────────────
st.markdown("""
<style>

@import url('https://fonts.googleapis.com/css2?family=Open+Sans:wght@300;400;600;700&display=swap');

* {
    font-family: 'Open Sans', Arial, sans-serif !important;
}

/* White page */
[data-testid="stAppViewContainer"] {
    background: #ffffff !important;
}

[data-testid="stHeader"] {
    background: #ffffff !important;
    box-shadow: none !important;
    border-bottom: 1px solid #dce6f0;
}

/* ── Sidebar: white with left border ── */
section[data-testid="stSidebar"] {
    background: #f7f9fc !important;
    border-right: 1px solid #dce6f0 !important;
}

section[data-testid="stSidebar"] * {
    color: #1a2744 !important;
}

section[data-testid="stSidebar"] h2, 
section[data-testid="stSidebar"] h3 {
    font-size: 11px !important;
    font-weight: 700 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.06em !important;
    color: #8a9bb5 !important;
    border-bottom: 1px solid #dce6f0 !important;
    padding-bottom: 6px !important;
    margin-top: 20px !important;
}

/* ── Page title area ── */
h1 {
    font-size: 24px !important;
    font-weight: 400 !important;
    color: #1a1a2e !important;
    letter-spacing: -0.01em !important;
}

/* ── KPI Cards: exact reference style ── */
.kpi-card {
    background: #ffffff;
    border: 1px solid #d0d8e8;
    border-top: 3px solid #2980c4;
    padding: 16px 20px;
    margin-bottom: 0;
}

.kpi-label {
    font-size: 11px;
    color: #6b7c99;
    text-transform: none;
    margin-bottom: 2px;
}

.kpi-value {
    font-size: 28px;
    font-weight: 700;
    color: #1a2744;
    line-height: 1.1;
}

.kpi-sub {
    font-size: 10px;
    color: #aab5c8;
    margin-top: 2px;
}

/* ── Section/panel wrapper ── */
.panel-box {
    border: 1px solid #d0d8e8;
    background: #ffffff;
    padding: 16px;
    margin-bottom: 16px;
}

.panel-title {
    font-size: 13px;
    font-weight: 700;
    color: #1a2744;
    margin-bottom: 2px;
}

.panel-subtitle {
    font-size: 10px;
    color: #aab5c8;
    margin-bottom: 12px;
}

/* ── Domain/page table ── */
.domain-table {
    width: 100%;
    border-collapse: collapse;
    font-size: 11px;
}

.domain-table th {
    color: #9baabb;
    font-weight: 400;
    font-size: 10px;
    padding: 3px 0;
    text-transform: none;
    border-bottom: 1px solid #eef2f7;
}

.domain-table td {
    padding: 4px 0;
    color: #1a2744;
    vertical-align: middle;
}

.domain-table td.views {
    text-align: right;
    color: #6b7c99;
    font-size: 11px;
}

.bar-wrap {
    background: #e8f4fb;
    height: 10px;
    border-radius: 2px;
    width: 120px;
}

.bar-fill {
    height: 10px;
    border-radius: 2px;
    background: #3b9ad9;
}

/* ── Plotly charts: reference styling ── */
/* Remove default streamlit chart padding */
[data-testid="stPlotlyChart"] {
    border: none !important;
    padding: 0 !important;
}

/* ── Download button ── */
.stDownloadButton > button {
    background: #1a4f8a !important;
    color: #ffffff !important;
    border: none !important;
    border-radius: 4px !important;
    font-size: 12px !important;
    font-weight: 600 !important;
    padding: 8px 18px !important;
}

/* ── Divider ── */
hr {
    border: none !important;
    border-top: 1px solid #d0d8e8 !important;
    margin: 16px 0 !important;
}

/* ── Success alert ── */
[data-testid="stAlert"] {
    border-radius: 4px !important;
    border: 1px solid #b8d8f0 !important;
    background: #eaf4fb !important;
    color: #1a4f8a !important;
}

/* ── DataFrame ── */
[data-testid="stDataFrame"] thead th {
    background: #f4f7fc !important;
    color: #6b7c99 !important;
    font-size: 11px !important;
    font-weight: 600 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.04em !important;
}

[data-testid="stDataFrame"] {
    border: 1px solid #d0d8e8 !important;
    font-size: 12px !important;
}

</style>
""", unsafe_allow_html=True)


# ── CHART THEME (matches image: white bg, teal/navy bars, light gridlines) ──
NAVY   = "#1a2744"
BLUE1  = "#1a4f8a"
BLUE2  = "#2980c4"
TEAL1  = "#3b9ad9"
TEAL2  = "#5bb8d4"
TEAL3  = "#8dd5e8"
PALETTE = [BLUE1, TEAL1, TEAL2, TEAL3, BLUE2, "#9dd4e8"]

def chart_layout(title=""):
    return dict(
        template="plotly_white",
        paper_bgcolor="#ffffff",
        plot_bgcolor="#ffffff",
        font=dict(family="Open Sans, Arial, sans-serif", color=NAVY, size=11),
        title=dict(
            text=f"<b>{title}</b>" if title else "",
            font=dict(size=13, color=NAVY),
            x=0, pad=dict(l=0, t=4)
        ),
        margin=dict(l=4, r=4, t=36 if title else 8, b=8),
        xaxis=dict(
            gridcolor="#eff3f8",
            linecolor="#d0d8e8",
            tickcolor="#d0d8e8",
            tickfont=dict(size=10, color="#9baabb"),
            title_font=dict(size=10)
        ),
        yaxis=dict(
            gridcolor="#eff3f8",
            linecolor="#d0d8e8",
            tickcolor="#d0d8e8",
            tickfont=dict(size=10, color="#9baabb"),
            title_font=dict(size=10)
        ),
        legend=dict(
            font=dict(size=10, color=NAVY),
            bgcolor="rgba(0,0,0,0)",
            borderwidth=0,
            orientation="h",
            y=-0.2
        ),
        colorway=PALETTE,
    )


# ── PAGE TITLE ────────────────────────────────────────────────────────────────
st.markdown("""
<h1 style="font-size:22px;font-weight:400;color:#1a1a2e;margin:8px 0 2px">
    Customer Behaviour Analysis KPI Dashboard
</h1>
<p style="font-size:11px;color:#888;margin:0 0 20px;max-width:900px">
    The following dashboard showcases customer behavior assessment to gain competitive advantages and analyze
    purchase patterns. It includes revenue, conversions, traffic sources, campaigns and device insights.
</p>
""", unsafe_allow_html=True)


# ── SIDEBAR ───────────────────────────────────────────────────────────────────
st.sidebar.markdown("<div style='padding:4px 0 12px'><span style='font-size:15px;font-weight:700;color:#1a2744'>Analytics</span><br><span style='font-size:10px;color:#9baabb;text-transform:uppercase;letter-spacing:.06em'>Control Panel</span></div>", unsafe_allow_html=True)
st.sidebar.header("Upload Dataset")

uploaded_file = st.sidebar.file_uploader("Upload Excel File", type=["xlsx"], key="upload_excel")
if uploaded_file:
    df_new = pd.read_excel(uploaded_file, engine="openpyxl")
    df_new = map_columns(df_new)
    df_new = clean_data(df_new)
    df_new.to_sql("analytics_data", con=engine, if_exists="append", index=False, chunksize=200)
    st.sidebar.success("✅ Data inserted successfully!")


# ── LOAD DATA ─────────────────────────────────────────────────────────────────
df = pd.read_sql(text("SELECT * FROM analytics_data"), engine)
if df.empty:
    st.warning("No data available in database.")
    st.stop()

df["date"] = pd.to_datetime(df["date"])


# ── SIDEBAR FILTERS ───────────────────────────────────────────────────────────
st.sidebar.header("Filters")
min_date = df["date"].min().date()
max_date = df["date"].max().date()
start_date = st.sidebar.date_input("Start Date", min_date)
end_date   = st.sidebar.date_input("End Date",   max_date)

selected_cities  = st.sidebar.multiselect("City",           df["city"].unique(),           default=list(df["city"].unique()))
selected_sources = st.sidebar.multiselect("Traffic Source", df["traffic_source"].unique(), default=list(df["traffic_source"].unique()))


# ── FILTER ────────────────────────────────────────────────────────────────────
df_f = df[
    (df["date"].dt.date >= start_date) &
    (df["date"].dt.date <= end_date)   &
    (df["city"].isin(selected_cities))  &
    (df["traffic_source"].isin(selected_sources))
]


# ── KPI ───────────────────────────────────────────────────────────────────────
total_revenue   = df_f["revenue"].sum()
total_cost      = df_f["cost"].sum()
total_clicks    = df_f["clicks"].sum()
conversion_rate = (df_f["converted"].sum() / total_clicks * 100) if total_clicks > 0 else 0

k1, k2, k3, k4 = st.columns(4)

for col, label, val, sub, accent in [
    (k1, "Total Revenue",    f"₹{total_revenue:,.0f}",   "All filtered periods",    "#2980c4"),
    (k2, "Total Cost",       f"₹{total_cost:,.0f}",      "Operational spend",       "#e05c5c"),
    (k3, "Conversion Rate",  f"{conversion_rate:.2f}%",  "Clicks → converted",      "#27ae7a"),
    (k4, "Total Clicks",     f"{total_clicks:,}",         "Across all sources",      "#8b5cf6"),
]:
    col.markdown(f"""
    <div class="kpi-card" style="border-top-color:{accent}">
        <div class="kpi-label">{label}</div>
        <div class="kpi-value">{val}</div>
        <div class="kpi-sub">{sub}</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)


# ── ROW 1: Visitors bar chart (full-width area) + Pie ─────────────────────────
col_a, col_b = st.columns([2, 1])

with col_a:
    trend = df_f.groupby(df_f["date"].dt.date)["clicks"].sum().reset_index()
    fig_trend = go.Figure()
    fig_trend.add_trace(go.Bar(
        x=trend["date"], y=trend["clicks"],
        marker_color=TEAL1, marker_line_width=0,
        name="Visitors"
    ))
    fig_trend.update_layout(**chart_layout(""))
    fig_trend.update_layout(showlegend=False, bargap=0.15)
    st.markdown('<div class="panel-box"><div class="panel-title">Visitors over time</div><div class="panel-subtitle">Daily click volume</div>', unsafe_allow_html=True)
    st.plotly_chart(fig_trend, use_container_width=True, config={"displayModeBar": False})
    st.markdown('</div>', unsafe_allow_html=True)

with col_b:
    device_data = df_f.groupby("device_type")["revenue"].sum().reset_index()
    fig_pie = go.Figure(go.Pie(
        labels=device_data["device_type"],
        values=device_data["revenue"],
        hole=0,
        textinfo="label+percent",
        textfont_size=11,
        marker=dict(colors=[BLUE1, BLUE2, TEAL1, TEAL2, TEAL3])
    ))
    fig_pie.update_layout(**chart_layout("Visitors by device"))
    fig_pie.update_layout(showlegend=False, margin=dict(l=4, r=4, t=36, b=8))
    st.markdown('<div class="panel-box"><div class="panel-title">Visitors by device</div>', unsafe_allow_html=True)
    st.plotly_chart(fig_pie, use_container_width=True, config={"displayModeBar": False})
    st.markdown('</div>', unsafe_allow_html=True)


# ── ROW 2: Multi-line / city bars + domain tables ─────────────────────────────
col_c, col_d, col_e = st.columns([1.4, 1.3, 1.3])

with col_c:
    trend_src = df_f.groupby([df_f["date"].dt.date, "traffic_source"])["clicks"].sum().reset_index()
    fig_lines = px.line(
        trend_src, x="date", y="clicks",
        color="traffic_source",
        markers=True,
        color_discrete_sequence=[NAVY, BLUE1, TEAL1, TEAL2],
        title="Page views by source"
    )
    fig_lines.update_traces(line_width=1.8)
    fig_lines.update_layout(**chart_layout("Page views"))
    st.markdown('<div class="panel-box"><div class="panel-title">Page views</div><div class="panel-subtitle">By traffic source</div>', unsafe_allow_html=True)
    st.plotly_chart(fig_lines, use_container_width=True, config={"displayModeBar": False})
    st.markdown('</div>', unsafe_allow_html=True)

with col_d:
    # Top referring cities as domain-style table
    city_rev = df_f.groupby("city")["clicks"].sum().reset_index().sort_values("clicks", ascending=False).head(10)
    max_v = city_rev["clicks"].max() if not city_rev.empty else 1
    rows = ""
    for _, row in city_rev.iterrows():
        pct = int(row["clicks"] / max_v * 100)
        rows += f"""
        <tr>
            <td>{row['city']}</td>
            <td><div class="bar-wrap"><div class="bar-fill" style="width:{pct}%"></div></div></td>
            <td class="views">{int(row['clicks']):,}</td>
        </tr>"""
    st.markdown(f"""
    <div class="panel-box" style="min-height:280px">
        <div class="panel-title">Top cities</div>
        <table class="domain-table" style="margin-top:8px">
            <tr><th>City</th><th>Clicks</th><th>Views</th></tr>
            {rows}
        </table>
    </div>
    """, unsafe_allow_html=True)

with col_e:
    # Top campaigns as page-style table
    camp_rev = df_f.groupby("campaign")["revenue"].sum().reset_index().sort_values("revenue", ascending=False).head(10)
    max_v2 = camp_rev["revenue"].max() if not camp_rev.empty else 1
    rows2 = ""
    for _, row in camp_rev.iterrows():
        pct = int(row["revenue"] / max_v2 * 100)
        rows2 += f"""
        <tr>
            <td>{row['campaign']}</td>
            <td><div class="bar-wrap"><div class="bar-fill" style="width:{pct}%"></div></div></td>
            <td class="views">₹{int(row['revenue']):,}</td>
        </tr>"""
    st.markdown(f"""
    <div class="panel-box" style="min-height:280px">
        <div class="panel-title">Top campaigns</div>
        <table class="domain-table" style="margin-top:8px">
            <tr><th>Campaign</th><th>Revenue</th><th>Value</th></tr>
            {rows2}
        </table>
    </div>
    """, unsafe_allow_html=True)


# ── ROW 3: Campaign conversions + ROI ─────────────────────────────────────────
col_f, col_g = st.columns(2)

with col_f:
    conv_c = df_f.groupby("campaign")["converted"].sum().reset_index()
    fig_conv = px.bar(conv_c, x="campaign", y="converted",
                      color="converted",
                      color_continuous_scale=[[0, "#e8f4fb"], [1, TEAL1]],
                      title="Conversions by campaign")
    fig_conv.update_coloraxes(showscale=False)
    fig_conv.update_layout(**chart_layout("Conversions by campaign"))
    st.plotly_chart(fig_conv, use_container_width=True, config={"displayModeBar": False})

with col_g:
    roi_c = df_f.groupby("campaign")["roi"].mean().reset_index()
    fig_roi = px.bar(roi_c, x="campaign", y="roi",
                     color="roi",
                     color_continuous_scale=[[0, "#ede8fb"], [1, "#5b3aed"]],
                     title="Average ROI by campaign")
    fig_roi.update_coloraxes(showscale=False)
    fig_roi.update_layout(**chart_layout("Average ROI by campaign"))
    st.plotly_chart(fig_roi, use_container_width=True, config={"displayModeBar": False})


# ── RAW DATA ──────────────────────────────────────────────────────────────────
st.markdown("""
<div style="font-size:12px;font-weight:700;color:#1a2744;text-transform:uppercase;
            letter-spacing:.06em;border-bottom:1px solid #d0d8e8;padding-bottom:6px;margin-bottom:12px">
    Raw Data
</div>
""", unsafe_allow_html=True)
st.dataframe(df_f, use_container_width=True, height=300)

csv = df_f.to_csv(index=False).encode("utf-8")
st.download_button(
    label="⬇  Export Filtered Data (CSV)",
    data=csv,
    file_name="filtered_analytics_data.csv",
    mime="text/csv"
)

st.markdown("""
<div style="font-size:9px;color:#c0c8d8;text-align:center;margin-top:24px;padding-top:12px;border-top:1px solid #eef2f7">
    This dashboard is linked to the database and updates automatically based on uploaded data.
</div>
""", unsafe_allow_html=True)
