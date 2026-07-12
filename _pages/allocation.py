"""
Allocation page for AssetFlow - Assign and return assets.
"""

import streamlit as st
import pandas as pd
import datetime
from utils.resource_db import (
    get_available_assets,
    get_allocated_assets,
    assign_asset,
    return_asset,
    get_allocation_history,
    search_allocations,
)


def show_allocation():
    st.title("👤 Resource Allocation")

    tab1, tab2, tab3 = st.tabs(["Assign Asset", "Return Asset", "Allocation History"])

    # ── Tab 1: Assign Asset ──────────────────────────────────────────────────
    with tab1:
        st.subheader("Assign Asset to Employee")
        available = get_available_assets()

        if not available:
            st.warning("No available assets to assign. Add assets in the Assets page first.")
        else:
            asset_options = {f"{a['asset_name']} (ID: {a['asset_id']})": a['asset_id'] for a in available}

            with st.form("assign_form"):
                selected_label = st.selectbox("Select Available Asset", list(asset_options.keys()))
                employee_name = st.text_input("Employee Name")
                assigned_date = st.date_input("Assignment Date", value=datetime.date.today())

                if st.form_submit_button("✅ Assign Asset", use_container_width=True):
                    if not employee_name.strip():
                        st.error("Employee Name is required.")
                    else:
                        asset_id = asset_options[selected_label]
                        success = assign_asset(asset_id, employee_name.strip(), str(assigned_date))
                        if success:
                            st.success(f"Asset assigned successfully to {employee_name.strip()}!")
                            st.rerun()
                        else:
                            st.error("Failed to assign asset. It may already be assigned.")

    # ── Tab 2: Return Asset ──────────────────────────────────────────────────
    with tab2:
        st.subheader("Return Asset")
        allocated = get_allocated_assets()

        if not allocated:
            st.info("No assets are currently assigned.")
        else:
            options = {
                f"Allocation #{a['allocation_id']} — {a['employee_name']} (Asset ID: {a['asset_id']})": a['allocation_id']
                for a in allocated
            }

            with st.form("return_form"):
                selected_option = st.selectbox("Select Allocation to Return", list(options.keys()))
                returned_date = st.date_input("Return Date", value=datetime.date.today())

                if st.form_submit_button("🔄 Process Return", use_container_width=True):
                    alloc_id = options[selected_option]
                    success = return_asset(alloc_id, str(returned_date))
                    if success:
                        st.success("Asset returned successfully and marked as Available!")
                        st.rerun()
                    else:
                        st.error("Failed to return asset.")

    # ── Tab 3: Allocation History ────────────────────────────────────────────
    with tab3:
        st.subheader("Allocation History")

        with st.expander("🔍 Search Filters"):
            col1, col2 = st.columns(2)
            with col1:
                search_asset_id = st.number_input("Filter by Asset ID (0 = all)", min_value=0, step=1, value=0)
            with col2:
                search_employee = st.text_input("Filter by Employee Name")

        if search_asset_id > 0 or search_employee.strip():
            df = search_allocations(
                asset_id=search_asset_id if search_asset_id > 0 else None,
                employee_name=search_employee
            )
        else:
            df = get_allocation_history()

        if df.empty:
            st.info("No allocation history found.")
        else:
            st.dataframe(df, use_container_width=True, hide_index=True)
