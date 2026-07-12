import streamlit as st
import pandas as pd
from utils.db import db
import uuid

def show_assets():
    st.title("📦 Asset Management")
    
    tab1, tab2, tab3 = st.tabs(["View Assets", "Add Asset", "Search Asset"])
    
    with tab1:
        st.subheader("All Assets")
        try:
            conn = db.get_connection()
            df = pd.read_sql("SELECT * FROM assets", conn)
            conn.close()
            if df.empty:
                st.info("No assets found.")
            else:
                st.dataframe(df, use_container_width=True)
        except Exception as e:
            st.error(f"Error fetching assets: {e}")
            
    with tab2:
        st.subheader("Add New Asset")
        with st.form("add_asset_form"):
            a_name = st.text_input("Asset Name")
            category = st.selectbox("Category", ["Laptops", "Desktops", "Monitors", "Peripherals"])
            purchase_date = st.date_input("Purchase Date")
            cost = st.number_input("Cost ($)", min_value=0.0)
            status = st.selectbox("Status", ["Available", "Assigned", "Under Maintenance", "Retired"])
            location = st.text_input("Location")
            
            if st.form_submit_button("Add Asset"):
                if a_name and location:
                    a_id = f"AST-{str(uuid.uuid4())[:8]}"
                    try:
                        conn = db.get_connection()
                        c = conn.cursor()
                        c.execute('''INSERT INTO assets 
                                     (asset_id, asset_name, category, purchase_date, cost, status, location)
                                     VALUES (?, ?, ?, ?, ?, ?, ?)''',
                                  (a_id, a_name, category, str(purchase_date), cost, status, location))
                        conn.commit()
                        conn.close()
                        st.success("Asset added successfully!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error adding asset: {e}")
                else:
                    st.error("Please fill all required fields.")
                    
    with tab3:
        st.subheader("Search & Delete")
        search_query = st.text_input("Search by Asset ID or Name")
        if search_query:
            try:
                conn = db.get_connection()
                df = pd.read_sql(f"SELECT * FROM assets WHERE asset_name LIKE '%{search_query}%' OR asset_id LIKE '%{search_query}%'", conn)
                conn.close()
                st.dataframe(df, use_container_width=True)
            except Exception as e:
                st.error(f"Error searching: {e}")
