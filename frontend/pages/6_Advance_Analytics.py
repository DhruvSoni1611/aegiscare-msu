from utils.analysis import analyze_vitals_trends
import streamlit as st
import plotly.express as px
import pandas as pd
from utils.styling import apply_custom_css
from components.navbar import render_navbar

apply_custom_css()
st.markdown('<h1 class="main-header">Healthcare Analytics Dashboard</h1>',
            unsafe_allow_html=True)
render_navbar()

st.header("🧠 Advanced Analytics")

# Check if patients data is available
if not st.session_state.patients_data:
    st.warning(
        "⚠️ No patients data available. Please log in and ensure data is loaded.")
    st.stop()

# Check if patients_data has any entries
if len(st.session_state.patients_data) == 0:
    st.info("📋 No patients found. Please upload patient data first.")
    st.stop()

st.subheader("Population Health Metrics")

all_vitals = []
for pid, patient in st.session_state.patients_data.items():
    patient_vitals = patient['vitals'].copy()
    patient_vitals['patient_id'] = pid
    patient_vitals['age_group'] = '65+' if patient['age'] >= 65 else '45-64' if patient['age'] >= 45 else '18-44'
    patient_vitals['condition'] = patient['condition']
    all_vitals.append(patient_vitals)

combined_df = pd.concat(all_vitals, ignore_index=True)

pop_col1, pop_col2, pop_col3, pop_col4 = st.columns(4)
with pop_col1:
    avg_hr = combined_df['heart_rate'].mean()
    st.metric("Population Avg HR", f"{avg_hr:.1f} bpm")
with pop_col2:
    avg_bp = combined_df['blood_pressure_sys'].mean()
    st.metric("Population Avg BP", f"{avg_bp:.0f} mmHg")
with pop_col3:
    avg_temp = combined_df['temperature'].mean()
    st.metric("Population Avg Temp", f"{avg_temp:.1f}°F")
with pop_col4:
    avg_o2 = combined_df['oxygen_saturation'].mean()
    st.metric("Population Avg O2", f"{avg_o2:.1f}%")

st.subheader("Vitals by Age Group")
age_analysis = (
    combined_df.groupby('age_group').agg({
        'heart_rate': 'mean',
        'blood_pressure_sys': 'mean',
        'temperature': 'mean',
        'oxygen_saturation': 'mean',
    }).round(1)
)

fig_age = px.bar(
    age_analysis.reset_index(),
    x='age_group',
    y=['heart_rate', 'blood_pressure_sys', 'oxygen_saturation'],
    title="Average Vitals by Age Group",
    barmode='group',
)
st.plotly_chart(fig_age, use_container_width=True)

st.subheader("Vitals by Medical Condition")
condition_analysis = (
    combined_df.groupby('condition').agg({
        'heart_rate': 'mean',
        'blood_pressure_sys': 'mean',
        'temperature': 'mean',
        'oxygen_saturation': 'mean',
    }).round(1)
)

fig_condition = px.imshow(
    condition_analysis,
    title="Vitals Heatmap by Medical Condition",
    aspect='auto',
)
st.plotly_chart(fig_condition, use_container_width=True)

st.subheader("Risk Stratification")

risk_patients = []
for pid, patient in st.session_state.patients_data.items():
    trends = analyze_vitals_trends(patient['vitals'])
    risk_score = 0
    for vital, data in trends.items():
        if data['status'] in ['HIGH', 'LOW']:
            risk_score += 2
        if data['trend'] == 'UP' and vital in ['heart_rate', 'blood_pressure_sys', 'temperature']:
            risk_score += 1
        elif data['trend'] == 'DOWN' and vital == 'oxygen_saturation':
            risk_score += 1

    risk_level = 'High' if risk_score >= 4 else 'Medium' if risk_score >= 2 else 'Low'
    risk_patients.append({
        'Patient ID': pid,
        'Name': patient['name'],
        'Age': patient['age'],
        'Condition': patient['condition'],
        'Risk Score': risk_score,
        'Risk Level': risk_level,
    })

risk_df = pd.DataFrame(risk_patients)

risk_counts = risk_df['Risk Level'].value_counts()
fig_risk = px.pie(
    values=risk_counts.values,
    names=risk_counts.index,
    title="Patient Risk Distribution",
)
st.plotly_chart(fig_risk, use_container_width=True)

high_risk = risk_df[risk_df['Risk Level'] ==
                    'High'].sort_values('Risk Score', ascending=False)
if len(high_risk) > 0:
    st.subheader("🚨 High-Risk Patients")
    st.dataframe(high_risk, use_container_width=True)
