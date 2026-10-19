import streamlit as st
import pandas as pd
from api_client import APIClient
from config import StateKeys
from components.alerts import show_error, show_success, show_info


def render_history_view():
    st.header("🕰️ Chat History & Session Browser")
    st.caption("Inspect past conversational sessions by tenant, view dialogue logs, and restore past sessions.")

    active_vendor = st.session_state.get(StateKeys.ACTIVE_VENDOR_ID, "")

    col1, col2 = st.columns([1, 2])

    with col1:
        st.subheader("Vendor Sessions")
        vendor_id_input = st.text_input("Vendor ID", value=active_vendor, placeholder="Vendor UUID")
        fetch_sessions = st.button("🔄 Fetch Sessions", use_container_width=True)

        sessions = []
        if fetch_sessions or vendor_id_input:
            try:
                with st.spinner("Fetching past sessions..."):
                    sessions = APIClient.get_vendor_sessions(vendor_id_input)
            except Exception as e:
                show_error(f"Failed to fetch sessions: {str(e)}")

        if sessions:
            st.markdown(f"**Found {len(sessions)} session(s):**")
            for s in sessions:
                s_id = s.get("session_id", "")
                title = s.get("title") or s_id[:16]
                time_str = s.get("updated_at", "")
                
                if st.button(f"💬 {title}\n({s_id[:8]}...)", key=f"sess_btn_{s_id}", use_container_width=True):
                    st.session_state["inspected_session_id"] = s_id
                    st.rerun()
        else:
            st.info("No past sessions found.")

    with col2:
        st.subheader("Conversation Transcript")
        inspected_session = st.session_state.get("inspected_session_id", "")
        session_id_input = st.text_input("Session ID to inspect", value=inspected_session)

        if st.button("📖 Load Session Dialogue", use_container_width=True):
            if not session_id_input:
                show_error("Please enter a Session ID.")
            else:
                try:
                    with st.spinner("Loading conversation messages..."):
                        messages = APIClient.get_session_messages(session_id_input)
                        if not messages:
                            st.info("No messages in this session.")
                        else:
                            st.session_state["loaded_session_messages"] = messages
                except Exception as e:
                    show_error(f"Failed to load messages: {str(e)}")

        loaded_msgs = st.session_state.get("loaded_session_messages", [])
        if loaded_msgs:
            st.markdown("---")
            for msg in loaded_msgs:
                role = msg.get("role", "user")
                content = msg.get("content") or msg.get("message", "")
                with st.chat_message(role):
                    st.markdown(content)
                    if "timestamp" in msg:
                        st.caption(f"Time: {msg['timestamp']}")
