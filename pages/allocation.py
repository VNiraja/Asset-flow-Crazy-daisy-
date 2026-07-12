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
