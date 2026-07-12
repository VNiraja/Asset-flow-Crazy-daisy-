import streamlit as st
import pandas as pd
from utils.db import db

def show_reports():
    st.title("📄 Asset Reports & Exports")

    try:
        conn = db.get_connection()
        df = pd.read_sql("SELECT * FROM assets", conn)
        maint_df = pd.read_sql("SELECT * FROM maintenance", conn)
        conn.close()
    except Exception as e:
        st.error(f"Error fetching data: {e}")
        return

    if df.empty:
        st.info("No data available for reports.")
        return

    st.subheader("Summary Statistics")

    stats_df = pd.DataFrame({
        'Metric': [
            'Total Asset Value', 
            'Average Asset Value', 
            'Total Maintenance Cost', 
            'Average Maintenance Cost'
        ],
        'Value': [
            f"${df['cost'].sum():,.2f}",
            f"${df['cost'].mean():,.2f}",
            f"${maint_df['cost'].sum() if not maint_df.empty else 0:,.2f}",
            f"${maint_df['cost'].mean() if not maint_df.empty else 0:,.2f}"
        ]
    })

    st.table(stats_df)

    st.subheader("Detailed Asset Data")

    col1, col2 = st.columns(2)
    with col1:
        status_filter = st.multiselect(
            "Filter by Status", 
            options=df['status'].unique(), 
            default=df['status'].unique()
        )
    with col2:
        category_filter = st.multiselect(
            "Filter by Category", 
            options=df['category'].unique(), 
            default=df['category'].unique()
        )

    filtered_df = df[(df['status'].isin(status_filter)) & (df['category'].isin(category_filter))]
    st.dataframe(filtered_df, use_container_width=True)

    st.subheader("Export Report")
    csv = filtered_df.to_csv(index=False).encode('utf-8')

    st.download_button(
        label="⬇️ Download CSV Report",
        data=csv,
        file_name='asset_report.csv',
        mime='text/csv',
    )
