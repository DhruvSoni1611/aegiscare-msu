import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from utils.styling import apply_custom_css
from utils.api import get
import pandas as pd

apply_custom_css()
st.markdown('<h1 class="main-header">Healthcare Analytics Dashboard</h1>',
            unsafe_allow_html=True)

st.header("📈 Patient Vitals Trends")

# Check if patients data is available
if not st.session_state.patients_data:
    st.warning(
        "⚠️ No patients data available. Please log in and ensure data is loaded.")
    st.stop()

# Check if patients_data has any entries
if len(st.session_state.patients_data) == 0:
    st.info("📋 No patients found. Please upload patient data first.")
    st.stop()

# Add pagination for patient selection
total_patients = len(st.session_state.patients_data)
patients_per_page = 100
total_pages = (total_patients + patients_per_page - 1) // patients_per_page

# Page navigation
col1, col2, col3 = st.columns([2, 1, 1])
with col1:
    st.info(
        f"📊 **Patient Vitals Analysis:** Total {total_patients} patients available")
with col2:
    current_page = st.selectbox("Page", range(
        1, total_pages + 1), key="patient_page")
with col3:
    if st.button("🔄 Refresh Patient Data", type="secondary"):
        st.rerun()

# Get patients for current page
start_idx = (current_page - 1) * patients_per_page
end_idx = min(start_idx + patients_per_page, total_patients)
patient_options = list(st.session_state.patients_data.keys())[
    start_idx:end_idx]

# Create patient selection dropdown with pagination
selected_patient_id = st.selectbox(
    f"Select Patient (Page {current_page} of {total_pages}, Showing {len(patient_options)} patients)",
    options=patient_options,
    format_func=lambda x: f"{x} - {st.session_state.patients_data[x]['name']}"
)

