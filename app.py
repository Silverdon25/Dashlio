# ------------------------------------------------------------
# SmartDash – Data Dashboard Builder
# Copyright (c) 2025 Mr. Devon Wildman
# All rights reserved.
#
# Unauthorized copying, modification, or distribution of this
# software, via any medium, is strictly prohibited.
# Proprietary and confidential.
# ------------------------------------------------------------
import streamlit as st
import pandas as pd
import plotly.express as px

# --- PAGE CONFIG ---
st.set_page_config(page_title="SmartDash - Data Dashboard Builder", page_icon="📊", layout="wide")

# --- HEADER SECTION ---
st.markdown("""
<h1 style='text-align: center; color: #2E86C1;'>📊 SmartDash</h1>
<p style='text-align: center; color: gray;'>Upload your data file to generate instant insights and visual dashboards.</p>
<hr>
""", unsafe_allow_html=True)

# --- SIDEBAR ---
st.sidebar.header("⚙️ Controls")
st.sidebar.info("Select chart options after uploading your data.")

# --- FILE UPLOAD SECTION ---
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

        # --- SUMMARY STATS ---
        with st.expander("📈 View Summary Statistics"):
            st.write(df.describe())

        # --- VISUALISATION SECTION ---
        st.subheader("📊 Data Visualisation")

        # Dropdowns in sidebar
        numeric_cols = df.select_dtypes(include=['float', 'int']).columns.tolist()
        all_cols = df.columns.tolist()

        if len(numeric_cols) > 0:
            x_axis = st.sidebar.selectbox("Select X-axis", options=all_cols)
            y_axis = st.sidebar.selectbox("Select Y-axis", options=numeric_cols)
            chart_type = st.sidebar.selectbox("Select Chart Type", ["Bar", "Line", "Scatter", "Pie"])

            if chart_type == "Bar":
                fig = px.bar(df, x=x_axis, y=y_axis, title=f"{y_axis} by {x_axis}")
            elif chart_type == "Line":
                fig = px.line(df, x=x_axis, y=y_axis, title=f"{y_axis} over {x_axis}")
            elif chart_type == "Scatter":
                fig = px.scatter(df, x=x_axis, y=y_axis, title=f"{y_axis} vs {x_axis}")
            elif chart_type == "Pie":
                fig = px.pie(df, names=x_axis, values=y_axis, title=f"{y_axis} distribution")

            st.plotly_chart(fig, use_container_width=True)

        else:
            st.warning("⚠️ No numerical columns found. Please upload a dataset with numbers.")

        # --- DOWNLOAD SECTION ---
        st.subheader("📥 Export Options")
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button("Download Cleaned Data (CSV)", csv, "cleaned_data.csv", "text/csv")

    except Exception as e:
        st.error(f"⚠️ Error reading file: {e}")

else:
    st.info("👆 Please upload a file to get started.")

# --- FOOTER ---
st.markdown("""
<hr>
<p style='text-align: center; color: gray;'>© 2025 SmartDash | Designed by Mr. Wildman</p>
""", unsafe_allow_html=True)

