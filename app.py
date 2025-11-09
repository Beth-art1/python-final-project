# app.py - Minimal Smart Water MVP (Streamlit)
# Save this file in your project folder and create a subfolder named "data"
# Required: pip install streamlit pandas matplotlib seaborn

import streamlit as st
import pandas as pd
import os
from pathlib import Path
import matplotlib.pyplot as plt
import seaborn as sns
import datetime
import json

sns.set_style("whitegrid")
st.set_page_config("Smart Water MVP", layout="wide")

DATA_DIR = Path("data")
USAGE_CSV = DATA_DIR / "water_usage.csv"
QUALITY_CSV = DATA_DIR / "water_quality.csv"

# Ensure data folder exists
DATA_DIR.mkdir(exist_ok=True)

# Initialize CSVs if missing
if not USAGE_CSV.exists():
    pd.DataFrame(columns=["date", "household", "liters"]).to_csv(USAGE_CSV, index=False)
if not QUALITY_CSV.exists():
    pd.DataFrame(columns=["date", "household", "pH"]).to_csv(QUALITY_CSV, index=False)

st.title("💧 Smart Water — Minimal MVP")
st.write("Track household water usage, record water quality (pH), and view nearby clean water sources.")

# --- Sidebar: Input forms ---
st.sidebar.header("Record data")

with st.sidebar.form("usage_form", clear_on_submit=True):
    st.write("Add daily water usage (liters)")
    household = st.text_input("Household name", value="Household A")
    date_input = st.date_input("Date", value=datetime.date.today())
    liters = st.number_input("Liters used", min_value=0.0, step=0.1, format="%.1f")
    submitted = st.form_submit_button("Save usage")
    if submitted:
        df_u = pd.read_csv(USAGE_CSV)
        new = {"date": date_input.isoformat(), "household": household, "liters": liters}
        df_u = pd.concat([df_u, pd.DataFrame([new])], ignore_index=True)
        df_u.to_csv(USAGE_CSV, index=False)
        st.success("✅ Usage saved")

with st.sidebar.form("quality_form", clear_on_submit=True):
    st.write("Record a water quality reading (pH)")
    household_q = st.text_input("Household name for reading", value="Household A")
    date_q = st.date_input("Reading date", value=datetime.date.today(), key="qdate")
    ph = st.number_input("pH value (0-14)", min_value=0.0, max_value=14.0, step=0.1, format="%.1f")
    submitted_q = st.form_submit_button("Save quality")
    if submitted_q:
        df_q = pd.read_csv(QUALITY_CSV)
        newq = {"date": date_q.isoformat(), "household": household_q, "pH": ph}
        df_q = pd.concat([df_q, pd.DataFrame([newq])], ignore_index=True)
        df_q.to_csv(QUALITY_CSV, index=False)
        st.success("✅ Water quality saved")

# --- Main area: Load and display data ---
st.header("Recent Data")

try:
    df_usage = pd.read_csv(USAGE_CSV, parse_dates=["date"])
    st.subheader("Water usage (most recent entries)")
    st.dataframe(df_usage.sort_values("date", ascending=False).head(10))
except Exception as e:
    st.error(f"Could not read usage data: {e}")
    df_usage = pd.DataFrame(columns=["date", "household", "liters"])

try:
    df_quality = pd.read_csv(QUALITY_CSV, parse_dates=["date"])
    st.subheader("Water quality readings (pH)")
    st.dataframe(df_quality.sort_values("date", ascending=False).head(10))
except Exception as e:
    st.error(f"Could not read quality data: {e}")
    df_quality = pd.DataFrame(columns=["date", "household", "pH"])

# --- Visualization: Usage trend per household ---
st.header("Usage Trends")
if not df_usage.empty:
    # convert date column to datetime if not already
    if df_usage["date"].dtype == "O":
        df_usage["date"] = pd.to_datetime(df_usage["date"], errors="coerce")

    households = df_usage["household"].unique().tolist()
    selected_household = st.selectbox("Choose household to view trend", households)
    df_h = df_usage[df_usage["household"] == selected_household].sort_values("date")
    if not df_h.empty:
        fig, ax = plt.subplots(figsize=(8, 3.5))
        ax.plot(df_h["date"], df_h["liters"], marker="o")
        ax.set_title(f"Daily water usage — {selected_household}")
        ax.set_xlabel("Date")
        ax.set_ylabel("Liters")
        plt.xticks(rotation=45)
        st.pyplot(fig)
    else:
        st.info("No usage data for that household yet.")
else:
    st.info("No usage data recorded yet. Use the sidebar form to add entries.")

# --- Water quality status ---
st.header("Water Quality Status (pH)")
if not df_quality.empty:
    # show latest reading per household
    latest = df_quality.sort_values("date").groupby("household").last().reset_index()
    def ph_status(p):
        if p < 6.5 or p > 8.5:
            return "Unsafe"
        if 6.5 <= p < 7.0 or 8.0 < p <= 8.5:
            return "Warning"
        return "Safe"
    latest["status"] = latest["pH"].apply(ph_status)
    st.dataframe(latest[["household","date","pH","status"]])
    st.write("Status guide: Safe (6.5–8.0), Warning (6.0–6.5 or 8.0–8.5), Unsafe (<6.0 or >8.5)")
else:
    st.info("No water quality readings yet. Use the sidebar form to add a pH reading.")

# --- Map of sample clean water sources ---
st.header("Nearby Clean Water Sources (sample)")
# sample sources list (lat, lon, name)
sample_sources = [
    {"name": "Community Well - East", "lat": 1.2833, "lon": 36.8167},
    {"name": "Public Tap - Central", "lat": 1.2921, "lon": 36.8219},
    {"name": "Borehole - West", "lat": 1.2700, "lon": 36.8000},
]
# show as a dataframe with lat/lon columns for st.map
map_df = pd.DataFrame([{"lat": s["lat"], "lon": s["lon"], "name": s["name"]} for s in sample_sources])
st.map(map_df[["lat","lon"]])

# show list with names and small details
for s in sample_sources:
    st.write(f"• **{s['name']}** — coordinates: ({s['lat']}, {s['lon']})")

st.markdown("---")


