import streamlit as st

DEFAULTS = {
    "session_id": None,        # backend session
    "role": None,              # "doctor" | "assistant"
    "passed_loader": False,    # CSV gate
    "patients_data": {},       # { uid: {...} }
    "vitals_data": {},         # optional cache for trends
}


def ensure_keys():
    for k, v in DEFAULTS.items():
        if k not in st.session_state:
            st.session_state[k] = v
