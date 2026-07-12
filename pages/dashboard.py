"""
Dashboard page for AssetFlow - KPI cards and analytics charts.
"""

import streamlit as st
import pandas as pd
from utils.resource_db import get_all_assets, get_maintenance_history
from utils.charts import (
    create_status_pie_chart,
    create_category_bar_chart,
    create_monthly_maintenance_cost_chart,
)


def show_dashboard():
    st.title("📊 Asset Management Dashboard")

    # Load data
    all_assets = get_all_assets()
    assets_df = pd.DataFrame(all_assets) if all_assets else pd.DataFrame()

    maint_df = get_maintenance_history()

    # ── KPI Cards ────────────────────────────────────────────────────────────
    st.subheader("Key Performance Indicators")
    col1, col2, col3, col4 = st.columns(4)

    total_assets     = len(assets_df)
    available_assets = len(assets_df[assets_df['status'] == 'Available'])   if not assets_df.empty else 0
    assigned_assets  = len(assets_df[assets_df['status'] == 'Assigned'])    if not assets_df.empty else 0
    under_maintenance= len(assets_df[assets_df['status'] == 'Maintenance']) if not assets_df.empty else 0

    with col1:
        st.metric("Total Assets", total_assets)
    with col2:
        st.metric("Available Assets", available_assets)
    with col3:
        st.metric("Assigned Assets", assigned_assets)
    with col4:
        st.metric("Under Maintenance", under_maintenance)

    st.markdown("---")

    # ── Charts ───────────────────────────────────────────────────────────────
    if not assets_df.empty:
        st.subheader("Analytics Overview")
        chart_col1, chart_col2 = st.columns(2)

        with chart_col1:
            st.plotly_chart(create_status_pie_chart(assets_df), use_container_width=True)
        with chart_col2:
            st.plotly_chart(create_category_bar_chart(assets_df), use_container_width=True)

        if not maint_df.empty:
            st.plotly_chart(
                create_monthly_maintenance_cost_chart(maint_df),
                use_container_width=True,
            )

    else:
        st.info("📦 No assets found. Go to the Assets page to add your first asset!")

    # ── Smart Insights ───────────────────────────────────────────────────────
    st.markdown("---")
    st.subheader("💡 Smart Insights")

    if not assets_df.empty:
        most_used_cat = assets_df['category'].value_counts().idxmax()
        st.info(f"📌 Most used asset category: **{most_used_cat}**")

        maintenance_assets = assets_df[assets_df['status'] == 'Maintenance']
        if not maintenance_assets.empty:
            st.warning(f"⚠️ {len(maintenance_assets)} asset(s) currently under maintenance: "
                       f"{', '.join(maintenance_assets['asset_name'].tolist())}")
        else:
            st.success("✅ All assets are operational — no active maintenance issues.")
    else:
        st.info("Add assets to see smart insights.")
