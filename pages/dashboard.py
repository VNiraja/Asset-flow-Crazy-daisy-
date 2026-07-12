import streamlit as st
import pandas as pd
from utils.db import db
from utils.charts import create_status_pie_chart, create_category_bar_chart, create_monthly_maintenance_cost_chart

def show_dashboard():
    st.title("📊 Asset Management Dashboard")
    
    try:
        conn = db.get_connection()
        assets_df = pd.read_sql("SELECT * FROM assets", conn)
        maint_df = pd.read_sql("SELECT * FROM maintenance", conn)
        conn.close()
    except Exception as e:
        st.error(f"Database error: {e}")
        return

    # KPI cards
    st.subheader("Key Performance Indicators")
    col1, col2, col3, col4 = st.columns(4)

    total_assets = len(assets_df)
    available_assets = len(assets_df[assets_df['status'] == 'Available']) if not assets_df.empty else 0
    assigned_assets = len(assets_df[assets_df['status'] == 'Assigned']) if not assets_df.empty else 0
    under_maintenance = len(assets_df[assets_df['status'] == 'Under Maintenance']) if not assets_df.empty else 0

    with col1:
        st.metric("Total Assets", total_assets)
    with col2:
        st.metric("Available Assets", available_assets)
    with col3:
        st.metric("Assigned Assets", assigned_assets)
    with col4:
        st.metric("Under Maintenance", under_maintenance)

    st.markdown("---")

    if not assets_df.empty:
        st.subheader("Analytics Overview")
        chart_col1, chart_col2 = st.columns(2)

        with chart_col1:
            st.plotly_chart(create_status_pie_chart(assets_df), use_container_width=True)

        with chart_col2:
            st.plotly_chart(create_category_bar_chart(assets_df), use_container_width=True)

        if not maint_df.empty:
            maint_df['last_maintenance_date'] = maint_df['maintenance_date']
            st.plotly_chart(create_monthly_maintenance_cost_chart(maint_df), use_container_width=True)
    else:
        st.info("Add some assets to view analytics.")
