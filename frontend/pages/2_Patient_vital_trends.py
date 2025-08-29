import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from utils.styling import apply_custom_css
from components.navbar import render_navbar
from utils.analysis import analyze_vitals_trends
import pandas as pd

apply_custom_css()
st.markdown('<h1 class="main-header">Healthcare Analytics Dashboard</h1>',
            unsafe_allow_html=True)
render_navbar()


st.header("📈 Patient Vitals Trends")


selected_patient = st.selectbox(
    "Select Patient",
    options=list(st.session_state.patients_data.keys()),
    format_func=lambda x: f"{x} - {st.session_state.patients_data[x]['name']}"
)

if selected_patient:
    patient = st.session_state.patients_data[selected_patient]
    vitals_df: pd.DataFrame = patient['vitals']

    col1, col2, col3 = st.columns(3)
    col1.metric("Age", patient['age'])
    col2.metric("Gender", patient['gender'])
    col3.metric("Condition", patient['condition'])

    trends = analyze_vitals_trends(vitals_df)

    st.subheader("Current Vital Signs")
    vital_cols = st.columns(5)

    vitals_display = [
        ("Heart Rate", "heart_rate", "bpm"),
        ("Systolic BP", "blood_pressure_sys", "mmHg"),
        ("Diastolic BP", "blood_pressure_dia", "mmHg"),
        ("Temperature", "temperature", "°F"),
        ("O2 Saturation", "oxygen_saturation", "%"),
    ]

    for i, (label, key, unit) in enumerate(vitals_display):
        trend_data = trends[key]
        status_color = "🔴" if trend_data['status'] in ['HIGH', 'LOW'] else "🟢"
        trend_arrow = "📈" if trend_data['trend'] == 'UP' else "📉" if trend_data['trend'] == 'DOWN' else "➡"

        vital_cols[i].metric(
            f"{status_color} {label}",
            f"{trend_data['current']:.1f} {unit}",
            delta=f"{trend_arrow} vs avg",
        )

        st.subheader("Trends Over Time")

        fig = make_subplots(
            rows=3, cols=2,
            subplot_titles=('Heart Rate', 'Blood Pressure', 'Temperature',
                            'Oxygen Saturation', 'Vital Signs Correlation'),
            specs=[[{"secondary_y": False}, {"secondary_y": False}],
                   [{"secondary_y": False}, {"secondary_y": False}],
                   [{"colspan": 2}, None]],
            vertical_spacing=0.08,
        )

        fig.add_trace(
            go.Scatter(x=vitals_df['timestamp'],
                       y=vitals_df['heart_rate'], name='Heart Rate'),
            row=1, col=1,
        )

        fig.add_trace(
            go.Scatter(
                x=vitals_df['timestamp'], y=vitals_df['blood_pressure_sys'], name='Systolic'),
            row=1, col=2,
        )
        fig.add_trace(
            go.Scatter(
                x=vitals_df['timestamp'], y=vitals_df['blood_pressure_dia'], name='Diastolic'),
            row=1, col=2,
        )

        fig.add_trace(
            go.Scatter(x=vitals_df['timestamp'],
                       y=vitals_df['temperature'], name='Temperature'),
            row=2, col=1,
        )

        fig.add_trace(
            go.Scatter(x=vitals_df['timestamp'],
                       y=vitals_df['oxygen_saturation'], name='O2 Sat'),
            row=2, col=2,
        )

        corr_data = vitals_df[[
            'heart_rate', 'blood_pressure_sys', 'temperature', 'oxygen_saturation']].corr()
        fig.add_trace(
            go.Heatmap(z=corr_data.values, x=corr_data.columns,
                       y=corr_data.columns, name='Correlation'),
            row=3, col=1,
        )

        fig.update_layout(height=800, showlegend=True,
                          title_text="Patient Vitals Analysis")
        st.plotly_chart(fig, use_container_width=True)


st.subheader("Trends Over Time")


fig = make_subplots(
    rows=3, cols=2,
    subplot_titles=('Heart Rate', 'Blood Pressure', 'Temperature',
                    'Oxygen Saturation', 'Vital Signs Correlation'),
    specs=[[{"secondary_y": False}, {"secondary_y": False}],
           [{"secondary_y": False}, {"secondary_y": False}],
           [{"colspan": 2}, None]],
    vertical_spacing=0.08,
)


fig.add_trace(
    go.Scatter(x=vitals_df['timestamp'],
               y=vitals_df['heart_rate'], name='Heart Rate'),
    row=1, col=1,
)


fig.add_trace(
    go.Scatter(x=vitals_df['timestamp'],
               y=vitals_df['blood_pressure_sys'], name='Systolic'),
    row=1, col=2,
)
fig.add_trace(
    go.Scatter(x=vitals_df['timestamp'],
               y=vitals_df['blood_pressure_dia'], name='Diastolic'),
    row=1, col=2,
)


fig.add_trace(
    go.Scatter(x=vitals_df['timestamp'],
               y=vitals_df['temperature'], name='Temperature'),
    row=2, col=1,
)


fig.add_trace(
    go.Scatter(x=vitals_df['timestamp'],
               y=vitals_df['oxygen_saturation'], name='O2 Sat'),
    row=2, col=2,
)


corr_data = vitals_df[['heart_rate', 'blood_pressure_sys',
                       'temperature', 'oxygen_saturation']].corr()
fig.add_trace(
    go.Heatmap(z=corr_data.values, x=corr_data.columns,
               y=corr_data.columns, name='Correlation'),
    row=3, col=1,
)


fig.update_layout(height=800, showlegend=True,
                  title_text="Patient Vitals Analysis")
st.plotly_chart(fig, use_container_width=True)
