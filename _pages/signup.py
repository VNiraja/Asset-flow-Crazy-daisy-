"""
Signup page for AssetFlow
Handles new user registration
"""

import streamlit as st
from utils.auth import auth_manager
from utils.validators import validate_full_name, validate_email, validate_password


def show_signup_page():
    """Display signup page"""

    # Custom CSS for styling
    st.markdown("""
        <style>
            .signup-container {
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
        st.title("📝 AssetFlow")
        st.markdown("Create Your Account")
        st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Signup form
    with st.form("signup_form", clear_on_submit=True):
        st.subheader("Register New Account")
        
        full_name = st.text_input(
            label="Full Name",
            placeholder="Enter your full name",
            key="signup_full_name"
        )
        
        email = st.text_input(
            label="Email Address",
            placeholder="Enter your email",
            key="signup_email"
        )
        
        password = st.text_input(
            label="Password",
            type="password",
            placeholder="Enter your password",
            key="signup_password",
            help="Minimum 8 characters, one uppercase, one lowercase, one digit, one special character"
        )
        
        confirm_password = st.text_input(
            label="Confirm Password",
            type="password",
            placeholder="Confirm your password",
            key="signup_confirm_password"
        )
        
        role = st.selectbox(
            label="Account Role",
            options=["employee", "admin"],
            format_func=lambda x: x.capitalize(),
            key="signup_role"
        )
        
        # Password requirements
        with st.expander("📋 Password Requirements"):
            st.markdown("""
            Your password must contain:
            - **Minimum 8 characters** in length
            - **At least 1 uppercase letter** (A-Z)
            - **At least 1 lowercase letter** (a-z)
            - **At least 1 digit** (0-9)
            - **At least 1 special character** (!@#$%^&*(),.?\":{}|<>)
            """)
        
        submit_button = st.form_submit_button(
            label="✅ Create Account",
            use_container_width=True
        )
        
        if submit_button:
            # Validate all fields
            errors = []
            
            # Validate full name
            is_valid, error_msg = validate_full_name(full_name)
            if not is_valid:
                errors.append(error_msg)
            
            # Validate email
            is_valid, error_msg = validate_email(email)
            if not is_valid:
                errors.append(error_msg)
            
            # Check if passwords match
            if password != confirm_password:
                errors.append("Passwords do not match")
            
            # Validate password
            is_valid, error_msg = validate_password(password)
            if not is_valid:
                errors.append(error_msg)
            
            # Display errors
            if errors:
                for error in errors:
                    st.error(f"❌ {error}")
            else:
                # Attempt signup
                success, message = auth_manager.signup(full_name, email, password, role)
                
                if success:
                    st.success("✅ Account created successfully! Logging you in...")
                    st.balloons()
                    
                    # Auto-login and redirect
                    import time
                    time.sleep(1)
                    
                    # Log the user in
                    login_success, msg, user_data = auth_manager.login(email, password)
                    if login_success and user_data:
                        st.session_state.logged_in = True
                        st.session_state.user_id = user_data.get('user_id')
                        st.session_state.username = user_data.get('full_name') or user_data.get('name')
                        st.session_state.role = user_data.get('role')
                        st.session_state.email = user_data.get('email')
                        st.session_state.page = "dashboard"
                    else:
                        st.session_state.page = "login"
                        
                    st.rerun()
                else:
                    st.error(f"❌ {message}")
    
    # Login section
    st.markdown("---")
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col2:
        st.markdown("### Already have an account?")
        if st.button("🔓 Login Here", use_container_width=True):
            st.session_state.page = "login"
            st.rerun()
    
    # Footer
    st.markdown("---")
    st.markdown(
        "<p style='text-align: center; color: #999;'>AssetFlow v1.0 | Secure Registration</p>",
        unsafe_allow_html=True
    )


if __name__ == "__main__":
    show_signup_page()
