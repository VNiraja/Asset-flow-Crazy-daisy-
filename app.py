import streamlit as st
from pages.login import show_login_page
from pages.signup import show_signup_page
import utils.db as db

st.set_page_config(page_title="AssetFlow", page_icon="💼", layout="wide")

def initialize_session_state():
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
    if 'user_id' not in st.session_state:
        st.session_state.user_id = None
    if 'username' not in st.session_state:
        st.session_state.username = None
    if 'role' not in st.session_state:
        st.session_state.role = None
    if 'page' not in st.session_state:
        st.session_state.page = 'login'

def show_navbar():
    if st.session_state.logged_in:
        with st.sidebar:
            st.title("AssetFlow 💼")
            st.markdown("---")
            st.write(f"**User:** {st.session_state.username}")
            st.write(f"**Role:** {st.session_state.role.upper()}")
            st.markdown("---")
            
            st.subheader("Navigation")
            if st.button("🏠 Dashboard", use_container_width=True):
                st.session_state.page = "dashboard"
                st.rerun()
            if st.button("📦 Assets", use_container_width=True):
                st.session_state.page = "assets"
                st.rerun()
            if st.button("👤 Allocation", use_container_width=True):
                st.session_state.page = "allocation"
                st.rerun()
            if st.button("🔧 Maintenance", use_container_width=True):
                st.session_state.page = "maintenance"
                st.rerun()
            if st.button("📊 Reports", use_container_width=True):
                st.session_state.page = "reports"
                st.rerun()
            
            st.markdown("---")
            if st.button("🚪 Logout", use_container_width=True):
                st.session_state.logged_in = False
                st.session_state.user_id = None
                st.session_state.username = None
                st.session_state.role = None
                st.session_state.page = "login"
                st.rerun()

def main():
    initialize_session_state()
    show_navbar()
    
    if not st.session_state.logged_in:
        if st.session_state.page == "signup":
            show_signup_page()
        else:
            show_login_page()
    else:
        # User is logged in
        if st.session_state.page == "dashboard":
            from pages.dashboard import show_dashboard
            show_dashboard()
        elif st.session_state.page == "assets":
            from pages.assets import show_assets
            show_assets()
        elif st.session_state.page == "allocation":
            from pages.allocation import show_allocation
            show_allocation()
        elif st.session_state.page == "maintenance":
            from pages.maintenance import show_maintenance
            show_maintenance()
        elif st.session_state.page == "reports":
            from pages.reports import show_reports
            show_reports()
        else:
            from pages.dashboard import show_dashboard
            show_dashboard()

if __name__ == "__main__":
    main()
