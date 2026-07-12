import streamlit as st

st.set_page_config(
    page_title="Asset Management System",
    page_icon="💼",
)

st.title("💼 Asset Management System")
st.markdown(
    """
    Welcome to the Asset Management System.
    
    Please select a page from the sidebar to continue:
    - **Dashboard**: View high-level metrics, charts, and smart insights.
    - **Reports**: View detailed data, summary statistics, and export CSV reports.
    """
)
