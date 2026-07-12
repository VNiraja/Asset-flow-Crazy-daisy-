import streamlit as st
import pandas as pd
from utils.db import db
import uuid

def show_maintenance():
    st.title("🔧 Maintenance Management")
    
    tab1, tab2 = st.tabs(["Log Maintenance", "Maintenance History"])
    
    with tab1:
        st.subheader("Log Asset Maintenance")
        try:
            conn = db.get_connection()
            assets_df = pd.read_sql("SELECT asset_id, asset_name FROM assets", conn)
            conn.close()
            
            if assets_df.empty:
                st.warning("No assets available.")
            else:
                with st.form("maint_form"):
                    asset_options = dict(zip(assets_df['asset_name'], assets_df['asset_id']))
                    selected_asset_name = st.selectbox("Select Asset", list(asset_options.keys()))
                    desc = st.text_area("Maintenance Description")
                    cost = st.number_input("Cost ($)", min_value=0.0)
                    date = st.date_input("Maintenance Date")
                    
                    if st.form_submit_button("Log Maintenance"):
                        if desc:
                            selected_id = asset_options[selected_asset_name]
                            m_id = f"MNT-{str(uuid.uuid4())[:8]}"
                            try:
                                conn = db.get_connection()
                                c = conn.cursor()
                                c.execute('''INSERT INTO maintenance 
                                             (maintenance_id, asset_id, maintenance_date, description, cost, status)
                                             VALUES (?, ?, ?, ?, ?, 'Completed')''',
                                          (m_id, selected_id, str(date), desc, cost))
                                c.execute("UPDATE assets SET status = 'Available' WHERE asset_id = ?", (selected_id,))
                                conn.commit()
                                conn.close()
                                st.success("Maintenance logged successfully!")
                            except Exception as e:
                                st.error(f"Error: {e}")
                        else:
                            st.error("Description is required.")
        except Exception as e:
            st.error(f"Error: {e}")

    with tab2:
        st.subheader("Maintenance Records")
        try:
            conn = db.get_connection()
            df = pd.read_sql("SELECT * FROM maintenance", conn)
            conn.close()
            if df.empty:
                st.info("No maintenance history found.")
            else:
                st.dataframe(df, use_container_width=True)
        except Exception as e:
            st.error(f"Error: {e}")
