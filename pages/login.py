"""
Login page for AssetFlow
Handles user authentication
"""

import streamlit as st
from utils.auth import auth_manager
from datetime import datetime


def show_login_page():
    """Display login page"""
    
    # Set page configuration
    st.set_page_config(
        page_title="AssetFlow - Login",
        page_icon="🔐",
        layout="centered"
    )
    
    # Custom CSS for styling
    st.markdown("""
        <style>
            .login-container {
                max-width: 400px;
                margin: 0 auto;
                padding: 2rem;
            }
            .header {
                text-align: center;
                margin-bottom: 2rem;
            }
            .header h1 {
                color: #1f77b4;
                margin: 0;
            }
            .header p {
                color: #666;
                margin-top: 0.5rem;
            }
        </style>
    """, unsafe_allow_html=True)
    
    # Header
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown('<div class="header">', unsafe_allow_html=True)
        st.title("🔐 AssetFlow")
        st.markdown("Authentication System")
        st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Login form
    with st.form("login_form", clear_on_submit=True):
        st.subheader("Login to Your Account")
        
        email = st.text_input(
            label="Email Address",
            placeholder="Enter your email",
            key="login_email"
        )
        
        password = st.text_input(
            label="Password",
            type="password",
            placeholder="Enter your password",
            key="login_password"
        )
        
        submit_button = st.form_submit_button(
            label="🔓 Login",
            use_container_width=True
        )
        
        if submit_button:
            if not email or not password:
                st.error("⚠️ Please enter both email and password")
            else:
                # Attempt login
                success, message, user_data = auth_manager.login(email, password)
                
                if success:
                    # Store user session
                    st.session_state.logged_in = True
                    st.session_state.user_id = user_data['user_id']
                    st.session_state.username = user_data['username']
                    st.session_state.role = user_data['role']
                    st.session_state.email = user_data['email']
                    st.session_state.login_time = datetime.now().isoformat()
                    
                    st.success("✅ Login successful! Redirecting...")
                    st.rerun()
                else:
                    st.error(f"❌ {message}")
    
    # Sign up section
    st.markdown("---")
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col2:
        st.markdown("### Don't have an account?")
        if st.button("📝 Sign Up Here", use_container_width=True):
            st.session_state.page = "signup"
            st.rerun()
    
    # Footer
    st.markdown("---")
    st.markdown(
        "<p style='text-align: center; color: #999;'>AssetFlow v1.0 | Secure Authentication</p>",
        unsafe_allow_html=True
    )


if __name__ == "__main__":
    show_login_page()
