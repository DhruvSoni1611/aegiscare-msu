import streamlit as st

DEFAULTS = {
    "session_id": None,        # backend session
    "role": None,              # "doctor" | "assistant"
    "passed_loader": False,    # CSV gate
    "patients_data": {},       # { uid: {...} }
    "vitals_data": {},         # optional cache for trends
    "show_new_patient_form": False,  # show/hide new patient form
    "show_add_note": False,    # show/hide add note form
}


def ensure_keys():
    for k, v in DEFAULTS.items():
        if k not in st.session_state:
            st.session_state[k] = v
