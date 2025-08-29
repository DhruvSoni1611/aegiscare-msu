import streamlit as st
import plotly.express as px
from datetime import datetime, timedelta
import pandas as pd
from utils.styling import apply_custom_css
from components.navbar import render_navbar

apply_custom_css()
st.markdown('<h1 class="main-header">Healthcare Analytics Dashboard</h1>',
            unsafe_allow_html=True)
render_navbar()

st.header("📝 NLP Summary Panel")
st.write("AI-powered analysis of clinical notes and patient summaries.")

nlp_patient = st.selectbox(
    "Select Patient for Analysis",
    options=list(st.session_state.patients_data.keys()),
    format_func=lambda x: f"{x} - {st.session_state.patients_data[x]['name']}"
)

if nlp_patient:
    patient = st.session_state.patients_data[nlp_patient]

    col1, col2 = st.columns([1, 1])

    with col1:
        st.subheader("Clinical Notes")
        for i, note in enumerate(patient['notes'], 1):
            st.text_area(f"Note {i}", note, height=80, disabled=True)

    with col2:
        st.subheader("AI Analysis Summary")
        st.markdown(
            """
            <div class="summary-panel">
            <h4>📊 Key Insights:</h4>
            <ul>
                <li><strong>Primary Concerns:</strong> Cardiovascular monitoring, blood pressure management</li>
                <li><strong>Treatment Response:</strong> Patient showing positive response to current regimen</li>
                <li><strong>Risk Factors:</strong> Elevated BP episodes, irregular heart rate patterns</li>
                <li><strong>Recommendations:</strong> Continue monitoring, consider medication adjustment</li>
            </ul>

            <h4>🔍 Sentiment Analysis:</h4>
            <p><span style="color: green;">●</span> Overall sentiment: <strong>Positive</strong> (Patient improving)</p>
            <p><span style="color: orange;">●</span> Concern level: <strong>Moderate</strong> (Requires monitoring)</p>

            <h4>📈 Trend Analysis:</h4>
            <p>Recent notes show improvement in patient condition with stable vitals and good treatment compliance.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.subheader("📌 Extracted Keywords")
        keywords = ["stable vitals", "medication",
                    "blood pressure", "monitoring", "improved", "comfortable"]
        keyword_cols = st.columns(3)
        for i, keyword in enumerate(keywords):
            with keyword_cols[i % 3]:
                st.code(keyword)

    st.subheader("🕒 Clinical Timeline")
    timeline_data = {
        'Date': pd.date_range(start=datetime.now() - timedelta(days=5), periods=6, freq='D'),
        'Event': [
            'Patient admitted',
            'Initial assessment completed',
            'Medication started',
            'Vitals stabilizing',
            'Family consultation',
            'Discharge planning initiated',
        ],
        'Severity': ['High', 'Medium', 'Low', 'Low', 'Low', 'Low'],
    }

    timeline_df = pd.DataFrame(timeline_data)
    fig = px.scatter(timeline_df, x='Date', y='Event',
                     color='Severity', title="Patient Care Timeline", height=300)
    st.plotly_chart(fig, use_container_width=True)
