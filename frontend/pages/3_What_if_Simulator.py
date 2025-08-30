import streamlit as st
import plotly.graph_objects as go
from utils.styling import apply_custom_css
from components.navbar import render_navbar
from utils.analysis import simulate_intervention_impact
import pandas as pd

apply_custom_css()
st.markdown('<h1 class="main-header">Healthcare Analytics Dashboard</h1>',
            unsafe_allow_html=True)
render_navbar()


st.header("🔮 What-If Simulator")
st.write("Simulate the potential impact of medical interventions on patient vitals.")

# Check if patients data is available
if not st.session_state.patients_data:
    st.warning(
        "⚠️ No patients data available. Please log in and ensure data is loaded.")
    st.stop()

# Check if patients_data has any entries
if len(st.session_state.patients_data) == 0:
    st.info("📋 No patients found. Please upload patient data first.")
    st.stop()

sim_patient = st.selectbox(
    "Select Patient for Simulation",
    options=list(st.session_state.patients_data.keys()),
    format_func=lambda x: f"{x} - {st.session_state.patients_data[x]['name']}"
)

if sim_patient:
    patient = st.session_state.patients_data[sim_patient]
    vitals_df: pd.DataFrame = patient['vitals']

    # Check if vitals data is available
    if vitals_df.empty:
        st.warning(
            "⚠️ No vitals data available for this patient. Please ensure the patient has vital signs recorded.")
        st.stop()

    col1, col2 = st.columns([1, 2])

    with col1:
        st.subheader("Intervention Parameters")

        intervention = st.selectbox(
            "Select Intervention",
            ["Blood Pressure Medication", "Beta Blocker",
                "Oxygen Therapy", "Fever Reducer"],
        )

        if intervention == "Blood Pressure Medication":
            magnitude = st.slider("BP Reduction (mmHg)", 5, 30, 15)
            st.info("Simulates antihypertensive medication effect")
        elif intervention == "Beta Blocker":
            magnitude = st.slider("Heart Rate Reduction (bpm)", 5, 25, 10)
            st.info("Simulates beta-blocker medication effect")
        elif intervention == "Oxygen Therapy":
            magnitude = st.slider("O2 Increase (%)", 1, 10, 5)
            st.info("Simulates supplemental oxygen therapy")
        elif intervention == "Fever Reducer":
            magnitude = st.slider("Temperature Reduction (°F)", 1.0, 3.0, 1.5)
            st.info("Simulates fever-reducing medication")

        simulate_btn = st.button("Run Simulation", type="primary")
        with col2:
            if simulate_btn:
                st.subheader("Simulation Results")

                simulated_df = simulate_intervention_impact(
                    vitals_df, intervention, magnitude)
                fig = go.Figure()

                if intervention in ["Blood Pressure Medication", "Beta Blocker"]:
                    if intervention == "Blood Pressure Medication":
                        fig.add_trace(go.Scatter(
                            x=vitals_df['timestamp'], y=vitals_df['blood_pressure_sys'], name='Original Systolic BP'))
                        fig.add_trace(go.Scatter(
                            x=simulated_df['timestamp'], y=simulated_df['blood_pressure_sys'], name='Simulated Systolic BP'))
                        fig.update_layout(yaxis_title="Blood Pressure (mmHg)")
                    else:
                        fig.add_trace(go.Scatter(
                            x=vitals_df['timestamp'], y=vitals_df['heart_rate'], name='Original Heart Rate'))
                        fig.add_trace(go.Scatter(
                            x=simulated_df['timestamp'], y=simulated_df['heart_rate'], name='Simulated Heart Rate'))
                        fig.update_layout(yaxis_title="Heart Rate (bpm)")

                elif intervention == "Oxygen Therapy":
                    fig.add_trace(go.Scatter(
                        x=vitals_df['timestamp'], y=vitals_df['oxygen_saturation'], name='Original O2 Sat'))
                    fig.add_trace(go.Scatter(
                        x=simulated_df['timestamp'], y=simulated_df['oxygen_saturation'], name='Simulated O2 Sat'))
                    fig.update_layout(yaxis_title="Oxygen Saturation (%)")

                else:
                    fig.add_trace(go.Scatter(
                        x=vitals_df['timestamp'], y=vitals_df['temperature'], name='Original Temperature'))
                    fig.add_trace(go.Scatter(
                        x=simulated_df['timestamp'], y=simulated_df['temperature'], name='Simulated Temperature'))
                    fig.update_layout(yaxis_title="Temperature (°F)")

                fig.update_layout(
                    title=f"Impact of {intervention}", xaxis_title="Time", height=400)
                st.plotly_chart(fig, use_container_width=True)

                st.subheader("Impact Summary")
                original_mean = vitals_df.iloc[-24:].mean()
                simulated_mean = simulated_df.iloc[-24:].mean()

                if intervention == "Blood Pressure Medication":
                    improvement = original_mean['blood_pressure_sys'] - \
                        simulated_mean['blood_pressure_sys']
                    st.success(
                        f"Average systolic BP reduction: {improvement:.1f} mmHg")
                elif intervention == "Beta Blocker":
                    improvement = original_mean['heart_rate'] - \
                        simulated_mean['heart_rate']
                    st.success(
                        f"Average heart rate reduction: {improvement:.1f} bpm")
                elif intervention == "Oxygen Therapy":
                    improvement = simulated_mean['oxygen_saturation'] - \
                        original_mean['oxygen_saturation']
                    st.success(
                        f"Average O2 saturation increase: {improvement:.1f}%")
                else:
                    improvement = original_mean['temperature'] - \
                        simulated_mean['temperature']
                    st.success(
                        f"Average temperature reduction: {improvement:.1f}°F")
