import streamlit as st
import numpy as np
from utils.styling import apply_custom_css
from components.navbar import render_navbar
from utils.analysis import analyze_vitals_trends


apply_custom_css()
st.markdown('<h1 class="main-header">Healthcare Analytics Dashboard</h1>',
            unsafe_allow_html=True)
render_navbar()


st.header("📊 Dashboard Overview")


col1, col2, col3, col4 = st.columns(4)


with col1:
    st.markdown(
        f"""
    <div class="metric-card">
    <h3>Total Patients</h3>
    <h2>{len(st.session_state.patients_data)}</h2>
    </div>
    """,
        unsafe_allow_html=True,
    )


with col2:
    critical_count = len([
        p for p in st.session_state.patients_data.values()
        if analyze_vitals_trends(p['vitals'])['heart_rate']['status'] == 'HIGH'
    ])
    st.markdown(
        f"""
    <div class="metric-card">
    <h3>Critical Alerts</h3>
    <h2>{critical_count}</h2>
    </div>
    """,
        unsafe_allow_html=True,
    )


with col3:
    avg_age = np.mean([p['age']
                      for p in st.session_state.patients_data.values()])
    st.markdown(
        f"""
    <div class="metric-card">
    <h3>Avg Age</h3>
    <h2>{avg_age:.0f}</h2>
    </div>
    """,
        unsafe_allow_html=True,
    )


with col4:
    conditions = [p['condition']
                  for p in st.session_state.patients_data.values()]
    most_common = max(set(conditions), key=conditions.count)
    st.markdown(
        f"""
    <div class="metric-card">
    <h3>Top Condition</h3>
    <h2>{most_common}</h2>
    </div>
    """,
        unsafe_allow_html=True,
    )


st.subheader("🚨 Recent Alerts")
alert_col1, alert_col2 = st.columns(2)


with alert_col1:
    st.markdown(
        """
  <div class="alert-high">
  <strong>HIGH PRIORITY:</strong> PT0023 - Heart Rate: 120 bpm
  </div>
  <div class="alert-high">
  <strong>HIGH PRIORITY:</strong> PT0007 - Blood Pressure: 165/95
  </div>
  """,
        unsafe_allow_html=True,
    )


with alert_col2:
    st.markdown(
        """
    <div class="alert-normal">
    <strong>NORMAL:</strong> PT0015 - All vitals stable
    </div>
    <div class="alert-normal">
    <strong>NORMAL:</strong> PT0031 - Improved oxygen levels
    </div>
    """,
        unsafe_allow_html=True,
    )
