import streamlit as st
import pandas as pd
import plotly.express as px

# Webpage setup
st.set_page_config(layout="wide", page_title="Tejas Traffic Analyzer")

# Custom Styling
st.markdown("""
    <style>
    .report-title { font-size:28px !important; font-weight: bold; color: #1E3A8A; }
    </style>
    """, unsafe_allow_html=True)

st.markdown('<p class="report-title">📡 RAN Network Performance Dashboard</p>', unsafe_allow_html=True)

# Helper function to read multiple files (CSV or Excel)
def load_and_combine_data(uploaded_files):
    all_data = []
    if uploaded_files:
        for file in uploaded_files:
            try:
                if file.name.endswith('.csv'):
                    df = pd.read_csv(file)
                else:
                    df = pd.read_excel(file)
                all_data.append(df)
            except Exception as e:
                st.error(f"Error loading {file.name}: {e}")
        if all_data:
            return pd.concat(all_data, ignore_index=True)
    return None

# --- SIDEBAR: Upload Section ---
with st.sidebar:
    st.header("📂 Upload Daily Reports")
    # accept_multiple_files=True add chesam maama
    file_kpi_list = st.file_uploader("Upload KPI Reports (4 Days)", type=['xlsx', 'csv'], accept_multiple_files=True)
    file_alarm = st.file_uploader("Upload Active Alarms", type=['xlsx', 'csv'])
    file_fm = st.file_uploader("Upload FM Report", type=['xlsx', 'csv'])
    file_vswr = st.file_uploader("Upload VSWR Report", type=['xlsx', 'csv'])
    
    st.info("💡 Tip: Select all 4 KPI files at once using Ctrl key.")

# --- SEARCH BAR ---
search_site = st.text_input("🔍 Search Site ID (e.g., AP_VJY_1234)", "").strip()

if search_site and file_kpi_list:
    # Multiple files ni combine chesthunnam
    df_kpi = load_and_combine_data(file_kpi_list)
    
    if df_kpi is not None:
        # Filter Data for Specific Site
        site_data = df_kpi[df_kpi['Site Id'] == search_site]

        if not site_data.empty:
            # --- 1. TRAFFIC SECTION (50%) ---
            st.subheader("📊 Multi-Day Traffic Comparison")
            
            # Date wise bar chart ready!
            fig_traffic = px.bar(
                site_data, 
                x='4G Cell Name', 
                y='Data Volume - Total (GB)', 
                color='Date',
                barmode='group',
                height=450,
                text_auto='.2f'
            )
            st.plotly_chart(fig_traffic, use_container_width=True)

            st.divider()

            # --- 2. BOTTOM SECTION (KPI & ALARMS) ---
            col_kpi, col_alarm = st.columns(2)
            with col_kpi:
                st.subheader("📉 RF KPI Parameters")
                kpi_cols = ['Date', '4G Cell Name', 'CSSR', 'RRC Connection Success Rate(All) (%)', 'ERAB Drop Rate - PS (%)']
                available_cols = [c for c in kpi_cols if c in site_data.columns]
                st.dataframe(site_data[available_cols].sort_values(by='Date', ascending=False), use_container_width=True)

            with col_alarm:
                st.subheader("⚠️ HW Alarms & Faults")
                if file_alarm:
                    # Single alarm file logic
                    df_al = pd.read_excel(file_alarm) if file_alarm.name.endswith('.xlsx') else pd.read_csv(file_alarm)
                    site_al = df_al[df_al.astype(str).apply(lambda x: search_site in x.values, axis=1)]
                    st.dataframe(site_al, use_container_width=True)
        else:
            st.error(f"Site ID {search_site} not found!")
else:
    st.warning("👈 Please upload the KPI files and enter a Site ID.")
