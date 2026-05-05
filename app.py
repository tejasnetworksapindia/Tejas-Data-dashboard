import streamlit as st
import pandas as pd
import plotly.express as px

# Webpage setup
st.set_page_config(layout="wide", page_title="Tejas RAN Analyzer")

st.markdown("""
    <style>
    .report-title { font-size:28px !important; font-weight: bold; color: #1E3A8A; }
    </style>
    """, unsafe_allow_html=True)

st.markdown('<p class="report-title">📡 Tejas RAN Performance Dashboard</p>', unsafe_allow_html=True)

# Helper function to read multiple files (CSV or Excel)
def load_and_combine_data(uploaded_files):
    all_data = []
    if uploaded_files:
        for file in uploaded_files:
            try:
                # Format check
                df = pd.read_csv(file) if file.name.endswith('.csv') else pd.read_excel(file)
                all_data.append(df)
            except Exception as e:
                st.error(f"Error loading {file.name}: {e}")
        if all_data:
            return pd.concat(all_data, ignore_index=True)
    return None

# --- SIDEBAR ---
with st.sidebar:
    st.header("📂 Reports Upload")
    file_kpi_list = st.file_uploader("Upload KPI Reports (Multiple Days)", type=['xlsx', 'csv'], accept_multiple_files=True)
    file_alarm = st.file_uploader("Upload Active Alarm Report", type=['xlsx', 'csv'])
    st.info("💡 Tip: Use Ctrl to select multiple KPI files.")

# --- SMART SEARCH BAR ---
search_site = st.text_input("🔍 Search Site (e.g., AT2001)", "").strip().upper()

if search_site and file_kpi_list:
    df_kpi = load_and_combine_data(file_kpi_list)
    
    if df_kpi is not None:
        # 🟢 SMART FILTER: Contains search_site (Partial Match)
        df_kpi['Site Id'] = df_kpi['Site Id'].astype(str)
        site_data = df_kpi[df_kpi['Site Id'].str.contains(search_site, case=False, na=False)]

        if not site_data.empty:
            # 📊 TRAFFIC SECTION (50%)
            st.subheader(f"📊 Traffic Analysis: {search_site} (All Bands & Cells)")
            
            # Sort data by Date and Cell Name
            site_data = site_data.sort_values(by=['Date', '4G Cell Name'])

            fig_traffic = px.bar(
                site_data, 
                x='4G Cell Name', 
                y='Data Volume - Total (GB)', 
                color='Date',
                barmode='group',
                height=450,
                text_auto='.2f',
                title="Cell-wise Traffic Comparison"
            )
            st.plotly_chart(fig_traffic, use_container_width=True)

            st.divider()

            # --- BOTTOM SECTION (KPI 25% | ALARMS 25%) ---
            col_kpi, col_alarm = st.columns(2)
            
            with col_kpi:
                st.subheader("📉 RF KPI Parameters")
                kpi_cols = ['Date', '4G Cell Name', 'CSSR', 'RRC Connection Success Rate(All) (%)', 'ERAB Drop Rate - PS (%)']
                available_cols = [c for c in kpi_cols if c in site_data.columns]
                st.dataframe(site_data[available_cols].sort_values(by=['Date', '4G Cell Name'], ascending=[False, True]), use_container_width=True)

            with col_alarm:
                st.subheader("⚠️ HW Alarms & Faults")
                if file_alarm:
                    try:
                        df_al = pd.read_csv(file_alarm) if file_alarm.name.endswith('.csv') else pd.read_excel(file_alarm)
                        # Alarm file lo kuda Site Id filter
                        site_al = df_al[df_al.astype(str).apply(lambda x: x.str.contains(search_site, case=False, na=False)).any(axis=1)]
                        if not site_al.empty:
                            st.dataframe(site_al, use_container_width=True)
                        else:
                            st.success(f"No active alarms for {search_site} ✅")
                    except:
                        st.error("Error reading Alarm file.")
                else:
                    st.info("Upload Alarm report to see faults.")
        else:
            st.error(f"Site '{search_site}' not found in the uploaded data.")
else:
    st.warning("👈 Please upload the KPI files and enter a Site ID.")
