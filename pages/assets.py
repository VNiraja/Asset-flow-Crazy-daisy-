import streamlit as st
import pandas as pd
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from utils.db import create_table, add_asset, get_all_assets, search_assets, get_asset_by_id, update_asset, delete_asset

# Initialise DB on every page load (no-op if table already exists)
create_table()

CATEGORIES = ["Hardware", "Software", "Furniture", "Vehicle", "Equipment", "Other"]
STATUSES   = ["Available", "Assigned", "Maintenance"]

# ── Global styles ─────────────────────────────────────────────────────────────
st.markdown("""
<style>
    .metric-card {
        border-radius: 12px;
        padding: 20px 16px;
        text-align: center;
        color: white;
        margin-bottom: 8px;
    }
    .metric-card .metric-value { font-size: 2rem; font-weight: 700; margin: 0; }
    .metric-card .metric-label { font-size: 0.85rem; opacity: 0.9;   margin: 0; }

    .card-total       { background: linear-gradient(135deg, #667eea, #764ba2); }
    .card-available   { background: linear-gradient(135deg, #11998e, #38ef7d); }
    .card-assigned    { background: linear-gradient(135deg, #f7971e, #ffd200); }
    .card-maintenance { background: linear-gradient(135deg, #cb2d3e, #ef473a); }

    .page-footer {
        text-align: center;
        color: #888;
        font-size: 0.8rem;
        padding: 24px 0 8px 0;
        border-top: 1px solid #e0e0e0;
        margin-top: 40px;
    }
    .explorer-container {
        border: 1px solid #e0e0e0;
        border-radius: 12px;
        padding: 20px;
        margin-top: 8px;
    }
</style>
""", unsafe_allow_html=True)

# ── Page header ───────────────────────────────────────────────────────────────
st.title("📦 Asset Management")
st.caption("Manage, track, and explore your organisation's assets in one place.")
st.divider()

# ── Add New Asset (expandable) ────────────────────────────────────────────────
with st.expander("➕ Add New Asset", expanded=False):
    with st.form("add_asset_form", clear_on_submit=True):
        col_a, col_b = st.columns(2)
        with col_a:
            asset_name    = st.text_input("Asset Name")
            purchase_date = st.date_input("Purchase Date")
            location      = st.text_input("Location")
        with col_b:
            category      = st.selectbox("Category", CATEGORIES)
            purchase_cost = st.number_input("Purchase Cost (₹)", min_value=0.0, step=0.01, format="%.2f")
            status        = st.selectbox("Status", STATUSES)

        submitted = st.form_submit_button("💾 Save Asset", use_container_width=True)

    if submitted:
        # Validation (unchanged)
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
            st.success(f'✅ Asset "{asset_name.strip()}" added successfully!')

st.divider()

# ── Asset Explorer ────────────────────────────────────────────────────────────
st.subheader("🔍 Asset Explorer")

with st.container():
    st.markdown('<div class="explorer-container">', unsafe_allow_html=True)

    # Search & filter controls (unchanged logic)
    col1, col2, col3 = st.columns(3)
    with col1:
        search_name = st.text_input("Search by Asset Name", placeholder="Type to search...")
    with col2:
        filter_category = st.selectbox("Filter by Category", ["All"] + CATEGORIES, key="explorer_category")
    with col3:
        filter_status = st.selectbox("Filter by Status", ["All"] + STATUSES, key="explorer_status")

    st.markdown('</div>', unsafe_allow_html=True)

# Fetch data (unchanged logic)
filtered   = search_assets(search_name, filter_category, filter_status)
all_assets = get_all_assets()

st.divider()

# ── Asset Summary (metric cards) ──────────────────────────────────────────────
st.subheader("📊 Asset Summary")

total       = len(all_assets)
available   = sum(1 for a in all_assets if a["status"] == "Available")
assigned    = sum(1 for a in all_assets if a["status"] == "Assigned")
maintenance = sum(1 for a in all_assets if a["status"] == "Maintenance")

mc1, mc2, mc3, mc4 = st.columns(4)

mc1.markdown(f"""
<div class="metric-card card-total">
    <p class="metric-value">{total}</p>
    <p class="metric-label">🗂 Total Assets</p>
</div>""", unsafe_allow_html=True)

mc2.markdown(f"""
<div class="metric-card card-available">
    <p class="metric-value">{available}</p>
    <p class="metric-label">✅ Available</p>
</div>""", unsafe_allow_html=True)

mc3.markdown(f"""
<div class="metric-card card-assigned">
    <p class="metric-value">{assigned}</p>
    <p class="metric-label">📌 Assigned</p>
</div>""", unsafe_allow_html=True)

mc4.markdown(f"""
<div class="metric-card card-maintenance">
    <p class="metric-value">{maintenance}</p>
    <p class="metric-label">🔧 Under Maintenance</p>
</div>""", unsafe_allow_html=True)

