import streamlit as st
import pandas as pd
from utils.styling import apply_custom_css
from components.navbar import render_navbar
from utils.api import get, post
from datetime import datetime
import io

apply_custom_css()
st.markdown('<h1 class="main-header">Healthcare Analytics Dashboard</h1>',
            unsafe_allow_html=True)
render_navbar()

st.header("👥 Patient Data Management")
st.write("View and manage patient data, vital signs, and health metrics for heart disease analysis.")

# CSV Upload Section
st.subheader("📁 Upload Heart Disease Dataset")
upload_col1, upload_col2 = st.columns([3, 1])

with upload_col1:
    uploaded_file = st.file_uploader(
        "Choose a CSV file with heart disease data",
        type=['csv'],
        help="Upload the merged_heart_10k.csv file or similar heart disease dataset"
    )

with upload_col2:
    if uploaded_file is not None:
        if st.button("🚀 Process Data", type="primary"):
            try:
                # Read the file content
                file_content = uploaded_file.read()

                # Send to backend for processing
                files = {"f": (uploaded_file.name, file_content, "text/csv")}
                response = post("/uploads/csv", files=files)

                if response.ok:
                    result = response.json()
                    st.success(f"✅ Data processed successfully!")
                    st.info(f"• Rows parsed: {result.get('rows_parsed', 0)}")
                    st.info(f"• Rows loaded: {result.get('rows_loaded', 0)}")
                    st.info(
                        f"• Patients processed: {result.get('patients_processed', 0)}")

                    # Refresh the page to show new data
                    st.rerun()
                else:
                    st.error(f"❌ Upload failed: {response.text}")
            except Exception as e:
                st.error(f"❌ Error processing file: {str(e)}")

st.divider()

tab1, tab2, tab3 = st.tabs(
    ["Patient Database", "Patient Details", "Data Export"])

with tab1:
    st.subheader("Current Patient Database")

    # Search functionality
    search_col1, search_col2 = st.columns([3, 1])
    with search_col1:
        search_query = st.text_input(
            "Search patients by name or ID", placeholder="Enter patient name or ID...")
    with search_col2:
        search_button = st.button("🔍 Search", type="primary")

    # Fetch patient data from backend
    try:
        if search_query and search_button:
            # Search for specific patients
            search_response = get(f"/patients/search?q={search_query}")
            if search_response.ok:
                search_data = search_response.json()
                patients = search_data.get('patients', [])
                st.success(
                    f"Found {len(patients)} patients matching '{search_query}'")
            else:
                st.error("Search failed")
                patients = []
        else:
            # Get all patients
            patients_response = get("/patients/")
            if patients_response.ok:
                patients_data = patients_response.json()
                patients = patients_data.get('patients', [])
            else:
                st.error("Failed to fetch patients")
                patients = []

        if patients:
            # Create comprehensive patient summary
            patient_summary = []
            for patient in patients:
                # Determine status based on heart disease vitals
                status = "🟢"  # Default to normal
                if patient.get('target') == 1:
                    status = "🔴"  # Heart disease
                elif patient.get('resting_bp') and patient['resting_bp'] > 130:
                    status = "🟡"  # High blood pressure
                elif patient.get('max_heart_rate') and (patient['max_heart_rate'] < 60 or patient['max_heart_rate'] > 100):
                    status = "🟡"  # Abnormal heart rate
                elif patient.get('cholesterol') and patient['cholesterol'] > 240:
                    status = "🟡"  # High cholesterol

                # Format chest pain type
                chest_pain = patient.get('chest_pain_type')
                if chest_pain == 0:
                    chest_pain_display = "Typical Angina"
                elif chest_pain == 1:
                    chest_pain_display = "Atypical Angina"
                elif chest_pain == 2:
                    chest_pain_display = "Non-anginal Pain"
                elif chest_pain == 3:
                    chest_pain_display = "Asymptomatic"
                else:
                    chest_pain_display = "N/A"

                patient_summary.append({
                    'Patient ID': patient.get('uid', 'N/A'),
                    'Name': patient.get('name', 'N/A'),
                    'Age': patient.get('age', 'N/A'),
                    'Gender': patient.get('sex', 'N/A'),
                    'Phone': patient.get('phone', 'N/A'),
                    'Blood Pressure': f"{patient.get('resting_bp', 'N/A')} mmHg",
                    'Cholesterol': f"{patient.get('cholesterol', 'N/A')} mg/dl",
                    'Heart Rate': f"{patient.get('max_heart_rate', 'N/A')} bpm",
                    'Chest Pain': chest_pain_display,
                    'Exercise Angina': "Yes" if patient.get('exercise_angina') == 1 else "No",
                    'ST Depression': f"{patient.get('st_depression', 'N/A')}" if patient.get('st_depression') is not None else 'N/A',
                    'Heart Disease': "Yes" if patient.get('target') == 1 else "No",
                    'Status': status,
                })

            # Display patient summary
            summary_df = pd.DataFrame(patient_summary)
            st.dataframe(summary_df, use_container_width=True, height=400)

            # Display metrics
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Total Patients", len(patient_summary))
            with col2:
                heart_disease_count = len(
                    [p for p in patient_summary if p['Heart Disease'] == 'Yes'])
                st.metric("Heart Disease Cases", heart_disease_count)
            with col3:
                high_risk_count = len(
                    [p for p in patient_summary if p['Status'] == '🟡' or p['Status'] == '🔴'])
                st.metric("High Risk Patients", high_risk_count)
            with col4:
                healthy_count = len(
                    [p for p in patient_summary if p['Status'] == '🟢'])
                st.metric("Healthy Patients", healthy_count)

        else:
            st.info("No patient data available. Please upload CSV data first.")

    except Exception as e:
        st.error(f"Error loading patient data: {str(e)}")

