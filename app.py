# ------------------------------------------------------------
# Dashlio — Data Dashboard Builder
# Production build (no legacy SmartDash references)
# ------------------------------------------------------------

from __future__ import annotations

import os
from dataclasses import dataclass

import pandas as pd
import plotly.express as px
import streamlit as st


# -----------------------------
# Customer / Tier settings
# -----------------------------
@dataclass(frozen=True)
class Plan:
    name: str
    max_rows: int
    max_cols: int
    max_upload_mb: int
    export_enabled: bool
    branding_locked: bool  # if True, show "Powered by Dashlio" and prevent hiding branding


PLANS = {
    "free": Plan(name="Free", max_rows=25_000, max_cols=50, max_upload_mb=10, export_enabled=False, branding_locked=True),
    "pro": Plan(name="Pro", max_rows=250_000, max_cols=200, max_upload_mb=50, export_enabled=True, branding_locked=False),
    "business": Plan(name="Business", max_rows=2_000_000, max_cols=500, max_upload_mb=200, export_enabled=True, branding_locked=False),
}

# Set your tier in Streamlit Secrets as TIER=free/pro/business
TIER = (st.secrets.get("TIER", "free") if hasattr(st, "secrets") else "free").lower().strip()
PLAN = PLANS.get(TIER, PLANS["free"])

APP_NAME = "Dashlio"

# If you upload a logo file to the repo, set the filename here
LOGO_FILE = "logo.png"  # put your new Dashlio logo in the repo with this exact name


# -----------------------------
# Page config (must be first Streamlit call)
# -----------------------------
page_icon = "📊"
if os.path.exists(LOGO_FILE):
    page_icon = LOGO_FILE

st.set_page_config(
    page_title=f"{APP_NAME} — Data Dashboard",
    page_icon=page_icon,
    layout="centered",
    initial_sidebar_state="expanded",
)

# -----------------------------
# Minimal clean styling
# -----------------------------
st.markdown(
    """
    <style>
      .main .block-container { padding-top: 1.25rem; padding-left: 1rem; padding-right: 1rem; max-width: 980px; }
      h1,h2,h3 { margin: 0.25rem 0 0.5rem 0; }
      .dashlio-muted { color: #6b7280; font-size: 0.95rem; }
      .dashlio-pill { display:inline-block; padding:0.2rem 0.55rem; border:1px solid #e5e7eb; border-radius:999px; font-size:0.85rem; }
      @media (prefers-color-scheme: dark) {
        body, .main { background: #0e1117 !important; color: #e6e6e6 !important; }
        .dashlio-pill { border-color:#334155; }
      }
    </style>
    """,
    unsafe_allow_html=True,
)

# -----------------------------
# Header (no fragile HTML mixing)
# -----------------------------
col1, col2 = st.columns([1, 3], vertical_alignment="center")
with col1:
    if os.path.exists(LOGO_FILE):
        st.image(LOGO_FILE, width=160)
with col2:
    st.title(APP_NAME)
    st.caption("Upload a dataset, preview it, and generate charts instantly.")

st.markdown(f"<span class='dashlio-pill'>Plan: {PLAN.name}</span>", unsafe_allow_html=True)
st.divider()

# -----------------------------
# Sidebar (pricing + limits + upgrade)
# -----------------------------
with st.sidebar:
    st.header("Account")
    st.write(f"**Current plan:** {PLAN.name}")
    st.write("**Limits:**")
    st.write(f"- Upload size: up to **{PLAN.max_upload_mb} MB**")
    st.write(f"- Rows: up to **{PLAN.max_rows:,}**")
    st.write(f"- Columns: up to **{PLAN.max_cols:,}**")
    st.write(f"- Export: **{'Enabled' if PLAN.export_enabled else 'Locked'}**")

    st.divider()
    st.subheader("Pricing")
    st.write("**Free** — basic charts, no export, branding locked")
    st.write("**Pro** — exports + higher limits")
    st.write("**Business** — highest limits + team use")

    st.divider()
    st.subheader("Chart Settings")
    chart_type = st.selectbox("Chart type", ["Bar", "Line", "Scatter", "Pie"], index=0)

# -----------------------------
# Helpers
# -----------------------------
def apply_plot_theme(fig):
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=10, r=10, t=30, b=10),
    )
    return fig


def read_uploaded_file(uploaded_file) -> pd.DataFrame:
    name = uploaded_file.name.lower()
    if name.endswith(".csv"):
        return pd.read_csv(uploaded_file)
    if name.endswith(".xlsx") or name.endswith(".xls"):
        return pd.read_excel(uploaded_file)
    raise ValueError("Unsupported file type. Please upload a CSV or Excel file.")


# -----------------------------
# Upload
# -----------------------------
uploaded_file = st.file_uploader("Upload a CSV or Excel file", type=["csv", "xlsx", "xls"])

if not uploaded_file:
    st.info("Upload a file to begin.")
else:
    # Basic upload size check (Streamlit also enforces server limits)
    # This is a soft guard for customer messaging.
    try:
        file_size_mb = (uploaded_file.size or 0) / (1024 * 1024)
        if file_size_mb > PLAN.max_upload_mb:
            st.error(f"This file is {file_size_mb:.1f} MB. Your plan allows up to {PLAN.max_upload_mb} MB.")
            st.stop()
    except Exception:
        pass

    try:
        df = read_uploaded_file(uploaded_file)

        # Enforce plan limits
        if df.shape[0] > PLAN.max_rows:
            st.error(f"Your dataset has {df.shape[0]:,} rows. Your plan allows up to {PLAN.max_rows:,}.")
            st.stop()
        if df.shape[1] > PLAN.max_cols:
            st.error(f"Your dataset has {df.shape[1]:,} columns. Your plan allows up to {PLAN.max_cols:,}.")
            st.stop()

        st.subheader("Preview")
        st.dataframe(df.head(50), use_container_width=True)

        with st.expander("Summary statistics"):
            st.write(df.describe(include="all"))

        st.subheader("Visualisation")

        all_cols = df.columns.tolist()
        numeric_cols = df.select_dtypes(include=["number"]).columns.tolist()

        if not numeric_cols:
            st.warning("No numeric columns found. Upload a dataset with at least one numeric column.")
            st.stop()

        x_axis = st.selectbox("X-axis", all_cols, index=0)
        y_axis = st.selectbox("Y-axis", numeric_cols, index=0)

        if chart_type == "Bar":
            fig = px.bar(df, x=x_axis, y=y_axis)
        elif chart_type == "Line":
            fig = px.line(df, x=x_axis, y=y_axis)
        elif chart_type == "Scatter":
            fig = px.scatter(df, x=x_axis, y=y_axis)
        else:
            fig = px.pie(df, names=x_axis, values=y_axis)

        st.plotly_chart(apply_plot_theme(fig), use_container_width=True)

        st.divider()
        st.subheader("Export")

        if not PLAN.export_enabled:
            st.warning("Export is locked on the Free plan. Upgrade to Pro to download cleaned data.")
        else:
            csv_bytes = df.to_csv(index=False).encode("utf-8")
            st.download_button(
                "Download CSV",
                data=csv_bytes,
                file_name="dashlio_export.csv",
                mime="text/csv",
            )

    except Exception as e:
        st.error(f"Error: {e}")

# -----------------------------
# Footer (branding lock)
# -----------------------------
st.divider()

if PLAN.branding_locked:
    st.caption("Powered by Dashlio")
else:
    st.caption("Dashlio")

st.caption("© 2025 Dashlio. All rights reserved.")

