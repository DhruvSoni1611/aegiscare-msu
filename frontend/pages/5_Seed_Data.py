import streamlit as st
import pandas as pd
from utils.styling import apply_custom_css
from components.navbar import render_navbar
from utils.data import generate_sample_patients
from utils.analysis import analyze_vitals_trends
from datetime import datetime

apply_custom_css()
st.markdown('<h1 class="main-header">Healthcare Analytics Dashboard</h1>',
            unsafe_allow_html=True)
render_navbar()

st.header("👥 Seed Patients Management")
st.write("Manage and configure sample patient data for testing and demonstration.")

tab1, tab2, tab3 = st.tabs(
    ["Current Patients", "Generate New Data", "Export Data"])

with tab1:
    st.subheader("Current Patient Database")

    patient_summary = []
    for pid, patient in st.session_state.patients_data.items():
        latest_vitals = patient['vitals'].iloc[-1]
        trends = analyze_vitals_trends(patient['vitals'])
        patient_summary.append({
            'Patient ID': pid,
            'Name': patient['name'],
            'Age': patient['age'],
            'Gender': patient['gender'],
            'Condition': patient['condition'],
            'Heart Rate': f"{latest_vitals['heart_rate']:.0f} bpm",
            'BP': f"{latest_vitals['blood_pressure_sys']:.0f}/{latest_vitals['blood_pressure_dia']:.0f}",
            'Temperature': f"{latest_vitals['temperature']:.1f}°F",
            'O2 Sat': f"{latest_vitals['oxygen_saturation']:.0f}%",
            'Status': '🔴' if any(v['status'] in ['HIGH', 'LOW'] for v in trends.values()) else '🟢',
        })

    summary_df = pd.DataFrame(patient_summary)
    st.dataframe(summary_df, use_container_width=True)

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Patients", len(patient_summary))
    with col2:
        critical_count = len(
            [p for p in patient_summary if p['Status'] == '🔴'])
        st.metric("Critical Status", critical_count)
    with col3:
        conditions = [p['condition']
                      for p in st.session_state.patients_data.values()]
        unique_conditions = len(set(conditions))
        st.metric("Unique Conditions", unique_conditions)

with tab2:
    st.subheader("Generate New Patient Data")
    col1, col2 = st.columns(2)

    with col1:
        num_patients = st.number_input(
            "Number of patients to generate", min_value=1, max_value=100, value=10)
        if st.button("Generate Patients", type="primary"):
            with st.spinner("Generating new patient data..."):
                new_patients = generate_sample_patients(num_patients)
                current_count = len(st.session_state.patients_data)
                for i, (_, patient_data) in enumerate(new_patients.items()):
                    new_id = f"PT{str(current_count + i + 1).zfill(4)}"
                    st.session_state.patients_data[new_id] = patient_data
            st.success(f"Successfully generated {num_patients} new patients!")
            st.rerun()

    with col2:
        st.info(
            """
            *Generation Features:*
            - Realistic vital signs patterns
            - Age and gender distribution
            - Common medical conditions
            - 30 days of historical data
            - Clinical notes samples
            """
        )

with tab3:
    st.subheader("Export Patient Data")
    col1, col2 = st.columns(2)

    with col1:
        if st.button("Export Summary CSV"):
            summary_df = pd.DataFrame(patient_summary)
            csv = summary_df.to_csv(index=False)
            st.download_button(
                label="Download CSV",
                data=csv,
                file_name=f"patient_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv",
            )

    with col2:
        selected_export_patient = st.selectbox(
            "Select Patient for Detailed Export",
            options=list(st.session_state.patients_data.keys()),
            format_func=lambda x: f"{x} - {st.session_state.patients_data[x]['name']}",
        )
        if selected_export_patient and st.button("Export Patient Vitals"):
            patient_vitals = st.session_state.patients_data[selected_export_patient]['vitals']
            csv = patient_vitals.to_csv(index=False)
            st.download_button(
                label="Download Patient Vitals CSV",
                data=csv,
                file_name=f"vitals_{selected_export_patient}{datetime.now().strftime('%Y%m%d%H%M%S')}.csv",
                mime="text/csv",
            )