with tab2:
    st.subheader("Patient Details & Vitals")

    # Patient selection
    try:
        patients_response = get("/patients/")
        if patients_response.ok:
            patients_data = patients_response.json()
            patients = patients_data.get('patients', [])

            if patients:
                # Create patient selector
                patient_options = {
                    f"{p['uid']} - {p['name']}": p['id'] for p in patients}
                selected_patient_label = st.selectbox(
                    "Select Patient for Detailed View",
                    options=list(patient_options.keys())
                )

                if selected_patient_label:
                    selected_patient_id = patient_options[selected_patient_label]

                    # Fetch detailed patient information
                    patient_detail_response = get(
                        f"/patients/{selected_patient_id}")
                    if patient_detail_response.ok:
                        patient_detail = patient_detail_response.json()

                        # Display patient information
                        col1, col2 = st.columns(2)

                        with col1:
                            st.subheader("📋 Patient Information")
                            st.write(
                                f"**ID:** {patient_detail.get('uid', 'N/A')}")
                            st.write(
                                f"**Name:** {patient_detail.get('name', 'N/A')}")
                            st.write(
                                f"**Age:** {patient_detail.get('age', 'N/A')}")
                            st.write(
                                f"**Gender:** {patient_detail.get('sex', 'N/A')}")
                            st.write(
                                f"**Contact:** {patient_detail.get('contact_phone', 'N/A')}")
                            st.write(
                                f"**Height:** {patient_detail.get('height_cm', 'N/A')} cm")
                            st.write(
                                f"**Weight:** {patient_detail.get('weight_kg', 'N/A')} kg")
                            st.write(
                                f"**BMI:** {patient_detail.get('bmi', 'N/A')}")

                        with col2:
                            st.subheader("💓 Vital Signs Summary")
                            st.write(
                                f"**Blood Pressure:** {patient_detail.get('bp_systolic', 'N/A')}/{patient_detail.get('bp_diastolic', 'N/A')} mmHg")
                            st.write(
                                f"**Heart Rate:** {patient_detail_response.get('heart_rate', 'N/A')} bpm")
                            st.write(
                                f"**Temperature:** {patient_detail.get('temperature', 'N/A')}°C")
                            st.write(
                                f"**O2 Saturation:** {patient_detail.get('oxygen_saturation', 'N/A')}%")
                            st.write(
                                f"**Respiratory Rate:** {patient_detail.get('respiratory_rate', 'N/A')} /min")
                            st.write(
                                f"**Cholesterol:** {patient_detail.get('cholesterol', 'N/A')} mg/dL")
                            st.write(
                                f"**Glucose:** {patient_detail.get('glucose', 'N/A')} mg/dL")
                            st.write(
                                f"**Last Updated:** {patient_detail.get('last_updated', 'N/A')}")

                        # Fetch and display vitals trends
                        st.subheader("📈 Vital Signs Trends")
                        vitals_response = get(
                            f"/patients/{selected_patient_id}/vitals")
                        if vitals_response.ok:
                            vitals_data = vitals_response.json()
                            vitals = vitals_data.get('vitals', [])

                            if vitals:
                                # Create vitals DataFrame
                                vitals_df = pd.DataFrame(vitals)
                                vitals_df['observed_at'] = pd.to_datetime(
                                    vitals_df['observed_at'])
                                vitals_df = vitals_df.sort_values(
                                    'observed_at')

                                # Display vitals table
                                st.dataframe(
                                    vitals_df, use_container_width=True)

                                # Create trend charts for numeric vitals
                                numeric_vitals = vitals_df[vitals_df['value_num'].notna(
                                )]
                                if not numeric_vitals.empty:
                                    st.subheader("📊 Vitals Trends Over Time")

                                    # Group by observation type and create line charts
                                    for obs_type in numeric_vitals['obs_type'].unique():
                                        type_data = numeric_vitals[numeric_vitals['obs_type'] == obs_type]
                                        if len(type_data) > 1:
                                            st.line_chart(
                                                type_data.set_index('observed_at')[
                                                    'value_num'],
                                                use_container_width=True
                                            )
                            else:
                                st.info(
                                    "No vitals data available for this patient")
                        else:
                            st.error("Failed to fetch vitals data")
                    else:
                        st.error("Failed to fetch patient details")
            else:
                st.info("No patients available. Please upload CSV data first.")

    except Exception as e:
        st.error(f"Error loading patient details: {str(e)}")

