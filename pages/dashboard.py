"""
Dashboard page for AssetFlow
Shows user information and welcome message
"""

import streamlit as st
from datetime import datetime


def show_dashboard():
    """Display dashboard page"""
    
    st.set_page_config(
        page_title="AssetFlow - Dashboard",
        page_icon="📊",
        layout="wide"
    )
    
    # Check if user is logged in
    if not st.session_state.get("logged_in", False):
        st.error("❌ You are not authorized to access this page")
        st.info("Please login first")
        st.stop()
    
    # Custom CSS
    st.markdown("""
        <style>
            .welcome-header {
                text-align: center;
                color: #1f77b4;
                margin-bottom: 2rem;
            }
            .info-card {
                background-color: #f0f2f6;
                padding: 1.5rem;
                border-radius: 0.5rem;
                margin: 1rem 0;
            }
        </style>
    """, unsafe_allow_html=True)
    
    # Header
    st.markdown('<div class="welcome-header">', unsafe_allow_html=True)
    st.title(f"👋 Welcome, {st.session_state.username}!")
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown("---")
    
    # User Information Section
    st.subheader("📋 Your Account Information")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### Account Details")
        st.info(f"""
        **Full Name:** {st.session_state.username}
        
        **Email:** {st.session_state.email}
        """)
    
    with col2:
        st.markdown("### Access Information")
        
        # Determine role badge
        role = st.session_state.get("role", "employee").upper()
        if role == "ADMIN":
            role_badge = "🔐 ADMIN"
            role_color = "#FF6B6B"
        else:
            role_badge = "👤 EMPLOYEE"
            role_color = "#4ECDC4"
        
        st.markdown(f"""
        **Role:** <span style='color: {role_color}; font-weight: bold;'>{role_badge}</span>
        
        **Login Time:** {st.session_state.login_time}
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Quick Stats
    st.subheader("📊 Quick Stats")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            label="User ID",
            value=st.session_state.user_id[:8] + "..."
        )
    
    with col2:
        st.metric(
            label="Account Status",
            value="Active"
        )
    
    with col3:
        st.metric(
            label="Role Level",
            value=st.session_state.get("role", "employee").capitalize()
        )
    
    st.markdown("---")
    
    # Available Features
    st.subheader("🎯 Available Features")
    
    features = []
    
    # All users can access dashboard
    features.append("✅ **Dashboard** - View your account information")
    
    # Admin-specific features
    if st.session_state.get("role") == "admin":
        features.append("✅ **Admin Panel** - Manage all users")
    
    for feature in features:
        st.write(feature)
    
    st.markdown("---")
    
    # Session Info
    with st.expander("ℹ️ Session Information"):
        st.write(f"**Session User ID:** {st.session_state.user_id}")
        st.write(f"**Session Created:** {st.session_state.login_time}")
        st.write(f"**Current Time:** {datetime.now().isoformat()}")
        st.write(f"**Session Status:** Active ✓")
    
    st.markdown("---")
    
    # Logout button
    st.markdown("### 🔓 Session Management")
    
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        if st.button("🚪 Logout", use_container_width=True, key="logout_btn"):
            # Clear session
            st.session_state.logged_in = False
            st.session_state.user_id = None
            st.session_state.username = None
            st.session_state.role = None
            st.session_state.email = None
            st.session_state.login_time = None
            
            st.success("✅ Logged out successfully")
            st.rerun()


if __name__ == "__main__":
    show_dashboard()
