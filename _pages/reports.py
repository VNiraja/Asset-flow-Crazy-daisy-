"""
Reports page for AssetFlow - Summary statistics and CSV export.
"""

import streamlit as st
import pandas as pd
from utils.resource_db import get_all_assets, get_maintenance_history


def show_reports():
    st.title("📄 Asset Reports & Exports")

    all_assets = get_all_assets()
    maint_df   = get_maintenance_history()

    if not all_assets:
        st.info("No data available. Add some assets first.")
        return

    df = pd.DataFrame(all_assets)

    # ── Summary Statistics ───────────────────────────────────────────────────
    st.subheader("📊 Summary Statistics")

    total_value      = df['purchase_cost'].sum() if 'purchase_cost' in df.columns else 0
    avg_value        = df['purchase_cost'].mean() if 'purchase_cost' in df.columns else 0
    total_maint_cost = maint_df['cost'].sum()   if not maint_df.empty else 0
    avg_maint_cost   = maint_df['cost'].mean()  if not maint_df.empty else 0

    stats_df = pd.DataFrame({
        'Metric': [
            'Total Asset Value',
            'Average Asset Value',
            'Total Maintenance Cost',
            'Average Maintenance Cost',
        ],
        'Value': [
            f"${total_value:,.2f}",
            f"${avg_value:,.2f}",
            f"${total_maint_cost:,.2f}",
            f"${avg_maint_cost:,.2f}",
        ]
    })
    st.table(stats_df)

    st.markdown("---")

    # ── Detailed Asset Data ──────────────────────────────────────────────────
    st.subheader("🗃 Detailed Asset Data")

    col1, col2 = st.columns(2)
    with col1:
        status_filter = st.multiselect(
            "Filter by Status",
            options=df['status'].unique().tolist(),
            default=df['status'].unique().tolist(),
        )
    with col2:
        category_filter = st.multiselect(
            "Filter by Category",
            options=df['category'].unique().tolist(),
            default=df['category'].unique().tolist(),
        )

    filtered_df = df[
        df['status'].isin(status_filter) & df['category'].isin(category_filter)
    ]

    st.dataframe(filtered_df, use_container_width=True, hide_index=True)

    # ── Export ───────────────────────────────────────────────────────────────
    st.markdown("---")
    st.subheader("📤 Export Report")

    csv = filtered_df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="⬇️ Download CSV Report",
        data=csv,
        file_name="asset_report.csv",
        mime="text/csv",
        use_container_width=True,
    )
