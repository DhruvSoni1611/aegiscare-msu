import streamlit as st
import time
from utils.api import post, get
from components.navbar import render_navbar  # if you already have one

st.set_page_config(page_title="AegisCare", layout="wide")

if "session_id" not in st.session_state:
    st.session_state.session_id = None
if "role" not in st.session_state:
    st.session_state.role = None
if "passed_loader" not in st.session_state:
    st.session_state.passed_loader = False
if "upload_status" not in st.session_state:
    st.session_state.upload_status = None

st.title("🏥 AegisCare - Healthcare Analytics Platform")

# Authentication tabs
tab_reg, tab_log = st.tabs(["Register", "Login"])

with tab_reg:
    st.subheader("Create Account")
    with st.form("reg"):
        email = st.text_input("Email")
        full_name = st.text_input("Full Name")
        password = st.text_input("Password", type="password")
        role = st.selectbox("Role", ["doctor", "assistant"])
        submit = st.form_submit_button("Register")

    if submit:
        if email and full_name and password:
            r = post("/auth/register", json={
                "email": email,
                "full_name": full_name,
                "password": password,
                "role": role
            })
            if r.ok:
                data = r.json()
                st.session_state.session_id = data["session_id"]
                st.session_state.role = data["role"]
                st.success("✅ Registration successful! You are now logged in.")
                st.experimental_rerun()
            else:
                st.error(f"❌ Registration failed: {r.text}")
        else:
            st.error("Please fill in all fields")

with tab_log:
    st.subheader("Login")
    with st.form("log"):
        email = st.text_input("Email", key="lemail")
        password = st.text_input("Password", type="password", key="lpass")
        submit = st.form_submit_button("Login")

    if submit:
        if email and password:
            r = post("/auth/login",
                     json={"email": email, "password": password})
            if r.ok:
                data = r.json()
                st.session_state.session_id = data["session_id"]
                st.session_state.role = data["role"]
                st.success("✅ Login successful!")
                st.experimental_rerun()
            else:
                st.error(f"❌ Login failed: {r.text}")
        else:
            st.error("Please enter email and password")

# CSV Upload Section - Only show if logged in but haven't uploaded yet
if st.session_state.session_id and not st.session_state.passed_loader:
    st.divider()
    st.subheader("📊 Data Setup Required")
    st.info("""
    **Welcome to AegisCare!** Before accessing the dashboard, you need to upload patient data.
    
    **Supported CSV Format:**
    - patient_uid, first_name, last_name, age, sex, contact_phone
    - height_cm, weight_kg, bmi
    - bp_sys, bp_dia, hr, cholesterol, glucose, temperature, oxygen_saturation, respiratory_rate
    
    **Note:** This process only needs to be done once. Your data will be processed and stored for analysis.
    """)

    uploaded_file = st.file_uploader(
        "Upload Patient CSV File",
        type=["csv"],
        help="Upload a CSV file with patient data and vital signs"
    )

    if uploaded_file is not None:
        col1, col2 = st.columns([1, 3])
        with col1:
            if st.button("🚀 Process Data", type="primary"):
                st.session_state.upload_status = "processing"

        with col2:
            if st.session_state.upload_status == "processing":
                with st.spinner("Processing your data..."):
                    try:
                        # Upload file to backend
                        r = post(
                            "/uploads/csv", files={"f": (uploaded_file.name, uploaded_file.getvalue(), "text/csv")})

                        if r.ok:
                            data = r.json()
                            st.session_state.upload_status = "completed"
                            st.session_state.passed_loader = True
                            st.success(f"""
                            ✅ **Data Processing Complete!**
                            
                            - **Patients Processed:** {data.get('patients_processed', 0)}
                            - **Rows Parsed:** {data.get('rows_parsed', 0)}
                            - **Data Loaded:** {data.get('rows_loaded', 0)}
                            
                            You can now access the dashboard from the sidebar.
                            """)
                            st.experimental_rerun()
                        else:
                            st.session_state.upload_status = "failed"
                            st.error(f"❌ Upload failed: {r.text}")
                    except Exception as e:
                        st.session_state.upload_status = "failed"
                        st.error(f"❌ Error during processing: {str(e)}")

# Main Application - Show after CSV upload
if st.session_state.session_id and st.session_state.passed_loader:
    st.divider()

    # Role-based navigation
    if st.session_state.role == "assistant":
        st.info(
            "👨‍⚕️ **Assistant Role:** You have access to Dashboard Overview and Seed Data pages.")
        allowed_pages = ["1_Dashboard_Overview", "5_Seed_Patients"]
    else:
        st.success(
            "👨‍⚕️ **Doctor Role:** You have access to all features including advanced analytics.")
        allowed_pages = [
            "1_Dashboard_Overview",
            "2_Patient_Vitals_Trends",
            "3_What_If_Simulator",
            "4_NLP_Summary_Panel",
            "5_Seed_Patients",
            "6_Advanced_Analytics"
        ]

    # Render navbar with allowed pages
    if 'render_navbar' in globals():
        render_navbar(allowed_pages)
    else:
        st.sidebar.success("✅ Data loaded successfully!")
        st.sidebar.info(f"Role: {st.session_state.role.title()}")

        # Quick navigation
        st.sidebar.subheader("Quick Navigation")
        for page in allowed_pages:
            if st.sidebar.button(f"📊 {page.replace('_', ' ').title()}"):
                st.switch_page(f"pages/{page}.py")
