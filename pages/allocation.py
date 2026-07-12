import streamlit as st
import sys
import os
import datetime

# Ensure the parent directory is in sys.path to import utils
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from utils import resource_db as db

st.set_page_config(page_title="Resource Allocation", layout="wide")
st.title("Resource Allocation")

# Ensure tables exist
db.create_tables()

tab1, tab2, tab3 = st.tabs(["Assign Asset", "Return Asset", "Allocation History"])

with tab1:
    st.header("Assign Asset to Employee")
    available_assets = db.get_available_assets()
    
    with st.form("assign_form"):
        col1, col2 = st.columns(2)
        with col1:
            asset_id = st.selectbox("Select Available Asset ID", options=available_assets)
            assigned_date = st.date_input("Assigned Date", value=datetime.date.today())
        with col2:
            employee_name = st.text_input("Employee Name")
            
        submitted = st.form_submit_button("Assign")
        
        if submitted:
            if not employee_name.strip():
                st.error("Employee name cannot be empty.")
            elif asset_id is None:
                st.error("No asset selected.")
            else:
                success = db.assign_asset(asset_id, employee_name.strip(), str(assigned_date))
                if success:
                    st.success(f"Asset {asset_id} successfully assigned to {employee_name.strip()}.")
                else:
                    st.error("Failed to assign asset. It might already be assigned.")

with tab2:
    st.header("Return Asset")
    allocated_assets = db.get_allocated_assets()
    options = {f"Allocation {a_id} - Asset {asset_id}": a_id for a_id, asset_id in allocated_assets}
    
    with st.form("return_form"):
        selected_option = st.selectbox("Select Currently Assigned Asset", options=list(options.keys()))
        returned_date = st.date_input("Returned Date", value=datetime.date.today())
        
        submitted = st.form_submit_button("Return Asset")
        
        if submitted:
            if not selected_option:
                st.error("No asset selected.")
            else:
                alloc_id = options[selected_option]
                success = db.return_asset(alloc_id, str(returned_date))
                if success:
                    st.success("Asset successfully returned.")
                else:
                    st.error("Failed to return asset. It might already be returned.")

with tab3:
    st.header("Allocation History")
    
    with st.expander("Search Filters"):
        col1, col2 = st.columns(2)
        with col1:
            search_asset_id = st.number_input("Search by Asset ID", min_value=0, step=1, value=0)
        with col2:
            search_employee = st.text_input("Search by Employee Name")
            
    if search_asset_id > 0 or search_employee:
        df = db.search_allocations(
            asset_id=search_asset_id if search_asset_id > 0 else None,
            employee_name=search_employee
        )
    else:
        df = db.get_allocation_history()
        
    st.dataframe(df, use_container_width=True, hide_index=True)