st.divider()

# ── Interactive Asset Table ───────────────────────────────────────────────────
st.subheader("🗃 Asset Records")

if filtered:
    df = pd.DataFrame(filtered)
    df.columns = ["ID", "Asset Name", "Category", "Purchase Date", "Purchase Cost", "Location", "Status"]

    # Format cost as Indian Rupees
    df["Purchase Cost"] = df["Purchase Cost"].apply(lambda x: f"₹{x:,.2f}")

    st.data_editor(
        df,
        use_container_width=True,
        hide_index=True,
        disabled=True,
        column_config={
            "ID":            st.column_config.NumberColumn("ID",            width="small"),
            "Asset Name":    st.column_config.TextColumn("Asset Name",      width="medium"),
            "Category":      st.column_config.TextColumn("Category",        width="small"),
            "Purchase Date": st.column_config.TextColumn("Purchase Date",   width="small"),
            "Purchase Cost": st.column_config.TextColumn("Purchase Cost (₹)", width="small"),
            "Location":      st.column_config.TextColumn("Location",        width="small"),
            "Status":        st.column_config.TextColumn("Status",          width="small"),
        },
    )
else:
    st.info("🔎 No assets match your search or filter criteria.")

# ── Asset Lifecycle Management ───────────────────────────────────────────────
st.divider()
st.subheader("✏️ Asset Lifecycle Management")

all_assets_for_lifecycle = get_all_assets()

if not all_assets_for_lifecycle:
    st.info("No assets available. Add an asset first.")
else:
    # Build dropdown options: "ID - Asset Name"
    asset_options = {
        f"{a['asset_id']} - {a['asset_name']}": a["asset_id"]
        for a in all_assets_for_lifecycle
    }

    selected_label = st.selectbox(
        "Select Asset",
        options=list(asset_options.keys()),
        key="lifecycle_select",
    )
    selected_id = asset_options[selected_label]

    # Load the selected asset fresh from DB
    asset = get_asset_by_id(selected_id)

    with st.expander("✏️ Edit Asset Details", expanded=True):

        # ── Pre-populate editable fields ──────────────────────────────────────
        import datetime

        # Parse stored date string back to a date object for st.date_input
        try:
            stored_date = datetime.date.fromisoformat(asset["purchase_date"])
        except (TypeError, ValueError):
            stored_date = datetime.date.today()

        edit_col1, edit_col2 = st.columns(2)
        with edit_col1:
            edit_name  = st.text_input("Asset Name",      value=asset["asset_name"],  key="edit_name")
            edit_date  = st.date_input("Purchase Date",   value=stored_date,           key="edit_date")
            edit_loc   = st.text_input("Location",        value=asset["location"] or "", key="edit_loc")
        with edit_col2:
            edit_cat   = st.selectbox(
                "Category", CATEGORIES,
                index=CATEGORIES.index(asset["category"]) if asset["category"] in CATEGORIES else 0,
                key="edit_cat",
            )
            edit_cost  = st.number_input(
                "Purchase Cost (₹)",
                min_value=0.0, step=0.01, format="%.2f",
                value=float(asset["purchase_cost"] or 0.0),
                key="edit_cost",
            )
            edit_status = st.selectbox(
                "Status", STATUSES,
                index=STATUSES.index(asset["status"]) if asset["status"] in STATUSES else 0,
                key="edit_status",
            )

        # ── Save Changes ──────────────────────────────────────────────────────
        if st.button("💾 Save Changes", use_container_width=True, key="btn_save"):
            if not edit_name.strip():
                st.error("Asset name cannot be empty.")
            elif edit_cost < 0:
                st.error("Purchase cost cannot be negative.")
            else:
                update_asset(
                    selected_id,
                    edit_name.strip(),
                    edit_cat,
                    str(edit_date),
                    edit_cost,
                    edit_loc.strip(),
                    edit_status,
                )
                st.success("✅ Asset updated successfully.")
                st.rerun()

        st.divider()

        # ── Delete Asset ──────────────────────────────────────────────────────
        st.markdown("**🗑 Delete Asset**")
        st.warning(
            f"You are about to permanently delete **{asset['asset_name']}**. "
            "This action cannot be undone."
        )
        confirm_delete = st.checkbox(
            "☑ I understand this action cannot be undone.",
            key="confirm_delete",
        )
        if st.button("🗑 Delete Asset", disabled=not confirm_delete,
                     use_container_width=True, key="btn_delete"):
            delete_asset(selected_id)
            st.success("🗑 Asset deleted successfully.")
            st.rerun()

# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown(
    '<div class="page-footer">AssetFlow — Enterprise Asset Management System</div>',
    unsafe_allow_html=True,
)
