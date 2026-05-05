import streamlit as st
import pandas as pd
import plotly.express as px

# Webpage setup
st.set_page_config(layout="wide", page_title="Tejas Traffic Analyzer")

# Custom Styling
st.markdown("""
    <style>
    .report-title { font-size:28px !important; font-weight: bold; color: #1E3A8A; }
    .stDataFrame { border: 1px solid #e6e9ef; }
    </style>
    """, unsafe_allow_html=True)

st.markdown('<p class="report-title">📡 RAN Network Performance Dashboard</p>', unsafe_allow_html=True)

# Helper function to read both CSV and Excel
def load_data(uploaded_file):
    if uploaded_file is not None:
        try:
            if uploaded_file.name.endswith('.csv'):
                return pd.read_csv(uploaded_file)
            else:
                return pd.read_excel(uploaded_file)
        except Exception as e:
            st.error(f"Error loading {uploaded_file.name}: {e}")
    return None

# --- SIDEBAR: Upload Section ---
with st.sidebar:
    st.header("📂 Upload Daily Reports")
    # type list lo csv kuda add chesam maama
    file_kpi = st.file_uploader("Upload KPI Report", type=['xlsx', 'csv'])
    file_alarm = st.file_uploader("Upload Active Alarms", type=['xlsx', 'csv'])
    file_fm = st.file_uploader("Upload FM Report", type=['xlsx', 'csv'])
    file_vswr = st.file_uploader("Upload VSWR Report", type=['xlsx', 'csv'])
    
    st.info("Note: Upload reports with 'Date' and 'Site Id' columns. Supports .xlsx and .csv")

# --- SEARCH BAR ---
search_site = st.text_input("🔍 Search Site ID (e.g., AP_VJY_1234)", "").strip()

if search_site and file_kpi:
    # CSV or Excel load chesthunnam
    df_kpi = load_data(file_kpi)
    
    if df_kpi is not None:
        # Filter Data for Specific Site
        site_data = df_kpi[df_kpi['Site Id'] == search_site]

        if not site_data.empty:
            # --- 1. TRAFFIC SECTION (50% Page Height) ---
            st.subheader("📊 Traffic Analysis (Last 3 Days Comparison)")
            
            fig_traffic = px.bar(
                site_data, 
                x='4G Cell Name', 
                y='Data Volume - Total (GB)', 
                color='Date',
                barmode='group',
                height=400,
                text_auto='.2f'
            )
            st.plotly_chart(fig_traffic, use_container_width=True)

            st.divider()

            # --- 2. BOTTOM SECTION (25% KPI | 25% ALARMS) ---
            col_kpi, col_alarm = st.columns([1, 1])

            with col_kpi:
                st.subheader("📉 RF KPI Parameters")
                kpi_cols = ['Date', '4G Cell Name', 'CSSR', 'RRC Connection Success Rate(All) (%)', 'ERAB Drop Rate - PS (%)']
                # Check if columns exist before showing
                available_cols = [c for c in kpi_cols if c in site_data.columns]
                st.dataframe(site_data[available_cols].sort_values(by='Date', ascending=False), use_container_width=True)

            with col_alarm:
                st.subheader("⚠️ HW Alarms & Faults")
                
                # Active Alarms logic (Supports CSV/Excel)
                if file_alarm:
                    df_al = load_data(file_alarm)
                    if df_al is not None:
                        site_al = df_al[df_al.astype(str).apply(lambda x: search_site in x.values, axis=1)]
                        if not site_al.empty:
                            st.write("Active Alarms Found:")
                            st.dataframe(site_al, use_container_width=True)
                        else:
                            st.success("No Active Alarms Found!")
                
                # VSWR Alarms logic (Supports CSV/Excel)
                if file_vswr:
                    df_vs = load_data(file_vswr)
                    if df_vs is not None:
                        site_vs = df_vs[df_vs.astype(str).apply(lambda x: search_site in x.values, axis=1)]
                        if not site_vs.empty:
                            st.warning("VSWR Issues Detected!")
                            st.dataframe(site_vs, use_container_width=True)
        else:
            st.error(f"Site ID {search_site} not found in the uploaded KPI report.")
else:
    st.warning("👈 Please upload the KPI file and enter a Site ID to see the flow.")

