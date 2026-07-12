"""
AssetFlow - Authentication Module
Main application entry point
"""

import streamlit as st
from pages.login import show_login_page
from pages.signup import show_signup_page
from pages.dashboard import show_dashboard
from pages.admin import show_admin_page


def initialize_session_state():
    """Initialize session state variables"""
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
    if 'user_id' not in st.session_state:
        st.session_state.user_id = None
    if 'username' not in st.session_state:
        st.session_state.username = None
    if 'role' not in st.session_state:
        st.session_state.role = None
    if 'email' not in st.session_state:
        st.session_state.email = None
    if 'login_time' not in st.session_state:
        st.session_state.login_time = None
    if 'page' not in st.session_state:
        st.session_state.page = 'login'


def show_navbar():
    """Display navigation bar"""
    if st.session_state.logged_in:
        with st.sidebar:
            st.markdown("---")
            st.write(f"### 👤 {st.session_state.username}")
            st.write(f"📧 {st.session_state.email}")
            st.write(f"**Role:** {st.session_state.role.upper()}")
            st.markdown("---")
            
            # Navigation menu
            st.subheader("📍 Navigation")
            
            col1, col2 = st.columns([1, 1])
            
            with col1:
                if st.button("📊 Dashboard", use_container_width=True, key="nav_dashboard"):
                    st.session_state.page = "dashboard"
                    st.rerun()
            
            if st.session_state.role == 'admin':
                with col2:
                    if st.button("⚙️ Admin", use_container_width=True, key="nav_admin"):
                        st.session_state.page = "admin"
                        st.rerun()
            
            st.markdown("---")
            
            if st.button("🚪 Logout", use_container_width=True, key="navbar_logout"):
                st.session_state.logged_in = False
                st.session_state.user_id = None
                st.session_state.username = None
                st.session_state.role = None
                st.session_state.email = None
                st.session_state.login_time = None
                st.session_state.page = "login"
                st.rerun()
            
            st.markdown("---")
            st.markdown(
                "<p style='text-align: center; color: #999; font-size: 0.8rem;'>AssetFlow v1.0</p>",
                unsafe_allow_html=True
            )


def main():
    """Main application"""
    
    # Initialize session state
    initialize_session_state()
    
    # Show navbar if logged in
    show_navbar()
    
    # Route to appropriate page
    if not st.session_state.logged_in:
        if st.session_state.page == "signup":
            show_signup_page()
        else:
            show_login_page()
    else:
        # User is logged in - show appropriate page
        if st.session_state.page == "admin":
            if st.session_state.role == "admin":
                show_admin_page()
            else:
                st.error("❌ You are not authorized.")
                st.session_state.page = "dashboard"
                st.rerun()
        else:
            # Default to dashboard
            st.session_state.page = "dashboard"
            show_dashboard()


if __name__ == "__main__":
    main()
