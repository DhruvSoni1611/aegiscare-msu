# import streamlit as st
# from components.navbar import render_navbar
# from utils.data import generate_sample_patients
# from utils.styling import apply_custom_css

# st.set_page_config(
#     page_title="AegisCare - Healthcare Dashboard",
#     page_icon="🏥",
#     layout="wide",
#     initial_sidebar_state="expanded"
# )

# # Apply styling
# apply_custom_css()

# # Session state initialization
# if 'patients_data' not in st.session_state:
#     st.session_state.patients_data = generate_sample_patients()

# if 'auth_token' not in st.session_state:
#     st.session_state.auth_token = None

# # Login / Register flow
# st.title("🔐 AegisCare Login")

# if not st.session_state.auth_token:
#     auth_mode = st.radio("Select mode", ["Login", "Register"])

#     if auth_mode == "Login":
#         username = st.text_input("Username")
#         password = st.text_input("Password", type="password")
#         if st.button("Login"):
#             # TODO: Replace with API call: POST /auth/login
#             if username and password:
#                 st.session_state.auth_token = "dummy_token"
#                 st.success("Login successful ✅")
#                 st.experimental_rerun()

#     elif auth_mode == "Register":
#         st.subheader("Register New Account")
#         with st.form("register_form"):
#             full_name = st.text_input("Full Name")
#             email = st.text_input("Email")
#             phone = st.text_input("Phone")
#             hospital = st.text_input("Hospital")
#             specialty = st.text_input("Specialty")
#             experience = st.number_input("Experience (years)", 0, 50)
#             username = st.text_input("Username")
#             password = st.text_input("Password", type="password")
#             confirm = st.text_input("Confirm Password", type="password")

#             submitted = st.form_submit_button("Register")
#             if submitted:
#                 # TODO: Replace with API call: POST /auth/register
#                 if password == confirm:
#                     st.success("Registration successful ✅ Please login")
#                 else:
#                     st.error("Passwords do not match!")

# else:
#     # Show Navbar + redirect to selected module
#     render_navbar()

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

st.title("AegisCare")

tab_reg, tab_log = st.tabs(["Register", "Login"])

with tab_reg:
    st.subheader("Create account")
    with st.form("reg"):
        email = st.text_input("Email")
        full_name = st.text_input("Full name")
        password = st.text_input("Password", type="password")
        role = st.selectbox("Role", ["doctor", "assistant"])
        submit = st.form_submit_button("Register")
    if submit:
        r = post("/auth/register", json={"email": email,
                 "full_name": full_name, "password": password, "role": role})
        if r.ok:
            data = r.json()
            st.session_state.session_id = data["session_id"]
            st.session_state.role = data["role"]
            st.success("Registered & logged in.")
        else:
            st.error(r.text)

with tab_log:
    st.subheader("Login")
    with st.form("log"):
        email = st.text_input("Email", key="lemail")
        password = st.text_input("Password", type="password", key="lpass")
        submit = st.form_submit_button("Login")
    if submit:
        r = post("/auth/login", json={"email": email, "password": password})
        if r.ok:
            data = r.json()
            st.session_state.session_id = data["session_id"]
            st.session_state.role = data["role"]
            st.success("Logged in.")
        else:
            st.error(r.text)

# Gate: CSV upload before showing dashboard
if st.session_state.session_id and not st.session_state.passed_loader:
    st.info("Before proceeding, upload patient CSV (seed data).")
    f = st.file_uploader("Upload CSV", type=["csv"])
    if f is not None:
        with st.spinner("Uploading & processing... (fixed 15 seconds)"):
            r = post("/uploads/csv",
                     files={"f": (f.name, f.getvalue(), "text/csv")})
            # fixed 15-second loader
            for _ in range(15):
                time.sleep(1)
            if r.ok:
                st.session_state.passed_loader = True
                st.success("Data processed. Open Dashboard from sidebar.")
            else:
                st.error(r.text)

# Optional navbar; gate links by role
if st.session_state.session_id and st.session_state.passed_loader:
    # Doctor: all pages; Assistant: dashboard + seed
    allowed_pages = ["1_Dashboard_Overview", "5_Seed_Patients"] if st.session_state.role == "assistant" else \
                    ["1_Dashboard_Overview", "2_Patient_Vitals_Trends", "3_What_If_Simulator",
                        "4_NLP_Summary_Panel", "5_Seed_Patients", "6_Advanced_Analytics"]
    # If your navbar supports allowed pages, pass it here
    if 'render_navbar' in globals():
        render_navbar(allowed_pages)
