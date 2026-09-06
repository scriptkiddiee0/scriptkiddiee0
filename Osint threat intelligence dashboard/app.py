import streamlit as st
import pandas as pd
import plotly.express as px
import os

DATA_FILE = "data/iocs.csv"

st.set_page_config(page_title="Threat Intelligence Dashboard", layout="wide")

# Custom styling — holographic cyber-ops / SOC command-center look

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@600;700;800&family=IBM+Plex+Mono:wght@400;500&display=swap');

    :root {
        --ink: #E6F6FF;         /* main text — bright icy white-blue */
        --paper: #050B18;       /* app background — deep navy/black */
        --card: #0B1830;        /* card / panel background */
        --neon-cyan: #33D6FF;   /* primary neon accent */
        --neon-purple: #7B5CFF;/* secondary neon accent */
        --neon-pink: #FF4FD8;   /* highlight accent */
        --slate: #7FA8C9;       /* secondary/muted text */
        --rule: #1B3A5C;        /* hairlines / dividers */
    }

    html, body, [class*="css"] {
        color: var(--ink);
    }

    html, body, .stApp {
        background-color: var(--paper);
    }

    .main, [data-testid="stAppViewContainer"] {
        background: transparent;
    }

    /* holographic glow field behind everything */
    [data-testid="stAppViewContainer"] > .main {
        background:
            radial-gradient(ellipse at top, rgba(51,214,255,0.10) 0%, rgba(5,11,24,0) 55%),
            radial-gradient(ellipse at bottom right, rgba(123,92,255,0.08) 0%, rgba(5,11,24,0) 60%);
    }

    /* ---------------- Header: HUD panel ---------------- */
    .case-header-wrap {
        position: relative;
        margin-bottom: 1.8rem;
    }

    .folder-tab {
        display: inline-block;
        background: linear-gradient(90deg, var(--neon-cyan), var(--neon-purple));
        color: #04101F;
        font-family: 'IBM Plex Mono', monospace;
        font-weight: 600;
        font-size: 0.7rem;
        letter-spacing: 0.08em;
        padding: 0.25rem 0.9rem;
        border-radius: 4px 4px 0 0;
        margin-bottom: -1px;
    }

    .case-header {
        display: flex;
        align-items: baseline;
        justify-content: space-between;
        gap: 1rem;
        border-top: 3px solid var(--neon-cyan);
        padding-top: 0.7rem;
        box-shadow: 0 -1px 20px rgba(51,214,255,0.35);
    }

    h1.case-title {
        font-family: 'Orbitron', sans-serif;
        font-weight: 800;
        font-size: 2.2rem;
        color: var(--ink);
        letter-spacing: 0.03em;
        margin: 0;
        line-height: 1.05;
        text-shadow: 0 0 18px rgba(51,214,255,0.55), 0 0 36px rgba(123,92,255,0.25);
    }

    .case-tagline {
        font-family: 'IBM Plex Mono', monospace;
        font-weight: 400;
        font-size: 1rem;
        color: var(--neon-cyan);
        letter-spacing: 0.05em;
        margin-top: 0.3rem;
    }

    .subtitle {
        font-family: 'IBM Plex Mono', monospace;
        font-size: 0.82rem;
        color: var(--slate);
        margin-top: 0.6rem;
    }

    .stamp {
        flex-shrink: 0;
        width: 80px;
        height: 80px;
        border: 2px solid var(--neon-purple);
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        text-align: center;
        color: var(--neon-purple);
        font-family: 'IBM Plex Mono', monospace;
        font-size: 1.8rem;
        box-shadow: 0 0 22px rgba(123,92,255,0.55);
        background: rgba(123,92,255,0.06);
    }

    /* ---------------- Section headings: neon underline ---------------- */
    .section-label {
        font-family: 'Orbitron', sans-serif;
        font-weight: 700;
        font-size: 1.1rem;
        color: var(--ink);
        margin-top: 2.4rem;
        margin-bottom: 0.9rem;
        padding-bottom: 0.35rem;
        border-bottom: 1px solid var(--rule);
        position: relative;
        letter-spacing: 0.02em;
    }

    .section-label .icon {
        margin-right: 0.5rem;
        filter: drop-shadow(0 0 6px rgba(51,214,255,0.8));
    }

    .section-label::after {
        content: "";
        position: absolute;
        left: 0;
        bottom: -3px;
        width: 46px;
        height: 2px;
        background: linear-gradient(90deg, var(--neon-cyan), var(--neon-purple));
        box-shadow: 0 0 8px rgba(51,214,255,0.8);
    }

    /* ---------------- Metrics: HUD tile ---------------- */
    [data-testid="stMetric"] {
        background-color: var(--card);
        border: 1px solid var(--rule);
        border-top: 2px solid var(--neon-cyan);
        padding: 1rem 1rem 0.85rem;
        box-shadow: 0 0 16px rgba(51,214,255,0.08) inset;
    }

    [data-testid="stMetricLabel"] {
        font-family: 'IBM Plex Mono', monospace;
        font-size: 0.72rem;
        color: var(--slate);
        text-transform: none;
        letter-spacing: 0.02em;
    }

    [data-testid="stMetricValue"] {
        font-family: 'Orbitron', sans-serif;
        font-weight: 700;
        color: var(--neon-cyan);
        text-shadow: 0 0 10px rgba(51,214,255,0.6);
    }

    /* ---------------- Inputs ---------------- */
    div[data-baseweb="select"], .stTextInput input {
        font-family: 'IBM Plex Mono', monospace;
        background-color: var(--card) !important;
        border: 1px solid var(--rule) !important;
        color: var(--ink) !important;
        border-radius: 3px !important;
    }

    div[data-baseweb="select"]:focus-within, .stTextInput input:focus {
        border-color: var(--neon-cyan) !important;
        box-shadow: 0 0 10px rgba(51,214,255,0.4) !important;
    }

    div[data-baseweb="select"] * {
        color: var(--ink) !important;
    }

    div[data-baseweb="popover"] {
        background-color: var(--card) !important;
    }

    ul[role="listbox"] {
        background-color: var(--card) !important;
        border: 1px solid var(--rule) !important;
    }

    li[role="option"]:hover {
        background-color: var(--paper) !important;
    }

    .stTextInput input::placeholder {
        color: var(--slate) !important;
        opacity: 0.7;
    }

    .stTextInput label, .stSelectbox label {
        color: var(--neon-cyan) !important;
        font-family: 'IBM Plex Mono', monospace;
    }

    .stDataFrame {
        font-family: 'IBM Plex Mono', monospace;
        border: 1px solid var(--rule);
    }

    [data-testid="stDataFrame"] {
        background-color: var(--card);
    }

    [data-testid="stDataFrame"] div {
        color: var(--ink);
    }

    [data-testid="stElementToolbar"] {
        background-color: var(--card);
    }

    section[data-testid="stSidebar"] {
        background-color: var(--card);
        border-right: 1px solid var(--neon-cyan);
        box-shadow: 4px 0 20px rgba(51,214,255,0.08);
    }

    section[data-testid="stSidebar"] h3 {
        font-family: 'Orbitron', sans-serif;
        font-weight: 600;
        color: var(--neon-cyan);
    }

    div[data-testid="stAlert"] {
        background-color: var(--card);
        border: 1px solid var(--rule);
        color: var(--ink);
    }
