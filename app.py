# ------------------------------------------------------------
# Dashlio – Data Dashboard Builder
# Copyright (c) 2025
# Designed and Developed by Mr. Devon Wildman
# All rights reserved.
# ------------------------------------------------------------

import streamlit as st
from PIL import Image
import pandas as pd
import plotly.express as px

# ------------------------------------------------------------
# PAGE CONFIG (MUST COME BEFORE ANY STREAMLIT OUTPUT)
# ------------------------------------------------------------
st.set_page_config(page_title="Dashlio - Data Dashboard", page_icon="📊"

)

# ------------------------------------------------------------
# MOBILE VIEW FIXES + DARK MODE + CLEAN UI
# ------------------------------------------------------------
st.markdown("""
<style>

/* Make layout fit properly on mobile */
.main .block-container {
    padding-top: 1rem !important;
    padding-left: 0.7rem !important;
    padding-right: 0.7rem !important;
}

/* Responsive charts */
.css-1kyxreq {
    width: 100% !important;
}

/* Clean UI spacing */
h1, h2, h3, h4 {
    margin-top: 0.2rem;
    margin-bottom: 0.5rem;
}

/* DARK MODE (auto based on device settings) */
@media (prefers-color-scheme: dark) {
    body, .main {
        background-color: #0e1117 !important;
        color: #e6e6e6 !important;
    }
    .sidebar .sidebar-content {
        background-color: #11141c !important;
    }
    .stButton>button {
        background-color: #1f2937 !important;
        color: white !important;
        border: 1px solid #3b4252 !important;
    }
    .stDownloadButton>button {
        background-color: #1f2937 !important;
        color: white !important;
        border: 1px solid #3b4252 !important;
    }
}
</style>
""", unsafe_allow_html=True)

# Ensure proper mobile viewport scaling:
st.markdown("""
<script>
var meta = document.createElement('meta');
meta.name = "viewport";
meta.content = "width=device-width, initial-scale=1, user-scalable=no";
document.getElementsByTagName('head')[0].appendChild(meta);
</script>
""", unsafe_allow_html=True)

# ------------------------------------------------------------
# APPLY DARK MODE TO PLOTLY CHARTS
# ------------------------------------------------------------
def apply_dark_mode(fig):
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#e6e6e6")
    )
    return fig

# ------------------------------------------------------------
# HEADER + LOGO
# ------------------------------------------------------------
logo = "logo.png"
st.image(logo, width=360)

st.markdown("""
<h1 style='color:#2E86C1; text-align:center;'>📊 Dashlio</h1>
<p style='color:gray; text-align:center;'>Designed and Developed by Mr. Devon Wildman</p>
<hr>
""", unsafe_allow_html=True)

# ------------------------------------------------------------
# SIDEBAR
# ------------------------------------------------------------
st.sidebar.header("⚙️ Controls")
st.sidebar.info("Upload your dataset to enable chart options.")

# ------------------------------------------------------------
# FILE UPLOAD SECTION
# ------------------------------------------------------------
uploaded_file = st.file_uploader("📂 Upload a CSV or Excel file", type=["csv", "xlsx"])

if uploaded_file:
    try:
        # Load data
        if uploaded_file.name.endswith(".csv"):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)

        # --- DATA PREVIEW ---
        st.subheader("👀 Data Preview")
        st.dataframe(df.head())

        # --- SUMMARY ---
        with st.expander("📈 View Summary Statistics"):
            st.write(df.describe())

        # --- VISUALISATION ---
        st.subheader("📊 Data Visualisation")
        numeric_cols = df.select_dtypes(include=['float', 'int']).columns.tolist()
        all_cols = df.columns.tolist()

        if numeric_cols:
            x_axis = st.sidebar.selectbox("Select X-axis", all_cols)
            y_axis = st.sidebar.selectbox("Select Y-axis", numeric_cols)
            chart_type = st.sidebar.selectbox("Select Chart Type", ["Bar", "Line", "Scatter", "Pie"])

            # Generate chart
            if chart_type == "Bar":
                fig = px.bar(df, x=x_axis, y=y_axis)
            elif chart_type == "Line":
                fig = px.line(df, x=x_axis, y=y_axis)
            elif chart_type == "Scatter":
                fig = px.scatter(df, x=x_axis, y=y_axis)
            else:
                fig = px.pie(df, names=x_axis, values=y_axis)

            # Apply Dark Mode to chart
            fig = apply_dark_mode(fig)

            st.plotly_chart(fig, use_container_width=True)

        else:
            st.warning("⚠️ No numerical columns found. Please upload a dataset with numbers.")

        # --- DOWNLOAD CLEANED FILE ---
        st.subheader("📥 Export Options")
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button("Download Cleaned Data (CSV)", csv, "cleaned_data.csv", "text/csv")

    except Exception as e:
        st.error(f"⚠️ Error reading file: {e}")

else:
    st.info("👆 Please upload a file to begin.")

# ------------------------------------------------------------
# FOOTER
# ------------------------------------------------------------
st.markdown("""
<hr>
<p style='text-align: center; color: gray;'>© 2025 Dashlio | Designed by Mr. Wildman</p>
""", unsafe_allow_html=True)

