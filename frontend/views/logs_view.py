import streamlit as st
import pandas as pd
from api_client import APIClient
from config import StateKeys
from components.alerts import show_error, show_success, show_info


def render_logs_view():
    st.header("📋 APM System Logs, Telemetry & Health")
    st.caption("Inspect live system performance metrics, application trace logs, MongoDB sinks, and system health status.")

    jwt_token = st.session_state.get(StateKeys.JWT_TOKEN)

    tab_health, tab_logs = st.tabs(["🩺 Platform Health & Redis", "📜 APM Logs & Telemetry"])

    with tab_health:
        st.subheader("System Infrastructure Health")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("💓 Run Backend Health Check", use_container_width=True):
                try:
                    res = APIClient.health_check()
                    show_success(f"Backend Status: {res.get('status', 'ok')}")
                    st.json(res)
                except Exception as e:
                    show_error(f"Health check failed: {str(e)}")

        with col2:
            if st.button("🔴 Ping Redis Connection", use_container_width=True):
                try:
                    res = APIClient.test_redis()
                    show_success(f"Redis Value Test: {res.get('value', 'OK')}")
                    st.json(res)
                except Exception as e:
                    show_error(f"Redis test failed: {str(e)}")

    with tab_logs:
        st.subheader("System Telemetry Logs")
        if not jwt_token:
            show_info("Please log in with Super Admin credentials in the **Authentication** tab to view system logs.")
        else:
            col1, col2, col3, col4 = st.columns([2, 2, 2, 1])
            active_vendor = st.session_state.get(StateKeys.ACTIVE_VENDOR_ID, "")
            active_ws = st.session_state.get(StateKeys.ACTIVE_WORKSPACE_ID, "")

            with col1:
                filter_vendor = st.text_input("Filter Vendor ID", value="")
            with col2:
                filter_ws = st.text_input("Filter Workspace ID", value="")
            with col3:
                filter_sess = st.text_input("Filter Session ID", value="")
            with col4:
                st.write("")
                st.write("")
                fetch_btn = st.button("🔄 Fetch Logs", use_container_width=True)

            if fetch_btn:
                try:
                    with st.spinner("Fetching logs..."):
                        logs = APIClient.get_logs(
                            vendor_id=filter_vendor or None,
                            workspace_id=filter_ws or None,
                            session_id=filter_sess or None
                        )
                        st.session_state["fetched_logs"] = logs
                except Exception as e:
                    show_error(f"Failed to fetch logs: {str(e)}")

            logs_data = st.session_state.get("fetched_logs", [])
            if logs_data:
                df = pd.DataFrame(logs_data)
                st.dataframe(df, use_container_width=True)
            else:
                st.info("No logs fetched yet. Click 'Fetch Logs' above.")
