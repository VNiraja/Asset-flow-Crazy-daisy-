import streamlit as st
import pandas as pd
from utils.db import db
import uuid

def show_allocation():
    st.title("👤 Resource Allocation")
    
    tab1, tab2 = st.tabs(["Assign Asset", "Allocation History"])
    
    with tab1:
        st.subheader("Assign Asset to Employee")
        try:
            conn = db.get_connection()
            assets_df = pd.read_sql("SELECT asset_id, asset_name FROM assets WHERE status = 'Available'", conn)
            conn.close()
            
            if assets_df.empty:
                st.warning("No available assets to assign.")
            else:
                with st.form("assign_form"):
                    asset_options = dict(zip(assets_df['asset_name'], assets_df['asset_id']))
                    selected_asset_name = st.selectbox("Select Asset", list(asset_options.keys()))
                    emp_name = st.text_input("Employee Name")
                    date = st.date_input("Assignment Date")
                    
                    if st.form_submit_button("Assign"):
                        if emp_name:
                            selected_id = asset_options[selected_asset_name]
                            alloc_id = f"ALL-{str(uuid.uuid4())[:8]}"
                            try:
                                conn = db.get_connection()
                                c = conn.cursor()
                                c.execute('''INSERT INTO allocations 
                                             (allocation_id, asset_id, employee_name, assigned_date, status)
                                             VALUES (?, ?, ?, ?, 'Active')''',
                                          (alloc_id, selected_id, emp_name, str(date)))
                                c.execute("UPDATE assets SET status = 'Assigned' WHERE asset_id = ?", (selected_id,))
                                conn.commit()
                                conn.close()
                                st.success("Asset assigned successfully!")
                                st.rerun()
                            except Exception as e:
                                st.error(f"Error: {e}")
                        else:
                            st.error("Employee Name is required.")
        except Exception as e:
            st.error(f"Error: {e}")

    with tab2:
        st.subheader("Allocation History & Returns")
        try:
            conn = db.get_connection()
            history_df = pd.read_sql("SELECT * FROM allocations", conn)
            
            if history_df.empty:
                st.info("No allocation history found.")
            else:
                st.dataframe(history_df, use_container_width=True)
                
                st.subheader("Return Asset")
                active_allocs = history_df[history_df['status'] == 'Active']
                if not active_allocs.empty:
                    with st.form("return_form"):
                        ret_alloc_id = st.selectbox("Select Allocation ID to Return", active_allocs['allocation_id'])
                        ret_date = st.date_input("Return Date")
                        if st.form_submit_button("Process Return"):
                            try:
                                asset_id = active_allocs[active_allocs['allocation_id'] == ret_alloc_id]['asset_id'].values[0]
                                c = conn.cursor()
                                c.execute("UPDATE allocations SET status = 'Returned', returned_date = ? WHERE allocation_id = ?", (str(ret_date), ret_alloc_id))
                                c.execute("UPDATE assets SET status = 'Available' WHERE asset_id = ?", (asset_id,))
                                conn.commit()
                                st.success("Asset returned successfully!")
                                st.rerun()
                            except Exception as e:
                                st.error(f"Error: {e}")
                else:
                    st.info("No active allocations to return.")
            conn.close()
        except Exception as e:
            st.error(f"Error: {e}")
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