if selected_patient_id:
    selected_patient = st.session_state.patients_data[selected_patient_id]

    # Display patient basic info
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Name", selected_patient['name'])
    col2.metric("Age", selected_patient['age'])
    col3.metric("Gender", selected_patient['gender'])
    col4.metric("Condition", selected_patient['condition'])

    # Fetch real vitals data from backend
    try:
        # Convert patient ID to numeric ID for backend API
        patient_numeric_id = None
        for pid, patient_data in st.session_state.patients_data.items():
            if pid == selected_patient_id:
                # Try to get numeric ID from the patient data
                patient_numeric_id = patient_data.get('id', pid)
                break

        if not patient_numeric_id:
            st.error("❌ Could not determine patient ID for backend API")
            st.stop()

        vitals_response = get(f"/patients/{patient_numeric_id}/vitals")
        if vitals_response.ok:
            vitals_data = vitals_response.json()
            vitals_df = pd.DataFrame(vitals_data.get('vitals', []))

            if not vitals_df.empty:
                # Convert timestamp to datetime
                vitals_df['timestamp'] = pd.to_datetime(
                    vitals_df['observed_at'])

                # Display current vital signs from the latest data
                st.subheader("Current Vital Signs")
                latest_vitals = vitals_df.iloc[-1]
                vital_cols = st.columns(5)

                vital_cols[0].metric(
                    "Heart Rate", f"{latest_vitals.get('heart_rate', 'N/A')} bpm")
                vital_cols[1].metric(
                    "Systolic BP", f"{latest_vitals.get('bp_sys', 'N/A')} mmHg")
                vital_cols[2].metric(
                    "Diastolic BP", f"{latest_vitals.get('bp_dia', 'N/A')} mmHg")
                vital_cols[3].metric(
                    "Temperature", f"{latest_vitals.get('temperature', 'N/A')}°F")
                vital_cols[4].metric(
                    "O2 Saturation", f"{latest_vitals.get('oxygen_saturation', 'N/A')}%")

                # Display vitals trends over time
                st.subheader("Vitals Trends Over Time")

                # Create subplots for different vitals
                fig = make_subplots(
                    rows=3, cols=2,
                    subplot_titles=('Heart Rate', 'Blood Pressure (Systolic)', 'Blood Pressure (Diastolic)',
                                    'Temperature', 'Oxygen Saturation', 'Vitals Summary'),
                    specs=[[{"secondary_y": False}, {"secondary_y": False}],
                           [{"secondary_y": False}, {"secondary_y": False}],
                           [{"secondary_y": False}, {"secondary_y": False}]],
                    vertical_spacing=0.08,
                )

                # Heart Rate
                if 'heart_rate' in vitals_df.columns:
                    fig.add_trace(
                        go.Scatter(x=vitals_df['timestamp'], y=vitals_df['heart_rate'],
                                   name='Heart Rate', mode='lines+markers', line=dict(color='red')),
                        row=1, col=1,
                    )

                # Systolic Blood Pressure
                if 'bp_sys' in vitals_df.columns:
                    fig.add_trace(
                        go.Scatter(x=vitals_df['timestamp'], y=vitals_df['bp_sys'],
                                   name='Systolic BP', mode='lines+markers', line=dict(color='blue')),
                        row=1, col=2,
                    )

                # Diastolic Blood Pressure
                if 'bp_dia' in vitals_df.columns:
                    fig.add_trace(
                        go.Scatter(x=vitals_df['timestamp'], y=vitals_df['bp_dia'],
                                   name='Diastolic BP', mode='lines+markers', line=dict(color='green')),
                        row=2, col=1,
                    )

                # Temperature
                if 'temperature' in vitals_df.columns:
                    fig.add_trace(
                        go.Scatter(x=vitals_df['timestamp'], y=vitals_df['temperature'],
                                   name='Temperature', mode='lines+markers', line=dict(color='orange')),
                        row=2, col=2,
                    )

                # Oxygen Saturation
                if 'oxygen_saturation' in vitals_df.columns:
                    fig.add_trace(
                        go.Scatter(x=vitals_df['timestamp'], y=vitals_df['oxygen_saturation'],
                                   name='O2 Saturation', mode='lines+markers', line=dict(color='purple')),
                        row=3, col=1,
                    )

                # Vitals Summary (Heart Rate vs Blood Pressure correlation)
                if 'heart_rate' in vitals_df.columns and 'bp_sys' in vitals_df.columns:
                    fig.add_trace(
                        go.Scatter(x=vitals_df['heart_rate'], y=vitals_df['bp_sys'],
                                   name='HR vs BP', mode='markers', marker=dict(color='brown', size=8)),
                        row=3, col=2,
                    )

                fig.update_layout(
                    height=800,
                    showlegend=True,
                    title_text=f"Patient Vitals Analysis - {selected_patient['name']}"
                )

                # Update axis labels
                fig.update_xaxes(title_text="Time", row=3, col=1)
                fig.update_xaxes(title_text="Heart Rate (bpm)", row=3, col=2)
                fig.update_yaxes(title_text="Heart Rate (bpm)", row=1, col=1)
                fig.update_yaxes(
                    title_text="Blood Pressure (mmHg)", row=1, col=2)
                fig.update_yaxes(
                    title_text="Blood Pressure (mmHg)", row=2, col=1)
                fig.update_yaxes(title_text="Temperature (°F)", row=2, col=2)
                fig.update_yaxes(title_text="O2 Saturation (%)", row=3, col=1)
                fig.update_yaxes(title_text="Systolic BP (mmHg)", row=3, col=2)

                st.plotly_chart(fig, use_container_width=True)

                # Statistical Summary
                st.subheader("📊 Statistical Summary")
                col1, col2, col3, col4 = st.columns(4)

                with col1:
                    if 'heart_rate' in vitals_df.columns:
                        st.metric("Mean Heart Rate",
                                  f"{vitals_df['heart_rate'].mean():.1f} bpm")
                    if 'temperature' in vitals_df.columns:
                        st.metric("Mean Temperature",
                                  f"{vitals_df['temperature'].mean():.1f}°F")

                with col2:
                    if 'bp_sys' in vitals_df.columns:
                        st.metric("Mean Systolic BP",
                                  f"{vitals_df['bp_sys'].mean():.1f} mmHg")
                    if 'oxygen_saturation' in vitals_df.columns:
                        st.metric("Mean O2 Saturation",
                                  f"{vitals_df['oxygen_saturation'].mean():.1f}%")

                with col3:
                    if 'heart_rate' in vitals_df.columns:
                        st.metric("Max Heart Rate",
                                  f"{vitals_df['heart_rate'].max():.0f} bpm")
                    if 'temperature' in vitals_df.columns:
                        st.metric("Max Temperature",
                                  f"{vitals_df['temperature'].max():.1f}°F")

                with col4:
                    if 'heart_rate' in vitals_df.columns:
                        st.metric("Min Heart Rate",
                                  f"{vitals_df['heart_rate'].min():.0f} bpm")
                    if 'oxygen_saturation' in vitals_df.columns:
                        st.metric("Min O2 Saturation",
                                  f"{vitals_df['oxygen_saturation'].min():.0f}%")

                # ML Model Predictions Section
                st.subheader("🤖 ML Model Predictions")

                # Fetch ML predictions from backend
                try:
                    ml_response = get(
                        f"/patients/{patient_numeric_id}/predictions")
                    if ml_response.ok:
                        predictions = ml_response.json()

                        # Display predictions in a structured format
                        col1, col2 = st.columns(2)

                        with col1:
                            st.subheader("📊 Risk Assessment")
                            if 'readmission_risk' in predictions:
                                risk_level = "High" if predictions['readmission_risk'] > 0.7 else "Medium" if predictions[
                                    'readmission_risk'] > 0.3 else "Low"
                                st.metric(
                                    "Readmission Risk", f"{predictions['readmission_risk']:.1%}", delta=risk_level)

                            if 'complication_risk' in predictions:
                                comp_risk = "High" if predictions['complication_risk'] > 0.7 else "Medium" if predictions[
                                    'complication_risk'] > 0.3 else "Low"
                                st.metric(
                                    "Complication Risk", f"{predictions['complication_risk']:.1%}", delta=comp_risk)

                            if 'mortality_risk' in predictions:
                                mort_risk = "High" if predictions['mortality_risk'] > 0.7 else "Medium" if predictions[
                                    'mortality_risk'] > 0.3 else "Low"
                                st.metric(
                                    "Mortality Risk", f"{predictions['mortality_risk']:.1%}", delta=mort_risk)

                        with col2:
                            st.subheader("🎯 Outcome Predictions")
                            if 'target' in predictions:
                                outcome = "Positive" if predictions['target'] == 1 else "Negative"
                                st.metric("Treatment Outcome", outcome)

                            if 'readmiss' in predictions:
                                readmiss = "Yes" if predictions['readmiss'] == 1 else "No"
                                st.metric("Readmission Likely", readmiss)

                            if 'complication' in predictions:
                                complication = "Yes" if predictions['complication'] == 1 else "No"
                                st.metric("Complication Expected",
                                          complication)

                        # Display prediction confidence and insights
                        st.subheader("💡 Clinical Insights")
                        insights = []

                        if 'readmission_risk' in predictions and predictions['readmission_risk'] > 0.5:
                            insights.append(
                                "⚠️ **High readmission risk** - Consider extended monitoring and follow-up care")

                        if 'complication_risk' in predictions and predictions['complication_risk'] > 0.6:
                            insights.append(
                                "🚨 **Elevated complication risk** - Monitor closely for adverse events")

                        if 'mortality_risk' in predictions and predictions['mortality_risk'] > 0.4:
                            insights.append(
                                "🔴 **Significant mortality risk** - Intensive care monitoring recommended")

                        if insights:
                            for insight in insights:
                                st.warning(insight)
                        else:
                            st.success(
                                "✅ **Low risk profile** - Patient shows favorable prognosis")

                        # Prediction trends chart
                        if len(vitals_df) > 1:
                            st.subheader("📈 Prediction Trends")

                            # Create a simple trend visualization
                            fig_trend = go.Figure()

                            # Add vitals trend line
                            if 'heart_rate' in vitals_df.columns:
                                fig_trend.add_trace(go.Scatter(
                                    x=vitals_df['timestamp'],
                                    y=vitals_df['heart_rate'],
                                    name='Heart Rate Trend',
                                    mode='lines+markers'
                                ))

                            fig_trend.update_layout(
                                title="Vitals Trend Analysis",
                                xaxis_title="Time",
                                yaxis_title="Value",
                                height=400
                            )

                            st.plotly_chart(
                                fig_trend, use_container_width=True)

                    else:
                        st.info("📊 ML predictions not available for this patient")

                except Exception as e:
                    st.info("📊 ML predictions service not available")

                # Trend Analysis
                st.subheader("📈 Trend Analysis")

                # Calculate trends (last 24 hours vs previous 24 hours)
                if len(vitals_df) >= 12:
                    recent_data = vitals_df.tail(6)  # Last 24 hours
                    previous_data = vitals_df.iloc[-12:-6]  # Previous 24 hours

                    col1, col2, col3 = st.columns(3)

                    with col1:
                        if 'heart_rate' in vitals_df.columns:
                            hr_trend = recent_data['heart_rate'].mean(
                            ) - previous_data['heart_rate'].mean()
                            hr_icon = "📈" if hr_trend > 0 else "📉" if hr_trend < 0 else "➡️"
                            st.metric(
                                "Heart Rate Trend", f"{hr_trend:+.1f} bpm", delta=f"{hr_icon} {abs(hr_trend):.1f}")

                    with col2:
                        if 'bp_sys' in vitals_df.columns:
                            bp_trend = recent_data['bp_sys'].mean(
                            ) - previous_data['bp_sys'].mean()
                            bp_icon = "📈" if bp_trend > 0 else "📉" if bp_trend < 0 else "➡️"
                            st.metric(
                                "BP Trend", f"{bp_trend:+.1f} mmHg", delta=f"{bp_icon} {abs(bp_trend):.1f}")

                    with col3:
                        if 'temperature' in vitals_df.columns:
                            temp_trend = recent_data['temperature'].mean(
                            ) - previous_data['temperature'].mean()
                            temp_icon = "📈" if temp_trend > 0 else "📉" if temp_trend < 0 else "➡️"
                            st.metric(
                                "Temperature Trend", f"{temp_trend:+.1f}°F", delta=f"{temp_icon} {abs(temp_trend):.1f}")
                else:
                    st.info(
                        "📊 Insufficient data for trend analysis (need at least 12 data points)")

                # Clinical Notes
                st.subheader("📝 Clinical Notes")
                if selected_patient.get('notes'):
                    for i, note in enumerate(selected_patient['notes'], 1):
                        st.info(f"**Note {i}:** {note}")
                else:
                    st.info("📝 No clinical notes available for this patient")

                # Add New Note Button
                if st.button("📝 Add New Clinical Note", type="secondary"):
                    st.session_state.show_add_note = True
                    st.rerun()

                if st.session_state.get('show_add_note', False):
                    with st.form("add_note_form"):
                        new_note = st.text_area(
                            "New Clinical Note", placeholder="Enter new clinical observation or note")
                        col1, col2 = st.columns([1, 1])
                        with col1:
                            if st.form_submit_button("✅ Add Note"):
                                if new_note.strip():
                                    if 'notes' not in selected_patient:
                                        selected_patient['notes'] = []
                                    selected_patient['notes'].append(
                                        new_note.strip())
                                    st.session_state.show_add_note = False
                                    st.success("✅ Note added successfully!")
                                    st.rerun()
                                else:
                                    st.error("❌ Please enter a note")
                        with col2:
                            if st.form_submit_button("❌ Cancel"):
                                st.session_state.show_add_note = False
                                st.rerun()

            else:
                st.warning("⚠️ No vitals data available for this patient.")
                st.info(
                    "📊 This patient has been added but no vitals data has been recorded yet.")

        else:
            st.warning("⚠️ Could not fetch vitals data from backend")
            st.info("📊 Please ensure the backend service is running and accessible")

    except Exception as e:
        st.error(f"❌ Error fetching vitals data: {str(e)}")
        st.info("📊 Please check backend connection and try again")

else:
    st.info("📋 Please select a patient to view their vitals trends and analysis.")
