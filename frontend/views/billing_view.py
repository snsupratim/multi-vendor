import streamlit as st
import plotly.express as px
import pandas as pd
from api_client import APIClient
from config import StateKeys
from components.alerts import show_error, show_success, show_info


def render_billing_view():
    st.header("💳 Tenant Billing & Token Tracking")
    st.caption("Track real-time LLM token consumption (Prompt vs Completion), manage tenant payment status, and enforce account block/unblock controls.")

    jwt_token = st.session_state.get(StateKeys.JWT_TOKEN)
    if not jwt_token:
        show_info("Please log in with Super Admin credentials in the **Authentication** tab first.")
        return

    active_vendor = st.session_state.get(StateKeys.ACTIVE_VENDOR_ID, "")

    col1, col2 = st.columns([2, 1])

    with col1:
        st.subheader("Tenant Token Usage & Quotas")
        vendor_id_input = st.text_input("Vendor ID", value=active_vendor, placeholder="Vendor UUID")
        fetch_stats = st.button("📊 Fetch Billing & Token Stats", use_container_width=True)

        if fetch_stats and vendor_id_input:
            try:
                with st.spinner("Fetching token analytics..."):
                    stats = APIClient.get_billing_stats(vendor_id_input)
                    st.session_state["vendor_billing_stats"] = stats
            except Exception as e:
                show_error(f"Failed to fetch billing stats: {str(e)}")

        stats = st.session_state.get("vendor_billing_stats", {})
        if stats:
            st.markdown("---")
            m1, m2, m3, m4 = st.columns(4)
            status_val = stats.get("status", "unknown").upper()
            prompt_tokens = stats.get("total_prompt_tokens", 0)
            completion_tokens = stats.get("total_completion_tokens", 0)
            total_tokens = stats.get("total_tokens", prompt_tokens + completion_tokens)
            total_requests = stats.get("total_requests", 0)

            m1.metric("Tenant Status", status_val)
            m2.metric("Prompt Tokens", f"{prompt_tokens:,}")
            m3.metric("Completion Tokens", f"{completion_tokens:,}")
            m4.metric("Total Tokens", f"{total_tokens:,}")

            # Plot token breakdown
            if total_tokens > 0:
                chart_df = pd.DataFrame([
                    {"Category": "Prompt Tokens", "Count": prompt_tokens},
                    {"Category": "Completion Tokens", "Count": completion_tokens}
                ])
                fig = px.pie(
                    chart_df,
                    names="Category",
                    values="Count",
                    title="Token Consumption Breakdown",
                    hole=0.4,
                    color_discrete_sequence=["#636EFA", "#EF553B"],
                    template="plotly_dark"
                )
                st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.subheader("Tenant Access Status Control")
        st.caption("Block or unblock a vendor. Blocked vendors receive `402 Payment Required` on chat requests.")
        
        target_vendor = st.text_input("Target Vendor ID", value=active_vendor, key="block_vendor_id")
        desired_status = st.radio("Set Status:", ["active", "inactive"])

        if st.button("💾 Update Tenant Status", type="primary", use_container_width=True):
            if not target_vendor:
                show_error("Target Vendor ID is required.")
            else:
                try:
                    with st.spinner("Updating vendor access status..."):
                        resp = APIClient.update_vendor_status(target_vendor, desired_status)
                        show_success(f"Vendor `{target_vendor}` status successfully updated to `{desired_status}`!")
                        st.json(resp)
                except Exception as e:
                    show_error(f"Failed to update status: {str(e)}")
