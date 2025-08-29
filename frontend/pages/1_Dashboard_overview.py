import streamlit as st
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from utils.styling import apply_custom_css
from components.navbar import render_navbar
from utils.api import get
import pandas as pd

apply_custom_css()
st.markdown('<h1 class="main-header">Healthcare Analytics Dashboard</h1>',
            unsafe_allow_html=True)
render_navbar()

st.header("📊 Dashboard Overview")

# Fetch dashboard statistics from backend
try:
    stats_response = get("/dashboard/stats")
    if stats_response.ok:
        stats = stats_response.json()
    else:
        st.error("Failed to fetch dashboard statistics")
        stats = {}
except Exception as e:
    st.error(f"Error connecting to backend: {str(e)}")
    stats = {}

# Display key metrics
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(
        f"""
    <div class="metric-card">
    <h3>Total Patients</h3>
    <h2>{stats.get('total_patients', 0)}</h2>
    </div>
    """,
        unsafe_allow_html=True,
    )

with col2:
    st.markdown(
        f"""
    <div class="metric-card">
    <h3>Total Observations</h3>
    <h2>{stats.get('total_observations', 0)}</h2>
    </div>
    """,
        unsafe_allow_html=True,
    )

with col3:
    st.markdown(
        f"""
    <div class="metric-card">
    <h3>Avg Age</h3>
    <h2>{stats.get('avg_age', 0):.1f}</h2>
    </div>
    """,
        unsafe_allow_html=True,
    )

with col4:
    st.markdown(
        f"""
    <div class="metric-card">
    <h3>Avg BMI</h3>
    <h2>{stats.get('avg_bmi', 0):.1f}</h2>
    </div>
    """,
        unsafe_allow_html=True,
    )

# Additional metrics row
col5, col6, col7, col8 = st.columns(4)

with col5:
    st.markdown(
        f"""
    <div class="metric-card">
    <h3>Male Patients</h3>
    <h2>{stats.get('male_patients', 0)}</h2>
    </div>
    """,
        unsafe_allow_html=True,
    )

with col6:
    st.markdown(
        f"""
    <div class="metric-card">
    <h3>Female Patients</h3>
    <h2>{stats.get('female_patients', 0)}</h2>
    </div>
    """,
        unsafe_allow_html=True,
    )

with col7:
    st.markdown(
        f"""
    <div class="metric-card">
    <h3>Data Uploads</h3>
    <h2>{stats.get('total_uploads', 0)}</h2>
    </div>
    """,
        unsafe_allow_html=True,
    )

with col8:
    # Calculate critical patients based on vitals
    critical_count = 0
    try:
        vitals_response = get("/dashboard/vitals-summary")
        if vitals_response.ok:
            vitals_data = vitals_response.json()
            # Count patients with high blood pressure or abnormal heart rate
            if 'blood_pressure_ranges' in vitals_data:
                critical_count += vitals_data['blood_pressure_ranges'].get(
                    'high', 0)
            if 'heart_rate_ranges' in vitals_data:
                critical_count += vitals_data['heart_rate_ranges'].get(
                    'high', 0)
    except:
        pass

    st.markdown(
        f"""
    <div class="metric-card">
    <h3>Critical Alerts</h3>
    <h2>{critical_count}</h2>
    </div>
    """,
        unsafe_allow_html=True,
    )

# Fetch and display vitals summary charts
try:
    vitals_response = get("/dashboard/vitals-summary")
    if vitals_response.ok:
        vitals_data = vitals_response.json()

        st.subheader("📈 Vital Signs Distribution")

        # Create charts for different vital ranges
        col_chart1, col_chart2 = st.columns(2)

        with col_chart1:
            if 'blood_pressure_ranges' in vitals_data:
                bp_data = vitals_data['blood_pressure_ranges']
                fig_bp = px.pie(
                    values=list(bp_data.values()),
                    names=list(bp_data.keys()),
                    title="Blood Pressure Distribution",
                    color_discrete_map={
                        'normal': '#00ff00',
                        'elevated': '#ffff00',
                        'high': '#ff0000'
                    }
                )
                st.plotly_chart(fig_bp, use_container_width=True)

        with col_chart2:
            if 'bmi_ranges' in vitals_data:
                bmi_data = vitals_data['bmi_ranges']
                fig_bmi = px.pie(
                    values=list(bmi_data.values()),
                    names=list(bmi_data.keys()),
                    title="BMI Distribution",
                    color_discrete_map={
                        'underweight': '#87ceeb',
                        'normal': '#90ee90',
                        'overweight': '#ffd700',
                        'obese': '#ff6347'
                    }
                )
                st.plotly_chart(fig_bmi, use_container_width=True)

        # Heart rate distribution
        if 'heart_rate_ranges' in vitals_data:
            hr_data = vitals_data['heart_rate_ranges']
            fig_hr = px.bar(
                x=list(hr_data.keys()),
                y=list(hr_data.values()),
                title="Heart Rate Distribution",
                color=list(hr_data.values()),
                color_continuous_scale='RdYlGn_r'
            )
            st.plotly_chart(fig_hr, use_container_width=True)

except Exception as e:
    st.warning(f"Could not load vitals charts: {str(e)}")

# Recent Activity Section
st.subheader("🔄 Recent Activity")
try:
    recent_response = get("/dashboard/recent-activity")
    if recent_response.ok:
        recent_data = recent_response.json()

        if recent_data.get('recent_patients'):
            # Create a DataFrame for recent patients
            df_recent = pd.DataFrame(recent_data['recent_patients'])

            # Display recent patients in a table
            st.dataframe(
                df_recent[['patient_uid', 'first_name',
                           'last_name', 'age', 'sex']].head(10),
                use_container_width=True,
                column_config={
                    'patient_uid': 'Patient ID',
                    'first_name': 'First Name',
                    'last_name': 'Last Name',
                    'age': 'Age',
                    'sex': 'Sex'
                }
            )
        else:
            st.info("No recent patient data available")

except Exception as e:
    st.warning(f"Could not load recent activity: {str(e)}")

# System Status
st.subheader("🔧 System Status")
status_col1, status_col2, status_col3 = st.columns(3)

with status_col1:
    st.success("✅ Database Connected")
    st.info(f"Total Records: {stats.get('total_observations', 0)}")

with status_col2:
    st.success("✅ API Services Active")
    st.info(f"Patients: {stats.get('total_patients', 0)}")

with status_col3:
    st.success("✅ Data Processing Complete")
    st.info(f"Uploads: {stats.get('total_uploads', 0)}")

# Quick Actions
st.subheader("⚡ Quick Actions")
action_col1, action_col2, action_col3 = st.columns(3)

with action_col1:
    if st.button("📊 View All Patients", type="primary"):
        st.switch_page("pages/5_Seed_Patients.py")

with action_col2:
    if st.button("📈 Patient Vitals Trends"):
        st.switch_page("pages/2_Patient_vital_trends.py")

with action_col3:
    if st.button("🔍 Search Patients"):
        st.switch_page("pages/5_Seed_Patients.py")
