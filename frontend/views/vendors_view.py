import streamlit as st
import pandas as pd
from api_client import APIClient
from config import StateKeys
from components.alerts import show_error, show_success, show_info


def render_vendors_view():
    st.header("🏢 Vendor Onboarding & Management")
    st.caption("Onboard new corporate tenants / vendors and manage tenant profiles (Super Admin access).")

    jwt_token = st.session_state.get(StateKeys.JWT_TOKEN)
    if not jwt_token:
        show_info("Please log in with Super Admin credentials in the **Authentication** tab first.")
        return

    tab_list, tab_create, tab_inspect = st.tabs(["📋 Vendor Directory", "➕ Onboard New Vendor", "🔍 Inspect Vendor"])

    with tab_list:
        st.subheader("Active Vendors")
        try:
            vendors = APIClient.get_all_vendors()
            if not vendors:
                st.info("No vendors registered yet.")
            else:
                df = pd.DataFrame(vendors)
                st.dataframe(df, use_container_width=True)

                st.markdown("#### Quick Select Active Tenant")
                vendor_options = {f"{v.get('name', 'Unknown')} ({v.get('id', '')})": v.get('id') for v in vendors}
                selected_label = st.selectbox("Select Vendor to work with:", list(vendor_options.keys()))
                
                if st.button("Set as Active Vendor Context", type="primary"):
                    st.session_state[StateKeys.ACTIVE_VENDOR_ID] = vendor_options[selected_label]
                    show_success(f"Active vendor set to: {vendor_options[selected_label]}")
                    st.rerun()

        except Exception as e:
            show_error(f"Failed to fetch vendors: {str(e)}")

    with tab_create:
        st.subheader("Onboard New Vendor")
        with st.form("create_vendor_form"):
            custom_id = st.text_input("Custom Vendor ID (Optional)", placeholder="e.g. 5e7dfe83-90c2-4574-83cf-512ee5a4bf8c")
            name = st.text_input("Vendor / Company Name", placeholder="e.g. Acme Payroll Corp")
            description = st.text_area("Description", placeholder="e.g. Multi-national HR & Payroll enterprise client")
            submit = st.form_submit_button("🏢 Create Vendor", use_container_width=True)

            if submit:
                if not name:
                    show_error("Vendor name is required.")
                else:
                    try:
                        with st.spinner("Onboarding vendor..."):
                            resp = APIClient.create_vendor(
                                name=name,
                                description=description,
                                vendor_id=custom_id.strip() if custom_id.strip() else None
                            )
                            new_id = resp.get("vendor_id") or resp.get("id") or resp.get("_id") or str(resp)
                            st.session_state[StateKeys.ACTIVE_VENDOR_ID] = new_id
                            show_success(f"Vendor '{name}' created successfully! ID: `{new_id}`")
                    except Exception as e:
                        show_error(f"Failed to create vendor: {str(e)}")

    with tab_inspect:
        st.subheader("Inspect Vendor by ID")
        current_active = st.session_state.get(StateKeys.ACTIVE_VENDOR_ID, "")
        vendor_id_input = st.text_input("Enter Vendor ID", value=current_active)
        
        if st.button("🔍 Fetch Vendor Details"):
            if not vendor_id_input:
                show_error("Please provide a Vendor ID.")
            else:
                try:
                    with st.spinner("Loading vendor..."):
                        data = APIClient.get_vendor(vendor_id_input)
                        st.json(data)
                except Exception as e:
                    show_error(f"Failed to load vendor: {str(e)}")
