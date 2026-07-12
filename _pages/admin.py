"""
Admin page for AssetFlow
Admin panel for managing users
"""

import streamlit as st
import pandas as pd
from utils.db import db


def show_admin_page():
    """Display admin page"""

    # Check if user is logged in and has admin role
    if not st.session_state.get("logged_in", False):
        st.error("❌ You are not authorized to access this page")
        st.info("Please login first")
        st.stop()
    
    if st.session_state.get("role") != "admin":
        st.error("❌ You are not authorized.")
        st.warning("⚠️ Admin access required. Only administrators can access this page.")
        st.stop()
    
    # Custom CSS
    st.markdown("""
        <style>
            .admin-header {
                text-align: center;
                color: #FF6B6B;
                margin-bottom: 2rem;
            }
        </style>
    """, unsafe_allow_html=True)
    
    # Header
    st.markdown('<div class="admin-header">', unsafe_allow_html=True)
    st.title("⚙️ Admin Panel")
    st.markdown("Manage AssetFlow Users")
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Admin info
    st.info(f"👤 Logged in as: **{st.session_state.username}** (Admin)")
    
    st.markdown("---")
    
    # Tabs for different admin functions
    tab1, tab2, tab3 = st.tabs(["👥 All Users", "📊 Statistics", "🔧 Management"])
    
    # Tab 1: All Users
    with tab1:
        st.subheader("📋 Registered Users")
        
        try:
            # Get all users from database
            users = db.get_all_users()
            
            if users:
                # Create DataFrame
                df = pd.DataFrame(users)
                
                # Format the dataframe
                df_display = df.copy()
                
                # Rename columns for better display
                df_display = df_display.rename(columns={
                    'user_id': 'User ID',
                    'full_name': 'Full Name',
                    'email': 'Email',
                    'role': 'Role'
                })
                
                # Display dataframe
                st.dataframe(df_display, use_container_width=True, hide_index=True)
                
                # Show user count
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric("Total Users", len(users))
                
                with col2:
                    admin_count = len([u for u in users if u['role'] == 'admin'])
                    st.metric("Admins", admin_count)
                
                with col3:
                    employee_count = len([u for u in users if u['role'] == 'employee'])
                    st.metric("Employees", employee_count)
                
                with col4:
                    st.metric("Active", len(users))
            else:
                st.info("No users registered yet")
        
        except Exception as e:
            st.error(f"❌ Error loading users: {str(e)}")
    
    # Tab 2: Statistics
    with tab2:
        st.subheader("📊 User Statistics")
        
        try:
            users = db.get_all_users()
            
            if users:
                # User statistics
                total_users = len(users)
                admin_count = len([u for u in users if u['role'] == 'admin'])
                employee_count = len([u for u in users if u['role'] == 'employee'])
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("Total Users", total_users)
                
                with col2:
                    st.metric("Administrators", admin_count)
                
                with col3:
                    st.metric("Employees", employee_count)
                
                st.markdown("---")
                
                # Role distribution chart
                st.write("### Role Distribution")
                
                role_data = {
                    'Role': ['Admin', 'Employee'],
                    'Count': [admin_count, employee_count]
                }
                
                role_df = pd.DataFrame(role_data)
                st.bar_chart(role_df.set_index('Role'))
                
                st.markdown("---")
                
                # Recent registrations
                st.write("### Recent Registrations (Last 5)")
                
                recent_users = users[:5]
                
                if recent_users:
                    recent_df = pd.DataFrame(recent_users)
                    
                    recent_df_display = recent_df[['full_name', 'email', 'role']]
                    recent_df_display = recent_df_display.rename(columns={
                        'full_name': 'Full Name',
                        'email': 'Email',
                        'role': 'Role'
                    })
                    
                    st.dataframe(recent_df_display, use_container_width=True, hide_index=True)
            else:
                st.info("No users to display")
        
        except Exception as e:
            st.error(f"❌ Error loading statistics: {str(e)}")
    
    # Tab 3: Management
    with tab3:
        st.subheader("🔧 User Management")
        
        try:
            users = db.get_all_users()
            
            if users:
                # Create a selection for user management
                user_emails = [u['email'] for u in users]
                user_dict = {u['email']: u for u in users}
                
                selected_email = st.selectbox(
                    "Select user to manage",
                    user_emails,
                    key="user_select"
                )
                
                if selected_email:
                    user = user_dict[selected_email]
                    
                    st.write("---")
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.write("### User Details")
                        st.write(f"**Name:** {user['full_name']}")
                        st.write(f"**Email:** {user['email']}")
                        st.write(f"**Current Role:** {user['role'].upper()}")
                        st.write(f"**User ID:** {user['user_id']}")
                    
                    with col2:
                        st.write("### Management Actions")
                        
                        # Change role
                        if st.session_state.user_id != user['user_id']:  # Can't change own role
                            new_role = st.radio(
                                "Change Role:",
                                ["admin", "employee"],
                                index=0 if user['role'] == 'admin' else 1,
                                key=f"role_select_{user['user_id']}"
                            )
                            
                            if st.button(f"Update Role", key=f"update_btn_{user['user_id']}"):
                                success, message = db.update_user_role(user['user_id'], new_role)
                                if success:
                                    st.success(f"✅ {message}")
                                    st.rerun()
                                else:
                                    st.error(f"❌ {message}")
                        else:
                            st.info("ℹ️ You cannot change your own role")
                        
                        # Delete user
                        st.write("---")
                        
                        if st.session_state.user_id != user['user_id']:  # Can't delete self
                            if st.button(f"🗑️ Delete User", key=f"delete_btn_{user['user_id']}", help="This action cannot be undone"):
                                success, message = db.delete_user(user['user_id'])
                                if success:
                                    st.success(f"✅ {message}")
                                    st.rerun()
                                else:
                                    st.error(f"❌ {message}")
                        else:
                            st.info("ℹ️ You cannot delete your own account")
            else:
                st.info("No users to manage")
        
        except Exception as e:
            st.error(f"❌ Error in management section: {str(e)}")
    
    st.markdown("---")
    
    # Back button
    if st.button("← Back to Dashboard"):
        st.session_state.page = "dashboard"
        st.rerun()


if __name__ == "__main__":
    show_admin_page()
