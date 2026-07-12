import streamlit as st
import sys
import os
import datetime

# Ensure the parent directory is in sys.path to import utils
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from utils import db

st.set_page_config(page_title="Maintenance Management", layout="wide")
st.title("Maintenance Management")

# Ensure tables exist
db.create_tables()

tab1, tab2 = st.tabs(["Add Maintenance Record", "Maintenance History"])

with tab1:
    st.header("Add New Maintenance Record")
    
    with st.form("maintenance_form"):
        col1, col2 = st.columns(2)
        with col1:
            asset_id = st.number_input("Asset ID", min_value=1, step=1)
            maintenance_date = st.date_input("Maintenance Date", value=datetime.date.today())
            status = st.selectbox("Status", options=["Scheduled", "In Progress", "Completed"])
        with col2:
            cost = st.number_input("Cost ($)", min_value=0.0, step=0.01, format="%.2f")
            description = st.text_area("Description")
            
        submitted = st.form_submit_button("Add Record")
        
        if submitted:
            if cost < 0:
                st.error("Maintenance cost cannot be negative.")
            elif not description.strip():
                st.error("Description cannot be empty.")
            else:
                success = db.add_maintenance(
                    asset_id=int(asset_id),
                    maintenance_date=str(maintenance_date),
                    description=description.strip(),
                    cost=float(cost),
                    status=status
                )
                if success:
                    st.success("Maintenance record added successfully.")
                else:
                    st.error("Failed to add maintenance record.")

with tab2:
    st.header("Maintenance History")
    
    with st.expander("Search Filters"):
        col1, col2 = st.columns(2)
        with col1:
            search_asset_id = st.number_input("Search by Asset ID (0 for all)", min_value=0, step=1, value=0)
        with col2:
            search_status = st.selectbox("Filter by Status", options=["All", "Scheduled", "In Progress", "Completed"])
            
    if search_asset_id > 0 or search_status != "All":
        df = db.search_maintenance(
            asset_id=search_asset_id if search_asset_id > 0 else None,
            status=search_status
        )
    else:
        df = db.get_maintenance_history()
        
    st.dataframe(df, use_container_width=True, hide_index=True)