</style>
""", unsafe_allow_html=True)


# Header

st.markdown("""
<div class="case-header-wrap">
    <div class="folder-tab">Case No. TF-0001</div>
    <div class="case-header">
        <div>
            <h1 class="case-title">🛰️ ThreatLens</h1>
            <div class="case-tagline">An OSINT Threat Intelligence Dashboard</div>
            <div class="subtitle">Malicious IPs, domains and URLs, pulled live from ThreatFox by abuse.ch.</div>
        </div>
        <div class="stamp">🛡️</div>
    </div>
</div>
""", unsafe_allow_html=True)

if not os.path.exists(DATA_FILE):
    st.error("No data found. Run fetch_data.py first, then refresh this page.")
    st.stop()

df = pd.read_csv(DATA_FILE)

if df.empty:
    st.warning("The data file is empty. Try running fetch_data.py again.")
    st.stop()

# Sidebar filter

st.sidebar.markdown("### 🔧 Filters")
ioc_types = ["All"] + sorted(df["type"].dropna().unique().tolist())
selected_type = st.sidebar.selectbox("Indicator type", ioc_types)

if selected_type != "All":
    df = df[df["type"] == selected_type]

# Summary metrics

col1, col2, col3 = st.columns(3)
col1.metric("TOTAL INDICATORS", len(df))
col2.metric("UNIQUE TYPES", df["type"].nunique())
col3.metric("UNIQUE THREATS", df["threat_type"].nunique() if "threat_type" in df.columns else 0)

# Search

st.markdown("<div class='section-label'><span class='icon'>🔍</span>Indicator Lookup</div>", unsafe_allow_html=True)
search_term = st.text_input("Enter an IP, domain, or URL")

if search_term:
    match = df[df["indicator"].astype(str).str.contains(search_term, case=False, na=False)]
    if not match.empty:
        st.error(f"⚠️ Match found — {len(match)} record(s) present in threat feed.")
        st.dataframe(match, use_container_width=True)
    else:
        st.success("✅ No match found in current threat feed.")

# Full table

st.markdown("<div class='section-label'><span class='icon'>🗂️</span>Full Indicator List</div>", unsafe_allow_html=True)
st.dataframe(df, use_container_width=True)

# Charts

st.markdown("<div class='section-label'><span class='icon'>📊</span>Distribution</div>", unsafe_allow_html=True)

chart_template = dict(
    layout=dict(
        paper_bgcolor="#0B1830",
        plot_bgcolor="#0B1830",
        font=dict(family="IBM Plex Mono", color="#E6F6FF", size=13),
        title=dict(font=dict(family="Orbitron", color="#E6F6FF", size=16)),
        legend=dict(
            font=dict(family="IBM Plex Mono", color="#E6F6FF", size=12),
            bgcolor="rgba(0,0,0,0)",
        ),
        xaxis=dict(
            title=dict(font=dict(color="#E6F6FF")),
            tickfont=dict(color="#7FA8C9"),
            gridcolor="#1B3A5C",
            linecolor="#1B3A5C",
            zerolinecolor="#1B3A5C",
        ),
        yaxis=dict(
            title=dict(font=dict(color="#E6F6FF")),
            tickfont=dict(color="#7FA8C9"),
            gridcolor="#1B3A5C",
            linecolor="#1B3A5C",
            zerolinecolor="#1B3A5C",
        ),
        colorway=["#33D6FF", "#7B5CFF", "#FF4FD8", "#5FE8C6", "#9FD1FF", "#B08CFF"],
    )
)

chart_col1, chart_col2 = st.columns(2)

with chart_col1:
    type_counts = df["type"].value_counts().reset_index()
    type_counts.columns = ["type", "count"]
    fig1 = px.pie(type_counts, names="type", values="count", title="🌐 By indicator type", hole=0.5)
    fig1.update_layout(chart_template["layout"])
    fig1.update_traces(textfont=dict(color="#050B18", size=13, family="IBM Plex Mono"))
    st.plotly_chart(fig1, use_container_width=True)

with chart_col2:
    if "threat_type" in df.columns:
        threat_counts = df["threat_type"].value_counts().reset_index().head(10)
        threat_counts.columns = ["threat_type", "count"]
        fig2 = px.bar(threat_counts, x="threat_type", y="count", title="🧬 Top threat categories")
        fig2.update_layout(chart_template["layout"])
        fig2.update_traces(marker_color="#33D6FF")
        st.plotly_chart(fig2, use_container_width=True)
