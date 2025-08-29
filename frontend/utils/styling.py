import streamlit as st


def apply_custom_css():
    st.markdown("""
    <style>
        .main-header {
            font-size: 2.5rem;
            font-weight: 700;
            color: #1f77b4;
            text-align: center;
            margin-bottom: 2rem;
        }
        .metric-card {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 1rem;
            border-radius: 10px;
            color: white;
            text-align: center;
            margin: 0.5rem 0;
        }
        .alert-high {
            background-color: #ff4444;
            color: white;
            padding: 0.5rem;
            border-radius: 5px;
            margin: 0.25rem 0;
        }
        .alert-normal {
            background-color: #00aa44;
            color: white;
            padding: 0.5rem;
            border-radius: 5px;
            margin: 0.25rem 0;
        }
        .summary-panel {
            background-color: #f8f9fa;
            border-left: 4px solid #1f77b4;
            padding: 1rem;
            border-radius: 0 8px 8px 0;
        }
    </style>
    """, unsafe_allow_html=True)
