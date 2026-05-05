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

# Helper function for single file reading (CSV or Excel)
def load_single_file(uploaded_file):
    if uploaded_file is not None:
        try:
            return pd.read_csv(uploaded_file) if uploaded_file.name.endswith('.csv') else pd.read_excel(uploaded_file)
        except Exception as e:
            st.error(f"Error loading {uploaded_file.name}: {e}")
    return None

# --- SIDEBAR: Upload Section (Ikkada 4 options add chesam maama) ---
with st.sidebar:
    st.header("📂 Upload Daily Reports")
    file_kpi_list = st.file_uploader("1. KPI Reports (Multiple Days)", type=['xlsx', 'csv'], accept_multiple_files=True)
    file_alarm = st.file_uploader("2. Active Alarm Report", type=['xlsx', 'csv'])
    file_fm = st.file_uploader("3. FM Report", type=['xlsx', 'csv'])
    file_vswr = st.file_uploader("4. VSWR Alarm Report", type=['xlsx', 'csv'])
    
    st.info("💡 Tip: Select all 4 KPI files at once using Ctrl key.")

# --- SEARCH BAR ---
search_site = st.text_input("🔍 Search Site ID (e.g., AT2001)", "").strip()

if search_site and file_kpi_list:
    # KPI Files ni combine chesthunnam
    df_kpi = load_and_combine_data(file_kpi_list)
    
    if df_kpi is not None:
        # Smart Search logic
        df_kpi['Site Id'] = df_kpi['Site Id'].astype(str)
        site_data = df_kpi[df_kpi['Site Id'].str.contains(search_site, case=False, na=False)]

        if not site_data.empty:
            # --- 1. TRAFFIC SECTION (50%) ---
            st.subheader(f"📊 Multi-Day Traffic Comparison: {search_site}")
            
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
                st.subheader("⚠️ HW Alarms & Faults (Combined)")
                
                combined_alarms = []
                
                # Check 3 Alarm Files
                for label, f in [("Active", file_alarm), ("FM", file_fm), ("VSWR", file_vswr)]:
                    df = load_single_file(f)
                    if df is not None:
                        # Smart Search in Alarm Files
                        site_al = df[df.astype(str).apply(lambda x: x.str.contains(search_site, case=False, na=False)).any(axis=1)].copy()
                        if not site_al.empty:
                            site_al['Source'] = label # File source identify cheyataniki
                            combined_alarms.append(site_al)
                
                if combined_alarms:
                    final_alarms = pd.concat(combined_alarms, ignore_index=True)
                    st.dataframe(final_alarms, use_container_width=True)
                else:
                    st.success(f"No active alarms found for {search_site} in any report! ✅")
        else:
            st.error(f"Site ID {search_site} not found in KPI data!")
else:
    st.warning("👈 Please upload the KPI files and enter a Site ID to see the flow.")
