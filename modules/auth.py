import hashlib
import streamlit as st
from modules.data_manager import load_data, log_event

def hash_password(password):
    return hashlib.sha256(str.encode(password)).hexdigest()

def verify_password(stored_hash, provided_password):
    return stored_hash == hashlib.sha256(str.encode(provided_password)).hexdigest()

def login_sidebar():
    data = load_data()
    if "admin_logged_in" not in st.session_state:
        st.session_state["admin_logged_in"] = False

    if not st.session_state["admin_logged_in"]:
        with st.sidebar.expander("🔐 Admin Login", expanded=False):
            username_in = st.text_input("Username")
            password_in = st.text_input("Password", type="password")
            if st.button("Login"):
                success = False
                # Try master password if available in secrets
                try:
                    master_pass = st.secrets["passwords"]["admin_password"]
                    if username_in == "admin" and password_in == master_pass:
                        success = True
                except: pass 
                
                if not success:
                    admins = data.get("admins", {})
                    if username_in in admins and verify_password(admins[username_in], password_in):
                        success = True
                
                if success:
                    st.session_state["admin_logged_in"] = True
                    log_event(f"Admin login: {username_in}")
                    st.query_params["page"] = "admin"
                    st.rerun()
                else:
                    st.error("Invalid credentials")
    else:
        if st.sidebar.button("Logout"):
            st.session_state["admin_logged_in"] = False
            st.query_params["page"] = "home"
            st.rerun()