with tab3:
    st.subheader("Export Patient Data")

    try:
        patients_response = get("/patients/")
        if patients_response.ok:
            patients_data = patients_response.json()
            patients = patients_data.get('patients', [])

            if patients:
                col1, col2 = st.columns(2)

                with col1:
                    st.subheader("Export Summary Data")
                    if st.button("📊 Export Patient Summary CSV", type="primary"):
                        # Create summary for export
                        export_summary = []
                        for patient in patients:
                            export_summary.append({
                                'Patient_ID': patient.get('uid', 'N/A'),
                                'First_Name': patient.get('name', 'N/A').split()[0] if patient.get('name') else 'N/A',
                                'Last_Name': ' '.join(patient.get('name', 'N/A').split()[1:]) if patient.get('name') and len(patient.get('name', '').split()) > 1 else 'N/A',
                                'Age': patient.get('age', 'N/A'),
                                'Gender': patient.get('sex', 'N/A'),
                                'Contact_Phone': patient.get('contact_phone', 'N/A'),
                                'Height_cm': patient.get('height_cm', 'N/A'),
                                'Weight_kg': patient.get('weight_kg', 'N/A'),
                                'BMI': patient.get('bmi', 'N/A'),
                                'BP_Systolic': patient.get('bp_systolic', 'N/A'),
                                'BP_Diastolic': patient.get('bp_diastolic', 'N/A'),
                                'Heart_Rate': patient.get('heart_rate', 'N/A'),
                                'Temperature': patient.get('temperature', 'N/A'),
                                'O2_Saturation': patient.get('oxygen_saturation', 'N/A'),
                                'Cholesterol': patient.get('cholesterol', 'N/A'),
                                'Glucose': patient.get('glucose', 'N/A')
                            })

                        summary_df = pd.DataFrame(export_summary)
                        csv = summary_df.to_csv(index=False)
                        st.download_button(
                            label="📥 Download Patient Summary CSV",
                            data=csv,
                            file_name=f"patient_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                            mime="text/csv",
                        )

                with col2:
                    st.subheader("Export Individual Patient Data")
                    # Create patient selector for detailed export
                    patient_options = {
                        f"{p['uid']} - {p['name']}": p['id'] for p in patients}
                    selected_export_patient = st.selectbox(
                        "Select Patient for Detailed Export",
                        options=list(patient_options.keys())
                    )

                    if selected_export_patient and st.button("📥 Export Patient Vitals"):
                        selected_patient_id = patient_options[selected_export_patient]

                        # Fetch patient vitals
                        vitals_response = get(
                            f"/patients/{selected_patient_id}/vitals")
                        if vitals_response.ok:
                            vitals_data = vitals_response.json()
                            vitals = vitals_data.get('vitals', [])

                            if vitals:
                                vitals_df = pd.DataFrame(vitals)
                                csv = vitals_df.to_csv(index=False)
                                st.download_button(
                                    label="📥 Download Patient Vitals CSV",
                                    data=csv,
                                    file_name=f"vitals_{selected_export_patient.split(' - ')[0]}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                                    mime="text/csv",
                                )
                            else:
                                st.warning(
                                    "No vitals data available for this patient")
                        else:
                            st.error("Failed to fetch vitals data")
            else:
                st.info("No patient data available for export")

    except Exception as e:
        st.error(f"Error during export: {str(e)}")

# System information
st.divider()
st.subheader("ℹ️ System Information")
st.info(f"""
**Data Source:** Backend API
**Last Updated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Total Patients:** {len(patients) if 'patients' in locals() else 0}
**Data Status:** {'✅ Active' if 'patients' in locals() and patients else '❌ No Data'}
""")
