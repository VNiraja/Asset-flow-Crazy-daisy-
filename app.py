# Entry point for the AssetFlow Streamlit app
"""
AssetFlow - Authentication Module
Main application entry point
"""

import streamlit as st
from _pages.login import show_login_page
from _pages.signup import show_signup_page
from utils.db import db  # initialises the users DB on startup

st.set_page_config(page_title="AssetFlow", page_icon="💼", layout="wide")


def initialize_session_state():
    defaults = {
        'logged_in': False,
        'user_id':   None,
        'username':  None,
        'role':      None,
        'page':      'login',
    }
    for key, val in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val


def show_navbar():
    if not st.session_state.logged_in:
        return
    with st.sidebar:
        st.title("AssetFlow 💼")
        st.markdown("---")
        st.write(f"**User:** {st.session_state.username}")
        st.write(f"**Role:** {st.session_state.role.upper()}")
        st.markdown("---")

        st.subheader("Navigation")
        if st.button("🏠 Dashboard",   use_container_width=True): st.session_state.page = "dashboard";   st.rerun()
        if st.button("📦 Assets",      use_container_width=True): st.session_state.page = "assets";      st.rerun()
        if st.button("👤 Allocation",  use_container_width=True): st.session_state.page = "allocation";  st.rerun()
        if st.button("🔧 Maintenance", use_container_width=True): st.session_state.page = "maintenance"; st.rerun()
        if st.button("📊 Reports",     use_container_width=True): st.session_state.page = "reports";     st.rerun()

        if st.session_state.role == "admin":
            if st.button("⚙️ Admin Panel", use_container_width=True):
                st.session_state.page = "admin"
                st.rerun()

        st.markdown("---")
        if st.button("🚪 Logout", use_container_width=True):
            for key in ['logged_in', 'user_id', 'username', 'role']:
                st.session_state[key] = None if key != 'logged_in' else False
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
        page = st.session_state.page

        if page == "dashboard":
            from _pages.dashboard import show_dashboard
            show_dashboard()
        elif page == "assets":
            from _pages.assets import show_assets
            show_assets()
        elif page == "allocation":
            from _pages.allocation import show_allocation
            show_allocation()
        elif page == "maintenance":
            from _pages.maintenance import show_maintenance
            show_maintenance()
        elif page == "reports":
            from _pages.reports import show_reports
            show_reports()
        elif page == "admin":
            from _pages.admin import show_admin_page
            show_admin_page()
        else:
            from _pages.dashboard import show_dashboard
            show_dashboard()


if __name__ == "__main__":
    main()
