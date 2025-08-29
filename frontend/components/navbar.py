import streamlit as st


def render_navbar():
    st.sidebar.title("🏥 Navigation")
    st.sidebar.success("Logged in ✅")

    page = st.sidebar.radio(
        "Go to:",
        [
            "Dashboard Overview",
            "Patient Vitals Trends",
            "What-If Simulator",
            "NLP Summary Panel",
            "Seed Patients",
            "Advanced Analytics"
        ]
    )

    st.session_state.current_page = page
