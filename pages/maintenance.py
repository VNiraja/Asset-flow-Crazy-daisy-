"""
Maintenance page for AssetFlow - Log and track asset maintenance.
"""

import streamlit as st
import datetime
from utils.resource_db import (
    get_all_assets,
    add_maintenance,
    get_maintenance_history,
    search_maintenance,
)


def show_maintenance():
    st.title("🔧 Maintenance Management")

    tab1, tab2 = st.tabs(["Log Maintenance", "Maintenance History"])

    # ── Tab 1: Add Maintenance Record ───────────────────────────────────────
    with tab1:
        st.subheader("Log Asset Maintenance")
        all_assets = get_all_assets()

        if not all_assets:
            st.warning("No assets found. Please add assets first.")
        else:
            asset_options = {f"{a['asset_name']} (ID: {a['asset_id']})": a['asset_id'] for a in all_assets}

            with st.form("maintenance_form"):
                col1, col2 = st.columns(2)
                with col1:
                    selected_label = st.selectbox("Select Asset", list(asset_options.keys()))
                    maintenance_date = st.date_input("Maintenance Date", value=datetime.date.today())
                    status = st.selectbox("Status", options=["Scheduled", "In Progress", "Completed"])
                with col2:
                    cost = st.number_input("Cost ($)", min_value=0.0, step=0.01, format="%.2f")
                    description = st.text_area("Description", placeholder="Describe the maintenance work...")

                if st.form_submit_button("💾 Log Maintenance", use_container_width=True):
                    if not description.strip():
                        st.error("Description cannot be empty.")
                    else:
                        asset_id = asset_options[selected_label]
                        success = add_maintenance(
                            asset_id=asset_id,
                            maintenance_date=str(maintenance_date),
                            description=description.strip(),
                            cost=float(cost),
                            status=status,
                        )
                        if success:
                            st.success("✅ Maintenance record added successfully!")
                            st.rerun()
                        else:
                            st.error("Failed to add maintenance record.")

    # ── Tab 2: Maintenance History ───────────────────────────────────────────
    with tab2:
        st.subheader("Maintenance History")

        with st.expander("🔍 Search Filters"):
            col1, col2 = st.columns(2)
            with col1:
                search_asset_id = st.number_input("Filter by Asset ID (0 = all)", min_value=0, step=1, value=0)
            with col2:
                search_status = st.selectbox("Filter by Status", ["All", "Scheduled", "In Progress", "Completed"])

        if search_asset_id > 0 or search_status != "All":
            df = search_maintenance(
                asset_id=search_asset_id if search_asset_id > 0 else None,
                status=search_status,
            )
        else:
            df = get_maintenance_history()

        if df.empty:
            st.info("No maintenance records found.")
        else:
            st.dataframe(df, use_container_width=True, hide_index=True)
