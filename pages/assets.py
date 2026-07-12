import streamlit as st
import pandas as pd
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from utils.db import create_table, add_asset, get_all_assets

# Initialise DB on every page load (no-op if table already exists)
create_table()

CATEGORIES = ["Hardware", "Software", "Furniture", "Vehicle", "Equipment", "Other"]
STATUSES   = ["Available", "Assigned", "Maintenance"]

st.title("Asset Management")
st.subheader("Add New Asset")

with st.form("add_asset_form", clear_on_submit=True):
    asset_name    = st.text_input("Asset Name")
    category      = st.selectbox("Category", CATEGORIES)
    purchase_date = st.date_input("Purchase Date")
    purchase_cost = st.number_input("Purchase Cost ($)", min_value=0.0, step=0.01, format="%.2f")
    location      = st.text_input("Location")
    status        = st.selectbox("Status", STATUSES)
    submitted     = st.form_submit_button("Submit")

if submitted:
    # Validation
    if not asset_name.strip():
        st.error("Asset name cannot be empty.")
    elif purchase_cost < 0:
        st.error("Purchase cost cannot be negative.")
    else:
        add_asset(
            asset_name.strip(),
            category,
            str(purchase_date),
            purchase_cost,
            location.strip(),
            status,
        )
        st.success(f'Asset "{asset_name.strip()}" added successfully!')

# Display all assets
st.subheader("All Assets")
assets = get_all_assets()

if assets:
    df = pd.DataFrame(assets)
    df.columns = ["ID", "Asset Name", "Category", "Purchase Date", "Purchase Cost ($)", "Location", "Status"]
    st.dataframe(df, use_container_width=True, hide_index=True)
else:
    st.info("No assets found. Add your first asset above.")
